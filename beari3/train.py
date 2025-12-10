"""
Beari3 Training Program
Main training loop implementing the 4-phase cycle:
  1. Prompt Input & Analysis
  2. Gold Standard Response
  3. Inference (Pattern Extraction)
  4. Storage
"""

import sys
from db.schema import Database
from utils.vocab_manager import VocabularyManager
from utils.semantic_manager import SemanticCategoryManager
from core.analyzer import SentenceAnalyzer
from core.inference import InferenceEngine
from core.generator import ResponseGenerator


class Beari3Trainer:
    def __init__(self, db_path="beari3.db"):
        print("\n" + "=" * 50)
        print("   BEARI3 - Supervised Learning Model")
        print("   Watch and Learn System with Abstraction")
        print("=" * 50)
        
        # Initialize components
        self.db = Database(db_path)
        self.vocab_manager = VocabularyManager(self.db)
        self.semantic_manager = SemanticCategoryManager(self.db)
        self.analyzer = SentenceAnalyzer(self.vocab_manager, self.semantic_manager)
        self.inference_engine = InferenceEngine(self.db)
        self.generator = ResponseGenerator(self.db, self.analyzer)
        
        print("\n✓ System initialized with semantic abstraction")
    
    def seed_vocabulary(self):
        """Seed common words to reduce initial friction"""
        print("\nSeeding common vocabulary...")
        self.vocab_manager.seed_common_words()
    
    def training_cycle(self):
        """
        Execute one complete training cycle:
        Phase A: Prompt Analysis
        Phase B: Response Input
        Phase C: Inference
        Phase D: Storage
        """
        print("\n" + "█" * 50)
        print("   NEW TRAINING CYCLE")
        print("█" * 50)
        
        # PHASE A: Prompt Input & Analysis
        print("\n📝 PHASE A: Prompt Analysis")
        print("-" * 50)
        prompt = input("Enter a prompt (what the user would say): ").strip()
        
        if not prompt:
            print("Empty input. Cycle cancelled.")
            return False
        
        # Analyze the prompt
        analysis = self.analyzer.analyze(prompt)
        
        # Handle unknown words and missing semantic categories
        if analysis['unknowns']:
            print(f"\n⚠️  Found {len(analysis['unknowns'])} unknown word(s)")
            choice = input("Would you like to define them now? (y/n): ").strip().lower()
            
            if choice == 'y':
                for word in analysis['unknowns']:
                    self.vocab_manager.add_word_interactive(word)
                print("\n✓ Vocabulary updated")
            else:
                print("⚠️  Skipping vocabulary update (may affect pattern learning)")
        
        # Check if semantic categories are missing
        missing_categories = []
        if analysis['target'] and 'target_category' not in analysis.get('semantic_tags', {}):
            missing_categories.append(analysis['target'])
        if analysis['verb'] and 'verb_category' not in analysis.get('semantic_tags', {}):
            missing_categories.append(analysis['verb'])
        
        if missing_categories:
            print(f"\n🏷️  Some words lack semantic categories: {missing_categories}")
            choice = input("Add semantic categories for better generalization? (y/n): ").strip().lower()
            
            if choice == 'y':
                for word in missing_categories:
                    self.semantic_manager.add_category_interactive(word)
                print("\n✓ Semantic categories updated")
                # Re-analyze to get updated signature
                print("\n🔄 Re-analyzing with new semantic categories...")
                analysis = self.analyzer.analyze(prompt)
            else:
                print("⚠️  Skipping semantic categorization (limits generalization)")
        
        # PHASE B: Gold Standard Response
        print("\n📝 PHASE B: Gold Standard Response")
        print("-" * 50)
        print("Now provide the IDEAL response to this prompt.")
        response = input("Enter the ideal response: ").strip()
        
        if not response:
            print("Empty response. Cycle cancelled.")
            return False
        
        # PHASE C: Inference Engine
        print("\n🧠 PHASE C: Pattern Extraction")
        print("-" * 50)
        inference_result = self.inference_engine.draw_conclusions(analysis, response)
        
        # PHASE D: Storage
        print("\n💾 PHASE D: Storage")
        print("-" * 50)
        
        # Create response template
        response_template = self.generator.create_template_from_response(response, analysis)
        
        self.inference_engine.save_conversational_unit(analysis, response, inference_result, response_template)
        
        print("\n✓ Training cycle complete!")
        return True
    
    def run(self):
        """Main training loop"""
        self.seed_vocabulary()
        
        print("\n" + "=" * 50)
        print("   TRAINING MODE ACTIVE")
        print("=" * 50)
        print("\nInstructions:")
        print("  - Enter prompts and their ideal responses")
        print("  - Beari3 will learn patterns from your examples")
        print("  - Type 'quit' or 'exit' at any prompt to stop")
        print("  - Press Ctrl+C to exit at any time")
        print("\n" + "=" * 50)
        
        cycle_count = 0
        
        try:
            while True:
                success = self.training_cycle()
                if success:
                    cycle_count += 1
                    print(f"\n📊 Completed {cycle_count} training cycle(s)")
                
                print("\n" + "-" * 50)
                continue_training = input("\nContinue training? (y/n): ").strip().lower()
                
                if continue_training != 'y':
                    break
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Training interrupted by user")
        
        print("\n" + "=" * 50)
        print(f"   Training Session Complete")
        print(f"   Total cycles: {cycle_count}")
        print("=" * 50)
        print("\n✓ Data saved to database")


def main():
    """Entry point for training program"""
    trainer = Beari3Trainer()
    trainer.run()


if __name__ == "__main__":
    main()
