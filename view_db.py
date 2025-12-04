"""
Database Viewer for Beari AI
A simple tool to inspect the contents of the Beari database in a readable format.
"""

import sys
from db.db_helpers import DatabaseHelper


def print_separator(char="=", length=70):
    """Print a separator line."""
    print(char * length)


def print_section_header(title):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def view_vocabulary(db):
    """Display all words in the vocabulary."""
    print_section_header("VOCABULARY")
    
    words = db.get_all_words()
    
    if not words:
        print("\nNo words in vocabulary yet.")
        return
    
    print(f"\nTotal words: {len(words)}\n")
    
    # Group by POS tag
    by_pos = {}
    for word in words:
        pos = word['pos_tag'] or 'Unknown'
        if pos not in by_pos:
            by_pos[pos] = []
        by_pos[pos].append(word)
    
    # Display grouped by POS
    for pos, word_list in sorted(by_pos.items()):
        print(f"\n{pos}s ({len(word_list)}):")
        print("-" * 70)
        
        for word in sorted(word_list, key=lambda x: x['word']):
            meaning = f" [{word['meaning_tag']}]" if word['meaning_tag'] else ""
            plural = " (plural)" if word['is_plural'] else ""
            print(f"  • {word['word']}{meaning}{plural}")


def view_relations(db):
    """Display all word relations."""
    print_section_header("RELATIONS")
    
    # Query all relations directly from the database
    query = """
        SELECT va.word as word_a, r.relation_type, vb.word as word_b, r.weight
        FROM relations r
        JOIN vocabulary va ON r.word_a_id = va.id
        JOIN vocabulary vb ON r.word_b_id = vb.id
        ORDER BY r.relation_type, va.word
    """
    
    db.cursor.execute(query)
    all_relations = [dict(row) for row in db.cursor.fetchall()]
    
    if not all_relations:
        print("\nNo relations defined yet.")
        return
    
    print(f"\nTotal relations: {len(all_relations)}\n")
    
    # Group by relation type
    by_type = {}
    for rel in all_relations:
        rel_type = rel['relation_type']
        if rel_type not in by_type:
            by_type[rel_type] = []
        by_type[rel_type].append(rel)
    
    # Display grouped by type
    for rel_type, rel_list in sorted(by_type.items()):
        print(f"\n{rel_type} ({len(rel_list)}):")
        print("-" * 70)
        
        for rel in sorted(rel_list, key=lambda x: x['word_a']):
            weight_str = f" [weight: {rel['weight']}]" if rel['weight'] > 1 else ""
            print(f"  • {rel['word_a']} → {rel['word_b']}{weight_str}")


def view_word_details(db, word):
    """Display detailed information about a specific word."""
    print_section_header(f"WORD DETAILS: '{word}'")
    
    word_info = db.get_word(word)
    
    if not word_info:
        print(f"\nWord '{word}' not found in vocabulary.")
        return
    
    # Basic info
    print(f"\nWord: {word_info['word']}")
    print(f"Part of Speech: {word_info['pos_tag'] or 'Not specified'}")
    print(f"Meaning Category: {word_info['meaning_tag'] or 'Not specified'}")
    print(f"Form: {'Plural' if word_info['is_plural'] else 'Singular'}")
    print(f"Added: {word_info['created_at']}")
    
    # Outgoing relations (what this word relates to)
    print("\nOutgoing Relations:")
    print("-" * 70)
    relations = db.get_relations(word)
    
    if relations:
        for rel in relations:
            weight_str = f" [weight: {rel['weight']}]" if rel['weight'] > 1 else ""
            print(f"  • {rel['relation_type']}: {rel['target_word']}{weight_str}")
    else:
        print("  No outgoing relations")
    
    # Incoming relations (what relates to this word)
    print("\nIncoming Relations:")
    print("-" * 70)
    reverse_relations = db.get_reverse_relations(word)
    
    if reverse_relations:
        for rel in reverse_relations:
            weight_str = f" [weight: {rel['weight']}]" if rel['weight'] > 1 else ""
            print(f"  • {rel['source_word']} → {rel['relation_type']}{weight_str}")
    else:
        print("  No incoming relations")


