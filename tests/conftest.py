"""
Pytest configuration and fixtures for Task Manager API tests
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from mongomock_motor import AsyncMongoMockClient

from app.core.config import get_settings
from app.database.mongodb import get_database
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Create a test database instance using in-memory MongoDB mock."""
    settings = get_settings()
    test_db_name = f"{settings.DATABASE_NAME}_test"
    
    # Use mongomock for in-memory testing
    client = AsyncMongoMockClient()
    test_database = client[test_db_name]
    
    print(f"✅ Created in-memory test database: {test_db_name}")
    
    yield test_database
    
    # Cleanup is automatic with mongomock - it's all in memory
    print(f"✅ Test database {test_db_name} cleaned up (in-memory)")
    client.close()


@pytest_asyncio.fixture
async def client(test_db: AsyncIOMotorDatabase) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with dependency overrides."""
    
    # Override the database dependency
    def get_test_database():
        return test_db
    
    app.dependency_overrides[get_database] = get_test_database
    
    # Also need to set up the database manager for the test
    from app.database.mongodb import database_manager
    database_manager.database = test_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()
    database_manager.database = None


@pytest_asyncio.fixture
async def clean_db(test_db: AsyncIOMotorDatabase):
    """Clean the test database before each test."""
    # Drop all collections before each test
    collections = await test_db.list_collection_names()
    for collection_name in collections:
        await test_db[collection_name].drop()
    
    yield
    
    # Optional: Clean up after test as well
    collections = await test_db.list_collection_names()
    for collection_name in collections:
        await test_db[collection_name].drop()


# Test data fixtures
@pytest.fixture
def user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }


@pytest.fixture
def user_data_2():
    """Second user data for testing."""
    return {
        "email": "user2@example.com",
        "password": "password456",
        "full_name": "Second User"
    }


@pytest.fixture
def task_data():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "por_hacer",
        "priority": "media"
    }


@pytest.fixture
def task_data_2():
    """Second task data for testing."""
    return {
        "title": "Another Task",
        "description": "Another test task",
        "status": "en_progreso",
        "priority": "alta"
    }


# Authentication fixtures
@pytest_asyncio.fixture
async def authenticated_user(client: AsyncClient, clean_db, user_data):
    """Create an authenticated user and return user data with tokens."""
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    register_data = response.json()
    
    return {
        "user_data": user_data,
        "access_token": register_data["access_token"],
        "refresh_token": register_data["refresh_token"],
        "user_info": register_data["user"]
    }


@pytest_asyncio.fixture
async def authenticated_user_2(client: AsyncClient, clean_db, user_data_2):
    """Create a second authenticated user for testing user isolation."""
    response = await client.post("/api/v1/auth/register", json=user_data_2)
    assert response.status_code == 201
    register_data = response.json()
    
    return {
        "user_data": user_data_2,
        "access_token": register_data["access_token"],
        "refresh_token": register_data["refresh_token"],
        "user_info": register_data["user"]
    }


@pytest.fixture
def auth_headers():
    """Helper function to create authorization headers."""
    def _auth_headers(access_token: str):
        return {"Authorization": f"Bearer {access_token}"}
    return _auth_headers


@pytest_asyncio.fixture
async def access_token(authenticated_user):
    """Get just the access token for simpler test signatures."""
    return authenticated_user["access_token"] 