"""Ingestion module for embedding and indexing Instagram scripts."""

import os
import glob
from typing import List, Dict, Any
from pinecone import Pinecone
import tenacity
from langchain_community.document_loaders import TextLoader
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Updated imports to resolve deprecation warnings
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

try:
    # Try relative import first (for when running as part of the app)
    from .config import (
        PINECONE_API_KEY,
        PINECONE_HOST,
        PINECONE_INDEX,
        PINECONE_REGION,
        EMBEDDING_MODEL,
        SCRIPTS_DIR,
        DEFAULT_HASHTAGS,
        logger
    )
except ImportError:
    # Fall back to absolute import (for when running directly)
    from config import (
        PINECONE_API_KEY,
        PINECONE_HOST,
        PINECONE_INDEX,
        PINECONE_REGION,
        EMBEDDING_MODEL,
        SCRIPTS_DIR,
        DEFAULT_HASHTAGS,
        logger
    )
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

try:
    # Try relative import first (for when running as part of the app)
    from .config import (
        PINECONE_API_KEY,
        PINECONE_HOST,
        PINECONE_INDEX,
        PINECONE_REGION,
        EMBEDDING_MODEL,
        SCRIPTS_DIR,
        DEFAULT_HASHTAGS,
        logger
    )
except ImportError:
    # Fall back to absolute import (for when running directly)
    from src.config import (
        PINECONE_API_KEY,
        PINECONE_HOST,
        PINECONE_INDEX,
        PINECONE_REGION,
        EMBEDDING_MODEL,
        SCRIPTS_DIR,
        DEFAULT_HASHTAGS,
        logger
    )


