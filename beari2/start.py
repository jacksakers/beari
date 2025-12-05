"""
Quick Start Script for Beari2
Initializes database and provides instructions for running both components.
"""

import os
import sys

def main():
    print("="*70)
    print("🐻 Beari2 Quick Start")
    print("="*70)
    print()
    
    # Check if database exists
    db_path = "beari2.db"
    if os.path.exists(db_path):
        print(f"✓ Database found: {db_path}")
    else:
        print(f"⚙️  Creating new database: {db_path}")
        from db.init_db import initialize_database
        initialize_database(db_path)
        print("✓ Database initialized!")
    
    print()
    print("="*70)
    print("📋 How to Run Beari2")
    print("="*70)
    print()
    print("OPTION 1: Chat Interface Only")
    print("-" * 70)
    print("  python beari2.py")
    print()
    print("OPTION 2: Chat + Real-Time Viewer (Recommended)")
    print("-" * 70)
    print("  Terminal 1: python viewer/app.py")
    print("  Terminal 2: python beari2.py")
    print("  Browser:    http://127.0.0.1:5000")
    print()
    print("="*70)
    print()
    
    choice = input("Would you like to start the chat now? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n🚀 Starting Beari2 chat interface...\n")
        from beari2 import main as chat_main
        chat_main()
    else:
        print("\n👋 Setup complete! Run 'python beari2.py' when ready.")
        print("   Or run 'python viewer/app.py' to start the viewer first.\n")


if __name__ == "__main__":
    main()
