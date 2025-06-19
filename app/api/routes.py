"""
Main API router that includes all route modules
"""

from fastapi import APIRouter

from app.api.endpoints import auth, tasks, users

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"]
) 