class ScriptIngester:
    """Handles ingestion and indexing of Instagram scripts into Pinecone."""
    
    def __init__(self):
        """Initialize the ingester with Pinecone connection."""
        self._initialize_pinecone()
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone connection."""
        try:
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            logger.info(f"Connected to Pinecone host: {PINECONE_HOST}")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    def load_scripts(self, scripts_dir: str = SCRIPTS_DIR, include_telugu: bool = True) -> List[Document]:
        """
        Load all text files from the scripts directory.
        
        Args:
            scripts_dir: Directory containing script text files
            include_telugu: Whether to include Telugu auto-generated scripts
            
        Returns:
            List of Document objects
        """
        if not os.path.exists(scripts_dir):
            logger.warning(f"Scripts directory {scripts_dir} does not exist")
            return []
        
        # Collect all script paths
        script_files = glob.glob(os.path.join(scripts_dir, "*.txt"))
        
        # Add Telugu scripts if requested
        if include_telugu:
            telugu_dir = os.path.join(scripts_dir, "auto_telugu")
            if os.path.exists(telugu_dir):
                telugu_files = glob.glob(os.path.join(telugu_dir, "*.txt"))
                script_files.extend(telugu_files)
                logger.info(f"Including {len(telugu_files)} Telugu scripts from {telugu_dir}")
            else:
                logger.info(f"Telugu scripts directory {telugu_dir} does not exist")
        
        if not script_files:
            logger.warning(f"No .txt files found in {scripts_dir}" + 
                         (f" or {os.path.join(scripts_dir, 'auto_telugu')}" if include_telugu else ""))
            return []
            
        documents = []
        
        for file_path in script_files:
            try:
                loader = TextLoader(file_path, encoding="utf-8")
                file_docs = loader.load()
                
                # Add metadata
                for doc in file_docs:
                    doc.metadata.update({
                        "source_file": os.path.basename(file_path),
                        "file_path": file_path
                    })
                    
                documents.extend(file_docs)
                logger.info(f"Loaded script: {os.path.basename(file_path)}")
                
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                continue
                
        logger.info(f"Successfully loaded {len(documents)} documents from {len(script_files)} files")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better retrieval.
        
        Args:
            documents: List of documents to split
            
        Returns:
            List of split document chunks
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        split_docs = text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks")
        return split_docs
    
    @tenacity.retry(
        wait=tenacity.wait_exponential(min=1, max=10),
        stop=tenacity.stop_after_attempt(5),
        retry=tenacity.retry_if_exception_type((Exception,))
    )
    def create_index(self, documents: List[Document]) -> None:
        """
        Create or update the Pinecone index with documents.
        
        Args:
            documents: List of documents to index
            
        Raises:
            ValueError: If no documents are provided
            ConnectionError: If Pinecone connection fails
            RuntimeError: If indexing fails
        """
        if not documents:
            error_msg = "No documents to index"
            logger.warning(error_msg)
            raise ValueError(error_msg)
            
        try:
            # Use direct Pinecone client instead of langchain-pinecone (which has compatibility issues)
            index_name = PINECONE_INDEX
            logger.info(f"Connecting to existing index: {index_name}")
            
            # Get the index directly
            index = self.pc.Index(index_name)
            
            # Prepare vectors for direct upsert
            import uuid
            vectors = []
            for i, doc in enumerate(documents):
                vector_id = f"script_{i}_{str(uuid.uuid4())[:8]}"
                embedding = self.embeddings.embed_query(doc.page_content)
                
                # Extract filename from source path
                source_path = doc.metadata.get("source", "unknown")
                source_filename = os.path.basename(source_path) if source_path != "unknown" else "unknown"
                
                vector = {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "text": doc.page_content,
                        "source": source_filename,
                        "source_path": source_path,
                        "content_type": "instagram_script"
                    }
                }
                vectors.append(vector)
            
            # Direct upsert to Pinecone
            upsert_response = index.upsert(vectors=vectors)
            logger.info(f"Successfully indexed {len(documents)} documents into '{index_name}': {upsert_response}")
            
        except Exception as e:
            error_msg = f"Pinecone API error: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
            
    def ingest_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Ingest provided documents into the Pinecone index.
        
        Args:
            documents: List of documents to ingest
            
        Returns:
            Dictionary with ingestion results containing:
            - success: Boolean indicating success/failure
            - message: Description of the result
            - documents_processed: Number of documents processed
            - chunks_created: Number of chunks created (if successful)
        """
        if not documents:
            logger.warning("No documents provided for ingestion")
            return {
                "success": False,
                "message": "No documents provided for ingestion",
                "documents_processed": 0
            }
        
        try:
            # Split documents
            split_docs = self.split_documents(documents)
            
            # Create index
            self.create_index(split_docs)
            
            result = {
                "success": True,
                "message": f"Successfully ingested {len(split_docs)} document chunks",
                "documents_processed": len(documents),
                "chunks_created": len(split_docs)
            }
            
            logger.info(f"Document ingestion completed: {result}")
            return result
            
        except Exception as e:
            error_msg = f"Document ingestion failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "documents_processed": 0
            }
    
    def ingest(self, scripts_dir: str = SCRIPTS_DIR, include_telugu: bool = True) -> Dict[str, Any]:
        """
        Main ingestion workflow.
        
        Args:
            scripts_dir: Directory containing script files
            include_telugu: Whether to include Telugu auto-generated scripts
            
        Returns:
            Dictionary with ingestion results
        """
        logger.info(f"Starting script ingestion process from {scripts_dir}" + 
                   (f" including Telugu scripts" if include_telugu else ""))
        
        try:
            # Load documents
            documents = self.load_scripts(scripts_dir, include_telugu)
            
            if not documents:
                error_msg = f"No script documents found in {scripts_dir}" + \
                           (f" or its Telugu subdirectory" if include_telugu else "")
                logger.warning(error_msg)
                return {
                    "success": False,
                    "message": error_msg,
                    "documents_processed": 0
                }
            
            # Use the ingest_documents method to process the documents
            result = self.ingest_documents(documents)
            logger.info(f"Ingestion completed: {result}")
            return result
            
        except Exception as e:
            error_msg = f"Ingestion failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "documents_processed": 0,
                "error": str(e)
            }


def main():
    """CLI entry point for ingestion."""
    ingester = ScriptIngester()
    result = ingester.ingest()
    
    if result["success"]:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['message']}")
        exit(1)


if __name__ == "__main__":
    main()
