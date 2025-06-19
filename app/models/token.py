"""
Token models and schemas for authentication
"""

from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """JWT token schema"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Tipo de token")


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = Field(None, description="Email del usuario")
    user_id: Optional[str] = Field(None, description="ID del usuario")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="JWT refresh token")


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Tipo de token")
    user: dict = Field(..., description="Información del usuario") 