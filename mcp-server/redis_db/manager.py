"""
Redis database manager and operations
"""

import logging
from typing import Any, Dict, List, Optional

import redis

logger = logging.getLogger(__name__)


class RedisManager:
    """Redis connection and operations manager"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
    ):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.client: Optional[redis.Redis] = None

    def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True,
            )
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            self.client.close()
            self.client = None

    def get_info(self) -> Dict[str, Any]:
        """Get Redis server information"""
        if not self.client:
            raise ConnectionError("Not connected to Redis")
        return self.client.info()

    def get_databases(self) -> List[int]:
        """Get list of available databases"""
        if not self.client:
            raise ConnectionError("Not connected to Redis")
        info = self.client.info("keyspace")
        databases = []
        for key, _value in info.items():
            if key.startswith("db"):
                db_num = int(key[2:])  # Extract number from "db0", "db1", etc.
                databases.append(db_num)
        return (
            sorted(databases) if databases else [0]
        )  # Default to db0 if no keyspace info

    def get_keys(self, pattern: str = "*", db: Optional[int] = None) -> List[str]:
        """Get keys matching pattern from specified database"""
        if not self.client:
            raise ConnectionError("Not connected to Redis")

        if db is not None and db != self.db:
            # Switch to different database temporarily
            temp_client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=db,
                decode_responses=True,
            )
            try:
                keys = temp_client.keys(pattern)
                temp_client.close()
                return keys
            except Exception as e:
                temp_client.close()
                raise e
        else:
            return self.client.keys(pattern)

    def get_key_info(self, key: str, db: Optional[int] = None) -> Dict[str, Any]:
        """Get information about a specific key"""
        if not self.client:
            raise ConnectionError("Not connected to Redis")

        client = self.client
        if db is not None and db != self.db:
            client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=db,
                decode_responses=True,
            )

        try:
            key_type = client.type(key)
            ttl = client.ttl(key)
            size = client.memory_usage(key) if hasattr(client, "memory_usage") else None

            info = {
                "key": key,
                "type": key_type,
                "ttl": ttl if ttl > 0 else "no expiration" if ttl == -1 else "expired",
                "memory_usage": size,
            }

            if db is not None and db != self.db:
                client.close()

            return info
        except Exception as e:
            if db is not None and db != self.db:
                client.close()
            raise e

    def get_value(self, key: str, db: Optional[int] = None) -> Any:
        """Get value of a key with automatic type detection"""
        if not self.client:
            raise ConnectionError("Not connected to Redis")

        client = self.client
        if db is not None and db != self.db:
            client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=db,
                decode_responses=True,
            )

        try:
            key_type = client.type(key)

            if key_type == "string":
                value = client.get(key)
            elif key_type == "list":
                value = client.lrange(key, 0, -1)
            elif key_type == "set":
                value = client.smembers(key)
            elif key_type == "zset":
                value = client.zrange(key, 0, -1, withscores=True)
            elif key_type == "hash":
                value = client.hgetall(key)
            else:
                value = f"Unsupported type: {key_type}"

            if db is not None and db != self.db:
                client.close()

            return value
        except Exception as e:
            if db is not None and db != self.db:
                client.close()
            raise e

    def execute_command(self, command: str, *args) -> Any:
        """Execute a Redis command"""
        if not self.client:
            raise ConnectionError("Not connected to Redis")
        return self.client.execute_command(command, *args)
