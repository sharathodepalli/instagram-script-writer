"""Integration tests for the Instagram Script-Writer application."""

import os
import pytest
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock
import pinecone
from langchain.schema import Document
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import FakeEmbeddings

from src.ingest import ScriptIngester
from src.generator import ScriptGenerator
from src.polish import ScriptPolisher
from src.utils import ScriptQualityChecker, ScriptFormatter
# Import Telugu scraper modules
try:
    from src.scraper.scraper import ReelScraper
    from src.scraper.processor import ReelProcessor
    from src.run_all import run_full, run_scraper, run_ingest, run_generate
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False


class TestIntegrationFlow:
    """Test the full application flow with mocked external services."""
    
    @pytest.fixture
    def mock_openai_completion(self):
        """Mock OpenAI ChatCompletion API calls."""
        with patch("openai.ChatCompletion.create") as mock_completion:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = """
HOOK: Tired of flat, boring Instagram content?

BODY:
Let me share a secret: the difference between average and viral content isn't just what you say—it's HOW you say it.

I spent years creating content that barely got noticed until I discovered these three psychological triggers that make viewers stop scrolling and engage:

1️⃣ Pattern interrupts - Start with something unexpected
2️⃣ Identity statements - Help viewers see themselves in your content
3️⃣ Open loops - Create curiosity that needs resolution

The best part? You can implement all three in your very next post!

CTA: Try these triggers in your next Reel and drop a comment with your results! Want my in-depth guide? Tap the link in bio!

CAPTION: Transform your Instagram engagement with these 3 psychology-backed content triggers that stop the scroll! #ContentCreator

VISUAL DIRECTIONS:
- Open with surprised expression, text overlay: "STOP POSTING UNTIL YOU KNOW THIS!"
- Cut to speaking directly to camera, energetic but authentic
- Use simple text animations for the 3 triggers
- Show before/after engagement examples
- End with encouraging hand gesture toward comments

HASHTAGS:
#ContentStrategy #InstagramTips #CreatorEconomy #EngagementHacks #SocialMediaTips #ReelsTips #CreatorAdvice
"""
            mock_completion.return_value = mock_response
            yield mock_completion

    @pytest.fixture
    def mock_pinecone_index(self):
        """Mock Pinecone initialization and index operations."""
        mock_index = Mock()
        # Mock query response
        mock_index.query.return_value = {
            "matches": [
                {"id": "doc1", "score": 0.92, "metadata": {"text": "Sample script 1"}},
                {"id": "doc2", "score": 0.85, "metadata": {"text": "Sample script 2"}},
                {"id": "doc3", "score": 0.78, "metadata": {"text": "Sample script 3"}}
            ]
        }
        
        mock_pinecone_client = Mock()
        mock_pinecone_client.Index.return_value = mock_index
        
        with patch("src.generator.Pinecone", return_value=mock_pinecone_client):
            yield mock_index

    @pytest.fixture
    def mock_langchain_pinecone(self):
        """Mock LangChain Pinecone operations."""
        with patch("langchain.vectorstores.Pinecone.from_documents") as mock_from_docs, \
             patch("langchain.vectorstores.Pinecone.from_existing_index") as mock_from_existing:
            
            # Create a simple FAISS index with fake embeddings for in-memory testing
            fake_embeddings = FakeEmbeddings(size=1536)  # OpenAI uses 1536-dim embeddings
            sample_docs = [
                Document(page_content="Sample Instagram script about fitness", 
                         metadata={"source": "fitness.txt"}),
                Document(page_content="Sample Instagram script about cooking", 
                         metadata={"source": "cooking.txt"}),
                Document(page_content="Sample Instagram script about travel", 
                         metadata={"source": "travel.txt"}),
            ]
            faiss_index = FAISS.from_documents(sample_docs, fake_embeddings)
            
            mock_from_docs.return_value = faiss_index
            mock_from_existing.return_value = faiss_index
            yield (mock_from_docs, mock_from_existing)

    @pytest.fixture
    def mock_text_loader(self):
        """Mock TextLoader to return sample documents."""
        with patch("langchain.document_loaders.TextLoader") as mock_loader:
            mock_load_instance = MagicMock()
            mock_load_instance.load.return_value = [
                Document(page_content="Sample Instagram script 1", metadata={"source": "script1.txt"}),
                Document(page_content="Sample Instagram script 2", metadata={"source": "script2.txt"}),
                Document(page_content="Sample Instagram script 3", metadata={"source": "script3.txt"}),
            ]
            mock_loader.return_value = mock_load_instance
            yield mock_loader

    @patch("langchain.embeddings.openai.OpenAIEmbeddings")
    @patch("langchain.chat_models.ChatOpenAI")
    def test_end_to_end_flow(self, mock_chat_openai, mock_embeddings, 
                            mock_text_loader, mock_langchain_pinecone, 
                            mock_pinecone_index, mock_openai_completion):
        """Test the full application flow from ingestion to quality control."""
        # 1. Setup environment to avoid missing env vars
        os.environ["OPENAI_API_KEY"] = "fake-api-key"
        os.environ["PINECONE_API_KEY"] = "fake-pinecone-key"
        os.environ["PINECONE_ENV"] = "test-env"
        os.environ["PINECONE_INDEX"] = "test-index"

        # 2. Ingest sample scripts
        ingester = ScriptIngester()
        docs = ingester.load_scripts()
        assert len(docs) > 0, "No documents loaded"
        ingester.ingest_documents(docs)
        
        # 3. Generate script
        generator = ScriptGenerator()
        script = generator.generate_script("test topic")
        assert isinstance(script, str), "Generated script should be a string"
        assert len(script) > 0, "Generated script should not be empty"
        
        # 4. Polish script
        polisher = ScriptPolisher()
        polished_script = polisher.polish(script)
        assert isinstance(polished_script, str), "Polished script should be a string"
        assert len(polished_script) > 0, "Polished script should not be empty"
        
        # 5. Quality control checks
        qc = ScriptQualityChecker()
        
        # 5.1 Check if the script has all required sections
        required_sections = ["HOOK:", "BODY:", "CTA:", "CAPTION:", "VISUAL DIRECTIONS:", "HASHTAGS:"]
        for section in required_sections:
            assert section in polished_script, f"Script missing required section: {section}"
        
        # 5.2 Extract caption and check length
        script_formatter = ScriptFormatter()
        caption = script_formatter.extract_section(polished_script, "CAPTION")
        caption_check = qc.check_caption_length(caption)
        assert caption_check.get("within_limits", False), f"Caption length check failed: {caption_check.get('message', '')}"
        
        # 5.3 Check for appropriate hashtags
        hashtags = script_formatter.extract_section(polished_script, "HASHTAGS")
        hashtag_list = [tag.strip() for tag in hashtags.split("#") if tag.strip()]
        assert 5 <= len(hashtag_list) <= 20, f"Expected 5-20 hashtags, got {len(hashtag_list)}"
        
        print("✅ End-to-end integration test passed successfully")


