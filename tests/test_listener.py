"""
Test Script for Beari Listener, Parser, and Question Generator
Run this to verify all learning components work correctly.
"""

import os
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_helpers import DatabaseHelper
from parser import Parser
from question_generator import QuestionGenerator
from listener import Listener


def test_parser():
    """Test the Parser module."""
    print("\n=== Testing Parser ===")
    
    # Create test database
    with DatabaseHelper("test_listener.db") as db:
        db.initialize_database()
        
        # Add some known words
        db.add_word("dog", pos_tag="Noun", meaning_tag="animal")
        db.add_word("cat", pos_tag="Noun", meaning_tag="animal")
        db.add_word("run", pos_tag="Verb")
        db.add_word("fast", pos_tag="Adjective")
        
        parser = Parser(db)
        
        # Test 1: Tokenization
        print("\n1. Testing tokenization...")
        text = "The dog runs fast!"
        tokens = parser.tokenize(text)
        print(f"   Input: '{text}'")
        print(f"   Tokens: {tokens}")
        assert tokens == ['the', 'dog', 'runs', 'fast'], "Tokenization failed"
        print("   ✓ Tokenization works correctly")
        
        # Test 2: Unknown word detection
        print("\n2. Testing unknown word detection...")
        tokens = ['the', 'dog', 'runs', 'fast']
        unknown = parser.identify_unknown_words(tokens)
        print(f"   Tokens: {tokens}")
        print(f"   Unknown words: {unknown}")
        assert 'the' in unknown and 'runs' in unknown, "Should detect 'the' and 'runs'"
        assert 'dog' not in unknown and 'fast' not in unknown, "Should recognize known words"
        print("   ✓ Unknown detection works correctly")
        
        # Test 3: Full sentence parsing
        print("\n3. Testing full sentence parsing...")
        result = parser.parse_sentence("The capybara runs fast")
        print(f"   Input: 'The capybara runs fast'")
        print(f"   Known: {result['known_words']}")
        print(f"   Unknown: {result['unknown_words']}")
        assert 'capybara' in result['unknown_words'], "Should detect 'capybara'"
        assert result['has_unknowns'], "Should flag unknowns"
        print("   ✓ Sentence parsing works correctly")
        
        # Test 4: Context extraction
        print("\n4. Testing context extraction...")
        tokens = ['the', 'big', 'dog', 'runs', 'fast']
        prev, next_word = parser.get_context_words(tokens, 'dog')
        print(f"   Tokens: {tokens}")
        print(f"   Context for 'dog': prev='{prev}', next='{next_word}'")
        assert prev == 'big' and next_word == 'runs', "Context extraction failed"
        print("   ✓ Context extraction works correctly")
        
        # Test 5: Sentence structure analysis
        print("\n5. Testing sentence structure analysis...")
        structure = parser.analyze_sentence_structure(['the', 'dog', 'run', 'fast'])
        print(f"   Tokens: ['the', 'dog', 'run', 'fast']")
        print(f"   Structure: {structure}")
        assert 'dog' in structure['nouns'], "Should identify 'dog' as noun"
        assert 'run' in structure['verbs'], "Should identify 'run' as verb"
        print("   ✓ Structure analysis works correctly")
    
    print("\n✓ All parser tests passed!")


def test_question_generator():
    """Test the Question Generator module."""
    print("\n=== Testing Question Generator ===")
    
    qgen = QuestionGenerator()
    
    # Test 1: Generate general question
    print("\n1. Testing general question generation...")
    question = qgen.generate_question("capybara")
    print(f"   Word: 'capybara'")
    print(f"   Question: {question}")
    assert "capybara" in question.lower(), "Question should contain the word"
    print("   ✓ General question generated")
    
    # Test 2: Generate contextual question (verb)
    print("\n2. Testing contextual question (verb)...")
    context = {'prev_word': 'to', 'next_word': 'quickly'}
    question = qgen.generate_question("scurry", context)
    print(f"   Word: 'scurry' (context: 'to ... quickly')")
    print(f"   Question: {question}")
    assert "scurry" in question.lower(), "Question should contain the word"
    print("   ✓ Contextual verb question generated")
    
    # Test 3: Generate contextual question (noun)
    print("\n3. Testing contextual question (noun)...")
    context = {'prev_word': 'the', 'next_word': 'is'}
    question = qgen.generate_question("platypus", context)
    print(f"   Word: 'platypus' (context: 'the ... is')")
    print(f"   Question: {question}")
    assert "platypus" in question.lower(), "Question should contain the word"
    print("   ✓ Contextual noun question generated")
    
    # Test 4: Parse user response (noun + animal)
    print("\n4. Testing response parsing...")
    response = "It's an animal, a type of creature"
    parsed = qgen.parse_user_response(response)
    print(f"   Response: '{response}'")
    print(f"   Parsed: {parsed}")
    assert parsed['pos_tag'] or parsed['meaning_tag'], "Should extract some info"
    print("   ✓ Response parsing works")
    
    # Test 5: Generate confirmation
    print("\n5. Testing confirmation generation...")
    confirmation = qgen.generate_confirmation("elephant", pos_tag="Noun", meaning_tag="animal")
    print(f"   Word: 'elephant' (Noun, animal)")
    print(f"   Confirmation: {confirmation}")
    assert "elephant" in confirmation.lower(), "Should mention the word"
    print("   ✓ Confirmation generated")
    
    print("\n✓ All question generator tests passed!")


