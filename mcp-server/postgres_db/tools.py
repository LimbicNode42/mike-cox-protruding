"""
PostgreSQL tools for the MCP server
"""
from mcp.server.fastmcp import FastMCP


def register_postgres_tools(mcp: FastMCP):
    """Register PostgreSQL-related tools with the MCP server"""
    
    @mcp.tool()
    async def postgres_query(sql: str, database: str = "postgres") -> str:
        """Execute a SQL query on PostgreSQL and return the results"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        try:
            results = await db_manager.query(database, sql)
            return f"Query executed successfully on PostgreSQL '{database}'. Results: {results}"
        except Exception as e:
            return f"PostgreSQL query failed on '{database}': {str(e)}"

    @mcp.tool()
    async def postgres_execute(sql: str, database: str = "postgres") -> str:
        """Execute INSERT, UPDATE, DELETE, or DDL statements on PostgreSQL"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        try:
            result = await db_manager.execute(database, sql)
            return f"SQL executed successfully on PostgreSQL '{database}': {result}"
        except Exception as e:
            return f"PostgreSQL SQL execution failed on '{database}': {str(e)}"

    @mcp.tool()
    async def postgres_create_table(database: str, table_name: str, columns: str) -> str:
        """Create a new table in PostgreSQL database
        
        Args:
            database: Target database name
            table_name: Name of the table to create
            columns: Column definitions (e.g., "id SERIAL PRIMARY KEY, name VARCHAR(100), email VARCHAR(255)")
        """
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        try:
            sql = f"CREATE TABLE {table_name} ({columns})"
            result = await db_manager.execute(database, sql)
            return f"Table '{table_name}' created successfully in PostgreSQL '{database}': {result}"
        except Exception as e:
            return f"Failed to create table '{table_name}' in PostgreSQL '{database}': {str(e)}"

    @mcp.tool()
    async def postgres_create_database(database_name: str) -> str:
        """Create a new PostgreSQL database"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        try:
            # Use the default 'postgres' database to create new database
            sql = f"CREATE DATABASE {database_name}"
            result = await db_manager.execute("postgres", sql)
            return f"Database '{database_name}' created successfully: {result}"
        except Exception as e:
            return f"Failed to create PostgreSQL database '{database_name}': {str(e)}"
