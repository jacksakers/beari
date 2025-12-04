# Beari AI Database System

This directory contains the SQLite database implementation for Beari AI, providing structured storage for vocabulary and word relations.

## Files Overview

- **`db_schema.py`** - Defines the database table structures (Vocabulary & Relations)
- **`db_helpers.py`** - Core database operations class with all helper functions
- **`init_db.py`** - Initialization script to set up database with sample data
- **`test_db.py`** - Comprehensive test suite for all database functions

## Quick Start

### 1. Initialize the Database

```bash
python init_db.py
```

This creates `beari.db` with the necessary tables and sample vocabulary.

### 2. Run Tests

```bash
python test_db.py
```

Verifies all database operations work correctly.

## Database Schema

### Vocabulary Table
Stores individual words with their linguistic properties:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| word | TEXT | The word (unique, lowercase) |
| pos_tag | TEXT | Part of Speech (Noun, Verb, Adjective, etc.) |
| meaning_tag | TEXT | Context category (animal, technology, emotion, etc.) |
| is_plural | INTEGER | 0 for singular, 1 for plural |
| created_at | TIMESTAMP | When the word was added |

### Relations Table
Stores connections between words:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| word_a_id | INTEGER | Source word ID (foreign key) |
| relation_type | TEXT | Type of relationship (is_a, capable_of, part_of, follows) |
| word_b_id | INTEGER | Target word ID (foreign key) |
| weight | INTEGER | Strength of connection (increases with repetition) |
| created_at | TIMESTAMP | When the relation was added |

## Usage Examples

### Basic Usage with Context Manager

```python
from db_helpers import DatabaseHelper

# Context manager automatically handles connection opening/closing
with DatabaseHelper() as db:
    # Add a word
    db.add_word("python", pos_tag="Noun", meaning_tag="technology")
    
    # Check if word exists
    if db.word_exists("python"):
        print("Word found!")
    
    # Get word information
    word_info = db.get_word("python")
    print(word_info)
```

### Vocabulary Operations

```python
with DatabaseHelper() as db:
    # Add words
    db.add_word("dog", pos_tag="Noun", meaning_tag="animal")
    db.add_word("run", pos_tag="Verb")
    db.add_word("fast", pos_tag="Adjective", meaning_tag="quality")
    
    # Update word properties
    db.update_word("dog", meaning_tag="pet")
    
    # Get specific word
    dog_info = db.get_word("dog")
    
    # Get all nouns
    all_nouns = db.get_all_words(pos_tag="Noun")
    
    # Check existence
    exists = db.word_exists("cat")
```

### Relation Operations

```python
with DatabaseHelper() as db:
    # First ensure words exist
    db.add_word("dog", pos_tag="Noun", meaning_tag="animal")
    db.add_word("bark", pos_tag="Verb")
    db.add_word("animal", pos_tag="Noun")
    
    # Add relations
    db.add_relation("dog", "capable_of", "bark")
    db.add_relation("dog", "is_a", "animal")
    
    # Adding the same relation increases its weight
    db.add_relation("dog", "capable_of", "bark")  # weight = 2
    db.add_relation("dog", "capable_of", "bark")  # weight = 3
    
    # Get all relations from a word
    all_relations = db.get_relations("dog")
    
    # Get specific relation type
    capabilities = db.get_relations("dog", relation_type="capable_of")
    
    # Get reverse relations (what points to this word)
    reverse = db.get_reverse_relations("animal")
    
    # Get weighted relations for probability selection
    weighted = db.get_weighted_relations("dog", "capable_of")
    # Returns: [('bark', 3), ('run', 1)]
```

### Statistics

```python
with DatabaseHelper() as db:
    stats = db.get_stats()
    print(f"Vocabulary size: {stats['vocabulary_size']}")
    print(f"Total relations: {stats['total_relations']}")
    print(f"Relation types: {stats['relation_types']}")
```

## Common Relation Types

- **`is_a`** - Defines hierarchy (e.g., "dog is_a animal")
- **`capable_of`** - What actions a word can perform (e.g., "dog capable_of bark")
- **`part_of`** - Component relationships (e.g., "wheel part_of car")
- **`follows`** - Sequential word patterns for sentence generation

## API Reference

### DatabaseHelper Class

#### Constructor
- `__init__(db_path="beari.db")` - Initialize with custom database path

#### Connection Management
- `connect()` - Establish database connection
- `close()` - Close database connection
- Context manager support: `with DatabaseHelper() as db:`

#### Vocabulary Methods
- `add_word(word, pos_tag=None, meaning_tag=None, is_plural=False)` → int
- `get_word(word)` → Dict | None
- `get_word_id(word)` → int | None
- `update_word(word, pos_tag=None, meaning_tag=None, is_plural=None)` → bool
- `word_exists(word)` → bool
- `get_all_words(pos_tag=None)` → List[Dict]

#### Relation Methods
- `add_relation(word_a, relation_type, word_b)` → int | None
- `get_relations(word, relation_type=None)` → List[Dict]
- `get_reverse_relations(word, relation_type=None)` → List[Dict]
- `get_weighted_relations(word, relation_type, min_weight=1)` → List[Tuple[str, int]]

#### Utility Methods
- `initialize_database()` - Create tables if they don't exist
- `get_stats()` → Dict
- `clear_database()` - ⚠️ Delete all data

## Design Principles

1. **Modular Architecture** - Each component has a single responsibility
2. **Type Safety** - Type hints throughout for better IDE support
3. **Comprehensive Comments** - Every function documented with purpose and parameters
4. **Error Handling** - Graceful handling of duplicates and missing data
5. **Weighted Relations** - Natural probability through repetition counting
6. **Context Manager Support** - Automatic resource cleanup

## Next Steps

This database system is ready for integration with:
- **The Listener** - Parse user input and populate vocabulary/relations
- **The Querist** - Ask questions about unknown words
- **The Orator** - Generate grammatically correct sentences using templates

See `main_idea.txt` for the complete architecture plan.
