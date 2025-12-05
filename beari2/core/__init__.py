"""Core package for Beari2."""

from .gap_analysis import (
    find_learning_opportunity,
    get_all_gaps,
    calculate_completeness,
    prioritize_learning_opportunities,
    suggest_next_question_field
)
from .object_manager import ObjectManager
from .question_generator import generate_question, generate_confirmation

__all__ = [
    'find_learning_opportunity',
    'get_all_gaps',
    'calculate_completeness',
    'prioritize_learning_opportunities',
    'suggest_next_question_field',
    'ObjectManager',
    'generate_question',
    'generate_confirmation'
]
