"""
Database schema for Beari3
Stores conversational units and learned patterns
"""

import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path="beari3.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize the database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Vocabulary table - stores known words with their POS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                part_of_speech TEXT NOT NULL,
                definition TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Conversational Units - stores training examples
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ConversationalUnits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_raw TEXT NOT NULL,
                prompt_structure TEXT NOT NULL,
                response_raw TEXT NOT NULL,
                response_strategy TEXT,
                key_words TEXT,
                pattern_signature TEXT,
                response_template TEXT,
                tense TEXT,
                sentiment_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Pattern Map - stores abstract patterns learned from training
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS PatternMap (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_pattern TEXT NOT NULL,
                response_pattern TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Semantic Categories - maps words to abstract categories for generalization
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS SemanticCategories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")
