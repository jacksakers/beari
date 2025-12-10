"""
Database Helper Functions for Beari AI
Provides core database operations for vocabulary and relations management.
"""

import sqlite3
import os
import sys
from typing import Optional, List, Dict, Tuple

# Handle imports for both direct execution and package import
try:
    from .db_schema import SCHEMA_STATEMENTS
except ImportError:
    # Add parent directory to path for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from db.db_schema import SCHEMA_STATEMENTS


class DatabaseHelper:
    """Manages all database operations for Beari's vocabulary and relations."""
    
    def __init__(self, db_path: str = "beari.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to the database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry: connect to database."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit: close database connection."""
        self.close()
    
    def initialize_database(self):
        """
        Create all necessary tables and indexes if they don't exist.
        This is safe to call multiple times.
        """
        for statement in SCHEMA_STATEMENTS:
            self.cursor.execute(statement)
        self.conn.commit()
        print("Database initialized successfully.")
    
    # ==================== VOCABULARY OPERATIONS ====================
    
    def add_word(self, word: str, pos_tag: Optional[str] = None, 
                 meaning_tag: Optional[str] = None, is_plural: bool = False) -> int:
        """
        Add a new word to the vocabulary table.
        
        Args:
            word: The word string (will be stored in lowercase)
            pos_tag: Part of Speech (e.g., 'Noun', 'Verb', 'Adjective')
            meaning_tag: Context category (e.g., 'animal', 'technology', 'emotion')
            is_plural: Whether the word is plural form
        
        Returns:
            The ID of the newly inserted word, or existing word ID if already present
        """
        word = word.lower()
        
        try:
            self.cursor.execute("""
                INSERT INTO vocabulary (word, pos_tag, meaning_tag, is_plural)
                VALUES (?, ?, ?, ?)
            """, (word, pos_tag, meaning_tag, 1 if is_plural else 0))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Word already exists, return its ID
            return self.get_word_id(word)
    
    def get_word(self, word: str) -> Optional[Dict]:
        """
        Retrieve a word's information from the vocabulary.
        
        Args:
            word: The word to look up
        
        Returns:
            Dictionary with word info, or None if not found
        """
        word = word.lower()
        self.cursor.execute("""
            SELECT id, word, pos_tag, meaning_tag, is_plural, created_at
            FROM vocabulary
            WHERE word = ?
        """, (word,))
        
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_word_id(self, word: str) -> Optional[int]:
        """
        Get the ID of a word without retrieving full information.
        
        Args:
            word: The word to look up
        
        Returns:
            Word ID or None if not found
        """
        word = word.lower()
        self.cursor.execute("SELECT id FROM vocabulary WHERE word = ?", (word,))
        row = self.cursor.fetchone()
        return row[0] if row else None
    
    def update_word(self, word: str, pos_tag: Optional[str] = None,
                   meaning_tag: Optional[str] = None, is_plural: Optional[bool] = None) -> bool:
        """
        Update an existing word's information.
        
        Args:
            word: The word to update
            pos_tag: New Part of Speech (if provided)
            meaning_tag: New meaning tag (if provided)
            is_plural: New plural status (if provided)
        
        Returns:
            True if update successful, False if word not found
        """
        word = word.lower()
        word_id = self.get_word_id(word)
        
        if not word_id:
            return False
        
        # Build dynamic update query based on provided parameters
        updates = []
        params = []
        
        if pos_tag is not None:
            updates.append("pos_tag = ?")
            params.append(pos_tag)
        
        if meaning_tag is not None:
            updates.append("meaning_tag = ?")
            params.append(meaning_tag)
        
        if is_plural is not None:
            updates.append("is_plural = ?")
            params.append(1 if is_plural else 0)
        
        if updates:
            params.append(word_id)
            query = f"UPDATE vocabulary SET {', '.join(updates)} WHERE id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
        
        return True
    
    def word_exists(self, word: str) -> bool:
        """
        Check if a word exists in the vocabulary.
        
        Args:
            word: The word to check
        
        Returns:
            True if word exists, False otherwise
        """
        return self.get_word_id(word) is not None
    
    def get_all_words(self, pos_tag: Optional[str] = None) -> List[Dict]:
        """
        Retrieve all words from vocabulary, optionally filtered by part of speech.
        
        Args:
            pos_tag: Optional filter by Part of Speech
        
        Returns:
            List of dictionaries containing word information
        """
        if pos_tag:
            self.cursor.execute("""
                SELECT id, word, pos_tag, meaning_tag, is_plural
                FROM vocabulary
                WHERE pos_tag = ?
                ORDER BY word
            """, (pos_tag,))
        else:
            self.cursor.execute("""
                SELECT id, word, pos_tag, meaning_tag, is_plural
                FROM vocabulary
                ORDER BY word
            """)
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== RELATION OPERATIONS ====================
    
    def add_relation(self, word_a: str, relation_type: str, word_b: str) -> Optional[int]:
        """
        Add or strengthen a relation between two words.
        
        Args:
            word_a: The first word (source)
            relation_type: Type of relation (e.g., 'is_a', 'capable_of', 'part_of', 'follows')
            word_b: The second word (target)
        
        Returns:
            The relation ID if successful, None if either word doesn't exist
        """
        word_a_id = self.get_word_id(word_a)
        word_b_id = self.get_word_id(word_b)
        
        if not word_a_id or not word_b_id:
            return None
        
        try:
            # Try to insert new relation
            self.cursor.execute("""
                INSERT INTO relations (word_a_id, relation_type, word_b_id, weight)
                VALUES (?, ?, ?, 1)
            """, (word_a_id, relation_type, word_b_id))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Relation already exists, increment its weight
            self.cursor.execute("""
                UPDATE relations
                SET weight = weight + 1
                WHERE word_a_id = ? AND relation_type = ? AND word_b_id = ?
            """, (word_a_id, relation_type, word_b_id))
            self.conn.commit()
            
            # Return the existing relation ID
            self.cursor.execute("""
                SELECT id FROM relations
                WHERE word_a_id = ? AND relation_type = ? AND word_b_id = ?
            """, (word_a_id, relation_type, word_b_id))
            row = self.cursor.fetchone()
            return row[0] if row else None
    
    def get_relations(self, word: str, relation_type: Optional[str] = None) -> List[Dict]:
        """
        Get all relations where the word is the source.
        
        Args:
            word: The source word
            relation_type: Optional filter by relation type
        
        Returns:
            List of dictionaries containing relation information
        """
        word_id = self.get_word_id(word)
        if not word_id:
            return []
        
        if relation_type:
            query = """
                SELECT r.id, r.relation_type, v.word as target_word, 
                       v.pos_tag, v.meaning_tag, r.weight
                FROM relations r
                JOIN vocabulary v ON r.word_b_id = v.id
                WHERE r.word_a_id = ? AND r.relation_type = ?
                ORDER BY r.weight DESC, v.word
            """
            self.cursor.execute(query, (word_id, relation_type))
        else:
            query = """
                SELECT r.id, r.relation_type, v.word as target_word,
                       v.pos_tag, v.meaning_tag, r.weight
                FROM relations r
                JOIN vocabulary v ON r.word_b_id = v.id
                WHERE r.word_a_id = ?
                ORDER BY r.weight DESC, v.word
            """
            self.cursor.execute(query, (word_id,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_reverse_relations(self, word: str, relation_type: Optional[str] = None) -> List[Dict]:
        """
        Get all relations where the word is the target.
        
        Args:
            word: The target word
            relation_type: Optional filter by relation type
        
        Returns:
            List of dictionaries containing relation information
        """
        word_id = self.get_word_id(word)
        if not word_id:
            return []
        
        if relation_type:
            query = """
                SELECT r.id, r.relation_type, v.word as source_word,
                       v.pos_tag, v.meaning_tag, r.weight
                FROM relations r
                JOIN vocabulary v ON r.word_a_id = v.id
                WHERE r.word_b_id = ? AND r.relation_type = ?
                ORDER BY r.weight DESC, v.word
            """
            self.cursor.execute(query, (word_id, relation_type))
        else:
            query = """
                SELECT r.id, r.relation_type, v.word as source_word,
                       v.pos_tag, v.meaning_tag, r.weight
                FROM relations r
                JOIN vocabulary v ON r.word_a_id = v.id
                WHERE r.word_b_id = ?
                ORDER BY r.weight DESC, v.word
            """
            self.cursor.execute(query, (word_id,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_weighted_relations(self, word: str, relation_type: str, 
                              min_weight: int = 1) -> List[Tuple[str, int]]:
        """
        Get relations with their weights for probabilistic selection.
        
        Args:
            word: The source word
            relation_type: Type of relation to filter
            min_weight: Minimum weight threshold
        
        Returns:
            List of tuples (target_word, weight)
        """
        word_id = self.get_word_id(word)
        if not word_id:
            return []
        
        self.cursor.execute("""
            SELECT v.word, r.weight
            FROM relations r
            JOIN vocabulary v ON r.word_b_id = v.id
            WHERE r.word_a_id = ? AND r.relation_type = ? AND r.weight >= ?
            ORDER BY r.weight DESC
        """, (word_id, relation_type, min_weight))
        
        return [(row[0], row[1]) for row in self.cursor.fetchall()]
    
    # ==================== STATISTICS ====================
    
    def get_stats(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with vocabulary size and relation counts
        """
        self.cursor.execute("SELECT COUNT(*) FROM vocabulary")
        vocab_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM relations")
        relation_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(DISTINCT relation_type) FROM relations")
        relation_types = self.cursor.fetchone()[0]
        
        return {
            'vocabulary_size': vocab_count,
            'total_relations': relation_count,
            'relation_types': relation_types
        }
    
    def clear_database(self):
        """
        WARNING: Delete all data from the database.
        Use with caution - this cannot be undone!
        """
        self.cursor.execute("DELETE FROM relations")
        self.cursor.execute("DELETE FROM vocabulary")
        self.conn.commit()
        print("Database cleared.")
