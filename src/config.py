"""Configuration module for Instagram Script-Writer."""

import os
import logging
import sys
from typing import Optional, List, Final
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
MODEL_FINE_TUNED: str = os.getenv("MODEL_FINE_TUNED", "gpt-3.5-turbo")

# LangSmith Configuration
LANGCHAIN_API_KEY: Optional[str] = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "Instagram-Script-Writer")

# Pinecone Configuration
PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
PINECONE_HOST: str = os.getenv("PINECONE_HOST", "https://scriptwriter-jltat6g.svc.aped-4627-b74a.pinecone.io")
PINECONE_INDEX: str = os.getenv("PINECONE_INDEX", "scriptwriter-384")
PINECONE_METRIC: str = os.getenv("PINECONE_METRIC", "cosine")
PINECONE_DIMENSIONS: int = int(os.getenv("PINECONE_DIMENSIONS", "384"))
PINECONE_CLOUD: str = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION: str = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_TYPE: str = os.getenv("PINECONE_TYPE", "dense")
PINECONE_CAPACITY_MODE: str = os.getenv("PINECONE_CAPACITY_MODE", "serverless")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Validation (skip in test/production environments)
if not os.getenv("TESTING_MODE") and not os.getenv("PRODUCTION_MODE"):
    required_vars = {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "PINECONE_API_KEY": PINECONE_API_KEY,
    }

    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Telugu Scraper Configuration
INSTA_USERNAME: Optional[str] = os.getenv("INSTA_USERNAME")
INSTA_PASSWORD: Optional[str] = os.getenv("INSTA_PASSWORD")
TARGET_HASHTAG: str = os.getenv("TARGET_HASHTAG", "Telugu")
MAX_FETCH: int = int(os.getenv("MAX_FETCH", "200"))
RAW_DIR: str = os.getenv("RAW_DIR", "data/raw_reels")
TOP_CSV: str = os.getenv("TOP_CSV", "data/top_reels.csv")
SCRIPT_DIR: str = os.getenv("SCRIPT_DIR", "scripts/auto_telugu")

# Default Hashtags
DEFAULT_HASHTAGS: Final[List[str]] = ["#Telugu", "#Trending", "#Reels", "#TeluguReels", "#InstaTelugu"]

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("ig_script_writer")

# App settings
SCRIPTS_DIR: str = "scripts"
MAX_SCRIPT_LENGTH: int = 500  # Maximum script length in words
MIN_SCRIPT_LENGTH: int = 50   # Minimum script length in words
RETRIEVAL_TOP_K: int = 3      # Number of examples to retrieve
TEMPERATURE: float = 0.7      # OpenAI temperature for generation
POLISH_TEMPERATURE: float = 0.5  # Temperature for polishing
