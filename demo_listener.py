"""
Simple Demo of Beari Listener Mode
Shows the parser and question generator in action.
"""

from listener import Listener


def demo_conversation():
    """Run a scripted demo conversation."""
    print("="*60)
    print("BEARI LISTENER MODE - DEMO")
    print("="*60)
    print("\nThis demo shows how Beari learns from conversation.\n")
    
    with Listener() as listener:
        # Check initial stats
        stats = listener.get_vocabulary_stats()
        print(f"Starting vocabulary: {stats['vocabulary_size']} words\n")
        print("-"*60)
        
        # Conversation 1: Unknown word
        print("\nYou: The capybara loves to swim")
        result1 = listener.process_input("The capybara loves to swim")
        
        if result1['type'] == 'question':
            print(f"Beari: {result1['question']}")
            print("\nYou: It's a large rodent, an animal from South America")
            result2 = listener.process_input("It's a large rodent, an animal from South America")
            print(f"Beari: {result2['message']}")
        
        print("\n" + "-"*60)
        
        # Conversation 2: Another unknown word
        print("\nYou: Python is a versatile programming language")
        result3 = listener.process_input("Python is a versatile programming language")
        
        if result3['type'] == 'question':
            print(f"Beari: {result3['question']}")
            print("\nYou: It's related to technology and coding")
            result4 = listener.process_input("It's related to technology and coding")
            print(f"Beari: {result4['message']}")
        
        print("\n" + "-"*60)
        
        # Conversation 3: Known words (if we added them)
        print("\nYou: I love to code")
        result5 = listener.process_input("I love to code")
        
        if result5['type'] == 'question':
            print(f"Beari: {result5['question']}")
        elif result5['type'] == 'understood':
            print(f"Beari: {result5['message']}")
        
        # Final stats
        print("\n" + "="*60)
        final_stats = listener.get_vocabulary_stats()
        print(f"\nFinal vocabulary: {final_stats['vocabulary_size']} words")
        print(f"Words learned this session: {final_stats['vocabulary_size'] - stats['vocabulary_size']}")
        print(f"Total relations: {final_stats['total_relations']}")
        print("\n" + "="*60)
        print("\nDemo complete! Run 'python listener.py' for interactive mode.")


if __name__ == "__main__":
    demo_conversation()
