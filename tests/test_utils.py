"""Tests for the utilities module."""

import pytest
from unittest.mock import Mock, patch

from src.utils import (
    ScriptQualityChecker, 
    ScriptFormatter, 
    generate_script_hash, 
    count_words, 
    count_characters, 
    extract_metrics
)


class TestScriptQualityChecker:
    """Test cases for ScriptQualityChecker class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.checker = ScriptQualityChecker()
    
    def test_check_script_length_within_limits(self):
        """Test script length check for content within limits."""
        # Create script with word count between MIN and MAX limits
        script = " ".join(["word"] * 100)  # 100 words
        
        result = self.checker.check_script_length(script)
        
        assert result["word_count"] == 100
        assert result["within_limits"] is True
        assert "appropriate" in result["message"]
    
    def test_check_script_length_too_short(self):
        """Test script length check for content that's too short."""
        script = " ".join(["word"] * 10)  # 10 words (likely below minimum)
        
        result = self.checker.check_script_length(script)
        
        assert result["word_count"] == 10
        assert result["within_limits"] is False
        assert result["issue"] == "too_short"
        assert "too short" in result["message"]
    
    def test_check_script_length_too_long(self):
        """Test script length check for content that's too long."""
        script = " ".join(["word"] * 1000)  # 1000 words (likely above maximum)
        
        result = self.checker.check_script_length(script)
        
        assert result["word_count"] == 1000
        assert result["within_limits"] is False
        assert result["issue"] == "too_long"
        assert "too long" in result["message"]
    
    def test_check_caption_length_found_within_limit(self):
        """Test caption length check for valid caption."""
        script = """
        HOOK: Great hook
        CAPTION: This is a short caption
        HASHTAGS: #test
        """
        
        result = self.checker.check_caption_length(script)
        
        assert result["caption_found"] is True
        assert result["within_limit"] is True
        assert result["char_count"] < 125
        assert "This is a short caption" in result["caption"]
    
    def test_check_caption_length_found_over_limit(self):
        """Test caption length check for caption over limit."""
        long_caption = "a" * 150  # 150 characters
        script = f"""
        HOOK: Great hook
        CAPTION: {long_caption}
        HASHTAGS: #test
        """
        
        result = self.checker.check_caption_length(script)
        
        assert result["caption_found"] is True
        assert result["within_limit"] is False
        assert result["char_count"] == 150
        assert "OVER LIMIT" in result["message"]
    
    def test_check_caption_length_not_found(self):
        """Test caption length check when no caption exists."""
        script = """
        HOOK: Great hook
        HASHTAGS: #test
        """
        
        result = self.checker.check_caption_length(script)
        
        assert result["caption_found"] is False
        assert "No caption found" in result["message"]
    
    def test_check_required_sections_all_present(self):
        """Test required sections check when all sections are present."""
        script = """
        HOOK: Great hook
        BODY: Main content
        CTA: Call to action
        CAPTION: Caption
        VISUAL: Visual directions
        HASHTAGS: #test
        """
        
        result = self.checker.check_required_sections(script)
        
        assert result["all_sections_present"] is True
        assert len(result["missing_sections"]) == 0
        assert len(result["found_sections"]) == 6
    
    def test_check_required_sections_some_missing(self):
        """Test required sections check when some sections are missing."""
        script = """
        HOOK: Great hook
        BODY: Main content
        HASHTAGS: #test
        """
        
        result = self.checker.check_required_sections(script)
        
        assert result["all_sections_present"] is False
        assert len(result["missing_sections"]) > 0
        assert "cta" in result["missing_sections"]
        assert "caption" in result["missing_sections"]
    
    def test_check_hashtags_found_optimal(self):
        """Test hashtag check with optimal number of hashtags."""
        script = """
        HOOK: Great hook
        HASHTAGS: #instagram #script #content #social #media #test
        """
        
        result = self.checker.check_hashtags(script)
        
        assert result["hashtags_found"] is True
        assert result["optimal_count"] is True
        assert result["count"] == 6
        assert result["has_duplicates"] is False
        assert len(result["hashtags"]) == 6
    
    def test_check_hashtags_found_with_duplicates(self):
        """Test hashtag check with duplicate hashtags."""
        script = """
        HOOK: Great hook
        HASHTAGS: #instagram #script #instagram #content #test
        """
        
        result = self.checker.check_hashtags(script)
        
        assert result["hashtags_found"] is True
        assert result["has_duplicates"] is True
        assert result["count"] == 5
        assert result["unique_count"] == 4
        assert "duplicates" in result["message"]
    
    def test_check_hashtags_not_found(self):
        """Test hashtag check when no hashtags exist."""
        script = """
        HOOK: Great hook
        BODY: Main content
        """
        
        result = self.checker.check_hashtags(script)
        
        assert result["hashtags_found"] is False
        assert "No hashtags found" in result["message"]
    
    def test_check_duplicate_content_no_duplicates(self):
        """Test duplicate check with no similar content."""
        new_script = "This is a completely unique script"
        existing_scripts = [
            "Different script about cooking",
            "Another script about travel",
            "Fitness script content"
        ]
        
        result = self.checker.check_duplicate_content(new_script, existing_scripts)
        
        assert result["is_duplicate"] is False
        assert result["max_similarity"] < 0.8
        assert len(result["all_similarities"]) == 3
    
    def test_check_duplicate_content_with_duplicate(self):
        """Test duplicate check with similar content."""
        new_script = "This is a script about morning routines and productivity"
        existing_scripts = [
            "This is a script about morning routines and productivity tips",  # Very similar
            "Different script about cooking",
            "Another script about travel"
        ]
        
        result = self.checker.check_duplicate_content(new_script, existing_scripts)
        
        # Should detect high similarity with first script
        assert result["max_similarity"] > 0.7  # High similarity
        assert result["similar_script_index"] == 0
    
    def test_check_duplicate_content_empty_list(self):
        """Test duplicate check with empty existing scripts list."""
        new_script = "Test script"
        existing_scripts = []
        
        result = self.checker.check_duplicate_content(new_script, existing_scripts)
        
        assert result["is_duplicate"] is False
        assert "No existing scripts" in result["message"]
    
    def test_full_quality_check_excellent(self):
        """Test full quality check for excellent script."""
        script = """
        HOOK: Amazing hook content that grabs attention immediately
        BODY: """ + " ".join(["word"] * 80) + """
        CTA: Perfect call to action that drives engagement
        CAPTION: Great caption under limit
        VISUAL DIRECTIONS: Clear visual instructions for filming
        HASHTAGS: #instagram #content #script #social #media #test
        """
        
        result = self.checker.full_quality_check(script)
        
        assert result["quality_level"] == "excellent"
        assert result["overall_score"] >= 80
    
    def test_full_quality_check_with_existing_scripts(self):
        """Test full quality check with existing scripts for duplicate detection."""
        script = """
        HOOK: Great hook
        BODY: """ + " ".join(["word"] * 100) + """
        CTA: Call to action
        CAPTION: Caption
        VISUAL: Visual directions
        HASHTAGS: #test #script #content #social #media
        """
        
        existing_scripts = ["Different script content entirely"]
        
        result = self.checker.full_quality_check(script, existing_scripts)
        
        assert "duplicates" in result["checks"]
        assert result["max_possible_score"] == 100  # With duplicate check


