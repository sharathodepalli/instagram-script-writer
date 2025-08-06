"""
UI Enhancements for Instagram Script Writer
Improve the current UI without rebuilding from scratch
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List

def load_enhanced_css():
    """Enhanced CSS for better UI"""
    st.markdown("""
    <style>
    /* Enhanced Main Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.3rem;
        opacity: 0.95;
        margin-bottom: 0;
    }
    
    /* Enhanced Script Output */
    .script-output {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: none;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        line-height: 1.9;
        color: #2c3e50;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
        position: relative;
        font-size: 16px;
    }
    
    .script-output::before {
        content: '✨ AI Generated Script';
        position: absolute;
        top: -12px;
        left: 30px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Enhanced Metrics Cards */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Enhanced Section Headers */
    .section-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem 2rem;
        border-radius: 15px;
        color: white;
        margin: 2rem 0 1rem 0;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
        box-shadow: 0 6px 20px rgba(240, 147, 251, 0.4);
    }
    
    /* Enhanced Progress Bars */
    .stProgress .st-bo {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 8px;
        border-radius: 10px;
    }
    
    /* Enhanced Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Success/Info Messages */
    .success-message {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(86, 171, 47, 0.3);
    }
    
    .info-message {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    }
    
    /* Enhanced Input Fields */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e9ecef;
        padding: 12px 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e9ecef;
        padding: 12px 16px;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Loading Animations */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .loading-text {
        animation: pulse 2s infinite;
        color: #667eea;
        font-weight: bold;
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .script-output {
            padding: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_animated_header():
    """Create an enhanced animated header"""
    st.markdown("""
    <div class="main-header">
        <h1>🧠 Intelligent Script Writer</h1>
        <p>AI-Powered Content That Understands Your Voice & Your Niche</p>
        <div style="margin-top: 1.5rem; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div style="text-align: center;">
                <div style="font-size: 2rem;">⚡</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Lightning Fast</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem;">🎯</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Personalized</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem;">🚀</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Viral Ready</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem;">🧠</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">AI-Powered</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_quality_gauge(score: float, title: str = "Quality Score") -> go.Figure:
    """Create a quality gauge visualization"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 20, 'color': '#2c3e50'}},
        delta = {'reference': 70, 'increasing': {'color': "#28a745"}, 'decreasing': {'color': "#dc3545"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickcolor': '#667eea'},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 50], 'color': "rgba(220, 53, 69, 0.3)"},
                {'range': [50, 70], 'color': "rgba(255, 193, 7, 0.3)"},
                {'range': [70, 90], 'color': "rgba(40, 167, 69, 0.3)"},
                {'range': [90, 100], 'color': "rgba(25, 135, 84, 0.3)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        font={'color': "#2c3e50", 'family': "Inter"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_metrics_dashboard(script_data: Dict[str, Any]):
    """Create an enhanced metrics dashboard"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Quality Score Gauge
        quality_score = script_data.get('best_attempt_score', 0)
        fig_quality = create_quality_gauge(quality_score, "Quality Score")
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        # Viral Potential Gauge  
        viral_score = script_data.get('viral_potential', 0)
        fig_viral = create_quality_gauge(viral_score, "Viral Potential")
        st.plotly_chart(fig_viral, use_container_width=True)
    
    with col3:
        # Personalization Gauge
        personal_score = script_data.get('personalization_score', 0) * 5  # Scale to 100
        fig_personal = create_quality_gauge(personal_score, "Personalization")
        st.plotly_chart(fig_personal, use_container_width=True)

def show_enhanced_success_message(script_data: Dict[str, Any]):
    """Show enhanced success message with confetti effect"""
    
    score = script_data.get('best_attempt_score', 0)
    viral_potential = script_data.get('viral_potential', 0)
    
    if score >= 80:
        emoji = "🌟"
        message = "EXCELLENT SCRIPT GENERATED!"
        color_class = "success-message"
    elif score >= 70:
        emoji = "⭐"
        message = "GREAT SCRIPT GENERATED!"
        color_class = "success-message"
    else:
        emoji = "✨"
        message = "GOOD SCRIPT GENERATED!"
        color_class = "info-message"
    
    st.markdown(f"""
    <div class="{color_class}">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{emoji}</div>
            <div style="font-size: 1.3rem; font-weight: bold; margin-bottom: 0.5rem;">{message}</div>
            <div style="font-size: 1rem; opacity: 0.9;">
                Quality: {score:.1f}/100 | Viral Potential: {viral_potential:.1f}% | 
                Length: {script_data.get('script_length_words', 0)} words
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_step_progress(current_step: int, total_steps: int, steps: List[str]):
    """Create a visual step progress indicator"""
    
    progress_html = """
    <div style="display: flex; justify-content: space-between; align-items: center; margin: 2rem 0;">
    """
    
    for i, step in enumerate(steps):
        is_current = i == current_step
        is_completed = i < current_step
        
        if is_completed:
            circle_color = "#28a745"
            text_color = "#28a745"
            icon = "✓"
        elif is_current:
            circle_color = "#667eea"
            text_color = "#667eea"
            icon = str(i + 1)
        else:
            circle_color = "#e9ecef"
            text_color = "#6c757d"
            icon = str(i + 1)
        
        progress_html += f"""
        <div style="text-align: center; flex: 1;">
            <div style="
                width: 40px; height: 40px; border-radius: 50%; 
                background: {circle_color}; color: white; 
                display: flex; align-items: center; justify-content: center;
                font-weight: bold; margin: 0 auto 0.5rem auto;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            ">{icon}</div>
            <div style="color: {text_color}; font-size: 0.9rem; font-weight: 500;">
                {step}
            </div>
        </div>
        """
        
        # Add connector line (except for last step)
        if i < len(steps) - 1:
            line_color = "#28a745" if is_completed else "#e9ecef"
            progress_html += f"""
            <div style="
                height: 2px; background: {line_color}; 
                flex-grow: 1; margin: 0 1rem; margin-top: -20px;
            "></div>
            """
    
    progress_html += "</div>"
    st.markdown(progress_html, unsafe_allow_html=True)

def create_feature_showcase():
    """Create a feature showcase section"""
    
    st.markdown("""
    <div class="section-header">
        🌟 What Makes This AI Special?
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    features = [
        ("🧠", "Personal Intelligence", "Learns your unique voice and style from your content"),
        ("🎯", "Domain Expertise", "Uses proven patterns from high-performing content in your niche"),
        ("⚡", "Multi-Attempt Generation", "Creates 3 versions and picks the best one"),
        ("📊", "Quality Scoring", "Analyzes and scores every script for viral potential")
    ]
    
    for col, (emoji, title, description) in zip([col1, col2, col3, col4], features):
        with col:
            st.markdown(f"""
            <div style="
                text-align: center; padding: 1.5rem; background: white; 
                border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                margin-bottom: 1rem; min-height: 200px;
                display: flex; flex-direction: column; justify-content: center;
            ">
                <div style="font-size: 3rem; margin-bottom: 1rem;">{emoji}</div>
                <div style="font-weight: bold; color: #2c3e50; margin-bottom: 0.5rem; font-size: 1.1rem;">
                    {title}
                </div>
                <div style="color: #6c757d; font-size: 0.9rem; line-height: 1.4;">
                    {description}
                </div>
            </div>
            """, unsafe_allow_html=True)

def create_onboarding_tour():
    """Create an onboarding tour for new users"""
    
    if 'show_onboarding' not in st.session_state:
        st.session_state.show_onboarding = True
    
    if st.session_state.show_onboarding and not st.session_state.get('current_persona'):
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 2rem; border-radius: 15px; margin: 2rem 0;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        ">
            <div style="text-align: center;">
                <h2 style="margin-bottom: 1rem;">👋 Welcome to Your AI Script Writer!</h2>
                <p style="font-size: 1.1rem; margin-bottom: 1.5rem; opacity: 0.95;">
                    Let's get you set up in 3 simple steps to start generating amazing, personalized content!
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show step progress
        create_step_progress(0, 3, ["Create Profile", "Generate Script", "Optimize & Use"])
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Get Started - Create Your Profile!", use_container_width=True):
                st.session_state.show_onboarding = False
                st.rerun()

def enhanced_script_display(script_data: Dict[str, Any]):
    """Enhanced script display with better formatting"""
    
    # Show success message with metrics
    show_enhanced_success_message(script_data)
    
    # Show metrics dashboard
    st.markdown("""
    <div class="section-header">
        📊 Performance Analytics
    </div>
    """, unsafe_allow_html=True)
    
    create_metrics_dashboard(script_data)
    
    # Show the script with enhanced formatting
    st.markdown("""
    <div class="section-header">
        📄 Your Personalized Script
    </div>
    """, unsafe_allow_html=True)
    
    # Original script display code here...
    script_content = script_data['script']
    
    # Enhanced formatting
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