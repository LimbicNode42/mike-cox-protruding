"""
Database tools and resources registry for the MCP server
Imports and registers tools and resources from enabled database modules
"""

from mcp.server.fastmcp import FastMCP
from postgres_db import register_postgres_tools, register_postgres_resources
from redis_db import register_redis_tools, register_redis_resources
from mongodb_db import register_mongodb_tools, register_mongodb_resources
from influxdb_db import register_influxdb_tools, register_influxdb_resources
from config import AppConfig


def register_database_tools(mcp: FastMCP, config: AppConfig):
    """Register database-related tools with the MCP server based on config toggles"""
    if config.enable_postgres:
        register_postgres_tools(mcp)
    if config.enable_redis:
        register_redis_tools(mcp)
    if config.enable_mongodb:
        register_mongodb_tools(mcp)
    if config.enable_influxdb:
        register_influxdb_tools(mcp)


def register_database_resources(mcp: FastMCP, config: AppConfig):
    """Register database-related resources with the MCP server based on config toggles"""
    if config.enable_postgres:
        register_postgres_resources(mcp)
    if config.enable_redis:
        register_redis_resources(mcp)
    if config.enable_mongodb:
        register_mongodb_resources(mcp)
    if config.enable_influxdb:
        register_influxdb_resources(mcp)
