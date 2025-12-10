"""
Unit tests for Beari3 abstraction and generalization features
Tests semantic categorization, tense detection, signature generation, and pattern matching
"""

import unittest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.schema import Database
from utils.vocab_manager import VocabularyManager
from utils.semantic_manager import SemanticCategoryManager
from core.analyzer import SentenceAnalyzer
from core.generator import ResponseGenerator
from core.inference import InferenceEngine


class TestSemanticCategorization(unittest.TestCase):
    """Test semantic category management"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db_path = "test_beari3.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        self.db = Database(self.test_db_path)
        self.semantic_manager = SemanticCategoryManager(self.db)
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_add_and_retrieve_category(self):
        """Test adding and retrieving semantic categories"""
        self.semantic_manager.add_category("taco", "FOOD", "meal")
        
        result = self.semantic_manager.get_category("taco")
        self.assertIsNotNone(result)
        self.assertEqual(result['category'], "FOOD")
        self.assertEqual(result['subcategory'], "meal")
    
    def test_category_case_insensitive(self):
        """Test that category lookup is case-insensitive"""
        self.semantic_manager.add_category("Pizza", "FOOD", "meal")
        
        result = self.semantic_manager.get_category("pizza")
        self.assertIsNotNone(result)
        self.assertEqual(result['category'], "FOOD")
    
    def test_common_categories_seeded(self):
        """Test that common categories are pre-seeded"""
        # Check a few common words
        curry = self.semantic_manager.get_category("curry")
        self.assertIsNotNone(curry)
        self.assertEqual(curry['category'], "FOOD")
        
        walk = self.semantic_manager.get_category("walk")
        self.assertIsNotNone(walk)
        self.assertEqual(walk['category'], "ACTIVITY")
        
        movie = self.semantic_manager.get_category("movie")
        self.assertIsNotNone(movie)
        self.assertEqual(movie['category'], "MEDIA")


class TestTenseDetection(unittest.TestCase):
    """Test tense detection in sentences"""
    
    def setUp(self):
        """Set up analyzer"""
        self.test_db_path = "test_beari3.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        self.db = Database(self.test_db_path)
        self.vocab_manager = VocabularyManager(self.db)
        self.semantic_manager = SemanticCategoryManager(self.db)
        self.analyzer = SentenceAnalyzer(self.vocab_manager, self.semantic_manager)
        
        # Seed vocabulary to avoid unknown word prompts
        self.vocab_manager.seed_common_words()
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_past_tense_detection(self):
        """Test detection of past tense"""
        analysis = self.analyzer.analyze("I cooked a curry.")
        self.assertEqual(analysis['tense'], "PAST")
    
    def test_present_tense_detection(self):
        """Test detection of present tense"""
        analysis = self.analyzer.analyze("I cook curry.")
        self.assertEqual(analysis['tense'], "PRESENT")
    
    def test_future_tense_detection(self):
        """Test detection of future tense"""
        analysis = self.analyzer.analyze("I will cook curry.")
        self.assertEqual(analysis['tense'], "FUTURE")


class TestSignatureGeneration(unittest.TestCase):
    """Test pattern signature generation"""
    
    def setUp(self):
        """Set up analyzer"""
        self.test_db_path = "test_beari3.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        self.db = Database(self.test_db_path)
        self.vocab_manager = VocabularyManager(self.db)
        self.semantic_manager = SemanticCategoryManager(self.db)
        self.analyzer = SentenceAnalyzer(self.vocab_manager, self.semantic_manager)
        
        # Seed vocabulary
        self.vocab_manager.seed_common_words()
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_signature_for_food_action(self):
        """Test signature generation for food-related actions"""
        analysis = self.analyzer.analyze("I cooked a curry.")
        
        # Should contain SELF (subject is I), PAST (tense), and FOOD/ACTION_CREATION
        self.assertIn("SELF", analysis['signature'])
        self.assertIn("PAST", analysis['signature'])
        # Should have either FOOD or ACTION_CREATION
        self.assertTrue(
            "FOOD" in analysis['signature'] or "ACTION_CREATION" in analysis['signature']
        )
    
    def test_signature_generalization(self):
        """Test that similar sentences produce similar signatures"""
        analysis1 = self.analyzer.analyze("I ate a burger.")
        analysis2 = self.analyzer.analyze("I ate a pizza.")
        
        # Both should have SELF_PAST and likely FOOD or ACTION_CONSUMPTION
        sig1_parts = set(analysis1['signature'].split('_'))
        sig2_parts = set(analysis2['signature'].split('_'))
        
        # Should share SELF and PAST
        self.assertIn("SELF", sig1_parts)
        self.assertIn("SELF", sig2_parts)
        self.assertIn("PAST", sig1_parts)
        self.assertIn("PAST", sig2_parts)
        
        # Should both be about FOOD
        self.assertTrue(
            "FOOD" in sig1_parts or "ACTION_CONSUMPTION" in sig1_parts
        )
        self.assertTrue(
            "FOOD" in sig2_parts or "ACTION_CONSUMPTION" in sig2_parts
        )


class TestGeneralization(unittest.TestCase):
    """Test response generation and generalization"""
    
    def setUp(self):
        """Set up full system"""
        self.test_db_path = "test_beari3.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        self.db = Database(self.test_db_path)
        self.vocab_manager = VocabularyManager(self.db)
        self.semantic_manager = SemanticCategoryManager(self.db)
        self.analyzer = SentenceAnalyzer(self.vocab_manager, self.semantic_manager)
        self.inference_engine = InferenceEngine(self.db)
        self.generator = ResponseGenerator(self.db, self.analyzer)
        
        # Seed vocabulary
        self.vocab_manager.seed_common_words()
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_template_creation(self):
        """Test that templates are created correctly"""
        analysis = self.analyzer.analyze("I ate a burger.")
        response = "Nice! How was the burger?"
        
        template = self.generator.create_template_from_response(response, analysis)
        
        self.assertIsNotNone(template)
        self.assertIn("{target}", template)
        self.assertEqual(template, "Nice! How was the {target}?")
    
    def test_generalization_across_similar_inputs(self):
        """Test that training on one food item generalizes to another"""
        # Train on curry
        analysis1 = self.analyzer.analyze("I cooked a curry.")
        response1 = "Yum! Did it taste good?"
        inference1 = self.inference_engine.draw_conclusions(analysis1, response1)
        template1 = self.generator.create_template_from_response(response1, analysis1)
        self.inference_engine.save_conversational_unit(analysis1, response1, inference1, template1)
        
        # Now try with taco (different food, same pattern)
        generated_response, confidence, match_info = self.generator.generate_response("I cooked a taco.")
        
        # Should generate something
        self.assertIsNotNone(generated_response)
        self.assertGreater(confidence, 0.0)
        print(f"\n  Generated: {generated_response}")
        print(f"  Confidence: {confidence}")
        print(f"  Match: {match_info}")
    
    def test_exact_match_preferred(self):
        """Test that exact signature matches are preferred"""
        # Train on specific pattern
        analysis = self.analyzer.analyze("I walked in the park.")
        response = "Nice! How was the walk?"
        inference = self.inference_engine.draw_conclusions(analysis, response)
        template = self.generator.create_template_from_response(response, analysis)
        self.inference_engine.save_conversational_unit(analysis, response, inference, template)
        
        # Try exact same pattern
        generated_response, confidence, match_info = self.generator.generate_response("I walked in the park.")
        
        # Should have high confidence (exact match)
        self.assertEqual(confidence, 1.0)
        print(f"\n  Exact match test:")
        print(f"  Generated: {generated_response}")
        print(f"  Confidence: {confidence}")


class TestSentimentAnalysis(unittest.TestCase):
    """Test sentiment analysis"""
    
    def setUp(self):
        """Set up analyzer"""
        self.test_db_path = "test_beari3.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        self.db = Database(self.test_db_path)
        self.vocab_manager = VocabularyManager(self.db)
        self.semantic_manager = SemanticCategoryManager(self.db)
        self.analyzer = SentenceAnalyzer(self.vocab_manager, self.semantic_manager)
        
        self.vocab_manager.seed_common_words()
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_positive_sentiment(self):
        """Test detection of positive sentiment"""
        analysis = self.analyzer.analyze("I love this great movie!")
        self.assertGreater(analysis['sentiment'], 0)
    
    def test_negative_sentiment(self):
        """Test detection of negative sentiment"""
        analysis = self.analyzer.analyze("I hate this terrible movie.")
        self.assertLess(analysis['sentiment'], 0)
    
    def test_neutral_sentiment(self):
        """Test detection of neutral sentiment"""
        analysis = self.analyzer.analyze("I watched a movie.")
        # Should be close to zero
        self.assertGreaterEqual(analysis['sentiment'], -0.2)
        self.assertLessEqual(analysis['sentiment'], 0.2)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSemanticCategorization))
    suite.addTests(loader.loadTestsFromTestCase(TestTenseDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestSignatureGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestGeneralization))
    suite.addTests(loader.loadTestsFromTestCase(TestSentimentAnalysis))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
