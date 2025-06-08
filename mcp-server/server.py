#!/usr/bin/env python3
"""
Production MCP Server with HTTP Transport
Production-ready version of the MCP server for Docker deployment
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from aiohttp import web, web_request
from postgres_db import DatabaseManager
from redis_db import RedisManager
from mongodb_db import MongoDBManager
from influxdb_db import InfluxDBManager
from config import AppConfig
from tools import register_database_tools, register_database_resources

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/mcp-server.log') if os.path.exists('/var/log') else logging.NullHandler()
    ]
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


class ProductionMCPServer:
    """Production MCP Server with HTTP Transport"""
    
    def __init__(self):
        self.app_context: AppContext | None = None
        self.config = AppConfig.from_env()
        
    async def initialize(self) -> AppContext:
        """Initialize application context with database connections"""
        logger.info("Initializing MCP Server...")
        
        # Initialize database managers based on toggles
        db_manager = None
        redis_manager = None
        mongodb_manager = None
        influxdb_manager = None
        
        if self.config.enable_postgres:
            db_manager = DatabaseManager()
        
        if self.config.enable_redis:
            redis_manager = RedisManager(
                host=self.config.redis.host,
                port=self.config.redis.port,
                password=self.config.redis.password,
                db=self.config.redis.db
            )
        
        if self.config.enable_mongodb:
            mongodb_manager = MongoDBManager(
                host=self.config.mongodb.host,
                port=self.config.mongodb.port,
                user=self.config.mongodb.user,
                password=self.config.mongodb.password,
                database=self.config.mongodb.database
            )
        
        if self.config.enable_influxdb:
            influxdb_manager = InfluxDBManager(
                host=self.config.influxdb.host,
                port=self.config.influxdb.port,
                token=self.config.influxdb.token,
                org=self.config.influxdb.org,
                bucket=self.config.influxdb.bucket
            )
        
        # Connect to enabled databases
        try:
            # Connect to PostgreSQL if enabled
            if self.config.enable_postgres and db_manager:
                try:
                    initial_db = self.config.postgres.database or "postgres"
                    await db_manager.add_database(
                        name=initial_db,
                        host=self.config.postgres.host,
                        port=self.config.postgres.port,
                        database=initial_db,
                        user=self.config.postgres.user,
                        password=self.config.postgres.password
                    )
                    logger.info(f"Connected to PostgreSQL at {self.config.postgres.host}:{self.config.postgres.port}")
                    
                    # Get list of all PostgreSQL databases and connect to them
                    try:
                        all_databases = await db_manager.list_all_databases_from_server()
                        for db_name in all_databases:
                            if db_name != initial_db:
                                try:
                                    await db_manager.add_database(
                                        name=db_name,
                                        host=self.config.postgres.host,
                                        port=self.config.postgres.port,
                                        database=db_name,
                                        user=self.config.postgres.user,
                                        password=self.config.postgres.password
                                    )
                                except Exception as e:
                                    logger.warning(f"Could not connect to PostgreSQL database '{db_name}': {e}")
                    except Exception as e:
                        logger.warning(f"Could not list PostgreSQL databases from server: {e}")
                except Exception as e:
                    logger.warning(f"Could not connect to PostgreSQL: {e}")
            else:
                logger.info("PostgreSQL disabled by configuration")
            
            # Connect to Redis if enabled
            if self.config.enable_redis and redis_manager:
                try:
                    await redis_manager.connect()
                    logger.info(f"Connected to Redis at {self.config.redis.host}:{self.config.redis.port}")
                except Exception as e:
                    logger.warning(f"Could not connect to Redis: {e}")
            else:
                logger.info("Redis disabled by configuration")
            
            # Connect to MongoDB if enabled
            if self.config.enable_mongodb and mongodb_manager:
                try:
                    await mongodb_manager.connect()
                    logger.info(f"Connected to MongoDB at {self.config.mongodb.host}:{self.config.mongodb.port}")
                except Exception as e:
                    logger.warning(f"Could not connect to MongoDB: {e}")
            else:
                logger.info("MongoDB disabled by configuration")
            
            # Connect to InfluxDB if enabled
            if self.config.enable_influxdb and influxdb_manager:
                try:
                    await influxdb_manager.connect()
                    logger.info(f"Connected to InfluxDB at {self.config.influxdb.host}:{self.config.influxdb.port}")
                except Exception as e:
                    logger.warning(f"Could not connect to InfluxDB: {e}")
            else:
                logger.info("InfluxDB disabled by configuration")
                
            self.app_context = AppContext(
                db_manager=db_manager,
                redis_manager=redis_manager,
                mongodb_manager=mongodb_manager,
                influxdb_manager=influxdb_manager,
                config=self.config
            )
            
            return self.app_context
            
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}")
            await self.cleanup()
            raise
    
    async def cleanup(self):
        """Cleanup resources on shutdown"""
        logger.info("Shutting down MCP Server...")
        
        if self.app_context:
            if self.app_context.db_manager:
                await self.app_context.db_manager.disconnect_all()
            if self.app_context.redis_manager:
                await self.app_context.redis_manager.disconnect()
            if self.app_context.mongodb_manager:
                await self.app_context.mongodb_manager.disconnect()
            if self.app_context.influxdb_manager:
                await self.app_context.influxdb_manager.disconnect()
    
    async def handle_request(self, request_data: dict) -> dict:
        """Handle incoming MCP requests"""
        # This is a simplified handler - in a real implementation,
        # you'd use the MCP protocol handlers
        try:
            method = request_data.get("method")
            params = request_data.get("params", {})
            
            if method == "tools/list":
                # Return available tools based on enabled databases
                tools = []
                if self.config.enable_postgres:
                    tools.extend([
                        {"name": "postgres_query", "description": "Execute SQL queries on PostgreSQL"},
                        {"name": "postgres_execute", "description": "Execute SQL statements on PostgreSQL"},
                        {"name": "postgres_create_table", "description": "Create tables in PostgreSQL"},
                        {"name": "postgres_create_database", "description": "Create PostgreSQL databases"}
                    ])
                
                if self.config.enable_redis:
                    tools.extend([
                        {"name": "redis_execute_command", "description": "Execute Redis commands"},
                        {"name": "redis_set_key", "description": "Set Redis key-value pairs"},
                        {"name": "redis_delete_key", "description": "Delete Redis keys"},
                        {"name": "redis_flush_database", "description": "Flush Redis databases"}
                    ])
                
                if self.config.enable_mongodb:
                    tools.extend([
                        {"name": "mongodb_find_documents", "description": "Find MongoDB documents"},
                        {"name": "mongodb_insert_document", "description": "Insert MongoDB documents"},
                        {"name": "mongodb_update_documents", "description": "Update MongoDB documents"},
                        {"name": "mongodb_delete_documents", "description": "Delete MongoDB documents"},
                        {"name": "mongodb_aggregate", "description": "Execute MongoDB aggregations"},
                        {"name": "mongodb_create_collection", "description": "Create MongoDB collections"}
                    ])
                
                if self.config.enable_influxdb:
                    tools.extend([
                        {"name": "influxdb_query", "description": "Execute InfluxDB Flux queries"},
                        {"name": "influxdb_write_data", "description": "Write data to InfluxDB"},
                        {"name": "influxdb_create_bucket", "description": "Create InfluxDB buckets"},
                        {"name": "influxdb_delete_data", "description": "Delete InfluxDB data"}
                    ])
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "result": {"tools": tools}
                }
            
            elif method == "resources/list":
                # Return available resources based on enabled databases
                resources = []
                if self.config.enable_postgres:
                    resources.extend([
                        {"uri": "postgres://databases", "name": "PostgreSQL Databases"},
                        {"uri": "postgres://connection", "name": "PostgreSQL Connection Info"}
                    ])
                
                if self.config.enable_redis:
                    resources.extend([
                        {"uri": "redis://info", "name": "Redis Server Info"},
                        {"uri": "redis://databases", "name": "Redis Databases"}
                    ])
                
                if self.config.enable_mongodb:
                    resources.extend([
                        {"uri": "mongodb://info", "name": "MongoDB Server Info"},
                        {"uri": "mongodb://databases", "name": "MongoDB Databases"}
                    ])
                
                if self.config.enable_influxdb:
                    resources.extend([
                        {"uri": "influxdb://info", "name": "InfluxDB Server Info"},
                        {"uri": "influxdb://buckets", "name": "InfluxDB Buckets"}
                    ])
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "result": {"resources": resources}
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "error": {
                        "code": -32601,
                        "message": "Method not found"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }

    async def run_http_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the MCP server with HTTP transport"""
        import json
        
        async def health_check(request: web_request.Request) -> web.Response:
            """Health check endpoint for load balancers"""
            return web.json_response({"status": "healthy", "version": "1.0.0"})
        
        async def mcp_handler(request: web_request.Request) -> web.Response:
            """Handle MCP protocol requests over HTTP"""
            try:
                request_data = await request.json()
                response_data = await self.handle_request(request_data)
                return web.json_response(response_data)
            except Exception as e:
                logger.error(f"HTTP handler error: {e}")
                return web.json_response({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }, status=400)
        
        # Initialize the server
        await self.initialize()
        
        # Create web application
        app = web.Application()
        app.router.add_get("/health", health_check)
        app.router.add_post("/mcp", mcp_handler)
        
        # Add CORS headers for browser clients
        async def cors_middleware(request: web_request.Request, handler):
            response = await handler(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            return response
        
        app.middlewares.append(cors_middleware)
          # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"MCP Server running on http://{host}:{port}")
        logger.info(f"Health check: http://{host}:{port}/health")
        logger.info(f"MCP endpoint: http://{host}:{port}/mcp")
        
        try:
            # Keep server running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.cleanup()
            await runner.cleanup()


async def create_app(config: AppConfig) -> web.Application:
    """Create and configure the web application for testing"""
    # Create MCP server instance
    server = ProductionMCPServer()
    
    # Initialize with provided config
    server.config = config
    await server.initialize()
    
    # Health check endpoint
    async def health_check(request: web_request.Request) -> web.Response:
        """Health check endpoint"""
        status = {
            "status": "healthy",
            "databases": {}
        }
        
        # Check database connections if enabled
        if server.postgres_manager:
            try:
                async with server.postgres_manager.connection() as conn:
                    await conn.fetchval("SELECT 1")
                status["databases"]["postgres"] = "connected"
            except Exception:
                status["databases"]["postgres"] = "disconnected"
        
        if server.redis_manager:
            try:
                await server.redis_manager.ping()
                status["databases"]["redis"] = "connected"
            except Exception:
                status["databases"]["redis"] = "disconnected"
        
        if server.mongodb_manager:
            try:
                await server.mongodb_manager.client.admin.command('ping')
                status["databases"]["mongodb"] = "connected"
            except Exception:
                status["databases"]["mongodb"] = "disconnected"
        
        if server.influxdb_manager:
            try:
                health = server.influxdb_manager.client.health()
                status["databases"]["influxdb"] = "connected" if health.status == "pass" else "unhealthy"
            except Exception:
                status["databases"]["influxdb"] = "disconnected"
        
        return web.json_response(status)
    
    # MCP protocol handler
    async def mcp_handler(request: web_request.Request) -> web.Response:
        """Handle MCP protocol requests over HTTP"""
        try:
            request_data = await request.json()
            response_data = await server.handle_request(request_data)
            return web.json_response(response_data)
        except Exception as e:
            logger.error(f"HTTP handler error: {e}")
            return web.json_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }, status=400)
    
    # Create web application
    app = web.Application()
    app.router.add_get("/health", health_check)
    app.router.add_post("/mcp", mcp_handler)
    
    # Add CORS headers for browser clients
    async def cors_middleware(request: web_request.Request, handler):
        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    app.middlewares.append(cors_middleware)
    
    # Store server instance in app for cleanup
    app["mcp_server"] = server
    
    return app


async def main():
    """Main entry point for production server"""
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    server = ProductionMCPServer()
    await server.run_http_server(host, port)


if __name__ == "__main__":
    asyncio.run(main())
