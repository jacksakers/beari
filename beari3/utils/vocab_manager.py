"""
Vocabulary Manager
Handles tracking known/unknown words and provides user-friendly POS assignment
"""

import sqlite3


class VocabularyManager:
    def __init__(self, db):
        self.db = db
    
    def is_word_known(self, word):
        """Check if a word exists in the vocabulary"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Vocabulary WHERE LOWER(word) = LOWER(?)", (word,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_unknown_words(self, words):
        """Filter a list of words to return only unknown ones"""
        unknown = []
        for word in words:
            if not self.is_word_known(word):
                unknown.append(word)
        return unknown
    
    def add_word_interactive(self, word):
        """
        Interactively add a word to vocabulary with user-friendly POS selection
        """
        print(f"\n🆕 Unknown word detected: '{word}'")
        print("\nWhat part of speech is this word?")
        print("  1. Noun (person, place, thing)")
        print("  2. Verb (action word)")
        print("  3. Adjective (describes a noun)")
        print("  4. Adverb (describes a verb)")
        print("  5. Pronoun (I, you, he, she, it, etc.)")
        print("  6. Preposition (in, on, at, etc.)")
        print("  7. Conjunction (and, but, or, etc.)")
        print("  8. Interjection (wow, cool, etc.)")
        print("  9. Other")
        
        pos_map = {
            "1": "NOUN",
            "2": "VERB",
            "3": "ADJ",
            "4": "ADV",
            "5": "PRON",
            "6": "ADP",
            "7": "CCONJ",
            "8": "INTJ",
            "9": "OTHER"
        }
        
        while True:
            choice = input("\nEnter number (1-9): ").strip()
            if choice in pos_map:
                pos = pos_map[choice]
                break
            print("Invalid choice. Please enter a number from 1-9.")
        
        definition = input(f"Optional - Enter a definition for '{word}' (or press Enter to skip): ").strip()
        
        self.add_word(word, pos, definition if definition else None)
        print(f"✓ Added '{word}' as {pos}")
    
    def add_word(self, word, pos, definition=None):
        """Add a word to the vocabulary database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Vocabulary (word, part_of_speech, definition)
                VALUES (?, ?, ?)
            """, (word, pos, definition))
            conn.commit()
        except sqlite3.IntegrityError:
            # Word already exists
            pass
        finally:
            conn.close()
    
    def get_word_info(self, word):
        """Get POS and definition for a word"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT word, part_of_speech, definition
            FROM Vocabulary
            WHERE LOWER(word) = LOWER(?)
        """, (word,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "word": result[0],
                "pos": result[1],
                "definition": result[2]
            }
        return None
    
    def seed_common_words(self):
        """Seed the database with common English words to reduce initial friction"""
        common_words = [
            # Pronouns
            ("I", "PRON"), ("you", "PRON"), ("he", "PRON"), ("she", "PRON"), 
            ("it", "PRON"), ("we", "PRON"), ("they", "PRON"), ("me", "PRON"),
            ("my", "PRON"), ("your", "PRON"), ("his", "PRON"), ("her", "PRON"),
            
            # Common verbs
            ("is", "VERB"), ("are", "VERB"), ("was", "VERB"), ("were", "VERB"),
            ("am", "VERB"), ("be", "VERB"), ("been", "VERB"), ("being", "VERB"),
            ("have", "VERB"), ("has", "VERB"), ("had", "VERB"), ("do", "VERB"),
            ("does", "VERB"), ("did", "VERB"), ("will", "VERB"), ("would", "VERB"),
            ("can", "VERB"), ("could", "VERB"), ("should", "VERB"), ("may", "VERB"),
            
            # Articles
            ("a", "DET"), ("an", "DET"), ("the", "DET"),
            
            # Prepositions
            ("in", "ADP"), ("on", "ADP"), ("at", "ADP"), ("to", "ADP"),
            ("for", "ADP"), ("with", "ADP"), ("from", "ADP"), ("of", "ADP"),
            
            # Conjunctions
            ("and", "CCONJ"), ("but", "CCONJ"), ("or", "CCONJ"), ("so", "CCONJ"),
            
            # Common adverbs
            ("just", "ADV"), ("very", "ADV"), ("really", "ADV"), ("too", "ADV"),
            ("also", "ADV"), ("now", "ADV"), ("then", "ADV"),
            
            # Common adjectives
            ("good", "ADJ"), ("bad", "ADJ"), ("big", "ADJ"), ("small", "ADJ"),
            ("new", "ADJ"), ("old", "ADJ"), ("great", "ADJ"),
            
            # Common interjections
            ("cool", "INTJ"), ("wow", "INTJ"), ("oh", "INTJ"), ("hey", "INTJ"),
        ]
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        for word, pos in common_words:
            try:
                cursor.execute("""
                    INSERT INTO Vocabulary (word, part_of_speech)
                    VALUES (?, ?)
                """, (word, pos))
            except sqlite3.IntegrityError:
                # Already exists, skip
                pass
        
        conn.commit()
        conn.close()
        print(f"✓ Seeded {len(common_words)} common words")
