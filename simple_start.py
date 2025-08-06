import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Get port from environment
port = os.environ.get('PORT', '8501')

print(f"Starting on port {port}")
print(f"Current directory: {os.getcwd()}")

# Check if app file exists
app_file = os.path.join('src', 'app_intelligent.py')
if not os.path.exists(app_file):
    print(f"ERROR: {app_file} not found!")
    print("Available files:")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                print(f"  {os.path.join(root, file)}")
    sys.exit(1)

# Start streamlit directly
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    sys.argv = [
        "streamlit",
        "run", 
        app_file,
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ]
    
    stcli.main()