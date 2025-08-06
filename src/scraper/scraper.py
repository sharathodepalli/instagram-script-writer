"""Instagram Reels scraper module using Instaloader."""

import os
import json
import time
import instaloader
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from datetime import datetime

from src.config import logger
from .config import (
    INSTA_USERNAME,
    INSTA_PASSWORD,
    TARGET_HASHTAG,
    MAX_FETCH,
    RAW_DIR,
    ensure_directories,
    validate_credentials,
    validate_environment
)


class ReelScraper:
    """Handles scraping of top Telugu Reels from Instagram."""

    def __init__(self):
        """Initialize the Instagram scraper with Instaloader."""
        # Validate environment
        env_validation = validate_environment()
        if not env_validation["valid"]:
            for error in env_validation["errors"]:
                logger.error(f"Environment validation error: {error}")
            raise ValueError("Invalid environment configuration for Telugu scraper")
        
        for warning in env_validation.get("warnings", []):
            logger.warning(warning)
        
        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=True,
            compress_json=False,
        )
        ensure_directories()

    def login(self) -> bool:
        """
        Log in to Instagram with provided credentials.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        if not validate_credentials():
            logger.warning("Instagram credentials not provided. Running in anonymous mode.")
            return False
        
        try:
            self.loader.login(INSTA_USERNAME, INSTA_PASSWORD)
            logger.info(f"Successfully logged in as {INSTA_USERNAME}")
            return True
        except instaloader.exceptions.BadCredentialsException:
            logger.error("Invalid Instagram credentials")
            return False
        except Exception as e:
            logger.error(f"Error logging in to Instagram: {e}")
            return False

    def fetch_reels(self, hashtag: str = TARGET_HASHTAG, max_count: int = MAX_FETCH) -> int:
        """
        Fetch top reels for a given hashtag.
        
        Args:
            hashtag: Instagram hashtag to scrape (default from config)
            max_count: Maximum number of posts to fetch (default from config)
            
        Returns:
            int: Number of reels successfully scraped
        """
        tag_path = Path(f"{RAW_DIR}/{hashtag}")
        tag_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Fetching up to {max_count} reels for #{hashtag}")
        
        try:
            # Get hashtag posts
            try:
                hashtag_posts = instaloader.Hashtag.from_name(self.loader.context, hashtag)
            except instaloader.exceptions.BadResponseException as e:
                logger.error(f"Failed to fetch hashtag #{hashtag}: {e}")
                logger.warning("Instagram may be rate-limiting requests. Try again later or use authenticated mode.")
                return 0
                
            count = 0
            saved_count = 0
            
            for post in hashtag_posts.get_posts():
                if count >= max_count:
                    break
                
                count += 1
                
                # Skip if not a video/reel
                if not post.is_video:
                    continue
                
                try:
                    # Extract relevant data
                    post_data = {
                        "id": post.mediaid,
                        "shortcode": post.shortcode,
                        "views": getattr(post, "video_view_count", 0),
                        "likes": post.likes,
                        "comments": post.comments,
                        "caption": post.caption if post.caption else "",
                        "audio": getattr(post, "music_info", {}).get("title", "Unknown Audio")
                    }
                    
                    # Save as JSON
                    json_path = tag_path / f"{post.shortcode}.json"
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(post_data, f, ensure_ascii=False, indent=2)
                    
                    saved_count += 1
                    
                    if saved_count % 10 == 0:
                        logger.info(f"Saved {saved_count} reels so far...")
                    
                    # Sleep to avoid rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing post {post.shortcode}: {e}")
            
            logger.info(f"Completed scraping. Saved {saved_count} reels out of {count} posts examined.")
            return saved_count
            
        except instaloader.exceptions.LoginRequiredException:
            logger.error("Login required to scrape hashtag posts. Please provide credentials.")
            return 0
        except instaloader.exceptions.ConnectionException as e:
            logger.error(f"Connection error while scraping: {e}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error while scraping: {e}")
            return 0


if __name__ == "__main__":
    # Run as standalone script
    scraper = ReelScraper()
    scraper.login()
    scraper.fetch_reels()
