"""
MongoDB resources for the MCP server
"""
from mcp.server.fastmcp import FastMCP
import json


def register_mongodb_resources(mcp: FastMCP):
    """Register MongoDB-related resources with the MCP server"""
    
    @mcp.resource("mongodb://info")
    async def mongodb_server_info() -> str:
        """Get MongoDB server information"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            info = await mongodb_manager.get_server_info()
            return json.dumps({"server_info": info}, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": f"Failed to get MongoDB server info: {str(e)}"}, indent=2)
    
    @mcp.resource("mongodb://databases")
    async def mongodb_databases() -> str:
        """List all MongoDB databases"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            databases = await mongodb_manager.get_databases()
            return json.dumps({"databases": databases}, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Failed to list MongoDB databases: {str(e)}"}, indent=2)
    
    @mcp.resource("mongodb://databases/{database}/info")
    async def mongodb_database_info(database: str) -> str:
        """Get information about a MongoDB database"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            info = await mongodb_manager.get_database_info(database)
            return json.dumps({
                "database": database,
                "info": info
            }, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": f"Failed to get MongoDB database info: {str(e)}"}, indent=2)
    
    @mcp.resource("mongodb://databases/{database}/collections")
    async def mongodb_collections(database: str) -> str:
        """List collections in a MongoDB database"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            collections = await mongodb_manager.get_collections(database)
            return json.dumps({
                "database": database,
                "collections": collections
            }, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Failed to list MongoDB collections: {str(e)}"}, indent=2)
    
    @mcp.resource("mongodb://databases/{database}/collections/{collection}/info")
    async def mongodb_collection_info(database: str, collection: str) -> str:
        """Get information about a MongoDB collection"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            info = await mongodb_manager.get_collection_info(database, collection)
            return json.dumps({
                "database": database,
                "collection": collection,
                "info": info
            }, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": f"Failed to get MongoDB collection info: {str(e)}"}, indent=2)
    
    @mcp.resource("mongodb://databases/{database}/collections/{collection}/schema")
    async def mongodb_collection_schema(database: str, collection: str) -> str:
        """Analyze MongoDB collection schema (sample size: 100)"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            schema = await mongodb_manager.get_collection_schema(database, collection, 100)
            return json.dumps({
                "database": database,
                "collection": collection,
                "schema": schema,
                "sample_size": 100
            }, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": f"Failed to get MongoDB collection schema: {str(e)}"}, indent=2)

    @mcp.resource("mongodb://databases/{database}/collections/{collection}/sample")
    async def mongodb_collection_sample(database: str, collection: str) -> str:
        """Get sample documents from a MongoDB collection (limit: 10)"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        try:
            documents = await mongodb_manager.find_documents(database, collection, {}, 10)
            return json.dumps({
                "database": database,
                "collection": collection,
                "sample_documents": documents,
                "limit": 10
            }, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": f"Failed to get MongoDB sample documents: {str(e)}"}, indent=2)
