"""
Database tools registry for the MCP server
Imports and registers tools from all database modules
"""
from mcp.server.fastmcp import FastMCP
from postgres_db.tools import register_postgres_tools
from redis_db.tools import register_redis_tools
from mongodb_db.tools import register_mongodb_tools
from influxdb_db.tools import register_influxdb_tools


def register_database_tools(mcp: FastMCP):
    """Register all database-related tools with the MCP server"""
    register_postgres_tools(mcp)
    register_redis_tools(mcp)
    register_mongodb_tools(mcp)
    register_influxdb_tools(mcp)
