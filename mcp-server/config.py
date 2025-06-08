"""
Configuration management for the MCP server
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class PostgresConfig:
    """PostgreSQL configuration"""
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: Optional[str] = None
    database: Optional[str] = None

    @classmethod
    def from_env(cls) -> "PostgresConfig":
        """Load PostgreSQL configuration from environment variables"""
        config = cls(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB")
        )
        logger.info(f"PostgreSQL config loaded: host={config.host}, port={config.port}, user={config.user}, database={config.database}")
        return config


@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0

    @classmethod
    def from_env(cls) -> "RedisConfig":
        """Load Redis configuration from environment variables"""
        return cls(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            db=int(os.getenv("REDIS_DB", "0"))
        )


@dataclass
class MongoDBConfig:
    """MongoDB configuration"""
    host: str = "localhost"
    port: int = 27017
    user: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None

    @classmethod
    def from_env(cls) -> "MongoDBConfig":
        """Load MongoDB configuration from environment variables"""
        return cls(
            host=os.getenv("MONGODB_HOST", "localhost"),
            port=int(os.getenv("MONGODB_PORT", "27017")),
            user=os.getenv("MONGODB_USER"),
            password=os.getenv("MONGODB_PASSWORD"),
            database=os.getenv("MONGODB_DB")
        )


@dataclass
class InfluxDBConfig:
    """InfluxDB configuration"""
    host: str = "localhost"
    port: int = 8086
    token: Optional[str] = None
    org: Optional[str] = None
    bucket: Optional[str] = None

    @classmethod
    def from_env(cls) -> "InfluxDBConfig":
        """Load InfluxDB configuration from environment variables"""
        return cls(
            host=os.getenv("INFLUXDB_HOST", "localhost"),
            port=int(os.getenv("INFLUXDB_PORT", "8086")),
            token=os.getenv("INFLUXDB_TOKEN"),
            org=os.getenv("INFLUXDB_ORG"),
            bucket=os.getenv("INFLUXDB_BUCKET")
        )


@dataclass
class AppConfig:
    """Application configuration"""
    postgres: PostgresConfig
    redis: RedisConfig
    mongodb: MongoDBConfig
    influxdb: InfluxDBConfig

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load all configuration from environment variables"""
        return cls(
            postgres=PostgresConfig.from_env(),
            redis=RedisConfig.from_env(),
            mongodb=MongoDBConfig.from_env(),
            influxdb=InfluxDBConfig.from_env()
        )
