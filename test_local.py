"""
Test script to verify the functionality of the ScriptGenerator class.
"""

import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generator import ScriptGenerator

def test_script_generator():
    """Test the ScriptGenerator class directly."""
    try:
        print("Initializing ScriptGenerator...")
        generator = ScriptGenerator()
        print("Successfully initialized ScriptGenerator!")
        
        # Test generating a script
        print("\nGenerating a test script...")
        topic = "Healthy breakfast ideas"
        result = generator.generate_script(topic, use_retrieval=False)
        
        if result["success"]:
            print(f"Successfully generated script for topic: {topic}")
            print("\nScript preview:")
            print("=" * 50)
            print(result["script"][:500] + "...")  # Show first 500 chars
            print("=" * 50)
        else:
            print(f"Failed to generate script: {result['error']}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_script_generator()
