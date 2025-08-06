#!/usr/bin/env python
"""Setup script to ingest sample scripts into Pinecone."""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ingest import ScriptIngester
from src.config import logger

def setup_sample_scripts():
    """Ingest sample scripts into Pinecone."""
    try:
        print("🚀 Setting up sample scripts in Pinecone...")
        
        # Initialize ingester
        ingester = ScriptIngester()
        
        # Load scripts from the scripts directory
        print("📚 Loading scripts from scripts directory...")
        docs = ingester.load_scripts(include_telugu=False)
        
        if not docs:
            print("❌ No scripts found to ingest. Make sure you have .txt files in the 'scripts' directory.")
            return False
        
        print(f"📖 Found {len(docs)} script documents")
        
        # Ingest documents
        print("🔄 Ingesting scripts into Pinecone...")
        result = ingester.ingest_documents(docs)
        
        if result:
            print(f"✅ Successfully ingested {len(docs)} scripts into Pinecone!")
            print("\n🎉 Your Pinecone index is now ready with sample scripts!")
            print("\nNext steps:")
            print("1. Open the Streamlit app: http://localhost:8503")
            print("2. Go to the 'Generate Script' page")
            print("3. Enter a topic and generate your first script!")
            return True
        else:
            print("❌ Failed to ingest scripts")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        logger.error(f"Setup error: {e}")
        return False

def main():
    """Main function."""
    print("Instagram Script-Writer Setup")
    print("=" * 40)
    
    success = setup_sample_scripts()
    
    if success:
        print("\n🎊 Setup complete! Your application is ready to use.")
    else:
        print("\n💥 Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
