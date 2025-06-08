import asyncpg
from typing import Optional, Any, List, Dict
import logging

logger = logging.getLogger(__name__)

class Database:
    """PostgreSQL database connection manager using asyncpg"""
    
    def __init__(self, host: str = "localhost", port: int = 5432, 
                 database: str = "postgres", user: str = "postgres", 
                 password: Optional[str] = None):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.pool: Optional[asyncpg.Pool] = None
    
    @classmethod
    async def connect(cls, host: str = "localhost", port: int = 5432,
                     database: str = "postgres", user: str = "postgres",
                     password: Optional[str] = None) -> "Database":
        """Create a new database instance and establish connection pool"""
        db = cls(host, port, database, user, password)
        await db._create_pool()
        return db
    
    async def _create_pool(self) -> None:
        """Create connection pool"""
        try:
            logger.info(f"Attempting to connect to PostgreSQL at {self.host}:{self.port}")
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=1,
                max_size=10,
                command_timeout=60,
                server_settings={
                    'application_name': 'mcp-server',
                }
            )
            logger.info(f"Connected to PostgreSQL database '{self.database}' at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to database '{self.database}' at {self.host}:{self.port}: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info(f"Database connection pool closed for '{self.database}'")


class DatabaseManager:
    """Manages multiple database connections"""
    
    def __init__(self):
        self.databases: Dict[str, Database] = {}
    
    async def add_database(self, name: str, host: str = "localhost", 
                          port: int = 5432, database: str = "postgres",
                          user: str = "postgres", password: Optional[str] = None) -> None:
        """Add a new database connection"""
        db = await Database.connect(host, port, database, user, password)
        self.databases[name] = db
        logger.info(f"Added database connection '{name}' for database '{database}'")
    
    def get_database(self, name: str) -> Database:
        """Get a database connection by name"""
        if name not in self.databases:
            raise ValueError(f"Database '{name}' not found. Available: {list(self.databases.keys())}")
        return self.databases[name]
    
    def list_databases(self) -> List[str]:
        """List all available database connection names"""
        return list(self.databases.keys())
    
    async def disconnect_all(self) -> None:
        """Disconnect all database connections"""
        for name, db in self.databases.items():
            await db.disconnect()
            logger.info(f"Disconnected database '{name}'")
        self.databases.clear()
    
    async def query(self, database_name: str, sql: str, *args) -> List[Dict[str, Any]]:
        """Execute a SELECT query on a specific database"""
        db = self.get_database(database_name)
        if not db.pool:
            raise RuntimeError(f"Database '{database_name}' not connected")
        
        async with db.pool.acquire() as connection:
            try:
                rows = await connection.fetch(sql, *args)
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Query failed on '{database_name}': {e}")
                raise
    
    async def execute(self, database_name: str, sql: str, *args) -> str:
        """Execute INSERT, UPDATE, DELETE queries on a specific database"""
        db = self.get_database(database_name)
        if not db.pool:
            raise RuntimeError(f"Database '{database_name}' not connected")
        
        async with db.pool.acquire() as connection:
            try:
                result = await connection.execute(sql, *args)
                logger.info(f"Query executed on '{database_name}': {result}")
                return result
            except Exception as e:
                logger.error(f"Execute failed on '{database_name}': {e}")
                raise
    
    async def fetchone(self, database_name: str, sql: str, *args) -> Optional[Dict[str, Any]]:
        """Execute a query and return a single row from a specific database"""
        db = self.get_database(database_name)
        if not db.pool:
            raise RuntimeError(f"Database '{database_name}' not connected")
        
        async with db.pool.acquire() as connection:
            try:
                row = await connection.fetchrow(sql, *args)
                return dict(row) if row else None
            except Exception as e:
                logger.error(f"Fetchone failed on '{database_name}': {e}")
                raise
    
    async def get_table_info(self, database_name: str, table_name: str) -> List[Dict[str, Any]]:
        """Get information about a table's columns in a specific database"""
        sql = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = $1
        ORDER BY ordinal_position;
        """
        return await self.query(database_name, sql, table_name)
    
    async def list_tables(self, database_name: str) -> List[str]:
        """List all tables in a specific database"""
        sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        rows = await self.query(database_name, sql)
        return [row['table_name'] for row in rows]
    
    async def list_all_databases_from_server(self) -> List[str]:
        """List all databases available on the PostgreSQL server"""
        # Use any connected database to query the server
        if not self.databases:
            raise RuntimeError("No databases connected")
        
        db = next(iter(self.databases.values()))
        sql = """
        SELECT datname 
        FROM pg_database 
        WHERE datistemplate = false
        ORDER BY datname;
        """
        
        async with db.pool.acquire() as connection:
            try:
                rows = await connection.fetch(sql)
                return [row['datname'] for row in rows]
            except Exception as e:
                logger.error(f"Failed to list databases from server: {e}")
                raise
