#!/usr/bin/env python
"""Test script generation with retrieval."""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.generator import ScriptGenerator

def test_retrieval_generation():
    """Test script generation with retrieval-augmented generation."""
    try:
        print("🎬 Testing Retrieval-Augmented Script Generation...")
        generator = ScriptGenerator()
        
        # Test topics that should find relevant examples in our ingested scripts
        topics = [
            "morning routine tips",  # Should match our morning_routine_productivity.txt
            "meal preparation hacks",  # Should match our meal_prep_hacks.txt
            "stress management techniques"  # Should match our stress_relief_technique.txt
        ]
        
        for i, topic in enumerate(topics, 1):
            print(f"\n📝 Test {i}/{len(topics)}: {topic}")
            
            # Test with retrieval enabled
            result = generator.generate_script(topic, use_retrieval=True)
            
            if result["success"]:
                print(f"✅ Success with retrieval!")
                print(f"   Script length: {len(result['script'])} characters")
                print(f"   Sources used: {result['source_documents']}")
                print(f"   Preview: {result['script'][:100]}...")
            else:
                print(f"❌ Failed: {result['error']}")
        
        print("\n🎉 Retrieval-augmented generation test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_retrieval_generation()
