# Beari3 - Supervised Learning Model

## Overview

Beari3 is a "Watch and Learn" conversational AI training system. Unlike traditional chatbots that try to generate responses immediately, Beari3 is a **Student** that learns by observing examples of prompt-response pairs provided by you (the Teacher).

The system analyzes the relationship between prompts and responses, extracts patterns, and stores this knowledge for future use.

## Core Philosophy

**"Show, Don't Tell"**

Instead of trying to chat before it knows enough words, Beari3:
1. Watches you provide example conversations
2. Analyzes the structure and patterns
3. Learns the "logic bridge" between inputs and outputs
4. Builds a pattern database for future inference

## The 4-Phase Training Cycle

Every training interaction goes through 4 phases:

### Phase A: Prompt Analysis
- User enters a prompt (e.g., "I just took a brisk walk")
- System analyzes: subject, verb, object, adjectives, sentence type
- Detects unknown words and prompts for definitions

### Phase B: Gold Standard Response
- User provides the ideal response (e.g., "Cool! How was the walk?")
- This becomes the "correct answer" for this type of input

### Phase C: Pattern Extraction (Inference)
- System compares prompt and response
- Identifies patterns (e.g., "Response uses affirmation + question about target")
- Learns the relationship logic

### Phase D: Storage
- Saves the complete interaction as a "Conversational Unit"
- Updates pattern database for future retrieval

## Installation

### 1. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Download spaCy Language Model

```powershell
python -m spacy download en_core_web_sm
```

This downloads the English language model needed for NLP analysis.

## Usage

### Start Training

```powershell
python train.py
```

### Training Session Example

```
Enter a prompt (what the user would say): I just took a brisk walk.

==============================
   ANALYSIS REPORT
==============================
Input: "I just took a brisk walk."
Type: STATEMENT
Subject: I
Verb: take
Target: walk
Adjectives: ['brisk']

⚠️  Unknown words detected: ['brisk']
These will need to be added to vocabulary...
==============================

⚠️  Found 1 unknown word(s)
Would you like to define them now? (y/n): y

🆕 Unknown word detected: 'brisk'

What part of speech is this word?
  1. Noun (person, place, thing)
  2. Verb (action word)
  3. Adjective (describes a noun)
  4. Adverb (describes a verb)
  ...

Enter number (1-9): 3
✓ Added 'brisk' as ADJ

Now provide the IDEAL response to this prompt.
Enter the ideal response: Cool! How was the walk?

==============================
   LEARNING CONCLUSIONS
==============================
1. Detected affirmation: 'Cool'
2. Response strategy is INTERROGATIVE (asking for more info)
3. Response focuses on the target 'walk'
4. PATTERN LEARNED: [Statement: Action] -> [Affirmation + Question about Target]
==============================

✓ Saved Conversational Unit #1
✓ New pattern saved: STATEMENT:take -> affirmation_question_target_callback:walk

Continue training? (y/n):
```

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

The system uses SQLite with three main tables:

### Vocabulary
Stores known words with their part of speech and definitions.

### ConversationalUnits
Stores complete training examples (prompt + response pairs).

### PatternMap
Stores abstract patterns learned from training (e.g., "Statement about action → Affirmation + Question").

## User-Friendly Features

### 🆕 Unknown Word Handling
When Beari3 encounters an unknown word, it prompts you with a simple numbered menu:
- Choose the part of speech (Noun, Verb, Adjective, etc.)
- Optionally add a definition
- Word is immediately added to vocabulary

### 📊 Verbose Output
Every step is clearly printed:
- Analysis reports show exactly what was detected
- Learning conclusions explain what patterns were found
- Storage confirmations show what was saved

### 🌱 Pre-seeded Vocabulary
Common English words (pronouns, articles, prepositions) are pre-loaded to reduce initial setup friction.

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

- **NLP Engine**: Uses spaCy for part-of-speech tagging and dependency parsing
- **Fallback Mode**: Works without spaCy (basic parsing) if needed
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
