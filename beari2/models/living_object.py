"""
LivingObject Model for Beari2
Represents a dynamic, growing object that can acquire new properties at runtime.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class LivingObject:
    """
    A Living Object that can grow and change dynamically.
    
    Each object represents a concept (word) and can have arbitrary
    properties added to it at runtime through the 'properties' dictionary.
    
    Properties are stored as relation -> [values] mappings, allowing
    multiple values for each property type.
    """
    
    def __init__(self, word: str, pos: str, object_id: Optional[int] = None):
        """
        Initialize a Living Object.
        
        Args:
            word: The word/concept this object represents
            pos: Part of speech (Noun, Verb, Adjective)
            object_id: Database ID (if loaded from DB)
        """
        self.id = object_id
        self.word = word.lower()
        self.pos = pos
        self.properties: Dict[str, List[Any]] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_property(self, relation: str, value: Any) -> None:
        """
        Add a property to this object dynamically.
        
        This is the "growth" mechanism - objects acquire new properties
        as they learn from user input.
        
        Args:
            relation: The property key (e.g., 'is', 'can_have', 'feels_like')
            value: The property value (can be string, int, or another object)
        """
        if relation not in self.properties:
            self.properties[relation] = []
        
        # Avoid duplicates
        if value not in self.properties[relation]:
            self.properties[relation].append(value)
            self.updated_at = datetime.now()
    
    def remove_property(self, relation: str, value: Optional[Any] = None) -> bool:
        """
        Remove a property or specific property value.
        
        Args:
            relation: The property key to remove
            value: Specific value to remove (if None, removes entire property)
        
        Returns:
            True if something was removed, False otherwise
        """
        if relation not in self.properties:
            return False
        
        if value is None:
            # Remove entire property
            del self.properties[relation]
            self.updated_at = datetime.now()
            return True
        else:
            # Remove specific value
            if value in self.properties[relation]:
                self.properties[relation].remove(value)
                self.updated_at = datetime.now()
                
                # Clean up empty property lists
                if not self.properties[relation]:
                    del self.properties[relation]
                
                return True
        
        return False
    
    def get_property(self, relation: str) -> Optional[List[Any]]:
        """
        Get all values for a specific property.
        
        Args:
            relation: The property key to retrieve
        
        Returns:
            List of values, or None if property doesn't exist
        """
        return self.properties.get(relation)
    
    def has_property(self, relation: str, value: Optional[Any] = None) -> bool:
        """
        Check if this object has a specific property or property value.
        
        Args:
            relation: The property key to check
            value: Specific value to check for (if None, just checks if property exists)
        
        Returns:
            True if property exists (and matches value if provided)
        """
        if relation not in self.properties:
            return False
        
        if value is None:
            return True
        
        return value in self.properties[relation]
    
    def get_all_properties(self) -> Dict[str, List[Any]]:
        """
        Get all properties of this object.
        
        Returns:
            Dictionary mapping relations to their values
        """
        return self.properties.copy()
    
    def get_sparse_fields(self, standard_fields: List[str]) -> List[str]:
        """
        Identify which standard fields are missing (for gap analysis).
        
        Args:
            standard_fields: List of expected property keys
        
        Returns:
            List of missing property keys
        """
        return [field for field in standard_fields if field not in self.properties]
    
    def merge_from(self, other: 'LivingObject') -> None:
        """
        Merge properties from another LivingObject into this one.
        
        Args:
            other: Another LivingObject to merge properties from
        """
        for relation, values in other.properties.items():
            for value in values:
                self.add_property(relation, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this object to a dictionary for serialization.
        
        Returns:
            Dictionary representation of this object
        """
        return {
            'id': self.id,
            'word': self.word,
            'pos': self.pos,
            'properties': self.properties,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        props_summary = ', '.join(f"{k}: {len(v)}" for k, v in self.properties.items())
        return f"LivingObject('{self.word}', {self.pos}, properties=[{props_summary}])"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        lines = [f"LivingObject: {self.word} ({self.pos})"]
        for relation, values in sorted(self.properties.items()):
            values_str = ', '.join(str(v) for v in values)
            lines.append(f"  {relation}: {values_str}")
        return '\n'.join(lines)
