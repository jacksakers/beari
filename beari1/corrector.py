"""
Corrector Module for Beari AI
Handles corrections when the user tells Beari that information is wrong.
"""

from typing import Dict, List, Optional
from db.db_helpers import DatabaseHelper


class Corrector:
    """
    The Corrector handles learning from mistakes and updating incorrect information.
    
    When a user says Beari is wrong, this module:
    - Identifies what information was incorrect
    - Removes or updates the wrong data
    - Confirms the correction with the user
    """
    
    def __init__(self, db_path: str = "beari.db"):
        """
        Initialize the Corrector with database connection.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db = DatabaseHelper(db_path)
        self.db.connect()
        
        # Track last thing Beari said (for context in corrections)
        self.last_statement = None
        self.last_word = None
        self.last_relations = []
    
    def close(self):
        """Close the database connection."""
        self.db.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def set_context(self, word: str, statement: str, relations: List[Dict] = None):
        """
        Set the context of what Beari just said (for correction tracking).
        
        Args:
            word: The word that was discussed
            statement: What Beari said about it
            relations: Relations that were mentioned
        """
        self.last_word = word
        self.last_statement = statement
        self.last_relations = relations or []
    
    def is_correction(self, user_input: str) -> bool:
        """
        Detect if the user is making a correction.
        
        Args:
            user_input: User's message
        
        Returns:
            True if this appears to be a correction
        """
        user_lower = user_input.lower()
        
        correction_phrases = [
            "that's wrong",
            "that is wrong",
            "you're wrong",
            "you are wrong",
            "incorrect",
            "not true",
            "that's not right",
            "that is not right",
            "no that's",
            "no that is",
            "actually",
            "not a",
            "is not",
            "isn't",
            "doesn't",
            "does not",
            "cannot",
            "can't",
            "can not"
        ]
        
        return any(phrase in user_lower for phrase in correction_phrases)
    
    def process_correction(self, user_input: str) -> Dict[str, any]:
        """
        Process a correction from the user.
        
        Args:
            user_input: The correction message
        
        Returns:
            Dictionary with correction results
        """
        if not self.last_word:
            return {
                'type': 'no_context',
                'message': "I'm not sure what you're correcting. Could you be more specific?"
            }
        
        user_lower = user_input.lower()
        
        # Detect what type of correction this is
        if "not a" in user_lower or "isn't a" in user_lower:
            # Correcting an "is_a" relation
            return self._correct_is_a_relation(user_input)
        
        elif "cannot" in user_lower or "can't" in user_lower or "doesn't" in user_lower:
            # Correcting a "capable_of" relation
            return self._correct_capable_of_relation(user_input)
        
        elif "not related to" in user_lower or "wrong category" in user_lower:
            # Correcting the meaning tag
            return self._correct_meaning_tag(user_input)
        
        elif "not a noun" in user_lower or "not a verb" in user_lower or "not an adjective" in user_lower:
            # Correcting POS tag
            return self._correct_pos_tag(user_input)
        
        else:
            # General correction - try to figure it out
            return self._general_correction(user_input)
    
    def _correct_is_a_relation(self, user_input: str) -> Dict[str, any]:
        """Correct an incorrect 'is_a' relationship."""
        # Find what category they're saying is wrong
        words = user_input.lower().split()
        
        # Look for pattern "not a WORD" or "isn't a WORD"
        wrong_category = None
        for i, word in enumerate(words):
            if word in ["not", "isn't"] and i + 2 < len(words):
                if words[i + 1] in ["a", "an"]:
                    wrong_category = words[i + 2]
                    break
        
        if not wrong_category:
            return {
                'type': 'clarification_needed',
                'message': f"What should I remove from my knowledge about '{self.last_word}'?"
            }
        
        # Try to remove this relation
        word_id = self.db.get_word_id(self.last_word)
        category_id = self.db.get_word_id(wrong_category)
        
        if not word_id:
            return {
                'type': 'error',
                'message': f"I can't find '{self.last_word}' in my memory."
            }
        
        if category_id:
            # Remove the specific relation
            self.db.cursor.execute(
                "DELETE FROM relations WHERE word_a_id = ? AND word_b_id = ? AND relation_type = 'is_a'",
                (word_id, category_id)
            )
            self.db.conn.commit()
            
            return {
                'type': 'corrected',
                'word': self.last_word,
                'removed_relation': f"{self.last_word} is_a {wrong_category}",
                'message': f"Got it! I've removed the incorrect information that '{self.last_word}' is a {wrong_category}."
            }
        
        # If category doesn't exist, remove all is_a relations for this word
        self.db.cursor.execute(
            "DELETE FROM relations WHERE word_a_id = ? AND relation_type = 'is_a'",
            (word_id,)
        )
        self.db.conn.commit()
        
        return {
            'type': 'corrected',
            'word': self.last_word,
            'message': f"I've removed the incorrect 'is_a' information about '{self.last_word}'."
        }
    
    def _correct_capable_of_relation(self, user_input: str) -> Dict[str, any]:
        """Correct an incorrect 'capable_of' relationship."""
        # Remove punctuation before splitting
        import re
        cleaned_input = re.sub(r'[^\w\s]', '', user_input)
        words = cleaned_input.lower().split()
        
        # Look for the action they're saying is wrong
        wrong_action = None
        for i, word in enumerate(words):
            if word in ["cannot", "cant", "doesnt", "does", "can"] and i + 1 < len(words):
                # Next word might be the action
                potential_action = words[i + 1]
                if potential_action not in ["not", "do"]:
                    wrong_action = potential_action
                    break
        
        if not wrong_action:
            return {
                'type': 'clarification_needed',
                'message': f"What action should I remove from '{self.last_word}'?"
            }
        
        # Use the context word (last_word) since user might use plural form
        word_id = self.db.get_word_id(self.last_word)
        action_id = self.db.get_word_id(wrong_action)
        
        if not word_id:
            return {
                'type': 'error',
                'message': f"I can't find '{self.last_word}' in my memory."
            }
        
        if action_id:
            # Check if the relation exists before trying to delete
            self.db.cursor.execute(
                "SELECT COUNT(*) FROM relations WHERE word_a_id = ? AND word_b_id = ? AND relation_type = 'capable_of'",
                (word_id, action_id)
            )
            count = self.db.cursor.fetchone()[0]
            
            if count > 0:
                self.db.cursor.execute(
                    "DELETE FROM relations WHERE word_a_id = ? AND word_b_id = ? AND relation_type = 'capable_of'",
                    (word_id, action_id)
                )
                self.db.conn.commit()
                
                return {
                    'type': 'corrected',
                    'word': self.last_word,
                    'removed_relation': f"{self.last_word} capable_of {wrong_action}",
                    'message': f"Understood! I've removed the incorrect information that '{self.last_word}' can {wrong_action}."
                }
            else:
                return {
                    'type': 'error',
                    'message': f"I don't have a record that '{self.last_word}' can {wrong_action}."
                }
        
        return {
            'type': 'error',
            'message': f"I don't know the action '{wrong_action}'."
        }
    
    def _correct_meaning_tag(self, user_input: str) -> Dict[str, any]:
        """Correct an incorrect meaning tag."""
        # Extract the correct category if mentioned
        words = user_input.lower().split()
        
        # Look for "actually" or "it's" followed by category
        new_category = None
        for i, word in enumerate(words):
            if word in ["actually", "really", "it's", "its"] and i + 1 < len(words):
                new_category = words[i + 1]
                break
        
        word_info = self.db.get_word(self.last_word)
        if not word_info:
            return {
                'type': 'error',
                'message': f"I can't find '{self.last_word}' in my memory."
            }
        
        if new_category:
            # Update to the correct category
            self.db.update_word(self.last_word, meaning_tag=new_category)
            return {
                'type': 'corrected',
                'word': self.last_word,
                'old_tag': word_info['meaning_tag'],
                'new_tag': new_category,
                'message': f"Thanks for the correction! I've updated '{self.last_word}' to be in the '{new_category}' category."
            }
        else:
            # Just remove the wrong tag
            self.db.update_word(self.last_word, meaning_tag=None)
            return {
                'type': 'corrected',
                'word': self.last_word,
                'old_tag': word_info['meaning_tag'],
                'message': f"I've removed the incorrect category from '{self.last_word}'. What category should it be?"
            }
    
    def _correct_pos_tag(self, user_input: str) -> Dict[str, any]:
        """Correct an incorrect part of speech tag."""
        user_lower = user_input.lower()
        
        # Detect what it should be
        new_pos = None
        if "is a noun" in user_lower or "it's a noun" in user_lower:
            new_pos = "Noun"
        elif "is a verb" in user_lower or "it's a verb" in user_lower or "an action" in user_lower:
            new_pos = "Verb"
        elif "is an adjective" in user_lower or "it's an adjective" in user_lower or "describing word" in user_lower:
            new_pos = "Adjective"
        
        word_info = self.db.get_word(self.last_word)
        if not word_info:
            return {
                'type': 'error',
                'message': f"I can't find '{self.last_word}' in my memory."
            }
        
        if new_pos:
            self.db.update_word(self.last_word, pos_tag=new_pos)
            return {
                'type': 'corrected',
                'word': self.last_word,
                'old_pos': word_info['pos_tag'],
                'new_pos': new_pos,
                'message': f"Thank you! I've corrected '{self.last_word}' to be a {new_pos}."
            }
        else:
            return {
                'type': 'clarification_needed',
                'message': f"What part of speech is '{self.last_word}'? (Noun, Verb, or Adjective)"
            }
    
    def _general_correction(self, user_input: str) -> Dict[str, any]:
        """Handle general corrections where the type isn't clear."""
        return {
            'type': 'clarification_needed',
            'message': f"I understand you're correcting something about '{self.last_word}'. Could you be more specific? For example:\n" +
                      f"- 'That's not a [category]' to correct its type\n" +
                      f"- '{self.last_word} cannot [action]' to correct what it can do\n" +
                      f"- 'It's not related to [category]' to correct its meaning"
        }
    
    def delete_word(self, word: str) -> Dict[str, any]:
        """
        Completely remove a word and all its relations.
        
        Args:
            word: Word to delete
        
        Returns:
            Dictionary with deletion results
        """
        word_id = self.db.get_word_id(word)
        
        if not word_id:
            return {
                'type': 'error',
                'message': f"I don't have '{word}' in my vocabulary."
            }
        
        # Delete all relations involving this word
        self.db.cursor.execute(
            "DELETE FROM relations WHERE word_a_id = ? OR word_b_id = ?",
            (word_id, word_id)
        )
        
        # Delete the word itself
        self.db.cursor.execute(
            "DELETE FROM vocabulary WHERE id = ?",
            (word_id,)
        )
        
        self.db.conn.commit()
        
        return {
            'type': 'deleted',
            'word': word,
            'message': f"I've completely forgotten about '{word}'."
        }
    
    def get_correction_suggestions(self, word: str) -> List[str]:
        """
        Suggest what might need correction about a word.
        
        Args:
            word: Word to analyze
        
        Returns:
            List of suggestion strings
        """
        word_info = self.db.get_word(word)
        
        if not word_info:
            return [f"'{word}' is not in my vocabulary."]
        
        suggestions = []
        suggestions.append(f"Part of Speech: {word_info['pos_tag'] or 'Not set'}")
        suggestions.append(f"Meaning Category: {word_info['meaning_tag'] or 'Not set'}")
        
        relations = self.db.get_relations(word)
        if relations:
            for rel in relations:
                suggestions.append(f"Relation: {word} {rel['relation_type']} {rel['target_word']}")
        
        return suggestions


def demo_corrector():
    """Demo function showing the Corrector in action."""
    print("=== Beari Corrector Mode Demo ===")
    print("Testing correction capabilities\n")
    
    with Corrector() as corrector:
        # Simulate a conversation where Beari gets something wrong
        print("Scenario: Beari says something incorrect\n")
        
        # Set context (what Beari just said)
        corrector.set_context(
            word="python",
            statement="Python is an animal",
            relations=[{'relation_type': 'is_a', 'target_word': 'animal'}]
        )
        
        print("Beari: 'Python is an animal.'\n")
        
        # User corrects it
        print("You: That's wrong! Python is not an animal.\n")
        
        result = corrector.process_correction("That's wrong! Python is not an animal.")
        print(f"Beari: {result['message']}\n")
        
        print("-" * 60)
        
        # Another correction scenario
        corrector.set_context(
            word="robot",
            statement="Robot can fly",
            relations=[{'relation_type': 'capable_of', 'target_word': 'fly'}]
        )
        
        print("\nBeari: 'Robot can fly.'\n")
        print("You: No, robots cannot fly.\n")
        
        result = corrector.process_correction("No, robots cannot fly.")
        print(f"Beari: {result['message']}\n")


if __name__ == "__main__":
    demo_corrector()
