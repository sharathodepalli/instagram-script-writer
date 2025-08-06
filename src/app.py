"""Streamlit web application for Instagram Script-Writer."""

import streamlit as st
import os
from typing import Dict, Any, List, Optional
import time

# Import our modules
try:
    # Try relative import first (when running as part of a package)
    from .config import logger, SCRIPTS_DIR
    from .ingest import ScriptIngester
    from .generator import ScriptGenerator
    from .polish import ScriptPolisher
    from .utils import ScriptQualityChecker, ScriptFormatter
except ImportError:
    # Fall back to absolute import (when running directly)
    from src.config import logger, SCRIPTS_DIR
    from src.ingest import ScriptIngester
    from src.generator import ScriptGenerator
    from src.polish import ScriptPolisher
    from src.utils import ScriptQualityChecker, ScriptFormatter

# Import Telugu scraper modules
try:
    from scraper.scraper import ReelScraper
    from scraper.processor import ReelProcessor
    SCRAPER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Telugu scraper modules not available: {e}")
    SCRAPER_AVAILABLE = False


def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'generated_scripts' not in st.session_state:
        st.session_state.generated_scripts = []
    if 'current_script' not in st.session_state:
        st.session_state.current_script = None
    if 'ingestion_complete' not in st.session_state:
        st.session_state.ingestion_complete = False


def load_css():
    """Load custom CSS for better styling."""
    st.markdown("""
    <style>
    .script-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        color: #2c3e50;
        font-size: 16px;
        line-height: 1.6;
    }
    .section-header {
        color: #1f77b4;
        font-weight: bold;
        margin-top: 15px;
    }
    .quality-score {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 5px;
    }
    .score-excellent { background-color: #d4edda; color: #155724; }
    .score-good { background-color: #fff3cd; color: #856404; }
    .score-fair { background-color: #f8d7da; color: #721c24; }
    .score-poor { background-color: #f5c6cb; color: #721c24; }
    </style>
    """, unsafe_allow_html=True)


def sidebar():
    """Create sidebar with navigation and controls."""
    st.sidebar.title("🎬 Instagram Script-Writer")
    
    # Navigation
    pages = {
        "📝 Generate Script": "generate",
        "📚 Manage Scripts": "manage", 
        "🔧 Settings": "settings",
        "📊 Analytics": "analytics"
    }
    
    selected_page = st.sidebar.selectbox(
        "Navigate to:",
        list(pages.keys()),
        index=0
    )
    
    st.sidebar.markdown("---")
    
    # Quick actions
    st.sidebar.subheader("Quick Actions")
    
    if st.sidebar.button("🔄 Ingest Scripts"):
        with st.sidebar:
            ingest_scripts()
    
    if SCRAPER_AVAILABLE and st.sidebar.button("🇮🇳 Refresh Telugu Examples"):
        with st.sidebar:
            refresh_telugu_examples()
    
    if st.sidebar.button("📊 Check Quality"):
        if st.session_state.current_script:
            check_script_quality(st.session_state.current_script)
        else:
            st.sidebar.warning("No script to check")
    
    return pages[selected_page]


