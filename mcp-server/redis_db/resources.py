"""
Redis resources for the MCP server
"""
from mcp.server.fastmcp import FastMCP
import json


def register_redis_resources(mcp: FastMCP):
    """Register Redis-related resources with the MCP server"""
    
    @mcp.resource("redis://info")
    async def redis_server_info() -> str:
        """Get Redis server information"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            info = await redis_manager.get_info()
            return json.dumps({"server_info": info}, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": f"Failed to get Redis info: {str(e)}"}, indent=2)
    
    @mcp.resource("redis://databases")
    async def redis_databases() -> str:
        """List Redis databases with data"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            databases = await redis_manager.get_databases()
            return json.dumps({"databases": databases}, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Failed to list Redis databases: {str(e)}"}, indent=2)
    
    @mcp.resource("redis://databases/{database}/keys")
    async def redis_database_keys(database: int) -> str:
        """List Redis keys in specified database (pattern: *)"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            keys = await redis_manager.get_keys("*", database)
            return json.dumps({
                "database": database,
                "keys": keys,
                "pattern": "*"
            }, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Failed to list Redis keys: {str(e)}"}, indent=2)
    
    @mcp.resource("redis://databases/{database}/keys/{key}/info")
    async def redis_key_info(database: int, key: str) -> str:
        """Get information about a Redis key"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            info = await redis_manager.get_key_info(key, database)
            return json.dumps({
                "database": database,
                "key": key,
                "info": info
            }, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": f"Failed to get Redis key info: {str(e)}"}, indent=2)
    
    @mcp.resource("redis://databases/{database}/keys/{key}/value")
    async def redis_key_value(database: int, key: str) -> str:
        """Get value of a Redis key"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            value = await redis_manager.get_value(key, database)
            return json.dumps({
                "database": database,
                "key": key,
                "value": value
            }, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": f"Failed to get Redis key value: {str(e)}"}, indent=2)
