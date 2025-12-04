"""
Database Schema for Beari AI
Defines the SQLite table structures for vocabulary and word relations.
"""

# SQL statement to create the Vocabulary table
CREATE_VOCABULARY_TABLE = """
CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,
    pos_tag TEXT,
    meaning_tag TEXT,
    is_plural INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# SQL statement to create the Relations table
CREATE_RELATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_a_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    word_b_id INTEGER NOT NULL,
    weight INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_a_id) REFERENCES vocabulary(id),
    FOREIGN KEY (word_b_id) REFERENCES vocabulary(id),
    UNIQUE(word_a_id, relation_type, word_b_id)
);
"""

# SQL statement to create an index for faster word lookups
CREATE_WORD_INDEX = """
CREATE INDEX IF NOT EXISTS idx_word ON vocabulary(word);
"""

# SQL statement to create an index for faster relation lookups
CREATE_RELATION_INDEX = """
CREATE INDEX IF NOT EXISTS idx_relations ON relations(word_a_id, relation_type);
"""

# All table creation statements in order
SCHEMA_STATEMENTS = [
    CREATE_VOCABULARY_TABLE,
    CREATE_RELATIONS_TABLE,
    CREATE_WORD_INDEX,
    CREATE_RELATION_INDEX
]
