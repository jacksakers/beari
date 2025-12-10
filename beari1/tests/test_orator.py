"""
Test Suite for Beari Orator and Corrector Modules
Run this to verify question answering and correction features work correctly.
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_helpers import DatabaseHelper
from orator import Orator
from corrector import Corrector


def test_orator():
    """Test the Orator module - question answering and sentence generation."""
    print("\n=== Testing Orator ===")
    
    # Create test database with sample data
    with DatabaseHelper("test_orator.db") as db:
        db.initialize_database()
        
        # Add sample vocabulary
        db.add_word("elephant", pos_tag="Noun", meaning_tag="animal")
        db.add_word("dog", pos_tag="Noun", meaning_tag="animal")
        db.add_word("robot", pos_tag="Noun", meaning_tag="technology")
        db.add_word("python", pos_tag="Noun", meaning_tag="technology")
        db.add_word("run", pos_tag="Verb")
        db.add_word("bark", pos_tag="Verb")
        db.add_word("calculate", pos_tag="Verb")
        db.add_word("friendly", pos_tag="Adjective")
        
        # Add relations
        db.add_relation("elephant", "is_a", "animal")
        db.add_relation("dog", "is_a", "animal")
        db.add_relation("dog", "capable_of", "run")
        db.add_relation("dog", "capable_of", "bark")
        db.add_relation("robot", "capable_of", "calculate")
        db.add_relation("python", "is_a", "language")
    
    with Orator("test_orator.db") as orator:
        # Test 1: Sentence generation
        print("\n1. Testing sentence generation...")
        sentence = orator.generate_sentence()
        print(f"   Generated: '{sentence}'")
        assert len(sentence) > 0, "Should generate a sentence"
        assert sentence.endswith('.'), "Should end with punctuation"
        print("   ✓ Sentence generation works")
        
        # Test 2: "What is" question
        print("\n2. Testing 'What is' question...")
        result = orator.answer_question("What is dog?")
        print(f"   Question: 'What is dog?'")
        print(f"   Answer: {result['message']}")
        assert result['type'] in ['answer', 'unknown'], "Should return answer or unknown"
        assert 'dog' in result['message'].lower(), "Should mention the word"
        print("   ✓ 'What is' questions work")
        
        # Test 3: Unknown word
        print("\n3. Testing unknown word...")
        result = orator.answer_question("What is unicorn?")
        print(f"   Question: 'What is unicorn?'")
        print(f"   Answer: {result['message']}")
        assert result['type'] == 'unknown', "Should identify unknown word"
        print("   ✓ Unknown word detection works")
        
        # Test 4: "What does" question
        print("\n4. Testing 'What does' question...")
        result = orator.answer_question("What does dog do?")
        print(f"   Question: 'What does dog do?'")
        print(f"   Answer: {result['message']}")
        assert 'run' in result['message'].lower() or 'bark' in result['message'].lower(), \
               "Should mention dog's capabilities"
        print("   ✓ 'What does' questions work")
        
        # Test 5: "Can" question
        print("\n5. Testing 'Can' question...")
        result = orator.answer_question("Can a dog run?")
        print(f"   Question: 'Can a dog run?'")
        print(f"   Answer: {result['message']}")
        assert result['type'] == 'answer', "Should provide an answer"
        print("   ✓ 'Can' questions work")
        
        # Test 6: "Is" question
        print("\n6. Testing 'Is' question...")
        result = orator.answer_question("Is dog an animal?")
        print(f"   Question: 'Is dog an animal?'")
        print(f"   Answer: {result['message']}")
        assert result['type'] == 'answer', "Should provide an answer"
        print("   ✓ 'Is' questions work")
        
        # Test 7: "Tell me about" question
        print("\n7. Testing 'Tell me about' question...")
        result = orator.answer_question("Tell me about python")
        print(f"   Question: 'Tell me about python'")
        print(f"   Answer: {result['message']}")
        assert 'python' in result['message'].lower(), "Should discuss python"
        print("   ✓ 'Tell me about' questions work")
    
    print("\n✓ All Orator tests passed!")


def test_corrector():
    """Test the Corrector module - handling corrections."""
    print("\n=== Testing Corrector ===")
    
    # Create test database with sample data
    with DatabaseHelper("test_corrector.db") as db:
        db.initialize_database()
        
        # Add sample vocabulary with some "wrong" information
        db.add_word("python", pos_tag="Noun", meaning_tag="animal")
        db.add_word("robot", pos_tag="Noun", meaning_tag="technology")
        db.add_word("animal", pos_tag="Noun")
        db.add_word("fly", pos_tag="Verb")
        db.add_word("bark", pos_tag="Verb")
        
        # Add some incorrect relations we'll correct
        db.add_relation("python", "is_a", "animal")
        db.add_relation("robot", "capable_of", "fly")
    
    with Corrector("test_corrector.db") as corrector:
        # Test 1: Correction detection
        print("\n1. Testing correction detection...")
        is_corr = corrector.is_correction("That's wrong!")
        assert is_corr == True, "Should detect 'that's wrong' as correction"
        print("   ✓ Detects 'that's wrong'")
        
        is_corr = corrector.is_correction("You are incorrect.")
        assert is_corr == True, "Should detect 'incorrect' as correction"
        print("   ✓ Detects 'incorrect'")
        
        is_corr = corrector.is_correction("Python is not an animal.")
        assert is_corr == True, "Should detect 'is not' as correction"
        print("   ✓ Detects 'is not'")
        
        is_corr = corrector.is_correction("The sky is blue.")
        assert is_corr == False, "Should not detect normal statement as correction"
        print("   ✓ Doesn't false-positive on normal statements")
        
        # Test 2: Correcting is_a relation
        print("\n2. Testing is_a relation correction...")
        corrector.set_context("python", "Python is an animal", 
                            [{'relation_type': 'is_a', 'target_word': 'animal'}])
        result = corrector.process_correction("That's wrong! Python is not an animal.")
        print(f"   Input: 'That's wrong! Python is not an animal.'")
        print(f"   Response: {result['message']}")
        assert result['type'] == 'corrected', "Should successfully correct"
        
        # Verify it was removed
        with DatabaseHelper("test_corrector.db") as db:
            relations = db.get_relations("python", relation_type="is_a")
            animal_relation = [r for r in relations if r['target_word'] == 'animal']
            assert len(animal_relation) == 0, "Should have removed the incorrect relation"
        print("   ✓ Successfully corrected is_a relation")
        
        # Test 3: Correcting capable_of relation
        print("\n3. Testing capable_of relation correction...")
        corrector.set_context("robot", "Robot can fly",
                            [{'relation_type': 'capable_of', 'target_word': 'fly'}])
        result = corrector.process_correction("No, robots cannot fly.")
        print(f"   Input: 'No, robots cannot fly.'")
        print(f"   Response: {result['message']}")
        assert result['type'] == 'corrected', "Should successfully correct"
        
        # Verify it was removed
        with DatabaseHelper("test_corrector.db") as db:
            relations = db.get_relations("robot", relation_type="capable_of")
            fly_relation = [r for r in relations if r['target_word'] == 'fly']
            assert len(fly_relation) == 0, "Should have removed the incorrect capability"
        print("   ✓ Successfully corrected capable_of relation")
        
        # Test 4: Correcting meaning tag
        print("\n4. Testing meaning tag correction...")
        corrector.set_context("python", "Python is related to animals")
        result = corrector.process_correction("Wrong category! Python is related to technology.")
        print(f"   Input: 'Wrong category! Python is related to technology.'")
        print(f"   Response: {result['message']}")
        # Should at least provide clarification
        assert result['type'] in ['corrected', 'clarification_needed'], "Should handle meaning correction"
        print("   ✓ Handles meaning tag corrections")
        
        # Test 5: Deleting a word completely
        print("\n5. Testing word deletion...")
        result = corrector.delete_word("python")
        print(f"   Deleting word: 'python'")
        print(f"   Response: {result['message']}")
        assert result['type'] == 'deleted', "Should successfully delete"
        
        # Verify it was removed
        with DatabaseHelper("test_corrector.db") as db:
            word = db.get_word("python")
            assert word is None, "Word should be completely removed"
        print("   ✓ Successfully deleted word")
        
        # Test 6: No context correction
        print("\n6. Testing correction without context...")
        corrector.last_word = None
        result = corrector.process_correction("That's wrong!")
        print(f"   Input: 'That's wrong!' (no context)")
        print(f"   Response: {result['message']}")
        assert result['type'] == 'no_context', "Should indicate no context"
        print("   ✓ Handles no-context corrections appropriately")
    
    print("\n✓ All Corrector tests passed!")


def test_integration():
    """Test integration of Orator and Corrector."""
    print("\n=== Testing Integration ===")
    
    # Create test database
    with DatabaseHelper("test_integration.db") as db:
        db.initialize_database()
        
        # Add vocabulary
        db.add_word("elephant", pos_tag="Noun", meaning_tag="animal")
        db.add_word("animal", pos_tag="Noun")
        db.add_relation("elephant", "is_a", "animal")
    
    with Orator("test_integration.db") as orator, \
         Corrector("test_integration.db") as corrector:
        
        print("\n1. Testing full correction workflow...")
        
        # Step 1: Ask a question
        print("   User asks: 'What is elephant?'")
        result = orator.answer_question("What is elephant?")
        print(f"   Beari says: '{result['message']}'")
        
        # Set correction context
        corrector.set_context(
            word='elephant',
            statement=result['message'],
            relations=result.get('relations', [])
        )
        
        # Step 2: User says it's wrong (even though it's correct, for testing)
        print("   User says: 'That's wrong! Elephant is not an animal.'")
        correction_result = corrector.process_correction("That's wrong! Elephant is not an animal.")
        print(f"   Beari says: '{correction_result['message']}'")
        assert correction_result['type'] == 'corrected', "Should process correction"
        
        # Step 3: Ask again to verify correction
        print("   User asks again: 'What is elephant?'")
        result2 = orator.answer_question("What is elephant?")
        print(f"   Beari says: '{result2['message']}'")
        # Should not say "is a animal" anymore (the is_a relation was removed)
        # but "related to animal" from meaning_tag is still okay
        assert 'is a animal' not in result2['message'].lower(), \
               "Should not include the removed is_a relation"
        
        print("   ✓ Full correction workflow successful")
    
    print("\n✓ All integration tests passed!")


def cleanup_test_databases():
    """Remove test database files."""
    test_dbs = ["test_orator.db", "test_corrector.db", "test_integration.db"]
    for db_file in test_dbs:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"Cleaned up {db_file}")


def main():
    """Run all tests."""
    print("="*70)
    print("BEARI ORATOR & CORRECTOR TEST SUITE")
    print("="*70)
    
    try:
        test_orator()
        test_corrector()
        test_integration()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\nBeari's question answering and correction systems are working correctly!")
        print("You can now run 'python beari.py' to chat with Beari.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        print("\nCleaning up test databases...")
        cleanup_test_databases()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
