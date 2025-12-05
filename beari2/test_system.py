"""
Quick test to verify Beari2 system is working.
"""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Beari2 components...\n")

# Test 1: Database
print("✓ Testing database...")
from db import DatabaseConnection, create_object, add_property, get_object, get_properties
with DatabaseConnection("beari2.db") as db:
    print("  ✓ Database connection successful")

# Test 2: LivingObject
print("✓ Testing LivingObject...")
from models.living_object import LivingObject
obj = LivingObject("test", "Noun")
obj.add_property("is", "example")
print(f"  ✓ Created object: {obj.word}")

# Test 3: ObjectManager
print("✓ Testing ObjectManager...")
from core.object_manager import ObjectManager
manager = ObjectManager("beari2.db")
test_obj = manager.create_or_get("dog", "Noun")
test_obj.add_property("is", "animal")
manager.save_object(test_obj)
print(f"  ✓ Saved object to database: {test_obj.word}")

# Test 4: Gap Analysis
print("✓ Testing Gap Analysis...")
from core.gap_analysis import find_learning_opportunity, calculate_completeness
gap = find_learning_opportunity(test_obj)
completeness = calculate_completeness(test_obj)
print(f"  ✓ Found gap: {gap}, Completeness: {completeness:.1%}")

# Test 5: Parser
print("✓ Testing Parser...")
from utils.input_parser import InputParser
parser = InputParser()
parsed = parser.parse_sentence("A dog is an animal")
print(f"  ✓ Parsed sentence - Subject: {parsed['subject']}, Verb: {parsed['verb']}, Object: {parsed['object']}")

# Test 6: Question Generator
print("✓ Testing Question Generator...")
from core.question_generator import generate_question
question = generate_question("dog", "can_do", "Noun")
print(f"  ✓ Generated question: {question}")

print("\n" + "="*70)
print("🎉 All tests passed! Beari2 is ready to use.")
print("="*70)
print("\nNext steps:")
print("  1. Run 'python beari2.py' to start chatting")
print("  2. Run 'python viewer/app.py' to start the real-time viewer")
print("  3. Run 'python demo.py' for an interactive demo")
print()
