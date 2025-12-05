"""
CRUD operations for DynamicProperties.
One function per operation for clean organization.
"""

from typing import Optional, Dict, List, Tuple

try:
    from .connection import DatabaseConnection
except ImportError:
    from connection import DatabaseConnection


def add_property(db: DatabaseConnection, parent_id: int, relation: str, 
                target_value: str, value_type: str = 'string') -> Optional[int]:
    """
    Add a property to a ConceptObject.
    
    Args:
        db: Database connection
        parent_id: ID of the parent ConceptObject
        relation: Property key (e.g., 'is', 'can_have')
        target_value: Property value
        value_type: Type of value (string, int, float, object)
    
    Returns:
        ID of created property, or existing ID if already exists
    """
    try:
        db.cursor.execute(
            """
            INSERT INTO DynamicProperties (parent_id, relation, target_value, value_type)
            VALUES (?, ?, ?, ?)
            """,
            (parent_id, relation, target_value, value_type)
        )
        db.commit()
        return db.cursor.lastrowid
    except Exception:
        # Property already exists, increment weight
        db.cursor.execute(
            """
            UPDATE DynamicProperties 
            SET weight = weight + 1 
            WHERE parent_id = ? AND relation = ? AND target_value = ?
            """,
            (parent_id, relation, target_value)
        )
        db.commit()
        
        # Return existing property ID
        db.cursor.execute(
            """
            SELECT id FROM DynamicProperties 
            WHERE parent_id = ? AND relation = ? AND target_value = ?
            """,
            (parent_id, relation, target_value)
        )
        row = db.cursor.fetchone()
        return row['id'] if row else None


def get_properties(db: DatabaseConnection, parent_id: int, 
                   relation: Optional[str] = None) -> List[Dict]:
    """
    Get all properties of a ConceptObject.
    
    Args:
        db: Database connection
        parent_id: ID of the parent ConceptObject
        relation: Optional filter by relation type
    
    Returns:
        List of property dictionaries
    """
    if relation:
        db.cursor.execute(
            """
            SELECT * FROM DynamicProperties 
            WHERE parent_id = ? AND relation = ?
            ORDER BY weight DESC, created_at
            """,
            (parent_id, relation)
        )
    else:
        db.cursor.execute(
            """
            SELECT * FROM DynamicProperties 
            WHERE parent_id = ?
            ORDER BY relation, weight DESC
            """,
            (parent_id,)
        )
    
    return [dict(row) for row in db.cursor.fetchall()]


def get_property_relations(db: DatabaseConnection, parent_id: int) -> List[str]:
    """
    Get all unique relation types for a ConceptObject.
    
    Args:
        db: Database connection
        parent_id: ID of the parent ConceptObject
    
    Returns:
        List of unique relation names
    """
    db.cursor.execute(
        """
        SELECT DISTINCT relation FROM DynamicProperties 
        WHERE parent_id = ?
        ORDER BY relation
        """,
        (parent_id,)
    )
    
    return [row['relation'] for row in db.cursor.fetchall()]


def remove_property(db: DatabaseConnection, parent_id: int, relation: str,
                   target_value: Optional[str] = None) -> bool:
    """
    Remove a property or all properties of a relation type.
    
    Args:
        db: Database connection
        parent_id: ID of the parent ConceptObject
        relation: Property key
        target_value: Specific value to remove (if None, removes all with this relation)
    
    Returns:
        True if something was removed, False otherwise
    """
    if target_value:
        db.cursor.execute(
            """
            DELETE FROM DynamicProperties 
            WHERE parent_id = ? AND relation = ? AND target_value = ?
            """,
            (parent_id, relation, target_value)
        )
    else:
        db.cursor.execute(
            """
            DELETE FROM DynamicProperties 
            WHERE parent_id = ? AND relation = ?
            """,
            (parent_id, relation)
        )
    
    db.commit()
    return db.cursor.rowcount > 0


def property_exists(db: DatabaseConnection, parent_id: int, relation: str,
                   target_value: Optional[str] = None) -> bool:
    """
    Check if a property exists.
    
    Args:
        db: Database connection
        parent_id: ID of the parent ConceptObject
        relation: Property key
        target_value: Specific value to check (if None, checks if relation exists)
    
    Returns:
        True if exists, False otherwise
    """
    if target_value:
        db.cursor.execute(
            """
            SELECT 1 FROM DynamicProperties 
            WHERE parent_id = ? AND relation = ? AND target_value = ?
            """,
            (parent_id, relation, target_value)
        )
    else:
        db.cursor.execute(
            """
            SELECT 1 FROM DynamicProperties 
            WHERE parent_id = ? AND relation = ?
            """,
            (parent_id, relation)
        )
    
    return db.cursor.fetchone() is not None


def get_property_count(db: DatabaseConnection, parent_id: Optional[int] = None) -> int:
    """
    Get count of properties.
    
    Args:
        db: Database connection
        parent_id: Optional filter by parent object
    
    Returns:
        Count of properties
    """
    if parent_id:
        db.cursor.execute(
            "SELECT COUNT(*) as count FROM DynamicProperties WHERE parent_id = ?",
            (parent_id,)
        )
    else:
        db.cursor.execute("SELECT COUNT(*) as count FROM DynamicProperties")
    
    return db.cursor.fetchone()['count']


def get_objects_with_property(db: DatabaseConnection, relation: str, 
                              target_value: str) -> List[int]:
    """
    Find all objects that have a specific property value.
    
    Args:
        db: Database connection
        relation: Property key
        target_value: Property value to search for
    
    Returns:
        List of parent object IDs
    """
    db.cursor.execute(
        """
        SELECT DISTINCT parent_id FROM DynamicProperties 
        WHERE relation = ? AND target_value = ?
        """,
        (relation, target_value)
    )
    
    return [row['parent_id'] for row in db.cursor.fetchall()]


def update_property_weight(db: DatabaseConnection, parent_id: int, 
                          relation: str, target_value: str, weight: int) -> bool:
    """
    Update the weight of a property (for importance/frequency).
    
    Args:
        db: Database connection
        parent_id: ID of the parent ConceptObject
        relation: Property key
        target_value: Property value
        weight: New weight value
    
    Returns:
        True if updated, False if not found
    """
    db.cursor.execute(
        """
        UPDATE DynamicProperties 
        SET weight = ? 
        WHERE parent_id = ? AND relation = ? AND target_value = ?
        """,
        (weight, parent_id, relation, target_value)
    )
    db.commit()
    
    return db.cursor.rowcount > 0