def view_statistics(db):
    """Display database statistics."""
    print_section_header("STATISTICS")
    
    stats = db.get_stats()
    
    print(f"\nVocabulary Size: {stats['vocabulary_size']} words")
    print(f"Total Relations: {stats['total_relations']}")
    print(f"\nRelation Types: {stats['relation_types']}")
    
    # POS distribution
    words = db.get_all_words()
    by_pos = {}
    by_meaning = {}
    
    for word in words:
        pos = word['pos_tag'] or 'Unknown'
        by_pos[pos] = by_pos.get(pos, 0) + 1
        
        if word['meaning_tag']:
            meaning = word['meaning_tag']
            by_meaning[meaning] = by_meaning.get(meaning, 0) + 1
    
    print("\nPart of Speech Distribution:")
    for pos, count in sorted(by_pos.items(), key=lambda x: -x[1]):
        print(f"  • {pos}: {count}")
    
    if by_meaning:
        print("\nMeaning Category Distribution:")
        for meaning, count in sorted(by_meaning.items(), key=lambda x: -x[1]):
            print(f"  • {meaning}: {count}")


def interactive_menu(db):
    """Interactive menu for exploring the database."""
    while True:
        print("\n" + "="*70)
        print("  BEARI DATABASE VIEWER - MENU")
        print("="*70)
        print("\n1. View all vocabulary")
        print("2. View all relations")
        print("3. View statistics")
        print("4. Search for a word")
        print("5. View everything")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            view_vocabulary(db)
        elif choice == '2':
            view_relations(db)
        elif choice == '3':
            view_statistics(db)
        elif choice == '4':
            word = input("Enter word to search: ").strip().lower()
            if word:
                view_word_details(db, word)
        elif choice == '5':
            view_statistics(db)
            view_vocabulary(db)
            view_relations(db)
        elif choice == '6' or choice.lower() == 'q':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")


def main():
    """Main entry point."""
    # Parse command line arguments
    db_path = "beari.db"
    mode = "menu"
    word_to_search = None
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ['-h', '--help']:
            print("\nBeari Database Viewer")
            print("="*70)
            print("\nUsage:")
            print("  python view_db.py                  # Interactive menu")
            print("  python view_db.py --all            # Show everything")
            print("  python view_db.py --vocab          # Show vocabulary only")
            print("  python view_db.py --relations      # Show relations only")
            print("  python view_db.py --stats          # Show statistics only")
            print("  python view_db.py --word <word>    # Show details for a word")
            print("  python view_db.py --db <path>      # Use custom database file")
            print("\nExamples:")
            print("  python view_db.py --all")
            print("  python view_db.py --word python")
            print("  python view_db.py --db test.db --vocab")
            return
        elif arg == '--all':
            mode = 'all'
        elif arg == '--vocab':
            mode = 'vocab'
        elif arg == '--relations':
            mode = 'relations'
        elif arg == '--stats':
            mode = 'stats'
        elif arg == '--word':
            mode = 'word'
            if len(sys.argv) > 2:
                word_to_search = sys.argv[2].lower()
            else:
                print("Error: --word requires a word argument")
                return
        elif arg == '--db':
            if len(sys.argv) > 2:
                db_path = sys.argv[2]
                if len(sys.argv) > 3:
                    mode = sys.argv[3].lstrip('--')
            else:
                print("Error: --db requires a path argument")
                return
    
    # Connect to database
    try:
        with DatabaseHelper(db_path) as db:
            print(f"\nConnected to: {db_path}")
            
            if mode == 'menu':
                interactive_menu(db)
            elif mode == 'all':
                view_statistics(db)
                view_vocabulary(db)
                view_relations(db)
            elif mode == 'vocab':
                view_vocabulary(db)
            elif mode == 'relations':
                view_relations(db)
            elif mode == 'stats':
                view_statistics(db)
            elif mode == 'word':
                view_word_details(db, word_to_search)
            
            print("\n" + "="*70 + "\n")
            
    except Exception as e:
        print(f"\nError: {e}")
        print(f"Make sure the database file exists at: {db_path}")
        print("Run 'python db/init_db.py' to create it.")


if __name__ == "__main__":
    main()
