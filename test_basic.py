#!/usr/bin/env python
"""Test script generation without Pinecone retrieval."""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.generator import ScriptGenerator

def test_without_retrieval():
    """Test script generation without using Pinecone retrieval."""
    try:
        print("Testing script generation without retrieval...")
        
        # Create generator (this will still try to connect to Pinecone but won't fail the whole process)
        try:
            generator = ScriptGenerator()
        except Exception as pinecone_error:
            print(f"⚠️  Pinecone connection failed: {pinecone_error}")
            print("🔄 Continuing with basic generation (no retrieval)...")
            # We'll create a mock generator for testing
            return test_basic_openai_only()
        
        # Test generation without retrieval
        topic = "morning routine tips"
        result = generator.generate_script(topic, use_retrieval=False)
        
        if result["success"]:
            print(f"\n✅ Script generated successfully for: {topic}")
            print("=" * 50)
            print(result["script"])
            print("=" * 50)
            return True
        else:
            print(f"❌ Generation failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_basic_openai_only():
    """Test just the OpenAI API call."""
    import openai
    from src.config import OPENAI_API_KEY, MODEL_FINE_TUNED
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=MODEL_FINE_TUNED,
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are a creative Instagram content creator."},
                {"role": "user", "content": "Write a short Instagram reel script about morning routine tips. Include HOOK, BODY, CTA sections."}
            ]
        )
        
        script = response.choices[0].message.content
        print("\n✅ OpenAI API is working! Generated script:")
        print("=" * 50)
        print(script)
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def main():
    """Main function."""
    print("🧪 Testing Instagram Script Writer without Pinecone...")
    
    success = test_without_retrieval()
    
    if success:
        print("\n🎉 Basic functionality is working!")
        print("\n📝 Next steps:")
        print("1. Get a valid Pinecone API key from https://app.pinecone.io/")
        print("2. Update the PINECONE_API_KEY in your .env file")
        print("3. Run the full application with retrieval enabled")
    else:
        print("\n💥 Test failed. Please check your OpenAI API key.")

if __name__ == "__main__":
    main()
