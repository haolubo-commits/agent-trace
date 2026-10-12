"""
Async MongoDB client connection management using Motor.
Provides database access, collection retrieval, and index initialization.
"""

from typing import Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoDBManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


mongodb_manager = MongoDBManager()


async def connect_to_mongo():
    """Initializes MongoDB connection and creates required indexes."""
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    mongodb_manager.client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=2000
    )
    mongodb_manager.db = mongodb_manager.client[settings.DATABASE_NAME]

    # Initialize indexes
    try:
        traces_col = mongodb_manager.db["traces"]
        await traces_col.create_index("trace_id", unique=True)
        await traces_col.create_index("session_id")
        await traces_col.create_index("status")
        await traces_col.create_index("created_at")

        steps_col = mongodb_manager.db["steps"]
        await steps_col.create_index("step_id", unique=True)
        await steps_col.create_index([("trace_id", 1), ("step_index", 1)])
        await steps_col.create_index("parent_step_id")
        await steps_col.create_index("step_type")

        tools_col = mongodb_manager.db["tool_calls"]
        await tools_col.create_index("tool_call_id", unique=True)
        await tools_col.create_index("step_id")
        await tools_col.create_index("trace_id")
        await tools_col.create_index("tool_name")

        logger.info("✓ MongoDB collections and indexes initialized successfully.")
    except Exception as e:
        logger.warning(f"Notice: MongoDB index initialization deferred ({e}).")


async def close_mongo_connection():
    """Closes MongoDB connection on application shutdown."""
    if mongodb_manager.client:
        logger.info("Closing MongoDB connection...")
        mongodb_manager.client.close()
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    """Dependency helper to access current MongoDB database instance."""
    return mongodb_manager.db
