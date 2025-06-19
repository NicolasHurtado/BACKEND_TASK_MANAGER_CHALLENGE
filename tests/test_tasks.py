"""
Tests for task endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTaskEndpoints:
    """Test task endpoints"""

    async def test_create_task_success(self, client: AsyncClient, authenticated_user, task_data, auth_headers):
        """Test successful task creation"""
        # Create task
        response = await client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=auth_headers(authenticated_user["access_token"])
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["status"] == task_data["status"]
        assert data["priority"] == task_data["priority"]
        assert "id" in data
        assert "created_at" in data
        assert "user_id" in data

    async def test_create_task_unauthorized(self, client: AsyncClient, clean_db, task_data):
        """Test task creation without authentication"""
        response = await client.post("/api/v1/tasks/", json=task_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_create_task_invalid_data(self, client: AsyncClient, authenticated_user, auth_headers):
        """Test task creation with invalid data"""        
        # Try to create task with invalid data
        invalid_task_data = {
            "title": "",  # Empty title
            "status": "invalid_status",  # Invalid status
            "priority": "invalid_priority"  # Invalid priority
        }
        
        response = await client.post(
            "/api/v1/tasks/",
            json=invalid_task_data,
            headers=auth_headers(authenticated_user["access_token"])
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_get_user_tasks_success(self, client: AsyncClient, authenticated_user, task_data, task_data_2, auth_headers):
        """Test getting user's tasks"""
        headers = auth_headers(authenticated_user["access_token"])
        
        # Create multiple tasks
        await client.post("/api/v1/tasks/", json=task_data, headers=headers)
        await client.post("/api/v1/tasks/", json=task_data_2, headers=headers)
        
        # Get tasks
        response = await client.get("/api/v1/tasks/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Check that tasks belong to the user
        for task in data:
            assert "id" in task
            assert "title" in task
            assert "status" in task
            assert "priority" in task
            assert "user_id" in task

    async def test_get_user_tasks_empty(self, client: AsyncClient, authenticated_user, auth_headers):
        """Test getting tasks when user has no tasks"""
        # Get tasks (should be empty)
        response = await client.get(
            "/api/v1/tasks/",
            headers=auth_headers(authenticated_user["access_token"])
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_get_task_by_id_success(self, client: AsyncClient, authenticated_user, task_data, auth_headers):
        """Test getting a specific task by ID"""
        headers = auth_headers(authenticated_user["access_token"])
        
        # Create task
        create_response = await client.post("/api/v1/tasks/", json=task_data, headers=headers)
        task_id = create_response.json()["id"]
        
        # Get task by ID
        response = await client.get(f"/api/v1/tasks/{task_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["status"] == task_data["status"]
        assert data["priority"] == task_data["priority"]

    async def test_get_task_by_id_not_found(self, client: AsyncClient, authenticated_user, auth_headers):
        """Test getting a non-existent task"""
        # Try to get non-existent task
        fake_task_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format
        response = await client.get(
            f"/api/v1/tasks/{fake_task_id}",
            headers=auth_headers(authenticated_user["access_token"])
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    async def test_update_task_success(self, client: AsyncClient, authenticated_user, task_data, auth_headers):
        """Test successful task update"""
        headers = auth_headers(authenticated_user["access_token"])
        
        # Create task
        create_response = await client.post("/api/v1/tasks/", json=task_data, headers=headers)
        task_id = create_response.json()["id"]
        
        # Update task
        update_data = {
            "title": "Updated Task Title",
            "status": "completada",
            "priority": "alta"
        }
        
        response = await client.put(f"/api/v1/tasks/{task_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["status"] == update_data["status"]
        assert data["priority"] == update_data["priority"]
        assert data["id"] == task_id

    async def test_update_task_not_found(self, client: AsyncClient, authenticated_user, auth_headers):
        """Test updating a non-existent task"""
        # Try to update non-existent task
        fake_task_id = "507f1f77bcf86cd799439011"
        update_data = {"title": "Updated Title"}
        
        response = await client.put(
            f"/api/v1/tasks/{fake_task_id}",
            json=update_data,
            headers=auth_headers(authenticated_user["access_token"])
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    async def test_delete_task_success(self, client: AsyncClient, authenticated_user, task_data, auth_headers):
        """Test successful task deletion"""
        headers = auth_headers(authenticated_user["access_token"])
        
        # Create task
        create_response = await client.post("/api/v1/tasks/", json=task_data, headers=headers)
        task_id = create_response.json()["id"]
        
        # Delete task
        response = await client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
        assert response.status_code == 204
        
        # Verify task is deleted
        get_response = await client.get(f"/api/v1/tasks/{task_id}", headers=headers)
        assert get_response.status_code == 404

    async def test_delete_task_not_found(self, client: AsyncClient, authenticated_user, auth_headers):
        """Test deleting a non-existent task"""
        # Try to delete non-existent task
        fake_task_id = "507f1f77bcf86cd799439011"
        
        response = await client.delete(
            f"/api/v1/tasks/{fake_task_id}",
            headers=auth_headers(authenticated_user["access_token"])
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    async def test_task_isolation_between_users(self, client: AsyncClient, authenticated_user, authenticated_user_2, task_data, auth_headers):
        """Test that users can only access their own tasks"""
        headers_1 = auth_headers(authenticated_user["access_token"])
        headers_2 = auth_headers(authenticated_user_2["access_token"])
        
        # User 1 creates a task
        create_response = await client.post("/api/v1/tasks/", json=task_data, headers=headers_1)
        task_id = create_response.json()["id"]
        
        # User 2 tries to access User 1's task
        response = await client.get(f"/api/v1/tasks/{task_id}", headers=headers_2)
        assert response.status_code == 404  # Should not find task that doesn't belong to user
        
        # User 2 gets their tasks (should be empty)
        response = await client.get("/api/v1/tasks/", headers=headers_2)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0 