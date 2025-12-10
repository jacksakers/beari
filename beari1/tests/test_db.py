"""
Test Script for Beari Database Functions
Run this script to verify that all database operations work correctly.
"""

from db_helpers import DatabaseHelper
import os


def test_vocabulary_operations():
    """Test all vocabulary-related functions."""
    print("\n=== Testing Vocabulary Operations ===")
    
    with DatabaseHelper("test_beari.db") as db:
        db.initialize_database()
        
        # Test 1: Add a new word
        print("\n1. Testing add_word()...")
        word_id = db.add_word("elephant", pos_tag="Noun", meaning_tag="animal")
        print(f"   ✓ Added 'elephant' with ID: {word_id}")
        
        # Test 2: Add duplicate word (should return existing ID)
        print("\n2. Testing duplicate word handling...")
        duplicate_id = db.add_word("elephant", pos_tag="Noun", meaning_tag="animal")
        assert word_id == duplicate_id, "Duplicate word should return same ID"
        print(f"   ✓ Duplicate correctly handled, returned ID: {duplicate_id}")
        
        # Test 3: Get word information
        print("\n3. Testing get_word()...")
        word_info = db.get_word("elephant")
        print(f"   ✓ Retrieved: {word_info}")
        assert word_info['word'] == "elephant"
        assert word_info['pos_tag'] == "Noun"
        
        # Test 4: Check if word exists
        print("\n4. Testing word_exists()...")
        exists = db.word_exists("elephant")
        not_exists = db.word_exists("unicorn")
        assert exists == True
        assert not_exists == False
        print(f"   ✓ 'elephant' exists: {exists}")
        print(f"   ✓ 'unicorn' exists: {not_exists}")
        
        # Test 5: Update word information
        print("\n5. Testing update_word()...")
        db.update_word("elephant", meaning_tag="large_animal", is_plural=False)
        updated_word = db.get_word("elephant")
        assert updated_word['meaning_tag'] == "large_animal"
        print(f"   ✓ Updated 'elephant': {updated_word}")
        
        # Test 6: Get all words
        print("\n6. Testing get_all_words()...")
        db.add_word("giraffe", pos_tag="Noun", meaning_tag="animal")
        db.add_word("run", pos_tag="Verb")
        all_words = db.get_all_words()
        nouns_only = db.get_all_words(pos_tag="Noun")
        print(f"   ✓ Total words: {len(all_words)}")
        print(f"   ✓ Nouns only: {len(nouns_only)}")
        
    print("\n✓ All vocabulary tests passed!")


def test_relation_operations():
    """Test all relation-related functions."""
    print("\n=== Testing Relation Operations ===")
    
    with DatabaseHelper("test_beari.db") as db:
        # Add test words first
        db.add_word("dog", pos_tag="Noun", meaning_tag="animal")
        db.add_word("bark", pos_tag="Verb")
        db.add_word("animal", pos_tag="Noun")
        db.add_word("run", pos_tag="Verb")
        
        # Test 1: Add a relation
        print("\n1. Testing add_relation()...")
        rel_id = db.add_relation("dog", "capable_of", "bark")
        print(f"   ✓ Added relation with ID: {rel_id}")
        
        # Test 2: Add duplicate relation (should increment weight)
        print("\n2. Testing relation weight increment...")
        db.add_relation("dog", "capable_of", "bark")
        db.add_relation("dog", "capable_of", "bark")
        relations = db.get_relations("dog", "capable_of")
        bark_weight = next(r['weight'] for r in relations if r['target_word'] == 'bark')
        print(f"   ✓ Weight after 3 additions: {bark_weight}")
        assert bark_weight == 3, "Weight should be 3"
        
        # Test 3: Get relations
        print("\n3. Testing get_relations()...")
        db.add_relation("dog", "is_a", "animal")
        db.add_relation("dog", "capable_of", "run")
        all_relations = db.get_relations("dog")
        capable_relations = db.get_relations("dog", "capable_of")
        print(f"   ✓ All relations from 'dog': {len(all_relations)}")
        print(f"   ✓ 'capable_of' relations: {len(capable_relations)}")
        for rel in all_relations:
            print(f"      - dog {rel['relation_type']} {rel['target_word']} (weight: {rel['weight']})")
        
        # Test 4: Get reverse relations
        print("\n4. Testing get_reverse_relations()...")
        reverse_relations = db.get_reverse_relations("animal")
        print(f"   ✓ Relations pointing to 'animal': {len(reverse_relations)}")
        for rel in reverse_relations:
            print(f"      - {rel['source_word']} {rel['relation_type']} animal")
        
        # Test 5: Get weighted relations
        print("\n5. Testing get_weighted_relations()...")
        weighted = db.get_weighted_relations("dog", "capable_of")
        print(f"   ✓ Weighted relations: {weighted}")
        
    print("\n✓ All relation tests passed!")


def test_statistics():
    """Test database statistics."""
    print("\n=== Testing Database Statistics ===")
    
    with DatabaseHelper("test_beari.db") as db:
        stats = db.get_stats()
        print(f"\n   Total vocabulary: {stats['vocabulary_size']}")
        print(f"   Total relations: {stats['total_relations']}")
        print(f"   Relation types: {stats['relation_types']}")
        print("\n✓ Statistics retrieved successfully!")


def cleanup_test_database():
    """Remove the test database file."""
    if os.path.exists("test_beari.db"):
        os.remove("test_beari.db")
        print("\n✓ Test database cleaned up.")


def main():
    """Run all tests."""
    print("="*60)
    print("BEARI DATABASE TEST SUITE")
    print("="*60)
    
    try:
        test_vocabulary_operations()
        test_relation_operations()
        test_statistics()
        
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
