"""
Beari2 - Object-Oriented Learning AI
Main conversation interface with Living Objects.
"""

import sys
import os
import random
from typing import Dict, Optional, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.living_object import LivingObject
from core.object_manager import ObjectManager
from core.gap_analysis import find_learning_opportunity, suggest_next_question_field
from core.question_generator import generate_question, generate_confirmation
from core.game_engine import GameEngine
from core.question_answerer import QuestionAnswerer
from utils.input_parser import InputParser
from utils.debug_logger import get_debug_logger, set_debug_mode
from db import initialize_database, get_object_count, DatabaseConnection


class Beari2:
    """
    Main Beari2 AI interface with Object-Oriented Learning.
    
    Features:
    - Parses input to extract subjects, predicates, objects
    - Creates and updates Living Objects dynamically
    - Identifies knowledge gaps and asks targeted questions
    - Answers user questions using database knowledge
    - Confirms learning through natural responses
    """
    
    def __init__(self, db_path: str = "beari2.db", use_game_engine: bool = True, debug: bool = False):
        """
        Initialize Beari2.
        
        Args:
            db_path: Path to database file
            use_game_engine: Enable the conversation game engine for optimized responses
            debug: Enable debug logging
        """
        self.db_path = db_path
        self.manager = ObjectManager(db_path)
        self.parser = InputParser()
        
        # Game Engine (optional)
        self.use_game_engine = use_game_engine
        self.game_engine = GameEngine() if use_game_engine else None
        
        # Question Answerer
        self.answerer = QuestionAnswerer(self.manager)
        
        # Learning state
        self.waiting_for_answer = False
        self.current_question_object = None
        self.current_question_field = None
        self.pending_pos_questions = []  # Queue of unknown words needing POS clarification
        self.waiting_for_pos_answer = False
        self.current_pos_word = None
        
        # Subject tracking (for conversation continuity)
        self.conversation_subjects = []
        
        # Debug mode
        set_debug_mode(debug)
        self.debug = get_debug_logger()
    
    def process_input(self, user_input: str) -> Dict:
        """
        Main input processing pipeline.
        
        Args:
            user_input: User's message
        
        Returns:
            Response dictionary
        """
        user_input = user_input.strip()
        
        self.debug.section(f"USER INPUT: '{user_input}'")
        
        if not user_input:
            return {'type': 'empty', 'message': '...'}
        
        # Check for quit
        if user_input.lower() in ['quit', 'exit', 'bye']:
            return {'type': 'quit', 'message': 'Goodbye! Keep learning! 🐻'}
        
        # Check for special commands
        if user_input.lower() == 'stats':
            return self._show_stats()
        
        if user_input.lower() == 'score':
            return self._show_game_score()
        
        if user_input.lower() == 'help':
            return self._show_help()
        
        if user_input.lower() == 'debug on':
            set_debug_mode(True)
            return {'type': 'command', 'message': '🐛 Debug mode enabled'}
        
        if user_input.lower() == 'debug off':
            set_debug_mode(False)
            return {'type': 'command', 'message': 'Debug mode disabled'}
        
        # if user enters ? then generate a question about a random object
        if user_input.strip() == '?':
            all_objects = self.manager.get_all()
            for obj in all_objects:
                field = suggest_next_question_field(obj)
                if field:
                    question = generate_question(obj.word, field, obj.pos)
                    self.waiting_for_answer = True
                    self.current_question_object = obj
                    self.current_question_field = field
                    return {
                        'type': 'asking',
                        'question': question,
                        'object': obj.word,
                        'field': field
                    }
            return {
                'type': 'no_question',
                'message': "I don't have any questions right now. Teach me something new!"
            }
        
        # If waiting for POS answer
        if self.waiting_for_pos_answer and self.current_pos_word:
            return self._process_pos_answer(user_input)
        
        # If waiting for answer to a property question
        if self.waiting_for_answer and self.current_question_object:
            # if the user input is empty, treat it as a pass and do not process
            if not user_input:
                self.waiting_for_answer = False
                self.current_question_object = None
                self.current_question_field = None
                return {'type': 'pass', 'message': 'No answer provided. Moving on.'}
            return self._process_learning_answer(user_input)
        
        # Otherwise, parse and learn from the input
        return self._process_new_sentence(user_input)
    
    def _process_pos_answer(self, answer: str) -> Dict:
        """
        Process user's answer to a part-of-speech question.
        
        Args:
            answer: User's answer
        
        Returns:
            Response dictionary
        """
        self.debug.log_learn(f"Processing POS answer: '{answer}' for word '{self.current_pos_word}'")
        
        answer_lower = answer.lower().strip()
        
        # Parse the answer
        pos_type = None
        if 'noun' in answer_lower:
            pos_type = 'Noun'
        elif 'verb' in answer_lower:
            pos_type = 'Verb'
        elif 'adjective' in answer_lower or 'adj' in answer_lower:
            pos_type = 'Adjective'
        
        if pos_type:
            # Create or update the object with the correct POS
            obj = self.manager.create_or_get(self.current_pos_word, pos_type)
            self.manager.save_object(obj)
            
            self.debug.log_learn(f"Saved '{self.current_pos_word}' as {pos_type}")
            
            # Reset state
            word = self.current_pos_word
            self.waiting_for_pos_answer = False
            self.current_pos_word = None
            
            # Check if there are more POS questions
            if self.pending_pos_questions:
                next_word = self.pending_pos_questions.pop(0)
                self.current_pos_word = next_word
                self.waiting_for_pos_answer = True
                
                return {
                    'type': 'pos_answered_asking_next',
                    'message': f"Thank you, I now know that {word} is a {pos_type.lower()}!\nWhat part of speech is {next_word}?",
                    'word': next_word
                }
            else:
                return {
                    'type': 'pos_answered',
                    'message': f"Thank you, I now know that {word} is a {pos_type.lower()}!",
                    'word': word,
                    'pos': pos_type
                }
        else:
            return {
                'type': 'pos_unclear',
                'message': "I'm not sure what you mean. Is it a noun, verb, or adjective?",
                'word': self.current_pos_word
            }
    
    def _process_new_sentence(self, sentence: str) -> Dict:
        """
        Process a new sentence: parse, create objects, update properties.
        Handles both questions and statements differently.
        
        Args:
            sentence: User's sentence
        
        Returns:
            Response dictionary
        """
        self.debug.log("Processing new sentence", "PROCESSING")
        
        # Parse the sentence
        parsed = self.parser.parse_sentence(sentence)
        sentence_type = parsed.get('sentence_type', 'statement')
        
        self.debug.log(f"Sentence type: {sentence_type}", "PROCESSING")
        
        # Handle greeting if present
        greeting_response = ""
        if parsed.get('greeting'):
            greeting = parsed['greeting'].capitalize()
            greeting_response = f"{greeting}! "
            self.debug.log_response(f"Adding greeting response: '{greeting}!'")
        
        # If user asked a question, try to answer it first
        answer_result = None
        if sentence_type == 'question':
            self.debug.log("Attempting to answer question", "PROCESSING")
            answer_result = self.answerer.answer_question(parsed)
        
        # Handle unknown words - ask about POS first
        if parsed.get('unknown_words') and sentence_type == 'statement':
            self.debug.log(f"Unknown words found: {parsed['unknown_words']}", "PROCESSING")
            self.pending_pos_questions = parsed['unknown_words'].copy()
            
            if self.pending_pos_questions:
                first_unknown = self.pending_pos_questions.pop(0)
                self.current_pos_word = first_unknown
                self.waiting_for_pos_answer = True
                
                self.debug.log(f"Asking POS question for: '{first_unknown}'", "PROCESSING")
                
                return {
                    'type': 'asking_pos',
                    'message': f"{greeting_response}What part of speech is {first_unknown}?",
                    'word': first_unknown,
                    'pending': len(self.pending_pos_questions)
                }
        
        # Extract relations (for statements, learn from them)
        relations = self.parser.extract_relations(parsed)
        
        self.debug.log(f"Extracted {len(relations)} relations", "PROCESSING")
        
        # Update or create objects for each component
        updated_objects = []
        
        # Only create/update objects if it's a statement (learning)
        # For questions, we just look up existing objects
        if sentence_type == 'statement':
            self.debug.log("Creating/updating objects from statement", "LEARN")
            self.debug.indent()
            
            # Track subjects for conversation
            if parsed.get('subjects'):
                for subject in parsed['subjects']:
                    if subject not in self.conversation_subjects:
                        self.conversation_subjects.append(subject)
                    # Keep only recent subjects (max 5)
                    if len(self.conversation_subjects) > 5:
                        self.conversation_subjects.pop(0)
            
            if parsed['subject']:
                obj = self.manager.create_or_get(parsed['subject'], 'Noun')
                updated_objects.append(obj)
                self.debug.log_learn(f"Created/loaded subject object: '{parsed['subject']}'")
            
            if parsed['object']:
                # Infer POS from context
                pos = 'Adjective' if parsed['verb_relation'] == 'is' else 'Noun'
                obj = self.manager.create_or_get(parsed['object'], pos)
                updated_objects.append(obj)
                self.debug.log_learn(f"Created/loaded object: '{parsed['object']}' as {pos}")
            
            if parsed['verb'] and parsed['verb'] not in self.parser.relation_verbs:
                obj = self.manager.create_or_get(parsed['verb'], 'Verb')
                updated_objects.append(obj)
                self.debug.log_learn(f"Created/loaded verb object: '{parsed['verb']}'")
            
            # Create objects for all parsed subjects and adjectives
            for subject in parsed.get('subjects', []):
                if subject and subject != parsed.get('subject'):
                    obj = self.manager.create_or_get(subject, 'Noun')
                    if obj not in updated_objects:
                        updated_objects.append(obj)
                        self.debug.log_learn(f"Created/loaded additional subject: '{subject}'")
            
            for adj in parsed.get('adjectives', []):
                obj = self.manager.create_or_get(adj, 'Adjective')
                if obj not in updated_objects:
                    updated_objects.append(obj)
                    self.debug.log_learn(f"Created/loaded adjective: '{adj}'")
            
            # Apply relations
            self.debug.log(f"Applying {len(relations)} relations to objects", "LEARN")
            for relation in relations:
                # Determine POS for source
                source_pos = 'Noun'
                if relation['source'] in parsed.get('adjectives', []):
                    source_pos = 'Adjective'
                elif relation['source'] == parsed.get('verb'):
                    source_pos = 'Verb'
                
                source_obj = self.manager.create_or_get(relation['source'], source_pos)
                
                # Handle property keys with numbering (is, is_2, is_3, etc.)
                base_relation = relation['relation']
                property_key = base_relation
                
                # Check if base_relation already exists in properties dict
                if base_relation in source_obj.properties and source_obj.properties[base_relation]:
                    # Count how many numbered versions exist
                    existing_numbered = [k for k in source_obj.properties.keys() if k.startswith(base_relation + '_')]
                    property_key = f"{base_relation}_{len(existing_numbered) + 1}"
                    self.debug.log_learn(f"Property '{base_relation}' exists, using '{property_key}'")
                
                source_obj.add_property(property_key, relation['target'])
                self.manager.save_object(source_obj)
                
                self.debug.log_db(f"Saved: {source_obj.word}.{property_key} = {relation['target']}")
                
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
            
            self.debug.dedent()
        else:
            # For questions, just load the relevant objects for context
            if parsed.get('question_target'):
                obj = self.manager.load_object(parsed['question_target'])
                if obj:
                    updated_objects.append(obj)
            if parsed.get('subject'):
                obj = self.manager.load_object(parsed['subject'])
                if obj and obj not in updated_objects:
                    updated_objects.append(obj)
        
        # Generate confirmation (for statements)
        confirmation = self._generate_confirmation(parsed, relations) if sentence_type == 'statement' else None
        
        # Find gap for inquiry mode
        gap_field = None
        gap_object = None
        for obj in updated_objects:
            field = suggest_next_question_field(obj)
            if field:
                gap_field = field
                gap_object = obj
                break
        
        # Build response message
        message_parts = []
        
        if greeting_response:
            message_parts.append(greeting_response.strip())
        
        if sentence_type == 'question' and answer_result:
            # Add the answer
            answer_text = answer_result.get('answer', "I don't know about that yet.")
            message_parts.append(answer_text)
        elif confirmation:
            # Add confirmation for statements
            message_parts.append(confirmation)
        
        # Add inquiry if we found a gap
        if gap_field and gap_object:
            question = generate_question(gap_object.word, gap_field, gap_object.pos)
            message_parts.append(question)
            
            # Set waiting state
            self.waiting_for_answer = True
            self.current_question_object = gap_object
            self.current_question_field = gap_field
            
            self.debug.log_response(f"Generated gap question: '{question}'")
        
        final_message = " ".join(message_parts) if message_parts else "I'm listening."
        
        # Determine response type
        if greeting_response and sentence_type == 'question':
            response_type = 'greeting'
        else:
            response_type = 'answered' if sentence_type == 'question' else 'learned'
        
        if gap_field and gap_object:
            response_type += '_and_asking'
        
        return {
            'type': response_type,
            'parsed': parsed,
            'relations': relations,
            'sentence_type': sentence_type,
            'message': final_message,
            'objects_updated': len(updated_objects),
            'updated_objects': [{'word': obj.word, 'pos': obj.pos} for obj in updated_objects]
        }
    
    def _generate_confirmation(self, parsed: Dict, relations: list) -> str:
        """
        Generate a natural confirmation of what was learned.
        Uses pronoun conversion to mirror back the user's statement properly.
        
        Args:
            parsed: Parsed sentence
            relations: Extracted relations
        
        Returns:
            Confirmation string
        """
        if not relations:
            return "I'm listening and learning from what you say."
        
        self.debug.log_response("Generating confirmation with pronoun conversion")
        
        # Generate confirmation based on first relation with converted pronouns
        rel = relations[0]
        
        # Convert source and target for response
        source = rel['source']
        target = rel['target']
        
        # Convert "I" to "you" for the response
        if source.lower() == 'i':
            source = 'you'
        elif source.lower() in ['you', 'beari']:
            source = 'I'
        
        if target.lower() == 'i':
            target = 'you'
        elif target.lower() in ['you', 'beari']:
            target = 'I'
        
        # Generate confirmation based on relation type
        if rel['relation'] == 'is' or rel['relation'].startswith('is_'):
            # Handle verb conjugation
            verb = 'are' if source.lower() == 'you' else 'is'
            if source.lower() == 'i':
                verb = 'am'
            return f"I see, {source} {verb} {target}."
        elif rel['relation'] == 'can_have' or rel['relation'].startswith('can_have_'):
            return f"Got it, {source} can have {target}."
        elif rel['relation'] == 'can_do' or rel['relation'].startswith('can_do_'):
            return f"I understand, {source} can {target}."
        elif rel['relation'] == 'feels_like' or rel['relation'].startswith('feels_like_'):
            return f"I see, {source} feels like {target}."
        elif rel['relation'].startswith('enjoy'):
            verb = 'are enjoying' if source.lower() == 'you' else 'is enjoying'
            if source.lower() == 'i':
                verb = 'am enjoying'
            
            # Convert possessives in target
            target_converted = target
            if 'my ' in target:
                target_converted = target.replace('my ', 'your ')
            elif 'your ' in target:
                target_converted = target.replace('your ', 'my ')
            
            return f"Understood, {source} {verb} {target_converted}."
        else:
            return f"I learned about {source}."
    
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
            non_stop_tokens = [t for t in parsed['tokens'] if t not in self.parser.stop_words]
            if non_stop_tokens:
                value = non_stop_tokens[0]
        
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
    
    def _show_game_score(self) -> Dict:
        """Show game engine statistics."""
        if not self.game_engine:
            return {
                'type': 'info',
                'message': "Game Engine is not enabled."
            }
        
        stats = self.game_engine.get_game_stats()
        
        message = (
            f"\n🎮 Game Engine Stats:\n"
            f"   Total Score: {stats['total_score']:.1f}\n"
            f"   Turns Played: {stats['turn_count']}\n"
            f"   Average Score: {stats['average_score']:.2f}\n"
        )
        
        if stats['history']:
            message += "\n   Recent moves:\n"
            for turn in stats['history'][-5:]:
                message += f"     Turn {turn['turn']}: {turn['type']} (+{turn['score']:.1f})\n"
        
        return {
            'type': 'game_stats',
            'stats': stats,
            'message': message
        }
    
    def _show_help(self) -> Dict:
        """Show help message."""
        game_status = "enabled 🎮" if self.use_game_engine else "disabled"
        message = (
            "\n📚 Beari2 Help:\n\n"
            "How to use:\n"
            "  • Tell me about things: 'A dog is an animal'\n"
            "  • I'll create Living Objects that grow with properties\n"
            "  • I'll ask you questions about what I don't know\n"
            "  • Watch the database viewer to see objects grow in real-time!\n\n"
            f"Game Engine: {game_status}\n"
            "  The game engine optimizes responses based on:\n"
            "  - User Happiness (empathy matching)\n"
            "  - Knowledge Gain (filling gaps)\n"
            "  - Conversation Flow (keeping chat going)\n\n"
            "Commands:\n"
            "  stats  - Show knowledge statistics\n"
            "  score  - Show game engine score\n"
            "  ?      - Ask me to generate a question\n"
            "  help   - Show this message\n"
            "  quit   - Exit\n"
        )
        
        return {'type': 'help', 'message': message}
    
    def chat_loop(self):
        """Run interactive chat loop."""
        print("="*70)
        print("🐻 Welcome to Beari2 - Object-Oriented Learning AI")
        if self.use_game_engine:
            print("🎮 Game Engine: ENABLED (optimized responses)")
        print("="*70)
        print("\nI learn by creating 'Living Objects' that grow with properties.")
        print("Tell me about things, and watch the database viewer to see them grow!")
        print("\nType 'help' for more info, 'quit' to exit.\n")
        print("="*70)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
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

                # Display pass message if any
                if result['type'] == 'pass':
                    print(f"\n🐻 Beari: {result['message']}")
                
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
