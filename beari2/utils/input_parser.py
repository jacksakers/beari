"""
Input Parser for Beari2.
Parses user sentences to extract subjects, predicates, and objects.
Also detects sentence types (question, statement, command).
"""

import re
import os
from typing import Dict, List, Tuple, Optional
from .debug_logger import get_debug_logger


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
        
        # Greeting words
        self.greetings = {
            'hello', 'hi', 'hey', 'greetings', 'howdy', 'hiya',
            'good morning', 'good afternoon', 'good evening', 'good night'
        }
        
        # Possessive words
        self.possessives = {
            'my': 'your',
            'your': 'my',
            'mine': 'yours',
            'yours': 'mine',
            'our': 'your',
            'their': 'their',
        }
        
        # Pronoun conversions for response generation
        self.pronoun_conversions = {
            'i': 'you',
            'you': 'i',
            'me': 'you',
            'we': 'you',
            'us': 'you',
            'beari': 'i',
        }
        
        # Verb conjugations (after pronoun conversion)
        self.verb_conjugations = {
            ('i', 'is'): 'am',
            ('i', 'are'): 'am',
            ('i', 'was'): 'was',
            ('you', 'is'): 'are',
            ('you', 'am'): 'are',
            ('you', 'was'): 'were',
        }
        
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
        
        # Load training data word lists
        self._load_word_lists()
        
        # Debug logger
        self.debug = get_debug_logger()
    
    def _load_word_lists(self):
        """Load nouns, verbs, and adjectives from training data."""
        base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'training_data')
        
        self.known_nouns = set()
        self.known_verbs = set()
        self.known_adjectives = set()
        
        # Load nouns
        try:
            nouns_path = os.path.join(base_path, 'nouns.txt')
            with open(nouns_path, 'r') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if parts:
                        self.known_nouns.add(parts[0].lower())
        except FileNotFoundError:
            pass
        
        # Load verbs
        try:
            verbs_path = os.path.join(base_path, 'verbs.txt')
            with open(verbs_path, 'r') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if parts:
                        self.known_verbs.add(parts[0].lower())
        except FileNotFoundError:
            pass
        
        # Load adjectives
        try:
            adjectives_path = os.path.join(base_path, 'adjectives.txt')
            with open(adjectives_path, 'r') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if parts:
                        self.known_adjectives.add(parts[0].lower())
        except FileNotFoundError:
            pass
    
    def detect_greeting(self, text: str) -> Optional[str]:
        """
        Detect if text contains a greeting.
        
        Args:
            text: Input text
        
        Returns:
            The greeting word/phrase found, or None
        """
        text_lower = text.lower()
        
        # Check multi-word greetings first
        for greeting in self.greetings:
            if ' ' in greeting and greeting in text_lower:
                self.debug.log_parse(f"Detected greeting: '{greeting}'")
                return greeting
        
        # Check single-word greetings
        tokens = self.tokenize(text)
        for token in tokens:
            if token in self.greetings:
                self.debug.log_parse(f"Detected greeting: '{token}'")
                return token
        
        return None
    
    def get_pos(self, word: str) -> Optional[str]:
        """
        Determine part of speech for a word.
        
        Args:
            word: Word to check
        
        Returns:
            'Noun', 'Verb', 'Adjective', or None if unknown
        """
        word_lower = word.lower()
        
        if word_lower in self.known_nouns:
            return 'Noun'
        elif word_lower in self.known_verbs:
            return 'Verb'
        elif word_lower in self.known_adjectives:
            return 'Adjective'
        
        return None
    
    def convert_for_response(self, text: str) -> str:
        """
        Convert user text to response text (pronoun and possessive conversions).
        
        Args:
            text: User's text
        
        Returns:
            Converted text for response
        """
        tokens = self.tokenize(text)
        converted_tokens = []
        
        for i, token in enumerate(tokens):
            # Convert pronouns
            if token in self.pronoun_conversions:
                converted = self.pronoun_conversions[token]
                converted_tokens.append(converted)
                self.debug.log_parse(f"Converted pronoun '{token}' -> '{converted}'")
            # Convert possessives
            elif token in self.possessives:
                converted = self.possessives[token]
                converted_tokens.append(converted)
                self.debug.log_parse(f"Converted possessive '{token}' -> '{converted}'")
            else:
                converted_tokens.append(token)
        
        # Apply verb conjugations
        for i in range(len(converted_tokens) - 1):
            pronoun = converted_tokens[i]
            verb = converted_tokens[i + 1]
            
            if (pronoun, verb) in self.verb_conjugations:
                conjugated = self.verb_conjugations[(pronoun, verb)]
                converted_tokens[i + 1] = conjugated
                self.debug.log_parse(f"Conjugated verb '{verb}' -> '{conjugated}' after '{pronoun}'")
        
        return ' '.join(converted_tokens)
    
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
        self.debug.section(f"PARSING: '{sentence}'")
        
        # Check for greeting
        greeting = self.detect_greeting(sentence)
        
        tokens = self.tokenize(sentence)
        self.debug.log_parse(f"Tokens: {tokens}")
        
        # Detect sentence type first
        sentence_info = self.detect_sentence_type(sentence)
        self.debug.log_parse(f"Sentence type: {sentence_info['sentence_type']}")
        
        # Find verb position
        verb_idx, verb = self._find_verb(tokens)
        if verb:
            self.debug.log_parse(f"Found verb '{verb}' at position {verb_idx}")
        
        # Track subjects, adjectives, and possessives
        subjects = []
        adjectives = []
        possessives = []
        unknown_words = []
        
        # Analyze each token
        for i, token in enumerate(tokens):
            self.debug.log_step(i + 1, f"Analyzing word '{token}'")
            self.debug.indent()
            
            # Skip if it's a greeting or stop word
            if token in self.greetings or token in self.stop_words:
                self.debug.log_parse(f"'{token}' is a greeting or stop word, skipping")
                self.debug.dedent()
                continue
            
            # Check for possessive
            if token in self.possessives:
                possessives.append(token)
                self.debug.log_parse(f"'{token}' detected as possessive")
                self.debug.dedent()
                continue
            
            # Determine part of speech
            pos = self.get_pos(token)
            
            # Also check for verb forms (enjoying -> enjoy)
            if pos is None:
                base_form = None
                if token.endswith('ing'):
                    base_form = token[:-3]
                    if base_form and base_form in self.known_verbs:
                        pos = 'Verb'
                elif token.endswith('ed'):
                    base_form = token[:-2]
                    if base_form and base_form in self.known_verbs:
                        pos = 'Verb'
                elif token.endswith('s') and not token.endswith('ss'):
                    base_form = token[:-1]
                    if base_form and base_form in self.known_verbs:
                        pos = 'Verb'
            
            if pos == 'Noun':
                subjects.append(token)
                self.debug.log_parse(f"'{token}' detected as Noun, added to subjects")
            elif pos == 'Adjective':
                adjectives.append(token)
                self.debug.log_parse(f"'{token}' detected as Adjective")
            elif pos == 'Verb':
                self.debug.log_parse(f"'{token}' detected as Verb")
            elif pos is None and token not in self.relation_verbs:
                # Unknown word
                # Skip pronouns and question words
                if token not in ['i', 'you', 'me', 'we', 'us', 'beari'] and token not in self.QUESTION_WORDS:
                    unknown_words.append(token)
                    self.debug.log_parse(f"'{token}' is unknown - POS needs to be determined")
            
            self.debug.dedent()
        
        result = {
            'original': sentence,
            'tokens': tokens,
            'greeting': greeting,
            'subject': None,
            'subjects': subjects,  # All noun subjects in sentence
            'verb': verb,
            'verb_relation': None,
            'object': None,
            'adjectives': adjectives,
            'possessives': possessives,
            'unknown_words': unknown_words,
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
                self.debug.log_parse(f"Primary subject: '{result['subject']}'")
            
            # Extract object (words after verb)
            object_tokens = [t for t in tokens[verb_idx+1:] if t not in self.stop_words]
            if object_tokens:
                result['object'] = object_tokens[0]  # First non-stop word after verb
                self.debug.log_parse(f"Primary object: '{result['object']}'")
                
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
        
        self.debug.log_parse(f"Parse result: subjects={subjects}, adjectives={adjectives}, unknown={unknown_words}")
        
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
        
        # Check loaded verb list
        for i, token in enumerate(tokens):
            # Handle verb tenses (remove -ing, -ed, -s)
            base_form = token
            if token.endswith('ing'):
                base_form = token[:-3]  # "enjoying" -> "enjoy"
                if base_form.endswith('i'):
                    base_form = base_form[:-1] + 'y'  # Handle "trying" -> "try"
            elif token.endswith('ed'):
                base_form = token[:-2]  # "walked" -> "walk"
            elif token.endswith('s') and not token.endswith('ss'):
                base_form = token[:-1]  # "walks" -> "walk"
            
            if base_form in self.known_verbs:
                self.debug.log_parse(f"Found verb '{token}' (base: '{base_form}')")
                return (i, base_form)
        
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
        
        self.debug.log_parse("Extracting relations...")
        self.debug.indent()
        
        # Subject-verb-object relations
        if parsed['subject'] and parsed['object']:
            if parsed['verb_relation'] == 'is':
                # "X is Y" -> X is_a Y
                relations.append({
                    'source': parsed['subject'],
                    'relation': 'is',
                    'target': parsed['object']
                })
                self.debug.log_learn(f"Relation: {parsed['subject']} is {parsed['object']}")
            elif parsed['verb_relation'] == 'can_have':
                # "X has Y" -> X can_have Y
                relations.append({
                    'source': parsed['subject'],
                    'relation': 'can_have',
                    'target': parsed['object']
                })
                self.debug.log_learn(f"Relation: {parsed['subject']} can_have {parsed['object']}")
            elif parsed['verb_relation'] == 'can_do':
                # "X can Y" -> X can_do Y
                relations.append({
                    'source': parsed['subject'],
                    'relation': 'can_do',
                    'target': parsed['object']
                })
                self.debug.log_learn(f"Relation: {parsed['subject']} can_do {parsed['object']}")
            elif parsed['verb_relation'] == 'feels_like':
                # "X feels Y" -> X feels_like Y
                relations.append({
                    'source': parsed['subject'],
                    'relation': 'feels_like',
                    'target': parsed['object']
                })
                self.debug.log_learn(f"Relation: {parsed['subject']} feels_like {parsed['object']}")
            elif parsed['verb'] and parsed['verb'] not in self.relation_verbs:
                # Custom verb relation
                relations.append({
                    'source': parsed['subject'],
                    'relation': parsed['verb'],
                    'target': parsed['object']
                })
                self.debug.log_learn(f"Relation: {parsed['subject']} {parsed['verb']} {parsed['object']}")
        
        # Adjective-noun relations (adjectives describe nouns)
        if parsed['object'] and parsed['adjectives']:
            for adj in parsed['adjectives']:
                # Object is described by adjective
                relations.append({
                    'source': parsed['object'],
                    'relation': 'is',
                    'target': adj
                })
                # Adjective can describe object
                relations.append({
                    'source': adj,
                    'relation': 'can_describe',
                    'target': parsed['object']
                })
                self.debug.log_learn(f"Relation: {parsed['object']} is {adj}")
                self.debug.log_learn(f"Relation: {adj} can_describe {parsed['object']}")
        
        # Handle subjects list with adjectives
        if parsed['subjects'] and parsed['adjectives']:
            for subject in parsed['subjects']:
                for adj in parsed['adjectives']:
                    # Subject is described by adjective
                    relations.append({
                        'source': subject,
                        'relation': 'is',
                        'target': adj
                    })
                    # Adjective can describe subject
                    relations.append({
                        'source': adj,
                        'relation': 'can_describe',
                        'target': subject
                    })
                    self.debug.log_learn(f"Relation: {subject} is {adj}")
                    self.debug.log_learn(f"Relation: {adj} can_describe {subject}")
        
        self.debug.dedent()
        
        return relations
