#!/usr/bin/env python3
"""
Enhanced Instagram Script Writer Launcher
This script properly handles imports and launches the enhanced application.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the enhanced Instagram Script Writer."""
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(current_dir))
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(current_dir)
    
    print("🚀 Starting Enhanced Instagram Script Writer Pro...")
    print(f"📁 Working directory: {current_dir}")
    
    # Check if enhanced app exists
    enhanced_app_path = current_dir / "src" / "enhanced_app.py"
    basic_app_path = current_dir / "src" / "app.py"
    
    if enhanced_app_path.exists():
        app_to_run = str(enhanced_app_path)
        print("✨ Launching Enhanced Version with all viral optimization features!")
    else:
        app_to_run = str(basic_app_path)
        print("⚡ Launching Basic Version")
    
    # Launch Streamlit
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            app_to_run, 
            "--server.port=8502",
            "--server.headless=false",
            "--browser.gatherUsageStats=false"
        ]
        
        print(f"🌐 App will be available at: http://localhost:8502")
        print("🔧 Press Ctrl+C to stop the application")
        print("-" * 50)
        
        subprocess.run(cmd, cwd=str(current_dir))
        
    except KeyboardInterrupt:
        print("\n👋 Instagram Script Writer stopped successfully!")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that you have your API keys in .env file")
        print("3. Try running: streamlit run src/app.py --server.port=8502")

if __name__ == "__main__":
    main()