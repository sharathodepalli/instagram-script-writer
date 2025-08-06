"""Configuration for the Telugu Reels scraper."""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables if not already loaded
load_dotenv()

# Instagram credentials
INSTA_USERNAME: Optional[str] = os.getenv("INSTA_USERNAME")
INSTA_PASSWORD: Optional[str] = os.getenv("INSTA_PASSWORD")

# Scraping parameters
TARGET_HASHTAG: str = os.getenv("TARGET_HASHTAG", "Telugu")
MAX_FETCH: int = int(os.getenv("MAX_FETCH", "100"))
TOP_N: int = int(os.getenv("TOP_N", "20"))

# File paths
RAW_DIR: str = os.getenv("RAW_DIR", "data/raw_reels")
TOP_CSV: str = os.getenv("TOP_CSV", "data/top_reels.csv")
SCRIPT_DIR: str = os.getenv("SCRIPT_DIR", "scripts/auto_telugu")

# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist."""
    Path(RAW_DIR).mkdir(parents=True, exist_ok=True)
    Path(f"{RAW_DIR}/{TARGET_HASHTAG}").mkdir(parents=True, exist_ok=True)
    Path(os.path.dirname(TOP_CSV)).mkdir(parents=True, exist_ok=True)
    Path(SCRIPT_DIR).mkdir(parents=True, exist_ok=True)

# Validate credentials
def validate_credentials() -> bool:
    """Check if Instagram credentials are provided."""
    return bool(INSTA_USERNAME and INSTA_PASSWORD)

# Validate environment
def validate_environment() -> dict:
    """
    Validate the environment configuration for the scraper.
    
    Returns:
        Dict with validation results and messages
    """
    results = {
        "valid": True,
        "warnings": [],
        "errors": []
    }
    
    # Check credentials
    if not INSTA_USERNAME or not INSTA_PASSWORD:
        results["warnings"].append("Instagram credentials not provided. Running in anonymous mode with limited functionality.")
    
    # Check if directories are writable
    try:
        ensure_directories()
    except PermissionError as e:
        results["valid"] = False
        results["errors"].append(f"Permission error creating directories: {e}")
    
    # Check if target hashtag is valid
    if not TARGET_HASHTAG or len(TARGET_HASHTAG.strip()) == 0:
        results["valid"] = False
        results["errors"].append("TARGET_HASHTAG is empty or not set")
    
    return results
