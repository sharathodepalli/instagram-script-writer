"""Enhanced Streamlit application with all viral optimization features."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
import time
import json
from pathlib import Path
from datetime import datetime

# Enhanced UI components
try:
    from streamlit_option_menu import option_menu
    from streamlit_aggrid import AgGrid, GridOptionsBuilder
    ENHANCED_UI_AVAILABLE = True
except ImportError:
    ENHANCED_UI_AVAILABLE = False

# Import all our enhanced modules
try:
    from .config import logger, SCRIPTS_DIR
    from .user_profile import UserProfileManager
    from .hashtag_optimizer import HashtagOptimizer
    from .viral_scorer import ViralPotentialScorer, format_viral_score_report
    from .enhanced_scraper import EnhancedContentScraper
    from .enhanced_generator import EnhancedScriptGenerator, analyze_script_performance_potential
    from .manual_script_manager import ManualScriptManager
except ImportError:
    from src.config import logger, SCRIPTS_DIR
    from src.user_profile import UserProfileManager
    from src.hashtag_optimizer import HashtagOptimizer
    from src.viral_scorer import ViralPotentialScorer, format_viral_score_report
    from src.enhanced_scraper import EnhancedContentScraper
    from src.enhanced_generator import EnhancedScriptGenerator, analyze_script_performance_potential
    from src.manual_script_manager import ManualScriptManager


class EnhancedInstagramScriptWriter:
    """Enhanced Instagram Script Writer with all viral optimization features."""
    
    def __init__(self):
        """Initialize the enhanced application."""
        self.profile_manager = UserProfileManager()
        self.hashtag_optimizer = HashtagOptimizer()
        self.viral_scorer = ViralPotentialScorer()
        self.scraper = EnhancedContentScraper()
        self.generator = EnhancedScriptGenerator()
        self.script_manager = ManualScriptManager()
        
        # Initialize session state
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        defaults = {
            'current_script': None,
            'generated_scripts': [],
            'user_profile': None,
            'trending_insights': {},
            'optimization_history': [],
            'uploaded_scripts': [],
            'selected_strategy': 'viral_optimized',
            'viral_analysis': None
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def run(self):
        """Run the enhanced Streamlit application."""
        # Page configuration
        st.set_page_config(
            page_title="Instagram Script Writer Pro",
            page_icon="🎬",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Load custom CSS
        self._load_custom_css()
        
        # Sidebar navigation
        selected_page = self._create_sidebar()
        
        # Main content area
        if selected_page == "🎯 Generate":
            self._show_generation_page()
        elif selected_page == "📊 Dashboard":
            self._show_dashboard_page()
        elif selected_page == "👤 Profile":
            self._show_profile_page()
        elif selected_page == "📁 Scripts":
            self._show_scripts_page()
        elif selected_page == "🔥 Viral Analysis":
            self._show_viral_analysis_page()
        elif selected_page == "📈 Trends":
            self._show_trends_page()
        elif selected_page == "⚙️ Settings":
            self._show_settings_page()
    
    def _load_custom_css(self):
        """Load custom CSS for enhanced styling."""
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
            font-size: 2rem;
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
        
        .hashtag-cloud {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        
        .hashtag-tag {
            background: #e3f2fd;
            color: #1976d2;
            padding: 0.25rem 0.5rem;
            border-radius: 15px;
            font-size: 0.8rem;
            border: 1px solid #bbdefb;
        }
        
        .success-alert {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        .warning-alert {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _create_sidebar(self):
        """Create enhanced sidebar navigation."""
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1>🎬 Script Writer Pro</h1>
                <p>AI-Powered Viral Content Generator</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation menu
            if ENHANCED_UI_AVAILABLE:
                selected = option_menu(
                    menu_title=None,
                    options=["🎯 Generate", "📊 Dashboard", "👤 Profile", "📁 Scripts", 
                            "🔥 Viral Analysis", "📈 Trends", "⚙️ Settings"],
                    icons=["target", "graph-up", "person", "folder", "fire", "trending-up", "gear"],
                    menu_icon="cast",
                    default_index=0,
                    styles={
                        "container": {"padding": "0!important", "background-color": "#fafafa"},
                        "icon": {"color": "orange", "font-size": "18px"},
                        "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                        "nav-link-selected": {"background-color": "#02ab21"},
                    }
                )
            else:
                selected = st.selectbox(
                    "Navigate to:",
                    ["🎯 Generate", "📊 Dashboard", "👤 Profile", "📁 Scripts", 
                     "🔥 Viral Analysis", "📈 Trends", "⚙️ Settings"]
                )
            
            # Quick stats
            st.markdown("---")
            st.markdown("### 📊 Quick Stats")
            
            profile_status = "✅ Active" if st.session_state.user_profile else "❌ Not Set"
            st.markdown(f"**Profile:** {profile_status}")
            
            scripts_count = len(st.session_state.generated_scripts)
            st.markdown(f"**Generated:** {scripts_count} scripts")
            
            if st.session_state.current_script and st.session_state.viral_analysis:
                score = st.session_state.viral_analysis.get("viral_score", {}).get("percentage", 0)
                st.markdown(f"**Last Score:** {score:.1f}%")
            
            # Quick actions
            st.markdown("---")
            st.markdown("### ⚡ Quick Actions")
            
            if st.button("🚀 Quick Generate", use_container_width=True):
                st.session_state.quick_generate = True
            
            if st.button("📤 Upload Script", use_container_width=True):
                st.session_state.show_upload = True
            
            if st.button("🔄 Refresh Trends", use_container_width=True):
                with st.spinner("Fetching latest trends..."):
                    self._refresh_trending_data()
                st.success("Trends updated!")
        
        return selected
    
    def _show_generation_page(self):
        """Show the main script generation page."""
        st.markdown('<div class="main-header"><h1>🎯 Generate Viral Scripts</h1><p>Create engaging Instagram content optimized for maximum reach</p></div>', unsafe_allow_html=True)
        
        # Generation form
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📝 Script Details")
            
            topic = st.text_input(
                "What's your content about?",
                placeholder="e.g., Morning routine for productivity, Best skincare tips, Travel hacks",
                help="Describe your content topic clearly"
            )
            
            # Strategy selection
            strategy = st.selectbox(
                "Generation Strategy",
                ["viral_optimized", "story_driven", "educational", "entertainment", "trending"],
                help="Choose the content strategy that best fits your goals"
            )
            
            # Advanced options
            with st.expander("🔧 Advanced Options"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    use_trending = st.checkbox("Use Trending Data", value=True, help="Incorporate current trending insights")
                    optimization_iterations = st.slider("Optimization Rounds", 1, 3, 2, help="More rounds = better optimization")
                
                with col_b:
                    generate_variants = st.checkbox("Generate Variants", help="Create multiple versions for A/B testing")
                    variant_count = st.slider("Variant Count", 2, 5, 3) if generate_variants else 1
        
        with col2:
            st.markdown("### 🎯 Profile Status")
            
            if st.session_state.user_profile:
                profile = st.session_state.user_profile
                st.success("✅ Profile Active")
                st.write(f"**Name:** {profile.name}")
                st.write(f"**Niche:** {profile.niche}")
                st.write(f"**Style:** {profile.content_style}")
            else:
                st.warning("⚠️ No Profile Set")
                st.write("Set up your profile for personalized scripts")
                if st.button("Create Profile", use_container_width=True):
                    st.session_state.show_profile_setup = True
            
            st.markdown("### 📊 Recent Performance")
            if st.session_state.generated_scripts:
                recent_scores = [s.get('viral_score', {}).get('percentage', 0) 
                               for s in st.session_state.generated_scripts[-5:]]
                avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0
                
                st.metric("Average Score", f"{avg_score:.1f}%")
                
                # Mini chart
                if len(recent_scores) > 1:
                    fig = px.line(
                        x=range(1, len(recent_scores) + 1),
                        y=recent_scores,
                        title="Recent Performance"
                    )
                    fig.update_layout(height=200, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
        
        # Generate button
        if st.button("🚀 Generate Script", type="primary", disabled=not topic, use_container_width=True):
            self._handle_script_generation(topic, strategy, use_trending, optimization_iterations, 
                                         generate_variants, variant_count)
        
        # Quick generate handling
        if hasattr(st.session_state, 'quick_generate') and st.session_state.quick_generate:
            if topic:
                self._handle_script_generation(topic, strategy, use_trending, optimization_iterations, 
                                             generate_variants, variant_count)
            else:
                st.warning("Please enter a topic first!")
            st.session_state.quick_generate = False
        
        # Display current script
        if st.session_state.current_script:
            self._display_generated_script(st.session_state.current_script)
    
    def _show_dashboard_page(self):
        """Show the analytics dashboard."""
        st.markdown('<div class="main-header"><h1>📊 Performance Dashboard</h1><p>Analyze your content performance and viral potential</p></div>', unsafe_allow_html=True)
        
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
            avg_score = sum(s.get('viral_score', {}).get('percentage', 0) for s in scripts) / len(scripts)
            st.markdown(f'<div class="metric-card"><h3>{avg_score:.1f}%</h3><p>Avg Viral Score</p></div>', unsafe_allow_html=True)
        
        with col3:
            high_performers = len([s for s in scripts if s.get('viral_score', {}).get('percentage', 0) >= 80])
            st.markdown(f'<div class="metric-card"><h3>{high_performers}</h3><p>High Performers</p></div>', unsafe_allow_html=True)
        
        with col4:
            strategies_used = len(set(s.get('strategy', 'unknown') for s in scripts))
            st.markdown(f'<div class="metric-card"><h3>{strategies_used}</h3><p>Strategies Used</p></div>', unsafe_allow_html=True)
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Performance Trend")
            scores = [s.get('viral_score', {}).get('percentage', 0) for s in scripts]
            dates = [s.get('generation_metadata', {}).get('generated_at', datetime.now().isoformat())[:10] 
                    for s in scripts]
            
            fig = px.line(x=range(1, len(scores) + 1), y=scores, 
                         title="Viral Score Progression", markers=True)
            fig.update_layout(xaxis_title="Script Number", yaxis_title="Viral Score %")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Strategy Performance")
            strategy_scores = {}
            for script in scripts:
                strategy = script.get('strategy', 'unknown')
                score = script.get('viral_score', {}).get('percentage', 0)
                if strategy not in strategy_scores:
                    strategy_scores[strategy] = []
                strategy_scores[strategy].append(score)
            
            strategy_avg = {k: sum(v)/len(v) for k, v in strategy_scores.items()}
            
            fig = px.bar(x=list(strategy_avg.keys()), y=list(strategy_avg.values()),
                        title="Average Score by Strategy")
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed analysis
        st.markdown("### 📋 Script Analysis")
        
        # Create performance table
        script_data = []
        for i, script in enumerate(scripts):
            viral_score = script.get('viral_score', {})
            script_data.append({
                '#': i + 1,
                'Topic': script.get('topic', 'Unknown')[:30] + "...",
                'Strategy': script.get('strategy', 'Unknown'),
                'Viral Score': f"{viral_score.get('percentage', 0):.1f}%",
                'Grade': viral_score.get('grade', 'N/A'),
                'Generated': script.get('generation_metadata', {}).get('generated_at', '')[:10]
            })
        
        df = pd.DataFrame(script_data)
        
        if ENHANCED_UI_AVAILABLE:
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination(paginationPageSize=10)
            gb.configure_selection('single', use_checkbox=True)
            gridOptions = gb.build()
            
            grid_response = AgGrid(
                df,
                gridOptions=gridOptions,
                data_return_mode='AS_INPUT',
                update_mode='MODEL_CHANGED',
                fit_columns_on_grid_load=True,
                enable_enterprise_modules=False,
                height=400,
                reload_data=False
            )
            
            if grid_response['selected_rows']:
                selected_idx = grid_response['selected_rows'][0]['#'] - 1
                st.session_state.current_script = scripts[selected_idx]
                st.success(f"Selected script #{selected_idx + 1} for viewing")
        else:
            st.dataframe(df, use_container_width=True)
    
    def _show_profile_page(self):
        """Show user profile management page."""
        st.markdown('<div class="main-header"><h1>👤 User Profile</h1><p>Set up your personal context for better script generation</p></div>', unsafe_allow_html=True)
        
        # Profile status
        if st.session_state.user_profile:
            profile = st.session_state.user_profile
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📋 Current Profile")
                
                # Display profile info
                profile_info = f"""
                **Name:** {profile.name}
                **Niche:** {profile.niche}
                **Target Audience:** {profile.target_audience}
                **Content Style:** {profile.content_style}
                **Tone:** {profile.tone}
                
                **Key Topics:** {', '.join(profile.key_topics[:5])}
                
                **Bio:**
                {profile.bio}
                """
                
                st.markdown(profile_info)
                
                # Profile actions
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✏️ Edit Profile", use_container_width=True):
                        st.session_state.edit_profile = True
                
                with col_b:
                    if st.button("🗑️ Delete Profile", use_container_width=True):
                        st.session_state.user_profile = None
                        st.success("Profile deleted")
                        st.rerun()
            
            with col2:
                st.markdown("### 📊 Profile Impact")
                
                # Show how profile affects generation
                if st.session_state.generated_scripts:
                    with_profile = [s for s in st.session_state.generated_scripts 
                                  if s.get('user_context')]
                    
                    if with_profile:
                        avg_with_profile = sum(s.get('viral_score', {}).get('percentage', 0) 
                                             for s in with_profile) / len(with_profile)
                        st.metric("Avg Score with Profile", f"{avg_with_profile:.1f}%")
                    
                    st.markdown("**Benefits:**")
                    st.markdown("✅ Personalized content")
                    st.markdown("✅ Consistent brand voice")
                    st.markdown("✅ Better hashtag targeting")
                    st.markdown("✅ Audience-specific messaging")
        
        else:
            # Profile creation
            st.markdown("### 🆕 Create Your Profile")
            
            tab1, tab2, tab3 = st.tabs(["📝 Manual Entry", "📄 Upload Document", "🎯 Quick Setup"])
            
            with tab1:
                self._show_manual_profile_creation()
            
            with tab2:
                self._show_document_upload_profile()
            
            with tab3:
                self._show_quick_profile_setup()
        
        # Handle profile editing
        if hasattr(st.session_state, 'edit_profile') and st.session_state.edit_profile:
            self._show_profile_editor()
    
    def _show_scripts_page(self):
        """Show script management page."""
        st.markdown('<div class="main-header"><h1>📁 Script Management</h1><p>Manage your generated and uploaded scripts</p></div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["🤖 Generated Scripts", "📤 Upload Scripts", "📊 Collection Analysis"])
        
        with tab1:
            self._show_generated_scripts()
        
        with tab2:
            self._show_script_upload()
        
        with tab3:
            self._show_collection_analysis()
    
    def _show_viral_analysis_page(self):
        """Show viral analysis and optimization page."""
        st.markdown('<div class="main-header"><h1>🔥 Viral Analysis</h1><p>Deep dive into what makes content go viral</p></div>', unsafe_allow_html=True)
        
        # Analyze current script or paste new content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📝 Script to Analyze")
            
            analysis_source = st.radio(
                "Analysis Source:",
                ["Current Script", "Paste Content", "Upload File"]
            )
            
            script_content = ""
            
            if analysis_source == "Current Script":
                if st.session_state.current_script:
                    script_content = st.session_state.current_script.get('script', '')
                    st.text_area("Script Content", script_content, height=300, disabled=True)
                else:
                    st.warning("No current script available. Generate or select a script first.")
            
            elif analysis_source == "Paste Content":
                script_content = st.text_area("Paste your script here:", height=300)
            
            elif analysis_source == "Upload File":
                uploaded_file = st.file_uploader("Upload script file", type=['txt', 'md'])
                if uploaded_file:
                    script_content = str(uploaded_file.read(), "utf-8")
                    st.text_area("Uploaded Content", script_content, height=300, disabled=True)
            
            # Analysis topic
            topic = st.text_input("Script Topic (optional)", 
                                placeholder="e.g., fitness tips, cooking hacks")
        
        with col2:
            st.markdown("### ⚡ Quick Actions")
            
            if st.button("🔍 Analyze Script", type="primary", disabled=not script_content, 
                        use_container_width=True):
                self._perform_viral_analysis(script_content, topic)
            
            if st.button("🚀 Optimize Script", disabled=not script_content, 
                        use_container_width=True):
                self._optimize_script(script_content, topic)
            
            if st.button("📊 Compare Scripts", use_container_width=True):
                st.session_state.show_comparison = True
        
        # Display analysis results
        if st.session_state.viral_analysis:
            self._display_viral_analysis_results(st.session_state.viral_analysis)
    
    def _show_trends_page(self):
        """Show trending content and insights page."""
        st.markdown('<div class="main-header"><h1>📈 Trending Insights</h1><p>Stay ahead with the latest viral trends and patterns</p></div>', unsafe_allow_html=True)
        
        # Trend discovery options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            niche = st.selectbox(
                "Content Niche",
                ["fitness", "food", "lifestyle", "business", "tech", "fashion", "travel", "entertainment"],
                help="Select your content niche for targeted insights"
            )
        
        with col2:
            language = st.selectbox(
                "Content Language",
                ["english", "hindi", "telugu", "tamil", "spanish", "portuguese", "french"],
                help="Target language for trending content"
            )
        
        with col3:
            max_content = st.slider("Content to Analyze", 10, 100, 30, 
                                   help="Number of viral posts to analyze")
        
        # Fetch trends button
        if st.button("🔍 Discover Trends", type="primary", use_container_width=True):
            self._fetch_trending_insights(niche, language, max_content)
        
        # Display trending insights
        if st.session_state.trending_insights:
            self._display_trending_insights(st.session_state.trending_insights)
        
        # Trending hashtags section
        st.markdown("### 🏷️ Trending Hashtags")
        
        if st.button("🔄 Refresh Hashtags"):
            trending_hashtags = self.hashtag_optimizer.discover_trending_hashtags(niche, language, 50)
            st.session_state.trending_hashtags = trending_hashtags
        
        if hasattr(st.session_state, 'trending_hashtags'):
            # Display hashtags in a nice cloud layout
            hashtag_html = '<div class="hashtag-cloud">'
            for hashtag in st.session_state.trending_hashtags[:30]:
                hashtag_html += f'<span class="hashtag-tag">{hashtag}</span>'
            hashtag_html += '</div>'
            
            st.markdown(hashtag_html, unsafe_allow_html=True)
    
    def _show_settings_page(self):
        """Show application settings and configuration."""
        st.markdown('<div class="main-header"><h1>⚙️ Settings</h1><p>Configure your Script Writer Pro experience</p></div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["🔧 General", "🤖 AI Settings", "📊 Analytics", "💾 Data"])
        
        with tab1:
            st.markdown("### 🎨 Interface Settings")
            
            # Theme and display options
            col1, col2 = st.columns(2)
            
            with col1:
                auto_scroll = st.checkbox("Auto-scroll to results", value=True)
                show_tips = st.checkbox("Show helpful tips", value=True)
                compact_view = st.checkbox("Compact view mode", value=False)
            
            with col2:
                animation_speed = st.selectbox("Animation Speed", ["Slow", "Normal", "Fast"], index=1)
                results_per_page = st.slider("Results per page", 5, 50, 10)
        
        with tab2:
            st.markdown("### 🧠 AI Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                default_strategy = st.selectbox(
                    "Default Generation Strategy",
                    ["viral_optimized", "story_driven", "educational", "entertainment", "trending"],
                    help="Default strategy for script generation"
                )
                
                optimization_level = st.selectbox(
                    "Optimization Level",
                    ["Basic (1 round)", "Standard (2 rounds)", "Maximum (3 rounds)"],
                    index=1
                )
            
            with col2:
                use_trending_default = st.checkbox("Use trending data by default", value=True)
                auto_optimize = st.checkbox("Auto-optimize generated scripts", value=True)
                smart_hashtags = st.checkbox("Smart hashtag suggestions", value=True)
        
        with tab3:
            st.markdown("### 📈 Analytics Settings")
            
            track_performance = st.checkbox("Track script performance", value=True)
            export_analytics = st.checkbox("Enable analytics export", value=True)
            
            if st.button("📊 Export Analytics Data"):
                self._export_analytics_data()
        
        with tab4:
            st.markdown("### 💾 Data Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Backup & Export**")
                if st.button("💾 Export All Scripts", use_container_width=True):
                    self._export_all_scripts()
                
                if st.button("📤 Export Profile", use_container_width=True):
                    self._export_profile()
            
            with col2:
                st.markdown("**Reset & Clear**")
                if st.button("🗑️ Clear Generated Scripts", use_container_width=True):
                    st.session_state.generated_scripts = []
                    st.success("Generated scripts cleared!")
                
                if st.button("⚠️ Reset All Data", use_container_width=True):
                    if st.checkbox("I understand this will delete all data"):
                        self._reset_all_data()
    
    def _handle_script_generation(self, topic: str, strategy: str, use_trending: bool,
                                optimization_iterations: int, generate_variants: bool, 
                                variant_count: int):
        """Handle the script generation process."""
        with st.spinner("🚀 Generating your viral script..."):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Update progress
                status_text.text("🤖 Initializing AI generator...")
                progress_bar.progress(10)
                
                if generate_variants:
                    status_text.text(f"🎭 Generating {variant_count} variants...")
                    progress_bar.progress(30)
                    
                    variants = self.generator.generate_multiple_variants(
                        topic, variant_count, [strategy]
                    )
                    
                    if variants:
                        # Use best variant as current
                        st.session_state.current_script = variants[0]
                        st.session_state.generated_scripts.extend(variants)
                        
                        progress_bar.progress(80)
                        status_text.text("✨ Analyzing viral potential...")
                        
                        # Analyze the best variant
                        analysis = analyze_script_performance_potential(
                            variants[0]['script'], topic
                        )
                        st.session_state.viral_analysis = analysis
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Generation complete!")
                        
                        st.success(f"🎉 Generated {len(variants)} variants! Best score: {variants[0]['viral_score'].percentage:.1f}%")
                    else:
                        st.error("❌ Failed to generate variants. Please try again.")
                
                else:
                    status_text.text("🎯 Generating optimized script...")
                    progress_bar.progress(50)
                    
                    result = self.generator.generate_viral_script(
                        topic, strategy, use_trending, optimization_iterations
                    )
                    
                    if result.get("success"):
                        st.session_state.current_script = result
                        st.session_state.generated_scripts.append(result)
                        
                        progress_bar.progress(80)
                        status_text.text("✨ Analyzing viral potential...")
                        
                        # Analyze the script
                        analysis = analyze_script_performance_potential(
                            result['script'], topic
                        )
                        st.session_state.viral_analysis = analysis
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Generation complete!")
                        
                        score = result['viral_score'].percentage
                        st.success(f"🎉 Script generated! Viral score: {score:.1f}%")
                    else:
                        st.error("❌ Generation failed. Please try again.")
                
                # Clean up progress indicators
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
            except Exception as e:
                st.error(f"❌ Generation error: {str(e)}")
                logger.error(f"Script generation error: {e}")
    
    def _display_generated_script(self, script_data: Dict[str, Any]):
        """Display a generated script with enhanced formatting."""
        st.markdown("---")
        st.markdown("## 📄 Generated Script")
        
        # Script metadata
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Viral Score", f"{script_data.get('viral_score', {}).get('percentage', 0):.1f}%")
        
        with col2:
            st.metric("Grade", script_data.get('viral_score', {}).get('grade', 'N/A'))
        
        with col3:
            strategy = script_data.get('strategy', 'Unknown')
            st.metric("Strategy", strategy.replace('_', ' ').title())
        
        with col4:
            hashtag_count = len(script_data.get('hashtag_strategy', {}).get('hashtags', []))
            st.metric("Hashtags", hashtag_count)
        
        # Script content
        script_content = script_data.get('script', '')
        
        # Format and display script
        formatted_script = self._format_script_display(script_content)
        st.markdown(f'<div class="script-preview">{formatted_script}</div>', unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("📋 Copy Script", use_container_width=True):
                st.code(script_content, language="text")
                st.info("Script ready to copy!")
        
        with col2:
            if st.button("🔍 Analyze", use_container_width=True):
                self._perform_viral_analysis(script_content, script_data.get('topic', ''))
        
        with col3:
            if st.button("✨ Optimize", use_container_width=True):
                self._optimize_script(script_content, script_data.get('topic', ''))
        
        with col4:
            if st.button("💾 Save", use_container_width=True):
                self._save_script_to_file(script_data)
        
        with col5:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.regenerate_current = True
                st.rerun()
        
        # Hashtag strategy display
        if script_data.get('hashtag_strategy'):
            self._display_hashtag_strategy(script_data['hashtag_strategy'])
    
    def _format_script_display(self, script: str) -> str:
        """Format script for better display."""
        # Add HTML formatting for better visual presentation
        formatted = script.replace('\n\n', '<br><br>')
        
        # Format section headers
        sections = ['HOOK:', 'BODY:', 'CTA:', 'CAPTION:', 'VISUAL DIRECTIONS:', 'HASHTAGS:']
        for section in sections:
            formatted = formatted.replace(section, f'<strong style="color: #1976d2;">{section}</strong>')
        
        return formatted
    
    def _display_hashtag_strategy(self, hashtag_strategy: Dict[str, Any]):
        """Display hashtag strategy with analysis."""
        st.markdown("### 🏷️ Hashtag Strategy")
        
        hashtags = hashtag_strategy.get('hashtags', [])
        strategy_report = hashtag_strategy.get('strategy_report', {})
        
        # Display hashtags in cloud format
        if hashtags:
            hashtag_html = '<div class="hashtag-cloud">'
            for hashtag in hashtags:
                hashtag_html += f'<span class="hashtag-tag">{hashtag}</span>'
            hashtag_html += '</div>'
            st.markdown(hashtag_html, unsafe_allow_html=True)
        
        # Strategy insights
        if strategy_report:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Performance Metrics:**")
                avg_scores = strategy_report.get('average_scores', {})
                for metric, score in avg_scores.items():
                    st.write(f"• {metric.replace('_', ' ').title()}: {score}")
            
            with col2:
                st.markdown("**Recommendations:**")
                recommendations = strategy_report.get('strategy_recommendations', [])
                for rec in recommendations[:3]:
                    st.write(f"• {rec}")
    
    def _perform_viral_analysis(self, script_content: str, topic: str):
        """Perform viral analysis on script content."""
        with st.spinner("🔍 Analyzing viral potential..."):
            try:
                # Get comprehensive analysis
                analysis = analyze_script_performance_potential(script_content, topic)
                st.session_state.viral_analysis = analysis
                
                st.success("✅ Analysis complete!")
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                logger.error(f"Viral analysis error: {e}")
    
    def _display_viral_analysis_results(self, analysis: Dict[str, Any]):
        """Display comprehensive viral analysis results."""
        st.markdown("---")
        st.markdown("## 🔥 Viral Analysis Results")
        
        viral_score = analysis.get('viral_score', {})
        
        # Overall score with visual styling
        score_percentage = viral_score.get('percentage', 0)
        grade = viral_score.get('grade', 'F')
        
        score_class = f"score-{grade[0].lower()}"
        
        st.markdown(f"""
        <div class="viral-score {score_class}">
            🎯 Viral Score: {score_percentage:.1f}% (Grade: {grade})
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Score Breakdown")
            
            breakdown = viral_score.get('breakdown', {})
            for component, score in breakdown.items():
                component_name = component.replace('_', ' ').title()
                max_score = self.viral_scorer.scoring_weights.get(component, 20)
                percentage = (score / max_score) * 100
                
                st.metric(component_name, f"{score:.1f}/{max_score}", f"{percentage:.0f}%")
        
        with col2:
            st.markdown("### 💡 Recommendations")
            
            recommendations = viral_score.get('recommendations', [])
            for i, rec in enumerate(recommendations[:5], 1):
                st.write(f"{i}. {rec}")
        
        # Performance factors
        st.markdown("### 📈 Performance Analysis")
        
        performance_factors = analysis.get('performance_factors', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Viral Potential", f"{performance_factors.get('viral_potential', 0):.1f}%")
        
        with col2:
            st.metric("Hashtag Score", f"{performance_factors.get('hashtag_optimization', 0):.1f}%")
        
        with col3:
            st.metric("Content Quality", f"{performance_factors.get('content_quality', 0):.1f}%")
        
        with col4:
            st.metric("Engagement Likelihood", f"{performance_factors.get('engagement_likelihood', 0):.1f}%")
        
        # Viral elements found
        viral_elements = viral_score.get('viral_elements', [])
        if viral_elements:
            st.markdown("### ✅ Viral Elements Found")
            elements_html = '<div class="hashtag-cloud">'
            for element in viral_elements:
                element_name = element.replace('_', ' ').title()
                elements_html += f'<span class="hashtag-tag">{element_name}</span>'
            elements_html += '</div>'
            st.markdown(elements_html, unsafe_allow_html=True)
        
        # Missing elements
        missing_elements = viral_score.get('missing_elements', [])
        if missing_elements:
            st.markdown("### ❌ Missing Viral Elements")
            for element in missing_elements:
                st.write(f"• {element}")
    
    def _optimize_script(self, script_content: str, topic: str):
        """Optimize script for better viral potential."""
        with st.spinner("✨ Optimizing script for viral potential..."):
            try:
                # Get optimization suggestions
                optimization = self.viral_scorer.optimize_for_virality(
                    script_content, topic
                )
                
                st.success("✅ Optimization analysis complete!")
                
                # Display optimization plan
                st.markdown("### 🚀 Optimization Plan")
                
                optimization_plan = optimization.get('optimization_plan', [])
                for i, plan in enumerate(optimization_plan, 1):
                    with st.expander(f"{i}. {plan.get('issue', 'Improvement')}"):
                        st.write(f"**Problem:** {plan.get('issue', '')}")
                        st.write(f"**Solution:** {plan.get('solution', '')}")
                        st.write(f"**Impact:** {plan.get('impact', '')}")
                        
                        examples = plan.get('examples', [])
                        if examples:
                            st.write("**Examples:**")
                            for example in examples:
                                st.write(f"• {example}")
                
                # Show potential score improvement
                current_score = optimization.get('current_score', {}).get('total_score', 0)
                potential_score = optimization.get('viral_score_potential', 0)
                improvement = potential_score - current_score
                
                if improvement > 0:
                    st.success(f"🎯 Potential improvement: +{improvement:.1f} points ({improvement/100*100:.1f}%)")
                
            except Exception as e:
                st.error(f"❌ Optimization failed: {str(e)}")
                logger.error(f"Script optimization error: {e}")
    
    def _show_manual_profile_creation(self):
        """Show manual profile creation form."""
        with st.form("create_profile"):
            st.markdown("#### 📝 Tell us about yourself")
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Your Name*", placeholder="e.g., Sarah Johnson")
                niche = st.selectbox("Content Niche*", 
                                   ["fitness", "food", "lifestyle", "business", "tech", 
                                    "fashion", "travel", "entertainment", "education"])
                target_audience = st.text_input("Target Audience*", 
                                              placeholder="e.g., Young professionals aged 25-35")
            
            with col2:
                content_style = st.selectbox("Content Style", 
                                           ["informative", "entertaining", "inspirational", 
                                            "educational", "humorous", "personal"])
                tone = st.selectbox("Tone", 
                                  ["friendly", "professional", "casual", "authoritative", 
                                   "playful", "serious"])
                key_topics = st.text_input("Key Topics (comma-separated)", 
                                         placeholder="e.g., productivity, motivation, success")
            
            bio = st.text_area("Bio/About You*", height=100,
                             placeholder="Tell us about your background, expertise, and what makes you unique...")
            
            personal_story = st.text_area("Your Story (optional)", height=100,
                                        placeholder="Share your journey, challenges overcome, or key experiences...")
            
            preferred_hashtags = st.text_input("Preferred Hashtags (optional)", 
                                             placeholder="#motivation #success #lifestyle")
            
            content_goals = st.text_area("Content Goals", height=60,
                                       placeholder="What do you want to achieve with your content?")
            
            if st.form_submit_button("✅ Create Profile", type="primary"):
                if name and niche and target_audience and bio:
                    # Create profile
                    profile_text = f"""
                    Name: {name}
                    Niche: {niche}
                    Target Audience: {target_audience}
                    Content Style: {content_style}
                    Tone: {tone}
                    Key Topics: {key_topics}
                    Bio: {bio}
                    Personal Story: {personal_story}
                    Content Goals: {content_goals}
                    """
                    
                    profile = self.profile_manager.create_profile_from_text(profile_text, name)
                    profile.preferred_hashtags = [tag.strip() for tag in preferred_hashtags.split(',') if tag.strip()]
                    
                    # Save and activate profile
                    self.profile_manager.save_profile(profile)
                    self.profile_manager.set_active_profile(profile.user_id)
                    st.session_state.user_profile = profile
                    
                    st.success("✅ Profile created successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please fill in all required fields marked with *")
    
    def _show_document_upload_profile(self):
        """Show document upload profile creation."""
        st.markdown("#### 📄 Upload Your Bio/About Document")
        
        uploaded_file = st.file_uploader(
            "Choose a file", 
            type=['pdf', 'docx', 'txt'],
            help="Upload a document containing information about yourself, your expertise, background, etc."
        )
        
        if uploaded_file:
            user_name = st.text_input("Your Name", placeholder="e.g., Sarah Johnson")
            
            if st.button("🚀 Create Profile from Document", type="primary"):
                if user_name:
                    try:
                        # Save uploaded file temporarily
                        temp_path = f"temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Create profile from document
                        profile = self.profile_manager.upload_profile_document(temp_path, user_name)
                        
                        # Save and activate profile
                        self.profile_manager.save_profile(profile)
                        self.profile_manager.set_active_profile(profile.user_id)
                        st.session_state.user_profile = profile
                        
                        # Clean up temp file
                        Path(temp_path).unlink(missing_ok=True)
                        
                        st.success("✅ Profile created from document!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error creating profile: {str(e)}")
                        Path(temp_path).unlink(missing_ok=True)
                else:
                    st.error("❌ Please enter your name")
    
    def _show_quick_profile_setup(self):
        """Show quick profile setup with minimal fields."""
        st.markdown("#### ⚡ Quick 30-Second Setup")
        
        with st.form("quick_profile"):
            name = st.text_input("Your Name", placeholder="e.g., Sarah")
            
            col1, col2 = st.columns(2)
            with col1:
                niche = st.selectbox("What do you create content about?", 
                                   ["fitness", "food", "lifestyle", "business", "tech", 
                                    "fashion", "travel", "entertainment"])
            
            with col2:
                style = st.selectbox("Your content style?", 
                                   ["fun & casual", "educational", "inspirational", "entertaining"])
            
            short_bio = st.text_area("One sentence about you:", height=60,
                                   placeholder="I'm a fitness enthusiast who loves sharing practical workout tips...")
            
            if st.form_submit_button("⚡ Create Quick Profile", type="primary"):
                if name and short_bio:
                    profile_text = f"""
                    Name: {name}
                    Niche: {niche}
                    Content Style: {style}
                    Bio: {short_bio}
                    Target Audience: People interested in {niche}
                    """
                    
                    profile = self.profile_manager.create_profile_from_text(profile_text, name)
                    
                    # Save and activate profile
                    self.profile_manager.save_profile(profile)
                    self.profile_manager.set_active_profile(profile.user_id)
                    st.session_state.user_profile = profile
                    
                    st.success("✅ Quick profile created! You can edit it anytime.")
                    st.rerun()
                else:
                    st.error("❌ Please fill in your name and bio")
    
    def _show_generated_scripts(self):
        """Show generated scripts management."""
        if not st.session_state.generated_scripts:
            st.info("No generated scripts yet. Create your first script in the Generate tab!")
            return
        
        scripts = st.session_state.generated_scripts
        
        # Scripts overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Scripts", len(scripts))
        
        with col2:
            avg_score = sum(s.get('viral_score', {}).get('percentage', 0) for s in scripts) / len(scripts)
            st.metric("Average Score", f"{avg_score:.1f}%")
        
        with col3:
            high_performers = len([s for s in scripts if s.get('viral_score', {}).get('percentage', 0) >= 80])
            st.metric("High Performers", high_performers)
        
        # Scripts list
        st.markdown("### 📋 Your Generated Scripts")
        
        for i, script in enumerate(reversed(scripts)):  # Show newest first
            with st.expander(f"Script #{len(scripts)-i}: {script.get('topic', 'Unknown Topic')[:50]}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Script preview
                    script_preview = script.get('script', '')[:300] + "..."
                    st.text_area("Preview", script_preview, height=150, key=f"preview_{i}", disabled=True)
                
                with col2:
                    # Script metadata
                    viral_score = script.get('viral_score', {})
                    st.metric("Score", f"{viral_score.get('percentage', 0):.1f}%")
                    st.metric("Grade", viral_score.get('grade', 'N/A'))
                    
                    strategy = script.get('strategy', 'Unknown')
                    st.write(f"**Strategy:** {strategy.replace('_', ' ').title()}")
                    
                    generated_at = script.get('generation_metadata', {}).get('generated_at', '')
                    if generated_at:
                        st.write(f"**Generated:** {generated_at[:10]}")
                    
                    # Actions
                    if st.button("👁️ View", key=f"view_{i}"):
                        st.session_state.current_script = script
                        st.success("Script loaded for viewing!")
                    
                    if st.button("🗑️ Delete", key=f"delete_{i}"):
                        scripts.remove(script)
                        if st.session_state.current_script == script:
                            st.session_state.current_script = None
                        st.success("Script deleted!")
                        st.rerun()
    
    def _show_script_upload(self):
        """Show script upload functionality."""
        st.markdown("### 📤 Upload Your Scripts")
        st.write("Upload your existing high-performing scripts to improve AI generation quality.")
        
        # Upload options
        upload_method = st.radio("Upload Method:", ["📄 Upload File", "📝 Paste Content"])
        
        if upload_method == "📄 Upload File":
            uploaded_file = st.file_uploader("Choose script file", type=['txt', 'md'])
            
            if uploaded_file:
                script_content = str(uploaded_file.read(), "utf-8")
                st.text_area("File Content Preview", script_content, height=200, disabled=True)
                
                # Metadata
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input("Script Title (optional)", 
                                        value=uploaded_file.name.replace('.txt', '').replace('.md', ''))
                    topic = st.text_input("Topic/Theme", placeholder="e.g., morning routine, fitness tips")
                
                with col2:
                    user_notes = st.text_area("Your Notes (optional)", height=100,
                                            placeholder="Notes about this script's performance, context, etc.")
                
                if st.button("📤 Upload Script", type="primary"):
                    self._upload_script(script_content, title, topic, user_notes)
        
        else:  # Paste Content
            script_content = st.text_area("Paste your script content here:", height=300)
            
            if script_content:
                # Metadata
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input("Script Title", placeholder="e.g., My Best Performing Script")
                    topic = st.text_input("Topic/Theme", placeholder="e.g., productivity tips")
                
                with col2:
                    user_notes = st.text_area("Your Notes (optional)", height=100,
                                            placeholder="Notes about this script's performance, context, etc.")
                
                if st.button("📤 Upload Script", type="primary"):
                    self._upload_script(script_content, title, topic, user_notes)
        
        # Show uploaded scripts
        uploaded_scripts = self.script_manager.get_uploaded_scripts()
        
        if uploaded_scripts:
            st.markdown("### 📁 Your Uploaded Scripts")
            
            for script in uploaded_scripts[:5]:  # Show recent 5
                with st.expander(f"{script.title} (Score: {script.viral_score:.1f})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Topic:** {script.topic}")
                        st.write(f"**Upload Date:** {script.upload_date[:10]}")
                        if script.user_notes:
                            st.write(f"**Notes:** {script.user_notes}")
                    
                    with col2:
                        st.metric("Viral Score", f"{script.viral_score:.1f}")
                        st.write(f"**Hashtags:** {len(script.hashtags)}")
                        
                        if st.button("🗑️ Delete", key=f"del_upload_{script.script_id}"):
                            self.script_manager.delete_script(script.script_id)
                            st.success("Script deleted!")
                            st.rerun()
    
    def _upload_script(self, content: str, title: str, topic: str, notes: str):
        """Upload a script to the system."""
        try:
            uploaded_script = self.script_manager.upload_script_content(
                content, title, topic, notes
            )
            
            st.success(f"✅ Script '{uploaded_script.title}' uploaded successfully!")
            st.info(f"Viral Score: {uploaded_script.viral_score:.1f}")
            
            # Add to session state for immediate display
            if 'uploaded_scripts' not in st.session_state:
                st.session_state.uploaded_scripts = []
            st.session_state.uploaded_scripts.append(uploaded_script)
            
        except Exception as e:
            st.error(f"❌ Upload failed: {str(e)}")
    
    def _show_collection_analysis(self):
        """Show analysis of script collection."""
        # Get analysis of uploaded scripts
        uploaded_analysis = self.script_manager.analyze_script_collection()
        
        # Get analysis of generated scripts
        generated_scripts = st.session_state.generated_scripts
        
        if not uploaded_analysis.get('summary') and not generated_scripts:
            st.info("Upload or generate scripts to see collection analysis!")
            return
        
        # Combined analysis
        st.markdown("### 📊 Collection Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            uploaded_count = uploaded_analysis.get('summary', {}).get('total_scripts', 0)
            st.metric("Uploaded Scripts", uploaded_count)
        
        with col2:
            generated_count = len(generated_scripts)
            st.metric("Generated Scripts", generated_count)
        
        with col3:
            total_scripts = uploaded_count + generated_count
            st.metric("Total Scripts", total_scripts)
        
        with col4:
            if generated_scripts:
                avg_gen_score = sum(s.get('viral_score', {}).get('percentage', 0) for s in generated_scripts) / len(generated_scripts)
            else:
                avg_gen_score = 0
            
            uploaded_avg = uploaded_analysis.get('summary', {}).get('average_viral_score', 0)
            
            if total_scripts > 0:
                overall_avg = (avg_gen_score * generated_count + uploaded_avg * uploaded_count) / total_scripts
            else:
                overall_avg = 0
            
            st.metric("Overall Avg Score", f"{overall_avg:.1f}%")
        
        # Performance insights
        if uploaded_analysis.get('best_practices'):
            st.markdown("### 💡 Best Practices Learned")
            for practice in uploaded_analysis['best_practices']:
                st.write(f"• {practice}")
        
        # Topic analysis
        if uploaded_analysis.get('topic_distribution'):
            st.markdown("### 📈 Topic Performance")
            
            topic_dist = uploaded_analysis['topic_distribution']
            topic_scores = uploaded_analysis.get('performance_insights', {}).get('average_score_by_topic', {})
            
            # Create topic performance chart
            topics = list(topic_dist.keys())
            counts = list(topic_dist.values())
            scores = [topic_scores.get(topic, 0) for topic in topics]
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(x=topics, y=counts, title="Scripts by Topic")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(x=topics, y=scores, title="Average Score by Topic")
                st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        recommendations = uploaded_analysis.get('recommendations', [])
        if recommendations:
            st.markdown("### 🎯 Recommendations")
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
    
    def _fetch_trending_insights(self, niche: str, language: str, max_content: int):
        """Fetch trending insights for the specified parameters."""
        with st.spinner(f"🔍 Discovering trends in {niche} ({language})..."):
            try:
                # Get viral content and analysis
                viral_content, analysis = self.scraper.get_niche_specific_content(
                    niche, language, max_content
                )
                
                st.session_state.trending_insights = {
                    "niche": niche,
                    "language": language,
                    "viral_content_count": len(viral_content),
                    "analysis": analysis,
                    "fetched_at": datetime.now().isoformat()
                }
                
                st.success(f"✅ Found {len(viral_content)} viral posts and analyzed trends!")
                
            except Exception as e:
                st.error(f"❌ Failed to fetch trends: {str(e)}")
                logger.error(f"Trending insights error: {e}")
    
    def _display_trending_insights(self, insights: Dict[str, Any]):
        """Display trending insights and analysis."""
        analysis = insights.get("analysis", {})
        
        # Overview metrics
        st.markdown("### 📊 Trending Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Viral Posts Analyzed", insights.get("viral_content_count", 0))
        
        with col2:
            st.metric("Top Hashtags Found", len(analysis.get("top_hashtags", [])))
        
        with col3:
            st.metric("Common Themes", len(analysis.get("common_themes", [])))
        
        with col4:
            st.metric("Viral Elements", len(analysis.get("viral_elements", [])))
        
        # Top hashtags
        top_hashtags = analysis.get("top_hashtags", [])[:20]
        if top_hashtags:
            st.markdown("### 🏷️ Top Performing Hashtags")
            hashtag_html = '<div class="hashtag-cloud">'
            for hashtag in top_hashtags:
                hashtag_html += f'<span class="hashtag-tag">{hashtag}</span>'
            hashtag_html += '</div>'
            st.markdown(hashtag_html, unsafe_allow_html=True)
        
        # Common themes and viral elements
        col1, col2 = st.columns(2)
        
        with col1:
            common_themes = analysis.get("common_themes", [])[:10]
            if common_themes:
                st.markdown("### 🎯 Trending Themes")
                for theme in common_themes:
                    st.write(f"• {theme}")
        
        with col2:
            viral_elements = analysis.get("viral_elements", [])[:10]
            if viral_elements:
                st.markdown("### 🔥 Viral Elements")
                for element in viral_elements:
                    st.write(f"• {element}")
        
        # Content recommendations
        recommendations = analysis.get("content_recommendations", [])
        if recommendations:
            st.markdown("### 💡 Content Recommendations")
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
        
        # Optimal posting times
        optimal_times = analysis.get("optimal_posting_times", [])
        if optimal_times:
            st.markdown("### ⏰ Optimal Posting Times")
            times_html = '<div class="hashtag-cloud">'
            for time_slot in optimal_times:
                times_html += f'<span class="hashtag-tag">{time_slot}</span>'
            times_html += '</div>'
            st.markdown(times_html, unsafe_allow_html=True)
    
    def _refresh_trending_data(self):
        """Refresh trending data for quick access."""
        try:
            # Get user's niche if available
            niche = "lifestyle"
            if st.session_state.user_profile:
                niche = st.session_state.user_profile.niche
            
            # Fetch trending hashtags
            trending_hashtags = self.hashtag_optimizer.discover_trending_hashtags(niche, "english", 30)
            st.session_state.trending_hashtags = trending_hashtags
            
            # Update trending insights if none exist
            if not st.session_state.trending_insights:
                self._fetch_trending_insights(niche, "english", 20)
                
        except Exception as e:
            logger.warning(f"Could not refresh trending data: {e}")
    
    def _save_script_to_file(self, script_data: Dict[str, Any]):
        """Save script to a file."""
        try:
            # Create filename
            topic = script_data.get("topic", "script")
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_topic.replace(' ', '_')}_{timestamp}.txt"
            
            # Get script content
            script_content = script_data.get("script", "")
            
            # Add metadata as comments
            metadata = f"""# Generated Script - {topic}
# Strategy: {script_data.get('strategy', 'Unknown')}
# Viral Score: {script_data.get('viral_score', {}).get('percentage', 0):.1f}%
# Generated: {script_data.get('generation_metadata', {}).get('generated_at', '')}

{script_content}
"""
            
            # Save to scripts directory
            scripts_dir = Path(SCRIPTS_DIR)
            scripts_dir.mkdir(exist_ok=True)
            filepath = scripts_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(metadata)
            
            st.success(f"💾 Script saved as: {filename}")
            
        except Exception as e:
            st.error(f"❌ Failed to save script: {str(e)}")
    
    def _export_analytics_data(self):
        """Export analytics data."""
        try:
            # Compile analytics data
            analytics_data = {
                "generated_scripts": len(st.session_state.generated_scripts),
                "uploaded_scripts": len(self.script_manager.get_uploaded_scripts()),
                "average_viral_score": sum(s.get('viral_score', {}).get('percentage', 0) 
                                         for s in st.session_state.generated_scripts) / max(len(st.session_state.generated_scripts), 1),
                "user_profile": st.session_state.user_profile.__dict__ if st.session_state.user_profile else None,
                "export_date": datetime.now().isoformat()
            }
            
            # Convert to JSON
            json_data = json.dumps(analytics_data, indent=2, default=str)
            
            st.download_button(
                label="📊 Download Analytics",
                data=json_data,
                file_name=f"script_writer_analytics_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")
    
    def _export_all_scripts(self):
        """Export all scripts."""
        try:
            all_scripts = {
                "generated_scripts": st.session_state.generated_scripts,
                "uploaded_scripts": [script.__dict__ for script in self.script_manager.get_uploaded_scripts()],
                "export_date": datetime.now().isoformat()
            }
            
            json_data = json.dumps(all_scripts, indent=2, default=str)
            
            st.download_button(
                label="💾 Download All Scripts",
                data=json_data,
                file_name=f"all_scripts_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")
    
    def _export_profile(self):
        """Export user profile."""
        try:
            if st.session_state.user_profile:
                profile_data = st.session_state.user_profile.__dict__
                json_data = json.dumps(profile_data, indent=2, default=str)
                
                st.download_button(
                    label="👤 Download Profile",
                    data=json_data,
                    file_name=f"user_profile_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            else:
                st.warning("No profile to export")
                
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")
    
    def _reset_all_data(self):
        """Reset all application data."""
        st.session_state.clear()
        self._initialize_session_state()
        st.success("✅ All data has been reset!")
        st.rerun()


def main():
    """Main application entry point."""
    app = EnhancedInstagramScriptWriter()
    app.run()


if __name__ == "__main__":
    main()