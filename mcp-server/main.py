"""
MCP Server main entry point
Handles server initialization, lifespan management, and tool registration
"""

import argparse
import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP

from config import AppConfig
from influxdb_db import InfluxDBManager
from mongodb_db import MongoDBManager
from postgres_db import DatabaseManager
from redis_db import RedisManager
from tools import register_database_resources, register_database_tools


# Configure logging based on mode (stderr for stdio, normal for HTTP)
def configure_logging(mode: str = "stdio"):
    if mode == "stdio":
        # For MCP Inspector - log to stderr so it doesn't interfere with JSON protocol on stdout
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
    else:
        # For HTTP mode - normal logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Application context containing shared resources"""

    db_manager: DatabaseManager | None = None
    redis_manager: RedisManager | None = None
    mongodb_manager: MongoDBManager | None = None
    influxdb_manager: InfluxDBManager | None = None
    config: AppConfig = None


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    # Load configuration from environment
    config = AppConfig.from_env()

    # Initialize database managers based on toggles
    db_manager = None
    redis_manager = None
    mongodb_manager = None
    influxdb_manager = None

    if config.enable_postgres:
        db_manager = DatabaseManager()

    if config.enable_redis:
        redis_manager = RedisManager(
            host=config.redis.host,
            port=config.redis.port,
            password=config.redis.password,
            db=config.redis.db,
        )

    if config.enable_mongodb:
        mongodb_manager = MongoDBManager(
            host=config.mongodb.host,
            port=config.mongodb.port,
            user=None,  # Temporarily disable auth to test connection
            password=None,
            database=config.mongodb.database,
        )

    if config.enable_influxdb:
        influxdb_manager = InfluxDBManager(
            host=config.influxdb.host,
            port=config.influxdb.port,
            token=config.influxdb.token,
            org=config.influxdb.org,
            bucket=config.influxdb.bucket,
        )
    # Connect to enabled databases
    try:  # Connect to PostgreSQL if enabled
        if config.enable_postgres and db_manager:
            try:
                initial_db = config.postgres.database or "postgres"
                db_manager.add_database(
                    name=initial_db,
                    host=config.postgres.host,
                    port=config.postgres.port,
                    database=initial_db,
                    user=config.postgres.user,
                    password=config.postgres.password,
                )
                logger.info(
                    f"Connected to PostgreSQL at {config.postgres.host}:{config.postgres.port}"
                )

                # Get list of all PostgreSQL databases and connect to them
                try:
                    all_databases = db_manager.list_all_databases_from_server()
                    for db_name in all_databases:
                        if (
                            db_name != initial_db
                        ):  # Skip the initial database as we already connected
                            try:
                                db_manager.add_database(
                                    name=db_name,
                                    host=config.postgres.host,
                                    port=config.postgres.port,
                                    database=db_name,
                                    user=config.postgres.user,
                                    password=config.postgres.password,
                                )
                            except Exception as e:
                                logger.warning(
                                    f"Could not connect to PostgreSQL database '{db_name}': {e}"
                                )
                except Exception as e:
                    logger.warning(
                        f"Could not list PostgreSQL databases from server: {e}"
                    )
            except Exception as e:
                logger.warning(f"Could not connect to PostgreSQL: {e}")
        else:
            logger.info("PostgreSQL disabled by configuration")

        # Connect to Redis if enabled
        if config.enable_redis and redis_manager:
            try:
                redis_manager.connect()
                logger.info(
                    f"Connected to Redis at {config.redis.host}:{config.redis.port}"
                )
            except Exception as e:
                logger.warning(f"Could not connect to Redis: {e}")
        else:
            logger.info("Redis disabled by configuration")

        # Connect to MongoDB if enabled
        if config.enable_mongodb and mongodb_manager:
            try:
                mongodb_manager.connect()
                logger.info(
                    f"Connected to MongoDB at {config.mongodb.host}:{config.mongodb.port}"
                )
            except Exception as e:
                logger.warning(f"Could not connect to MongoDB: {e}")
        else:
            logger.info("MongoDB disabled by configuration")

        # Connect to InfluxDB if enabled
        if config.enable_influxdb and influxdb_manager:
            try:
                influxdb_manager.connect()
                logger.info(
                    f"Connected to InfluxDB at {config.influxdb.host}:{config.influxdb.port}"
                )
            except Exception as e:
                logger.warning(f"Could not connect to InfluxDB: {e}")
        else:
            logger.info("InfluxDB disabled by configuration")

        yield AppContext(
            db_manager=db_manager,
            redis_manager=redis_manager,
            mongodb_manager=mongodb_manager,
            influxdb_manager=influxdb_manager,
            config=config,
        )
    finally:
        # Cleanup on shutdown
        if db_manager:
            db_manager.disconnect_all()
        if redis_manager:
            redis_manager.disconnect()
        if mongodb_manager:
            mongodb_manager.disconnect()
        if influxdb_manager:
            influxdb_manager.disconnect()


def create_server() -> FastMCP:
    """Create and configure the MCP server"""
    # Load configuration to determine which tools/resources to register
    config = AppConfig.from_env()

    # Create server with lifespan management
    mcp = FastMCP("Database MCP Server", lifespan=app_lifespan)

    # Register database tools and resources based on config toggles
    register_database_tools(mcp, config)
    register_database_resources(mcp, config)

    return mcp


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Database MCP Server")
    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default="stdio",
        help="Server mode: stdio for MCP Inspector, http for production",
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (HTTP mode only)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (HTTP mode only)"
    )
    return parser.parse_args()


async def run_http_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the server in HTTP mode using uvicorn"""
    import uvicorn

    # Create the MCP server
    mcp = create_server()

    # Get the Starlette app from FastMCP for streamable HTTP transport
    app = mcp.streamable_http_app()

    # Configure uvicorn
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
    )

    # Run the server
    server = uvicorn.Server(config)
    logger.info(f"Starting Database MCP Server in HTTP mode on {host}:{port}")
    await server.serve()


if __name__ == "__main__":
    """Run the server when executed directly"""
    args = parse_arguments()

    # Configure logging based on mode
    configure_logging(args.mode)

    if args.mode == "http":
        # Run HTTP server with uvicorn
        asyncio.run(run_http_server(args.host, args.port))