def refresh_telugu_examples():
    """Refresh Telugu examples: fetch, process, and ingest."""
    try:
        # Step 1: Initialize scraper and check environment
        with st.spinner("Initializing Telugu scraper..."):
            try:
                from src.scraper.config import validate_environment
                env_validation = validate_environment()
                
                if not env_validation["valid"]:
                    for error in env_validation["errors"]:
                        st.error(f"❌ Configuration error: {error}")
                    return
                
                for warning in env_validation.get("warnings", []):
                    st.warning(warning)
                
                scraper = ReelScraper()
            except Exception as e:
                st.error(f"❌ Failed to initialize Telugu scraper: {str(e)}")
                logger.error(f"Telugu scraper initialization error: {e}")
                return
        
        # Step 2: Fetch reels
        with st.spinner("Fetching Telugu reels from Instagram..."):
            logged_in = scraper.login()
            
            if not logged_in:
                st.warning("⚠️ Running in anonymous mode. Limited results may be available.")
                
            num_reels = scraper.fetch_reels()
            
            if num_reels == 0:
                st.error("❌ Failed to fetch any Telugu reels. Instagram may be rate-limiting requests or the hashtag might not exist.")
                return
                
            st.info(f"✅ Fetched {num_reels} Telugu reels")
        
        # Step 3: Process reels
        with st.spinner("Processing Telugu reels..."):
            try:
                processor = ReelProcessor()
                top_count, script_count = processor.process_all()
                
                if script_count == 0:
                    st.error("❌ Failed to generate any script templates from fetched reels.")
                    return
                    
                st.info(f"✅ Generated {script_count} script templates from top {top_count} reels")
            except Exception as e:
                st.error(f"❌ Failed to process Telugu reels: {str(e)}")
                logger.error(f"Telugu processing error: {e}")
                return
        
        # Step 4: Ingest scripts
        with st.spinner("Ingesting Telugu scripts into vector database..."):
            try:
                ingester = ScriptIngester()
                docs = ingester.load_scripts(include_telugu=True)
                
                if not docs:
                    st.error("❌ No documents found to ingest")
                    return
                    
                result = ingester.ingest_documents(docs)
                
                if not result:
                    st.error("❌ Failed to ingest documents")
                    return
                
                st.success(f"✅ Successfully refreshed Telugu examples! {script_count} scripts generated and {len(docs)} documents ingested.")
                st.session_state.ingestion_complete = True
                
            except Exception as e:
                st.error(f"❌ Failed to ingest Telugu scripts: {str(e)}")
                logger.error(f"Telugu ingestion error: {e}")
    
    except Exception as e:
        st.error(f"❌ Telugu refresh failed: {str(e)}")
        logger.error(f"Telugu refresh error: {e}")
        # Show suggestions for common errors
        if "rate limit" in str(e).lower() or "429" in str(e):
            st.warning("⚠️ Instagram may be rate-limiting requests. Try again later or use authenticated mode.")
        elif "authentication" in str(e).lower() or "login" in str(e).lower():
            st.warning("⚠️ Instagram authentication failed. Check your credentials in .env file.")


def ingest_scripts():
    """Handle script ingestion with progress feedback."""
    try:
        with st.spinner("Ingesting scripts..."):
            ingester = ScriptIngester()
            docs = ingester.load_scripts(include_telugu=True)
            result = ingester.ingest_documents(docs)
            
        if result:
            st.success(f"✅ Successfully ingested {len(docs)} scripts")
            st.session_state.ingestion_complete = True
        else:
            st.error("❌ Ingestion failed")
            
    except Exception as e:
        st.error(f"❌ Ingestion failed: {str(e)}")
        logger.error(f"Ingestion error: {e}")


def generate_page():
    """Main script generation page."""
    st.title("📝 Generate Instagram Script")
    
    # Topic input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        topic = st.text_input(
            "What's your script topic?",
            placeholder="e.g., Morning routine for productivity",
            help="Describe what you want your Instagram script to be about"
        )
    
    with col2:
        use_retrieval = st.checkbox("Use examples", value=True, help="Use similar scripts as examples")
    
    # Generation options
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            generate_variants = st.checkbox("Generate variants", help="Create multiple versions for A/B testing")
            variant_count = st.slider("Number of variants", 2, 5, 3) if generate_variants else 1
            
        with col2:
            auto_polish = st.checkbox("Auto-polish", value=True, help="Automatically polish the generated script")
            quality_check = st.checkbox("Quality check", value=True, help="Check script quality after generation")
    
    # Generate button
    if st.button("🚀 Generate Script", type="primary", disabled=not topic):
        generate_script_workflow(topic, use_retrieval, generate_variants, variant_count, auto_polish, quality_check)
    
    # Display current script
    if st.session_state.current_script:
        display_script(st.session_state.current_script)


