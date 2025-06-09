"""
Redis resources for the MCP server
"""

import json

from mcp.server.fastmcp import FastMCP


def register_redis_resources(mcp: FastMCP):
    """Register Redis-related resources with the MCP server"""

    @mcp.resource("redis://info")
    def redis_server_info() -> str:
        """Get Redis server information"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        if not redis_manager:
            return json.dumps(
                {"error": "Redis is disabled in the server configuration"}, indent=2
            )
        try:
            info = redis_manager.get_info()
            return json.dumps({"server_info": info}, indent=2, default=str)
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to get Redis info: {str(e)}"}, indent=2
            )

    @mcp.resource("redis://databases")
    def redis_databases() -> str:
        """List Redis databases with data"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        if not redis_manager:
            return json.dumps(
                {"error": "Redis is disabled in the server configuration"}, indent=2
            )
        try:
            databases = redis_manager.get_databases()
            return json.dumps({"databases": databases}, indent=2)
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to list Redis databases: {str(e)}"}, indent=2
            )

    @mcp.resource("redis://databases/{database}/keys")
    def redis_database_keys(database: int) -> str:
        """List Redis keys in specified database (pattern: *)"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        if not redis_manager:
            return json.dumps(
                {"error": "Redis is disabled in the server configuration"}, indent=2
            )
        try:
            keys = redis_manager.get_keys("*", database)
            return json.dumps(
                {"database": database, "keys": keys, "pattern": "*"}, indent=2
            )
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to list Redis keys: {str(e)}"}, indent=2
            )

    @mcp.resource("redis://databases/{database}/keys/{key}/info")
    def redis_key_info(database: int, key: str) -> str:
        """Get information about a Redis key"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        if not redis_manager:
            return json.dumps(
                {"error": "Redis is disabled in the server configuration"}, indent=2
            )
        try:
            info = redis_manager.get_key_info(key, database)
            return json.dumps(
                {"database": database, "key": key, "info": info}, indent=2, default=str
            )
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to get Redis key info: {str(e)}"}, indent=2
            )

    @mcp.resource("redis://databases/{database}/keys/{key}/value")
    def redis_key_value(database: int, key: str) -> str:
        """Get value of a Redis key"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        if not redis_manager:
            return json.dumps(
                {"error": "Redis is disabled in the server configuration"}, indent=2
            )
        try:
            value = redis_manager.get_value(key, database)
            return json.dumps(
                {"database": database, "key": key, "value": value},
                indent=2,
                default=str,
            )
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to get Redis key value: {str(e)}"}, indent=2
            )
