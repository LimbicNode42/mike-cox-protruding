"""
MCP Server main entry point
Handles server initialization, lifespan management, and tool registration
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import logging

from postgres_db import DatabaseManager
from redis_db import RedisManager
from mongodb_db import MongoDBManager
from influxdb_db import InfluxDBManager
from config import AppConfig
from tools import register_database_tools
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr so it doesn't interfere with MCP JSON protocol on stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Application context containing shared resources"""
    db_manager: DatabaseManager
    redis_manager: RedisManager
    mongodb_manager: MongoDBManager
    influxdb_manager: InfluxDBManager
    config: AppConfig


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    # Load configuration from environment
    config = AppConfig.from_env()
      # Initialize all database managers
    db_manager = DatabaseManager()
    redis_manager = RedisManager(
        host=config.redis.host,
        port=config.redis.port,
        password=config.redis.password,
        db=config.redis.db
    )
    mongodb_manager = MongoDBManager(
        host=config.mongodb.host,
        port=config.mongodb.port,
        user=None,  # Temporarily disable auth to test connection
        password=None,
        database=config.mongodb.database
    )
    influxdb_manager = InfluxDBManager(
        host=config.influxdb.host,
        port=config.influxdb.port,
        token=config.influxdb.token,
        org=config.influxdb.org,
        bucket=config.influxdb.bucket
    )
    
    # Connect to all databases
    try:        # Connect to PostgreSQL
        initial_db = config.postgres.database or "postgres"
        await db_manager.add_database(
            name=initial_db,
            host=config.postgres.host,
            port=config.postgres.port,
            database=initial_db,
            user=config.postgres.user,
            password=config.postgres.password
        )
          # Get list of all PostgreSQL databases and connect to them
        try:
            all_databases = await db_manager.list_all_databases_from_server()
            for db_name in all_databases:
                if db_name != initial_db:  # Skip the initial database as we already connected
                    try:
                        await db_manager.add_database(
                            name=db_name,
                            host=config.postgres.host,
                            port=config.postgres.port,
                            database=db_name,
                            user=config.postgres.user,
                            password=config.postgres.password
                        )
                    except Exception as e:                        logger.warning(f"Could not connect to PostgreSQL database '{db_name}': {e}")
        except Exception as e:
            logger.warning(f"Could not list PostgreSQL databases from server: {e}")
        
        # Connect to Redis
        try:
            await redis_manager.connect()
            logger.info(f"Connected to Redis at {config.redis.host}:{config.redis.port}")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")
        
        # Connect to MongoDB
        try:
            await mongodb_manager.connect()
            logger.info(f"Connected to MongoDB at {config.mongodb.host}:{config.mongodb.port}")
        except Exception as e:
            logger.warning(f"Could not connect to MongoDB: {e}")
        
        # Connect to InfluxDB
        try:
            await influxdb_manager.connect()
            logger.info(f"Connected to InfluxDB at {config.influxdb.host}:{config.influxdb.port}")
        except Exception as e:
            logger.warning(f"Could not connect to InfluxDB: {e}")
        
        yield AppContext(
            db_manager=db_manager,
            redis_manager=redis_manager,
            mongodb_manager=mongodb_manager,
            influxdb_manager=influxdb_manager,
            config=config
        )
    finally:
        # Cleanup on shutdown
        await db_manager.disconnect_all()
        await redis_manager.disconnect()
        await mongodb_manager.disconnect()
        await influxdb_manager.disconnect()


def create_server() -> FastMCP:
    """Create and configure the MCP server"""
    # Create server with lifespan management
    mcp = FastMCP("Database MCP Server", lifespan=app_lifespan)
    
    # Register all database tools
    register_database_tools(mcp)
    
    return mcp


# Create the server instance
mcp = create_server()


if __name__ == "__main__":
    """Run the server when executed directly"""
    # FastMCP handles its own event loop
    mcp.run()