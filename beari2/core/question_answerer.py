"""
Question Answering Engine for Beari2.
Attempts to answer user questions using knowledge from the Living Object database.
"""

from typing import Dict, Optional, List, Any
import random


class QuestionAnswerer:
    """
    Answers user questions by querying the Living Object database.
    
    Supports different question types:
    - Definition: "What is X?"
    - Property: "What can X do?"
    - Confirmation: "Is X Y?"
    - Relation: "How is X related to Y?"
    """
    
    # Templates for different answer types
    ANSWER_TEMPLATES = {
        'definition': [
            "{word} is {value}.",
            "I know that {word} is {value}.",
            "From what I've learned, {word} is {value}.",
        ],
        'property': [
            "{word} {relation} {value}.",
            "I believe {word} {relation} {value}.",
            "Based on what I know, {word} {relation} {value}.",
        ],
        'confirmation_yes': [
            "Yes, {word} is {value}!",
            "That's right! {word} is {value}.",
            "Correct! I know that {word} is {value}.",
        ],
        'confirmation_no': [
            "I don't think so. I know {word} is {other_value}.",
            "Not exactly. From what I learned, {word} is {other_value}.",
            "Hmm, I don't have that information. But {word} is {other_value}.",
        ],
        'unknown': [
            "I don't know about {word} yet. Can you tell me?",
            "Hmm, I haven't learned about {word}. What can you tell me?",
            "I don't have information about {word}. Would you like to teach me?",
        ],
        'no_properties': [
            "I know about {word}, but I don't have many details yet.",
            "I've heard of {word}, but I'd love to learn more!",
            "I know {word} exists, but what else can you tell me?",
        ],
    }
    
    # Relation to natural language mapping
    RELATION_PHRASES = {
        'is': 'is',
        'are': 'are',
        'can_do': 'can',
        'can_have': 'can have',
        'can_be': 'can be',
        'feels_like': 'feels like',
        'part_of': 'is part of',
        'used_for': 'is used for',
        'performed_by': 'is performed by',
        'affects': 'affects',
        'requires': 'requires',
        'results_in': 'results in',
        'describes': 'describes',
        'opposite': 'is the opposite of',
        'similar_to': 'is similar to',
    }
    
    def __init__(self, object_manager):
        """
        Initialize the question answerer.
        
        Args:
            object_manager: ObjectManager instance for database access
        """
        self.manager = object_manager
    
    def answer_question(self, parsed: Dict) -> Dict:
        """
        Attempt to answer a parsed question.
        
        Args:
            parsed: Parsed sentence dictionary with question info
            
        Returns:
            Dictionary with answer, confidence, and metadata
        """
        question_type = parsed.get('question_type', 'general')
        question_target = parsed.get('question_target')
        question_word = parsed.get('question_word')
        
        # Try to find the target object
        target_obj = None
        if question_target:
            target_obj = self.manager.load_object(question_target)
        
        # Also try with subject/object from parsing
        if not target_obj and parsed.get('subject'):
            target_obj = self.manager.load_object(parsed['subject'])
        if not target_obj and parsed.get('object'):
            target_obj = self.manager.load_object(parsed['object'])
        
        # Generate answer based on question type
        if question_type == 'definition':
            return self._answer_definition(question_target, target_obj, parsed)
        elif question_type == 'confirmation':
            return self._answer_confirmation(question_target, target_obj, parsed)
        elif question_type == 'ability':
            return self._answer_ability(question_target, target_obj, parsed)
        elif question_type == 'manner':
            return self._answer_manner(question_target, target_obj, parsed)
        else:
            return self._answer_general(question_target, target_obj, parsed)
    
    def _answer_definition(self, word: str, obj: Any, parsed: Dict) -> Dict:
        """Answer 'What is X?' type questions."""
        if not obj:
            return self._unknown_answer(word or parsed.get('subject', 'that'))
        
        # Look for 'is' properties
        is_values = obj.get_property('is')
        
        if is_values:
            value = is_values[0]  # Use first value
            template = random.choice(self.ANSWER_TEMPLATES['definition'])
            answer = template.format(word=obj.word, value=value)
            
            return {
                'answered': True,
                'answer': answer,
                'object': obj.word,
                'property': 'is',
                'values': is_values,
                'confidence': 0.9,
            }
        
        # Try other properties
        other_answer = self._find_any_property_answer(obj)
        if other_answer:
            return other_answer
        
        # Object exists but no properties
        template = random.choice(self.ANSWER_TEMPLATES['no_properties'])
        return {
            'answered': True,
            'answer': template.format(word=obj.word),
            'object': obj.word,
            'confidence': 0.5,
        }
    
    def _answer_confirmation(self, word: str, obj: Any, parsed: Dict) -> Dict:
        """Answer 'Is X Y?' type questions."""
        if not obj:
            return self._unknown_answer(word or parsed.get('subject', 'that'))
        
        # The question asks if X is Y, so check parsed object
        query_value = parsed.get('object')
        
        if query_value:
            # Check if this value exists in properties
            is_values = obj.get_property('is') or []
            
            if query_value.lower() in [v.lower() for v in is_values]:
                template = random.choice(self.ANSWER_TEMPLATES['confirmation_yes'])
                return {
                    'answered': True,
                    'answer': template.format(word=obj.word, value=query_value),
                    'confirmed': True,
                    'object': obj.word,
                    'confidence': 0.95,
                }
            elif is_values:
                template = random.choice(self.ANSWER_TEMPLATES['confirmation_no'])
                return {
                    'answered': True,
                    'answer': template.format(word=obj.word, other_value=is_values[0]),
                    'confirmed': False,
                    'object': obj.word,
                    'confidence': 0.7,
                }
        
        return self._find_any_property_answer(obj) or self._unknown_answer(obj.word)
    
    def _answer_ability(self, word: str, obj: Any, parsed: Dict) -> Dict:
        """Answer 'Can X do Y?' type questions."""
        if not obj:
            return self._unknown_answer(word or parsed.get('subject', 'that'))
        
        # Look for 'can_do' properties
        can_values = obj.get_property('can_do')
        
        if can_values:
            template = random.choice(self.ANSWER_TEMPLATES['property'])
            answer = template.format(
                word=obj.word,
                relation='can',
                value=can_values[0]
            )
            
            return {
                'answered': True,
                'answer': answer,
                'object': obj.word,
                'property': 'can_do',
                'values': can_values,
                'confidence': 0.85,
            }
        
        return self._find_any_property_answer(obj) or self._unknown_answer(obj.word)
    
    def _answer_manner(self, word: str, obj: Any, parsed: Dict) -> Dict:
        """Answer 'How does X?' type questions."""
        if not obj:
            return self._unknown_answer(word or parsed.get('subject', 'that'))
        
        # Look for 'is' or descriptive properties
        feels_values = obj.get_property('is')
        
        if feels_values:
            template = random.choice(self.ANSWER_TEMPLATES['property'])
            answer = template.format(
                word=obj.word,
                relation='is',
                value=feels_values[0]
            )
            
            return {
                'answered': True,
                'answer': answer,
                'object': obj.word,
                'property': 'is',
                'values': feels_values,
                'confidence': 0.85,
            }
        
        return self._find_any_property_answer(obj) or self._unknown_answer(obj.word)
    
    def _answer_general(self, word: str, obj: Any, parsed: Dict) -> Dict:
        """Answer general questions by finding any relevant property."""
        if not obj:
            return self._unknown_answer(word or parsed.get('subject', 'that'))
        
        return self._find_any_property_answer(obj) or self._unknown_answer(obj.word)
    
    def _find_any_property_answer(self, obj: Any) -> Optional[Dict]:
        """Try to find any property to answer about the object."""
        if not obj:
            return None
        
        all_props = obj.get_all_properties()
        
        for relation, values in all_props.items():
            if values:
                phrase = self.RELATION_PHRASES.get(relation, relation)
                template = random.choice(self.ANSWER_TEMPLATES['property'])
                answer = template.format(
                    word=obj.word,
                    relation=phrase,
                    value=values[0]
                )
                
                return {
                    'answered': True,
                    'answer': answer,
                    'object': obj.word,
                    'property': relation,
                    'values': values,
                    'confidence': 0.7,
                }
        
        return None
    
    def _unknown_answer(self, word: str) -> Dict:
        """Generate an answer when we don't know about the word."""
        template = random.choice(self.ANSWER_TEMPLATES['unknown'])
        return {
            'answered': False,
            'answer': template.format(word=word),
            'object': word,
            'confidence': 0.0,
        }
    
    def generate_follow_up(self, answer_result: Dict, parsed: Dict) -> Optional[str]:
        """
        Generate a follow-up after answering a question.
        
        Could be:
        - A related question back to the user
        - An elaboration connecting to other objects
        - A self-relation ("I like X too!")
        
        Args:
            answer_result: Result from answer_question
            parsed: Original parsed sentence
            
        Returns:
            Follow-up string or None
        """
        obj_word = answer_result.get('object', '')
        
        # If we answered, try to elaborate or ask a follow-up
        if answer_result.get('answered') and answer_result.get('confidence', 0) > 0.5:
            follow_ups = [
                f"Do you have any experience with {obj_word}?",
                f"What else would you like to know about {obj_word}?",
                f"That reminds me, I'd love to learn more about things related to {obj_word}.",
            ]
            return random.choice(follow_ups)
        
        # If we didn't answer, the unknown template already asks a question
        return None