def generate_script_workflow(topic: str, use_retrieval: bool, generate_variants: bool, 
                           variant_count: int, auto_polish: bool, quality_check: bool):
    """Handle the complete script generation workflow."""
    generator = ScriptGenerator()
    
    try:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Generate script(s)
        status_text.text("🤖 Generating script...")
        progress_bar.progress(20)
        
        if generate_variants:
            results = generator.generate_multiple_variants(topic, variant_count)
            if results:
                result = results[0]  # Use first variant as primary
                st.session_state.generated_scripts.extend(results)
            else:
                st.error("❌ Failed to generate script variants")
                return
        else:
            result = generator.generate_script(topic, use_retrieval)
            if result["success"]:
                st.session_state.generated_scripts.append(result)
            else:
                st.error(f"❌ Generation failed: {result['error']}")
                return
        
        progress_bar.progress(50)
        
        # Step 2: Polish (if enabled)
        if auto_polish and result["success"]:
            status_text.text("✨ Polishing script...")
            progress_bar.progress(70)
            
            polisher = ScriptPolisher()
            polish_result = polisher.polish_script(result["script"])
            
            if polish_result["success"]:
                result["polished_script"] = polish_result["polished_script"]
                result["polish_improvements"] = polish_result["improvements"]
        
        # Step 3: Quality check (if enabled)
        if quality_check and result["success"]:
            status_text.text("🔍 Checking quality...")
            progress_bar.progress(90)
            
            checker = ScriptQualityChecker()
            script_to_check = result.get("polished_script", result["script"])
            existing_scripts = [s["script"] for s in st.session_state.generated_scripts[:-1]]
            
            quality_result = checker.full_quality_check(script_to_check, existing_scripts)
            result["quality_check"] = quality_result
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Script generated successfully!")
        
        st.session_state.current_script = result
        
        # Show success message
        st.success(f"🎉 Generated script for: **{topic}**")
        
        # Clear progress indicators after a moment
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.error(f"❌ Generation failed: {str(e)}")
        logger.error(f"Generation workflow error: {e}")


