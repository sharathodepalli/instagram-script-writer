#!/usr/bin/env python
"""Test Pinecone connection and setup."""

import os
import sys
from pinecone import Pinecone, ServerlessSpec

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.config import (
    PINECONE_API_KEY, 
    PINECONE_INDEX, 
    PINECONE_REGION,
    PINECONE_DIMENSIONS,
    PINECONE_METRIC,
    logger
)

def test_pinecone_connection():
    """Test Pinecone connection and create index if needed."""
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        print(f"✅ Successfully connected to Pinecone with API key: {PINECONE_API_KEY[:10]}...")
        
        # List existing indexes
        indexes = pc.list_indexes()
        print(f"📋 Existing indexes: {[idx.name for idx in indexes]}")
        
        # Check if our index exists
        if PINECONE_INDEX not in [idx.name for idx in indexes]:
            print(f"❌ Index '{PINECONE_INDEX}' does not exist. Creating it...")
            
            # Create the index
            pc.create_index(
                name=PINECONE_INDEX,
                dimension=PINECONE_DIMENSIONS,
                metric=PINECONE_METRIC,
                spec=ServerlessSpec(
                    cloud='aws',
                    region=PINECONE_REGION
                )
            )
            print(f"✅ Created index '{PINECONE_INDEX}'")
        else:
            print(f"✅ Index '{PINECONE_INDEX}' already exists")
            
        # Test accessing the index
        index = pc.Index(PINECONE_INDEX)
        stats = index.describe_index_stats()
        print(f"📊 Index stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return False

def main():
    """Main function."""
    print("Testing Pinecone connection...")
    print(f"API Key: {PINECONE_API_KEY[:10]}...")
    print(f"Index: {PINECONE_INDEX}")
    print(f"Region: {PINECONE_REGION}")
    print(f"Dimensions: {PINECONE_DIMENSIONS}")
    
    success = test_pinecone_connection()
    
    if success:
        print("\n🎉 Pinecone setup is working correctly!")
    else:
        print("\n💥 Pinecone setup failed. Please check your API key and configuration.")

if __name__ == "__main__":
    main()
