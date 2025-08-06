import os
import subprocess
import sys

def main():
    """Simple startup script for Render deployment"""
    
    # Set port from environment or default to 8501
    port = os.environ.get('PORT', '8501')
    
    # Run streamlit with proper configuration
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 
        'src/app_intelligent.py',
        '--server.port', port,
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false'
    ]
    
    print(f"Starting Streamlit on port {port}")
    print(f"Command: {' '.join(cmd)}")
    
    # Run the command
    subprocess.run(cmd)

if __name__ == "__main__":
    main()