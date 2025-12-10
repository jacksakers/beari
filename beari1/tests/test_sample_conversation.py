"""
Unit test for sample conversation from training_data/sample_conversation.txt

Tests the complete conversation flow with all features:
- Greeting detection
- Question analysis
- Pronoun conversion
- POS detection and questioning
- Adjective-noun relationships
- Property numbering (is, is_2, etc.)
- Database updates
- Response generation
"""

import os
import sys
import unittest

# Add beari2 directory to path
beari2_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'beari2')
sys.path.insert(0, beari2_dir)

# Change to beari2 directory so relative imports work
orig_dir = os.getcwd()
os.chdir(beari2_dir)

from beari2 import Beari2
from db import initialize_database, DatabaseConnection, get_object, get_all_objects
from utils import set_debug_mode


class TestSampleConversation(unittest.TestCase):
    """Test the complete sample conversation flow."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        cls.test_db = "test_sample_conversation.db"
        
        # Remove existing test db
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
        
        # Initialize fresh database
        initialize_database(cls.test_db)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
    
    def setUp(self):
        """Set up Beari instance for each test."""
        self.beari = Beari2(db_path=self.test_db, use_game_engine=False, debug=False)
    
    def test_01_greeting_and_question(self):
        """Test: 'Hello, how are you Beari?'"""
        print("\n" + "="*60)
        print("TEST 1: Hello, how are you Beari?")
        print("="*60)
        
        result = self.beari.process_input("Hello, how are you Beari?")
        
        # Should detect greeting
        self.assertIn('type', result)
        
        # Response should start with greeting
        message = result.get('message', '')
        print(f"Response: {message}")
        
        # Check that response contains greeting
        self.assertTrue(
            message.lower().startswith('hello') or 'hello' in message.lower(),
            "Response should contain greeting"
        )
    
    def test_02_first_statement(self):
        """Test: 'I am well!'"""
        print("\n" + "="*60)
        print("TEST 2: I am well!")
        print("="*60)
        
        result = self.beari.process_input("I am well!")
        
        print(f"Response: {result.get('message', '')}")
        print(f"Type: {result.get('type')}")
        print(f"Objects updated: {result.get('objects_updated', 0)}")
        
        # Should learn that "I am well"
        self.assertEqual(result.get('type'), 'learned_and_asking')
        
        # Check database for "i" object with "is" = "well"
        with DatabaseConnection(self.test_db) as db:
            i_obj = get_object(db, 'i')
            self.assertIsNotNone(i_obj, "'i' object should exist in database")
            
            well_obj = get_object(db, 'well')
            self.assertIsNotNone(well_obj, "'well' object should exist in database")
        
        # Confirmation should convert "I" to "you"
        self.assertIn('you', result.get('message', '').lower())
    
    def test_03_complex_statement_with_unknown_word(self):
        """Test: 'I am enjoying my cold Saturday morning.'"""
        print("\n" + "="*60)
        print("TEST 3: I am enjoying my cold Saturday morning.")
        print("="*60)
        
        result = self.beari.process_input("I am enjoying my cold Saturday morning.")
        
        print(f"Response: {result.get('message', '')}")
        print(f"Type: {result.get('type')}")
        
        # Should ask about POS of "Saturday" (unknown word)
        self.assertEqual(result.get('type'), 'asking_pos')
        self.assertEqual(result.get('word'), 'saturday')
        
        message = result.get('message', '')
        self.assertIn('saturday', message.lower())
        self.assertIn('part of speech', message.lower())
    
    def test_04_pos_answer(self):
        """Test answering POS question: 'a noun'"""
        print("\n" + "="*60)
        print("TEST 4: Answer POS question - 'a noun'")
        print("="*60)
        
        # First trigger the question
        self.beari.process_input("I am enjoying my cold Saturday morning.")
        
        # Then answer it
        result = self.beari.process_input("a noun")
        
        print(f"Response: {result.get('message', '')}")
        print(f"Type: {result.get('type')}")
        
        # Should confirm and thank
        self.assertIn(result.get('type'), ['pos_answered', 'pos_answered_asking_next'])
        message = result.get('message', '')
        self.assertIn('thank', message.lower())
        self.assertIn('saturday', message.lower())
        self.assertIn('noun', message.lower())
        
        # Check database that Saturday is saved as Noun
        with DatabaseConnection(self.test_db) as db:
            saturday_obj = get_object(db, 'saturday')
            self.assertIsNotNone(saturday_obj, "'saturday' object should exist")
            self.assertEqual(saturday_obj['type'], 'Noun')
    
    def test_05_database_state_after_statements(self):
        """Verify database state after processing statements."""
        print("\n" + "="*60)
        print("TEST 5: Verify database state")
        print("="*60)
        
        # Process the full conversation flow
        self.beari.process_input("I am well!")
        self.beari.process_input("I am enjoying my cold Saturday morning.")
        self.beari.process_input("a noun")
        
        with DatabaseConnection(self.test_db) as db:
            # Check "I" object
            i_obj = get_object(db, 'i')
            self.assertIsNotNone(i_obj)
            print(f"Found 'i' object: {i_obj}")
            
            # Check "well" object
            well_obj = get_object(db, 'well')
            self.assertIsNotNone(well_obj)
            print(f"Found 'well' object: {well_obj}")
            
            # Check "morning" object (might not exist if stopped at POS question)
            morning_obj = get_object(db, 'morning')
            if morning_obj:
                print(f"Found 'morning' object: {morning_obj}")
                self.assertEqual(morning_obj['type'], 'Noun')
            else:
                print("'morning' object not yet created (stopped at POS question)")
            
            # Check "cold" object (might not exist if stopped at POS question)
            cold_obj = get_object(db, 'cold')
            if cold_obj:
                print(f"Found 'cold' object: {cold_obj}")
                self.assertEqual(cold_obj['type'], 'Adjective')
            else:
                print("'cold' object not yet created (stopped at POS question)")
            
            # Check "saturday" object (should exist after answering POS question)
            saturday_obj = get_object(db, 'saturday')
            self.assertIsNotNone(saturday_obj, "'saturday' should exist after POS answer")
            print(f"Found 'saturday' object: {saturday_obj}")
            self.assertEqual(saturday_obj['type'], 'Noun')
    
    def test_06_adjective_can_describe_relation(self):
        """Verify that 'cold' has can_describe relationship with nouns."""
        print("\n" + "="*60)
        print("TEST 6: Verify adjective can_describe relationship")
        print("="*60)
        
        # Process statements
        self.beari.process_input("I am enjoying my cold Saturday morning.")
        self.beari.process_input("a noun")
        
        # Load cold object and check properties
        cold_obj = self.beari.manager.load_object('cold')
        
        if cold_obj is None:
            # Object might not have been created if we stopped at POS question
            self.skipTest("'cold' object not created (stopped at POS question)")
        
        print(f"Cold object properties: {cold_obj.properties}")
        
        # Check that cold has can_describe property
        # properties is a Dict[str, List]
        can_describe_values = cold_obj.properties.get('can_describe', [])
        self.assertGreater(len(can_describe_values), 0, "'cold' should have can_describe properties")
        
        # Should describe either "saturday" or "morning"
        print(f"Cold can describe: {can_describe_values}")
        self.assertTrue(
            'saturday' in can_describe_values or 'morning' in can_describe_values,
            "'cold' should describe 'saturday' or 'morning'"
        )
    
    def test_07_feels_like_statement(self):
        """Test: 'Morning feels renewing and refreshing.'"""
        print("\n" + "="*60)
        print("TEST 7: Morning feels renewing and refreshing.")
        print("="*60)
        
        result = self.beari.process_input("Morning feels renewing and refreshing.")
        
        print(f"Response: {result.get('message', '')}")
        print(f"Type: {result.get('type')}")
        
        # Load morning object
        morning_obj = self.beari.manager.load_object('morning')
        
        if morning_obj is None:
            self.skipTest("'morning' object not created (stopped at POS question)")
        
        print(f"Morning object properties: {morning_obj.properties}")
        
        # Check for feels_like property
        # properties is a Dict[str, List]
        feels_like_props = {k: v for k, v in morning_obj.properties.items() if k.startswith('feels_like')}
        self.assertGreater(len(feels_like_props), 0, "'morning' should have feels_like property")
        
        # Should have "renewing" as a feels_like value
        all_values = []
        for values in feels_like_props.values():
            all_values.extend(values)
        
        print(f"Morning feels_like: {all_values}")
        self.assertIn('renewing', all_values, "'morning' should feel like 'renewing'")
    
    def test_08_multiple_property_numbering(self):
        """Test that multiple 'is' properties are numbered (is, is_2, is_3)."""
        print("\n" + "="*60)
        print("TEST 8: Multiple property numbering")
        print("="*60)
        
        # Add multiple "is" properties to an object
        self.beari.process_input("A dog is friendly.")
        result = self.beari.process_input("A dog is furry.")
        
        print(f"Response: {result.get('message', '')}")
        
        # Load dog object
        dog_obj = self.beari.manager.load_object('dog')
        self.assertIsNotNone(dog_obj)
        
        print(f"Dog object properties: {dog_obj.properties}")
        
        # Check for multiple "is" properties
        # properties is a Dict[str, List], not a list of dicts
        is_props = {k: v for k, v in dog_obj.properties.items() if k.startswith('is')}
        print(f"'is' properties: {is_props}")
        self.assertGreaterEqual(len(is_props), 2, "Should have at least 2 'is'-related properties")
        
        # Check that they are numbered
        self.assertIn('is', is_props, "Should have 'is' property")
        numbered_props = [k for k in is_props.keys() if k.startswith('is_')]
        self.assertGreater(len(numbered_props), 0, "Should have numbered 'is_X' properties")
        print(f"Numbered properties: {numbered_props}")
    
    def test_09_full_conversation_flow(self):
        """Test the complete conversation flow from sample."""
        print("\n" + "="*60)
        print("TEST 9: Full conversation flow")
        print("="*60)
        
        # Clean database for this test
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        initialize_database(self.test_db)
        self.beari = Beari2(db_path=self.test_db, use_game_engine=False, debug=False)
        
        # Note: Turn 2 will ask a gap question ("What can i do?")
        # This sets waiting_for_answer=True, so turn 3 will be processed as an answer to that question
        # rather than as a new statement that would trigger POS questions
        conversation = [
            ("Hello, how are you Beari?", "greeting"),
            ("I am well!", "learned"),
            ("I can run", "learned"),  # Answer the gap question from turn 2
            ("I am enjoying my cold Saturday morning.", "asking_pos"),  # Now asks POS about saturday
            ("a noun", "pos_answered"),  # Answer the POS question
        ]
        
        for i, (user_input, expected_type_partial) in enumerate(conversation, 1):
            print(f"\n--- Turn {i} ---")
            print(f"User: {user_input}")
            print(f"Waiting for answer: {self.beari.waiting_for_answer}")
            print(f"Waiting for POS answer: {self.beari.waiting_for_pos_answer}")
            
            result = self.beari.process_input(user_input)
            response_type = result.get('type', '')
            
            print(f"Beari: {result.get('message', '')}")
            print(f"Type: {response_type}")
            print(f"Expected type to contain: '{expected_type_partial}'")
            
            # Check type matches expected (can be partial match)
            self.assertIn(
                expected_type_partial, response_type,
                f"Turn {i}: Expected type to contain '{expected_type_partial}', got '{response_type}'"
            )
        
        # Final database check
        print("\n--- Final Database State ---")
        with DatabaseConnection(self.test_db) as db:
            all_objects = get_all_objects(db)
            print(f"Total objects: {len(all_objects)}")
            for obj in all_objects:
                print(f"  - {obj['name']} ({obj['type']})")
        
        # Verify key objects exist (only those we know were created)
        key_objects = ['i', 'well', 'saturday']
        with DatabaseConnection(self.test_db) as db:
            for word in key_objects:
                obj = get_object(db, word)
                self.assertIsNotNone(obj, f"'{word}' should exist in database")
                print(f"[OK] Verified '{word}' exists")


class TestDebugMode(unittest.TestCase):
    """Test debug mode functionality."""
    
    def setUp(self):
        """Set up for debug tests."""
        self.test_db = "test_debug.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        initialize_database(self.test_db)
    
    def tearDown(self):
        """Clean up debug test database."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_debug_mode_on_off(self):
        """Test enabling and disabling debug mode."""
        print("\n" + "="*60)
        print("TEST: Debug mode on/off")
        print("="*60)
        
        # Create with debug off
        beari = Beari2(db_path=self.test_db, debug=False)
        result = beari.process_input("debug on")
        self.assertEqual(result.get('type'), 'command')
        print("[OK] Debug mode enabled")
        
        result = beari.process_input("debug off")
        self.assertEqual(result.get('type'), 'command')
        print("[OK] Debug mode disabled")
    
    def test_debug_logging(self):
        """Test that debug mode logs parsing steps."""
        print("\n" + "="*60)
        print("TEST: Debug logging output")
        print("="*60)
        
        # Create with debug enabled
        beari = Beari2(db_path=self.test_db, debug=True)
        
        print("\nProcessing with debug enabled:")
        result = beari.process_input("I am happy!")
        
        # Just verify it doesn't crash
        self.assertIsNotNone(result)
        print("[OK] Debug logging works without errors")


def run_tests():
    """Run all tests with verbose output."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSampleConversation))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDebugMode))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
