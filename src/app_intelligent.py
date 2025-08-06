"""
Intelligent Instagram Script Writer - The REAL Deal
Focus on backend functionality that truly understands users and generates personalized viral content
"""

import streamlit as st
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import our intelligent engine
import sys
sys.path.append('.')
from src.intelligent_script_engine import IntelligentScriptEngine, ContentRequest, UserPersona

def init_session_state():
    """Initialize session state"""
    defaults = {
        'engine': IntelligentScriptEngine(),
        'current_persona': None,
        'personas': [],
        'generated_scripts': [],
        'current_script': None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def load_existing_personas():
    """Load existing personas"""
    try:
        personas = st.session_state.engine.list_personas()
        st.session_state.personas = personas
        
        # Auto-load first persona if available
        if personas and not st.session_state.current_persona:
            first_persona = st.session_state.engine.load_persona(personas[0]['user_id'])
            if first_persona:
                st.session_state.current_persona = first_persona
                
    except Exception as e:
        st.error(f"Error loading personas: {e}")

def main():
    """Main application"""
    st.set_page_config(
        page_title="🧠 Intelligent Script Writer",
        page_icon="🧠",
        layout="wide"
    )
    
    # Initialize
    init_session_state()
    load_existing_personas()
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .persona-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .script-output {
        background: #ffffff;
        border: 2px solid #667eea;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        line-height: 1.8;
        color: #2c3e50;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
        font-size: 16px;
    }
    
    .metric-good { color: #28a745; font-weight: bold; }
    .metric-average { color: #ffc107; font-weight: bold; }
    .metric-poor { color: #dc3545; font-weight: bold; }
    
    .success-banner {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Ensure good text contrast */
    .script-output strong {
        color: #667eea !important;
    }
    
    .script-output p {
        color: #2c3e50 !important;
        margin: 10px 0 !important;
    }
    
    /* Better hashtag styling */
    .script-output div:contains("HASHTAGS") + * {
        color: #1976d2 !important;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 Intelligent Instagram Script Writer</h1>
        <p>The AI that truly understands YOU and creates personalized viral content</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Your Profile")
        
        if st.session_state.current_persona:
            persona = st.session_state.current_persona
            st.markdown(f"""
            <div class="persona-card">
                <h3>👤 {persona.name}</h3>
                <p><strong>Expertise:</strong> {', '.join(persona.expertise[:2])}</p>
                <p><strong>Voice:</strong> {persona.unique_voice}</p>
                <p><strong>Audience:</strong> {persona.target_audience[:50]}...</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Switch Profile"):
                st.session_state.show_profile_selector = True
            
            if st.button("✏️ Edit Profile"):
                st.session_state.edit_current_persona = True
        
        else:
            st.warning("⚠️ No profile set")
            st.info("Create your profile to get personalized scripts")
        
        st.markdown("---")
        
        # Quick stats
        st.header("📊 Stats")
        st.metric("Generated Scripts", len(st.session_state.generated_scripts))
        if st.session_state.generated_scripts:
            avg_score = sum(s.get('best_attempt_score', 0) for s in st.session_state.generated_scripts) / len(st.session_state.generated_scripts)
            st.metric("Avg Quality Score", f"{avg_score:.1f}/100")
        
        st.markdown("---")
        
        # Available personas
        if st.session_state.personas:
            st.header("👥 Available Profiles")
            for persona_info in st.session_state.personas:
                if st.button(f"📁 {persona_info['name']}", key=f"load_{persona_info['user_id']}"):
                    loaded_persona = st.session_state.engine.load_persona(persona_info['user_id'])
                    if loaded_persona:
                        st.session_state.current_persona = loaded_persona
                        st.success(f"Loaded {loaded_persona.name}'s profile!")
                        st.rerun()
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["🚀 Generate Script", "👤 Manage Profile", "📊 Script History"])
    
    with tab1:
        show_script_generation()
    
    with tab2:
        show_profile_management()
    
    with tab3:
        show_script_history()

def show_script_generation():
    """Script generation interface"""
    
    if not st.session_state.current_persona:
        st.warning("⚠️ Please create or select a profile first to generate personalized scripts")
        return
    
    persona = st.session_state.current_persona
    
    st.header(f"🚀 Generate Script for {persona.name}")
    
    # Generation form
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 What do you want to create?")
        
        topic = st.text_area(
            "Topic/Idea",
            height=100,
            placeholder="e.g., How to grow your Instagram following in 30 days\n\nBe specific about what you want to teach or share. The more detail, the better the script!",
            help="Describe exactly what you want your reel to be about"
        )
        
        context = st.text_area(
            "Additional Context (Optional)",
            height=80,
            placeholder="e.g., This is for beginners who have never used Instagram for business. Focus on simple, actionable steps.",
            help="Any additional context about your audience or specific requirements"
        )
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            duration = st.selectbox(
                "Video Length",
                [15, 30, 45, 60, 90],
                index=1,
                help="Target duration for your reel"
            )
        
        with col_b:
            content_type = st.selectbox(
                "Content Type",
                ["educational", "inspirational", "entertaining", "story-driven"],
                help="What kind of content do you want to create?"
            )
        
        with col_c:
            urgency = st.selectbox(
                "Priority",
                ["normal", "trending", "urgent"],
                help="How quickly do you need this content?"
            )
        
        # Special requirements
        with st.expander("🔧 Special Requirements"):
            requirements = st.multiselect(
                "Select any special requirements:",
                [
                    "Include personal story",
                    "Add statistics/data",
                    "Include call-to-action for DMs",
                    "Mention specific product/service",
                    "Keep it beginner-friendly",
                    "Make it controversy/debate-worthy",
                    "Include trending audio suggestion",
                    "Add visual directions for trending format"
                ]
            )
    
    with col2:
        st.subheader("🎯 Personalization Preview")
        
        st.info(f"**Your Voice:** {persona.unique_voice}")
        st.info(f"**Target Audience:** {persona.target_audience}")
        st.info(f"**Your Expertise:** {', '.join(persona.expertise[:3])}")
        
        st.subheader("📏 Script Specs")
        target_words = st.session_state.engine._calculate_target_length(duration)
        st.metric("Target Length", f"~{target_words} words")
        st.metric("Estimated Duration", f"{duration} seconds")
        
        # Learned patterns preview
        if persona.hook_patterns:
            st.subheader("🧠 Your Patterns")
            st.write("**Hook Style:**")
            for pattern in persona.hook_patterns[:2]:
                st.write(f"• {pattern}")
    
    # Generate button
    if st.button("🚀 Generate Intelligent Script", type="primary", disabled=not topic):
        generate_intelligent_script(topic, context, duration, content_type, urgency, requirements)
    
    # Display current script
    if st.session_state.current_script:
        display_generated_script(st.session_state.current_script)

def generate_intelligent_script(topic: str, context: str, duration: int, 
                               content_type: str, urgency: str, requirements: List[str]):
    """Generate script using intelligent engine"""
    
    persona = st.session_state.current_persona
    
    with st.spinner("🧠 Creating your personalized script..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Create request
            status_text.text("📋 Analyzing your request...")
            progress_bar.progress(20)
            
            request = ContentRequest(
                topic=topic,
                context=context,
                target_length=duration,
                specific_requirements=requirements,
                content_type=content_type,
                urgency=urgency
            )
            
            # Generate script
            status_text.text("🤖 Generating personalized content...")
            progress_bar.progress(60)
            
            result = st.session_state.engine.generate_personalized_script(persona.user_id, request)
            
            status_text.text("✨ Optimizing for viral potential...")
            progress_bar.progress(90)
            
            if result["success"]:
                st.session_state.current_script = result
                st.session_state.generated_scripts.append(result)
                
                progress_bar.progress(100)
                status_text.text("✅ Perfect script generated!")
                
                # Success banner
                score = result['best_attempt_score']
                viral_potential = result['viral_potential']
                
                st.markdown(f"""
                <div class="success-banner">
                    <h3>🎉 Personalized Script Generated!</h3>
                    <p>Quality Score: {score:.1f}/100 | Viral Potential: {viral_potential:.1f}% | Length: {result['script_length_words']} words</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Clear progress
                import time
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
                st.rerun()
            
            else:
                st.error("❌ Script generation failed. Please try again.")
        
        except Exception as e:
            st.error(f"❌ Generation error: {str(e)}")
            progress_bar.empty()
            status_text.empty()

def display_generated_script(script_data: Dict[str, Any]):
    """Display the generated script with analytics"""
    
    st.markdown("---")
    st.header("📄 Your Personalized Script")
    
    # Analytics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        score = script_data['best_attempt_score']
        score_class = "metric-good" if score >= 70 else "metric-average" if score >= 50 else "metric-poor"
        st.markdown(f'<p class="{score_class}">Quality Score<br>{score:.1f}/100</p>', unsafe_allow_html=True)
    
    with col2:
        viral = script_data['viral_potential']
        viral_class = "metric-good" if viral >= 70 else "metric-average" if viral >= 50 else "metric-poor"
        st.markdown(f'<p class="{viral_class}">Viral Potential<br>{viral:.1f}%</p>', unsafe_allow_html=True)
    
    with col3:
        words = script_data['script_length_words']
        duration = script_data['estimated_duration']
        st.markdown(f'<p class="metric-good">Length<br>{words} words<br>~{duration}s</p>', unsafe_allow_html=True)
    
    with col4:
        personalization = script_data['personalization_score']
        pers_class = "metric-good" if personalization >= 15 else "metric-average" if personalization >= 10 else "metric-poor"
        st.markdown(f'<p class="{pers_class}">Personalization<br>{personalization:.1f}/20</p>', unsafe_allow_html=True)
    
    with col5:
        attempts = script_data['generation_attempts']
        st.markdown(f'<p class="metric-good">AI Attempts<br>{attempts}/3</p>', unsafe_allow_html=True)
    
    # Script content
    script_content = script_data['script']
    
    # Format with better styling
    formatted_script = script_content.replace(
        'HOOK:', '<div style="color: #667eea; font-weight: bold; font-size: 18px; margin-top: 10px;">🎯 HOOK:</div>'
    ).replace(
        'BODY:', '<div style="color: #667eea; font-weight: bold; font-size: 18px; margin-top: 20px;">📝 BODY:</div>'
    ).replace(
        'CTA:', '<div style="color: #667eea; font-weight: bold; font-size: 18px; margin-top: 20px;">📢 CTA:</div>'
    ).replace(
        'CAPTION:', '<div style="color: #667eea; font-weight: bold; font-size: 18px; margin-top: 20px;">💬 CAPTION:</div>'
    ).replace(
        'VISUAL DIRECTIONS:', '<div style="color: #667eea; font-weight: bold; font-size: 18px; margin-top: 20px;">🎬 VISUAL DIRECTIONS:</div>'
    ).replace(
        'HASHTAGS:', '<div style="color: #667eea; font-weight: bold; font-size: 18px; margin-top: 20px;">🏷️ HASHTAGS:</div>'
    )
    
    st.markdown(f"""
    <div class="script-output">
    {formatted_script}
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Copy Script", use_container_width=True):
            st.code(script_data['script'], language="text")
    
    with col2:
        if st.button("🔄 Regenerate", use_container_width=True):
            # Keep the same request but regenerate
            st.session_state.regenerate = True
            st.rerun()
    
    with col3:
        if st.button("💾 Save to History", use_container_width=True):
            # Already saved automatically
            st.success("✅ Script saved to history!")
    
    with col4:
        if st.button("📊 Detailed Analysis", use_container_width=True):
            show_detailed_analysis(script_data)

def show_detailed_analysis(script_data: Dict[str, Any]):
    """Show detailed script analysis"""
    
    st.subheader("📊 Detailed Script Analysis")
    
    # Request details
    request_data = script_data.get('request', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Original Request:**")
        st.write(f"Topic: {request_data.get('topic', 'N/A')}")
        st.write(f"Context: {request_data.get('context', 'None provided')}")
        st.write(f"Duration: {request_data.get('target_length', 'N/A')} seconds")
        st.write(f"Type: {request_data.get('content_type', 'N/A')}")
    
    with col2:
        st.write("**Generation Details:**")
        st.write(f"Generated: {script_data.get('generated_at', 'N/A')[:19]}")
        st.write(f"Persona Used: {script_data.get('persona_used', 'N/A')}")
        st.write(f"Optimization Applied: {'Yes' if script_data.get('optimization_applied') else 'No'}")
        st.write(f"Success Rate: {script_data.get('generation_attempts', 0)}/3 attempts")

def show_profile_management():
    """Profile creation and management interface"""
    
    st.header("👤 Profile Management")
    
    if st.session_state.current_persona:
        show_existing_profile()
    else:
        show_profile_creation()

def show_existing_profile():
    """Show and edit existing profile"""
    
    persona = st.session_state.current_persona
    
    st.subheader(f"Current Profile: {persona.name}")
    
    # Profile overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Basic Info:**")
        st.write(f"Name: {persona.name}")
        st.write(f"Created: {persona.created_at[:10]}")
        st.write(f"Voice Style: {persona.unique_voice}")
        st.write(f"Primary Goal: {persona.primary_goal}")
    
    with col2:
        st.write("**Audience & Expertise:**")
        st.write(f"Target Audience: {persona.target_audience}")
        st.write(f"Expertise: {', '.join(persona.expertise)}")
        st.write(f"Personality: {', '.join(persona.personality_traits)}")
    
    # Full story
    with st.expander("📖 Your Full Story"):
        st.write(persona.story)
    
    # Learned patterns
    user_patterns = st.session_state.engine.patterns.get(persona.user_id, [])
    if user_patterns:
        with st.expander("🧠 Learned Patterns"):
            for pattern in user_patterns:
                st.write(f"**{pattern.pattern_type}:** {pattern.content}")
    
    # Actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Create New Profile", use_container_width=True):
            st.session_state.current_persona = None
            st.rerun()
    
    with col2:
        if st.button("📤 Upload More Scripts", use_container_width=True):
            st.session_state.show_script_upload = True
    
    with col3:
        if st.button("🗑️ Delete Profile", use_container_width=True):
            st.session_state.confirm_delete = True

def show_profile_creation():
    """Profile creation interface"""
    
    st.subheader("🆕 Create Your Intelligent Profile")
    st.write("Tell me about yourself and I'll create a personalized AI that understands your unique voice and style.")
    
    with st.form("create_profile"):
        # Basic info
        name = st.text_input("Your Name*", placeholder="e.g., Sarah Johnson")
        
        # The big story
        story = st.text_area(
            "Your Story* (This is the most important part!)",
            height=200,
            placeholder="""Tell me about yourself! For example:

Hi, I'm Sarah, a certified personal trainer and nutritionist with 5 years of experience. I specialize in helping busy professionals stay fit with quick, effective workouts they can do at home.

My journey started when I was working 60-hour weeks in corporate and gained 30 pounds. I tried every diet and workout program but nothing stuck because they were too complicated and time-consuming.

That's when I developed my 15-minute workout method and lost the weight for good. Now I help other busy people achieve their fitness goals without spending hours at the gym.

What makes me different is that I focus on sustainable habits, not quick fixes. I believe fitness should fit into your life, not take over your life.

My audience is primarily working professionals aged 25-45 who want to get in shape but feel like they don't have time. They're tired of complicated programs and want simple, proven strategies that actually work.

The more detail you provide, the better I can understand you!""",
            help="This is where the magic happens! The more you tell me about yourself, your background, your expertise, your audience, and what makes you unique, the better your personalized AI will be."
        )
        
        # Example scripts
        st.subheader("📄 Your Best Scripts (Optional but Recommended)")
        st.write("Upload 1-3 of your most successful scripts so I can learn your style:")
        
        example_scripts = []
        for i in range(3):
            script = st.text_area(
                f"Example Script {i+1} (Optional)",
                height=150,
                key=f"script_{i}",
                placeholder=f"""Paste one of your successful scripts here, for example:

HOOK: Want to lose weight without giving up your favorite foods? Here's my secret!

BODY: I used to think I had to eat salad every day to lose weight. Then I discovered the 80/20 rule that changed everything. 80% of the time I eat nutritious foods, 20% of the time I enjoy treats guilt-free.

CTA: What's your favorite treat that you don't want to give up? Comment below!

CAPTION: The weight loss secret that lets you eat what you love ✨

HASHTAGS: #WeightLoss #HealthyEating #SustainableFitness #FoodFreedom"""
            )
            if script.strip():
                example_scripts.append(script.strip())
        
        # Submit
        if st.form_submit_button("🧠 Create My Intelligent Profile", type="primary"):
            if name and story:
                create_intelligent_profile(name, story, example_scripts)
            else:
                st.error("❌ Please provide at least your name and story!")

def create_intelligent_profile(name: str, story: str, example_scripts: List[str]):
    """Create intelligent profile using the engine"""
    
    with st.spinner("🧠 Creating your intelligent profile..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔍 Analyzing your story...")
            progress_bar.progress(25)
            
            status_text.text("🎯 Understanding your audience...")
            progress_bar.progress(50)
            
            if example_scripts:
                status_text.text("📚 Learning from your scripts...")
                progress_bar.progress(75)
            
            # Create persona
            persona = st.session_state.engine.create_user_persona(name, story, example_scripts)
            
            status_text.text("✅ Profile created successfully!")
            progress_bar.progress(100)
            
            # Set as current
            st.session_state.current_persona = persona
            
            # Update personas list
            st.session_state.personas = st.session_state.engine.list_personas()
            
            # Success message
            st.markdown(f"""
            <div class="success-banner">
                <h3>🎉 Intelligent Profile Created!</h3>
                <p>Your AI now understands your unique voice and style. Ready to generate personalized scripts!</p>
            </div>
            """, unsafe_allow_html=True)
            
            import time
            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Profile creation failed: {str(e)}")
            progress_bar.empty()
            status_text.empty()

def show_script_history():
    """Show script generation history"""
    
    st.header("📊 Script History")
    
    if not st.session_state.generated_scripts:
        st.info("No scripts generated yet! Go to the Generate tab to create your first personalized script.")
        return
    
    scripts = st.session_state.generated_scripts
    
    # Overall stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Scripts", len(scripts))
    
    with col2:
        avg_score = sum(s.get('best_attempt_score', 0) for s in scripts) / len(scripts)
        st.metric("Avg Quality", f"{avg_score:.1f}/100")
    
    with col3:
        avg_viral = sum(s.get('viral_potential', 0) for s in scripts) / len(scripts)
        st.metric("Avg Viral Potential", f"{avg_viral:.1f}%")
    
    with col4:
        total_words = sum(s.get('script_length_words', 0) for s in scripts)
        st.metric("Total Words Generated", total_words)
    
    st.markdown("---")
    
    # Script list
    for i, script in enumerate(reversed(scripts)):  # Show newest first
        request = script.get('request', {})
        
        with st.expander(f"📄 {request.get('topic', 'Untitled')[:60]}... (Score: {script.get('best_attempt_score', 0):.1f})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Script preview
                script_preview = script['script'][:400] + "..." if len(script['script']) > 400 else script['script']
                st.text_area("Script Preview", script_preview, height=200, disabled=True, key=f"preview_{i}")
            
            with col2:
                # Metrics
                st.write("**Performance:**")
                st.write(f"Quality Score: {script.get('best_attempt_score', 0):.1f}/100")
                st.write(f"Viral Potential: {script.get('viral_potential', 0):.1f}%")
                st.write(f"Personalization: {script.get('personalization_score', 0):.1f}/20")
                
                st.write("**Details:**")
                st.write(f"Length: {script.get('script_length_words', 0)} words")
                st.write(f"Duration: ~{script.get('estimated_duration', 0)}s")
                st.write(f"Generated: {script.get('generated_at', '')[:10]}")
                
                # Actions
                if st.button("👁️ View Full", key=f"view_{i}"):
                    st.session_state.current_script = script
                    st.success("Script loaded for viewing!")
                
                if st.button("📋 Copy", key=f"copy_{i}"):
                    st.code(script['script'])

if __name__ == "__main__":
    main()