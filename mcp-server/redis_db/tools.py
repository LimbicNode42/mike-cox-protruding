"""
Redis tools for the MCP server
"""
from mcp.server.fastmcp import FastMCP
import json


def register_redis_tools(mcp: FastMCP):
    """Register Redis-related tools with the MCP server"""
    
    @mcp.tool()
    async def redis_info() -> str:
        """Get Redis server information"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            info = await redis_manager.get_info()
            return f"Redis server info: {json.dumps(info, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get Redis info: {str(e)}"
    
    @mcp.tool()
    async def redis_list_databases() -> str:
        """List Redis databases with data"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            databases = await redis_manager.get_databases()
            return f"Redis databases with data: {databases}"
        except Exception as e:
            return f"Failed to list Redis databases: {str(e)}"
    
    @mcp.tool()
    async def redis_list_keys(pattern: str = "*", database: int = 0) -> str:
        """List Redis keys matching pattern in specified database"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            keys = await redis_manager.get_keys(pattern, database)
            return f"Redis keys in database {database} matching '{pattern}': {keys}"
        except Exception as e:
            return f"Failed to list Redis keys: {str(e)}"
    
    @mcp.tool()
    async def redis_get_key_info(key: str, database: int = 0) -> str:
        """Get information about a Redis key"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            info = await redis_manager.get_key_info(key, database)
            return f"Redis key '{key}' info: {json.dumps(info, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get Redis key info: {str(e)}"
    
    @mcp.tool()
    async def redis_get_value(key: str, database: int = 0) -> str:
        """Get value of a Redis key"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            value = await redis_manager.get_value(key, database)
            return f"Redis key '{key}' value: {json.dumps(value, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get Redis key value: {str(e)}"
    
    @mcp.tool()
    async def redis_execute_command(command: str, *args) -> str:
        """Execute a Redis command"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            result = await redis_manager.execute_command(command, *args)
            return f"Redis command result: {json.dumps(result, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to execute Redis command: {str(e)}"
