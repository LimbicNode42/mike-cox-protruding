import logging
import threading
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2 import extras

logger = logging.getLogger(__name__)


class Database:
    """PostgreSQL database connection manager using psycopg2"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        user: str = "postgres",
        password: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self._lock = threading.Lock()

    @classmethod
    def connect(
        cls,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        user: str = "postgres",
        password: Optional[str] = None,
    ) -> "Database":
        """Create a new database instance and establish connection pool"""
        db = cls(host, port, database, user, password)
        db._create_pool()
        return db

    def _create_pool(self) -> None:
        """Create connection pool"""
        try:
            logger.info(
                f"Attempting to connect to PostgreSQL at {self.host}:{self.port}"
            )

            # Build connection string
            connection_string = f"host={self.host} port={self.port} dbname={self.database} user={self.user}"
            if self.password:
                connection_string += f" password={self.password}"

            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=connection_string,
                application_name="mcp-server",
            )
            logger.info(
                f"Connected to PostgreSQL database '{self.database}' at {self.host}:{self.port}"
            )
        except Exception as e:
            logger.error(
                f"Failed to connect to database '{self.database}' at {self.host}:{self.port}: {e}"
            )
            raise

    def disconnect(self) -> None:
        """Close the connection pool"""
        if self.pool:
            self.pool.closeall()
            logger.info(f"Database connection pool closed for '{self.database}'")


class DatabaseManager:
    """Manages multiple database connections"""

    def __init__(self):
        self.databases: Dict[str, Database] = {}

    def add_database(
        self,
        name: str,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        user: str = "postgres",
        password: Optional[str] = None,
    ) -> None:
        """Add a new database connection"""
        db = Database.connect(host, port, database, user, password)
        self.databases[name] = db
        logger.info(f"Added database connection '{name}' for database '{database}'")

    def get_database(self, name: str) -> Database:
        """Get a database connection by name"""
        if name not in self.databases:
            raise ValueError(
                f"Database '{name}' not found. Available: {list(self.databases.keys())}"
            )
        return self.databases[name]

    def list_databases(self) -> List[str]:
        """List all available database connection names"""
        return list(self.databases.keys())

    def disconnect_all(self) -> None:
        """Disconnect all database connections"""
        for name, db in self.databases.items():
            db.disconnect()
            logger.info(f"Disconnected database '{name}'")
        self.databases.clear()

    def query(self, database_name: str, sql: str, *args) -> List[Dict[str, Any]]:
        """Execute a SELECT query on a specific database"""
        db = self.get_database(database_name)
        if not db.pool:
            raise RuntimeError(f"Database '{database_name}' not connected")

        connection = None
        try:
            connection = db.pool.getconn()
            cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(sql, args if args else None)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Query failed on '{database_name}': {e}")
            raise
        finally:
            if connection:
                db.pool.putconn(connection)

    def execute(self, database_name: str, sql: str, *args) -> str:
        """Execute INSERT, UPDATE, DELETE queries on a specific database"""
        db = self.get_database(database_name)
        if not db.pool:
            raise RuntimeError(f"Database '{database_name}' not connected")

        connection = None
        try:
            connection = db.pool.getconn()
            cursor = connection.cursor()
            cursor.execute(sql, args if args else None)
            connection.commit()
            result = f"Affected rows: {cursor.rowcount}"
            logger.info(f"Query executed on '{database_name}': {result}")
            return result
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Execute failed on '{database_name}': {e}")
            raise
        finally:
            if connection:
                db.pool.putconn(connection)

    def fetchone(self, database_name: str, sql: str, *args) -> Optional[Dict[str, Any]]:
        """Execute a query and return a single row from a specific database"""
        db = self.get_database(database_name)
        if not db.pool:
            raise RuntimeError(f"Database '{database_name}' not connected")

        connection = None
        try:
            connection = db.pool.getconn()
            cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(sql, args if args else None)
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Fetchone failed on '{database_name}': {e}")
            raise
        finally:
            if connection:
                db.pool.putconn(connection)

    def get_table_info(
        self, database_name: str, table_name: str
    ) -> List[Dict[str, Any]]:
        """Get information about a table's columns in a specific database"""
        sql = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
        """
        return self.query(database_name, sql, table_name)

    def list_tables(self, database_name: str) -> List[str]:
        """List all tables in a specific database"""
        sql = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        rows = self.query(database_name, sql)
        return [row["table_name"] for row in rows]

    def list_all_databases_from_server(self) -> List[str]:
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

        connection = None
        try:
            connection = db.pool.getconn()
            cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [row["datname"] for row in rows]
        except Exception as e:
            logger.error(f"Failed to list databases from server: {e}")
            raise
        finally:
            if connection:
                db.pool.putconn(connection)
