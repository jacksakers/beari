"""
Beari2 - Object-Oriented Learning AI
Main conversation interface with Living Objects.
"""

import sys
import os
from typing import Dict, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.living_object import LivingObject
from core.object_manager import ObjectManager
from core.gap_analysis import find_learning_opportunity, suggest_next_question_field
from core.question_generator import generate_question, generate_confirmation
from utils.input_parser import InputParser
from db import initialize_database, get_object_count, DatabaseConnection


class Beari2:
    """
    Main Beari2 AI interface with Object-Oriented Learning.
    
    Features:
    - Parses input to extract subjects, predicates, objects
    - Creates and updates Living Objects dynamically
    - Identifies knowledge gaps and asks targeted questions
    - Confirms learning through natural responses
    """
    
    def __init__(self, db_path: str = "beari2.db"):
        """
        Initialize Beari2.
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        self.manager = ObjectManager(db_path)
        self.parser = InputParser()
        
        # Learning state
        self.waiting_for_answer = False
        self.current_question_object = None
        self.current_question_field = None
    
    def process_input(self, user_input: str) -> Dict:
        """
        Main input processing pipeline.
        
        Args:
            user_input: User's message
        
        Returns:
            Response dictionary
        """
        user_input = user_input.strip()
        
        if not user_input:
            return {'type': 'empty', 'message': '...'}
        
        # Check for quit
        if user_input.lower() in ['quit', 'exit', 'bye']:
            return {'type': 'quit', 'message': 'Goodbye! Keep learning! 🐻'}
        
        # Check for special commands
        if user_input.lower() == 'stats':
            return self._show_stats()
        
        if user_input.lower() == 'help':
            return self._show_help()
        
        # If waiting for answer to a question
        if self.waiting_for_answer and self.current_question_object:
            return self._process_learning_answer(user_input)
        
        # Otherwise, parse and learn from the input
        return self._process_new_sentence(user_input)
    
    def _process_new_sentence(self, sentence: str) -> Dict:
        """
        Process a new sentence: parse, create objects, update properties.
        
        Args:
            sentence: User's sentence
        
        Returns:
            Response dictionary
        """
        # Parse the sentence
        parsed = self.parser.parse_sentence(sentence)
        
        # Extract relations
        relations = self.parser.extract_relations(parsed)
        
        # Update or create objects for each component
        updated_objects = []
        
        if parsed['subject']:
            obj = self.manager.create_or_get(parsed['subject'], 'Noun')
            updated_objects.append(obj)
        
        if parsed['object']:
            # Infer POS from context
            pos = 'Adjective' if parsed['verb_relation'] == 'is' else 'Noun'
            obj = self.manager.create_or_get(parsed['object'], pos)
            updated_objects.append(obj)
        
        if parsed['verb'] and parsed['verb'] not in self.parser.relation_verbs:
            obj = self.manager.create_or_get(parsed['verb'], 'Verb')
            updated_objects.append(obj)
        
        # Apply relations
        for relation in relations:
            source_obj = self.manager.create_or_get(relation['source'], 'Noun')
            source_obj.add_property(relation['relation'], relation['target'])
            self.manager.save_object(source_obj)
            
            # Update the object in updated_objects if it exists there
            for i, obj in enumerate(updated_objects):
                if obj.word == source_obj.word and obj.pos == source_obj.pos:
                    updated_objects[i] = source_obj
                    break
            else:
                # If not in list, add it
                updated_objects.append(source_obj)
        
        # Save all updated objects
        for obj in updated_objects:
            self.manager.save_object(obj)
        
        # Generate confirmation
        confirmation = self._generate_confirmation(parsed, relations)
        
        # Now enter inquiry mode - find a gap to ask about
        question_result = self._enter_inquiry_mode(updated_objects)
        
        response = {
            'type': 'learned',
            'parsed': parsed,
            'relations': relations,
            'message': confirmation,
            'objects_updated': len(updated_objects)
        }
        
        # Add question if found
        if question_result:
            response['question'] = question_result['question']
            response['type'] = 'learned_and_asking'
        
        return response
    
    def _generate_confirmation(self, parsed: Dict, relations: list) -> str:
        """
        Generate a natural confirmation of what was learned.
        
        Args:
            parsed: Parsed sentence
            relations: Extracted relations
        
        Returns:
            Confirmation string
        """
        if not relations:
            return "I'm listening and learning from what you say."
        
        # Generate confirmation based on first relation
        rel = relations[0]
        
        if rel['relation'] == 'is':
            return f"I see, {rel['source']} is {rel['target']}."
        elif rel['relation'] == 'can_have':
            return f"Got it, {rel['source']} can have {rel['target']}."
        elif rel['relation'] == 'can_do':
            return f"I understand, {rel['source']} can {rel['target']}."
        elif rel['relation'] == 'feels_like':
            return f"I see, {rel['source']} feels like {rel['target']}."
        else:
            return f"I learned about {rel['source']}."
    
    def _enter_inquiry_mode(self, objects: list) -> Optional[Dict]:
        """
        Scan objects for gaps and generate a question.
        
        Args:
            objects: List of LivingObjects that were just updated
        
        Returns:
            Question dictionary or None
        """
        for obj in objects:
            # Find a gap
            field = suggest_next_question_field(obj)
            
            if field:
                # Generate question
                question = generate_question(obj.word, field, obj.pos)
                
                # Set state
                self.waiting_for_answer = True
                self.current_question_object = obj
                self.current_question_field = field
                
                return {
                    'question': question,
                    'object': obj.word,
                    'field': field
                }
        
        return None
    
    def _process_learning_answer(self, answer: str) -> Dict:
        """
        Process user's answer to a learning question.
        
        Args:
            answer: User's answer
        
        Returns:
            Response dictionary
        """
        if not self.current_question_object or not self.current_question_field:
            self.waiting_for_answer = False
            return {'type': 'error', 'message': 'Internal error: no question context'}
        
        # Parse the answer to extract the value
        parsed = self.parser.parse_sentence(answer)
        
        # Try to extract a meaningful value from the answer
        value = None
        if parsed['object']:
            value = parsed['object']
        elif len(parsed['tokens']) > 0:
            # Use the first non-stop word
            value = parsed['tokens'][0]
        
        if not value:
            return {
                'type': 'clarification',
                'message': "I didn't quite understand. Could you rephrase that?"
            }
        
        # Add the property
        self.current_question_object.add_property(self.current_question_field, value)
        self.manager.save_object(self.current_question_object)
        
        # Generate confirmation
        confirmation = generate_confirmation(
            self.current_question_object.word,
            self.current_question_field,
            value
        )
        
        # Reset state
        obj_word = self.current_question_object.word
        field = self.current_question_field
        self.waiting_for_answer = False
        self.current_question_object = None
        self.current_question_field = None
        
        return {
            'type': 'learned_answer',
            'object': obj_word,
            'field': field,
            'value': value,
            'message': confirmation
        }
    
    def _show_stats(self) -> Dict:
        """Show database statistics."""
        with DatabaseConnection(self.db_path) as db:
            total = get_object_count(db)
        
        message = f"\n📊 Beari2 Knowledge:\n   Total Objects: {total}"
        
        return {
            'type': 'stats',
            'total_objects': total,
            'message': message
        }
    
    def _show_help(self) -> Dict:
        """Show help message."""
        message = (
            "\n📚 Beari2 Help:\n\n"
            "How to use:\n"
            "  • Tell me about things: 'A dog is an animal'\n"
            "  • I'll create Living Objects that grow with properties\n"
            "  • I'll ask you questions about what I don't know\n"
            "  • Watch the database viewer to see objects grow in real-time!\n\n"
            "Commands:\n"
            "  stats  - Show knowledge statistics\n"
            "  help   - Show this message\n"
            "  quit   - Exit\n"
        )
        
        return {'type': 'help', 'message': message}
    
    def chat_loop(self):
        """Run interactive chat loop."""
        print("="*70)
        print("🐻 Welcome to Beari2 - Object-Oriented Learning AI")
        print("="*70)
        print("\nI learn by creating 'Living Objects' that grow with properties.")
        print("Tell me about things, and watch the database viewer to see them grow!")
        print("\nType 'help' for more info, 'quit' to exit.\n")
        print("="*70)
        
        while True:
            try:
                user_input = input("\n🧑 You: ").strip()
                
                if not user_input:
                    continue
                
                # Process
                result = self.process_input(user_input)
                
                # Handle quit
                if result['type'] == 'quit':
                    print(f"\n🐻 Beari: {result['message']}")
                    break
                
                # Display response
                if result.get('message'):
                    print(f"\n🐻 Beari: {result['message']}")
                
                # Display question if any
                if result.get('question'):
                    print(f"\n🐻 Beari: {result['question']}")
                
            except KeyboardInterrupt:
                print("\n\n🐻 Beari: Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Let's keep going!")


def main():
    """Main entry point."""
    db_path = "beari2.db"
    
    # Initialize database if needed
    if not os.path.exists(db_path):
        print("\n🔧 Initializing database...")
        initialize_database(db_path)
        print()
    
    # Start chat
    beari = Beari2(db_path)
    beari.chat_loop()


if __name__ == "__main__":
    main()
