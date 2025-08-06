"""Utility functions for Instagram Script-Writer."""

import re
import hashlib
from typing import List, Dict, Any, Set, Optional, Tuple
from collections import Counter
import difflib

try:
    # Try relative import first (for when running as part of the app)
    from .config import (
        MAX_SCRIPT_LENGTH,
        MIN_SCRIPT_LENGTH,
        DEFAULT_HASHTAGS,
        logger
    )
except ImportError:
    # Fall back to absolute import (for when running directly)
    from src.config import (
        MAX_SCRIPT_LENGTH,
        MIN_SCRIPT_LENGTH,
        DEFAULT_HASHTAGS,
        logger
    )


class ScriptQualityChecker:
    """Handles quality control checks for generated scripts."""
    
    def __init__(self):
        """Initialize the quality checker."""
        self.duplicate_threshold = 0.8  # Similarity threshold for duplicate detection
        
    def check_script_length(self, script: str) -> Dict[str, Any]:
        """
        Check if script length is within acceptable bounds.
        
        Args:
            script: The script text to check
            
        Returns:
            Dictionary with length check results
        """
        words = script.split()
        word_count = len(words)
        
        result = {
            "word_count": word_count,
            "within_limits": MIN_SCRIPT_LENGTH <= word_count <= MAX_SCRIPT_LENGTH,
            "min_limit": MIN_SCRIPT_LENGTH,
            "max_limit": MAX_SCRIPT_LENGTH
        }
        
        if word_count < MIN_SCRIPT_LENGTH:
            result["issue"] = "too_short"
            result["message"] = f"Script is too short ({word_count} words). Minimum: {MIN_SCRIPT_LENGTH}"
        elif word_count > MAX_SCRIPT_LENGTH:
            result["issue"] = "too_long"
            result["message"] = f"Script is too long ({word_count} words). Maximum: {MAX_SCRIPT_LENGTH}"
        else:
            result["message"] = "Script length is appropriate"
            
        return result
        
    def check_caption_length(self, script: str) -> Dict[str, Any]:
        """
        Check if Instagram caption is within character limit.
        
        Args:
            script: The script text containing a caption
            
        Returns:
            Dictionary with caption check results
        """
        caption = self._extract_caption(script)
        
        if not caption:
            return {
                "caption_found": False,
                "caption": "",
                "char_count": 0,
                "within_limit": False,
                "limit": 125,
                "message": "No caption found in script"
            }
            
        char_count = len(caption)
        within_limit = char_count <= 125
        
        return {
            "caption_found": True,
            "caption": caption,
            "char_count": char_count,
            "within_limit": within_limit,
            "limit": 125,
            "message": f"Caption: {char_count}/125 characters" + ("" if within_limit else " (OVER LIMIT)")
        }
        
    def check_required_sections(self, script: str) -> Dict[str, Any]:
        """
        Check if script contains all required sections.
        
        Args:
            script: The script text to check
            
        Returns:
            Dictionary with section check results
        """
        required_sections = ["hook", "body", "cta", "caption", "visual", "hashtag"]
        found_sections = []
        missing_sections = []
        
        script_lower = script.lower()
        
        for section in required_sections:
            if section in script_lower:
                found_sections.append(section)
            else:
                missing_sections.append(section)
                
        return {
            "all_sections_present": len(missing_sections) == 0,
            "found_sections": found_sections,
            "missing_sections": missing_sections,
            "total_sections": len(required_sections),
            "found_count": len(found_sections),
            "message": f"Found {len(found_sections)}/{len(required_sections)} required sections"
        }
        
    def check_hashtags(self, script: str) -> Dict[str, Any]:
        """
        Check hashtag quality and count.
        
        Args:
            script: The script text containing hashtags
            
        Returns:
            Dictionary with hashtag check results
        """
        hashtags = self._extract_hashtags(script)
        
        if not hashtags:
            return {
                "hashtags_found": False,
                "hashtags": [],
                "count": 0,
                "optimal_count": False,
                "has_duplicates": False,
                "unique_count": 0,
                "message": "No hashtags found in script"
            }
            
        # Check count (recommended 5-7)
        count = len(hashtags)
        optimal_count = 5 <= count <= 7
        
        # Check for duplicates
        unique_hashtags = set(hashtags)
        has_duplicates = len(unique_hashtags) != len(hashtags)
        
        return {
            "hashtags_found": True,
            "hashtags": hashtags,
            "count": count,
            "optimal_count": optimal_count,
            "has_duplicates": has_duplicates,
            "unique_count": len(unique_hashtags),
            "message": f"Found {count} hashtags (optimal: 5-7)" + 
                      (" with duplicates" if has_duplicates else "")
        }
        
    def check_duplicate_content(self, new_script: str, existing_scripts: List[str]) -> Dict[str, Any]:
        """
        Check if new script is too similar to existing scripts.
        
        Args:
            new_script: New script to check
            existing_scripts: List of existing scripts to compare against
            
        Returns:
            Dictionary with duplicate check results
        """
        if not existing_scripts:
            return {
                "is_duplicate": False,
                "message": "No existing scripts to compare against"
            }
            
        similarities = []
        
        for i, existing in enumerate(existing_scripts):
            similarity = self._calculate_similarity(new_script, existing)
            similarities.append({
                "script_index": i,
                "similarity": similarity
            })
            
        # Find highest similarity
        max_similarity = max(similarities, key=lambda x: x["similarity"])
        is_duplicate = max_similarity["similarity"] >= self.duplicate_threshold
        
        return {
            "is_duplicate": is_duplicate,
            "max_similarity": max_similarity["similarity"],
            "threshold": self.duplicate_threshold,
            "similar_script_index": max_similarity["script_index"],
            "all_similarities": similarities,
            "message": f"Max similarity: {max_similarity['similarity']:.2%}" + 
                      (" (DUPLICATE DETECTED)" if is_duplicate else "")
        }
        
    def _extract_caption(self, script: str) -> Optional[str]:
        """Extract caption from script text."""
        lines = script.split('\n')
        
        for line in lines:
            if 'caption:' in line.lower():
                return line.split(':', 1)[-1].strip()
                
        return None
        
    def _extract_hashtags(self, script: str) -> List[str]:
        """Extract hashtags from script text."""
        # Find hashtag section
        lines = script.split('\n')
        hashtag_section = ""
        
        for line in lines:
            if 'hashtag' in line.lower():
                hashtag_section = line
                break
                
        if not hashtag_section:
            return []
            
        # Extract hashtags using regex
        hashtags = re.findall(r'#\w+', hashtag_section)
        return [tag.lower() for tag in hashtags]
        
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        # Simple similarity based on character-level comparison
        matcher = difflib.SequenceMatcher(None, text1.lower(), text2.lower())
        return matcher.ratio()
        
    def full_quality_check(self, script: str, existing_scripts: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive quality check on a script.
        
        Args:
            script: Script to check
            existing_scripts: Optional list of existing scripts for duplicate checking
            
        Returns:
            Comprehensive quality report
        """
        logger.info("Performing full quality check on script")
        
        checks = {
            "length": self.check_script_length(script),
            "caption": self.check_caption_length(script),
            "sections": self.check_required_sections(script),
            "hashtags": self.check_hashtags(script)
        }
        
        if existing_scripts:
            checks["duplicates"] = self.check_duplicate_content(script, existing_scripts)
            
        # Calculate overall score
        score_components = []
        
        if checks["length"]["within_limits"]:
            score_components.append(20)
        if checks["caption"]["within_limit"]:
            score_components.append(20)
        if checks["sections"]["all_sections_present"]:
            score_components.append(25)
        if checks["hashtags"]["optimal_count"]:
            score_components.append(15)
        if existing_scripts and not checks["duplicates"]["is_duplicate"]:
            score_components.append(20)
            
        total_score = sum(score_components)
        max_possible = 100 if existing_scripts else 80
        
        # Determine quality level
        if total_score >= max_possible * 0.9:
            quality_level = "excellent"
        elif total_score >= max_possible * 0.7:
            quality_level = "good"
        elif total_score >= max_possible * 0.5:
            quality_level = "fair"
        else:
            quality_level = "poor"
            
        return {
            "overall_score": total_score,
            "max_possible_score": max_possible,
            "quality_level": quality_level,
            "checks": checks,
            "passed_checks": len([c for c in checks.values() if c.get("within_limits") or c.get("within_limit") or c.get("all_sections_present") or c.get("optimal_count") or not c.get("is_duplicate")]),
            "total_checks": len(checks)
        }


class ScriptFormatter:
    """Handles formatting and structure of scripts."""
    
    @staticmethod
    def format_script_display(script: str) -> str:
        """
        Format script for better display.
        
        Args:
            script: Raw script text
            
        Returns:
            Formatted script string
        """
        lines = script.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Format section headers
            if any(keyword in line.lower() for keyword in ['hook:', 'body:', 'cta:', 'caption:', 'visual:', 'hashtag:']):
                formatted_lines.append(f"\n📌 {line.upper()}")
            else:
                formatted_lines.append(f"   {line}")
                
        return '\n'.join(formatted_lines)
        
    @staticmethod
    def extract_sections_dict(script: str) -> Dict[str, str]:
        """
        Extract script sections into a structured dictionary.
        
        Args:
            script: Script text
            
        Returns:
            Dictionary with extracted sections
        """
        sections = {
            "hook": "",
            "body": "",
            "cta": "",
            "caption": "",
            "visual_directions": "",
            "hashtags": ""
        }
        
        lines = script.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            lower_line = line.lower()
            if any(keyword in lower_line for keyword in ['hook:', 'hook']):
                current_section = "hook"
                line = line.split(':', 1)[-1].strip()
            elif any(keyword in lower_line for keyword in ['body:', 'body']):
                current_section = "body"
                line = line.split(':', 1)[-1].strip()
            elif any(keyword in lower_line for keyword in ['cta:', 'call-to-action:', 'call to action:']):
                current_section = "cta"
                line = line.split(':', 1)[-1].strip()
            elif any(keyword in lower_line for keyword in ['caption:', 'caption']):
                current_section = "caption"
                line = line.split(':', 1)[-1].strip()
            elif any(keyword in lower_line for keyword in ['visual:', 'visual directions:', 'visuals:']):
                current_section = "visual_directions"
                line = line.split(':', 1)[-1].strip()
            elif any(keyword in lower_line for keyword in ['hashtags:', 'hashtag:', '#']):
                current_section = "hashtags"
                line = line.split(':', 1)[-1].strip()
                
            # Add content to current section
            if current_section and line:
                if sections[current_section]:
                    sections[current_section] += f" {line}"
                else:
                    sections[current_section] = line
                    
        return sections


def generate_script_hash(script: str) -> str:
    """
    Generate a unique hash for a script.
    
    Args:
        script: Script text
        
    Returns:
        MD5 hash of the script
    """
    return hashlib.md5(script.encode('utf-8')).hexdigest()


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def count_characters(text: str) -> int:
    """Count characters in text."""
    return len(text)


def extract_metrics(script: str) -> Dict[str, int]:
    """
    Extract basic metrics from a script.
    
    Args:
        script: Script text
        
    Returns:
        Dictionary with script metrics
    """
    return {
        "word_count": count_words(script),
        "character_count": count_characters(script),
        "line_count": len(script.split('\n')),
        "paragraph_count": len([p for p in script.split('\n\n') if p.strip()])
    }
