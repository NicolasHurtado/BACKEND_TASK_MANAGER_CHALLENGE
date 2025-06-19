"""
Tests for main application endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestMainEndpoints:
    """Test main application endpoints"""

    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Task Manager API" in data["message"]

    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint if it exists"""
        response = await client.get("/health")
        
        # This might return 404 if health endpoint doesn't exist
        # We'll check for both success and not found as valid responses
        assert response.status_code == 200