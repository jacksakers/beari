"""
Question Generator for Beari2.
Generates natural language questions about missing object properties.
"""

from typing import Dict
from db.schema import RELATION_TYPES


def generate_question(word: str, field: str, obj_type: str) -> str:
    """
    Generate a natural language question about a missing field.
    
    Args:
        word: The word/concept to ask about
        field: The missing property field
        obj_type: Type of object (Noun, Verb, Adjective)
    
    Returns:
        Natural language question string
    """
    # Question templates based on field type and object type
    templates = {
        'is': {
            'Noun': f"What is {word}?",
            'Verb': f"What kind of action is {word}?",
            'Adjective': f"What does {word} describe?",
        },
        'feels_like': {
            'Noun': f"What does {word} feel like?",
            'Verb': f"What does it feel like to {word}?",
            'Adjective': f"How does something {word} feel?",
        },
        'can_do': {
            'Noun': f"What can {word} do?",
            'Verb': f"What can happen when you {word}?",
            'Adjective': f"What can {word} things do?",
        },
        'can_have': {
            'Noun': f"What can {word} have?",
            'Verb': f"What do you need to {word}?",
            'Adjective': f"What can {word} things have?",
        },
        'can_be': {
            'Noun': f"What can {word} be?",
            'Verb': f"What states result from {word}?",
            'Adjective': f"What else can be {word}?",
        },
        'part_of': {
            'Noun': f"What is {word} part of?",
            'Verb': f"What process is {word} part of?",
            'Adjective': f"What category is {word} part of?",
        },
        'used_for': {
            'Noun': f"What is {word} used for?",
            'Verb': f"Why do people {word}?",
            'Adjective': f"When is {word} used?",
        },
        'performed_by': {
            'Verb': f"Who or what can {word}?",
        },
        'affects': {
            'Verb': f"What does {word} affect?",
        },
        'requires': {
            'Verb': f"What does {word} require?",
        },
        'results_in': {
            'Verb': f"What does {word} result in?",
        },
        'describes': {
            'Adjective': f"What does {word} describe?",
        },
        'intensity': {
            'Adjective': f"How intense or strong is {word}?",
        },
        'opposite': {
            'Adjective': f"What is the opposite of {word}?",
        },
        'similar_to': {
            'Adjective': f"What is similar to {word}?",
        },
        'can_describe': {
            'Adjective': f"What kinds of things can be {word}?",
        },
    }
    
    # Get the appropriate template
    if field in templates and obj_type in templates[field]:
        return templates[field][obj_type]
    
    # Fallback generic question
    relation_desc = RELATION_TYPES.get(field, field)
    return f"Tell me about the {relation_desc} of {word}?"


def generate_confirmation(word: str, field: str, value: str) -> str:
    """
    Generate a confirmation message after learning new information.
    
    Args:
        word: The word that was learned about
        field: The property field that was filled
        value: The value that was learned
    
    Returns:
        Confirmation message
    """
    templates = {
        'is': f"I see, {word} is {value}.",
        'feels_like': f"I understand, {word} feels like {value}.",
        'can_do': f"Got it, {word} can {value}.",
        'can_have': f"I see, {word} can have {value}.",
        'can_be': f"Understood, {word} can be {value}.",
        'part_of': f"I see, {word} is part of {value}.",
        'used_for': f"Got it, {word} is used for {value}.",
        'performed_by': f"I understand, {word} is performed by {value}.",
        'affects': f"I see, {word} affects {value}.",
        'requires': f"Got it, {word} requires {value}.",
        'results_in': f"I understand, {word} results in {value}.",
        'describes': f"I see, {word} describes {value}.",
        'intensity': f"Got it, {word} has intensity: {value}.",
        'opposite': f"I see, the opposite of {word} is {value}.",
        'similar_to': f"I understand, {word} is similar to {value}.",
        'can_describe': f"Got it, {word} can describe {value}.",
    }
    
    return templates.get(field, f"I learned that {word} has {field}: {value}.")
