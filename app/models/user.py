"""
User models and schemas
"""

from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, validation_info=None):
        if v is None:
            return v
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
            else:
                raise ValueError("Invalid ObjectId string")
        raise ValueError(f"Invalid ObjectId type: {type(v)}")

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr = Field(..., description="Email del usuario")
    full_name: str = Field(..., min_length=2, max_length=100, description="Nombre completo")
    is_active: bool = Field(default=True, description="Usuario activo")


class UserCreate(UserBase):
    """Schema for creating users"""
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña")


class UserUpdate(BaseModel):
    """Schema for updating users"""
    email: Optional[EmailStr] = Field(None, description="Email del usuario")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nombre completo")
    is_active: Optional[bool] = Field(None, description="Usuario activo")


class PasswordChange(BaseModel):
    """Schema for changing password"""
    current_password: str = Field(..., min_length=6, description="Contraseña actual")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")


class UserInDB(UserBase):
    """User schema as stored in database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    hashed_password: str = Field(..., description="Contraseña hasheada")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de actualización")


class User(UserBase):
    """Public user schema (without sensitive data)"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: str = Field(..., description="ID del usuario")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=6, description="Contraseña") 