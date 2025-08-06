# Testing Guide

This document provides instructions for testing the Instagram Script-Writer application both locally and in Docker.

## Local Testing

### Prerequisites

1. Python 3.9+ installed
2. Required packages installed: `pip install -r requirements.txt`
3. Valid API keys in `.env` file

### Running Tests

1. Run the test suite:

   ```
   python -m pytest tests/
   ```

2. Test specific components:
   ```
   python test_local.py
   ```

### Running the Application Locally

1. Use the run.sh script:

   ```
   ./run.sh
   ```

2. Or run directly with Python:

   ```
   python run_app.py
   ```

3. Open the application in your browser:
   - http://localhost:8502

## Docker Testing

### Prerequisites

1. Docker and Docker Compose installed
2. Valid API keys in `.env` file

### Building and Running the Docker Container

1. Use the run_docker.sh script:

   ```
   ./run_docker.sh
   ```

2. Or run the Docker commands manually:

   ```
   docker-compose build
   docker-compose up
   ```

3. Open the application in your browser:
   - http://localhost:8501

## Troubleshooting

### Common Issues

1. **Module Not Found Errors**

   - Check your Python path and make sure you're running from the project root directory
   - Try using the `run_app.py` script which sets up the correct import paths

2. **API Authentication Errors**

   - Verify your API keys in the `.env` file
   - Check for any environment-specific configuration in `config.py`

3. **Embedding Model Errors**

   - The application now defaults to using `all-MiniLM-L6-v2` model
   - If you want to use a different model, make sure it's accessible (some models require authentication)

4. **Docker Issues**
   - Verify Docker is running
   - Check logs with `docker-compose logs`
   - Make sure ports 8501/8502 are not in use by other applications
