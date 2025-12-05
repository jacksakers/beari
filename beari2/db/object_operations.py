"""
CRUD operations for ConceptObjects.
One function per operation for clean organization.
"""

from typing import Optional, Dict, List

try:
    from .connection import DatabaseConnection
except ImportError:
    from connection import DatabaseConnection


def create_object(db: DatabaseConnection, name: str, obj_type: str) -> Optional[int]:
    """
    Create a new ConceptObject in the database.
    
    Args:
        db: Database connection
        name: Name of the concept (word)
        obj_type: Type of object (Noun, Verb, Adjective)
    
    Returns:
        ID of created object, or existing ID if already exists
    """
    name = name.lower()
    
    try:
        db.cursor.execute(
            "INSERT INTO ConceptObjects (name, type) VALUES (?, ?)",
            (name, obj_type)
        )
        db.commit()
        return db.cursor.lastrowid
    except Exception:
        # Object already exists, return its ID
        db.cursor.execute(
            "SELECT id FROM ConceptObjects WHERE name = ?",
            (name,)
        )
        row = db.cursor.fetchone()
        return row['id'] if row else None


def get_object(db: DatabaseConnection, name: str) -> Optional[Dict]:
    """
    Retrieve a ConceptObject by name.
    
    Args:
        db: Database connection
        name: Name of the concept
    
    Returns:
        Dictionary with object data, or None if not found
    """
    name = name.lower()
    
    db.cursor.execute(
        "SELECT * FROM ConceptObjects WHERE name = ?",
        (name,)
    )
    
    row = db.cursor.fetchone()
    return dict(row) if row else None


def get_object_by_id(db: DatabaseConnection, object_id: int) -> Optional[Dict]:
    """
    Retrieve a ConceptObject by ID.
    
    Args:
        db: Database connection
        object_id: ID of the object
    
    Returns:
        Dictionary with object data, or None if not found
    """
    db.cursor.execute(
        "SELECT * FROM ConceptObjects WHERE id = ?",
        (object_id,)
    )
    
    row = db.cursor.fetchone()
    return dict(row) if row else None


def update_object(db: DatabaseConnection, name: str, obj_type: str) -> bool:
    """
    Update a ConceptObject's type.
    
    Args:
        db: Database connection
        name: Name of the concept
        obj_type: New type
    
    Returns:
        True if updated, False if not found
    """
    name = name.lower()
    
    db.cursor.execute(
        "UPDATE ConceptObjects SET type = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
        (obj_type, name)
    )
    db.commit()
    
    return db.cursor.rowcount > 0


def delete_object(db: DatabaseConnection, name: str) -> bool:
    """
    Delete a ConceptObject and all its properties.
    
    Args:
        db: Database connection
        name: Name of the concept to delete
    
    Returns:
        True if deleted, False if not found
    """
    name = name.lower()
    
    db.cursor.execute(
        "DELETE FROM ConceptObjects WHERE name = ?",
        (name,)
    )
    db.commit()
    
    return db.cursor.rowcount > 0


def object_exists(db: DatabaseConnection, name: str) -> bool:
    """
    Check if a ConceptObject exists.
    
    Args:
        db: Database connection
        name: Name of the concept
    
    Returns:
        True if exists, False otherwise
    """
    name = name.lower()
    
    db.cursor.execute(
        "SELECT 1 FROM ConceptObjects WHERE name = ?",
        (name,)
    )
    
    return db.cursor.fetchone() is not None


def get_all_objects(db: DatabaseConnection, obj_type: Optional[str] = None) -> List[Dict]:
    """
    Get all ConceptObjects, optionally filtered by type.
    
    Args:
        db: Database connection
        obj_type: Optional filter by type
    
    Returns:
        List of object dictionaries
    """
    if obj_type:
        db.cursor.execute(
            "SELECT * FROM ConceptObjects WHERE type = ? ORDER BY name",
            (obj_type,)
        )
    else:
        db.cursor.execute(
            "SELECT * FROM ConceptObjects ORDER BY name"
        )
    
    return [dict(row) for row in db.cursor.fetchall()]


def get_object_count(db: DatabaseConnection) -> int:
    """
    Get total count of ConceptObjects.
    
    Args:
        db: Database connection
    
    Returns:
        Total count of objects
    """
    db.cursor.execute("SELECT COUNT(*) as count FROM ConceptObjects")
    return db.cursor.fetchone()['count']
