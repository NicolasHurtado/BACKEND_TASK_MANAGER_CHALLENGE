"""
Task repository for database operations
"""

from datetime import datetime
from typing import Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.task import Task, TaskCreate, TaskInDB, TaskStats, TaskStatus, TaskUpdate


class TaskRepository:
    """Task repository for MongoDB operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.tasks

    async def create_indexes(self) -> None:
        """Create database indexes for performance"""
        # Index on user_id for user's tasks
        await self.collection.create_index("user_id")
        # Index on status for filtering
        await self.collection.create_index("status")
        # Index on created_at for sorting
        await self.collection.create_index("created_at")
        # Index on due_date for filtering
        await self.collection.create_index("due_date")
        # Compound index for user queries
        await self.collection.create_index([("user_id", 1), ("status", 1)])

    async def create_task(self, task_create: TaskCreate, user_id: str) -> TaskInDB:
        """Create a new task"""
        task_dict = task_create.model_dump()
        task_dict["user_id"] = user_id
        
        task_in_db = TaskInDB(**task_dict)
        
        # Convert user_id to ObjectId for database storage
        task_data = task_in_db.model_dump(by_alias=True, exclude={"id"})
        task_data["user_id"] = ObjectId(user_id)
        
        result = await self.collection.insert_one(task_data)
        task_in_db.id = str(result.inserted_id)
        return task_in_db

    async def get_task_by_id(self, task_id: str, user_id: str) -> Optional[TaskInDB]:
        """Get task by ID (ensuring user ownership)"""
        if not ObjectId.is_valid(task_id):
            return None
            
        task_doc = await self.collection.find_one({
            "_id": ObjectId(task_id),
            "user_id": ObjectId(user_id)
        })
        if task_doc:
            return self._doc_to_task_in_db(task_doc)
        return None

    async def get_user_tasks(
        self, 
        user_id: str, 
        status: Optional[TaskStatus] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[TaskInDB]:
        """Get user's tasks with optional status filter"""
        query = {"user_id": ObjectId(user_id)}
        if status:
            query["status"] = status.value
            
        cursor = (
            self.collection
            .find(query)
            .skip(skip)
            .limit(limit)
            .sort("created_at", -1)
        )
        
        tasks = []
        async for task_doc in cursor:
            tasks.append(self._doc_to_task_in_db(task_doc))
        return tasks

    async def update_task(
        self, 
        task_id: str, 
        task_update: TaskUpdate, 
        user_id: str
    ) -> Optional[TaskInDB]:
        """Update task (ensuring user ownership)"""
        if not ObjectId.is_valid(task_id):
            return None
            
        update_data = task_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_task_by_id(task_id, user_id)
        
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # If status changed to completed, add completed_at timestamp
        if update_data.get("status") == TaskStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
        elif update_data.get("status") in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]:
            update_data["completed_at"] = None
            
        await self.collection.update_one(
            {
                "_id": ObjectId(task_id),
                "user_id": ObjectId(user_id)
            },
            {"$set": update_data}
        )
        
        return await self.get_task_by_id(task_id, user_id)

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete task (ensuring user ownership)"""
        if not ObjectId.is_valid(task_id):
            return False
            
        result = await self.collection.delete_one({
            "_id": ObjectId(task_id),
            "user_id": ObjectId(user_id)
        })
        return result.deleted_count > 0

    async def count_user_tasks(self, user_id: str, status: Optional[TaskStatus] = None) -> int:
        """Count user's tasks with optional status filter"""
        query = {"user_id": ObjectId(user_id)}
        if status:
            query["status"] = status.value
        return await self.collection.count_documents(query)

    async def get_user_task_stats(self, user_id: str) -> TaskStats:
        """Get task statistics for a user"""
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "todo": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", TaskStatus.TODO]}, 1, 0]
                        }
                    },
                    "in_progress": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", TaskStatus.IN_PROGRESS]}, 1, 0]
                        }
                    },
                    "completed": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", TaskStatus.COMPLETED]}, 1, 0]
                        }
                    },
                    "priority_stats": {
                        "$push": "$priority"
                    }
                }
            }
        ]
        
        result = []
        async for doc in self.collection.aggregate(pipeline):
            result.append(doc)
            
        if not result:
            return TaskStats(
                total=0,
                todo=0,
                in_progress=0,
                completed=0,
                by_priority={"baja": 0, "media": 0, "alta": 0},
                completion_rate=0.0
            )
            
        stats = result[0]
        
        # Count tasks by priority
        priority_counts = {"baja": 0, "media": 0, "alta": 0}
        for priority in stats.get("priority_stats", []):
            if priority in priority_counts:
                priority_counts[priority] += 1
        
        # Calculate completion rate
        total = stats["total"]
        completed = stats["completed"]
        completion_rate = (completed / total * 100) if total > 0 else 0.0
        
        return TaskStats(
            total=stats["total"],
            todo=stats["todo"],
            in_progress=stats["in_progress"],
            completed=stats["completed"],
            by_priority=priority_counts,
            completion_rate=round(completion_rate, 2)
        )

    def _doc_to_task_in_db(self, task_doc: dict) -> TaskInDB:
        """Convert MongoDB document to TaskInDB model"""
        # Ensure _id and user_id are properly handled
        if "_id" in task_doc and not isinstance(task_doc["_id"], str):
            task_doc["_id"] = str(task_doc["_id"])
        if "user_id" in task_doc and not isinstance(task_doc["user_id"], str):
            task_doc["user_id"] = str(task_doc["user_id"])
        return TaskInDB(**task_doc)

    def to_public_task(self, task_in_db: TaskInDB) -> Task:
        """Convert TaskInDB to public Task schema"""
        return Task(
            id=str(task_in_db.id),
            title=task_in_db.title,
            description=task_in_db.description,
            status=task_in_db.status,
            priority=task_in_db.priority,
            due_date=task_in_db.due_date,
            user_id=str(task_in_db.user_id),
            created_at=task_in_db.created_at,
            updated_at=task_in_db.updated_at,
            completed_at=task_in_db.completed_at
        ) 