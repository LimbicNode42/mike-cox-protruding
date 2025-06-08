"""
Redis tools for the MCP server
"""

import json

from mcp.server.fastmcp import FastMCP


def register_redis_tools(mcp: FastMCP):
    """Register Redis-related tools with the MCP server"""

    @mcp.tool()
    async def redis_execute_command(command: str, *args) -> str:
        """Execute a Redis command"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        if not redis_manager:
            return "Redis is disabled in the server configuration"
        try:
            result = await redis_manager.execute_command(command, *args)
            return f"Redis command result: {json.dumps(result, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to execute Redis command: {str(e)}"

    @mcp.tool()
    async def redis_set_key(key: str, value: str, database: int = 0) -> str:
        """Set a Redis key-value pair"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        if not redis_manager:
            return "Redis is disabled in the server configuration"
        try:
            result = await redis_manager.execute_command("SET", key, value)
            await redis_manager.execute_command("SELECT", database)
            return (
                f"Redis key '{key}' set successfully in database {database}: {result}"
            )
        except Exception as e:
            return f"Failed to set Redis key '{key}': {str(e)}"

    @mcp.tool()
    async def redis_delete_key(key: str, database: int = 0) -> str:
        """Delete a Redis key"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        if not redis_manager:
            return "Redis is disabled in the server configuration"
        try:
            await redis_manager.execute_command("SELECT", database)
            result = await redis_manager.execute_command("DEL", key)
            return f"Redis key '{key}' deleted from database {database}: {result} key(s) removed"
        except Exception as e:
            return f"Failed to delete Redis key '{key}': {str(e)}"

    @mcp.tool()
    async def redis_flush_database(database: int = 0) -> str:
        """Flush all keys from a Redis database"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        if not redis_manager:
            return "Redis is disabled in the server configuration"
        try:
            await redis_manager.execute_command("SELECT", database)
            result = await redis_manager.execute_command("FLUSHDB")
            return f"Redis database {database} flushed successfully: {result}"
        except Exception as e:
            return f"Failed to flush Redis database {database}: {str(e)}"
