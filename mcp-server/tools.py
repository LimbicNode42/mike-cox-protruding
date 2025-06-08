"""
Database tools and resources for the MCP server
Organized by database type: PostgreSQL, Redis, MongoDB, InfluxDB
"""
from mcp.server.fastmcp import FastMCP
import json


def register_database_tools(mcp: FastMCP):
    """Register all database-related tools with the MCP server"""
    
    # =============================================================================
    # POSTGRESQL TOOLS
    # =============================================================================
    
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
    
    # =============================================================================
    # REDIS TOOLS
    # =============================================================================
    
    @mcp.tool()
    async def redis_info() -> str:
        """Get Redis server information"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            info = await redis_manager.get_info()
            return f"Redis server info: {json.dumps(info, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get Redis info: {str(e)}"
    
    @mcp.tool()
    async def redis_list_databases() -> str:
        """List Redis databases with data"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            databases = await redis_manager.get_databases()
            return f"Redis databases with data: {databases}"
        except Exception as e:
            return f"Failed to list Redis databases: {str(e)}"
    
    @mcp.tool()
    async def redis_list_keys(pattern: str = "*", database: int = 0) -> str:
        """List Redis keys matching pattern in specified database"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            keys = await redis_manager.get_keys(pattern, database)
            return f"Redis keys in database {database} matching '{pattern}': {keys}"
        except Exception as e:
            return f"Failed to list Redis keys: {str(e)}"
    
    @mcp.tool()
    async def redis_get_key_info(key: str, database: int = 0) -> str:
        """Get information about a Redis key"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            info = await redis_manager.get_key_info(key, database)
            return f"Redis key '{key}' info: {json.dumps(info, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get Redis key info: {str(e)}"
    
    @mcp.tool()
    async def redis_get_value(key: str, database: int = 0) -> str:
        """Get value of a Redis key"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            value = await redis_manager.get_value(key, database)
            return f"Redis key '{key}' value: {json.dumps(value, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get Redis key value: {str(e)}"
    
    @mcp.tool()
    async def redis_execute_command(command: str, *args) -> str:
        """Execute a Redis command"""
        ctx = mcp.get_context()
        redis_manager = ctx.request_context.lifespan_context.redis_manager
        try:
            result = await redis_manager.execute_command(command, *args)
            return f"Redis command result: {json.dumps(result, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to execute Redis command: {str(e)}"
    
    # =============================================================================
    # MONGODB TOOLS
    # =============================================================================
    
    @mcp.tool()
    async def mongodb_server_info() -> str:
        """Get MongoDB server information"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            info = await mongodb_manager.get_server_info()
            return f"MongoDB server info: {json.dumps(info, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get MongoDB server info: {str(e)}"
    
    @mcp.tool()
    async def mongodb_list_databases() -> str:
        """List all MongoDB databases"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            databases = await mongodb_manager.get_databases()
            return f"MongoDB databases: {databases}"
        except Exception as e:
            return f"Failed to list MongoDB databases: {str(e)}"
    
    @mcp.tool()
    async def mongodb_database_info(database: str) -> str:
        """Get information about a MongoDB database"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            info = await mongodb_manager.get_database_info(database)
            return f"MongoDB database '{database}' info: {json.dumps(info, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get MongoDB database info: {str(e)}"
    
    @mcp.tool()
    async def mongodb_list_collections(database: str) -> str:
        """List collections in a MongoDB database"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            collections = await mongodb_manager.get_collections(database)
            return f"MongoDB collections in '{database}': {collections}"
        except Exception as e:
            return f"Failed to list MongoDB collections: {str(e)}"
    
    @mcp.tool()
    async def mongodb_collection_info(database: str, collection: str) -> str:
        """Get information about a MongoDB collection"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            info = await mongodb_manager.get_collection_info(database, collection)
            return f"MongoDB collection '{collection}' info: {json.dumps(info, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get MongoDB collection info: {str(e)}"
    
    @mcp.tool()
    async def mongodb_collection_schema(database: str, collection: str, sample_size: int = 100) -> str:
        """Analyze MongoDB collection schema"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            schema = await mongodb_manager.get_collection_schema(database, collection, sample_size)
            return f"MongoDB collection '{collection}' schema: {json.dumps(schema, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get MongoDB collection schema: {str(e)}"
    
    @mcp.tool()
    async def mongodb_find_documents(database: str, collection: str, filter_query: str = "{}", limit: int = 10) -> str:
        """Find documents in a MongoDB collection"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            # Parse filter query from JSON string
            import json
            filter_dict = json.loads(filter_query) if filter_query != "{}" else {}
            documents = await mongodb_manager.find_documents(database, collection, filter_dict, limit)
            return f"MongoDB documents from '{collection}': {json.dumps(documents, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to find MongoDB documents: {str(e)}"
    
    @mcp.tool()
    async def mongodb_aggregate(database: str, collection: str, pipeline: str) -> str:
        """Execute MongoDB aggregation pipeline"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            # Parse pipeline from JSON string
            import json
            pipeline_list = json.loads(pipeline)
            results = await mongodb_manager.execute_aggregation(database, collection, pipeline_list)
            return f"MongoDB aggregation results: {json.dumps(results, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to execute MongoDB aggregation: {str(e)}"
    
    # =============================================================================
    # INFLUXDB TOOLS
    # =============================================================================
    
    @mcp.tool()
    async def influxdb_server_info() -> str:
        """Get InfluxDB server information"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            info = await influxdb_manager.get_server_info()
            return f"InfluxDB server info: {json.dumps(info, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get InfluxDB server info: {str(e)}"
    
    @mcp.tool()
    async def influxdb_list_buckets() -> str:
        """List all InfluxDB buckets"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            buckets = await influxdb_manager.get_buckets()
            return f"InfluxDB buckets: {json.dumps(buckets, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to list InfluxDB buckets: {str(e)}"
    
    @mcp.tool()
    async def influxdb_list_measurements(bucket: str, start_time: str = "-1h") -> str:
        """List measurements in an InfluxDB bucket"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            measurements = await influxdb_manager.get_measurements(bucket, start_time)
            return f"InfluxDB measurements in bucket '{bucket}': {measurements}"
        except Exception as e:
            return f"Failed to list InfluxDB measurements: {str(e)}"
    
    @mcp.tool()
    async def influxdb_get_fields(bucket: str, measurement: str, start_time: str = "-1h") -> str:
        """Get fields for an InfluxDB measurement"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            fields = await influxdb_manager.get_fields(bucket, measurement, start_time)
            return f"InfluxDB fields in '{measurement}': {json.dumps(fields, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get InfluxDB fields: {str(e)}"
    
    @mcp.tool()
    async def influxdb_get_tags(bucket: str, measurement: str, start_time: str = "-1h") -> str:
        """Get tag keys for an InfluxDB measurement"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            tags = await influxdb_manager.get_tags(bucket, measurement, start_time)
            return f"InfluxDB tags in '{measurement}': {json.dumps(tags, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get InfluxDB tags: {str(e)}"
    
    @mcp.tool()
    async def influxdb_get_tag_values(bucket: str, measurement: str, tag_key: str, start_time: str = "-1h") -> str:
        """Get values for an InfluxDB tag key"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            values = await influxdb_manager.get_tag_values(bucket, measurement, tag_key, start_time)
            return f"InfluxDB tag '{tag_key}' values: {values}"
        except Exception as e:
            return f"Failed to get InfluxDB tag values: {str(e)}"
    
    @mcp.tool()
    async def influxdb_query(bucket: str, flux_query: str) -> str:
        """Execute a Flux query on InfluxDB"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            results = await influxdb_manager.query_data(bucket, flux_query)
            return f"InfluxDB query results: {json.dumps(results, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to execute InfluxDB query: {str(e)}"
    
    @mcp.tool()
    async def influxdb_sample_data(bucket: str, measurement: str, limit: int = 10, start_time: str = "-1h") -> str:
        """Get sample data from an InfluxDB measurement"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager
        try:
            data = await influxdb_manager.get_sample_data(bucket, measurement, limit, start_time)
            return f"InfluxDB sample data from '{measurement}': {json.dumps(data, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to get InfluxDB sample data: {str(e)}"
