"""
FastAPI dependencies for dependency injection
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import verify_token
from app.database.mongodb import get_database
from app.models.user import UserInDB
from app.repositories.user_repository import UserRepository
from app.repositories.task_repository import TaskRepository

# Security scheme - auto_error=False to handle errors manually
security = HTTPBearer(auto_error=False)


async def get_user_repository() -> UserRepository:
    """Get user repository instance"""
    database = get_database()
    return UserRepository(database)


async def get_task_repository() -> TaskRepository:
    """Get task repository instance"""
    database = get_database()
    return TaskRepository(database)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserInDB:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if credentials are provided
    if credentials is None:
        raise credentials_exception
    
    token_data = verify_token(credentials.credentials)
    if token_data is None or token_data.email is None:
        raise credentials_exception
    
    user = await user_repo.get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
        
    return user


async def get_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> UserInDB:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user


# Type aliases for dependency injection
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
TaskRepositoryDep = Annotated[TaskRepository, Depends(get_task_repository)]
CurrentUserDep = Annotated[UserInDB, Depends(get_current_user)]
ActiveUserDep = Annotated[UserInDB, Depends(get_active_user)] 