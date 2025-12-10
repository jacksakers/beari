"""
Import Training Data into Beari Database
Loads all words from nouns.txt, verbs.txt, and adjectives.txt into the database.
"""

import sys
import os
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_helpers import DatabaseHelper


def parse_training_file(filepath):
    """
    Parse a training data file and extract words with their POS tags.
    
    Format: word\tfrequency\t\t(pos_tags)
    Example: "people\t372\t\t(noun)"
    
    Args:
        filepath: Path to the training data file
    
    Returns:
        List of tuples: [(word, pos_tag), ...]
    """
    words_data = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            try:
                # Split by tabs
                parts = line.split('\t')
                
                if len(parts) < 4:
                    print(f"Warning: Skipping malformed line {line_num}: {line}")
                    continue
                
                word = parts[0].strip().lower()
                pos_info = parts[3].strip()  # e.g., "(noun)" or "(verb, noun)"
                
                # Extract POS tags from parentheses
                pos_match = re.search(r'\((.*?)\)', pos_info)
                if not pos_match:
                    print(f"Warning: No POS tag found on line {line_num}: {line}")
                    continue
                
                pos_tags = pos_match.group(1).split(',')
                
                # Add an entry for each POS tag
                for pos in pos_tags:
                    pos = pos.strip()
                    # Capitalize first letter for consistency
                    pos_tag = pos.capitalize()
                    words_data.append((word, pos_tag))
                    
            except Exception as e:
                print(f"Error parsing line {line_num}: {line}")
                print(f"  Error: {e}")
                continue
    
    return words_data


def import_file(db, filepath, primary_pos):
    """
    Import words from a training file into the database.
    
    Args:
        db: DatabaseHelper instance
        filepath: Path to the training file
        primary_pos: Primary POS tag for this file (Noun, Verb, or Adjective)
    
    Returns:
        Number of words imported
    """
    print(f"\nImporting from: {os.path.basename(filepath)}")
    print("-" * 70)
    
    words_data = parse_training_file(filepath)
    
    if not words_data:
        print("No valid words found in file.")
        return 0
    
    print(f"Found {len(words_data)} word entries to import...")
    
    imported = 0
    skipped = 0
    
    for word, pos_tag in words_data:
        try:
            # Check if word already exists
            if db.word_exists(word):
                skipped += 1
                if skipped <= 5:  # Only show first few
                    print(f"  Skipped (already exists): {word}")
                elif skipped == 6:
                    print(f"  ... (suppressing further duplicate messages)")
                continue
            
            # Add word to database
            db.add_word(word, pos_tag=pos_tag)
            imported += 1
            
            # Show progress every 100 words
            if imported % 100 == 0:
                print(f"  Imported: {imported} words...")
                
        except Exception as e:
            print(f"  Error importing '{word}': {e}")
    
    print(f"\n✓ Imported {imported} new words from {os.path.basename(filepath)}")
    if skipped > 0:
        print(f"  Skipped {skipped} words (already in database)")
    
    return imported


def main():
    """Main import function."""
    print("=" * 70)
    print("BEARI AI - TRAINING DATA IMPORT")
    print("=" * 70)
    
    # File paths
    training_dir = "training_data"
    files_to_import = [
        (os.path.join(training_dir, "nouns.txt"), "Noun"),
        (os.path.join(training_dir, "verbs.txt"), "Verb"),
        (os.path.join(training_dir, "adjectives.txt"), "Adjective")
    ]
    
    # Check that files exist
    missing_files = []
    for filepath, _ in files_to_import:
        if not os.path.exists(filepath):
            missing_files.append(filepath)
    
    if missing_files:
        print("\nError: Missing training data files:")
        for f in missing_files:
            print(f"  • {f}")
        return
    
    # Connect to database
    with DatabaseHelper() as db:
        # Get initial stats
        initial_stats = db.get_stats()
        print(f"\nInitial database state:")
        print(f"  Vocabulary: {initial_stats['vocabulary_size']} words")
        print(f"  Relations: {initial_stats['total_relations']}")
        
        # Import each file
        total_imported = 0
        for filepath, pos_type in files_to_import:
            count = import_file(db, filepath, pos_type)
            total_imported += count
        
        # Get final stats
        final_stats = db.get_stats()
        
        print("\n" + "=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)
        print(f"\nFinal database state:")
        print(f"  Vocabulary: {final_stats['vocabulary_size']} words")
        print(f"  Relations: {final_stats['total_relations']}")
        print(f"\nTotal words imported: {total_imported}")
        print(f"Net vocabulary increase: {final_stats['vocabulary_size'] - initial_stats['vocabulary_size']}")


if __name__ == "__main__":
    main()
