"""Database package for Beari2."""

from .connection import DatabaseConnection
from .init_db import initialize_database, reset_database
from .object_operations import (
    create_object, get_object, get_object_by_id, update_object,
    delete_object, object_exists, get_all_objects, get_object_count
)
from .property_operations import (
    add_property, get_properties, get_property_relations, remove_property,
    property_exists, get_property_count, get_objects_with_property,
    update_property_weight
)
from .schema import STANDARD_FIELDS, RELATION_TYPES

__all__ = [
    'DatabaseConnection',
    'initialize_database', 'reset_database',
    'create_object', 'get_object', 'get_object_by_id', 'update_object',
    'delete_object', 'object_exists', 'get_all_objects', 'get_object_count',
    'add_property', 'get_properties', 'get_property_relations', 'remove_property',
    'property_exists', 'get_property_count', 'get_objects_with_property',
    'update_property_weight',
    'STANDARD_FIELDS', 'RELATION_TYPES'
]
