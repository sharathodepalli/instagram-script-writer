"""Process scraped Instagram Reels data into templates."""

import os
import json
import glob
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging
import re

from src.config import logger
from .config import (
    TARGET_HASHTAG,
    RAW_DIR,
    TOP_CSV,
    SCRIPT_DIR,
    TOP_N,
    ensure_directories
)


class ReelProcessor:
    """Process scraped Instagram Reels data into script templates."""
    
    def __init__(self):
        """Initialize the processor."""
        ensure_directories()
    
    def load_all_reels(self, hashtag: str = TARGET_HASHTAG) -> List[Dict[str, Any]]:
        """
        Load all reel data from JSON files.
        
        Args:
            hashtag: The hashtag folder to look in (default from config)
            
        Returns:
            List of dictionaries containing reel data
        """
        json_pattern = os.path.join(RAW_DIR, hashtag, "*.json")
        all_reels = []
        
        logger.info(f"Loading reel data from {json_pattern}")
        
        try:
            for json_file in glob.glob(json_pattern):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        reel_data = json.load(f)
                        all_reels.append(reel_data)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON file: {json_file}")
                except Exception as e:
                    logger.error(f"Error reading file {json_file}: {e}")
            
            logger.info(f"Loaded {len(all_reels)} reels")
            return all_reels
            
        except Exception as e:
            logger.error(f"Error loading reel data: {e}")
            return []
    
    def build_top_list(self, top_n: int = TOP_N, hashtag: str = TARGET_HASHTAG) -> pd.DataFrame:
        """
        Build a list of top reels sorted by views.
        
        Args:
            top_n: Number of top reels to include (default from config)
            hashtag: The hashtag to process (default from config)
            
        Returns:
            DataFrame containing the top reels
        """
        all_reels = self.load_all_reels(hashtag)
        
        if not all_reels:
            logger.warning("No reels found to process")
            return pd.DataFrame()
        
        # Convert to DataFrame and sort by views
        df = pd.DataFrame(all_reels)
        df = df.sort_values(by='views', ascending=False).reset_index(drop=True)
        
        # Take top N
        top_df = df.head(top_n)
        
        # Save to CSV
        try:
            top_df.to_csv(TOP_CSV, index=False)
            logger.info(f"Saved top {len(top_df)} reels to {TOP_CSV}")
        except Exception as e:
            logger.error(f"Failed to save CSV: {e}")
        
        return top_df
    
    def get_hook_from_caption(self, caption: str) -> str:
        """
        Extract or create a hook from the caption.
        
        Args:
            caption: Full caption text
            
        Returns:
            First line or sentence suitable as a hook
        """
        if not caption:
            return "Check out this trending Telugu reel!"
        
        # Get first line or first sentence that's at least 20 chars
        lines = caption.split('\n')
        for line in lines:
            clean_line = line.strip()
            if len(clean_line) >= 20:
                return clean_line
        
        # If no good line found, use first sentence
        sentences = re.split(r'[.!?]', caption)
        for sentence in sentences:
            clean_sentence = sentence.strip()
            if len(clean_sentence) >= 15:
                return clean_sentence
        
        # Fallback
        return caption[:60].strip() if caption else "Trending Telugu reel!"
    
    def trim_caption(self, caption: str, max_length: int = 120) -> str:
        """
        Trim caption to specified length.
        
        Args:
            caption: Full caption text
            max_length: Maximum length for trimmed caption
            
        Returns:
            Trimmed caption
        """
        if not caption:
            return ""
        
        if len(caption) <= max_length:
            return caption
        
        # Try to trim at a natural breaking point
        trimmed = caption[:max_length]
        last_space = trimmed.rfind(' ')
        
        if last_space > max_length * 0.8:  # Only trim at space if it's not too early
            trimmed = trimmed[:last_space]
        
        # Add ellipsis if we trimmed
        if len(caption) > max_length:
            trimmed = trimmed.rstrip() + "..."
            
        return trimmed
    
    def generate_script_template(self, reel: Dict[str, Any]) -> str:
        """
        Generate a script template from reel data.
        
        Args:
            reel: Dictionary containing reel data
            
        Returns:
            Formatted script template
        """
        shortcode = reel.get('shortcode', 'unknown')
        caption = reel.get('caption', '')
        audio = reel.get('audio', 'Unknown audio')
        
        hook = self.get_hook_from_caption(caption)
        trimmed_caption = self.trim_caption(caption)
        
        template = f"""TITLE: Telugu Reel {shortcode}
FORMAT: Reel

HOOK:
{hook}

BODY:
- Original audio: "{audio}"
- Visual: mirror pacing of key scene.
- Narration: summarize action.

CTA:
"Follow for more Telugu trends!"

CAPTION:
{trimmed_caption}

HASHTAGS:
#Telugu #Trending #Reels #TeluguReels #InstaTelugu

VISUAL_DIRECTIONS:
- replicate camera angles & transitions.
"""
        return template
    
    def export_scripts(self, top_df: Optional[pd.DataFrame] = None) -> int:
        """
        Export script templates for top reels.
        
        Args:
            top_df: DataFrame containing top reels (will be loaded from CSV if not provided)
            
        Returns:
            Number of script templates created
        """
        if top_df is None:
            try:
                top_df = pd.read_csv(TOP_CSV)
            except Exception as e:
                logger.error(f"Failed to read top reels CSV: {e}")
                return 0
        
        if len(top_df) == 0:
            logger.warning("No reels to export scripts for")
            return 0
        
        scripts_created = 0
        
        for _, reel in top_df.iterrows():
            try:
                shortcode = reel['shortcode']
                script_content = self.generate_script_template(reel)
                
                script_path = os.path.join(SCRIPT_DIR, f"{shortcode}.txt")
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                
                scripts_created += 1
                
            except Exception as e:
                logger.error(f"Error creating script for reel {reel.get('shortcode', 'unknown')}: {e}")
        
        logger.info(f"Created {scripts_created} script templates in {SCRIPT_DIR}")
        return scripts_created
    
    def process_all(self) -> Tuple[int, int]:
        """
        Run the full processing pipeline.
        
        Returns:
            Tuple of (number of reels processed, number of scripts created)
            
        Raises:
            ValueError: If no reels are found or processing fails
            IOError: If there are filesystem issues
            Exception: For any other errors during processing
        """
        # Build the top reels list
        top_df = self.build_top_list()
        
        if top_df.empty:
            error_msg = "No reels found or failed to build top reels list"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        top_count = len(top_df)
        logger.info(f"Processing {top_count} top Telugu reels")
        
        # Generate script templates
        scripts_created = self.export_scripts(top_df)
        
        if scripts_created == 0:
            error_msg = "Failed to create any script templates"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.info(f"Successfully processed {top_count} reels and created {scripts_created} script templates")
        return top_count, scripts_created


if __name__ == "__main__":
    # Run as standalone script
    processor = ReelProcessor()
    processor.process_all()
