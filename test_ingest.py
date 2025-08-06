#!/usr/bin/env python
"""Test script ingestion into Pinecone."""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ingest import ScriptIngester

def test_ingestion():
    """Test ingesting sample scripts into Pinecone."""
    try:
        print("🔄 Initializing Script Ingester...")
        ingester = ScriptIngester()
        
        print("📂 Loading scripts from scripts/ directory...")
        documents = ingester.load_scripts()
        
        if not documents:
            print("❌ No scripts found to ingest")
            return
            
        print(f"📝 Found {len(documents)} scripts to ingest")
        for i, doc in enumerate(documents, 1):
            print(f"  {i}. {doc.metadata.get('source', 'Unknown')} ({len(doc.page_content)} chars)")
        
        print("🚀 Starting ingestion into Pinecone...")
        ingester.create_index(documents)
        
        print("✅ Ingestion completed successfully!")
        print("🎉 Your Pinecone index 'scriptwriter' now contains sample scripts for retrieval.")
        
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ingestion()
