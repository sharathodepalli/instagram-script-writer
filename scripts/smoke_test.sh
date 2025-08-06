#!/bin/bash

echo "==== Instagram Script-Writer Smoke Test ===="
echo "This script will run tests to verify your setup is working correctly."

# Check Python and dependencies
echo -e "\n1. Checking Python and dependencies..."
python -c "import sys; print(f'Python version: {sys.version}')" || { echo "Python check failed!"; exit 1; }
python -c "import langchain, langchain_community, pinecone, sentence_transformers, streamlit; print('All dependencies available')" || { echo "Dependency check failed!"; exit 1; }

# Test Pinecone connection
echo -e "\n2. Testing Pinecone connection..."
python tests/test_pinecone.py || { echo "Pinecone connection test failed!"; exit 1; }

# Run ingestion
echo -e "\n3. Running script ingestion..."
python src/ingest.py || { echo "Ingestion failed!"; exit 1; }

# Generate a test script
echo -e "\n4. Generating a test script..."
echo "travel tips" | python src/generator.py || { echo "Script generation failed!"; exit 1; }

echo -e "\n✅ All tests passed! Your Instagram Script-Writer setup is working correctly."
echo "You can now run the Streamlit app with: streamlit run src/app.py"
