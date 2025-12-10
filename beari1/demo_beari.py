"""
Demo Script for Complete Beari AI System
Shows Listener, Orator, and Corrector working together.
"""

from beari import BeariAI
from db.db_helpers import DatabaseHelper


def demo_conversation():
    """Run a scripted demo showing all of Beari's capabilities."""
    print("="*70)
    print("🐻 BEARI AI - COMPLETE SYSTEM DEMO")
    print("="*70)
    print("\nThis demo shows:")
    print("  ✓ Learning from conversation (Listener)")
    print("  ✓ Answering questions (Orator)")
    print("  ✓ Handling corrections (Corrector)")
    print("\n" + "="*70 + "\n")
    
    with BeariAI() as beari:
        # Show initial stats
        stats = beari.listener.get_vocabulary_stats()
        print(f"Starting vocabulary: {stats['vocabulary_size']} words\n")
        
        # ===== PART 1: LEARNING MODE =====
        print("="*70)
        print("PART 1: Learning from Conversation")
        print("="*70)
        
        conversations = [
            "The elephant is a large animal",
            "Elephants can trumpet loudly",
            "They live in Africa and Asia"
        ]
        
        for conv in conversations:
            print(f"\n🧑 You: {conv}")
            result = beari.process_input(conv)
            
            if result.get('type') == 'question':
                print(f"🐻 Beari: {result['question']}")
                
                # Simulate user answer
                if 'elephant' in conv.lower():
                    answer = "It's a large mammal"
                    print(f"\n🧑 You: {answer}")
                    result = beari.process_input(answer)
                    print(f"🐻 Beari: {result['message']}")
            elif result.get('message'):
                print(f"🐻 Beari: {result['message']}")
        
        # ===== PART 2: QUESTION ANSWERING =====
        print("\n" + "="*70)
        print("PART 2: Answering Questions")
        print("="*70)
        
        questions = [
            "What is dog?",
            "What does robot do?",
            "Tell me about python",
            "Can a dog run?",
            "Is cat an animal?"
        ]
        
        for question in questions:
            print(f"\n🧑 You: {question}")
            result = beari.process_input(question)
            print(f"🐻 Beari: {result['message']}")
        
        # ===== PART 3: CORRECTIONS =====
        print("\n" + "="*70)
        print("PART 3: Learning from Corrections")
        print("="*70)
        
        # First, Beari says something (might be wrong)
        print("\n🧑 You: What is python?")
        result = beari.process_input("What is python?")
        print(f"🐻 Beari: {result['message']}")
        
        # User corrects if wrong
        if 'animal' in result['message'].lower():
            print("\n🧑 You: That's wrong! Python is not an animal, it's a programming language.")
            result = beari.process_input("That's wrong! Python is not an animal.")
            print(f"🐻 Beari: {result['message']}")
            
            # Ask again to confirm correction
            print("\n🧑 You: What is python?")
            result = beari.process_input("What is python?")
            print(f"🐻 Beari: {result['message']}")
        
        # Another correction scenario
        print("\n" + "-"*70)
        print("\n🧑 You: Can a cat fly?")
        result = beari.process_input("Can a cat fly?")
        print(f"🐻 Beari: {result['message']}")
        
        if 'yes' in result['message'].lower() or 'can' in result['message'].lower():
            print("\n🧑 You: No! Cats cannot fly.")
            result = beari.process_input("No! Cats cannot fly.")
            print(f"🐻 Beari: {result['message']}")
        
        # ===== PART 4: SENTENCE GENERATION =====
        print("\n" + "="*70)
        print("PART 4: Sentence Generation")
        print("="*70)
        
        print("\n🧑 You: generate")
        for i in range(3):
            result = beari.process_input("generate")
            print(f"🐻 Beari: {result['message']}")
        
        # ===== FINAL STATS =====
        print("\n" + "="*70)
        print("FINAL STATISTICS")
        print("="*70)
        
        result = beari.process_input("stats")
        print(result['message'])
        
        print("\n" + "="*70)
        print("✓ Demo Complete!")
        print("="*70)
        print("\nRun 'python beari.py' to chat with Beari interactively!")


def test_all_features():
    """Test all major features of Beari."""
    print("\n" + "="*70)
    print("🧪 BEARI AI - FEATURE TEST SUITE")
    print("="*70)
    
    with BeariAI() as beari:
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Learning unknown word
        print("\n[Test 1] Learning Mode - Unknown Word")
        tests_total += 1
        result = beari.process_input("The giraffe is tall")
        if 'giraffe' in result.get('question', '').lower() or result.get('type') == 'question':
            print("  ✓ Correctly identified unknown word")
            tests_passed += 1
        else:
            print("  ✗ Failed to identify unknown word")
        
        # Test 2: Question answering
        print("\n[Test 2] Question Answering - Known Word")
        tests_total += 1
        result = beari.process_input("What is dog?")
        if result.get('type') == 'answer' or 'dog' in result.get('message', '').lower():
            print("  ✓ Successfully answered question")
            tests_passed += 1
        else:
            print("  ✗ Failed to answer question")
        
        # Test 3: Correction detection
        print("\n[Test 3] Correction Detection")
        tests_total += 1
        # First ask a question to set context
        beari.process_input("What is robot?")
        # Then make a correction
        result = beari.process_input("That's wrong!")
        if result.get('type') in ['corrected', 'clarification_needed']:
            print("  ✓ Correctly detected correction")
            tests_passed += 1
        else:
            print("  ✗ Failed to detect correction")
        
        # Test 4: Sentence generation
        print("\n[Test 4] Sentence Generation")
        tests_total += 1
        result = beari.process_input("generate")
        if result.get('type') == 'generated' and result.get('message'):
            print(f"  ✓ Generated: {result['message']}")
            tests_passed += 1
        else:
            print("  ✗ Failed to generate sentence")
        
        # Test 5: Stats command
        print("\n[Test 5] Statistics Command")
        tests_total += 1
        result = beari.process_input("stats")
        if result.get('type') == 'stats' and 'vocabulary' in result.get('message', '').lower():
            print("  ✓ Stats command works")
            tests_passed += 1
        else:
            print("  ✗ Stats command failed")
        
        # Test 6: Help command
        print("\n[Test 6] Help Command")
        tests_total += 1
        result = beari.process_input("help")
        if result.get('type') == 'help' and 'help' in result.get('message', '').lower():
            print("  ✓ Help command works")
            tests_passed += 1
        else:
            print("  ✗ Help command failed")
        
        # Summary
        print("\n" + "="*70)
        print(f"TEST RESULTS: {tests_passed}/{tests_total} tests passed")
        print("="*70)
        
        if tests_passed == tests_total:
            print("✅ All tests passed!")
        else:
            print(f"⚠️  {tests_total - tests_passed} test(s) failed")


def main():
    """Run both demo and tests."""
    print("\n" + "🐻"*35)
    print("BEARI AI - DEMONSTRATION & TESTING")
    print("🐻"*35)
    
    # First run the demo
    demo_conversation()
    
    # Pause before tests
    print("\n\nPress Enter to run feature tests...")
    input()
    
    # Run tests
    test_all_features()
    
    print("\n\n" + "="*70)
    print("All demos and tests complete!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Run 'python beari.py' for interactive chat")
    print("  2. Run 'python view_db.py' to inspect the database")
    print("  3. Try teaching Beari new things and correcting mistakes!")
    print("\n")


if __name__ == "__main__":
    main()
