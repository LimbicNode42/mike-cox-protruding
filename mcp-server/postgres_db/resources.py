"""
PostgreSQL resources for the MCP server
"""

import json

from mcp.server.fastmcp import FastMCP


def register_postgres_resources(mcp: FastMCP):
    """Register PostgreSQL-related resources with the MCP server"""

    @mcp.resource("postgres://databases")
    def postgres_databases() -> str:
        """List all connected PostgreSQL databases"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        if not db_manager:
            return json.dumps(
                {"error": "PostgreSQL is disabled in the server configuration"},
                indent=2,
            )
        try:
            databases = db_manager.list_databases()
            return json.dumps({"databases": databases}, indent=2)
        except Exception as e:
            return json.dumps(
                {"error": f"Failed to list PostgreSQL databases: {str(e)}"}, indent=2
            )

    @mcp.resource("postgres://databases/{database}/tables")
    def postgres_tables(database: str) -> str:
        """List all tables in a PostgreSQL database"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        if not db_manager:
            return json.dumps(
                {"error": "PostgreSQL is disabled in the server configuration"},
                indent=2,
            )
        try:
            tables = db_manager.list_tables(database)
            return json.dumps({"database": database, "tables": tables}, indent=2)
        except Exception as e:
            return json.dumps(
                {
                    "error": f"Failed to list PostgreSQL tables in '{database}': {str(e)}"
                },
                indent=2,
            )

    @mcp.resource("postgres://databases/{database}/tables/{table_name}/schema")
    def postgres_table_schema(database: str, table_name: str) -> str:
        """Get column information for a PostgreSQL table"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        if not db_manager:
            return json.dumps(
                {"error": "PostgreSQL is disabled in the server configuration"},
                indent=2,
            )
        try:
            info = db_manager.get_table_info(database, table_name)
            return json.dumps(
                {"database": database, "table": table_name, "schema": info}, indent=2
            )
        except Exception as e:
            return json.dumps(
                {
                    "error": f"Failed to get PostgreSQL table info for '{table_name}' in '{database}': {str(e)}"
                },
                indent=2,
            )

    @mcp.resource("postgres://connection")
    def postgres_connection_info() -> str:
        """Get PostgreSQL connection information"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        if not db_manager:
            return json.dumps(
                {"error": "PostgreSQL is disabled in the server configuration"},
                indent=2,
            )

        if not db_manager.databases:
            return json.dumps({"error": "No PostgreSQL connections active"}, indent=2)

        first_db = next(iter(db_manager.databases.values()))
        connection_info = {
            "host": first_db.host,
            "port": first_db.port,
            "user": first_db.user,
            "connected_databases": db_manager.list_databases(),
        }

        return json.dumps({"connection": connection_info}, indent=2)

    @mcp.resource("postgres://databases/{database}/tables/{table_name}/sample")
    def postgres_table_sample(database: str, table_name: str) -> str:
        """Get sample data from a PostgreSQL table (first 10 rows)"""
        ctx = mcp.get_context()
        db_manager = ctx.request_context.lifespan_context.db_manager
        if not db_manager:
            return json.dumps(
                {"error": "PostgreSQL is disabled in the server configuration"},
                indent=2,
            )
        try:
            results = db_manager.query(database, f"SELECT * FROM {table_name} LIMIT 10")
            return json.dumps(
                {
                    "database": database,
                    "table": table_name,
                    "sample_data": results,
                    "note": "Limited to first 10 rows",
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {
                    "error": f"Failed to get sample data from '{table_name}' in '{database}': {str(e)}"
                },
                indent=2,
            )
