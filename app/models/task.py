"""
Task models and schemas
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.models.user import PyObjectId


class TaskStatus(str, Enum):
    """Task status enumeration"""
    TODO = "por_hacer"
    IN_PROGRESS = "en_progreso"
    COMPLETED = "completada"


class TaskPriority(str, Enum):
    """Task priority enumeration"""
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"


class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=1, max_length=200, description="Título de la tarea")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción de la tarea")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Estado de la tarea")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Prioridad de la tarea")
    due_date: Optional[datetime] = Field(None, description="Fecha límite de la tarea")


class TaskCreate(TaskBase):
    """Schema for creating tasks"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating tasks"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Título de la tarea")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción de la tarea")
    status: Optional[TaskStatus] = Field(None, description="Estado de la tarea")
    priority: Optional[TaskPriority] = Field(None, description="Prioridad de la tarea")
    due_date: Optional[datetime] = Field(None, description="Fecha límite de la tarea")


class TaskInDB(TaskBase):
    """Task schema as stored in database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str = Field(..., description="ID del usuario propietario")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de actualización")
    completed_at: Optional[datetime] = Field(None, description="Fecha de completado")


class Task(TaskBase):
    """Public task schema"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: str = Field(..., description="ID de la tarea")
    user_id: str = Field(..., description="ID del usuario propietario")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")
    completed_at: Optional[datetime] = Field(None, description="Fecha de completado")


class TaskStats(BaseModel):
    """Task statistics schema"""
    total: int = Field(..., description="Total de tareas")
    todo: int = Field(..., description="Tareas por hacer")
    in_progress: int = Field(..., description="Tareas en progreso")
    completed: int = Field(..., description="Tareas completadas")
    by_priority: dict[str, int] = Field(..., description="Tareas por prioridad")
    completion_rate: float = Field(..., description="Tasa de completado (%)") 