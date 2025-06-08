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
    async def postgres_list_databases() -> str:
        """List all connected PostgreSQL databases"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        try:
            databases = db_manager.list_databases()
            return f"Connected PostgreSQL databases: {', '.join(databases)}"
        except Exception as e:
            return f"Failed to list PostgreSQL databases: {str(e)}"

    @mcp.tool()
    async def postgres_list_tables(database: str = "postgres") -> str:
        """List all tables in a PostgreSQL database"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        try:
            tables = await db_manager.list_tables(database)
            return f"Tables in PostgreSQL database '{database}': {', '.join(tables)}"
        except Exception as e:
            return f"Failed to list PostgreSQL tables in '{database}': {str(e)}"

    @mcp.tool()
    async def postgres_get_table_info(table_name: str, database: str = "postgres") -> str:
        """Get column information for a PostgreSQL table"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        try:
            info = await db_manager.get_table_info(database, table_name)
            return f"PostgreSQL table '{table_name}' in database '{database}' columns: {info}"
        except Exception as e:
            return f"Failed to get PostgreSQL table info for '{table_name}' in '{database}': {str(e)}"

    @mcp.tool()
    async def postgres_execute(sql: str, database: str = "postgres") -> str:
        """Execute INSERT, UPDATE, or DELETE on PostgreSQL"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        try:
            result = await db_manager.execute(database, sql)
            return f"SQL executed successfully on PostgreSQL '{database}': {result}"
        except Exception as e:
            return f"PostgreSQL SQL execution failed on '{database}': {str(e)}"

    @mcp.tool()
    async def postgres_connection_info() -> str:
        """Get PostgreSQL connection information"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        
        if not db_manager.databases:
            return "No PostgreSQL connections active"
        
        info_lines = ["PostgreSQL Connection Information:"]
        first_db = next(iter(db_manager.databases.values()))
        info_lines.append(f"Host: {first_db.host}")
        info_lines.append(f"Port: {first_db.port}")
        info_lines.append(f"User: {first_db.user}")
        info_lines.append(f"Connected Databases: {', '.join(db_manager.list_databases())}")
        
        return "\n".join(info_lines)
