"""
Orator Module for Beari AI
The Orator (Mode C): Generates sentences using strict grammar templates and answers questions.
"""

import random
from typing import Dict, List, Optional
from db.db_helpers import DatabaseHelper


class Orator:
    """
    The Orator handles sentence generation and question answering.
    
    This is Mode C from the design doc: uses templates to construct grammatically
    correct sentences based on Subject-Predicate-Object structure.
    """
    
    def __init__(self, db_path: str = "beari.db"):
        """
        Initialize the Orator with database connection.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db = DatabaseHelper(db_path)
        self.db.connect()
        
        # Sentence templates for generation
        self.templates = [
            "{subject} {verb} {object}.",
            "{subject} {verb}.",
            "The {noun} {verb} the {object}.",
            "{adjective} {noun} {verb}.",
            "{subject} is {adjective}.",
        ]
    
    def close(self):
        """Close the database connection."""
        self.db.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def generate_sentence(self, template: Optional[str] = None) -> str:
        """
        Generate a sentence using a template and database words.
        
        Args:
            template: Optional specific template to use
        
        Returns:
            Generated sentence or error message
        """
        if template is None:
            template = random.choice(self.templates)
        
        # Get words from database
        nouns = self.db.get_all_words(pos_tag="Noun")
        verbs = self.db.get_all_words(pos_tag="Verb")
        adjectives = self.db.get_all_words(pos_tag="Adjective")
        
        if not nouns or not verbs:
            return "I don't have enough vocabulary to generate sentences yet."
        
        # Fill in template
        parts = {}
        parts['subject'] = self._pick_subject(nouns)
        parts['verb'] = self._pick_verb_for_subject(parts['subject'], verbs)
        parts['object'] = self._pick_object_for_verb(parts['verb'], nouns)
        parts['noun'] = random.choice(nouns)['word'] if nouns else "thing"
        parts['adjective'] = random.choice(adjectives)['word'] if adjectives else "nice"
        
        try:
            return template.format(**parts)
        except KeyError:
            # If template has placeholders we don't have, use simple template
            return f"{parts['subject']} {parts['verb']}."
    
    def _pick_subject(self, nouns: List[Dict]) -> str:
        """Pick a subject noun, preferring those with relations."""
        if not nouns:
            return "something"
        
        # Try to pick a noun that has outgoing relations
        for _ in range(3):  # Try 3 times
            noun = random.choice(nouns)['word']
            relations = self.db.get_relations(noun)
            if relations:
                return noun
        
        # Fallback to any noun
        return random.choice(nouns)['word']
    
    def _pick_verb_for_subject(self, subject: str, verbs: List[Dict]) -> str:
        """Pick a verb, preferring those related to the subject."""
        if not verbs:
            return "is"
        
        # Check if subject has "capable_of" relations
        relations = self.db.get_relations(subject, relation_type="capable_of")
        if relations:
            # See if any of these are verbs
            for rel in relations:
                word_info = self.db.get_word(rel['target_word'])
                if word_info and word_info['pos_tag'] == "Verb":
                    return rel['target_word']
        
        # Fallback to random verb
        return random.choice(verbs)['word']
    
    def _pick_object_for_verb(self, verb: str, nouns: List[Dict]) -> str:
        """Pick an object noun, preferring those related to the verb."""
        if not nouns:
            return "something"
        
        # Check if verb has relations to nouns
        relations = self.db.get_relations(verb)
        if relations:
            for rel in relations:
                word_info = self.db.get_word(rel['target_word'])
                if word_info and word_info['pos_tag'] == "Noun":
                    return rel['target_word']
        
        # Fallback to random noun
        return random.choice(nouns)['word']
    
    def answer_question(self, question: str) -> Dict[str, any]:
        """
        Answer a question about a word based on database knowledge.
        
        Args:
            question: User's question
        
        Returns:
            Dictionary with answer information
        """
        question_lower = question.lower().strip()
        
        # Parse the question to find what word they're asking about
        question_words = question_lower.split()
        
        # Common question patterns
        if "what is" in question_lower or "what's" in question_lower:
            # Extract the word after "what is"
            word = self._extract_subject_from_question(question_lower, "what is")
            if not word:
                word = self._extract_subject_from_question(question_lower, "what's")
            return self._answer_what_is(word)
        
        elif "what does" in question_lower:
            word = self._extract_subject_from_question(question_lower, "what does")
            return self._answer_what_does(word)
        
        elif "is" in question_lower and "?" in question:
            # Pattern: "Is X a Y?"
            return self._answer_is_question(question_lower)
        
        elif "can" in question_lower and "?" in question:
            # Pattern: "Can X do Y?"
            return self._answer_can_question(question_lower)
        
        elif "tell me about" in question_lower:
            word = self._extract_subject_from_question(question_lower, "tell me about")
            return self._tell_about_word(word)
        
        else:
            return {
                'type': 'unknown_question',
                'message': "I'm not sure what you're asking. Try asking 'What is X?' or 'Tell me about X.'"
            }
    
    def _extract_subject_from_question(self, question: str, pattern: str) -> Optional[str]:
        """Extract the main subject word from a question."""
        if pattern not in question:
            return None
        
        # Get text after pattern
        after_pattern = question.split(pattern, 1)[1].strip()
        
        # Remove common words and punctuation
        after_pattern = after_pattern.replace('?', '').replace('.', '').strip()
        words = after_pattern.split()
        
        # Remove articles and common words
        stop_words = {'a', 'an', 'the', 'this', 'that', 'these', 'those'}
        words = [w for w in words if w not in stop_words]
        
        if words:
            # Return the first significant word
            return words[0]
        
        return None
    
    def _answer_what_is(self, word: Optional[str]) -> Dict[str, any]:
        """Answer 'What is X?' questions."""
        if not word:
            return {
                'type': 'clarification_needed',
                'message': "What do you want to know about?"
            }
        
        word_info = self.db.get_word(word)
        
        if not word_info:
            return {
                'type': 'unknown',
                'word': word,
                'message': f"I don't know anything about '{word}' yet."
            }
        
        # Build answer from database knowledge
        answer_parts = [f"'{word.capitalize()}'"]
        
        # Add POS information
        if word_info['pos_tag']:
            pos_description = {
                'Noun': 'is a noun',
                'Verb': 'is a verb (an action)',
                'Adjective': 'is an adjective (a describing word)'
            }
            answer_parts.append(pos_description.get(word_info['pos_tag'], f"is a {word_info['pos_tag']}"))
        
        # Add meaning tag
        if word_info['meaning_tag']:
            answer_parts.append(f"related to {word_info['meaning_tag']}")
        
        # Add relations
        relations = self.db.get_relations(word)
        if relations:
            relation_info = []
            for rel in relations[:3]:  # Limit to 3 relations
                if rel['relation_type'] == 'is_a':
                    relation_info.append(f"is a {rel['target_word']}")
                elif rel['relation_type'] == 'capable_of':
                    relation_info.append(f"can {rel['target_word']}")
                elif rel['relation_type'] == 'part_of':
                    relation_info.append(f"is part of {rel['target_word']}")
            
            if relation_info:
                answer_parts.extend(relation_info)
        
        message = ". ".join(answer_parts) + "."
        
        return {
            'type': 'answer',
            'word': word,
            'word_info': word_info,
            'relations': relations,
            'message': message
        }
    
    def _answer_what_does(self, word: Optional[str]) -> Dict[str, any]:
        """Answer 'What does X do?' questions."""
        if not word:
            return {
                'type': 'clarification_needed',
                'message': "What word are you asking about?"
            }
        
        word_info = self.db.get_word(word)
        
        if not word_info:
            return {
                'type': 'unknown',
                'word': word,
                'message': f"I don't know anything about '{word}' yet."
            }
        
        # Look for capable_of relations
        relations = self.db.get_relations(word, relation_type="capable_of")
        
        if not relations:
            return {
                'type': 'answer',
                'word': word,
                'message': f"I know '{word}' but I don't know what it does or can do."
            }
        
        actions = [rel['target_word'] for rel in relations]
        action_list = ", ".join(actions)
        
        return {
            'type': 'answer',
            'word': word,
            'relations': relations,
            'message': f"'{word.capitalize()}' can {action_list}."
        }
    
    def _answer_is_question(self, question: str) -> Dict[str, any]:
        """Answer 'Is X a Y?' questions."""
        # Parse pattern: "is WORD a CATEGORY"
        words = question.replace('?', '').split()
        
        if 'is' not in words:
            return {'type': 'unknown_question', 'message': "I'm not sure what you're asking."}
        
        is_index = words.index('is')
        if is_index + 1 >= len(words):
            return {'type': 'unknown_question', 'message': "I'm not sure what you're asking."}
        
        # Skip articles before subject
        subject_index = is_index + 1
        while subject_index < len(words) and words[subject_index] in ['a', 'an', 'the']:
            subject_index += 1
        
        if subject_index >= len(words):
            return {'type': 'unknown_question', 'message': "I'm not sure what you're asking."}
        
        subject = words[subject_index]
        
        # Find category after subject, skipping articles
        category_index = subject_index + 1
        while category_index < len(words) and words[category_index] in ['a', 'an', 'the']:
            category_index += 1
        
        if category_index >= len(words):
            return {'type': 'unknown_question', 'message': "I'm not sure what you're asking."}
        
        category = words[category_index]
        
        word_info = self.db.get_word(subject)
        
        if not word_info:
            return {
                'type': 'unknown',
                'word': subject,
                'message': f"I don't know anything about '{subject}' yet."
            }
        
        # Check is_a relations
        relations = self.db.get_relations(subject, relation_type="is_a")
        
        for rel in relations:
            if category in rel['target_word'] or rel['target_word'] in category:
                return {
                    'type': 'answer',
                    'word': subject,
                    'message': f"Yes, '{subject}' is a {rel['target_word']}."
                }
        
        # Check meaning tag
        if word_info['meaning_tag'] and category in word_info['meaning_tag']:
            return {
                'type': 'answer',
                'word': subject,
                'message': f"Yes, '{subject}' is related to {word_info['meaning_tag']}."
            }
        
        return {
            'type': 'answer',
            'word': subject,
            'message': f"I'm not sure if '{subject}' is a {category}. I don't have that information."
        }
    
    def _answer_can_question(self, question: str) -> Dict[str, any]:
        """Answer 'Can X do Y?' questions."""
        words = question.replace('?', '').split()
        
        if 'can' not in words:
            return {'type': 'unknown_question', 'message': "I'm not sure what you're asking."}
        
        can_index = words.index('can')
        if can_index + 1 >= len(words):
            return {'type': 'unknown_question', 'message': "I'm not sure what you're asking."}
        
        # Skip articles (a, an, the)
        subject_index = can_index + 1
        while subject_index < len(words) and words[subject_index] in ['a', 'an', 'the']:
            subject_index += 1
        
        if subject_index >= len(words):
            return {'type': 'unknown_question', 'message': "I'm not sure what you're asking."}
        
        subject = words[subject_index]
        action = words[subject_index + 1] if subject_index + 1 < len(words) else None
        
        word_info = self.db.get_word(subject)
        
        if not word_info:
            return {
                'type': 'unknown',
                'word': subject,
                'message': f"I don't know anything about '{subject}' yet."
            }
        
        if not action:
            # General "what can X do?"
            relations = self.db.get_relations(subject, relation_type="capable_of")
            if relations:
                actions = [rel['target_word'] for rel in relations]
                action_list = ", ".join(actions)
                return {
                    'type': 'answer',
                    'word': subject,
                    'message': f"'{subject.capitalize()}' can {action_list}."
                }
            else:
                return {
                    'type': 'answer',
                    'word': subject,
                    'message': f"I don't know what '{subject}' can do."
                }
        
        # Check if subject can do specific action
        relations = self.db.get_relations(subject, relation_type="capable_of")
        
        for rel in relations:
            if action in rel['target_word'] or rel['target_word'] in action:
                return {
                    'type': 'answer',
                    'word': subject,
                    'message': f"Yes, '{subject}' can {rel['target_word']}."
                }
        
        return {
            'type': 'answer',
            'word': subject,
            'message': f"I don't think '{subject}' can {action}, based on what I know."
        }
    
    def _tell_about_word(self, word: Optional[str]) -> Dict[str, any]:
        """Provide comprehensive information about a word."""
        if not word:
            return {
                'type': 'clarification_needed',
                'message': "What word do you want me to tell you about?"
            }
        
        word_info = self.db.get_word(word)
        
        if not word_info:
            return {
                'type': 'unknown',
                'word': word,
                'message': f"I don't know anything about '{word}' yet. Would you like to teach me?"
            }
        
        # Build comprehensive answer
        info_parts = [f"Here's what I know about '{word}':"]
        
        # POS and meaning
        if word_info['pos_tag']:
            info_parts.append(f"It's a {word_info['pos_tag']}")
        
        if word_info['meaning_tag']:
            info_parts.append(f"Category: {word_info['meaning_tag']}")
        
        # Relations
        relations = self.db.get_relations(word)
        if relations:
            relation_sentences = []
            for rel in relations:
                if rel['relation_type'] == 'is_a':
                    relation_sentences.append(f"It is a {rel['target_word']}")
                elif rel['relation_type'] == 'capable_of':
                    relation_sentences.append(f"It can {rel['target_word']}")
                elif rel['relation_type'] == 'part_of':
                    relation_sentences.append(f"It is part of {rel['target_word']}")
            
            if relation_sentences:
                info_parts.extend(relation_sentences)
        
        # Reverse relations (what connects to this word)
        reverse_rels = self.db.get_reverse_relations(word)
        if reverse_rels:
            reverse_sentences = []
            for rel in reverse_rels[:3]:  # Limit to 3
                if rel['relation_type'] == 'is_a':
                    reverse_sentences.append(f"{rel['source_word']} is a type of {word}")
            
            if reverse_sentences:
                info_parts.extend(reverse_sentences)
        
        message = ". ".join(info_parts) + "."
        
        return {
            'type': 'answer',
            'word': word,
            'word_info': word_info,
            'relations': relations,
            'reverse_relations': reverse_rels,
            'message': message
        }


def demo_orator():
    """Demo function showing the Orator in action."""
    print("=== Beari Orator Mode Demo ===")
    print("Generating sentences and answering questions\n")
    
    with Orator() as orator:
        # Generate a few sentences
        print("Generated Sentences:")
        print("-" * 60)
        for i in range(5):
            sentence = orator.generate_sentence()
            print(f"{i+1}. {sentence}")
        
        print("\n" + "=" * 60)
        print("\nAnswering Questions:")
        print("-" * 60)
        
        # Answer some questions
        questions = [
            "What is dog?",
            "What does robot do?",
            "Tell me about python",
            "Can a dog run?",
            "Is cat an animal?"
        ]
        
        for question in questions:
            print(f"\nQ: {question}")
            answer = orator.answer_question(question)
            print(f"A: {answer['message']}")


if __name__ == "__main__":
    demo_orator()
