"""Tests for the script generator module."""

import pytest
import openai
from unittest.mock import Mock, patch, MagicMock
from langchain.schema import Document

from src.generator import ScriptGenerator


class TestScriptGenerator:
    """Test cases for ScriptGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('src.generator.Pinecone'), \
             patch('src.generator.ChatOpenAI'), \
             patch('src.generator.HuggingFaceEmbeddings'):
            self.generator = ScriptGenerator()
    
    @pytest.fixture
    def mock_retriever(self):
        """Mock retriever with sample documents."""
        mock_retriever = Mock()
        mock_docs = [
            Document(page_content="Sample script 1", metadata={"source_file": "script1.txt"}),
            Document(page_content="Sample script 2", metadata={"source_file": "script2.txt"}),
            Document(page_content="Sample script 3", metadata={"source_file": "script3.txt"})
        ]
        mock_retriever.get_relevant_documents.return_value = mock_docs
        return mock_retriever
    
    @patch('src.generator.Pinecone')
    def test_initialize_pinecone_success(self, mock_pinecone_class):
        """Test successful Pinecone initialization."""
        mock_pinecone_instance = Mock()
        mock_pinecone_class.return_value = mock_pinecone_instance
        
        with patch('src.generator.ChatOpenAI'), \
             patch('src.generator.HuggingFaceEmbeddings'):
            generator = ScriptGenerator()
            mock_pinecone_class.assert_called_once()
    
    @patch('src.generator.Pinecone')
    def test_initialize_pinecone_failure(self, mock_pinecone_class):
        """Test Pinecone initialization failure."""
        mock_pinecone_class.side_effect = Exception("Connection failed")
        
        with patch('src.generator.ChatOpenAI'), \
             patch('src.generator.HuggingFaceEmbeddings'):
            with pytest.raises(Exception, match="Connection failed"):
                ScriptGenerator()
    
    def test_get_retriever_success(self):
        """Test successful retriever creation."""
        # Setup mocks
        mock_index = Mock()
        self.generator.pc = Mock()
        self.generator.pc.Index.return_value = mock_index
        
        mock_vectorstore = Mock()
        mock_retriever = Mock()
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        with patch('src.generator.LC_Pinecone', return_value=mock_vectorstore):
            retriever = self.generator.get_retriever()
            
            assert retriever == mock_retriever
            self.generator.pc.Index.assert_called_once()
            mock_vectorstore.as_retriever.assert_called_once()
    
    def test_get_retriever_failure(self):
        """Test retriever creation failure."""
        # Setup mock to raise exception
        self.generator.pc = Mock()
        self.generator.pc.Index.side_effect = Exception("Retriever failed")
        
        with pytest.raises(Exception, match="Retriever failed"):
            self.generator.get_retriever()
    
    @patch('openai.OpenAI')
    def test_call_llm_success(self, mock_openai_class):
        """Test successful LLM call."""
        # Create mock client and response
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated script content"
        
        mock_client.chat.completions.create.return_value = mock_response
        
        result = self.generator._call_llm("Test prompt")
        
        assert result == "Generated script content"
        mock_client.chat.completions.create.assert_called_once()
    
    def test_parse_script_complete(self):
        """Test parsing a complete script with all sections."""
        script = """
        HOOK: This is the hook
        BODY: This is the main body content
        CTA: This is the call to action
        CAPTION: Short caption
        VISUAL DIRECTIONS: Visual directions content
        HASHTAGS: #tag1 #tag2 #tag3
        """
        
        parsed = self.generator._parse_script(script)
        
        assert parsed["hook"] == "This is the hook"
        assert parsed["body"] == "This is the main body content"
        assert parsed["cta"] == "This is the call to action"
        assert parsed["caption"] == "Short caption"
        assert parsed["visual_directions"] == "Visual directions content"
        assert parsed["hashtags"] == "#tag1 #tag2 #tag3"
    
    def test_parse_script_incomplete(self):
        """Test parsing an incomplete script."""
        script = """
        HOOK: This is the hook
        BODY: This is the main body content
        """
        
        parsed = self.generator._parse_script(script)
        
        assert parsed["hook"] == "This is the hook"
        assert parsed["body"] == "This is the main body content"
        assert parsed["cta"] == ""
        assert parsed["caption"] == ""
        assert parsed["visual_directions"] == ""
        assert parsed["hashtags"] == ""
