# Beari3 - Supervised Learning Model

## Overview

Beari3 is a "Watch and Learn" conversational AI training system. Unlike traditional chatbots that try to generate responses immediately, Beari3 is a **Student** that learns by observing examples of prompt-response pairs provided by you (the Teacher).

The system analyzes the relationship between prompts and responses, extracts patterns, and stores this knowledge for future use.

## Core Philosophy

**"Show, Don't Tell"** with **Semantic Abstraction**

Instead of trying to chat before it knows enough words, Beari3:
1. Watches you provide example conversations
2. Analyzes structure, tense, sentiment, and semantic categories
3. Creates abstract pattern signatures (e.g., SELF_PAST_FOOD)
4. Learns the "logic bridge" between inputs and outputs
5. **Generalizes**: Training on "curry" works for "pizza", "taco", etc.
6. Builds a pattern database for future inference

## The 4-Phase Training Cycle

Every training interaction goes through 4 phases:

### Phase A: Deep Analysis (Abstraction Phase)
- User enters a prompt (e.g., "I just cooked a spicy curry")
- System analyzes: subject, verb, object, adjectives, sentence type
- **Tense Detection**: PAST, PRESENT, or FUTURE
- **Sentiment Analysis**: Positive, negative, or neutral (-1 to 1)
- **Semantic Categorization**: Maps words to categories (curry → FOOD)
- **Pattern Signature Generation**: Creates abstract signature (SELF_PAST_ACTION_CREATION_FOOD)
- Detects unknown words and missing semantic categories

### Phase B: Gold Standard Response
- User provides the ideal response (e.g., "Yum! Did it taste good?")
- This becomes the "correct answer" for this type of input

### Phase C: Pattern Extraction (Inference)
- System compares prompt and response
- Identifies patterns (e.g., "Response uses affirmation + question about target")
- Creates response template with placeholders: "Yum! Did {target} taste good?"
- Learns the relationship logic

### Phase D: Storage
- Saves the complete interaction as a "Conversational Unit"
- Stores: raw text, signature, template, tense, sentiment
- Updates pattern database for future retrieval
- **Key**: Signature allows generalization to similar inputs

## Installation

### Option 1: Automated Setup (Recommended)

```powershell
cd beari3
python setup.py
```

### Option 2: Manual Setup

#### 1. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

#### 2. Download spaCy Language Model

```powershell
python -m spacy download en_core_web_sm
```

#### 3. Download TextBlob Corpora

```powershell
python -m textblob.download_corpora
```

This downloads the English language model and sentiment analysis data needed for NLP.

## Usage

### Start Training

```powershell
python train.py
```

### Run Generalization Demo

See abstraction in action - train on one example, test on many:

```powershell
python demo_generalization.py
```

### Run Unit Tests

```powershell
python tests/test_abstraction.py
```

### Training Session Example

```
Enter a prompt (what the user would say): I just cooked a spicy curry.

==================================================
   EXTENDED ANALYSIS REPORT
==================================================
Input: "I just cooked a spicy curry."
Type: STATEMENT
Subject: I
Verb: cook
Target: curry
Adjectives: ['spicy']

--- ABSTRACTION LAYER ---
Tense: PAST
Sentiment: 0.0 (Neutral)
Semantic Tags: {'verb_category': 'ACTION_CREATION', 'target_category': 'FOOD'}

>>> PATTERN SIGNATURE:
>>> SELF_PAST_ACTION_CREATION_FOOD
--------------------------------------------------

✓ All words recognized
==================================================

🏷️  Some words lack semantic categories: []
Add semantic categories for better generalization? (y/n): n

Now provide the IDEAL response to this prompt.
Enter the ideal response: Yum! Did it taste good?

==================================================
   LEARNING CONCLUSIONS
==================================================
1. Detected affirmation: 'Yum'
2. Response strategy is INTERROGATIVE (asking for more info)
==================================================

💾 PHASE D: Storage
--------------------------------------------------
✓ Saved Conversational Unit #1
  Signature: SELF_PAST_ACTION_CREATION_FOOD
  Template: Yum! Did {target} taste good?

Continue training? (y/n):
```