def display_script(script_data: Dict[str, Any]):
    """Display a generated script with formatting and options."""
    st.markdown("---")
    st.subheader("📄 Generated Script")
    
    # Get the script text (polished if available, otherwise original)
    script_text = script_data.get("polished_script", script_data.get("script", ""))
    
    if not script_text:
        st.error("No script content available")
        return
    
    # Display formatted script
    formatted_script = ScriptFormatter.format_script_display(script_text)
    st.markdown(f'<div class="script-container">{formatted_script}</div>', unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Copy to Clipboard"):
            st.code(script_text, language="text")
            st.info("Script copied! Use Ctrl+C to copy from the code block above.")
    
    with col2:
        if st.button("✨ Polish Script"):
            polish_current_script()
    
    with col3:
        if st.button("🔍 Quality Check"):
            check_script_quality(script_data)
    
    with col4:
        if st.button("💾 Save Script"):
            save_script(script_data)
    
    # Show quality score if available
    if "quality_check" in script_data:
        display_quality_results(script_data["quality_check"])
    
    # Show metadata
    with st.expander("📊 Script Metadata"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Topic:** {script_data.get('topic', 'N/A')}")
            st.write(f"**Model:** {script_data.get('model_used', 'N/A')}")
            st.write(f"**Retrieval Used:** {'Yes' if script_data.get('retrieval_used') else 'No'}")
            
        with col2:
            if script_data.get("source_documents"):
                st.write(f"**Source Files:** {', '.join(script_data['source_documents'])}")
            if script_data.get("variant_number"):
                st.write(f"**Variant:** #{script_data['variant_number']}")


def polish_current_script():
    """Polish the current script."""
    if not st.session_state.current_script:
        st.error("No script to polish")
        return
        
    try:
        with st.spinner("Polishing script..."):
            polisher = ScriptPolisher()
            script_text = st.session_state.current_script.get("script", "")
            
            result = polisher.polish_script(script_text)
            
        if result["success"]:
            st.session_state.current_script["polished_script"] = result["polished_script"]
            st.session_state.current_script["polish_improvements"] = result["improvements"]
            st.success("✨ Script polished successfully!")
            st.rerun()
        else:
            st.error(f"❌ Polishing failed: {result['error']}")
            
    except Exception as e:
        st.error(f"❌ Polishing error: {str(e)}")


def check_script_quality(script_data: Dict[str, Any]):
    """Check and display script quality."""
    try:
        checker = ScriptQualityChecker()
        script_text = script_data.get("polished_script", script_data.get("script", ""))
        
        if not script_text:
            st.error("No script content to check")
            return
            
        existing_scripts = [s["script"] for s in st.session_state.generated_scripts if s != script_data]
        
        with st.spinner("Checking script quality..."):
            quality_result = checker.full_quality_check(script_text, existing_scripts)
        
        script_data["quality_check"] = quality_result
        display_quality_results(quality_result)
        
    except Exception as e:
        st.error(f"❌ Quality check failed: {str(e)}")


def display_quality_results(quality_result: Dict[str, Any]):
    """Display quality check results."""
    st.markdown("### 📊 Quality Analysis")
    
    # Overall score
    score = quality_result["overall_score"]
    max_score = quality_result["max_possible_score"]
    quality_level = quality_result["quality_level"]
    
    score_class = f"score-{quality_level}"
    
    st.markdown(f"""
    <div class="quality-score {score_class}">
        Quality Score: {score}/{max_score} ({quality_level.title()})
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed checks
    col1, col2 = st.columns(2)
    
    checks = quality_result["checks"]
    
    with col1:
        st.write("**Length Check:**")
        length_check = checks["length"]
        st.write(f"✅ {length_check['message']}" if length_check["within_limits"] else f"❌ {length_check['message']}")
        
        st.write("**Caption Check:**")
        caption_check = checks["caption"]
        if caption_check["caption_found"]:
            st.write(f"✅ {caption_check['message']}" if caption_check["within_limit"] else f"❌ {caption_check['message']}")
        else:
            st.write(f"❌ {caption_check['message']}")
    
    with col2:
        st.write("**Sections Check:**")
        sections_check = checks["sections"]
        st.write(f"✅ {sections_check['message']}" if sections_check["all_sections_present"] else f"❌ {sections_check['message']}")
        
        st.write("**Hashtags Check:**")
        hashtags_check = checks["hashtags"]
        if hashtags_check["hashtags_found"]:
            st.write(f"✅ {hashtags_check['message']}" if hashtags_check["optimal_count"] else f"⚠️ {hashtags_check['message']}")
        else:
            st.write(f"❌ {hashtags_check['message']}")
    
    # Duplicate check (if performed)
    if "duplicates" in checks:
        duplicate_check = checks["duplicates"]
        st.write("**Duplicate Check:**")
        st.write(f"✅ {duplicate_check['message']}" if not duplicate_check["is_duplicate"] else f"❌ {duplicate_check['message']}")


def save_script(script_data: Dict[str, Any]):
    """Save script to a file."""
    try:
        # Create filename
        topic = script_data.get("topic", "script")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_topic.replace(' ', '_')}.txt"
        
        # Get script content
        script_text = script_data.get("polished_script", script_data.get("script", ""))
        
        # Save to scripts directory
        os.makedirs(SCRIPTS_DIR, exist_ok=True)
        filepath = os.path.join(SCRIPTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(script_text)
        
        st.success(f"💾 Script saved as: {filename}")
        
    except Exception as e:
        st.error(f"❌ Failed to save script: {str(e)}")


def manage_page():
    """Script management page."""
    st.title("📚 Manage Scripts")
    
    # Show generated scripts
    if st.session_state.generated_scripts:
        st.subheader(f"Generated Scripts ({len(st.session_state.generated_scripts)})")
        
        for i, script in enumerate(st.session_state.generated_scripts):
            with st.expander(f"Script {i+1}: {script.get('topic', 'Unknown Topic')}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    script_text = script.get("polished_script", script.get("script", ""))
                    st.text_area("Script Content", script_text, height=150, key=f"script_{i}")
                
                with col2:
                    if st.button("Load", key=f"load_{i}"):
                        st.session_state.current_script = script
                        st.success("Script loaded!")
                    
                    if st.button("Delete", key=f"delete_{i}"):
                        st.session_state.generated_scripts.pop(i)
                        st.rerun()
    else:
        st.info("No scripts generated yet. Go to the Generate page to create your first script!")


def settings_page():
    """Settings and configuration page."""
    st.title("🔧 Settings")
    
    # Environment status
    st.subheader("Environment Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**OpenAI API:**")
        st.write("✅ Connected" if os.getenv("OPENAI_API_KEY") else "❌ Not configured")
        
        st.write("**Pinecone API:**")  
        st.write("✅ Connected" if os.getenv("PINECONE_API_KEY") else "❌ Not configured")
    
    with col2:
        st.write("**Scripts Directory:**")
        st.write(f"📁 {SCRIPTS_DIR}")
        script_count = len([f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.txt')]) if os.path.exists(SCRIPTS_DIR) else 0
        st.write(f"Scripts available: {script_count}")
    
    # Ingestion controls
    st.subheader("Script Ingestion")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Re-ingest All Scripts"):
            ingest_scripts()
    
    with col2:
        if st.button("🧹 Clear Generated Scripts"):
            st.session_state.generated_scripts = []
            st.session_state.current_script = None
            st.success("Generated scripts cleared!")


def analytics_page():
    """Analytics and insights page."""
    st.title("📊 Analytics")
    
    if not st.session_state.generated_scripts:
        st.info("No analytics available. Generate some scripts first!")
        return
    
    scripts = st.session_state.generated_scripts
    
    # Basic stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Scripts", len(scripts))
    
    with col2:
        polished_count = len([s for s in scripts if "polished_script" in s])
        st.metric("Polished Scripts", polished_count)
    
    with col3:
        avg_quality = sum([s.get("quality_check", {}).get("overall_score", 0) for s in scripts]) / len(scripts)
        st.metric("Avg Quality Score", f"{avg_quality:.1f}")
    
    with col4:
        unique_topics = len(set([s.get("topic", "") for s in scripts]))
        st.metric("Unique Topics", unique_topics)
    
    # Quality distribution
    st.subheader("Quality Distribution")
    
    quality_levels = [s.get("quality_check", {}).get("quality_level", "unknown") for s in scripts]
    quality_counts = {level: quality_levels.count(level) for level in set(quality_levels)}
    
    if quality_counts:
        st.bar_chart(quality_counts)
    
    # Recent scripts
    st.subheader("Recent Scripts")
    
    for script in scripts[-5:]:  # Show last 5 scripts
        with st.expander(f"📝 {script.get('topic', 'Unknown')}"):
            st.write(f"**Quality:** {script.get('quality_check', {}).get('quality_level', 'Not checked').title()}")
            st.write(f"**Polished:** {'Yes' if 'polished_script' in script else 'No'}")
            st.write(f"**Model:** {script.get('model_used', 'Unknown')}")


def main():
    """Main Streamlit application."""
    # Page config
    st.set_page_config(
        page_title="Instagram Script-Writer",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize
    init_session_state()
    load_css()
    
    # Get current page from sidebar
    current_page = sidebar()
    
    # Route to appropriate page
    if current_page == "generate":
        generate_page()
    elif current_page == "manage":
        manage_page()
    elif current_page == "settings":
        settings_page()
    elif current_page == "analytics":
        analytics_page()


if __name__ == "__main__":
    main()
