"""
Test database connection
"""

import pytest
from mongomock_motor import AsyncMongoMockClient


@pytest.mark.asyncio
async def test_in_memory_database_connection():
    """Test that we can connect to the in-memory test database"""
    
    # Test connection to in-memory MongoDB mock
    client = AsyncMongoMockClient()
    
    # Test basic operations
    test_db = client.test_database
    test_collection = test_db.test_collection
    
    # Insert a document
    result = await test_collection.insert_one({"test": "value"})
    assert result.inserted_id is not None
    
    # Find the document
    doc = await test_collection.find_one({"test": "value"})
    assert doc is not None
    assert doc["test"] == "value"
    
    print("✅ In-memory MongoDB mock works correctly")
    client.close()


@pytest.mark.asyncio
async def test_test_database_fixture(test_db):
    """Test that the test_db fixture works"""
    
    # Try to insert and retrieve a test document
    test_collection = test_db.test_collection
    
    test_doc = {"test": "document", "value": 123}
    result = await test_collection.insert_one(test_doc)
    assert result.inserted_id is not None
    
    # Retrieve the document
    found_doc = await test_collection.find_one({"_id": result.inserted_id})
    assert found_doc is not None
    assert found_doc["test"] == "document"
    assert found_doc["value"] == 123
    
    print("✅ Test database fixture works correctly")
    
    # Clean up
    await test_collection.delete_one({"_id": result.inserted_id}) 