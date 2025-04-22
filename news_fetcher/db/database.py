"""
Database Module

This module provides database connection and operations.
"""
import logging
import sqlite3
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from pathlib import Path

from news_fetcher.config.settings import config
from news_fetcher.models.base import BaseModel

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for models
T = TypeVar('T', bound=BaseModel)


class Database:
    """Database connection and operations."""

    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize the database connection.

        Args:
            db_url: The database URL. If None, uses the URL from config.
        """
        self.db_url = db_url or config.DATABASE_URL or "sqlite:///news_fetcher.db"
        self.conn = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        """
        Initialize the database connection and create tables if they don't exist.
        """
        try:
            # Extract the database path from the URL
            if self.db_url.startswith("sqlite:///"):
                db_path = self.db_url[10:]
                # Ensure the directory exists
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)
                self.conn = sqlite3.connect(db_path)
                self.conn.row_factory = sqlite3.Row
                logger.info(f"Connected to SQLite database at {db_path}")
            else:
                # For future support of other databases
                raise ValueError(f"Unsupported database URL: {self.db_url}")

            # Create tables
            self._create_tables()
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def _create_tables(self) -> None:
        """
        Create database tables if they don't exist.
        """
        cursor = self.conn.cursor()

        # Create articles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT,
            source_name TEXT,
            author TEXT,
            title TEXT NOT NULL,
            description TEXT,
            url TEXT,
            url_to_image TEXT,
            published_at TEXT,
            content TEXT,
            fetched_at TEXT NOT NULL,
            themes TEXT
        )
        ''')

        # Create summaries table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            model_used TEXT,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
        ''')

        self.conn.commit()
        logger.info("Database tables created successfully")

    def close(self) -> None:
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def insert(self, model: BaseModel) -> int:
        """
        Insert a model instance into the database.

        Args:
            model: The model instance to insert.

        Returns:
            The ID of the inserted record.
        """
        if not self.conn:
            raise ConnectionError("Database connection not established")

        cursor = self.conn.cursor()
        data = model.to_dict()
        
        # Remove id for insertion if it's None
        if "id" in data and data["id"] is None:
            del data["id"]
            
        # Prepare the SQL statement
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        sql = f"INSERT INTO {model.table_name} ({columns}) VALUES ({placeholders})"
        
        try:
            cursor.execute(sql, list(data.values()))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting into {model.table_name}: {str(e)}")
            raise

    def update(self, model: BaseModel) -> bool:
        """
        Update a model instance in the database.

        Args:
            model: The model instance to update.

        Returns:
            True if the update was successful, False otherwise.
        """
        if not self.conn:
            raise ConnectionError("Database connection not established")
            
        if not model.id:
            raise ValueError("Cannot update model without ID")

        cursor = self.conn.cursor()
        data = model.to_dict()
        
        # Remove id from data for update
        del data["id"]
        
        # Prepare the SQL statement
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        sql = f"UPDATE {model.table_name} SET {set_clause} WHERE id = ?"
        
        try:
            cursor.execute(sql, list(data.values()) + [model.id])
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error updating {model.table_name}: {str(e)}")
            raise

    def delete(self, model: BaseModel) -> bool:
        """
        Delete a model instance from the database.

        Args:
            model: The model instance to delete.

        Returns:
            True if the deletion was successful, False otherwise.
        """
        if not self.conn:
            raise ConnectionError("Database connection not established")
            
        if not model.id:
            raise ValueError("Cannot delete model without ID")

        cursor = self.conn.cursor()
        sql = f"DELETE FROM {model.table_name} WHERE id = ?"
        
        try:
            cursor.execute(sql, (model.id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error deleting from {model.table_name}: {str(e)}")
            raise

    def get_by_id(self, model_class: Type[T], id: int) -> Optional[T]:
        """
        Get a model instance by ID.

        Args:
            model_class: The model class to instantiate.
            id: The ID of the record to retrieve.

        Returns:
            A model instance if found, None otherwise.
        """
        if not self.conn:
            raise ConnectionError("Database connection not established")

        cursor = self.conn.cursor()
        sql = f"SELECT * FROM {model_class.table_name} WHERE id = ?"
        
        try:
            cursor.execute(sql, (id,))
            row = cursor.fetchone()
            if row:
                return model_class.from_dict(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error getting {model_class.table_name} by ID: {str(e)}")
            raise

    def get_all(self, model_class: Type[T], limit: int = 100, offset: int = 0) -> List[T]:
        """
        Get all model instances with pagination.

        Args:
            model_class: The model class to instantiate.
            limit: The maximum number of records to retrieve.
            offset: The number of records to skip.

        Returns:
            A list of model instances.
        """
        if not self.conn:
            raise ConnectionError("Database connection not established")

        cursor = self.conn.cursor()
        sql = f"SELECT * FROM {model_class.table_name} LIMIT ? OFFSET ?"
        
        try:
            cursor.execute(sql, (limit, offset))
            rows = cursor.fetchall()
            return [model_class.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all {model_class.table_name}: {str(e)}")
            raise

    def query(self, model_class: Type[T], sql: str, params: tuple = ()) -> List[T]:
        """
        Execute a custom SQL query and return model instances.

        Args:
            model_class: The model class to instantiate.
            sql: The SQL query to execute.
            params: The parameters for the SQL query.

        Returns:
            A list of model instances.
        """
        if not self.conn:
            raise ConnectionError("Database connection not established")

        cursor = self.conn.cursor()
        
        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [model_class.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error executing query on {model_class.table_name}: {str(e)}")
            raise

    def execute(self, sql: str, params: tuple = ()) -> Any:
        """
        Execute a custom SQL statement.

        Args:
            sql: The SQL statement to execute.
            params: The parameters for the SQL statement.

        Returns:
            The cursor object.
        """
        if not self.conn:
            raise ConnectionError("Database connection not established")

        cursor = self.conn.cursor()
        
        try:
            cursor.execute(sql, params)
            self.conn.commit()
            return cursor
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error executing SQL: {str(e)}")
            raise


# Create a singleton instance for easy import
db = Database()
