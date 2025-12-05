"""
Input Parser for Beari2.
Parses user sentences to extract subjects, predicates, and objects.
"""

import re
from typing import Dict, List, Tuple, Optional


class InputParser:
    """
    Parses natural language input to extract components.
    
    Identifies:
    - Subject (the actor)
    - Verb (the action)
    - Object (the receiver)
    - Adjectives (descriptors)
    """
    
    def __init__(self):
        """Initialize the parser."""
        # Common articles and determiners to filter
        self.stop_words = {'the', 'a', 'an', 'this', 'that', 'these', 'those'}
        
        # Common verbs that indicate relationships
        self.relation_verbs = {
            'is': 'is',
            'am': 'is',
            'are': 'is',
            'was': 'is',
            'were': 'is',
            'has': 'can_have',
            'have': 'can_have',
            'had': 'can_have',
            'can': 'can_do',
            'could': 'can_do',
            'feels': 'feels_like',
            'feel': 'feels_like',
            'felt': 'feels_like',
        }
    
    def tokenize(self, text: str) -> List[str]:
        """
        Split text into tokens.
        
        Args:
            text: Input text
        
        Returns:
            List of word tokens
        """
        # Remove punctuation except apostrophes
        text = re.sub(r'[^\w\s\']', '', text)
        return [t.lower() for t in text.split() if t]
    
    def parse_sentence(self, sentence: str) -> Dict:
        """
        Parse a sentence into components.
        
        Args:
            sentence: Input sentence
        
        Returns:
            Dictionary with parsed components
        """
        tokens = self.tokenize(sentence)
        
        # Find verb position
        verb_idx, verb = self._find_verb(tokens)
        
        result = {
            'original': sentence,
            'tokens': tokens,
            'subject': None,
            'verb': verb,
            'verb_relation': None,
            'object': None,
            'adjectives': [],
            'structure': 'unknown'
        }
        
        if verb_idx is not None:
            # Get verb relation type
            result['verb_relation'] = self.relation_verbs.get(verb, 'action')
            
            # Extract subject (words before verb)
            subject_tokens = [t for t in tokens[:verb_idx] if t not in self.stop_words]
            if subject_tokens:
                result['subject'] = subject_tokens[-1]  # Last non-stop word before verb
            
            # Extract object (words after verb)
            object_tokens = [t for t in tokens[verb_idx+1:] if t not in self.stop_words]
            if object_tokens:
                result['object'] = object_tokens[0]  # First non-stop word after verb
                
                # Additional words might be adjectives
                if len(object_tokens) > 1:
                    result['adjectives'] = object_tokens[1:]
            
            # Determine structure
            if result['subject'] and result['object']:
                result['structure'] = 'subject-verb-object'
            elif result['subject']:
                result['structure'] = 'subject-verb'
            elif result['object']:
                result['structure'] = 'verb-object'
        
        return result
    
    def _find_verb(self, tokens: List[str]) -> Tuple[Optional[int], Optional[str]]:
        """
        Find the main verb in a sentence.
        
        Args:
            tokens: List of word tokens
        
        Returns:
            Tuple of (verb_index, verb_word)
        """
        # Check for known relation verbs first
        for i, token in enumerate(tokens):
            if token in self.relation_verbs:
                return (i, token)
        
        # Common verbs pattern (very basic)
        common_verbs = [
            'do', 'does', 'did', 'make', 'makes', 'made',
            'go', 'goes', 'went', 'get', 'gets', 'got',
            'see', 'saw', 'know', 'knew', 'think', 'thought',
            'take', 'takes', 'took', 'come', 'comes', 'came',
            'want', 'wants', 'wanted', 'use', 'uses', 'used',
            'find', 'finds', 'found', 'give', 'gives', 'gave',
            'tell', 'tells', 'told', 'work', 'works', 'worked',
            'call', 'calls', 'called', 'try', 'tries', 'tried',
            'ask', 'asks', 'asked', 'need', 'needs', 'needed',
            'become', 'becomes', 'became', 'leave', 'leaves', 'left',
            'put', 'puts', 'help', 'helps', 'helped',
        ]
        
        for i, token in enumerate(tokens):
            if token in common_verbs:
                return (i, token)
        
        return (None, None)
    
    def extract_relations(self, parsed: Dict) -> List[Dict]:
        """
        Extract relationships from parsed sentence.
        
        Args:
            parsed: Parsed sentence dictionary
        
        Returns:
            List of relation dictionaries
        """
        relations = []
        
        # Subject-verb-object relations
        if parsed['subject'] and parsed['object']:
            if parsed['verb_relation'] == 'is':
                # "X is Y" -> X is_a Y
                relations.append({
                    'source': parsed['subject'],
                    'relation': 'is',
                    'target': parsed['object']
                })
            elif parsed['verb_relation'] == 'can_have':
                # "X has Y" -> X can_have Y
                relations.append({
                    'source': parsed['subject'],
                    'relation': 'can_have',
                    'target': parsed['object']
                })
            elif parsed['verb_relation'] == 'can_do':
                # "X can Y" -> X can_do Y
                relations.append({
                    'source': parsed['subject'],
                    'relation': 'can_do',
                    'target': parsed['object']
                })
            elif parsed['verb_relation'] == 'feels_like':
                # "X feels Y" -> X feels_like Y
                relations.append({
                    'source': parsed['subject'],
                    'relation': 'feels_like',
                    'target': parsed['object']
                })
        
        # Adjective relations
        if parsed['object'] and parsed['adjectives']:
            for adj in parsed['adjectives']:
                relations.append({
                    'source': parsed['object'],
                    'relation': 'is',
                    'target': adj
                })
        
        return relations
