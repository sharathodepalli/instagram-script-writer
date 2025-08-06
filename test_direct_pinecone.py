#!/usr/bin/env python
"""Test direct Pinecone ingestion without langchain-pinecone."""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.ingest import ScriptIngester
import uuid

def direct_pinecone_test():
    """Test ingestion using direct Pinecone client."""
    
    print("🔧 Testing direct Pinecone ingestion...")
    
    # Initialize components
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = "scriptwriter-384"
    
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load scripts using existing ingester
    ingester = ScriptIngester()
    documents = ingester.load_scripts()
    
    if not documents:
        print("❌ No documents found")
        return
        
    print(f"📝 Found {len(documents)} documents to ingest")
    
    # Prepare vectors for direct upsert
    vectors = []
    for i, doc in enumerate(documents):
        vector_id = f"script_{i}_{str(uuid.uuid4())[:8]}"
        embedding = embeddings.embed_query(doc.page_content)
        
        vector = {
            "id": vector_id,
            "values": embedding,
            "metadata": {
                "text": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "content_type": "instagram_script"
            }
        }
        vectors.append(vector)
        
        print(f"  {i+1}. {vector_id}: {len(embedding)} dimensions")
    
    # Direct upsert to Pinecone
    try:
        print(f"\n🚀 Upserting {len(vectors)} vectors to {index_name}...")
        upsert_response = index.upsert(vectors=vectors)
        print(f"✅ Successfully upserted: {upsert_response}")
        
        # Verify the upsert
        stats = index.describe_index_stats()
        print(f"📊 Index stats after upsert: {stats}")
        
        # Test a simple query
        print(f"\n🔍 Testing query...")
        query_embedding = embeddings.embed_query("morning routine productivity")
        query_response = index.query(
            vector=query_embedding,
            top_k=2,
            include_metadata=True
        )
        
        print(f"📋 Query results:")
        for match in query_response.matches:
            print(f"  - Score: {match.score:.4f}")
            print(f"    Source: {match.metadata.get('source', 'unknown')}")
            print(f"    Preview: {match.metadata.get('text', '')[:100]}...")
            print()
        
        print("🎉 Direct Pinecone ingestion successful!")
        
    except Exception as e:
        print(f"❌ Direct ingestion failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    direct_pinecone_test()
