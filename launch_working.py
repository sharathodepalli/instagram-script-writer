#!/usr/bin/env python3
"""
Working launcher for Instagram Script Writer with enhanced backend
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the working enhanced version."""
    
    current_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(current_dir))
    os.environ['PYTHONPATH'] = str(current_dir)
    
    print("🚀 Starting Instagram Script Writer Pro (Working Version)...")
    
    # Use the working enhanced app
    app_to_run = str(current_dir / "src" / "enhanced_app_working.py")
    
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            app_to_run, 
            "--server.port=8504",
            "--server.headless=false"
        ]
        
        print(f"🌐 App available at: http://localhost:8504")
        print("🔧 Press Ctrl+C to stop")
        print("-" * 50)
        
        subprocess.run(cmd, cwd=str(current_dir))
        
    except KeyboardInterrupt:
        print("\n👋 App stopped!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()