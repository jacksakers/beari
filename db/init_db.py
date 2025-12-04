"""
Database Initialization Script for Beari AI
Run this script to set up the database for the first time.
"""

from db_helpers import DatabaseHelper


def main():
    """Initialize the Beari database with tables and sample data."""
    
    print("=== Beari Database Initialization ===\n")
    
    # Create database connection and initialize tables
    with DatabaseHelper() as db:
        db.initialize_database()
        
        # Add some sample words to get started
        print("\nAdding sample vocabulary...")
        
        # Sample nouns
        db.add_word("dog", pos_tag="Noun", meaning_tag="animal")
        db.add_word("cat", pos_tag="Noun", meaning_tag="animal")
        db.add_word("robot", pos_tag="Noun", meaning_tag="technology")
        db.add_word("python", pos_tag="Noun", meaning_tag="technology")
        db.add_word("language", pos_tag="Noun", meaning_tag="technology")
        db.add_word("love", pos_tag="Noun", meaning_tag="emotion")
        db.add_word("feeling", pos_tag="Noun", meaning_tag="emotion")
        db.add_word("emotion", pos_tag="Noun", meaning_tag="emotion")
        
        # Sample verbs
        db.add_word("is", pos_tag="Verb")
        db.add_word("run", pos_tag="Verb")
        db.add_word("chase", pos_tag="Verb")
        db.add_word("calculate", pos_tag="Verb")
        db.add_word("learn", pos_tag="Verb")
        db.add_word("think", pos_tag="Verb")
        
        # Sample adjectives
        db.add_word("friendly", pos_tag="Adjective", meaning_tag="personality")
        db.add_word("intelligent", pos_tag="Adjective", meaning_tag="personality")
        db.add_word("fast", pos_tag="Adjective", meaning_tag="quality")
        db.add_word("easy", pos_tag="Adjective", meaning_tag="quality")
        
        print("Sample vocabulary added.")
        
        # Add some sample relations
        print("\nAdding sample relations...")
        
        # Define relationships
        db.add_relation("python", "is_a", "language")
        db.add_relation("robot", "is_a", "machine")
        db.add_relation("dog", "capable_of", "run")
        db.add_relation("dog", "capable_of", "chase")
        db.add_relation("cat", "capable_of", "run")
        db.add_relation("robot", "capable_of", "calculate")
        db.add_relation("robot", "capable_of", "learn")
        db.add_relation("love", "is_a", "feeling")
        db.add_relation("feeling", "is_a", "emotion")
        
        print("Sample relations added.")
        
        # Display statistics
        print("\n" + "="*50)
        stats = db.get_stats()
        print(f"Database initialized successfully!")
        print(f"Total words: {stats['vocabulary_size']}")
        print(f"Total relations: {stats['total_relations']}")
        print(f"Relation types: {stats['relation_types']}")
        print("="*50)
        
        print("\n✓ Database is ready!")
        print("You can now use the database helper functions in your code.")


if __name__ == "__main__":
    main()
