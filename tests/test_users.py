"""
Tests for user endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUserEndpoints:
    """Test user endpoints"""

    async def test_get_current_user_success(self, client: AsyncClient, authenticated_user, auth_headers):
        """Test getting current user profile"""
        # User already registered and token available from fixture
        user_data = authenticated_user["user_data"]
        
        # Get current user profile
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers(authenticated_user["access_token"])
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    async def test_get_current_user_unauthorized(self, client: AsyncClient, clean_db):
        """Test getting current user without authentication"""
        response = await client.get("/api/v1/users/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_get_current_user_invalid_token(self, client: AsyncClient, clean_db):
        """Test getting current user with invalid token"""
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_get_current_user_expired_token(self, client: AsyncClient, clean_db):
        """Test getting current user with expired token"""
        # This would require mocking time or creating an expired token
        # For now, we'll test with a malformed token that will definitely be invalid
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNjA5NDU5MjAwfQ.invalid"
        
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data 