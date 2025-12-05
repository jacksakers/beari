"""
Database Schema for Beari2
Implements Entity-Attribute-Value pattern for dynamic object growth.
"""

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS ConceptObjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS DynamicProperties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_id INTEGER NOT NULL,
        relation TEXT NOT NULL,
        target_value TEXT NOT NULL,
        value_type TEXT DEFAULT 'string',
        weight INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES ConceptObjects(id) ON DELETE CASCADE,
        UNIQUE(parent_id, relation, target_value)
    )
    """,
    
    """
    CREATE INDEX IF NOT EXISTS idx_concept_name 
    ON ConceptObjects(name)
    """,
    
    """
    CREATE INDEX IF NOT EXISTS idx_concept_type 
    ON ConceptObjects(type)
    """,
    
    """
    CREATE INDEX IF NOT EXISTS idx_property_parent 
    ON DynamicProperties(parent_id)
    """,
    
    """
    CREATE INDEX IF NOT EXISTS idx_property_relation 
    ON DynamicProperties(relation)
    """,
    
    """
    CREATE INDEX IF NOT EXISTS idx_property_target 
    ON DynamicProperties(target_value)
    """,
]

# Standard property templates for different object types
STANDARD_FIELDS = {
    'Noun': ['is', 'feels_like', 'can_do', 'can_have', 'can_be', 'part_of', 'used_for'],
    'Verb': ['performed_by', 'affects', 'requires', 'results_in', 'feels_like'],
    'Adjective': ['describes', 'intensity', 'opposite', 'similar_to', 'can_describe'],
}

# Common relation types and their descriptions
RELATION_TYPES = {
    'is': 'State or quality of being',
    'feels_like': 'Sensory or emotional quality',
    'can_do': 'Capable action',
    'can_have': 'Possession or containment',
    'can_be': 'Potential state',
    'part_of': 'Component relationship',
    'used_for': 'Purpose or function',
    'performed_by': 'Agent of action',
    'affects': 'Target of action',
    'requires': 'Prerequisite',
    'results_in': 'Consequence',
    'describes': 'Describes which concept',
    'intensity': 'Degree or strength',
    'opposite': 'Antonym',
    'similar_to': 'Synonym or related concept',
    'can_describe': 'Can describe which types',
}
