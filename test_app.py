import streamlit as st
import os

st.title("Test App - Instagram Script Writer")
st.write("If you can see this, Streamlit is working!")

# Show environment info
st.write("## Environment Info")
st.write(f"Port: {os.environ.get('PORT', 'Not set')}")
st.write(f"Current directory: {os.getcwd()}")

# Test imports
st.write("## Import Tests")
try:
    import openai
    st.success("OpenAI imported successfully")
except Exception as e:
    st.error(f"OpenAI import failed: {e}")

try:
    from pinecone import Pinecone
    st.success("Pinecone imported successfully") 
except Exception as e:
    st.error(f"Pinecone import failed: {e}")

try:
    from src.intelligent_script_engine import IntelligentScriptEngine
    st.success("Main app components imported successfully")
except Exception as e:
    st.error(f"Main app import failed: {e}")

st.write("## Next Steps")
st.write("If all imports are successful, the main app should work.")
st.write("Try changing start command to use the main app: `python simple_start.py`")