#!/usr/bin/env python3
"""
Launch the Intelligent Instagram Script Writer
The REAL system that understands users deeply and generates personalized viral content
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the intelligent script writer."""
    
    current_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(current_dir))
    os.environ['PYTHONPATH'] = str(current_dir)
    
    print("🧠 Starting Intelligent Instagram Script Writer...")
    print("   The AI that truly understands YOU and creates personalized viral content")
    print("=" * 70)
    
    # Use the intelligent app
    app_to_run = str(current_dir / "src" / "app_intelligent.py")
    
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            app_to_run, 
            "--server.port=8505",
            "--server.headless=false"
        ]
        
        print("🌐 Intelligent App available at: http://localhost:8505")
        print("🔧 Press Ctrl+C to stop")
        print("🎯 Features:")
        print("   • Deep user understanding from stories & example scripts")
        print("   • Personalized content generation based on your patterns")
        print("   • Proper script length for 15s-90s videos")
        print("   • Multi-attempt generation with quality scoring")
        print("   • Viral potential analysis & optimization")
        print("-" * 70)
        
        subprocess.run(cmd, cwd=str(current_dir))
        
    except KeyboardInterrupt:
        print("\n👋 Intelligent Script Writer stopped!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()