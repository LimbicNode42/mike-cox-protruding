"""
Database tools and resources registry for the MCP server
Imports and registers tools and resources from enabled database modules
"""

from mcp.server.fastmcp import FastMCP

from config import AppConfig
from influxdb_db import register_influxdb_resources, register_influxdb_tools
from mongodb_db import register_mongodb_resources, register_mongodb_tools
from postgres_db import register_postgres_resources, register_postgres_tools
from redis_db import register_redis_resources, register_redis_tools


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
