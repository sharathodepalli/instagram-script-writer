#!/usr/bin/env python
"""Test script to verify Pinecone connection and embedding functionality."""

import pytest
import pinecone
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone as LC_Pinecone
from langchain.schema import Document
import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    PINECONE_API_KEY,
    PINECONE_HOST,
    PINECONE_INDEX,
    PINECONE_REGION,
    EMBEDDING_MODEL,
    logger
)

def test_pinecone_connection():
    """Test the Pinecone connection and embedding functionality."""
    try:
        logger.info(f"Testing connection to Pinecone at {PINECONE_HOST}")
        logger.info(f"Using embedding model: {EMBEDDING_MODEL}")

        # Initialize Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Initialize the embedder
        embedder = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        # Create a test document
        test_doc = Document(
            page_content="This is a test document for Instagram Script-Writer.",
            metadata={"source": "test", "date": "2025-08-05"}
        )
        
        logger.info("Creating a test vector in Pinecone...")
        
        # Get the Pinecone index
        index = pc.Index(PINECONE_INDEX)
        
        # Create a vector store with the test document
        vector_store = LC_Pinecone.from_documents(
            [test_doc],
            embedder,
            index_name=PINECONE_INDEX,
            namespace="test"
        )
        
        logger.info("Test vector created successfully. Attempting a similarity search...")
        
        # Query the vector store
        results = vector_store.similarity_search("test instagram", k=1)
        
        if results:
            logger.info(f"✅ Search successful! Found {len(results)} results.")
            logger.info(f"First result: {results[0].page_content}")
            return True
        else:
            logger.error("❌ Search returned no results.")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_pinecone_connection()
    if success:
        logger.info("✅ Pinecone connection test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Pinecone connection test failed.")
        sys.exit(1)
