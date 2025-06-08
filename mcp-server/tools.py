"""
Database tools and resources registry for the MCP server
Imports and registers tools and resources from all database modules
"""
from mcp.server.fastmcp import FastMCP
from postgres_db import register_postgres_tools, register_postgres_resources
from redis_db import register_redis_tools, register_redis_resources
from mongodb_db import register_mongodb_tools, register_mongodb_resources
from influxdb_db import register_influxdb_tools, register_influxdb_resources


def register_database_tools(mcp: FastMCP):
    """Register all database-related tools with the MCP server"""
    register_postgres_tools(mcp)
    register_redis_tools(mcp)
    register_mongodb_tools(mcp)
    register_influxdb_tools(mcp)


def register_database_resources(mcp: FastMCP):
    """Register all database-related resources with the MCP server"""
    register_postgres_resources(mcp)
    register_redis_resources(mcp)
    register_mongodb_resources(mcp)
    register_influxdb_resources(mcp)
