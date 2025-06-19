"""
MongoDB database configuration and connection management
"""

import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """MongoDB database connection manager"""
    
    def __init__(self) -> None:
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.settings = get_settings()

    async def connect_to_database(self) -> None:
        """Create database connection"""
        try:
            logger.info("Conectando a MongoDB...")
            self.client = AsyncIOMotorClient(
                self.settings.MONGODB_URL,
                maxPoolSize=10,
                minPoolSize=5,
                serverSelectionTimeoutMS=5000,
            )
            
            # Test the connection
            await self.client.admin.command('ping')
            
            self.database = self.client[self.settings.DATABASE_NAME]
            logger.info(f"✅ Conectado exitosamente a MongoDB: {self.settings.DATABASE_NAME}")
            
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            raise

    async def close_database_connection(self) -> None:
        """Close database connection"""
        if self.client is not None:
            logger.info("Cerrando conexión a MongoDB...")
            self.client.close()
            logger.info("✅ Conexión cerrada exitosamente")

    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if self.database is None:
            raise RuntimeError("Database not connected. Call connect_to_database() first.")
        return self.database


# Global database manager instance
database_manager = DatabaseManager()


async def connect_to_mongo() -> None:
    """Connect to MongoDB"""
    await database_manager.connect_to_database()


async def close_mongo_connection() -> None:
    """Close MongoDB connection"""
    await database_manager.close_database_connection()


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance for dependency injection"""
    return database_manager.get_database() 