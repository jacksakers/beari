# Beari2 - Object-Oriented Learning AI 🐻

Beari2 is an AI system that learns by creating and growing "Living Objects" - dynamic data structures that acquire new properties through conversation.

## 🌟 Key Features

- **Living Objects**: Dynamic objects that grow with arbitrary properties at runtime
- **Object-Oriented Learning (OOL)**: Maps language to conceptual objects with relationships
- **Gap Analysis Engine**: Automatically identifies missing knowledge and asks targeted questions
- **Real-Time Database Viewer**: Beautiful Flask-based web interface showing objects as they grow
- **Entity-Attribute-Value (EAV) Database**: Flexible schema supporting unlimited property growth

## 📁 Project Structure

```
beari2/
├── core/                      # Core learning algorithms
│   ├── gap_analysis.py       # Identifies missing object properties
│   ├── object_manager.py     # Manages LivingObject lifecycle
│   └── question_generator.py # Generates natural language questions
├── db/                        # Database layer
│   ├── connection.py         # Database connection management
│   ├── init_db.py            # Database initialization
│   ├── object_operations.py  # CRUD for ConceptObjects
│   ├── property_operations.py # CRUD for DynamicProperties
│   └── schema.py             # Database schema and constants
├── models/                    # Data models
│   └── living_object.py      # The LivingObject class
├── utils/                     # Utilities
│   └── input_parser.py       # Natural language parser
├── viewer/                    # Real-time web viewer
│   ├── app.py                # Flask server
│   └── templates/
│       └── viewer.html       # Beautiful real-time UI
└── beari2.py                 # Main conversation interface
```

## 🚀 Getting Started

### Installation

1. Install dependencies:
```bash
pip install flask flask-cors
```

2. Initialize the database:
```bash
cd beari2
python db/init_db.py
```

### Running Beari2

**Option 1: Chat Interface Only**
```bash
cd beari2
python beari2.py
```

**Option 2: Chat + Real-Time Viewer (Recommended)**

Terminal 1 - Start the viewer:
```bash
cd beari2/viewer
python app.py
```

Terminal 2 - Start the chat:
```bash
cd beari2
python beari2.py
```

Then open your browser to `http://127.0.0.1:5000` to watch the database grow in real-time!

## 💬 Usage Examples

### Basic Conversation
```
You: A dog is an animal
Beari: I see, dog is animal.
Beari: What can dog do?

You: Dogs can bark
Beari: Got it, dog can bark.
Beari: What does dog feel like?

You: Dogs feel friendly
Beari: I understand, dog feels like friendly.
```

### Special Commands
- `stats` - Show knowledge statistics
- `help` - Display help message
- `quit` - Exit the conversation

## 🏗️ Architecture

### Living Objects
Each word becomes a `LivingObject` that can grow dynamically:
```python
dog = LivingObject("dog", "Noun")
dog.add_property("is", "animal")
dog.add_property("can_do", "bark")
dog.add_property("feels_like", "friendly")
```

### Database Schema
**ConceptObjects Table**: Stores the objects (words)
- id, name, type (Noun/Verb/Adjective), timestamps

**DynamicProperties Table**: Stores properties (EAV pattern)
- id, parent_id, relation, target_value, weight, timestamps

This allows unlimited property types without schema changes!

### Learning Pipeline
1. **Parse** → Extract subject, verb, object from input
2. **Create/Update** → Build or update LivingObjects
3. **Save** → Persist to database
4. **Analyze** → Find knowledge gaps
5. **Question** → Ask about missing properties

## 🎨 Real-Time Viewer Features

- **Live Updates**: See objects appear and grow as you chat
- **Beautiful UI**: Modern, responsive design with animations
- **Filtering**: Filter by type (Noun/Verb/Adjective)
- **Search**: Search objects by name
- **Statistics**: Real-time counts and metrics
- **Property Weights**: See how often relationships are mentioned

## 🧪 Design Philosophy

Beari2 implements "Object-Oriented Learning" from the design document:

1. **Dynamic Growth**: Objects acquire properties on-the-fly
2. **Relationship Mapping**: Language patterns map to object properties
3. **Active Learning**: System identifies and fills knowledge gaps
4. **Visual Feedback**: Real-time visualization of learning process

## 📊 Standard Property Templates

**Nouns**: is, feels_like, can_do, can_have, can_be, part_of, used_for
**Verbs**: performed_by, affects, requires, results_in, feels_like
**Adjectives**: describes, intensity, opposite, similar_to, can_describe

## 🔧 Extending Beari2

### Adding New Relation Types
Edit `db/schema.py` and add to `RELATION_TYPES` and `STANDARD_FIELDS`

### Improving Parser
Edit `utils/input_parser.py` to recognize more sentence patterns

### Custom Questions
Edit `core/question_generator.py` to add new question templates

## 📝 Notes

- One function per file for clean organization
- All database operations separated by concern
- Context managers used throughout for safety
- Type hints on all functions
- Comprehensive docstrings

## 🐛 Troubleshooting

**Database locked error**: Make sure only one instance is writing at a time

**Viewer not updating**: Check that the Flask server is running and accessible

**Import errors**: Make sure you're running from the correct directory

## 🎯 Future Enhancements

- Sentence generation from object graph traversal
- Context clustering for semantic grouping
- Multi-object reasoning
- Natural language query interface
- Export knowledge graphs

---

Built with 🐻 and Python
