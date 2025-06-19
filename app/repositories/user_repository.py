"""
User repository for database operations
"""

from typing import List, Optional
from datetime import datetime

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.models.user import User, UserCreate, UserInDB, UserUpdate


class UserRepository:
    """User repository for MongoDB operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.users

    async def create_indexes(self) -> None:
        """Create database indexes for performance"""
        # Unique index on email
        await self.collection.create_index("email", unique=True)
        # Index on created_at for sorting
        await self.collection.create_index("created_at")

    async def create_user(self, user_create: UserCreate, hashed_password: str) -> UserInDB:
        """Create a new user"""
        user_dict = user_create.model_dump()
        user_dict["hashed_password"] = hashed_password
        
        user_in_db = UserInDB(**user_dict)
        
        try:
            result = await self.collection.insert_one(
                user_in_db.model_dump(by_alias=True, exclude={"id"})
            )
            user_in_db.id = str(result.inserted_id)
            return user_in_db
        except DuplicateKeyError:
            raise ValueError("El email ya está registrado")

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        if not ObjectId.is_valid(user_id):
            return None
            
        user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_doc:
            return self._doc_to_user_in_db(user_doc)
        return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        user_doc = await self.collection.find_one({"email": email})
        if user_doc:
            return self._doc_to_user_in_db(user_doc)
        return None

    def _doc_to_user_in_db(self, user_doc: dict) -> UserInDB:
        """Convert MongoDB document to UserInDB model"""
        # Ensure _id is properly handled
        if "_id" in user_doc and not isinstance(user_doc["_id"], str):
            user_doc["_id"] = str(user_doc["_id"])
        return UserInDB(**user_doc)

    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
        """Update user"""
        if not ObjectId.is_valid(user_id):
            return None
            
        update_data = user_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_user_by_id(user_id)
            
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
            
        try:
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return await self.get_user_by_id(user_id)
        except DuplicateKeyError:
            raise ValueError("El email ya está registrado")

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if not ObjectId.is_valid(user_id):
            return False
            
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """Get all users with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
        users = []
        async for user_doc in cursor:
            users.append(self._doc_to_user_in_db(user_doc))
        return users

    async def count_users(self) -> int:
        """Count total users"""
        return await self.collection.count_documents({})

    async def change_password(self, user_id: str, new_hashed_password: str) -> bool:
        """Change user password"""
        if not ObjectId.is_valid(user_id):
            return False
            
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "hashed_password": new_hashed_password,
                "updated_at": datetime.utcnow()
            }}
        )
        return result.modified_count > 0

    def to_public_user(self, user_in_db: UserInDB) -> User:
        """Convert UserInDB to public User schema"""
        return User(
            id=str(user_in_db.id),
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            is_active=user_in_db.is_active,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at
        ) 