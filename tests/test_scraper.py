"""Tests for the Telugu Reels scraper module."""

import os
import pytest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path
import pandas as pd

from src.scraper.scraper import ReelScraper
from src.scraper.processor import ReelProcessor
from src.scraper.config import ensure_directories


class TestReelScraper:
    """Test cases for ReelScraper class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        ensure_directories()
    
    @patch('src.scraper.scraper.instaloader.Instaloader')
    def test_init(self, mock_instaloader):
        """Test initialization of ReelScraper."""
        scraper = ReelScraper()
        assert scraper.loader is not None
        mock_instaloader.assert_called_once()
    
    @patch('src.scraper.scraper.instaloader.Instaloader')
    @patch('src.scraper.scraper.INSTA_USERNAME', 'test_user')
    @patch('src.scraper.scraper.INSTA_PASSWORD', 'test_pass')
    def test_login_success(self, mock_instaloader):
        """Test successful login."""
        mock_loader = MagicMock()
        mock_instaloader.return_value = mock_loader
        
        scraper = ReelScraper()
        result = scraper.login()
        
        assert result is True
        mock_loader.login.assert_called_once_with('test_user', 'test_pass')
    
    @patch('src.scraper.scraper.instaloader.Instaloader')
    @patch('src.scraper.scraper.INSTA_USERNAME', 'test_user')
    @patch('src.scraper.scraper.INSTA_PASSWORD', 'test_pass')
    def test_login_failed(self, mock_instaloader):
        """Test failed login."""
        mock_loader = MagicMock()
        mock_loader.login.side_effect = Exception("Login failed")
        mock_instaloader.return_value = mock_loader
        
        scraper = ReelScraper()
        result = scraper.login()
        
        assert result is False
        mock_loader.login.assert_called_once()
    
    @patch('src.scraper.scraper.instaloader.Hashtag')
    @patch('src.scraper.scraper.instaloader.Instaloader')
    def test_fetch_reels(self, mock_instaloader, mock_hashtag):
        """Test fetching reels."""
        # Setup mocks
        mock_loader = MagicMock()
        mock_instaloader.return_value = mock_loader
        
        mock_hashtag_instance = MagicMock()
        mock_hashtag.from_name.return_value = mock_hashtag_instance
        
        # Create mock posts
        mock_posts = [
            self._create_mock_post("post1", True, 1000),
            self._create_mock_post("post2", True, 2000),
            self._create_mock_post("post3", False, 0),  # Not a video
        ]
        mock_hashtag_instance.get_posts.return_value = mock_posts
        
        with patch('builtins.open', MagicMock()), \
             patch('json.dump') as mock_json_dump:
            
            scraper = ReelScraper()
            result = scraper.fetch_reels(hashtag="Telugu", max_count=5)
            
            # Should only process 2 posts (skipping post3 as it's not a video)
            assert result == 2
            assert mock_json_dump.call_count == 2
    
    @staticmethod
    def _create_mock_post(shortcode, is_video, views):
        """Helper to create mock post objects."""
        mock_post = MagicMock()
        mock_post.shortcode = shortcode
        mock_post.is_video = is_video
        mock_post.mediaid = 12345
        mock_post.likes = 500
        mock_post.comments = 50
        mock_post.caption = "Test caption"
        
        # Set video_view_count if it's a video
        if is_video:
            mock_post.video_view_count = views
            
        return mock_post


class TestReelProcessor:
    """Test cases for ReelProcessor class."""
    
    @pytest.fixture
    def sample_reels(self, tmp_path):
        """Create sample reel JSON files."""
        reel_data = [
            {
                "id": 1001,
                "shortcode": "ABC123",
                "views": 5000,
                "likes": 200,
                "comments": 30,
                "caption": "Test caption 1",
                "audio": "Test audio 1"
            },
            {
                "id": 1002,
                "shortcode": "DEF456",
                "views": 8000,
                "likes": 400,
                "comments": 60,
                "caption": "Test caption 2",
                "audio": "Test audio 2"
            },
            {
                "id": 1003,
                "shortcode": "GHI789",
                "views": 3000,
                "likes": 150,
                "comments": 20,
                "caption": "Test caption 3",
                "audio": "Test audio 3"
            }
        ]
        
        # Create temp directory for test data
        test_dir = tmp_path / "raw_reels" / "Telugu"
        test_dir.mkdir(parents=True)
        
        # Write sample files
        for reel in reel_data:
            file_path = test_dir / f"{reel['shortcode']}.json"
            with open(file_path, 'w') as f:
                json.dump(reel, f)
        
        return tmp_path, reel_data
    
    @patch('src.scraper.processor.RAW_DIR')
    def test_load_all_reels(self, mock_raw_dir, sample_reels):
        """Test loading all reels."""
        tmp_path, reel_data = sample_reels
        mock_raw_dir.return_value = str(tmp_path / "raw_reels")
        
        processor = ReelProcessor()
        with patch('src.scraper.processor.glob.glob') as mock_glob:
            # Set up mock to return our sample files
            sample_files = [str(tmp_path / "raw_reels" / "Telugu" / f"{reel['shortcode']}.json") for reel in reel_data]
            mock_glob.return_value = sample_files
            
            # Mock open to return our reel data
            with patch('builtins.open', MagicMock()):
                with patch('json.load') as mock_json_load:
                    mock_json_load.side_effect = reel_data
                    loaded_reels = processor.load_all_reels("Telugu")
                    
                    assert len(loaded_reels) == 3
                    assert loaded_reels[0]["shortcode"] == "ABC123"
                    assert loaded_reels[1]["shortcode"] == "DEF456"
                    assert loaded_reels[2]["shortcode"] == "GHI789"
    
    @patch('src.scraper.processor.TOP_CSV')
    def test_build_top_list(self, mock_top_csv, tmp_path):
        """Test building top reels list."""
        processor = ReelProcessor()
        
        # Mock load_all_reels
        sample_reels = [
            {"shortcode": "ABC123", "views": 5000, "likes": 200, "comments": 30, "caption": "Caption 1", "audio": "Audio 1"},
            {"shortcode": "DEF456", "views": 8000, "likes": 400, "comments": 60, "caption": "Caption 2", "audio": "Audio 2"},
            {"shortcode": "GHI789", "views": 3000, "likes": 150, "comments": 20, "caption": "Caption 3", "audio": "Audio 3"}
        ]
        
        with patch.object(processor, 'load_all_reels', return_value=sample_reels), \
             patch('pandas.DataFrame.to_csv') as mock_to_csv:
                
            mock_top_csv.return_value = str(tmp_path / "top_reels.csv")
            top_df = processor.build_top_list(top_n=2)
            
            assert len(top_df) == 2
            assert top_df.iloc[0]["shortcode"] == "DEF456"  # Highest views
            assert top_df.iloc[1]["shortcode"] == "ABC123"  # Second highest
            mock_to_csv.assert_called_once()
    
    def test_get_hook_from_caption(self):
        """Test extracting hook from caption."""
        processor = ReelProcessor()
        
        # Test with multi-line caption
        caption1 = "This is the first line.\nThis is the second line."
        assert processor.get_hook_from_caption(caption1) == "This is the first line."
        
        # Test with single sentence
        caption2 = "Short caption."
        assert processor.get_hook_from_caption(caption2) == "Short caption."
        
        # Test with empty caption
        assert "trending" in processor.get_hook_from_caption("").lower()
    
    def test_trim_caption(self):
        """Test trimming captions."""
        processor = ReelProcessor()
        
        # Test with short caption
        short = "This is a short caption."
        assert processor.trim_caption(short, 100) == short
        
        # Test with long caption
        long = "This is a very long caption that exceeds the maximum length and should be trimmed properly at a space to avoid cutting words in the middle and maintain readability."
        trimmed = processor.trim_caption(long, 50)
        assert len(trimmed) <= 53  # Allow for ellipsis
        assert trimmed.endswith("...")
        assert " in" not in trimmed  # Should trim at space
        
        # Test with empty caption
        assert processor.trim_caption("") == ""
    
    @patch('src.scraper.processor.SCRIPT_DIR')
    def test_export_scripts(self, mock_script_dir, tmp_path):
        """Test exporting scripts."""
        processor = ReelProcessor()
        mock_script_dir.return_value = str(tmp_path / "scripts")
        
        # Create sample DataFrame
        data = {
            'shortcode': ['ABC123', 'DEF456'],
            'views': [5000, 8000],
            'likes': [200, 400],
            'comments': [30, 60],
            'caption': ['Test caption 1', 'Test caption 2'],
            'audio': ['Test audio 1', 'Test audio 2']
        }
        df = pd.DataFrame(data)
        
        with patch('builtins.open', MagicMock()):
            count = processor.export_scripts(df)
            assert count == 2
