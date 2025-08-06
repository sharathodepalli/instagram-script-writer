import os
import subprocess
import sys

def main():
    """Robust startup script for Render deployment"""
    
    # Set production mode to skip environment variable validation
    os.environ['PRODUCTION_MODE'] = '1'
    
    # Set port from environment or default to 8501
    port = os.environ.get('PORT', '8501')
    
    # Ensure the port is accessible
    print(f"Starting Streamlit on port {port}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.executable}")
    
    # Check if the app file exists
    app_file = 'src/app_intelligent.py'
    if not os.path.exists(app_file):
        print(f"ERROR: App file {app_file} not found!")
        print(f"Available files: {os.listdir('.')}")
        if os.path.exists('src'):
            print(f"Files in src: {os.listdir('src')}")
        sys.exit(1)
    
    # Run streamlit with proper configuration
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 
        app_file,
        '--server.port', port,
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run the command
        result = subprocess.run(cmd, check=True)
        print(f"Streamlit exited with code: {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()