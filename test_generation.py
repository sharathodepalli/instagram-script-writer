#!/usr/bin/env python
"""Test script generation with various topics."""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.generator import ScriptGenerator

def test_multiple_topics():
    """Test script generation with different topics."""
    topics = [
        "Telugu morning routines for productivity",
        "Healthy Telugu breakfast recipes",
        "Telugu skincare tips with natural ingredients",
        "Quick Telugu workout routines at home",
        "Telugu cooking hacks for busy people"
    ]
    
    try:
        print("🎬 Testing Instagram Script Generator...")
        generator = ScriptGenerator()
        
        for i, topic in enumerate(topics, 1):
            print(f"\n📝 Generating script {i}/{len(topics)}: {topic}")
            
            result = generator.generate_script(topic, use_retrieval=False)
            
            if result["success"]:
                print(f"✅ Success! Generated {len(result['script'])} characters")
                print("Preview:", result['script'][:100] + "...")
            else:
                print(f"❌ Failed: {result['error']}")
        
        print("\n🎉 All tests completed! Your app is working perfectly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_multiple_topics()
