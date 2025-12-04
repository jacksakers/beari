"""
Question Generator Module for Beari AI
Generates intelligent questions about unknown words based on context.
"""

import random
from typing import Dict, List, Optional


class QuestionGenerator:
    """Generates contextual questions to learn about unknown words."""
    
    def __init__(self):
        """Initialize the question generator with templates."""
        
        # Templates for different question types
        self.noun_questions = [
            "I don't know the word '{word}'. Is '{word}' a person, place, or thing?",
            "What is '{word}'? Is it a person, place, thing, or idea?",
            "I haven't learned '{word}' yet. Can you tell me what '{word}' is?",
            "'{word}' is new to me. Is it a type of animal, object, or something else?"
        ]
        
        self.verb_questions = [
            "I don't know what '{word}' means. Is it an action or activity?",
            "What does '{word}' mean? Is it something you do?",
            "Is '{word}' an action word? What does it mean?",
            "Can you explain what it means to '{word}'?"
        ]
        
        self.adjective_questions = [
            "I don't know '{word}'. Is it a describing word (adjective)?",
            "What does '{word}' mean? Does it describe something?",
            "Is '{word}' a word that describes qualities or characteristics?"
        ]
        
        self.general_questions = [
            "I don't know the word '{word}'. Can you tell me what it means?",
            "'{word}' is unfamiliar to me. What does it mean?",
            "I need to learn about '{word}'. What is it?",
            "Please help me understand: what is '{word}'?"
        ]
        
        # Follow-up questions for categorization
        self.category_questions = {
            'animal': "Is '{word}' a type of animal?",
            'technology': "Does '{word}' relate to technology or computers?",
            'emotion': "Is '{word}' related to feelings or emotions?",
            'food': "Is '{word}' something you can eat?",
            'action': "Is '{word}' something you can do?",
            'object': "Is '{word}' a physical object?",
            'concept': "Is '{word}' an idea or concept?"
        }
        
        # Response patterns to detect user's answer type
        self.pos_indicators = {
            'noun': ['person', 'place', 'thing', 'object', 'animal', 'idea', 'concept', 'noun'],
            'verb': ['action', 'activity', 'do', 'doing', 'verb', 'perform'],
            'adjective': ['describe', 'describing', 'quality', 'adjective', 'characteristic']
        }
        
        self.category_indicators = {
            'animal': ['animal', 'creature', 'beast', 'pet', 'wildlife'],
            'technology': ['technology', 'computer', 'software', 'digital', 'tech', 'device'],
            'emotion': ['emotion', 'feeling', 'mood', 'sentiment'],
            'food': ['food', 'eat', 'edible', 'meal', 'dish'],
            'object': ['object', 'thing', 'item', 'tool'],
            'concept': ['idea', 'concept', 'abstract', 'notion']
        }
    
    def generate_question(self, word: str, context: Optional[Dict] = None) -> str:
        """
        Generate an appropriate question about an unknown word.
        
        Args:
            word: The unknown word to ask about
            context: Optional context information (previous/next words, sentence structure)
        
        Returns:
            Question string to ask the user
        """
        # If we have context clues, try to be more specific
        if context:
            question = self._contextual_question(word, context)
            if question:
                return question
        
        # Otherwise, ask a general question
        return random.choice(self.general_questions).format(word=word)
    
    def _contextual_question(self, word: str, context: Dict) -> Optional[str]:
        """
        Generate a context-aware question based on surrounding words.
        
        Args:
            word: The unknown word
            context: Dictionary with 'prev_word', 'next_word', etc.
        
        Returns:
            Contextual question or None if no context available
        """
        prev_word = context.get('prev_word', '')
        next_word = context.get('next_word', '')
        
        # Check if word appears after common verb patterns
        if prev_word in ['to', 'can', 'will', 'would', 'should', 'could']:
            return random.choice(self.verb_questions).format(word=word)
        
        # Check if word appears before "is" or "are" (likely a noun/subject)
        if next_word in ['is', 'are', 'was', 'were']:
            return random.choice(self.noun_questions).format(word=word)
        
        # Check if word appears after articles (likely a noun)
        if prev_word in ['a', 'an', 'the']:
            return random.choice(self.noun_questions).format(word=word)
        
        # Check if word appears after "very", "so", "really" (likely an adjective)
        if prev_word in ['very', 'so', 'really', 'quite', 'extremely']:
            return random.choice(self.adjective_questions).format(word=word)
        
        return None
    
    def generate_category_question(self, word: str, category_hint: str = None) -> str:
        """
        Generate a question to determine the category/meaning_tag of a word.
        
        Args:
            word: The word being categorized
            category_hint: Optional hint about likely category
        
        Returns:
            Question string about category
        """
        if category_hint and category_hint in self.category_questions:
            return self.category_questions[category_hint].format(word=word)
        
        # Ask general categorization question
        questions = [
            "What category does '{word}' belong to? (e.g., animal, technology, emotion, food)",
            "How would you categorize '{word}'?",
            "What type of thing is '{word}'?"
        ]
        return random.choice(questions).format(word=word)
    
    def parse_user_response(self, response: str) -> Dict[str, any]:
        """
        Parse the user's answer to extract POS tag and meaning tag.
        
        Args:
            response: User's response to the question
        
        Returns:
            Dictionary with 'pos_tag' and 'meaning_tag' if detected
        """
        response_lower = response.lower()
        result = {
            'pos_tag': None,
            'meaning_tag': None
        }
        
        # Detect Part of Speech
        for pos, indicators in self.pos_indicators.items():
            if any(indicator in response_lower for indicator in indicators):
                result['pos_tag'] = pos.capitalize()
                break
        
        # Detect category/meaning
        for category, indicators in self.category_indicators.items():
            if any(indicator in response_lower for indicator in indicators):
                result['meaning_tag'] = category
                break
        
        # If no structured tags found, try to extract the raw response
        if not result['pos_tag'] and not result['meaning_tag']:
            result['raw_response'] = response.strip()
        
        return result
    
    def generate_confirmation(self, word: str, pos_tag: str = None, 
                            meaning_tag: str = None) -> str:
        """
        Generate a confirmation message after learning a new word.
        
        Args:
            word: The word that was learned
            pos_tag: Part of Speech tag
            meaning_tag: Meaning/category tag
        
        Returns:
            Confirmation message
        """
        messages = []
        
        if pos_tag and meaning_tag:
            messages = [
                f"Got it! I've learned that '{word}' is a {pos_tag} related to {meaning_tag}.",
                f"Thanks! I now know '{word}' is a {pos_tag} in the {meaning_tag} category.",
                f"Understood. '{word}' ({pos_tag}, {meaning_tag}) has been added to my vocabulary."
            ]
        elif pos_tag:
            messages = [
                f"Thank you! I've learned that '{word}' is a {pos_tag}.",
                f"Got it. '{word}' is now in my vocabulary as a {pos_tag}."
            ]
        elif meaning_tag:
            messages = [
                f"Thanks! I've learned about '{word}' (category: {meaning_tag}).",
                f"Understood. '{word}' has been added to my {meaning_tag} vocabulary."
            ]
        else:
            messages = [
                f"Thank you! I've added '{word}' to my vocabulary.",
                f"Got it! '{word}' is now part of my knowledge."
            ]
        
        return random.choice(messages)
    
    def generate_relation_question(self, word_a: str, word_b: str) -> str:
        """
        Generate a question about the relationship between two words.
        
        Args:
            word_a: First word
            word_b: Second word
        
        Returns:
            Question about their relationship
        """
        questions = [
            f"How are '{word_a}' and '{word_b}' related?",
            f"What's the connection between '{word_a}' and '{word_b}'?",
            f"Can you explain the relationship between '{word_a}' and '{word_b}'?"
        ]
        return random.choice(questions)
