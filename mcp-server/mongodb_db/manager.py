"""
MongoDB database manager and operations
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MongoDBManager:
    """MongoDB connection and operations manager"""
    
    def __init__(self, host: str = "localhost", port: int = 27017,
                 user: Optional[str] = None, password: Optional[str] = None,
                 database: Optional[str] = None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.client: Optional[AsyncIOMotorClient] = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            # Build connection string - don't append database name to URI
            connection_string = f"mongodb://"
            if self.user and self.password:
                connection_string += f"{self.user}:{self.password}@"
            connection_string += f"{self.host}:{self.port}/"
            
            logger.info(f"Connecting to MongoDB with connection string: {connection_string.replace(self.password or '', '***')}")
            
            self.client = AsyncIOMotorClient(connection_string)
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
    
    async def get_databases(self) -> List[str]:
        """Get list of databases"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")
        db_info = await self.client.list_database_names()
        return db_info
    
    async def get_database_info(self, database: str) -> Dict[str, Any]:
        """Get information about a database"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")
        
        db = self.client[database]
        stats = await db.command("dbStats")
        return {
            "name": database,
            "collections": stats.get("collections", 0),
            "objects": stats.get("objects", 0),
            "dataSize": stats.get("dataSize", 0),
            "storageSize": stats.get("storageSize", 0),
            "indexes": stats.get("indexes", 0),
            "indexSize": stats.get("indexSize", 0)
        }
    
    async def get_collections(self, database: str) -> List[str]:
        """Get list of collections in a database"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")
        
        db = self.client[database]
        collections = await db.list_collection_names()
        return collections
    
    async def get_collection_info(self, database: str, collection: str) -> Dict[str, Any]:
        """Get information about a collection"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")
        
        db = self.client[database]
        coll = db[collection]
        
        # Get collection stats
        stats = await db.command("collStats", collection)
        
        # Get indexes
        indexes = []
        async for index in coll.list_indexes():
            indexes.append(index)
        
        return {
            "name": collection,
            "count": stats.get("count", 0),
            "size": stats.get("size", 0),
            "storageSize": stats.get("storageSize", 0),
            "indexes": indexes,
            "avgObjSize": stats.get("avgObjSize", 0)
        }
    
    async def get_collection_schema(self, database: str, collection: str, sample_size: int = 100) -> Dict[str, Any]:
        """Analyze collection schema by sampling documents"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")
        
        db = self.client[database]
        coll = db[collection]
        
        # Sample documents to infer schema
        pipeline = [{"$sample": {"size": sample_size}}, {"$limit": sample_size}]
        
        field_types = {}
        sample_count = 0
        
        async for doc in coll.aggregate(pipeline):
            sample_count += 1
            for field, value in doc.items():
                field_type = type(value).__name__
                if field not in field_types:
                    field_types[field] = {}
                if field_type not in field_types[field]:
                    field_types[field][field_type] = 0
                field_types[field][field_type] += 1
        
        # Convert to schema format
        schema = {}
        for field, types in field_types.items():
            most_common_type = max(types.items(), key=lambda x: x[1])
            schema[field] = {
                "primary_type": most_common_type[0],
                "type_distribution": types,
                "frequency": sum(types.values()) / sample_count if sample_count > 0 else 0
            }
        
        return {
            "schema": schema,
            "sample_size": sample_count,
            "total_documents": await coll.count_documents({})
        }
    
    async def find_documents(self, database: str, collection: str, 
                           filter_query: Dict = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Find documents in a collection"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")
        
        db = self.client[database]
        coll = db[collection]
        
        if filter_query is None:
            filter_query = {}
        
        cursor = coll.find(filter_query).limit(limit)
        documents = []
        async for doc in cursor:
            # Convert ObjectId to string for JSON serialization
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            documents.append(doc)
        
        return documents
    
    async def execute_aggregation(self, database: str, collection: str, 
                                 pipeline: List[Dict]) -> List[Dict[str, Any]]:
        """Execute an aggregation pipeline"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")
        
        db = self.client[database]
        coll = db[collection]
        
        results = []
        async for doc in coll.aggregate(pipeline):
            # Convert ObjectId to string for JSON serialization
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            results.append(doc)
        
        return results
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get MongoDB server information"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")
        
        server_info = await self.client.admin.command("buildInfo")
        return {
            "version": server_info.get("version"),
            "gitVersion": server_info.get("gitVersion"),
            "platform": server_info.get("platform"),
            "maxBsonObjectSize": server_info.get("maxBsonObjectSize")
        }
