#!/usr/bin/env python
"""Debug Pinecone index connection."""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings

def debug_pinecone_connection():
    """Debug what index we're actually connecting to."""
    
    print("🔍 Debugging Pinecone connection...")
    
    # Get configuration
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX", "scriptwriter-384")
    
    print(f"📊 Configuration:")
    print(f"  - API Key: {api_key[:10]}...")
    print(f"  - Index Name: {index_name}")
    
    # Initialize Pinecone
    pc = Pinecone(api_key=api_key)
    
    # List all indexes
    print(f"\n📋 Available indexes:")
    indexes = pc.list_indexes()
    for index in indexes:
        print(f"  - {index.name}: {index.dimension} dimensions")
    
    # Try to get stats for our target index
    try:
        print(f"\n🎯 Connecting to index: {index_name}")
        index = pc.Index(index_name)
        stats = index.describe_index_stats()
        print(f"  - Index stats: {stats}")
        
        # Test embeddings
        print(f"\n🧠 Testing embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        test_vector = embeddings.embed_query("test")
        print(f"  - Embedding dimension: {len(test_vector)}")
        
        # Test vector store creation
        print(f"\n🏪 Testing vector store creation...")
        vectorstore = PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings,
            pinecone_api_key=api_key
        )
        print(f"  - Vector store created successfully!")
        
        # Try a simple upsert test
        print(f"\n⬆️ Testing document addition...")
        from langchain.schema import Document
        test_doc = Document(page_content="This is a test document", metadata={"source": "test"})
        vectorstore.add_documents([test_doc])
        print(f"  - Document added successfully!")
        
        print(f"\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pinecone_connection()
