# Beari3 Quick Start Guide

## Installation (Option 1 - Automated)

```powershell
cd beari3
python setup.py
```

This will automatically install all dependencies and download the spaCy model.

## Installation (Option 2 - Manual)

```powershell
cd beari3
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Running Beari3

### Start Training
```powershell
python train.py
```

### View Database
```powershell
python view_db.py
```

## Example Training Session

```
Enter a prompt: I just ate a burger.

[System analyzes: subject=I, verb=eat, target=burger]

Enter the ideal response: Nice! How was the burger?

[System learns: Pattern = Statement:Action → Affirmation + Question(Target)]

✓ Conversational Unit saved!
```

## Tips

1. **Define unknown words** when prompted - it improves pattern recognition
2. **Be consistent** with your response styles
3. **Use the viewer** to check what patterns have been learned
4. **Start simple** - basic statements work best initially

## Files

- `train.py` - Main training program (run this!)
- `view_db.py` - Database viewer
- `setup.py` - Automated setup
- `beari3.db` - Database (created on first run)
- `README.md` - Full documentation

## Need Help?

Check README.md for complete documentation.
