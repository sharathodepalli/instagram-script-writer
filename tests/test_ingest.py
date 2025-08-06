"""Tests for the ingestion module."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from langchain.schema import Document

from src.ingest import ScriptIngester


class TestScriptIngester:
    """Test cases for ScriptIngester class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.ingester = ScriptIngester()
        
    @pytest.fixture
    def temp_scripts_dir(self):
        """Create temporary directory with test script files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test script files
            test_scripts = [
                ("script1.txt", "This is a test Instagram script about morning routines."),
                ("script2.txt", "Another test script about productivity tips."),
                ("script3.txt", "A third script about healthy eating habits.")
            ]
            
            for filename, content in test_scripts:
                with open(os.path.join(temp_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            yield temp_dir
    
    @patch('src.ingest.Pinecone')
    def test_initialize_pinecone_success(self, mock_pinecone):
        """Test successful Pinecone initialization."""
        # Test that initialization doesn't raise an exception
        ingester = ScriptIngester()
        mock_pinecone.assert_called_once()
        
    @patch('src.ingest.Pinecone')
    def test_initialize_pinecone_failure(self, mock_pinecone):
        """Test Pinecone initialization failure."""
        mock_pinecone.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Connection failed"):
            ScriptIngester()
    
    def test_load_scripts_success(self, temp_scripts_dir):
        """Test successful script loading."""
        documents = self.ingester.load_scripts(temp_scripts_dir)
        
        assert len(documents) == 3
        assert all(isinstance(doc, Document) for doc in documents)
        assert all('source_file' in doc.metadata for doc in documents)
        assert all('file_path' in doc.metadata for doc in documents)
    
    def test_load_scripts_no_directory(self):
        """Test loading scripts from non-existent directory."""
        documents = self.ingester.load_scripts("/non/existent/directory")
        assert documents == []
    
    def test_load_scripts_empty_directory(self):
        """Test loading scripts from empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            documents = self.ingester.load_scripts(temp_dir)
            assert documents == []
    
    def test_split_documents(self):
        """Test document splitting functionality."""
        # Create test documents
        long_text = "A " * 1500  # Create text longer than chunk size
        documents = [Document(page_content=long_text, metadata={"test": "data"})]
        
        split_docs = self.ingester.split_documents(documents)
        
        assert len(split_docs) > 1  # Should be split into multiple chunks
        assert all(isinstance(doc, Document) for doc in split_docs)
    
    @patch('src.ingest.LC_Pinecone')
    def test_create_index_success(self, mock_pinecone):
        """Test successful index creation."""
        mock_vectorstore = Mock()
        mock_pinecone.from_documents.return_value = mock_vectorstore
        
        documents = [Document(page_content="test", metadata={})]
        
        # Should not raise an exception
        self.ingester.create_index(documents)
        
        mock_pinecone.from_documents.assert_called_once()
    
    @patch('src.ingest.LC_Pinecone')
    def test_create_index_empty_documents(self, mock_pinecone):
        """Test index creation with empty document list."""
        self.ingester.create_index([])
        
        # Should not call Pinecone if no documents
        mock_pinecone.from_documents.assert_not_called()
    
    @patch('src.ingest.LC_Pinecone')
    def test_create_index_failure(self, mock_pinecone):
        """Test index creation failure."""
        mock_pinecone.from_documents.side_effect = Exception("Index creation failed")
        
        documents = [Document(page_content="test", metadata={})]
        
        with pytest.raises(Exception, match="Index creation failed"):
            self.ingester.create_index(documents)
    
    @patch.object(ScriptIngester, 'create_index')
    @patch.object(ScriptIngester, 'split_documents')
    @patch.object(ScriptIngester, 'load_scripts')
    def test_ingest_success(self, mock_load, mock_split, mock_create):
        """Test successful complete ingestion workflow."""
        # Mock the workflow steps
        mock_documents = [Document(page_content="test", metadata={})]
        mock_split_docs = [Document(page_content="test chunk", metadata={})]
        
        mock_load.return_value = mock_documents
        mock_split.return_value = mock_split_docs
        mock_create.return_value = None
        
        result = self.ingester.ingest()
        
        assert result["success"] is True
        assert result["documents_processed"] == 1
        assert result["chunks_created"] == 1
        assert "Successfully ingested" in result["message"]
    
    @patch.object(ScriptIngester, 'load_scripts')
    def test_ingest_no_documents(self, mock_load):
        """Test ingestion with no documents found."""
        mock_load.return_value = []
        
        result = self.ingester.ingest()
        
        assert result["success"] is False
        assert result["documents_processed"] == 0
        assert "No documents found" in result["message"]
    
    @patch.object(ScriptIngester, 'load_scripts')
    def test_ingest_failure(self, mock_load):
        """Test ingestion failure."""
        mock_load.side_effect = Exception("Load failed")
        
        result = self.ingester.ingest()
        
        assert result["success"] is False
        assert "Ingestion failed" in result["message"]


@patch('src.ingest.ScriptIngester')
def test_main_success(mock_ingester_class):
    """Test main function with successful ingestion."""
    mock_ingester = Mock()
    mock_ingester.ingest.return_value = {
        "success": True,
        "message": "Test success"
    }
    mock_ingester_class.return_value = mock_ingester
    
    # Import here to avoid issues with mocking
    from src.ingest import main
    
    # Should not raise SystemExit
    main()


@patch('src.ingest.ScriptIngester')
def test_main_failure(mock_ingester_class):
    """Test main function with ingestion failure."""
    mock_ingester = Mock()
    mock_ingester.ingest.return_value = {
        "success": False,
        "message": "Test failure"
    }
    mock_ingester_class.return_value = mock_ingester
    
    from src.ingest import main
    
    with pytest.raises(SystemExit, match="1"):
        main()