@pytest.mark.skipif(not SCRAPER_AVAILABLE, reason="Telugu scraper modules not available")
class TestTeluguScraperIntegration:
    """Test the Telugu scraper integration with the full pipeline."""
    
    @pytest.fixture
    def setup_temp_dirs(self):
        """Create temporary directories for testing."""
        temp_base = tempfile.mkdtemp()
        temp_raw = os.path.join(temp_base, "data", "raw_reels", "Telugu")
        temp_scripts = os.path.join(temp_base, "scripts", "auto_telugu")
        
        os.makedirs(temp_raw, exist_ok=True)
        os.makedirs(temp_scripts, exist_ok=True)
        
        # Create a sample reel JSON
        sample_reel = {
            "id": 12345,
            "shortcode": "ABC123",
            "views": 50000,
            "likes": 1000,
            "comments": 200,
            "caption": "This is a sample Telugu reel caption. #Telugu #Trending",
            "audio": "Popular Telugu Song"
        }
        
        with open(os.path.join(temp_raw, "ABC123.json"), "w") as f:
            json.dump(sample_reel, f)
        
        yield temp_base, temp_raw, temp_scripts
        
        # Clean up after test
        shutil.rmtree(temp_base)
    
    @patch("src.scraper.scraper.ReelScraper")
    @patch("src.scraper.processor.ReelProcessor")
    @patch("src.ingest.ScriptIngester")
    @patch("src.generator.ScriptGenerator")
    @patch("src.polish.ScriptPolisher")
    def test_run_full_pipeline(
        self, mock_polisher, mock_generator, mock_ingester, 
        mock_processor, mock_scraper, setup_temp_dirs
    ):
        """Test the full pipeline from scraping to generation."""
        temp_base, temp_raw, temp_scripts = setup_temp_dirs
        
        # Mock scraper
        mock_scraper_instance = MagicMock()
        mock_scraper_instance.login.return_value = True
        mock_scraper_instance.fetch_reels.return_value = 5
        mock_scraper.return_value = mock_scraper_instance
        
        # Mock processor
        mock_processor_instance = MagicMock()
        mock_processor_instance.process_all.return_value = (3, 3)  # (top_count, script_count)
        mock_processor.return_value = mock_processor_instance
        
        # Mock ingester
        mock_ingester_instance = MagicMock()
        mock_ingester_instance.load_scripts.return_value = ["doc1", "doc2", "doc3"]
        mock_ingester_instance.ingest_documents.return_value = True
        mock_ingester.return_value = mock_ingester_instance
        
        # Mock generator
        sample_draft = """
HOOK: Sample Telugu reel hook

BODY:
- Original audio: "Popular Telugu Song"
- Visual: mirror pacing of key scene.
- Narration: summarize action.

CTA:
"Follow for more Telugu trends!"

CAPTION:
This is a sample Telugu reel caption.

HASHTAGS:
#Telugu #Trending #Reels #TeluguReels #InstaTelugu

VISUAL_DIRECTIONS:
- replicate camera angles & transitions.
"""
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_script.return_value = sample_draft
        mock_generator.return_value = mock_generator_instance
        
        # Mock polisher
        mock_polisher_instance = MagicMock()
        mock_polisher_instance.polish.return_value = sample_draft + "\nPOLISHED: yes"
        mock_polisher.return_value = mock_polisher_instance
        
        # Run the full pipeline
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test_key", 
            "PINECONE_API_KEY": "test_key",
            "RAW_DIR": os.path.join(temp_base, "data", "raw_reels"),
            "SCRIPT_DIR": os.path.join(temp_base, "scripts", "auto_telugu"),
        }):
            result = run_full("test topic")
            
            # Verify each component was called correctly
            mock_scraper_instance.login.assert_called_once()
            mock_scraper_instance.fetch_reels.assert_called_once()
            mock_processor_instance.process_all.assert_called_once()
            mock_ingester_instance.load_scripts.assert_called_once()
            mock_ingester_instance.ingest_documents.assert_called_once()
            mock_generator_instance.generate_script.assert_called_once_with("test topic")
            mock_polisher_instance.polish.assert_called_once()
            
            # Verify result contains all required sections
            assert "HOOK:" in result
            assert "BODY:" in result
            assert "CTA:" in result
            assert "CAPTION:" in result
            assert "HASHTAGS:" in result
            assert "VISUAL_DIRECTIONS:" in result
            assert "POLISHED: yes" in result


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
