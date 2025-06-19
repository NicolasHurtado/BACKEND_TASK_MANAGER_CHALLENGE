"""
Test basic application startup
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_app_starts():
    """Test that the app starts without import errors"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200 