**Now the magic**: If you later say "I just cooked a taco" or "I cooked a pizza", 
Beari3 will respond with "Yum! Did the taco taste good?" because it learned the 
**abstract pattern** for FOOD items, not just curry!

## Project Structure

```
beari3/
├── train.py              # Main training program
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── core/                # Core logic
│   ├── analyzer.py      # Sentence analysis (NLP)
│   └── inference.py     # Pattern extraction
├── db/                  # Database layer
│   └── schema.py        # SQLite schema
└── utils/               # Utilities
    └── vocab_manager.py # Vocabulary management
```

## Database Structure

The system uses SQLite with four main tables:

### Vocabulary
Stores known words with their part of speech and definitions.

### SemanticCategories (NEW!)
Maps words to abstract categories for generalization:
- curry, pizza, taco → FOOD
- walk, run, jog → ACTIVITY  
- movie, book, song → MEDIA

### ConversationalUnits
Stores complete training examples with:
- Raw text (prompt + response)
- **Pattern signature** (e.g., SELF_PAST_ACTION_CREATION_FOOD)
- **Response template** (e.g., "Yum! Did {target} taste good?")
- Tense, sentiment, semantic tags

### PatternMap
Stores abstract patterns learned from training (e.g., "Statement about action → Affirmation + Question").

## User-Friendly Features

### 🆕 Unknown Word Handling
When Beari3 encounters an unknown word, it prompts you with a simple numbered menu:
- Choose the part of speech (Noun, Verb, Adjective, etc.)
- Optionally add a definition
- Word is immediately added to vocabulary

### 🏷️ Semantic Category Assignment
When a word lacks a semantic category, get a user-friendly menu:
- 12 common categories (FOOD, ACTIVITY, MEDIA, etc.)
- Option to create custom categories
- Enables powerful generalization across similar items

### 📊 Verbose Output
Every step is clearly printed:
- Analysis reports show structure AND abstraction
- Pattern signatures reveal generalization potential
- Learning conclusions explain what patterns were found
- Storage confirmations show signatures and templates

### 🌱 Pre-seeded Data
Common English words (pronouns, articles, prepositions) and semantic mappings 
(curry→FOOD, walk→ACTIVITY) are pre-loaded to reduce initial setup friction.

### 🧠 Intelligent Generalization
Training on ONE example applies to MANY similar inputs:
- Train on "curry" → Works for "pizza", "taco", "burger"
- Train on "walk" → Works for "run", "jog", "hike"
- Train on "movie" → Works for "book", "show", "podcast"

## Future Usage (Auto Mode)

Once the database contains enough patterns, Beari3 can switch to "Auto Mode" where it:
1. Receives a new prompt
2. Searches for similar conversational units
3. Applies learned patterns to generate responses
4. Uses the pattern database to produce contextually appropriate replies

## Tips for Training

1. **Start Simple**: Begin with basic statements and questions
2. **Be Consistent**: Use similar response styles for similar prompts
3. **Build Vocabulary**: Define unknown words as you go
4. **Vary Examples**: Provide different types of conversations
5. **Check Patterns**: Review what patterns the system learns

## Technical Notes

- **NLP Engine**: Uses spaCy for part-of-speech tagging, dependency parsing, and tense detection
- **Sentiment Analysis**: Uses TextBlob for polarity scoring (-1 to 1)
- **Abstraction**: Semantic categorization + signature generation enables generalization
- **Pattern Matching**: Exact and partial signature matching for response generation
- **Fallback Mode**: Works without spaCy/TextBlob (basic parsing) if needed
- **Database**: SQLite (no external database required)
- **Platform**: Cross-platform (Windows, Mac, Linux)

## Troubleshooting

### "spaCy model not found"
Run: `python -m spacy download en_core_web_sm`

### "Import spacy could not be resolved"
Run: `pip install spacy`

### Database errors
Delete `beari3.db` to start fresh

## License

This is part of the Barebones_AI project.
