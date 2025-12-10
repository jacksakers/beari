"""
Semantic Category Manager
Handles mapping words to abstract categories for generalization
"""

import sqlite3


class SemanticCategoryManager:
    def __init__(self, db):
        self.db = db
        self._seed_common_categories()
    
    def get_category(self, word):
        """Get the semantic category for a word"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, subcategory
            FROM SemanticCategories
            WHERE LOWER(word) = LOWER(?)
        """, (word,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"category": result[0], "subcategory": result[1]}
        return None
    
    def add_category_interactive(self, word):
        """
        Interactively add a semantic category for a word
        """
        print(f"\n🏷️  What category does '{word}' belong to?")
        print("\nCommon categories:")
        print("  1. FOOD (pizza, burger, curry, etc.)")
        print("  2. ACTIVITY (walk, run, exercise, etc.)")
        print("  3. MEDIA (movie, book, song, etc.)")
        print("  4. PLACE (park, store, home, etc.)")
        print("  5. PERSON (friend, family, colleague, etc.)")
        print("  6. OBJECT (phone, car, computer, etc.)")
        print("  7. EMOTION (happy, sad, angry, etc.)")
        print("  8. STATE (tired, hungry, excited, etc.)")
        print("  9. ACTION_CREATION (cook, build, make, etc.)")
        print("  10. ACTION_CONSUMPTION (eat, drink, watch, etc.)")
        print("  11. ACTION_MOVEMENT (walk, run, drive, etc.)")
        print("  12. Custom (enter your own)")
        
        category_map = {
            "1": "FOOD",
            "2": "ACTIVITY",
            "3": "MEDIA",
            "4": "PLACE",
            "5": "PERSON",
            "6": "OBJECT",
            "7": "EMOTION",
            "8": "STATE",
            "9": "ACTION_CREATION",
            "10": "ACTION_CONSUMPTION",
            "11": "ACTION_MOVEMENT"
        }
        
        while True:
            choice = input("\nEnter number (1-12): ").strip()
            if choice in category_map:
                category = category_map[choice]
                break
            elif choice == "12":
                category = input("Enter custom category (UPPERCASE): ").strip().upper()
                if category:
                    break
            print("Invalid choice. Please try again.")
        
        subcategory = input(f"Optional - Enter subcategory for '{word}' (or press Enter to skip): ").strip()
        
        self.add_category(word, category, subcategory if subcategory else None)
        print(f"✓ Added '{word}' → {category}" + (f" ({subcategory})" if subcategory else ""))
    
    def add_category(self, word, category, subcategory=None):
        """Add a word-category mapping to the database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO SemanticCategories (word, category, subcategory)
                VALUES (?, ?, ?)
            """, (word, category, subcategory))
            conn.commit()
        except sqlite3.IntegrityError:
            # Word already exists, update it
            cursor.execute("""
                UPDATE SemanticCategories
                SET category = ?, subcategory = ?
                WHERE LOWER(word) = LOWER(?)
            """, (category, subcategory, word))
            conn.commit()
        finally:
            conn.close()
    
    def get_all_categories(self):
        """Get all unique categories"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM SemanticCategories ORDER BY category")
        results = cursor.fetchall()
        conn.close()
        return [r[0] for r in results]
    
    def get_words_in_category(self, category):
        """Get all words in a specific category"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT word, subcategory
            FROM SemanticCategories
            WHERE category = ?
            ORDER BY word
        """, (category,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def _seed_common_categories(self):
        """Seed database with common word-category mappings"""
        common_mappings = [
            # Foods
            ("curry", "FOOD", "meal"),
            ("pizza", "FOOD", "meal"),
            ("burger", "FOOD", "meal"),
            ("taco", "FOOD", "meal"),
            ("sandwich", "FOOD", "meal"),
            ("salad", "FOOD", "meal"),
            ("pasta", "FOOD", "meal"),
            ("sushi", "FOOD", "meal"),
            
            # Activities
            ("walk", "ACTIVITY", "movement"),
            ("run", "ACTIVITY", "movement"),
            ("jog", "ACTIVITY", "movement"),
            ("exercise", "ACTIVITY", "physical"),
            ("workout", "ACTIVITY", "physical"),
            ("swim", "ACTIVITY", "physical"),
            ("hike", "ACTIVITY", "movement"),
            
            # Media
            ("movie", "MEDIA", "video"),
            ("film", "MEDIA", "video"),
            ("book", "MEDIA", "text"),
            ("song", "MEDIA", "audio"),
            ("show", "MEDIA", "video"),
            ("video", "MEDIA", "video"),
            ("podcast", "MEDIA", "audio"),
            
            # Places
            ("park", "PLACE", "outdoor"),
            ("store", "PLACE", "indoor"),
            ("mall", "PLACE", "indoor"),
            ("gym", "PLACE", "indoor"),
            ("beach", "PLACE", "outdoor"),
            ("restaurant", "PLACE", "indoor"),
            ("home", "PLACE", "indoor"),
            
            # Actions - Creation
            ("cook", "ACTION_CREATION", None),
            ("cooked", "ACTION_CREATION", None),
            ("make", "ACTION_CREATION", None),
            ("made", "ACTION_CREATION", None),
            ("build", "ACTION_CREATION", None),
            ("built", "ACTION_CREATION", None),
            ("create", "ACTION_CREATION", None),
            ("created", "ACTION_CREATION", None),
            
            # Actions - Consumption
            ("eat", "ACTION_CONSUMPTION", None),
            ("ate", "ACTION_CONSUMPTION", None),
            ("drink", "ACTION_CONSUMPTION", None),
            ("drank", "ACTION_CONSUMPTION", None),
            ("watch", "ACTION_CONSUMPTION", None),
            ("watched", "ACTION_CONSUMPTION", None),
            ("read", "ACTION_CONSUMPTION", None),
            
            # Actions - Movement
            ("go", "ACTION_MOVEMENT", None),
            ("went", "ACTION_MOVEMENT", None),
            ("travel", "ACTION_MOVEMENT", None),
            ("traveled", "ACTION_MOVEMENT", None),
            ("visit", "ACTION_MOVEMENT", None),
            ("visited", "ACTION_MOVEMENT", None),
            
            # Emotions/States
            ("happy", "EMOTION", "positive"),
            ("sad", "EMOTION", "negative"),
            ("angry", "EMOTION", "negative"),
            ("excited", "EMOTION", "positive"),
            ("tired", "STATE", "physical"),
            ("hungry", "STATE", "physical"),
        ]
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        for word, category, subcategory in common_mappings:
            try:
                cursor.execute("""
                    INSERT INTO SemanticCategories (word, category, subcategory)
                    VALUES (?, ?, ?)
                """, (word, category, subcategory))
            except sqlite3.IntegrityError:
                # Already exists, skip
                pass
        
        conn.commit()
        conn.close()
