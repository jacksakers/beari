"""
Listener Module for Beari AI
The Listener mode: continuously learns from user input and asks questions about unknowns.
"""

from typing import Dict, List
from db.db_helpers import DatabaseHelper
from parser import Parser
from question_generator import QuestionGenerator


class Listener:
    """
    The Listener handles continuous learning from user input.
    
    This is Mode A from the design doc: parses input, detects unknown words,
    asks questions about them, and updates the database with new knowledge.
    """
    
    def __init__(self, db_path: str = "beari.db"):
        """
        Initialize the Listener with database connection.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db = DatabaseHelper(db_path)
        self.db.connect()
        self.parser = Parser(self.db)
        self.question_gen = QuestionGenerator()
        
        # State tracking for learning mode
        self.learning_mode = False
        self.pending_word = None
        self.pending_context = None
    
    def close(self):
        """Close the database connection."""
        self.db.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def process_input(self, user_input: str) -> Dict[str, any]:
        """
        Main processing pipeline for user input.
        
        If we're in learning mode (waiting for an answer about an unknown word),
        process the answer. Otherwise, parse the input and check for unknowns.
        
        Args:
            user_input: The user's input string
        
        Returns:
            Dictionary with response information and next actions
        """
        # If we're waiting for an answer about a word
        if self.learning_mode and self.pending_word:
            return self._process_learning_response(user_input)
        
        # Otherwise, parse the new input
        return self._process_new_input(user_input)
    
    def _process_new_input(self, user_input: str) -> Dict[str, any]:
        """
        Process new user input: parse, identify unknowns, ask questions.
        
        Args:
            user_input: User's input sentence
        
        Returns:
            Response dictionary
        """
        # Parse the sentence
        parse_result = self.parser.parse_sentence(user_input)
        
        response = {
            'type': 'parse',
            'parsed': parse_result,
            'question': None,
            'learned': False,
            'message': None
        }
        
        # If there are unknown words, ask about the first meaningful one
        if parse_result['has_unknowns']:
            # Skip common stop words and ask about more meaningful words first
            stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 
                         'to', 'for', 'of', 'and', 'or', 'but', 'not'}
            
            # Find first non-stop-word unknown
            unknown_word = None
            for word in parse_result['unknown_words']:
                if word not in stop_words:
                    unknown_word = word
                    break
            
            # If all unknowns are stop words, just use the first one
            if not unknown_word:
                unknown_word = parse_result['unknown_words'][0]
            
            # Get context for better questions
            prev_word, next_word = self.parser.get_context_words(
                parse_result['tokens'], 
                unknown_word
            )
            context = {'prev_word': prev_word, 'next_word': next_word}
            
            # Generate question
            question = self.question_gen.generate_question(unknown_word, context)
            
            # Enter learning mode
            self.learning_mode = True
            self.pending_word = unknown_word
            self.pending_context = context
            
            response['question'] = question
            response['type'] = 'question'
        else:
            # All words are known, update relations
            self._update_relations(parse_result['tokens'])
            response['message'] = "I understood that!"
            response['type'] = 'understood'
        
        return response
    
    def _process_learning_response(self, user_response: str) -> Dict[str, any]:
        """
        Process the user's answer to a question about an unknown word.
        
        Args:
            user_response: User's explanation of the unknown word
        
        Returns:
            Response dictionary
        """
        # Parse the user's response to extract POS and meaning tags
        parsed_response = self.question_gen.parse_user_response(user_response)
        
        pos_tag = parsed_response.get('pos_tag')
        meaning_tag = parsed_response.get('meaning_tag')
        
        # If we couldn't parse structured info, use the raw response as meaning
        if not pos_tag and not meaning_tag:
            meaning_tag = parsed_response.get('raw_response', 'general')
        
        # Add the word to the database
        word_id = self.db.add_word(
            self.pending_word,
            pos_tag=pos_tag,
            meaning_tag=meaning_tag
        )
        
        # Generate confirmation
        confirmation = self.question_gen.generate_confirmation(
            self.pending_word,
            pos_tag,
            meaning_tag
        )
        
        # Exit learning mode
        self.learning_mode = False
        stored_word = self.pending_word
        self.pending_word = None
        self.pending_context = None
        
        return {
            'type': 'learned',
            'word': stored_word,
            'word_id': word_id,
            'pos_tag': pos_tag,
            'meaning_tag': meaning_tag,
            'message': confirmation,
            'learned': True
        }
    
    def _update_relations(self, tokens: List[str]) -> None:
        """
        Update word-to-word relations based on sequential appearance.
        
        This creates "follows" relationships between consecutive words,
        which helps with sentence generation later.
        
        Args:
            tokens: List of tokens from a sentence
        """
        for i in range(len(tokens) - 1):
            current_word = tokens[i]
            next_word = tokens[i + 1]
            
            # Only create relations between known words
            if self.db.word_exists(current_word) and self.db.word_exists(next_word):
                self.db.add_relation(current_word, "follows", next_word)
    
    def learn_from_sentence(self, sentence: str) -> Dict[str, any]:
        """
        Complete learning cycle for a single sentence.
        
        This is a convenience method that processes input and handles
        the full conversation flow automatically.
        
        Args:
            sentence: Input sentence to learn from
        
        Returns:
            Final result after learning is complete
        """
        result = self.process_input(sentence)
        
        # If it asked a question, we need another input
        # This method just returns the state
        return result
    
    def get_vocabulary_stats(self) -> Dict[str, any]:
        """
        Get current vocabulary statistics.
        
        Returns:
            Dictionary with vocabulary size and other stats
        """
        return self.db.get_stats()
    
    def is_waiting_for_answer(self) -> bool:
        """
        Check if the listener is waiting for a user response.
        
        Returns:
            True if in learning mode, False otherwise
        """
        return self.learning_mode


def interactive_listener_demo():
    """
    Demo function showing how to use the Listener in an interactive session.
    """
    print("=== Beari Listener Mode Demo ===")
    print("Type 'quit' to exit, 'stats' to see vocabulary statistics\n")
    
    with Listener() as listener:
        while True:
            # Get user input
            if listener.is_waiting_for_answer():
                user_input = input("Answer: ")
            else:
                user_input = input("You: ")
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'stats':
                stats = listener.get_vocabulary_stats()
                print(f"\nVocabulary Statistics:")
                print(f"  Total words: {stats['vocabulary_size']}")
                print(f"  Total relations: {stats['total_relations']}")
                print(f"  Relation types: {stats['relation_types']}\n")
                continue
            
            # Process input
            result = listener.process_input(user_input)
            
            # Display response
            if result['type'] == 'question':
                print(f"Beari: {result['question']}")
            elif result['type'] == 'learned':
                print(f"Beari: {result['message']}")
            elif result['type'] == 'understood':
                print(f"Beari: {result['message']}")
            else:
                print("Beari: [Processing...]")


if __name__ == "__main__":
    interactive_listener_demo()
