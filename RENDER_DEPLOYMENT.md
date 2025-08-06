# Render Deployment Fix for 404 Error

## Current Issue
Getting 404 error on Render deployment. Try these start commands in order:

## Option 1: Simple Python Script
Start Command: `python run.py`

## Option 2: Direct Streamlit
Start Command: `streamlit run src/app_intelligent.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

## Option 3: Python Module
Start Command: `python -m streamlit run src/app_intelligent.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

## Option 4: Alternative Startup
Start Command: `python start.py`

## Option 5: Launch Script  
Start Command: `python launch_intelligent.py`

## Environment Variables Required
- OPENAI_API_KEY
- PINECONE_API_KEY
- PINECONE_HOST
- PINECONE_INDEX=scriptwriter-384
- LANGCHAIN_API_KEY (optional)

## Troubleshooting
1. Check Render build logs for errors
2. Verify environment variables are set
3. Check if port binding is correct
4. Ensure all dependencies install successfully

## Files Added
- run.py - Simple startup script
- Procfile - For alternative deployment
- Updated .streamlit/config.toml - Render-specific config