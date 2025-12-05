"""
Demo script for Beari2
Demonstrates the Living Objects concept with sample interactions.
"""

import os
import sys

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from beari2 import Beari2
from db.init_db import reset_database


def demo_conversation():
    """Run a demo conversation showing Beari2's capabilities."""
    
    print("="*70)
    print("🐻 Beari2 Demo - Living Objects in Action")
    print("="*70)
    print("\nThis demo shows how Beari2 learns by creating Living Objects")
    print("that grow with properties through conversation.\n")
    
    input("Press Enter to start the demo...")
    
    # Reset database for clean demo
    print("\n🔧 Resetting database for demo...")
    reset_database("beari2.db")
    
    # Create Beari2 instance
    beari = Beari2("beari2.db")
    
    # Demo conversation
    demo_inputs = [
        ("A dog is an animal", "Creating 'dog' object with 'is' property"),
        ("Dogs can bark", "Adding 'can_do' property to dog"),
        ("friendly", "Answering Beari's question about what dogs feel like"),
        ("A cat is an animal", "Creating 'cat' object"),
        ("Cats can meow", "Adding capabilities to cat"),
        ("soft", "Answering about cat's feel"),
        ("The sun is bright", "Creating adjective relationship"),
        ("stats", "Checking our knowledge"),
    ]
    
    print("\n" + "="*70)
    print("Starting Demo Conversation")
    print("="*70 + "\n")
    
    for user_input, description in demo_inputs:
        print(f"\n💭 ({description})")
        print(f"🧑 You: {user_input}")
        
        # Process input
        result = beari.process_input(user_input)
        
        # Display response
        if result.get('message'):
            print(f"🐻 Beari: {result['message']}")
        
        if result.get('question'):
            print(f"🐻 Beari: {result['question']}")
        
        # Pause for dramatic effect
        import time
        time.sleep(1.5)
    
    print("\n" + "="*70)
    print("Demo Complete!")
    print("="*70)
    print("\n📊 What happened:")
    print("  • Created Living Objects for: dog, cat, animal, bark, meow, sun, bright")
    print("  • Added dynamic properties: is, can_do, feels_like")
    print("  • Beari asked questions about missing properties")
    print("  • All objects and properties saved to database")
    print()
    print("💡 Next Steps:")
    print("  1. Run 'python viewer/app.py' to see the objects visually")
    print("  2. Run 'python beari2.py' to continue the conversation")
    print("  3. Watch objects grow in real-time as you chat!")
    print()


def show_objects():
    """Show all objects in the database."""
    from core.object_manager import ObjectManager
    
    manager = ObjectManager("beari2.db")
    objects = manager.get_all()
    
    if not objects:
        print("No objects in database yet.")
        return
    
    print("\n" + "="*70)
    print("Living Objects in Database")
    print("="*70 + "\n")
    
    for obj in objects:
        print(f"\n{obj.word.upper()} ({obj.pos})")
        print("-" * 40)
        if obj.properties:
            for relation, values in obj.properties.items():
                print(f"  {relation}: {', '.join(str(v) for v in values)}")
        else:
            print("  (no properties yet)")
    
    print()


if __name__ == "__main__":
    print()
    print("Choose an option:")
    print("  1. Run interactive demo")
    print("  2. Show objects in database")
    print("  3. Exit")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        demo_conversation()
    elif choice == "2":
        show_objects()
    else:
        print("Goodbye!")
