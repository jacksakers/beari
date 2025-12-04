# Beari Listener Mode - Parser & Question Generator

This implements **Mode A: The Listener** from the design document - continuous learning from user input.

## Components

### 1. **Parser** (`parser.py`)
Tokenizes user input and identifies unknown words by checking the database.

**Key Functions:**
- `tokenize(text)` - Splits text into words
- `identify_unknown_words(tokens)` - Finds words not in database
- `parse_sentence(text)` - Full parsing pipeline
- `get_context_words(tokens, word)` - Gets surrounding words for context
- `analyze_sentence_structure(tokens)` - Identifies nouns, verbs, adjectives

### 2. **Question Generator** (`question_generator.py`)
Generates intelligent, context-aware questions about unknown words.

**Key Functions:**
- `generate_question(word, context)` - Creates appropriate question
- `parse_user_response(response)` - Extracts POS and meaning tags from answers
- `generate_confirmation(word, pos_tag, meaning_tag)` - Creates learning confirmation

**Question Types:**
- Noun questions: "Is 'X' a person, place, or thing?"
- Verb questions: "Is 'X' an action?"
- Adjective questions: "Does 'X' describe something?"
- Context-aware questions based on surrounding words

### 3. **Listener** (`listener.py`)
Orchestrates the learning workflow - integrates parser and question generator.

**Key Functions:**
- `process_input(user_input)` - Main processing pipeline
- `learn_from_sentence(sentence)` - Complete learning cycle
- `get_vocabulary_stats()` - Get current vocabulary size

**State Management:**
- Tracks whether waiting for answer about unknown word
- Stores pending word and context during Q&A
- Updates database with learned words and relations

## Usage Examples

### Interactive Mode

```bash
python listener.py
```

This launches an interactive session where you can chat with Beari and it will ask about unknown words.

### Programmatic Usage

```python
from listener import Listener

with Listener() as listener:
    # First input with unknown word
    result = listener.process_input("The capybara is cute")
    print(result['question'])  # Beari asks: "What is 'capybara'?"
    
    # Answer the question
    result = listener.process_input("It's an animal from South America")
    print(result['message'])  # Beari confirms learning
    
    # Check vocabulary growth
    stats = listener.get_vocabulary_stats()
    print(f"Words learned: {stats['vocabulary_size']}")
```

### Parser Only

```python
from db.db_helpers import DatabaseHelper
from parser import Parser

with DatabaseHelper() as db:
    parser = Parser(db)
    
    # Parse a sentence
    result = parser.parse_sentence("The robot calculates data")
    print(f"Known: {result['known_words']}")
    print(f"Unknown: {result['unknown_words']}")
```

### Question Generator Only

```python
from question_generator import QuestionGenerator

qgen = QuestionGenerator()

# Generate contextual question
context = {'prev_word': 'the', 'next_word': 'is'}
question = qgen.generate_question("elephant", context)
print(question)  # "What is 'elephant'? Is it a person, place, or thing?"

# Parse user response
response = "It's an animal"
parsed = qgen.parse_user_response(response)
print(parsed)  # {'pos_tag': 'Noun', 'meaning_tag': 'animal'}
```

## Testing

Run the comprehensive test suite:

```bash
python tests\test_listener.py
```

This tests:
- Parser tokenization and unknown word detection
- Question generation with different contexts
- Full learning workflow with database updates
- Integration of all components

## How It Works

1. **User inputs sentence** → Parser tokenizes and checks database
2. **Unknown words found** → Question Generator creates contextual question
3. **Listener enters learning mode** → Waits for user's answer
4. **User explains word** → Parser extracts POS/meaning tags
5. **Database updated** → Word added with relationships
6. **Confirmation given** → Learning mode exits

## Smart Features

- **Skip common words**: Asks about meaningful words before articles ("elephant" before "the")
- **Context-aware questions**: Detects if word likely noun, verb, or adjective based on position
- **Weighted relations**: Tracks word pairs to build sequential knowledge
- **Natural conversations**: Varied question templates and confirmations

## Next Steps

These components are ready for integration with:
- **The Orator** (Mode C) - Generate grammatically correct sentences using learned vocabulary
- **Enhanced training** - Use parser to process training documents and populate database
- **Advanced POS tagging** - Integrate NLP libraries for better part-of-speech detection

## Architecture

```
User Input
    ↓
Parser (tokenize, identify unknowns)
    ↓
Listener (orchestrate)
    ↓
Question Generator (ask about unknowns)
    ↓
User Response
    ↓
Database (store new knowledge)
```

All components work together to enable continuous, conversational learning!
