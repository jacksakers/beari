"""
Demo script for Beari3 abstraction and generalization
Shows how training on one example generalizes to similar inputs
"""

import sys
from db.schema import Database
from utils.vocab_manager import VocabularyManager
from utils.semantic_manager import SemanticCategoryManager
from core.analyzer import SentenceAnalyzer
from core.inference import InferenceEngine
from core.generator import ResponseGenerator


class Beari3Demo:
    def __init__(self, db_path="demo_beari3.db"):
        print("\n" + "=" * 70)
        print("   BEARI3 GENERALIZATION DEMO")
        print("   Watch how training on one example generalizes to others!")
        print("=" * 70)
        
        # Initialize components
        self.db = Database(db_path)
        self.vocab_manager = VocabularyManager(self.db)
        self.semantic_manager = SemanticCategoryManager(self.db)
        self.analyzer = SentenceAnalyzer(self.vocab_manager, self.semantic_manager)
        self.inference_engine = InferenceEngine(self.db)
        self.generator = ResponseGenerator(self.db, self.analyzer)
        
        # Seed vocabulary
        self.vocab_manager.seed_common_words()
        
        print("\n✓ System initialized with semantic abstraction")
    
    def train_example(self, prompt, response):
        """Train on a single example"""
        print("\n" + "─" * 70)
        print("📚 TRAINING EXAMPLE")
        print("─" * 70)
        print(f"User says: \"{prompt}\"")
        print(f"Ideal response: \"{response}\"")
        
        # Analyze
        analysis = self.analyzer.analyze(prompt)
        
        # Draw conclusions
        inference = self.inference_engine.draw_conclusions(analysis, response)
        
        # Create template
        template = self.generator.create_template_from_response(response, analysis)
        
        # Save
        self.inference_engine.save_conversational_unit(analysis, response, inference, template)
        
        print("✓ Training complete!")
    
    def test_generalization(self, test_prompts):
        """Test how the model generalizes to new inputs"""
        print("\n" + "=" * 70)
        print("🧪 TESTING GENERALIZATION")
        print("=" * 70)
        
        for prompt in test_prompts:
            print("\n" + "─" * 70)
            print(f"User says: \"{prompt}\"")
            
            # Generate response
            response, confidence, match_info = self.generator.generate_response(prompt)
            
            if response:
                print(f"Beari3: \"{response}\"")
                print(f"💡 Confidence: {confidence:.0%}")
                print(f"📊 Match: {match_info}")
            else:
                print("Beari3: [No matching pattern found]")
                print(f"💡 {match_info}")
    
    def run_food_demo(self):
        """Demo: Food generalization"""
        print("\n" + "=" * 70)
        print("   DEMO 1: Food Generalization")
        print("=" * 70)
        print("\nScenario: We train on 'curry', test on other foods")
        
        # Train on curry
        self.train_example(
            "I just cooked a spicy curry.",
            "Yum! Did it taste good?"
        )
        
        # Test on other foods
        test_cases = [
            "I just cooked a taco.",
            "I just cooked a pizza.",
            "I just cooked a burger.",
        ]
        
        self.test_generalization(test_cases)
    
    def run_activity_demo(self):
        """Demo: Activity generalization"""
        print("\n" + "=" * 70)
        print("   DEMO 2: Activity Generalization")
        print("=" * 70)
        print("\nScenario: We train on 'walk', test on other activities")
        
        # Train on walk
        self.train_example(
            "I went for a brisk walk.",
            "Nice! How was the walk?"
        )
        
        # Test on other activities
        test_cases = [
            "I went for a run.",
            "I went for a jog.",
            "I went for a swim.",
        ]
        
        self.test_generalization(test_cases)
    
    def run_media_demo(self):
        """Demo: Media consumption generalization"""
        print("\n" + "=" * 70)
        print("   DEMO 3: Media Generalization")
        print("=" * 70)
        print("\nScenario: We train on 'movie', test on other media")
        
        # Train on movie
        self.train_example(
            "I watched a great movie.",
            "Awesome! What movie was it?"
        )
        
        # Test on other media
        test_cases = [
            "I watched a show.",
            "I read a book.",
            "I listened to a podcast.",
        ]
        
        self.test_generalization(test_cases)
    
    def run_tense_demo(self):
        """Demo: Cross-tense generalization"""
        print("\n" + "=" * 70)
        print("   DEMO 4: Cross-Tense Generalization")
        print("=" * 70)
        print("\nScenario: We train on past tense, test on other tenses")
        
        # Train on past
        self.train_example(
            "I ate a burger.",
            "Nice! How was it?"
        )
        
        # Test on different tenses
        test_cases = [
            "I eat burgers.",  # Present
            "I will eat a burger.",  # Future
        ]
        
        self.test_generalization(test_cases)
    
    def run_signature_comparison(self):
        """Show signature comparison"""
        print("\n" + "=" * 70)
        print("   SIGNATURE COMPARISON")
        print("=" * 70)
        print("\nLet's see how different sentences map to signatures:\n")
        
        test_sentences = [
            "I cooked a curry.",
            "I ate a pizza.",
            "I watched a movie.",
            "I went for a walk.",
            "He cooked a burger.",
            "I will cook pasta.",
        ]
        
        for sentence in test_sentences:
            analysis = self.analyzer.analyze(sentence)
            print(f"  \"{sentence}\"")
            print(f"  → {analysis['signature']}")
            print()


def main():
    """Run all demos"""
    import os
    
    # Clean up old demo database
    demo_db = "demo_beari3.db"
    if os.path.exists(demo_db):
        os.remove(demo_db)
    
    demo = Beari3Demo(demo_db)
    
    print("\n" + "=" * 70)
    print("   SELECT DEMO")
    print("=" * 70)
    print("\n1. Food Generalization (curry → taco, pizza, burger)")
    print("2. Activity Generalization (walk → run, jog, swim)")
    print("3. Media Generalization (movie → show, book, podcast)")
    print("4. Tense Generalization (past → present, future)")
    print("5. Signature Comparison (see abstraction in action)")
    print("6. Run ALL demos")
    print("7. Exit")
    
    while True:
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == "1":
            demo.run_food_demo()
        elif choice == "2":
            demo.run_activity_demo()
        elif choice == "3":
            demo.run_media_demo()
        elif choice == "4":
            demo.run_tense_demo()
        elif choice == "5":
            demo.run_signature_comparison()
        elif choice == "6":
            demo.run_food_demo()
            demo.run_activity_demo()
            demo.run_media_demo()
            demo.run_tense_demo()
            demo.run_signature_comparison()
            print("\n" + "=" * 70)
            print("   ALL DEMOS COMPLETE!")
            print("=" * 70)
            break
        elif choice == "7":
            print("\n✓ Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-7.")


if __name__ == "__main__":
    main()
