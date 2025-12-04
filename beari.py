"""
Beari AI - Main Conversation Interface
Integrates Listener (learning), Orator (answering), and Corrector (fixing mistakes).
"""

from listener import Listener
from orator import Orator
from corrector import Corrector
from db.db_helpers import DatabaseHelper


class BeariAI:
    """
    Main Beari AI conversational interface.
    
    Combines three modes:
    - Listener: Learns from user input, asks about unknowns
    - Orator: Answers questions based on knowledge
    - Corrector: Fixes mistakes when user corrects Beari
    """
    
    def __init__(self, db_path: str = "beari.db"):
        """
        Initialize Beari with all subsystems.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self.listener = Listener(db_path)
        self.orator = Orator(db_path)
        self.corrector = Corrector(db_path)
        
        # Track conversation state
        self.waiting_for_learning_response = False
    
    def close(self):
        """Close all subsystem connections."""
        self.listener.close()
        self.orator.close()
        self.corrector.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def process_input(self, user_input: str) -> dict:
        """
        Main processing pipeline for user input.
        
        Routes input to appropriate subsystem:
        1. Check if it's a correction
        2. Check if it's a question
        3. Otherwise, learn from it (Listener mode)
        
        Args:
            user_input: User's message
        
        Returns:
            Dictionary with response information
        """
        user_input = user_input.strip()
        
        if not user_input:
            return {
                'type': 'empty',
                'message': "..."
            }
        
        # Check for quit commands
        if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
            return {
                'type': 'quit',
                'message': "Goodbye! Thanks for chatting with me."
            }
        
        # Check for special commands
        if user_input.lower() == 'stats':
            return self._show_stats()
        
        if user_input.lower() == 'help':
            return self._show_help()
        
        if user_input.lower().startswith('generate'):
            return self._generate_sentence()
        
        if user_input.lower().startswith('forget '):
            word = user_input[7:].strip()
            return self.corrector.delete_word(word)
        
        # Priority 1: If waiting for learning response from Listener
        if self.listener.is_waiting_for_answer():
            result = self.listener.process_input(user_input)
            return result
        
        # Priority 2: Check if user is correcting Beari
        if self.corrector.is_correction(user_input):
            result = self.corrector.process_correction(user_input)
            return result
        
        # Priority 3: Check if user is asking a question
        if self._is_question(user_input):
            result = self.orator.answer_question(user_input)
            
            # Set context for potential corrections
            if result['type'] == 'answer' and 'word' in result:
                self.corrector.set_context(
                    word=result.get('word'),
                    statement=result.get('message'),
                    relations=result.get('relations', [])
                )
            
            return result
        
        # Priority 4: Learn from the input (Listener mode)
        result = self.listener.process_input(user_input)
        return result
    
    def _is_question(self, text: str) -> bool:
        """
        Detect if the input is a question.
        
        Args:
            text: User's input
        
        Returns:
            True if it appears to be a question
        """
        text_lower = text.lower()
        
        # Check for question mark
        if '?' in text:
            return True
        
        # Check for question words at the start
        question_starters = [
            'what', 'who', 'where', 'when', 'why', 'how',
            'is', 'are', 'can', 'could', 'would', 'should',
            'do', 'does', 'did', 'will', 'tell me'
        ]
        
        first_word = text_lower.split()[0] if text_lower.split() else ""
        
        return first_word in question_starters
    
    def _show_stats(self) -> dict:
        """Show vocabulary statistics."""
        stats = self.listener.get_vocabulary_stats()
        
        message = (
            f"\n📊 Beari's Knowledge Statistics:\n"
            f"   Vocabulary: {stats['vocabulary_size']} words\n"
            f"   Relations: {stats['total_relations']} connections\n"
            f"   Relation types: {', '.join(stats['relation_types'])}"
        )
        
        return {
            'type': 'stats',
            'stats': stats,
            'message': message
        }
    
    def _show_help(self) -> dict:
        """Show help information."""
        message = (
            "\n📚 Beari AI Help:\n\n"
            "How to use Beari:\n"
            "  • Just chat naturally - I'll learn from what you say\n"
            "  • Ask me questions: 'What is X?' or 'Can X do Y?'\n"
            "  • Correct me: 'That's wrong!' or 'X is not a Y'\n"
            "  • Tell me about things I don't know\n\n"
            "Special commands:\n"
            "  stats     - Show my vocabulary size\n"
            "  generate  - Generate a random sentence\n"
            "  forget X  - Remove word X from my memory\n"
            "  help      - Show this help message\n"
            "  quit      - Exit the conversation\n"
        )
        
        return {
            'type': 'help',
            'message': message
        }
    
    def _generate_sentence(self) -> dict:
        """Generate a random sentence."""
        sentence = self.orator.generate_sentence()
        
        return {
            'type': 'generated',
            'message': sentence
        }
    
    def chat_loop(self):
        """Run an interactive chat loop with the user."""
        print("="*70)
        print("🐻 Welcome to Beari AI - Your Learning Companion!")
        print("="*70)
        print("\nI learn from our conversations and can answer your questions.")
        print("Type 'help' for commands, or just start chatting!")
        print("Type 'quit' to exit.\n")
        
        # Show initial stats
        stats = self.listener.get_vocabulary_stats()
        print(f"Current vocabulary: {stats['vocabulary_size']} words\n")
        print("="*70)
        
        while True:
            try:
                user_input = input("\n🧑 You: ").strip()
                
                if not user_input:
                    continue
                
                # Process input
                result = self.process_input(user_input)
                
                # Handle quit
                if result['type'] == 'quit':
                    print(f"\n🐻 Beari: {result['message']}")
                    break
                
                # Display response - check both 'message' and 'question' fields
                if result.get('question'):
                    print(f"\n🐻 Beari: {result['question']}")
                elif result.get('message'):
                    print(f"\n🐻 Beari: {result['message']}")
                
            except KeyboardInterrupt:
                print("\n\n🐻 Beari: Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Let's keep chatting! Try again.")


def main():
    """Main entry point for Beari AI."""
    
    # Initialize database if needed
    db = DatabaseHelper()
    db.connect()
    
    # Check if database is empty
    stats = db.get_stats()
    
    if stats['vocabulary_size'] == 0:
        print("\n⚠️  Your database is empty!")
        print("Would you like to initialize it with sample vocabulary? (y/n)")
        
        choice = input("> ").strip().lower()
        
        if choice == 'y':
            print("\nInitializing database...")
            from db.init_db import main as init_main
            db.close()
            init_main()
            print("\n✓ Database initialized!\n")
        else:
            print("\nOkay! I'll learn vocabulary as we chat.\n")
    
    db.close()
    
    # Start the chat
    with BeariAI() as beari:
        beari.chat_loop()


if __name__ == "__main__":
    main()
