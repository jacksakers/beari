"""
Database initialization for Beari2.
Creates tables and sets up initial schema.
"""

import os
import sys

# Add parent directory to path for standalone execution
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .connection import DatabaseConnection
    from .schema import SCHEMA_STATEMENTS
except ImportError:
    from connection import DatabaseConnection
    from schema import SCHEMA_STATEMENTS


def initialize_database(db_path: str = "beari2.db") -> None:
    """
    Initialize the database with schema.
    
    Args:
        db_path: Path to database file
    """
    with DatabaseConnection(db_path) as db:
        print(f"Initializing database at {db_path}...")
        
        for statement in SCHEMA_STATEMENTS:
            db.cursor.execute(statement)
        
        db.commit()
        print("[OK] Database initialized successfully")


def reset_database(db_path: str = "beari2.db") -> None:
    """
    Delete and recreate the database (WARNING: destroys all data).
    
    Args:
        db_path: Path to database file
    """
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted existing database: {db_path}")
    
    initialize_database(db_path)


if __name__ == "__main__":
    initialize_database()
