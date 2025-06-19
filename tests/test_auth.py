"""
Tests for authentication endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test authentication endpoints"""

    async def test_register_user_success(self, client: AsyncClient, clean_db, user_data):
        """Test successful user registration"""
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["full_name"] == user_data["full_name"]
        assert data["user"]["is_active"] is True
        assert "id" in data["user"]

    async def test_register_user_duplicate_email(self, client: AsyncClient, authenticated_user, user_data):
        """Test registration with duplicate email"""
        # First user already registered by authenticated_user fixture
        
        # Try to register with same email
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "ya está registrado" in data["detail"].lower()

    async def test_register_user_invalid_email(self, client: AsyncClient, clean_db):
        """Test registration with invalid email"""
        invalid_data = {
            "email": "invalid-email",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        response = await client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_register_user_weak_password(self, client: AsyncClient, clean_db):
        """Test registration with weak password"""
        weak_password_data = {
            "email": "test@example.com",
            "password": "123",  # Too short
            "full_name": "Test User"
        }
        
        response = await client.post("/api/v1/auth/register", json=weak_password_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_login_success(self, client: AsyncClient, authenticated_user):
        """Test successful login"""
        # User already registered by authenticated_user fixture
        user_data = authenticated_user["user_data"]
        
        # Now try to login
        login_data = {
            "username": user_data["email"],  # FastAPI OAuth2 uses 'username' field
            "password": user_data["password"]
        }
        
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,  # Use data instead of json for form data
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient, authenticated_user):
        """Test login with invalid credentials"""
        # User already registered by authenticated_user fixture
        user_data = authenticated_user["user_data"]
        
        # Try to login with wrong password
        login_data = {
            "username": user_data["email"],
            "password": "wrongpassword"
        }
        
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_login_nonexistent_user(self, client: AsyncClient, clean_db):
        """Test login with non-existent user"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_refresh_token_success(self, client: AsyncClient, authenticated_user):
        """Test successful token refresh"""
        # User already registered and tokens available from fixture
        refresh_token = authenticated_user["refresh_token"]
        
        # Use refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_token_invalid(self, client: AsyncClient, clean_db):
        """Test refresh with invalid token"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_refresh_token_missing(self, client: AsyncClient, clean_db):
        """Test refresh without token"""
        response = await client.post("/api/v1/auth/refresh", json={})
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data 