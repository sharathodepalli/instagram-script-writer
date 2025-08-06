"""
Main entry point for running the Enhanced Instagram Script-Writer application.
"""
import os
import sys
import streamlit.web.cli as stcli

def main():
    # Add the current directory to the path so modules can be found
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Set PYTHONPATH to include current directory
    os.environ['PYTHONPATH'] = os.path.abspath(os.path.dirname(__file__))
    
    # Check if enhanced app is available, fallback to original
    enhanced_app_path = "src/enhanced_app.py"
    original_app_path = "src/app.py"
    
    if os.path.exists(enhanced_app_path):
        app_to_run = enhanced_app_path
        print("🚀 Starting Enhanced Instagram Script Writer Pro...")
    else:
        app_to_run = original_app_path
        print("⚡ Starting Instagram Script Writer (Basic)...")
    
    # Run the Streamlit app
    sys.argv = ["streamlit", "run", app_to_run, "--server.port=8502"]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
