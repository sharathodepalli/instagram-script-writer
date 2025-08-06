"""Tests for the script polishing module."""

import pytest
from unittest.mock import Mock, patch

from src.polish import ScriptPolisher


class TestScriptPolisher:
    """Test cases for ScriptPolisher class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('src.polish.openai'):
            self.polisher = ScriptPolisher()
    
    def test_init_default_model(self):
        """Test initialization with default model."""
        with patch('src.polish.openai'):
            polisher = ScriptPolisher()
            assert polisher.model == "gpt-4"
    
    def test_init_custom_model(self):
        """Test initialization with custom model."""
        with patch('src.polish.openai'):
            polisher = ScriptPolisher(model="gpt-3.5-turbo")
            assert polisher.model == "gpt-3.5-turbo"
    
    def test_get_polish_prompt_basic(self):
        """Test basic polish prompt generation."""
        script = "Test script content"
        prompt = self.polisher._get_polish_prompt(script)
        
        assert "copyeditor" in prompt
        assert "Instagram" in prompt
        assert script in prompt
        assert "HOOK" in prompt
        assert "CAPTION" in prompt
    
    def test_get_polish_prompt_with_focus(self):
        """Test polish prompt with focus area."""
        script = "Test script content"
        focus = "engagement"
        prompt = self.polisher._get_polish_prompt(script, focus)
        
        assert script in prompt
        assert focus in prompt
        assert "Special focus on" in prompt
    
    @patch('src.polish.openai.ChatCompletion.create')
    def test_call_openai_success(self, mock_create):
        """Test successful OpenAI API call."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Polished content"
        mock_create.return_value = mock_response
        
        result = self.polisher._call_openai("Test prompt")
        
        assert result == "Polished content"
        mock_create.assert_called_once()
        
        # Check the call arguments
        call_args = mock_create.call_args
        assert call_args[1]["model"] == "gpt-4"
        assert len(call_args[1]["messages"]) == 2
    
    @patch('src.polish.openai.ChatCompletion.create')
    def test_call_openai_rate_limit(self, mock_create):
        """Test OpenAI API call with rate limit error."""
        import openai
        mock_create.side_effect = openai.error.RateLimitError("Rate limit exceeded")
        
        with pytest.raises(openai.error.RateLimitError):
            self.polisher._call_openai("Test prompt")
    
    @patch.object(ScriptPolisher, '_call_openai')
    @patch.object(ScriptPolisher, '_analyze_improvements')
    def test_polish_script_success(self, mock_analyze, mock_call):
        """Test successful script polishing."""
        original_script = "Original script content"
        polished_script = "Polished script content"
        improvements = {"word_count_change": 5}
        
        mock_call.return_value = polished_script
        mock_analyze.return_value = improvements
        
        result = self.polisher.polish_script(original_script)
        
        assert result["success"] is True
        assert result["original_script"] == original_script
        assert result["polished_script"] == polished_script
        assert result["improvements"] == improvements
        assert result["model_used"] == "gpt-4"
        assert result["focus_area"] is None
    
    @patch.object(ScriptPolisher, '_call_openai')
    def test_polish_script_with_focus(self, mock_call):
        """Test script polishing with focus area."""
        original_script = "Original script content"
        focus_area = "clarity"
        
        mock_call.return_value = "Polished content"
        
        result = self.polisher.polish_script(original_script, focus_area)
        
        assert result["success"] is True
        assert result["focus_area"] == focus_area
    
    @patch.object(ScriptPolisher, '_call_openai')
    def test_polish_script_failure(self, mock_call):
        """Test script polishing failure."""
        mock_call.side_effect = Exception("Polishing failed")
        
        result = self.polisher.polish_script("Test script")
        
        assert result["success"] is False
        assert "Polishing failed" in result["error"]
        assert result["original_script"] == "Test script"
    
    @patch.object(ScriptPolisher, 'polish_script')
    def test_polish_multiple_passes_success(self, mock_polish):
        """Test multiple polishing passes."""
        # Mock successful polishing for each pass
        mock_results = [
            {
                "success": True,
                "polished_script": f"Polished pass {i}",
                "improvements": {"word_count_change": i}
            }
            for i in range(1, 3)
        ]
        mock_polish.side_effect = mock_results
        
        result = self.polisher.polish_multiple_passes("Original script", passes=2)
        
        assert result["success"] is True
        assert result["passes_completed"] == 2
        assert result["final_script"] == "Polished pass 2"
        assert len(result["pass_results"]) == 2
        assert result["pass_results"][0]["pass_number"] == 1
        assert result["pass_results"][1]["pass_number"] == 2
    
    @patch.object(ScriptPolisher, 'polish_script')
    def test_polish_multiple_passes_partial_failure(self, mock_polish):
        """Test multiple polishing passes with partial failure."""
        # First pass succeeds, second fails
        mock_results = [
            {
                "success": True,
                "polished_script": "Polished pass 1",
                "improvements": {"word_count_change": 1}
            },
            {
                "success": False,
                "error": "Second pass failed"
            }
        ]
        mock_polish.side_effect = mock_results
        
        result = self.polisher.polish_multiple_passes("Original script", passes=2)
        
        assert result["success"] is True  # At least one pass succeeded
        assert result["passes_completed"] == 1
        assert result["final_script"] == "Polished pass 1"
    
    def test_analyze_improvements_basic(self):
        """Test basic improvement analysis."""
        original = "Short script"
        polished = "This is a longer polished script"
        
        improvements = self.polisher._analyze_improvements(original, polished)
        
        assert improvements["original_word_count"] == 2
        assert improvements["polished_word_count"] == 7
        assert improvements["word_count_change"] == 5
    
    def test_extract_caption_found(self):
        """Test caption extraction when caption exists."""
        script = """
        HOOK: Great hook
        CAPTION: This is a test caption
        HASHTAGS: #test
        """
        
        caption = self.polisher._extract_caption(script)
        assert caption == "This is a test caption"
    
    def test_extract_caption_not_found(self):
        """Test caption extraction when no caption exists."""
        script = """
        HOOK: Great hook
        HASHTAGS: #test
        """
        
        caption = self.polisher._extract_caption(script)
        assert caption is None
    
    def test_analyze_improvements_with_captions(self):
        """Test improvement analysis with captions."""
        original = "Original script\nCAPTION: Short caption"
        polished = "Polished script\nCAPTION: This is a longer caption"
        
        improvements = self.polisher._analyze_improvements(original, polished)
        
        assert improvements["caption_length_original"] > 0
        assert improvements["caption_length_polished"] > improvements["caption_length_original"]
        assert improvements["caption_within_limit"] is True  # Both are under 125 chars
    
    def test_compare_versions(self):
        """Test version comparison functionality."""
        original = "Original script content"
        polished = "Polished script content with improvements"
        
        comparison = self.polisher.compare_versions(original, polished)
        
        assert comparison["original"] == original
        assert comparison["polished"] == polished
        assert "improvements" in comparison
        assert "side_by_side" in comparison
        assert "original_lines" in comparison["side_by_side"]
        assert "polished_lines" in comparison["side_by_side"]


@patch('src.polish.ScriptPolisher')
def test_main_success(mock_polisher_class):
    """Test main function with successful polishing."""
    mock_polisher = Mock()
    mock_polisher.polish_script.return_value = {
        "success": True,
        "original_script": "Original",
        "polished_script": "Polished",
        "improvements": {
            "original_word_count": 5,
            "polished_word_count": 8,
            "caption_length_polished": 50
        }
    }
    mock_polisher_class.return_value = mock_polisher
    
    from src.polish import main
    
    # Mock input
    with patch('builtins.input', side_effect=["Test script to polish", "clarity"]):
        main()  # Should not raise any exceptions


@patch('src.polish.ScriptPolisher')
def test_main_failure(mock_polisher_class):
    """Test main function with polishing failure."""
    mock_polisher = Mock()
    mock_polisher.polish_script.return_value = {
        "success": False,
        "error": "Polishing failed"
    }
    mock_polisher_class.return_value = mock_polisher
    
    from src.polish import main
    
    with patch('builtins.input', side_effect=["Test script", ""]):
        main()  # Should handle failure gracefully


def test_main_empty_script():
    """Test main function with empty script input."""
    from src.polish import main
    
    with patch('builtins.input', return_value=""):
        main()  # Should handle empty input gracefully
