"""
Object Manager for Beari2.
Bridges between LivingObjects and database operations.
"""

from typing import Optional, List
from models.living_object import LivingObject
from db import (
    DatabaseConnection, create_object, get_object, get_all_objects,
    add_property, get_properties, get_property_relations
)


class ObjectManager:
    """
    Manages LivingObject lifecycle and persistence.
    
    Provides high-level operations for creating, loading, and updating
    LivingObjects with automatic database synchronization.
    """
    
    def __init__(self, db_path: str = "beari2.db"):
        """
        Initialize the ObjectManager.
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
    
    def create_or_get(self, word: str, pos: str) -> LivingObject:
        """
        Create a new LivingObject or retrieve existing one.
        
        Args:
            word: The word/concept
            pos: Part of speech
        
        Returns:
            LivingObject instance
        """
        with DatabaseConnection(self.db_path) as db:
            # Try to get existing object
            obj_data = get_object(db, word)
            
            if obj_data:
                # Load existing object
                return self._load_object(db, obj_data)
            else:
                # Create new object
                obj_id = create_object(db, word, pos)
                obj = LivingObject(word, pos, obj_id)
                return obj
    
    def load_object(self, word: str) -> Optional[LivingObject]:
        """
        Load a LivingObject from the database.
        
        Args:
            word: The word to load
        
        Returns:
            LivingObject instance or None if not found
        """
        with DatabaseConnection(self.db_path) as db:
            obj_data = get_object(db, word)
            
            if obj_data:
                return self._load_object(db, obj_data)
            
            return None
    
    def _load_object(self, db: DatabaseConnection, obj_data: dict) -> LivingObject:
        """
        Internal method to load object with properties.
        
        Args:
            db: Database connection
            obj_data: Object data from database
        
        Returns:
            LivingObject instance
        """
        obj = LivingObject(
            obj_data['name'],
            obj_data['type'],
            obj_data['id']
        )
        
        # Load properties
        properties = get_properties(db, obj_data['id'])
        
        for prop in properties:
            obj.add_property(prop['relation'], prop['target_value'])
        
        return obj
    
    def save_object(self, obj: LivingObject) -> None:
        """
        Save a LivingObject to the database.
        
        This synchronizes all properties to the database.
        
        Args:
            obj: LivingObject to save
        """
        with DatabaseConnection(self.db_path) as db:
            # Ensure object exists in database
            if obj.id is None:
                obj.id = create_object(db, obj.word, obj.pos)
            
            # Get current properties in database
            db_relations = get_property_relations(db, obj.id)
            
            # Add/update all properties
            for relation, values in obj.properties.items():
                for value in values:
                    add_property(db, obj.id, relation, str(value))
    
    def add_property_to_object(self, word: str, relation: str, value: str) -> bool:
        """
        Add a property to an object (creates object if needed).
        
        Args:
            word: The word/concept
            relation: Property key
            value: Property value
        
        Returns:
            True if successful
        """
        with DatabaseConnection(self.db_path) as db:
            obj_data = get_object(db, word)
            
            if not obj_data:
                # Object doesn't exist, can't add property without knowing POS
                return False
            
            add_property(db, obj_data['id'], relation, value)
            return True
    
    def get_all(self, obj_type: Optional[str] = None) -> List[LivingObject]:
        """
        Get all LivingObjects from database.
        
        Args:
            obj_type: Optional filter by type
        
        Returns:
            List of LivingObject instances
        """
        with DatabaseConnection(self.db_path) as db:
            objects_data = get_all_objects(db, obj_type)
            
            objects = []
            for obj_data in objects_data:
                obj = self._load_object(db, obj_data)
                objects.append(obj)
            
            return objects
