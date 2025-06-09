"""
MongoDB database manager and operations
"""

import logging
from typing import Any, Dict, List, Optional

from pymongo import MongoClient

logger = logging.getLogger(__name__)


class MongoDBManager:
    """MongoDB connection and operations manager"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 27017,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.client: Optional[MongoClient] = None

    def connect(self):
        """Connect to MongoDB"""
        try:
            # Build connection string
            connection_string = "mongodb://"
            if self.user and self.password:
                connection_string += f"{self.user}:{self.password}@"
            connection_string += f"{self.host}:{self.port}/"

            logger.info(
                f"Connecting to MongoDB with connection string: {connection_string.replace(self.password or '', '***')}"
            )

            self.client = MongoClient(connection_string)
            # Test connection
            self.client.admin.command("ping")
            logger.info(f"Connected to MongoDB at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.client = None

    def get_databases(self) -> List[str]:
        """Get list of databases"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")
        db_info = self.client.list_database_names()
        return db_info

    def get_database_info(self, database: str) -> Dict[str, Any]:
        """Get information about a database"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")

        db = self.client[database]
        stats = db.command("dbStats")
        return {
            "name": database,
            "collections": stats.get("collections", 0),
            "objects": stats.get("objects", 0),
            "dataSize": stats.get("dataSize", 0),
            "storageSize": stats.get("storageSize", 0),
            "indexes": stats.get("indexes", 0),
            "indexSize": stats.get("indexSize", 0),
        }

    def get_collections(self, database: str) -> List[str]:
        """Get list of collections in a database"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")

        db = self.client[database]
        collections = db.list_collection_names()
        return collections

    def get_collection_info(self, database: str, collection: str) -> Dict[str, Any]:
        """Get information about a collection"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")

        db = self.client[database]
        coll = db[collection]

        # Get collection stats
        stats = db.command("collStats", collection)

        # Get indexes
        indexes = list(coll.list_indexes())

        return {
            "name": collection,
            "count": stats.get("count", 0),
            "size": stats.get("size", 0),
            "storageSize": stats.get("storageSize", 0),
            "indexes": indexes,
            "avgObjSize": stats.get("avgObjSize", 0),
        }

    def get_collection_schema(
        self, database: str, collection: str, sample_size: int = 100
    ) -> Dict[str, Any]:
        """Analyze collection schema by sampling documents"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")

        db = self.client[database]
        coll = db[collection]

        # Sample documents to infer schema
        pipeline = [{"$sample": {"size": sample_size}}, {"$limit": sample_size}]

        field_types = {}
        sample_count = 0

        for doc in coll.aggregate(pipeline):
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
                "frequency": sum(types.values()) / sample_count
                if sample_count > 0
                else 0,
            }

        return {
            "schema": schema,
            "sample_size": sample_count,
            "total_documents": coll.count_documents({}),
        }

    def find_documents(
        self, database: str, collection: str, filter_query: Dict = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find documents in a collection"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")

        db = self.client[database]
        coll = db[collection]

        if filter_query is None:
            filter_query = {}

        cursor = coll.find(filter_query).limit(limit)
        documents = []
        for doc in cursor:
            # Convert ObjectId to string for JSON serialization
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            documents.append(doc)

        return documents

    def execute_aggregation(
        self, database: str, collection: str, pipeline: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Execute an aggregation pipeline"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")

        db = self.client[database]
        coll = db[collection]

        results = []
        for doc in coll.aggregate(pipeline):
            # Convert ObjectId to string for JSON serialization
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            results.append(doc)

        return results

    def get_server_info(self) -> Dict[str, Any]:
        """Get MongoDB server information"""
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")

        server_info = self.client.admin.command("buildInfo")
        return {
            "version": server_info.get("version"),
            "gitVersion": server_info.get("gitVersion"),
            "platform": server_info.get("platform"),
            "maxBsonObjectSize": server_info.get("maxBsonObjectSize"),
        }
