# Add lifespan support for startup/shutdown with strong typing
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import os

from database import DatabaseManager

from mcp.server.fastmcp import FastMCP

# Create a named server
mcp = FastMCP("Server")

# Specify dependencies for deployment and development
# mcp = FastMCP("Server", dependencies=["pandas", "numpy"])


@dataclass
class AppContext:
    db_manager: DatabaseManager


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    # Initialize PostgreSQL connections to multiple databases
    db_manager = DatabaseManager()
    
    # Get database credentials from environment
    host = os.getenv("POSTGRES_HOST", "192.168.0.50")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD")
    
    # Connect to default postgres database first
    await db_manager.add_database(
        name="postgres",
        host=host,
        port=port,
        database="postgres",
        user=user,
        password=password
    )
    
    # Get list of all databases and connect to them
    try:
        all_databases = await db_manager.list_all_databases_from_server()
        for db_name in all_databases:
            if db_name != "postgres":  # Skip postgres as we already connected
                try:
                    await db_manager.add_database(
                        name=db_name,
                        host=host,
                        port=port,
                        database=db_name,
                        user=user,
                        password=password
                    )
                except Exception as e:
                    print(f"Warning: Could not connect to database '{db_name}': {e}")
    except Exception as e:
        print(f"Warning: Could not list databases from server: {e}")
    
    try:
        yield AppContext(db_manager=db_manager)
    finally:
        # Cleanup on shutdown
        await db_manager.disconnect_all()


# Pass lifespan to server
mcp = FastMCP("Server", lifespan=app_lifespan)


# Access type-safe lifespan context in tools
@mcp.tool()
async def query_db(sql: str, database: str = "postgres") -> str:
    """Execute a SQL query and return the results"""
    ctx = mcp.get_context()
    db_manager = ctx.request_context.lifespan_context.db_manager
    try:
        results = await db_manager.query(database, sql)
        return f"Query executed successfully on '{database}'. Results: {results}"
    except Exception as e:
        return f"Query failed on '{database}': {str(e)}"

@mcp.tool()
async def list_databases() -> str:
    """List all connected databases"""
    ctx = mcp.get_context()
    db_manager = ctx.request_context.lifespan_context.db_manager
    try:
        databases = db_manager.list_databases()
        return f"Connected databases: {', '.join(databases)}"
    except Exception as e:
        return f"Failed to list databases: {str(e)}"

@mcp.tool()
async def list_tables(database: str = "postgres") -> str:
    """List all tables in the specified PostgreSQL database"""
    ctx = mcp.get_context()
    db_manager = ctx.request_context.lifespan_context.db_manager
    try:
        tables = await db_manager.list_tables(database)
        return f"Tables in database '{database}': {', '.join(tables)}"
    except Exception as e:
        return f"Failed to list tables in '{database}': {str(e)}"

@mcp.tool()
async def get_table_info(table_name: str, database: str = "postgres") -> str:
    """Get column information for a specific table in a specific database"""
    ctx = mcp.get_context()
    db_manager = ctx.request_context.lifespan_context.db_manager
    try:
        info = await db_manager.get_table_info(database, table_name)
        return f"Table '{table_name}' in database '{database}' columns: {info}"
    except Exception as e:
        return f"Failed to get table info for '{table_name}' in '{database}': {str(e)}"

@mcp.tool()
async def execute_sql(sql: str, database: str = "postgres") -> str:
    """Execute an INSERT, UPDATE, or DELETE statement on a specific database"""
    ctx = mcp.get_context()
    db_manager = ctx.request_context.lifespan_context.db_manager
    try:
        result = await db_manager.execute(database, sql)
        return f"SQL executed successfully on '{database}': {result}"
    except Exception as e:
        return f"SQL execution failed on '{database}': {str(e)}"

@mcp.tool()
async def get_connection_info() -> str:
    """Get information about the current database connections"""
    ctx = mcp.get_context()
    db_manager = ctx.request_context.lifespan_context.db_manager
    
    if not db_manager.databases:
        return "No database connections active"
    
    info_lines = ["Database Connection Information:"]
    
    # Get connection details from the first database (they all use same host/port)
    first_db = next(iter(db_manager.databases.values()))
    info_lines.append(f"Host: {first_db.host}")
    info_lines.append(f"Port: {first_db.port}")
    info_lines.append(f"User: {first_db.user}")
    info_lines.append(f"Connected Databases: {', '.join(db_manager.list_databases())}")
    
    return "\n".join(info_lines)