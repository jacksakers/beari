"""
Input Parser for Beari2.
Parses user sentences to extract subjects, predicates, and objects.
Also detects sentence types (question, statement, command).
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
    - Sentence type (question, statement, command)
    """
    
    # Question words for detection
    QUESTION_WORDS = {
        'what', 'who', 'where', 'when', 'why', 'how', 
        'which', 'whose', 'whom', 'is', 'are', 'was', 
        'were', 'do', 'does', 'did', 'can', 'could', 
        'will', 'would', 'should', 'have', 'has', 'had'
    }
    
    # Question types based on question word
    QUESTION_TYPE_MAP = {
        'what': 'definition',      # "What is X?" -> asking for definition/identity
        'who': 'identity',         # "Who is X?" -> asking about identity
        'where': 'location',       # "Where is X?" -> asking about location
        'when': 'time',            # "When is X?" -> asking about time
        'why': 'reason',           # "Why is X?" -> asking for reason
        'how': 'manner',           # "How is X?" or "How does X?" -> asking about manner
        'which': 'selection',      # "Which X?" -> asking for selection
        'is': 'confirmation',      # "Is X Y?" -> yes/no confirmation
        'are': 'confirmation',
        'was': 'confirmation',
        'were': 'confirmation',
        'do': 'confirmation',
        'does': 'confirmation',
        'did': 'confirmation',
        'can': 'ability',          # "Can X do Y?" -> asking about ability
        'could': 'ability',
        'will': 'future',
        'would': 'hypothetical',
        'should': 'recommendation',
        'have': 'possession',
        'has': 'possession',
    }
    
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
    
    def detect_sentence_type(self, sentence: str) -> Dict:
        """
        Detect whether the sentence is a question, statement, or command.
        
        Args:
            sentence: Input sentence
            
        Returns:
            Dictionary with sentence_type, question_type, and question_target
        """
        sentence = sentence.strip()
        tokens = self.tokenize(sentence)
        
        result = {
            'sentence_type': 'statement',  # Default
            'question_type': None,
            'question_word': None,
            'question_target': None,  # What the question is about
        }
        
        # Check for question mark (strongest indicator)
        if sentence.endswith('?'):
            result['sentence_type'] = 'question'
        
        # Check if starts with question word
        if tokens:
            first_word = tokens[0]
            if first_word in self.QUESTION_WORDS:
                result['sentence_type'] = 'question'
                result['question_word'] = first_word
                result['question_type'] = self.QUESTION_TYPE_MAP.get(first_word, 'general')
                
                # Extract what the question is about
                result['question_target'] = self._extract_question_target(tokens, first_word)
        
        # Check for command patterns (imperative)
        command_starters = {'tell', 'show', 'give', 'explain', 'describe', 'list'}
        if tokens and tokens[0] in command_starters:
            result['sentence_type'] = 'command'
        
        return result
    
    def _extract_question_target(self, tokens: List[str], question_word: str) -> Optional[str]:
        """
        Extract the target/subject of a question.
        
        For "What is a dog?" -> returns "dog"
        For "Who can fly?" -> returns None (asking about who)
        
        Args:
            tokens: List of word tokens
            question_word: The question word used
            
        Returns:
            The target word/concept being asked about
        """
        # Skip question word and find the main subject
        meaningful_tokens = [t for t in tokens[1:] if t not in self.stop_words 
                           and t not in self.relation_verbs]
        
        if meaningful_tokens:
            return meaningful_tokens[0]
        
        return None
    
    def parse_sentence(self, sentence: str) -> Dict:
        """
        Parse a sentence into components.
        
        Args:
            sentence: Input sentence
        
        Returns:
            Dictionary with parsed components
        """
        tokens = self.tokenize(sentence)
        
        # Detect sentence type first
        sentence_info = self.detect_sentence_type(sentence)
        
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
            'structure': 'unknown',
            # Sentence type information
            'sentence_type': sentence_info['sentence_type'],
            'question_type': sentence_info.get('question_type'),
            'question_word': sentence_info.get('question_word'),
            'question_target': sentence_info.get('question_target'),
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
        
        # import list of common verbs from verbs.txt
        try:
            with open('training_data/verbs.txt', 'r') as f:
                common_verbs = set(line.strip().lower() for line in f if line.strip())
        except FileNotFoundError:
            common_verbs = set()
        
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
