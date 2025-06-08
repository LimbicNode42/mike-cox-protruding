"""
MongoDB tools for the MCP server
"""
from mcp.server.fastmcp import FastMCP
import json


def register_mongodb_tools(mcp: FastMCP):
    """Register MongoDB-related tools with the MCP server"""
    
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