class TestScriptFormatter:
    """Test cases for ScriptFormatter class."""
    
    def test_format_script_display(self):
        """Test script formatting for display."""
        script = """
        HOOK: Great hook
        This is hook content
        BODY: Main body
        This is body content
        CTA: Call to action
        """
        
        formatted = ScriptFormatter.format_script_display(script)
        
        assert "📌 HOOK:" in formatted
        assert "📌 BODY:" in formatted
        assert "📌 CTA:" in formatted
        assert "Great hook" in formatted
    
    def test_extract_sections_dict_complete(self):
        """Test extraction of all script sections into dictionary."""
        script = """
        HOOK: Amazing hook content
        BODY: Main body content here
        CTA: Strong call to action
        CAPTION: Perfect caption
        VISUAL DIRECTIONS: Clear filming instructions
        HASHTAGS: #test #script #content
        """
        
        sections = ScriptFormatter.extract_sections_dict(script)
        
        assert sections["hook"] == "Amazing hook content"
        assert sections["body"] == "Main body content here"
        assert sections["cta"] == "Strong call to action"
        assert sections["caption"] == "Perfect caption"
        assert sections["visual_directions"] == "Clear filming instructions"
        assert sections["hashtags"] == "#test #script #content"
    
    def test_extract_sections_dict_partial(self):
        """Test extraction with only some sections present."""
        script = """
        HOOK: Great hook
        BODY: Main content
        """
        
        sections = ScriptFormatter.extract_sections_dict(script)
        
        assert sections["hook"] == "Great hook"
        assert sections["body"] == "Main content"
        assert sections["cta"] == ""
        assert sections["caption"] == ""
        assert sections["visual_directions"] == ""
        assert sections["hashtags"] == ""


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_generate_script_hash(self):
        """Test script hash generation."""
        script = "Test script content"
        hash1 = generate_script_hash(script)
        hash2 = generate_script_hash(script)
        hash3 = generate_script_hash("Different content")
        
        assert hash1 == hash2  # Same content should have same hash
        assert hash1 != hash3  # Different content should have different hash
        assert len(hash1) == 32  # MD5 hash length
    
    def test_count_words(self):
        """Test word counting function."""
        text = "This is a test sentence with seven words"
        assert count_words(text) == 8
        
        text = "Single"
        assert count_words(text) == 1
        
        text = ""
        assert count_words(text) == 0
    
    def test_count_characters(self):
        """Test character counting function."""
        text = "Hello"
        assert count_characters(text) == 5
        
        text = "Hello World!"
        assert count_characters(text) == 12
        
        text = ""
        assert count_characters(text) == 0
    
    def test_extract_metrics(self):
        """Test metrics extraction from script."""
        script = """This is line one
        This is line two
        
        This is after a blank line"""
        
        metrics = extract_metrics(script)
        
        assert "word_count" in metrics
        assert "character_count" in metrics
        assert "line_count" in metrics
        assert "paragraph_count" in metrics
        
        assert metrics["word_count"] > 0
        assert metrics["character_count"] > 0
        assert metrics["line_count"] >= 3
        assert metrics["paragraph_count"] >= 1
