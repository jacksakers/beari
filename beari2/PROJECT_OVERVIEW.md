# Beari2 Project Overview

## 📦 Complete File Structure

```
beari2/
│
├── README.md                     # Main documentation
├── requirements.txt              # Python dependencies
├── start.py                      # Quick start script
├── demo.py                       # Interactive demo
├── beari2.py                     # Main conversation interface
│
├── core/                         # Core learning algorithms
│   ├── __init__.py
│   ├── gap_analysis.py          # Gap detection & priority analysis
│   ├── object_manager.py        # LivingObject persistence
│   └── question_generator.py    # Natural language questions
│
├── db/                          # Database layer
│   ├── __init__.py
│   ├── connection.py            # DB connection management
│   ├── init_db.py               # Database initialization
│   ├── object_operations.py     # ConceptObjects CRUD
│   ├── property_operations.py   # DynamicProperties CRUD
│   └── schema.py                # Schema & relation types
│
├── models/                      # Data models
│   ├── __init__.py
│   └── living_object.py         # LivingObject class
│
├── utils/                       # Utility functions
│   ├── __init__.py
│   └── input_parser.py          # Natural language parser
│
└── viewer/                      # Real-time web viewer
    ├── app.py                   # Flask server with SSE
    └── templates/
        └── viewer.html          # Beautiful real-time UI
```

## 🎯 Key Components

### 1. LivingObject Model (`models/living_object.py`)
The heart of the system - a dynamic object that grows with arbitrary properties.

**Key Features:**
- Dynamic property addition at runtime
- Property management (add, remove, get, has)
- Gap analysis for missing fields
- Serialization to/from database
- Merge capabilities

### 2. Database Layer (`db/`)
Entity-Attribute-Value pattern for unlimited flexibility.

**Tables:**
- `ConceptObjects`: Stores objects (id, name, type)
- `DynamicProperties`: Stores properties (parent_id, relation, target_value, weight)

**Operations:**
- One file per operation type (clean separation)
- Context manager support
- Foreign key constraints
- Automatic weight tracking

### 3. Gap Analysis Engine (`core/gap_analysis.py`)
Identifies missing knowledge and prioritizes learning.

**Functions:**
- `find_learning_opportunity()`: Find first missing field
- `get_all_gaps()`: Get all missing fields
- `calculate_completeness()`: Percentage complete
- `prioritize_learning_opportunities()`: Sort by incompleteness
- `suggest_next_question_field()`: Smart field selection

### 4. Question Generator (`core/question_generator.py`)
Generates natural language questions about missing properties.

**Features:**
- Context-aware question templates
- Different questions for Nouns/Verbs/Adjectives
- Natural confirmation messages
- Relation-specific phrasing

### 5. Input Parser (`utils/input_parser.py`)
Extracts structure from natural language.

**Extracts:**
- Subject (actor)
- Verb (action/relation)
- Object (receiver)
- Adjectives (descriptors)
- Relationships between them

### 6. Object Manager (`core/object_manager.py`)
Bridges LivingObjects and database.

**Operations:**
- Create or get objects
- Load from database
- Save with all properties
- Batch operations
- Automatic synchronization

### 7. Real-Time Viewer (`viewer/`)
Beautiful Flask app with Server-Sent Events.

**Features:**
- Live updates (2-second refresh)
- Filter by type (Noun/Verb/Adjective)
- Search functionality
- Statistics dashboard
- Property weight visualization
- Smooth animations
- Responsive design

### 8. Main Interface (`beari2.py`)
Orchestrates all components into conversation flow.

**Pipeline:**
1. Parse input
2. Extract relations
3. Create/update objects
4. Save to database
5. Find gaps
6. Ask questions
7. Process answers

## 🔄 Learning Flow

```
User Input
    ↓
Input Parser
    ↓
Relation Extraction
    ↓
Object Manager (create/update)
    ↓
Database (persist)
    ↓
Gap Analysis (find missing fields)
    ↓
Question Generator
    ↓
User Answer
    ↓
Add Property to Object
    ↓
Save & Continue
```

## 🎨 Design Principles

1. **One Function Per File**: Maximum organization
2. **Separation of Concerns**: DB, logic, UI all separate
3. **Dynamic Growth**: Objects expand without schema changes
4. **Active Learning**: System drives its own education
5. **Real-Time Feedback**: Immediate visualization
6. **Type Safety**: Type hints everywhere
7. **Documentation**: Comprehensive docstrings
8. **Context Managers**: Safe resource handling

## 🚀 Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Quick start (guided setup)
python start.py

# Run demo
python demo.py

# Start chat only
python beari2.py

# Start viewer only
python viewer/app.py

# Initialize database manually
python db/init_db.py
```

## 📊 Database Schema Details

### ConceptObjects Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Word/concept (unique) |
| type | TEXT | Noun/Verb/Adjective |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update |

### DynamicProperties Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| parent_id | INTEGER | FK to ConceptObjects |
| relation | TEXT | Property key |
| target_value | TEXT | Property value |
| value_type | TEXT | Type hint (string/int/float/object) |
| weight | INTEGER | Frequency/importance |
| created_at | TIMESTAMP | Creation time |

## 🎭 Relation Types

**For Nouns:**
- `is`: State or quality
- `feels_like`: Sensory/emotional
- `can_do`: Capable actions
- `can_have`: Possessions
- `can_be`: Potential states
- `part_of`: Component relationships
- `used_for`: Purpose/function

**For Verbs:**
- `performed_by`: Agent
- `affects`: Target
- `requires`: Prerequisites
- `results_in`: Consequences
- `feels_like`: Emotional quality

**For Adjectives:**
- `describes`: What it describes
- `intensity`: Strength
- `opposite`: Antonym
- `similar_to`: Synonym
- `can_describe`: Applicable types

## 🎯 Example Session

```
You: A dog is an animal
Beari: I see, dog is animal.
Beari: What can dog do?

You: bark
Beari: Got it, dog can bark.
Beari: What does dog feel like?

You: friendly
Beari: I understand, dog feels like friendly.

[In viewer: See 'dog' object with 3 properties growing in real-time]
```

## 🔮 Extension Points

### Add New Relation Types
Edit `db/schema.py`:
- Add to `RELATION_TYPES` dict
- Add to `STANDARD_FIELDS` for POS types

### Improve Parsing
Edit `utils/input_parser.py`:
- Add verb patterns
- Add sentence structures
- Improve relation extraction

### Customize Questions
Edit `core/question_generator.py`:
- Add question templates
- Customize for domain
- Add multi-lingual support

### Enhance Viewer
Edit `viewer/templates/viewer.html`:
- Add graph visualization
- Add relationship view
- Add timeline view

## 📈 Performance Notes

- SQLite handles 100,000+ objects easily
- Server-Sent Events scale to ~100 concurrent users
- Database indexes on name, type, relation, target
- Automatic property weight tracking reduces duplicates

## 🐛 Known Limitations

- Parser is basic (keyword-based)
- No pronoun resolution
- No multi-sentence context
- English only
- No persistent conversation history

## 🎓 Learning Resources

This implementation demonstrates:
- Entity-Attribute-Value (EAV) pattern
- Server-Sent Events (SSE)
- Dynamic object systems
- Active learning
- Knowledge representation
- Natural language processing basics

---

**Built with care for clean, organized, educational code! 🐻**
