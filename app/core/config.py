"""
Application configuration using Pydantic Settings
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=[
            ".env",  # Current directory
            str(Path(__file__).parent.parent.parent / ".env"),  # Backend root directory
        ],
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_ignore_empty=True
    )

    # Project Info
    PROJECT_NAME: str = "Task Manager API"
    PROJECT_DESCRIPTION: str = "Sistema de Gestión de Tareas - API REST con FastAPI"
    VERSION: str = "0.1.0"
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # CORS
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"], 
        description="Allowed hosts for CORS"
    )
    
    # Database Configuration
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017/taskmanager",
        description="MongoDB connection URL"
    )
    DATABASE_NAME: str = Field(
        default="taskmanager",
        description="Database name"
    )
    
    # JWT Configuration
    SECRET_KEY: str = Field(
        default="super-secret-key-change-in-production-please-make-it-very-long",
        description="Secret key for JWT tokens"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, 
        description="Access token expiration time in minutes"
    )
    
    # Password Hashing
    PWD_CONTEXT_SCHEMES: List[str] = Field(
        default=["bcrypt"], 
        description="Password hashing schemes"
    )
    PWD_CONTEXT_DEPRECATED: str = Field(
        default="auto", 
        description="Deprecated password schemes"
    )
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings() 