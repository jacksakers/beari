# Beari Orator & Corrector System

This implements **Mode C: The Orator** (sentence generation and question answering) plus a new **Corrector** system for learning from mistakes.

## New Components

### 1. **Orator** (`orator.py`)
Generates sentences and answers questions based on database knowledge.

**Key Functions:**
- `generate_sentence(template)` - Creates grammatically correct sentences using templates
- `answer_question(question)` - Answers user questions about words in the database
- Template-based generation ensures Subject-Predicate-Object structure

**Supported Question Types:**
- **"What is X?"** - Provides definition, POS tag, and relations
- **"What does X do?"** - Lists capabilities (capable_of relations)
- **"Is X a Y?"** - Checks is_a relations and meaning tags
- **"Can X do Y?"** - Verifies capable_of relations
- **"Tell me about X"** - Comprehensive information dump

### 2. **Corrector** (`corrector.py`)
Handles corrections when users tell Beari it's wrong.

**Key Functions:**
- `is_correction(user_input)` - Detects correction phrases
- `process_correction(user_input)` - Processes and applies corrections
- `delete_word(word)` - Completely removes a word and its relations
- `set_context(word, statement, relations)` - Tracks what Beari just said for context

**Correction Types:**
- **is_a corrections**: "X is not a Y" → Removes incorrect is_a relations
- **capable_of corrections**: "X cannot Y" → Removes incorrect capabilities  
- **Meaning tag corrections**: "Wrong category" → Updates or removes meaning tags
- **POS tag corrections**: "It's not a noun" → Updates part of speech
- **Complete deletion**: `forget X` → Removes word entirely

### 3. **Main Interface** (`beari.py`)
Integrates all three modes (Listener, Orator, Corrector).

**Processing Priority:**
1. Check if waiting for learning response (Listener mode)
2. Check if user is making a correction (Corrector mode)
3. Check if user is asking a question (Orator mode)
4. Otherwise, learn from input (Listener mode)

**Special Commands:**
- `stats` - Show vocabulary statistics
- `help` - Show help information
- `generate` - Generate a random sentence
- `forget X` - Remove word X from database
- `quit` - Exit

## Usage Examples

### Interactive Chat

```bash
python beari.py
```

This launches the full Beari experience with learning, answering, and corrections.

### Run Demo

```bash
python demo_beari.py
```

Shows a scripted conversation demonstrating all features.

### Question Answering Only

```python
from orator import Orator

with Orator() as orator:
    # Answer questions
    result = orator.answer_question("What is dog?")
    print(result['message'])
    
    # Generate sentences
    sentence = orator.generate_sentence()
    print(sentence)
```

### Correction Handling

```python
from corrector import Corrector

with Corrector() as corrector:
    # Set context (what Beari just said)
    corrector.set_context(
        word="python",
        statement="Python is an animal",
        relations=[{'relation_type': 'is_a', 'target_word': 'animal'}]
    )
    
    # Process correction
    result = corrector.process_correction("That's wrong! Python is not an animal.")
    print(result['message'])  # "Got it! I've removed the incorrect information..."
```

### Full Integration

```python
from beari import BeariAI

with BeariAI() as beari:
    # Ask a question
    result = beari.process_input("What is dog?")
    print(result['message'])
    
    # Make a correction
    result = beari.process_input("That's wrong!")
    print(result['message'])
    
    # Learn new information
    result = beari.process_input("The giraffe is tall")
    print(result['message'])
```

## Testing

Run the comprehensive test suite:

```bash
python tests\test_orator.py
```

This tests:
- Sentence generation with templates
- All question types (what is, what does, can, is, tell me about)
- Unknown word handling
- Correction detection
- Correction processing (is_a, capable_of, tags)
- Word deletion
- Full integration workflow

## Example Conversation

```
🧑 You: What is dog?
🐻 Beari: 'Dog' is a noun related to animal. It is a animal. It can run. It can bark.

🧑 You: Can a dog fly?
🐻 Beari: I don't think 'dog' can fly, based on what I know.

🧑 You: What about robots?
🐻 Beari: I don't know the word 'robots'. Is 'robots' a person, place, or thing?

🧑 You: It's a machine that can think
🐻 Beari: Got it! I learned 'robots'. It's a Noun (thing).

🧑 You: Actually, that's wrong. Robots cannot think.
🐻 Beari: Understood! I've removed the incorrect information that 'robots' can think.

🧑 You: generate
🐻 Beari: The robot calculates data.
```

## How It Works

### Question Answering Flow

1. **Parse question** → Identify question type and target word
2. **Look up word** → Check if it exists in database
3. **Gather relations** → Get all relevant connections
4. **Format answer** → Build natural language response
5. **Set context** → Store for potential corrections

### Correction Flow

1. **Detect correction** → Match correction phrases
2. **Parse correction** → Identify what's wrong
3. **Locate data** → Find the incorrect relation/tag
4. **Update database** → Remove or modify the data
5. **Confirm** → Tell user what was changed

### Sentence Generation Flow

1. **Pick template** → Select Subject-Verb-Object pattern
2. **Choose subject** → Pick noun (prefer ones with relations)
3. **Choose verb** → Pick verb (prefer related to subject)
4. **Choose object** → Pick noun (prefer related to verb)
5. **Fill template** → Insert words and return sentence

## Architecture Notes

- **Context tracking**: Corrector tracks last statement for intelligent corrections
- **Template-based generation**: Ensures grammatical correctness (no gibberish)
- **Relation-aware**: Prefers words with rich connections for better sentences
- **Graceful degradation**: If can't answer, says "I don't know" instead of making things up
- **User-friendly corrections**: Accepts natural language like "that's wrong!" or "X cannot Y"

## Next Steps

With all three modes working together:
1. **Chat naturally** - Beari learns, answers, and corrects
2. **Teach Beari** - Add vocabulary through conversation
3. **Ask questions** - Test what Beari knows
4. **Fix mistakes** - Correct wrong information
5. **Generate content** - Have Beari create sentences

Run `python beari.py` to start chatting!
