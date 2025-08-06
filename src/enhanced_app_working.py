"""Working Enhanced Streamlit application with viral optimization features."""

import streamlit as st
import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Import our modules
try:
    from .config import logger, SCRIPTS_DIR
    from .ingest import ScriptIngester  
    from .generator import ScriptGenerator
    from .polish import ScriptPolisher
    from .utils import ScriptQualityChecker, ScriptFormatter
except ImportError:
    from src.config import logger, SCRIPTS_DIR
    from src.ingest import ScriptIngester
    from src.generator import ScriptGenerator  
    from src.polish import ScriptPolisher
    from src.utils import ScriptQualityChecker, ScriptFormatter

# Try to import enhanced features, fallback to basic if not available
try:
    from src.user_profile import UserProfileManager
    from src.viral_scorer import ViralPotentialScorer
    from src.hashtag_optimizer import HashtagOptimizer
    from src.manual_script_manager import ManualScriptManager
    ENHANCED_FEATURES = True
    logger.info("✅ Enhanced features loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Enhanced features not available: {e}")
    ENHANCED_FEATURES = False

def init_session_state():
    """Initialize Streamlit session state variables."""
    defaults = {
        'generated_scripts': [],
        'current_script': None,
        'ingestion_complete': False,
        'user_profile': None,
        'viral_analysis': None,
        'enhancement_enabled': ENHANCED_FEATURES
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def load_css():
    """Load custom CSS for better styling."""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .script-preview {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
    }
    
    .viral-score {
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .score-a { background: linear-gradient(45deg, #56ab2f, #a8e6cf); color: white; }
    .score-b { background: linear-gradient(45deg, #f093fb, #f5576c); color: white; }
    .score-c { background: linear-gradient(45deg, #4facfe, #00f2fe); color: white; }
    .score-d { background: linear-gradient(45deg, #ffecd2, #fcb69f); color: #333; }
    
    .enhancement-badge {
        background: #28a745;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .success-alert {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def create_sidebar():
    """Create sidebar with navigation and controls."""
    with st.sidebar:
        # Header
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h1>🎬 Script Writer</h1>
        </div>
        """, unsafe_allow_html=True)
        
        if ENHANCED_FEATURES:
            st.markdown('<span class="enhancement-badge">✨ ENHANCED</span>', unsafe_allow_html=True)
        
        # Navigation
        pages = {
            "🎯 Generate Script": "generate",
            "📊 Dashboard": "dashboard", 
            "👤 Profile": "profile",
            "📁 Scripts": "scripts",
            "🔥 Viral Analysis": "viral",
            "⚙️ Settings": "settings"
        }
        
        selected_page = st.selectbox(
            "Navigate to:",
            list(pages.keys()),
            index=0
        )
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        
        profile_status = "✅ Active" if st.session_state.user_profile else "❌ Not Set"
        st.markdown(f"**Profile:** {profile_status}")
        
        scripts_count = len(st.session_state.generated_scripts)
        st.markdown(f"**Generated:** {scripts_count} scripts")
        
        if st.session_state.viral_analysis:
            score = st.session_state.viral_analysis.get('percentage', 0)
            st.markdown(f"**Last Score:** {score:.1f}%")
        
        # Quick actions
        st.markdown("---")
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🔄 Ingest Scripts", use_container_width=True):
            ingest_scripts()
        
        if ENHANCED_FEATURES and st.button("📤 Upload Script", use_container_width=True):
            st.session_state.show_upload = True
    
    return pages[selected_page]

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
    if ENHANCED_FEATURES:
        st.markdown('<div class="main-header"><h1>🎯 Generate Viral Scripts</h1><p>AI-powered content optimized for maximum reach</p></div>', unsafe_allow_html=True)
    else:
        st.title("📝 Generate Instagram Script")
    
    # Generation form
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Script Details")
        
        topic = st.text_input(
            "What's your script topic?",
            placeholder="e.g., Morning routine for productivity",
            help="Describe what you want your Instagram script to be about"
        )
        
        if ENHANCED_FEATURES:
            # Enhanced options
            strategy = st.selectbox(
                "Generation Strategy",
                ["viral_optimized", "story_driven", "educational", "entertainment"],
                help="Choose the content strategy that best fits your goals"
            )
            
            with st.expander("🔧 Advanced Options"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    use_viral_scoring = st.checkbox("Viral Analysis", value=True)
                    auto_optimize = st.checkbox("Auto-optimize", value=True)
                
                with col_b:
                    use_trending = st.checkbox("Use Trending Data", value=True)
                    generate_hashtags = st.checkbox("Smart Hashtags", value=True)
        else:
            use_retrieval = st.checkbox("Use examples", value=True, help="Use similar scripts as examples")
    
    with col2:
        st.markdown("### 🎯 Status")
        
        if ENHANCED_FEATURES and st.session_state.user_profile:
            profile = st.session_state.user_profile
            st.success("✅ Profile Active")
            st.write(f"**Name:** {profile.name}")
            st.write(f"**Niche:** {profile.niche}")
        elif ENHANCED_FEATURES:
            st.warning("⚠️ No Profile Set")
            if st.button("Create Profile", use_container_width=True):
                st.session_state.current_page = "profile"
                st.rerun()
        
        # Recent performance
        if st.session_state.generated_scripts:
            recent_count = min(5, len(st.session_state.generated_scripts))
            st.write(f"**Recent Scripts:** {recent_count}")
    
    # Generate button
    if st.button("🚀 Generate Script", type="primary", disabled=not topic, use_container_width=True):
        if ENHANCED_FEATURES:
            generate_enhanced_script(topic, strategy, use_viral_scoring, generate_hashtags)
        else:
            generate_basic_script(topic, use_retrieval)
    
    # Display current script
    if st.session_state.current_script:
        display_generated_script(st.session_state.current_script)

def generate_enhanced_script(topic: str, strategy: str, use_viral_scoring: bool, generate_hashtags: bool):
    """Generate script with enhanced features."""
    with st.spinner("🚀 Generating optimized script..."):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Generate basic script
            status_text.text("🤖 Generating script...")
            progress_bar.progress(25)
            
            generator = ScriptGenerator()
            result = generator.generate_script(topic)
            
            if not result.get("success"):
                st.error("❌ Script generation failed")
                return
            
            script_content = result["script"]
            progress_bar.progress(50)
            
            # Step 2: Viral analysis if enabled
            if use_viral_scoring:
                status_text.text("🔍 Analyzing viral potential...")
                progress_bar.progress(75)
                
                try:
                    viral_scorer = ViralPotentialScorer()
                    user_context = None
                    if st.session_state.user_profile:
                        profile_manager = UserProfileManager()
                        profile_manager.current_profile = st.session_state.user_profile
                        user_context = profile_manager.get_context_for_generation()
                    
                    viral_score = viral_scorer.calculate_viral_score(script_content, topic, user_context)
                    st.session_state.viral_analysis = {
                        'percentage': viral_score.percentage,
                        'grade': viral_score.grade,
                        'breakdown': viral_score.breakdown,
                        'recommendations': viral_score.recommendations
                    }
                    
                except Exception as e:
                    logger.warning(f"Viral analysis failed: {e}")
                    st.session_state.viral_analysis = None
            
            # Step 3: Generate hashtags if enabled
            if generate_hashtags:
                status_text.text("🏷️ Optimizing hashtags...")
                try:
                    hashtag_optimizer = HashtagOptimizer()
                    user_context = None
                    if st.session_state.user_profile:
                        profile_manager = UserProfileManager()
                        profile_manager.current_profile = st.session_state.user_profile
                        user_context = profile_manager.get_context_for_generation()
                    
                    hashtags = hashtag_optimizer.generate_optimal_hashtags(topic, user_context, 25)
                    hashtag_tags = [h.tag for h in hashtags]
                    
                    # Add hashtags to script
                    if "HASHTAGS:" in script_content:
                        parts = script_content.split("HASHTAGS:")
                        script_content = parts[0] + "HASHTAGS:\n" + " ".join(hashtag_tags)
                    else:
                        script_content += f"\n\nHASHTAGS:\n{' '.join(hashtag_tags)}"
                    
                except Exception as e:
                    logger.warning(f"Hashtag optimization failed: {e}")
            
            progress_bar.progress(100)
            status_text.text("✅ Enhanced script generated!")
            
            # Save enhanced result
            enhanced_result = {
                "script": script_content,
                "topic": topic,
                "strategy": strategy,
                "success": True,
                "model_used": result.get("model_used", "gpt-3.5-turbo"),
                "retrieval_used": result.get("retrieval_used", False),
                "generated_at": datetime.now().isoformat()
            }
            
            st.session_state.current_script = enhanced_result
            st.session_state.generated_scripts.append(enhanced_result)
            
            # Show success with viral score if available
            if st.session_state.viral_analysis:
                score = st.session_state.viral_analysis['percentage']
                grade = st.session_state.viral_analysis['grade']
                st.success(f"🎉 Enhanced script generated! Viral Score: {score:.1f}% (Grade: {grade})")
            else:
                st.success("🎉 Enhanced script generated successfully!")
            
            # Clean up
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"❌ Enhanced generation failed: {str(e)}")
            logger.error(f"Enhanced generation error: {e}")

def generate_basic_script(topic: str, use_retrieval: bool):
    """Generate script with basic features."""
    generator = ScriptGenerator()
    
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🤖 Generating script...")
        progress_bar.progress(50)
        
        result = generator.generate_script(topic, use_retrieval)
        
        progress_bar.progress(100)
        status_text.text("✅ Script generated!")
        
        if result.get("success"):
            st.session_state.current_script = result
            st.session_state.generated_scripts.append(result)
            st.success(f"🎉 Generated script for: **{topic}**")
        else:
            st.error(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
        
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.error(f"❌ Generation failed: {str(e)}")
        logger.error(f"Generation error: {e}")

def display_generated_script(script_data: Dict[str, Any]):
    """Display a generated script with formatting and options."""
    st.markdown("---")
    st.markdown("## 📄 Generated Script")
    
    # Script metadata
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.session_state.viral_analysis:
            score = st.session_state.viral_analysis['percentage']
            st.metric("Viral Score", f"{score:.1f}%")
        else:
            st.metric("Status", "Generated")
    
    with col2:
        if st.session_state.viral_analysis:
            grade = st.session_state.viral_analysis['grade']
            st.metric("Grade", grade)
        else:
            strategy = script_data.get('strategy', 'Standard')
            st.metric("Strategy", strategy.replace('_', ' ').title())
    
    with col3:
        model = script_data.get('model_used', 'GPT-3.5')
        st.metric("Model", model.replace('gpt-', 'GPT-').upper())
    
    with col4:
        retrieval = "Yes" if script_data.get('retrieval_used') else "No"
        st.metric("Examples Used", retrieval)
    
    # Script content
    script_content = script_data.get('script', '')
    
    # Display viral score if available
    if st.session_state.viral_analysis:
        score = st.session_state.viral_analysis['percentage']
        grade = st.session_state.viral_analysis['grade']
        
        if score >= 90:
            score_class = "score-a"
        elif score >= 80:
            score_class = "score-b"
        elif score >= 70:
            score_class = "score-c"
        else:
            score_class = "score-d"
        
        st.markdown(f"""
        <div class="viral-score {score_class}">
            🎯 Viral Analysis: {score:.1f}% (Grade: {grade})
        </div>
        """, unsafe_allow_html=True)
    
    # Format and display script
    formatted_script = format_script_display(script_content)
    st.markdown(f'<div class="script-preview">{formatted_script}</div>', unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Copy Script", use_container_width=True):
            st.code(script_content, language="text")
            st.info("Script ready to copy!")
    
    with col2:
        if ENHANCED_FEATURES and st.button("🔍 Analyze", use_container_width=True):
            analyze_script_viral_potential(script_content, script_data.get('topic', ''))
    
    with col3:
        if st.button("✨ Polish", use_container_width=True):
            polish_current_script()
    
    with col4:
        if st.button("💾 Save", use_container_width=True):
            save_script_to_file(script_data)
    
    # Show recommendations if available
    if st.session_state.viral_analysis and st.session_state.viral_analysis.get('recommendations'):
        st.markdown("### 💡 Viral Optimization Tips")
        for i, rec in enumerate(st.session_state.viral_analysis['recommendations'][:3], 1):
            st.write(f"{i}. {rec}")

def format_script_display(script: str) -> str:
    """Format script for better display."""
    formatted = script.replace('\n\n', '<br><br>')
    
    # Format section headers
    sections = ['HOOK:', 'BODY:', 'CTA:', 'CAPTION:', 'VISUAL DIRECTIONS:', 'HASHTAGS:']
    for section in sections:
        formatted = formatted.replace(section, f'<strong style="color: #1976d2;">{section}</strong>')
    
    return formatted

def analyze_script_viral_potential(script_content: str, topic: str):
    """Analyze script for viral potential."""
    if not ENHANCED_FEATURES:
        st.warning("Viral analysis requires enhanced features")
        return
    
    with st.spinner("🔍 Analyzing viral potential..."):
        try:
            viral_scorer = ViralPotentialScorer()
            user_context = None
            if st.session_state.user_profile:
                profile_manager = UserProfileManager()
                profile_manager.current_profile = st.session_state.user_profile
                user_context = profile_manager.get_context_for_generation()
            
            viral_score = viral_scorer.calculate_viral_score(script_content, topic, user_context)
            
            st.session_state.viral_analysis = {
                'percentage': viral_score.percentage,
                'grade': viral_score.grade,
                'breakdown': viral_score.breakdown,
                'recommendations': viral_score.recommendations,
                'viral_elements': viral_score.viral_elements,
                'missing_elements': viral_score.missing_elements
            }
            
            st.success("✅ Viral analysis complete!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            logger.error(f"Viral analysis error: {e}")

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

def save_script_to_file(script_data: Dict[str, Any]):
    """Save script to a file."""
    try:
        topic = script_data.get("topic", "script")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_topic.replace(' ', '_')}_{timestamp}.txt"
        
        script_content = script_data.get("polished_script", script_data.get("script", ""))
        
        scripts_dir = Path(SCRIPTS_DIR)
        scripts_dir.mkdir(exist_ok=True)
        filepath = scripts_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        st.success(f"💾 Script saved as: {filename}")
        
    except Exception as e:
        st.error(f"❌ Failed to save script: {str(e)}")

def dashboard_page():
    """Show analytics dashboard."""
    st.markdown('<div class="main-header"><h1>📊 Performance Dashboard</h1></div>', unsafe_allow_html=True)
    
    if not st.session_state.generated_scripts:
        st.info("Generate some scripts to see your performance dashboard!")
        return
    
    scripts = st.session_state.generated_scripts
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_scripts = len(scripts)
        st.markdown(f'<div class="metric-card"><h3>{total_scripts}</h3><p>Total Scripts</p></div>', unsafe_allow_html=True)
    
    with col2:
        if ENHANCED_FEATURES:
            # Calculate average viral score if available
            viral_scores = []
            for script in scripts:
                if hasattr(script, 'viral_score'):
                    viral_scores.append(script.viral_score)
            
            if viral_scores:
                avg_score = sum(viral_scores) / len(viral_scores)
                st.markdown(f'<div class="metric-card"><h3>{avg_score:.1f}%</h3><p>Avg Viral Score</p></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="metric-card"><h3>-</h3><p>Viral Analysis</p></div>', unsafe_allow_html=True)
        else:
            polished_count = len([s for s in scripts if "polished_script" in s])
            st.markdown(f'<div class="metric-card"><h3>{polished_count}</h3><p>Polished Scripts</p></div>', unsafe_allow_html=True)
    
    with col3:
        strategies_used = len(set(s.get('strategy', 'standard') for s in scripts))
        st.markdown(f'<div class="metric-card"><h3>{strategies_used}</h3><p>Strategies Used</p></div>', unsafe_allow_html=True)
    
    with col4:
        recent_count = len([s for s in scripts if 'generated_at' in s])
        st.markdown(f'<div class="metric-card"><h3>{recent_count}</h3><p>Recent Scripts</p></div>', unsafe_allow_html=True)
    
    # Scripts list
    st.markdown("### 📋 Your Generated Scripts")
    
    for i, script in enumerate(reversed(scripts)):
        with st.expander(f"Script #{len(scripts)-i}: {script.get('topic', 'Unknown Topic')[:50]}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                script_preview = script.get('script', '')[:300] + "..."
                st.text_area("Preview", script_preview, height=100, key=f"preview_{i}", disabled=True)
            
            with col2:
                strategy = script.get('strategy', 'Standard')
                st.write(f"**Strategy:** {strategy.replace('_', ' ').title()}")
                
                generated_at = script.get('generated_at', '')
                if generated_at:
                    st.write(f"**Generated:** {generated_at[:10]}")
                
                if st.button("👁️ View", key=f"view_{i}"):
                    st.session_state.current_script = script
                    st.success("Script loaded!")
                
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    scripts.remove(script)
                    if st.session_state.current_script == script:
                        st.session_state.current_script = None
                    st.success("Script deleted!")
                    st.rerun()

def profile_page():
    """User profile management page."""
    if not ENHANCED_FEATURES:
        st.info("Profile management requires enhanced features. Using basic version.")
        return
    
    st.markdown('<div class="main-header"><h1>👤 User Profile</h1><p>Personalize your content generation</p></div>', unsafe_allow_html=True)
    
    if st.session_state.user_profile:
        # Show existing profile
        profile = st.session_state.user_profile
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📋 Current Profile")
            st.write(f"**Name:** {profile.name}")
            st.write(f"**Niche:** {profile.niche}")
            st.write(f"**Target Audience:** {profile.target_audience}")
            st.write(f"**Content Style:** {profile.content_style}")
            st.write(f"**Tone:** {profile.tone}")
            st.write(f"**Bio:** {profile.bio}")
        
        with col2:
            if st.button("✏️ Edit Profile", use_container_width=True):
                st.session_state.edit_profile = True
            
            if st.button("🗑️ Delete Profile", use_container_width=True):
                st.session_state.user_profile = None
                st.success("Profile deleted!")
                st.rerun()
    
    else:
        # Create new profile
        st.markdown("### 🆕 Create Your Profile")
        
        with st.form("create_profile"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Your Name*", placeholder="e.g., Sarah Johnson")
                niche = st.selectbox("Content Niche*", 
                                   ["fitness", "food", "lifestyle", "business", "tech", "fashion", "travel"])
            
            with col2:
                content_style = st.selectbox("Content Style", 
                                           ["informative", "entertaining", "inspirational", "educational"])
                tone = st.selectbox("Tone", 
                                  ["friendly", "professional", "casual", "authoritative"])
            
            bio = st.text_area("Bio/About You*", height=100,
                             placeholder="Tell us about yourself, your expertise, and what makes you unique...")
            
            target_audience = st.text_input("Target Audience", 
                                          placeholder="e.g., Young professionals aged 25-35")
            
            if st.form_submit_button("✅ Create Profile", type="primary"):
                if name and niche and bio:
                    try:
                        from src.user_profile import UserProfile
                        import hashlib
                        
                        # Create profile object
                        user_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
                        
                        profile = UserProfile(
                            user_id=user_id,
                            name=name,
                            bio=bio,
                            niche=niche,
                            target_audience=target_audience or f"People interested in {niche}",
                            content_style=content_style,
                            tone=tone,
                            key_topics=[niche],
                            personal_story=bio,
                            unique_selling_points=[f"Expert in {niche}"],
                            preferred_hashtags=[f"#{niche}"],
                            content_goals=f"Create engaging {niche} content",
                            created_at=datetime.now().isoformat(),
                            updated_at=datetime.now().isoformat()
                        )
                        
                        st.session_state.user_profile = profile
                        st.success("✅ Profile created successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error creating profile: {str(e)}")
                else:
                    st.error("❌ Please fill in all required fields")

def scripts_page():
    """Script management page."""
    st.title("📁 Script Management")
    
    if ENHANCED_FEATURES:
        tab1, tab2 = st.tabs(["🤖 Generated Scripts", "📤 Upload Scripts"])
        
        with tab1:
            if st.session_state.generated_scripts:
                st.write(f"You have {len(st.session_state.generated_scripts)} generated scripts")
                # Show scripts (already handled in dashboard_page)
            else:
                st.info("No generated scripts yet!")
        
        with tab2:
            st.markdown("### 📤 Upload Your Best Scripts")
            st.write("Upload your successful scripts to improve AI generation.")
            
            uploaded_file = st.file_uploader("Choose script file", type=['txt'])
            
            if uploaded_file:
                script_content = str(uploaded_file.read(), "utf-8")
                st.text_area("Content Preview", script_content, height=200, disabled=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input("Script Title", value=uploaded_file.name.replace('.txt', ''))
                    topic = st.text_input("Topic", placeholder="e.g., fitness tips")
                
                with col2:
                    notes = st.text_area("Notes", placeholder="Performance details, engagement, etc.")
                
                if st.button("📤 Upload Script", type="primary"):
                    try:
                        script_manager = ManualScriptManager()
                        uploaded_script = script_manager.upload_script_content(
                            script_content, title, topic, notes
                        )
                        st.success(f"✅ Script uploaded! Viral Score: {uploaded_script.viral_score:.1f}")
                    except Exception as e:
                        st.error(f"❌ Upload failed: {str(e)}")
    else:
        # Basic scripts management
        if st.session_state.generated_scripts:
            st.write(f"You have {len(st.session_state.generated_scripts)} generated scripts")
        else:
            st.info("No generated scripts yet!")

def viral_page():
    """Viral analysis page."""
    if not ENHANCED_FEATURES:
        st.info("Viral analysis requires enhanced features")
        return
    
    st.markdown('<div class="main-header"><h1>🔥 Viral Analysis</h1><p>Optimize your content for maximum reach</p></div>', unsafe_allow_html=True)
    
    # Analysis options
    analysis_source = st.radio("Analyze:", ["Current Script", "Paste Content"])
    
    script_content = ""
    
    if analysis_source == "Current Script":
        if st.session_state.current_script:
            script_content = st.session_state.current_script.get('script', '')
            st.text_area("Script Content", script_content, height=200, disabled=True)
        else:
            st.warning("No current script available")
    
    elif analysis_source == "Paste Content":
        script_content = st.text_area("Paste your script:", height=200)
    
    topic = st.text_input("Topic (optional)", placeholder="e.g., fitness tips")
    
    if st.button("🔍 Analyze Viral Potential", disabled=not script_content):
        analyze_script_viral_potential(script_content, topic)
    
    # Display results
    if st.session_state.viral_analysis:
        st.markdown("---")
        st.markdown("## 🎯 Analysis Results")
        
        analysis = st.session_state.viral_analysis
        score = analysis['percentage']
        grade = analysis['grade']
        
        # Score display
        if score >= 90:
            score_class = "score-a"
        elif score >= 80:
            score_class = "score-b"
        elif score >= 70:
            score_class = "score-c"
        else:
            score_class = "score-d"
        
        st.markdown(f"""
        <div class="viral-score {score_class}">
            🎯 Viral Score: {score:.1f}% (Grade: {grade})
        </div>
        """, unsafe_allow_html=True)
        
        # Breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Score Breakdown")
            breakdown = analysis.get('breakdown', {})
            for component, score_val in breakdown.items():
                component_name = component.replace('_', ' ').title()
                st.write(f"**{component_name}:** {score_val:.1f}")
        
        with col2:
            st.markdown("### 💡 Recommendations")
            recommendations = analysis.get('recommendations', [])
            for i, rec in enumerate(recommendations[:5], 1):
                st.write(f"{i}. {rec}")
        
        # Viral elements
        viral_elements = analysis.get('viral_elements', [])
        if viral_elements:
            st.markdown("### ✅ Viral Elements Found")
            for element in viral_elements:
                st.write(f"• {element.replace('_', ' ').title()}")
        
        # Missing elements
        missing_elements = analysis.get('missing_elements', [])
        if missing_elements:
            st.markdown("### ❌ Missing Elements")
            for element in missing_elements:
                st.write(f"• {element}")

def settings_page():
    """Settings and configuration page."""
    st.title("⚙️ Settings")
    
    # Feature status
    st.markdown("### 🔧 Feature Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Enhanced Features:** {'✅ Enabled' if ENHANCED_FEATURES else '❌ Disabled'}")
        st.write(f"**OpenAI API:** {'✅ Connected' if os.getenv('OPENAI_API_KEY') else '❌ Not configured'}")
    
    with col2:
        st.write(f"**Pinecone API:** {'✅ Connected' if os.getenv('PINECONE_API_KEY') else '❌ Not configured'}")
        st.write(f"**Scripts Directory:** 📁 {SCRIPTS_DIR}")
    
    # Data management
    st.markdown("### 💾 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Re-ingest Scripts"):
            ingest_scripts()
    
    with col2:
        if st.button("🧹 Clear Generated Scripts"):
            st.session_state.generated_scripts = []
            st.session_state.current_script = None
            st.success("Generated scripts cleared!")

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Instagram Script Writer Pro" if ENHANCED_FEATURES else "Instagram Script Writer",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize
    init_session_state()
    load_css()
    
    # Get current page from sidebar
    current_page = create_sidebar()
    
    # Route to appropriate page
    if current_page == "generate":
        generate_page()
    elif current_page == "dashboard":
        dashboard_page()
    elif current_page == "profile":
        profile_page()
    elif current_page == "scripts":
        scripts_page()
    elif current_page == "viral":
        viral_page()
    elif current_page == "settings":
        settings_page()

if __name__ == "__main__":
    main()