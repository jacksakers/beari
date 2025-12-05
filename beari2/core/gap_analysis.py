"""
Gap Analysis Engine for Beari2.
Identifies missing properties in LivingObjects to generate learning questions.
"""

from typing import List, Optional, Dict
from models.living_object import LivingObject
from db.schema import STANDARD_FIELDS


def find_learning_opportunity(obj: LivingObject) -> Optional[str]:
    """
    Find the first missing standard field for an object.
    
    This implements the "Gap Detection Algorithm" from the design doc.
    
    Args:
        obj: LivingObject to analyze
    
    Returns:
        Name of a missing field, or None if all fields are filled
    """
    standard_fields = STANDARD_FIELDS.get(obj.pos, [])
    
    for field in standard_fields:
        if not obj.has_property(field):
            return field
    
    return None


def get_all_gaps(obj: LivingObject) -> List[str]:
    """
    Get all missing standard fields for an object.
    
    Args:
        obj: LivingObject to analyze
    
    Returns:
        List of missing field names
    """
    standard_fields = STANDARD_FIELDS.get(obj.pos, [])
    return obj.get_sparse_fields(standard_fields)


def calculate_completeness(obj: LivingObject) -> float:
    """
    Calculate how complete an object is (percentage of fields filled).
    
    Args:
        obj: LivingObject to analyze
    
    Returns:
        Completeness percentage (0.0 to 1.0)
    """
    standard_fields = STANDARD_FIELDS.get(obj.pos, [])
    
    if not standard_fields:
        return 1.0
    
    filled = sum(1 for field in standard_fields if obj.has_property(field))
    return filled / len(standard_fields)


def prioritize_learning_opportunities(objects: List[LivingObject]) -> List[Dict]:
    """
    Prioritize which objects need learning attention most.
    
    Returns objects sorted by incompleteness and recency.
    
    Args:
        objects: List of LivingObjects to analyze
    
    Returns:
        List of dictionaries with object and priority info
    """
    priorities = []
    
    for obj in objects:
        gaps = get_all_gaps(obj)
        completeness = calculate_completeness(obj)
        
        if gaps:  # Only include objects with missing fields
            priorities.append({
                'object': obj,
                'gaps': gaps,
                'completeness': completeness,
                'gap_count': len(gaps),
                'priority_score': (1 - completeness) * 100  # Higher score = more gaps
            })
    
    # Sort by priority score (most incomplete first)
    priorities.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return priorities


def suggest_next_question_field(obj: LivingObject) -> Optional[str]:
    """
    Suggest which field to ask about next based on importance.
    
    Some fields are more important than others for understanding a concept.
    
    Args:
        obj: LivingObject to analyze
    
    Returns:
        Field name to ask about, or None if complete
    """
    # Priority order for different object types
    priority_order = {
        'Noun': ['is', 'can_do', 'can_have', 'feels_like', 'used_for', 'part_of', 'can_be'],
        'Verb': ['performed_by', 'affects', 'feels_like', 'requires', 'results_in'],
        'Adjective': ['describes', 'intensity', 'opposite', 'similar_to', 'can_describe'],
    }
    
    ordered_fields = priority_order.get(obj.pos, [])
    
    for field in ordered_fields:
        if not obj.has_property(field):
            return field
    
    # Fallback to any missing field
    return find_learning_opportunity(obj)
