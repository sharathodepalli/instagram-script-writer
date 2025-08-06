#!/usr/bin/env python
"""Script to ingest sample scripts into Pinecone database."""

import os
import sys

# Ensure we're in the correct directory
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

# Add the project root to Python path
sys.path.insert(0, current_dir)

from src.ingest import ScriptIngester

def main():
    """Main function to run script ingestion."""
    try:
        print("🚀 Starting script ingestion into Pinecone...")
        
        ingester = ScriptIngester()
        
        # Ingest scripts from the scripts directory
        scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
        
        if not os.path.exists(scripts_dir):
            print(f"❌ Scripts directory not found: {scripts_dir}")
            return
        
        # Use the main ingest method which handles file loading
        result = ingester.ingest(scripts_dir, include_telugu=False)
        
        if result["success"]:
            print(f"🎉 {result['message']}")
            print(f"� Processed {result['documents_processed']} documents")
            if 'chunks_created' in result:
                print(f"📝 Created {result['chunks_created']} document chunks")
            print("Your vector database is now ready for retrieval-augmented generation!")
        else:
            print(f"❌ Failed: {result['message']}")
            if 'error' in result:
                print(f"Error details: {result['error']}")
        
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")

if __name__ == "__main__":
    main()
