"""
Parser Module for Beari AI
Tokenizes user input and identifies unknown words by checking the database.
"""

import re
from typing import List, Tuple, Dict
from db.db_helpers import DatabaseHelper


class Parser:
    """Handles parsing of user input and identification of unknown words."""
    
    def __init__(self, db: DatabaseHelper):
        """
        Initialize the parser with a database connection.
        
        Args:
            db: DatabaseHelper instance for vocabulary lookups
        """
        self.db = db
    
    def tokenize(self, text: str) -> List[str]:
        """
        Split text into individual words/tokens.
        
        This handles basic punctuation and converts to lowercase.
        More sophisticated tokenization could be added later.
        
        Args:
            text: Input string to tokenize
        
        Returns:
            List of tokens (words)
        """
        # Remove punctuation except apostrophes (for contractions)
        text = re.sub(r'[^\w\s\']', ' ', text)
        
        # Split by whitespace and convert to lowercase
        tokens = text.lower().split()
        
        # Filter out empty strings
        tokens = [t for t in tokens if t]
        
        return tokens
    
    def identify_unknown_words(self, tokens: List[str]) -> List[str]:
        """
        Check which tokens are not in the vocabulary database.
        
        Args:
            tokens: List of word tokens
        
        Returns:
            List of unknown words (not in database)
        """
        unknown = []
        
        for token in tokens:
            if not self.db.word_exists(token):
                # Only add each unknown word once
                if token not in unknown:
                    unknown.append(token)
        
        return unknown
    
    def parse_sentence(self, text: str) -> Dict[str, any]:
        """
        Complete parsing pipeline: tokenize and identify unknowns.
        
        Args:
            text: User input sentence
        
        Returns:
            Dictionary containing:
                - 'original': original text
                - 'tokens': list of all tokens
                - 'known_words': list of known words
                - 'unknown_words': list of unknown words
                - 'has_unknowns': boolean flag
        """
        tokens = self.tokenize(text)
        unknown_words = self.identify_unknown_words(tokens)
        known_words = [t for t in tokens if t not in unknown_words]
        
        return {
            'original': text,
            'tokens': tokens,
            'known_words': known_words,
            'unknown_words': unknown_words,
            'has_unknowns': len(unknown_words) > 0
        }
    
    def get_context_words(self, tokens: List[str], target_word: str) -> Tuple[str, str]:
        """
        Get the words immediately before and after a target word.
        Useful for understanding context.
        
        Args:
            tokens: List of tokens from a sentence
            target_word: The word to find context for
        
        Returns:
            Tuple of (previous_word, next_word), or empty strings if not found
        """
        try:
            idx = tokens.index(target_word)
            prev_word = tokens[idx - 1] if idx > 0 else ""
            next_word = tokens[idx + 1] if idx < len(tokens) - 1 else ""
            return (prev_word, next_word)
        except ValueError:
            return ("", "")
    
    def analyze_sentence_structure(self, tokens: List[str]) -> Dict[str, any]:
        """
        Basic sentence structure analysis.
        
        Identifies potential subjects, verbs, and objects based on
        known POS tags in the database.
        
        Args:
            tokens: List of tokens
        
        Returns:
            Dictionary with structure information
        """
        structure = {
            'nouns': [],
            'verbs': [],
            'adjectives': [],
            'unknown_pos': []
        }
        
        for token in tokens:
            word_info = self.db.get_word(token)
            if word_info:
                pos = word_info.get('pos_tag', '').lower()
                if 'noun' in pos:
                    structure['nouns'].append(token)
                elif 'verb' in pos:
                    structure['verbs'].append(token)
                elif 'adjective' in pos or 'adj' in pos:
                    structure['adjectives'].append(token)
            else:
                structure['unknown_pos'].append(token)
        
        return structure
