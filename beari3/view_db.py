"""
Database Viewer for Beari3
View learned conversational units and patterns
"""

import sqlite3
import json
from db.schema import Database


class Beari3Viewer:
    def __init__(self, db_path="beari3.db"):
        self.db = Database(db_path)
    
    def view_vocabulary(self, limit=50):
        """Display vocabulary words"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT word, part_of_speech, definition
            FROM Vocabulary
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        print("\n" + "="*60)
        print(f"   VOCABULARY ({len(results)} words shown)")
        print("="*60)
        
        for word, pos, definition in results:
            def_text = f" - {definition}" if definition else ""
            print(f"  {word:<20} [{pos:<8}]{def_text}")
        
        print("="*60)
    
    def view_conversational_units(self, limit=10):
        """Display conversational units"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, prompt_raw, response_raw, response_strategy, key_words, created_at
            FROM ConversationalUnits
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        print("\n" + "="*80)
        print(f"   CONVERSATIONAL UNITS ({len(results)} shown)")
        print("="*80)
        
        for c_id, prompt, response, strategy, keywords, created in results:
            print(f"\n  ID: {c_id} | Created: {created}")
            print(f"  Prompt:   {prompt}")
            print(f"  Response: {response}")
            print(f"  Strategy: {strategy}")
            print(f"  Keywords: {keywords}")
            print("-"*80)
        
        print("="*80)
    
    def view_patterns(self):
        """Display learned patterns"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT input_pattern, response_pattern, usage_count, created_at
            FROM PatternMap
            ORDER BY usage_count DESC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        print("\n" + "="*80)
        print(f"   LEARNED PATTERNS ({len(results)} total)")
        print("="*80)
        
        for input_pat, response_pat, count, created in results:
            print(f"\n  Input:    {input_pat}")
            print(f"  Response: {response_pat}")
            print(f"  Seen {count} time(s) | First learned: {created}")
            print("-"*80)
        
        print("="*80)
    
    def stats(self):
        """Display database statistics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Vocabulary")
        vocab_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ConversationalUnits")
        unit_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM PatternMap")
        pattern_count = cursor.fetchone()[0]
        
        conn.close()
        
        print("\n" + "="*50)
        print("   DATABASE STATISTICS")
        print("="*50)
        print(f"  Vocabulary Words:      {vocab_count:>6}")
        print(f"  Conversational Units:  {unit_count:>6}")
        print(f"  Learned Patterns:      {pattern_count:>6}")
        print("="*50)


def main():
    """Interactive viewer menu"""
    viewer = Beari3Viewer()
    
    print("\n" + "="*50)
    print("   BEARI3 DATABASE VIEWER")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("  1. View statistics")
        print("  2. View vocabulary")
        print("  3. View conversational units")
        print("  4. View learned patterns")
        print("  5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            viewer.stats()
        elif choice == "2":
            viewer.view_vocabulary()
        elif choice == "3":
            viewer.view_conversational_units()
        elif choice == "4":
            viewer.view_patterns()
        elif choice == "5":
            print("\n✓ Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