def test_listener():
    """Test the Listener module with full workflow."""
    print("\n=== Testing Listener ===")
    
    # Clean up test db if it exists
    if os.path.exists("test_listener.db"):
        os.remove("test_listener.db")
    
    with Listener("test_listener.db") as listener:
        # Initialize database with sample data
        listener.db.initialize_database()
        listener.db.add_word("dog", pos_tag="Noun", meaning_tag="animal")
        listener.db.add_word("run", pos_tag="Verb")
        
        # Test 1: Process input with unknown word
        print("\n1. Testing unknown word detection...")
        result = listener.process_input("The elephant runs fast")
        print(f"   Input: 'The elephant runs fast'")
        print(f"   Result type: {result['type']}")
        print(f"   Question: {result.get('question')}")
        assert result['type'] == 'question', "Should ask a question"
        assert result['question'], "Should generate a question"
        assert listener.is_waiting_for_answer(), "Should be in learning mode"
        print("   ✓ Unknown word detected, question asked")
        
        # Test 2: Process learning response
        print("\n2. Testing learning response...")
        result = listener.process_input("It's an animal, a large creature")
        print(f"   Response: 'It's an animal, a large creature'")
        print(f"   Result type: {result['type']}")
        print(f"   Learned word: {result.get('word')}")
        print(f"   Message: {result.get('message')}")
        assert result['type'] == 'learned', "Should confirm learning"
        assert result['learned'], "Should mark as learned"
        assert not listener.is_waiting_for_answer(), "Should exit learning mode"
        print("   ✓ Word learned successfully")
        
        # Test 3: Verify word was added to database
        print("\n3. Testing database update...")
        word_info = listener.db.get_word("elephant")
        print(f"   Checking database for 'elephant'...")
        print(f"   Word info: {word_info}")
        assert word_info is not None, "Word should be in database"
        assert word_info['word'] == 'elephant', "Word should match"
        print("   ✓ Word stored in database correctly")
        
        # Test 4: Process input with all known words
        print("\n4. Testing with all known words...")
        result = listener.process_input("The dog runs")
        print(f"   Input: 'The dog runs'")
        print(f"   Result type: {result['type']}")
        assert result['type'] in ['understood', 'question'], "Should process normally"
        print("   ✓ Known words processed correctly")
        
        # Test 5: Check statistics
        print("\n5. Testing statistics...")
        stats = listener.get_vocabulary_stats()
        print(f"   Stats: {stats}")
        assert stats['vocabulary_size'] >= 2, "Should have at least 2 words"
        print("   ✓ Statistics retrieved correctly")
    
    print("\n✓ All listener tests passed!")


def test_integration():
    """Test full integration of all components."""
    print("\n=== Testing Full Integration ===")
    
    # Clean up test db if it exists
    if os.path.exists("test_listener.db"):
        os.remove("test_listener.db")
    
    with Listener("test_listener.db") as listener:
        listener.db.initialize_database()
        
        # Simulate a conversation
        print("\n1. Simulating conversation...")
        
        # First sentence with unknown words
        print("\n   User: 'The robot calculates data'")
        result1 = listener.process_input("The robot calculates data")
        print(f"   Beari: {result1.get('question') or result1.get('message')}")
        
        if result1['type'] == 'question':
            # Answer about the unknown word
            print("\n   User: 'It's a machine, related to technology'")
            result2 = listener.process_input("It's a machine, related to technology")
            print(f"   Beari: {result2.get('message')}")
        
        # Second sentence
        print("\n   User: 'Python is easy'")
        result3 = listener.process_input("Python is easy")
        print(f"   Beari: {result3.get('question') or result3.get('message')}")
        
        if result3['type'] == 'question':
            print("\n   User: 'It's a programming language'")
            result4 = listener.process_input("It's a programming language")
            print(f"   Beari: {result4.get('message')}")
        
        # Check final stats
        stats = listener.get_vocabulary_stats()
        print(f"\n   Final vocabulary size: {stats['vocabulary_size']}")
        print(f"   Total relations: {stats['total_relations']}")
        
        print("\n✓ Integration test completed!")


def cleanup_test_database():
    """Remove test database file."""
    if os.path.exists("test_listener.db"):
        os.remove("test_listener.db")
        print("\n✓ Test database cleaned up")


def main():
    """Run all tests."""
    print("="*60)
    print("BEARI LISTENER TEST SUITE")
    print("="*60)
    
    try:
        test_parser()
        test_question_generator()
        test_listener()
        test_integration()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✓")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cleanup_test_database()


if __name__ == "__main__":
    main()
