# Beari3 Quick Start Guide

## Installation (Automated - Recommended)

```powershell
cd beari3
python setup.py
```

This installs spaCy, TextBlob, and downloads all required language models.

## Running Beari3

### 1. See Generalization Demo (Recommended First!)

```powershell
python demo_generalization.py
```

Watch how training on "curry" generalizes to "pizza", "taco", etc.!

### 2. Start Training Mode

```powershell
python train.py
```

### 3. View Database

```powershell
python view_db.py
```

### 4. Run Tests

```powershell
python tests/test_abstraction.py
```

## Example: The Power of Generalization

```
📚 TRAIN ON ONE EXAMPLE:
Prompt: "I just cooked a curry."
Response: "Yum! Did it taste good?"

✓ System learns signature: SELF_PAST_ACTION_CREATION_FOOD
✓ Creates template: "Yum! Did {target} taste good?"

🧪 NOW IT WORKS ON ALL FOODS:
"I cooked a taco." → "Yum! Did the taco taste good?"
"I cooked a pizza." → "Yum! Did the pizza taste good?"
```

## Key Features

### 🏷️ Semantic Categories
- curry, pizza, taco → FOOD
- walk, run, jog → ACTIVITY

### 🧠 Abstract Signatures
- "I ate curry" → SELF_PAST_ACTION_CONSUMPTION_FOOD
- "I ate pizza" → SELF_PAST_ACTION_CONSUMPTION_FOOD (same!)

## Tips

1. **Add semantic categories** when prompted - enables generalization
2. **Run the demo** to understand abstraction before training
3. **Be consistent** with response styles
4. **Start simple** - basic statements work best initially

## Files

- `train.py` - Main training program (run this!)
- `view_db.py` - Database viewer
- `setup.py` - Automated setup
- `beari3.db` - Database (created on first run)
- `README.md` - Full documentation

## Need Help?

Check README.md for complete documentation.
