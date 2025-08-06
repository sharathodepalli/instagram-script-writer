#!/usr/bin/env python3
"""
Render Startup Script for Instagram Script Writer
Ensures proper startup with all dependencies loaded
"""
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys
    
    # Set the streamlit app file
    sys.argv = [
        "streamlit", 
        "run", 
        "src/app_intelligent.py",
        "--server.port=" + os.environ.get("PORT", "8501"),
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false"
    ]
    
    # Run streamlit
    sys.exit(stcli.main())