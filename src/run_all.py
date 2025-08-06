"""Command-line interface for running the Instagram Script-Writer pipeline."""

import argparse
import time
import sys
from typing import Optional, Dict, Any, Tuple
import logging

from src.config import logger
from src.scraper.scraper import ReelScraper
from src.scraper.processor import ReelProcessor
from src.ingest import ScriptIngester
from src.generator import ScriptGenerator
from src.polish import ScriptPolisher
from src.utils import ScriptQualityChecker, ScriptFormatter


def run_scraper() -> int:
    """
    Run the scraper and processor.
    
    Returns:
        Number of script templates generated
    
    Raises:
        RuntimeError: If scraper or processor encounters an unrecoverable error
    """
    logger.info("Starting scraper phase...")
    
    try:
        # Initialize and run scraper
        scraper = ReelScraper()
        logged_in = scraper.login()
        if not logged_in:
            logger.warning("Running in anonymous mode. Results may be limited.")
        
        num_reels = scraper.fetch_reels()
        if num_reels == 0:
            logger.error("No reels were fetched. Check your internet connection and Instagram access.")
            raise RuntimeError("Failed to fetch any reels")
            
        logger.info(f"Fetched {num_reels} reels")
        
        # Process the reels
        processor = ReelProcessor()
        top_count, script_count = processor.process_all()
        
        if script_count == 0:
            logger.error("No script templates were generated. Check the reel data.")
            raise RuntimeError("Failed to generate any script templates")
        
        logger.info(f"✅ Scraper phase complete: {top_count} top reels processed, {script_count} script templates generated")
        return script_count
        
    except Exception as e:
        logger.error(f"❌ Scraper phase failed: {str(e)}")
        raise RuntimeError(f"Scraper phase failed: {str(e)}") from e


def run_ingest() -> int:
    """
    Run the ingestion process.
    
    Returns:
        Number of documents ingested
    
    Raises:
        RuntimeError: If ingestion process fails
    """
    logger.info("Starting ingest phase...")
    
    try:
        # Initialize and run ingester
        ingester = ScriptIngester()
        docs = ingester.load_scripts(include_telugu=True)
        
        if not docs:
            error_msg = "No documents found to ingest"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        result = ingester.ingest_documents(docs)
        
        if not result.get("success", False):
            error_msg = result.get("message", "Ingestion failed")
            logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        logger.info(f"✅ Ingest phase complete: {len(docs)} documents ingested")
        return len(docs)
        
    except Exception as e:
        logger.error(f"❌ Ingest phase failed: {str(e)}")
        raise RuntimeError(f"Ingest phase failed: {str(e)}") from e


def run_generate(topic: str) -> Optional[str]:
    """
    Run the generation process.
    
    Args:
        topic: The topic to generate a script about
    
    Returns:
        The final polished script or None if generation failed
    
    Raises:
        ValueError: If no topic is provided
        RuntimeError: If generation process fails
    """
    if not topic:
        error_msg = "No topic provided for generation"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"Starting generation phase for topic: {topic}")
    
    try:
        # Initialize generator and generate script
        generator = ScriptGenerator()
        draft = generator.generate_script(topic)
        
        if not draft:
            error_msg = "Failed to generate script draft"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info("Draft generated, starting polish phase...")
        
        # Polish the draft
        polisher = ScriptPolisher()
        final = polisher.polish(draft)
        
        if not final:
            logger.warning("Polish phase failed, returning unpolished draft")
            return draft  # Return draft if polish fails
        
        # Run quality checks
        qc = ScriptQualityChecker()
        formatter = ScriptFormatter()
        
        caption = formatter.extract_section(final, "CAPTION")
        caption_check = qc.check_caption_length(caption)
        
        if not caption_check.get("within_limits", False):
            logger.warning(f"Caption length check failed: {caption_check.get('message', '')}")
        else:
            logger.info("Quality checks passed")
        
        logger.info("✅ Generation and polish phases complete")
        return final
        
    except Exception as e:
        logger.error(f"❌ Generation phase failed: {str(e)}")
        raise RuntimeError(f"Generation phase failed: {str(e)}") from e


def run_full(topic: str) -> Optional[str]:
    """
    Run the full pipeline from scraping to generation.
    
    Args:
        topic: The topic to generate a script about
        
    Returns:
        The final polished script or None if any phase fails
    """
    logger.info("Starting full pipeline...")
    
    try:
        # Run scraper
        script_count = run_scraper()
        logger.info(f"Scraper phase completed with {script_count} scripts")
        
        # Run ingest
        doc_count = run_ingest()
        logger.info(f"Ingest phase completed with {doc_count} documents")
        
        # Run generate
        final = run_generate(topic)
        
        logger.info("✅ Full pipeline completed successfully!")
        return final
        
    except Exception as e:
        logger.error(f"❌ Full pipeline failed: {str(e)}")
        return None


def main():
    """Main entry point for command-line execution."""
    parser = argparse.ArgumentParser(description="Instagram Script-Writer Pipeline")
    parser.add_argument("--mode", type=str, required=True, 
                        choices=["scraper", "ingest", "generate", "full"],
                        help="Pipeline mode to run")
    parser.add_argument("--topic", type=str, help="Topic for script generation")
    
    args = parser.parse_args()
    
    try:
        # Execute based on mode
        if args.mode == "scraper":
            script_count = run_scraper()
            print(f"✅ Successfully generated {script_count} script templates")
            
        elif args.mode == "ingest":
            doc_count = run_ingest()
            print(f"✅ Successfully ingested {doc_count} documents")
            
        elif args.mode == "generate":
            if not args.topic:
                parser.error("--topic is required when mode is 'generate'")
                
            script = run_generate(args.topic)
            if script:
                print("\n--- GENERATED SCRIPT ---\n")
                print(script)
                print("\n✅ Script generation complete")
            else:
                print("\n❌ Script generation failed")
                sys.exit(1)
                
        elif args.mode == "full":
            if not args.topic:
                parser.error("--topic is required when mode is 'full'")
                
            script = run_full(args.topic)
            if script:
                print("\n--- GENERATED SCRIPT ---\n")
                print(script)
                print("\n✅ Full pipeline completed successfully")
            else:
                print("\n❌ Full pipeline failed")
                sys.exit(1)
                
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
