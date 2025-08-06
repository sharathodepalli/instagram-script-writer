#!/usr/bin/env python3
import os
import sys
import subprocess
import time

def debug_start():
    print("=== RENDER DEBUG STARTUP ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    # Check environment
    print("\n=== ENVIRONMENT VARIABLES ===")
    port = os.environ.get('PORT', '8501')
    print(f"PORT: {port}")
    print(f"OPENAI_API_KEY: {'SET' if os.environ.get('OPENAI_API_KEY') else 'NOT SET'}")
    print(f"PINECONE_API_KEY: {'SET' if os.environ.get('PINECONE_API_KEY') else 'NOT SET'}")
    
    # Check file structure
    print("\n=== FILE STRUCTURE ===")
    print("Files in current directory:")
    for item in os.listdir('.'):
        print(f"  {item}")
    
    print("\nFiles in src directory:")
    if os.path.exists('src'):
        for item in os.listdir('src'):
            print(f"  src/{item}")
    else:
        print("  src directory NOT FOUND!")
        
    # Check if main app exists
    app_file = 'src/app_intelligent.py'
    print(f"\nMain app file '{app_file}': {'EXISTS' if os.path.exists(app_file) else 'NOT FOUND'}")
    
    # Try importing streamlit
    print("\n=== DEPENDENCY CHECK ===")
    try:
        import streamlit
        print(f"Streamlit version: {streamlit.__version__}")
    except ImportError as e:
        print(f"Streamlit import failed: {e}")
        return False
        
    # Try starting streamlit
    print("\n=== STARTING STREAMLIT ===")
    if not os.path.exists(app_file):
        print("ERROR: App file not found, cannot start!")
        return False
    
    cmd = [
        sys.executable, '-m', 'streamlit', 'run',
        app_file,
        '--server.port', port,
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'false'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("Starting Streamlit...")
    
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"Failed to start Streamlit: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = debug_start()
    if not success:
        print("\n=== STARTUP FAILED ===")
        sys.exit(1)