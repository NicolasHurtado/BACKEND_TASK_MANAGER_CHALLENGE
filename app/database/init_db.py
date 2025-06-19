"""
Database initialization script
"""

import asyncio
import logging

from app.database.mongodb import connect_to_mongo, get_database, close_mongo_connection
from app.repositories.user_repository import UserRepository
from app.repositories.task_repository import TaskRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database() -> None:
    """Initialize database with indexes and initial data"""
    try:
        # Connect to database
        await connect_to_mongo()
        logger.info("Conectado a MongoDB")
        
        # Get database instance
        database = get_database()
        
        # Initialize repositories
        user_repo = UserRepository(database)
        task_repo = TaskRepository(database)
        
        # Create indexes
        logger.info("Creando índices para usuarios...")
        await user_repo.create_indexes()
        
        logger.info("Creando índices para tareas...")
        await task_repo.create_indexes()
        
        logger.info("✅ Base de datos inicializada exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error inicializando la base de datos: {e}")
        raise
    finally:
        # Close connection
        await close_mongo_connection()


async def main() -> None:
    """Main function"""
    await init_database()


if __name__ == "__main__":
    asyncio.run(main()) 