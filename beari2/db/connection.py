"""
Database connection management for Beari2.
"""

import sqlite3
from typing import Optional


class DatabaseConnection:
    """Manages SQLite database connection with context manager support."""
    
    def __init__(self, db_path: str = "beari2.db"):
        """
        Initialize database connection manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
    
    def connect(self) -> sqlite3.Connection:
        """
        Establish connection to database.
        
        Returns:
            SQLite connection object
        """
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        return self.conn
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def commit(self) -> None:
        """Commit current transaction."""
        if self.conn:
            self.conn.commit()
    
    def rollback(self) -> None:
        """Rollback current transaction."""
        if self.conn:
            self.conn.rollback()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()
