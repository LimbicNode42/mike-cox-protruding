"""
MongoDB tools for the MCP server
"""
from mcp.server.fastmcp import FastMCP
import json


def register_mongodb_tools(mcp: FastMCP):
    """Register MongoDB-related tools with the MCP server"""
    
    @mcp.tool()
    async def mongodb_find_documents(database: str, collection: str, filter_query: str = "{}", limit: int = 10) -> str:
        """Find documents in a MongoDB collection"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        if not mongodb_manager:
            return "MongoDB is disabled in the server configuration"
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
        if not mongodb_manager:
            return "MongoDB is disabled in the server configuration"
        try:
            # Parse pipeline from JSON string
            import json
            pipeline_list = json.loads(pipeline)
            results = await mongodb_manager.execute_aggregation(database, collection, pipeline_list)
            return f"MongoDB aggregation results: {json.dumps(results, indent=2, default=str)}"
        except Exception as e:
            return f"Failed to execute MongoDB aggregation: {str(e)}"

    @mcp.tool()
    async def mongodb_insert_document(database: str, collection: str, document: str) -> str:
        """Insert a document into a MongoDB collection"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        if not mongodb_manager:
            return "MongoDB is disabled in the server configuration"
        try:
            # Parse document from JSON string
            import json
            doc_dict = json.loads(document)
            
            # Access the MongoDB client through the manager
            client = mongodb_manager.client
            db = client[database]
            coll = db[collection]
            result = await coll.insert_one(doc_dict)
            
            return f"Document inserted successfully into '{collection}': {str(result.inserted_id)}"
        except Exception as e:
            return f"Failed to insert MongoDB document: {str(e)}"

    @mcp.tool()
    async def mongodb_update_documents(database: str, collection: str, filter_query: str, update_query: str) -> str:
        """Update documents in a MongoDB collection"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        if not mongodb_manager:
            return "MongoDB is disabled in the server configuration"
        try:
            # Parse queries from JSON strings
            import json
            filter_dict = json.loads(filter_query)
            update_dict = json.loads(update_query)
            
            # Access the MongoDB client through the manager
            client = mongodb_manager.client
            db = client[database]
            coll = db[collection]
            result = await coll.update_many(filter_dict, update_dict)
            
            return f"Documents updated in '{collection}': {result.modified_count} document(s) modified"
        except Exception as e:
            return f"Failed to update MongoDB documents: {str(e)}"

    @mcp.tool()
    async def mongodb_delete_documents(database: str, collection: str, filter_query: str) -> str:
        """Delete documents from a MongoDB collection"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        if not mongodb_manager:
            return "MongoDB is disabled in the server configuration"
        try:
            # Parse filter query from JSON string
            import json
            filter_dict = json.loads(filter_query)
            
            # Access the MongoDB client through the manager
            client = mongodb_manager.client
            db = client[database]
            coll = db[collection]
            result = await coll.delete_many(filter_dict)
            
            return f"Documents deleted from '{collection}': {result.deleted_count} document(s) removed"
        except Exception as e:
            return f"Failed to delete MongoDB documents: {str(e)}"

    @mcp.tool()
    async def mongodb_create_collection(database: str, collection: str) -> str:
        """Create a new collection in a MongoDB database"""
        ctx = mcp.get_context()
        mongodb_manager = ctx.request_context.lifespan_context.mongodb_manager
        if not mongodb_manager:
            return "MongoDB is disabled in the server configuration"
        try:
            # Access the MongoDB client through the manager
            client = mongodb_manager.client
            db = client[database]
            await db.create_collection(collection)
            
            return f"Collection '{collection}' created successfully in database '{database}'"
        except Exception as e:
            return f"Failed to create MongoDB collection '{collection}': {str(e)}"
