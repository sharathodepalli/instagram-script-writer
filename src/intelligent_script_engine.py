"""
Intelligent Script Generation Engine
The core brain that understands users, learns patterns, and generates personalized viral content
"""

import json
import re
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import openai
from openai import APIError
from collections import Counter, defaultdict
import hashlib
from langsmith import traceable

try:
    from .config import OPENAI_API_KEY, MODEL_FINE_TUNED, LANGCHAIN_API_KEY, LANGCHAIN_TRACING_V2, LANGCHAIN_PROJECT, logger
    from .domain_intelligence import DomainIntelligenceEngine
except ImportError:
    from src.config import OPENAI_API_KEY, MODEL_FINE_TUNED, LANGCHAIN_API_KEY, LANGCHAIN_TRACING_V2, LANGCHAIN_PROJECT, logger
    from src.domain_intelligence import DomainIntelligenceEngine

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Configure LangSmith tracing
if LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_TRACING_V2"] = LANGCHAIN_TRACING_V2
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT


@dataclass
class UserPersona:
    """Deep user understanding and persona"""
    user_id: str
    name: str
    
    # Core Identity
    story: str  # User's personal story/background
    expertise: List[str]  # What they're expert in
    unique_voice: str  # Their unique speaking style
    personality_traits: List[str]  # Personality characteristics
    
    # Content Patterns (learned from their scripts)
    hook_patterns: List[str]  # Their successful hook styles
    storytelling_style: str  # How they tell stories
    cta_preferences: List[str]  # Their preferred call-to-actions
    script_structure: Dict[str, Any]  # Their typical script structure
    
    # Audience Understanding
    target_audience: str
    audience_pain_points: List[str]  # What their audience struggles with
    audience_desires: List[str]  # What their audience wants
    audience_language: str  # How their audience speaks
    
    # Performance Intelligence
    high_performing_topics: List[str]  # Their best topics
    engagement_triggers: List[str]  # What gets their audience engaged
    optimal_script_length: int  # Ideal length for their content (in words)
    posting_insights: Dict[str, Any]  # Best times, frequencies, etc.
    
    # Content Goals
    primary_goal: str  # educate, entertain, inspire, sell, etc.
    secondary_goals: List[str]
    brand_message: str  # Core message they want to convey
    
    created_at: str
    updated_at: str


@dataclass
class ScriptPattern:
    """Learned patterns from user's successful scripts"""
    pattern_id: str
    pattern_type: str  # hook, body, cta, structure, etc.
    content: str
    performance_score: float
    topic_relevance: List[str]  # Which topics this pattern works for
    extracted_at: str


@dataclass
class ContentRequest:
    """Intelligent content generation request"""
    topic: str
    context: Optional[str]  # Additional context from user
    target_length: int  # Desired length in seconds (30-60 seconds)
    specific_requirements: List[str]  # Any special requirements
    content_type: str  # educational, entertaining, inspirational, etc.
    urgency: str  # how urgent/trending this needs to be


class IntelligentScriptEngine:
    """
    The core intelligence that understands users deeply and generates 
    personalized, viral-optimized scripts
    """
    
    def __init__(self, data_dir: str = "data/intelligence"):
        """Initialize the intelligent engine"""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Script length standards (words for different durations)
        self.length_standards = {
            15: 35,   # 15 seconds: ~35 words
            30: 75,   # 30 seconds: ~75 words  
            45: 115,  # 45 seconds: ~115 words
            60: 150,  # 60 seconds: ~150 words
            90: 225   # 90 seconds: ~225 words
        }
        
        # Core components
        self.personas = {}  # user_id -> UserPersona
        self.patterns = defaultdict(list)  # user_id -> List[ScriptPattern]
        
        # Domain intelligence for niche expertise
        try:
            self.domain_intelligence = DomainIntelligenceEngine()
            logger.info("🎯 Domain Intelligence connected")
        except Exception as e:
            logger.warning(f"⚠️ Domain Intelligence unavailable: {e}")
            self.domain_intelligence = None
        
        self.viral_intelligence = self._load_viral_intelligence()
        
        logger.info("🧠 Intelligent Script Engine initialized")
    
    @traceable
    def create_user_persona(self, name: str, story: str, example_scripts: List[str] = None) -> UserPersona:
        """
        Create a deep user persona from their story and example scripts
        """
        logger.info(f"🔍 Creating intelligent persona for {name}")
        
        # Generate unique user ID
        user_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        # Analyze user's story and background
        story_analysis = self._analyze_user_story(story)
        
        # Analyze example scripts if provided
        script_patterns = []
        script_insights = {}
        if example_scripts:
            script_patterns = self._extract_script_patterns(example_scripts, user_id)
            script_insights = self._analyze_user_scripts(example_scripts)
        
        # Create comprehensive persona
        persona = UserPersona(
            user_id=user_id,
            name=name,
            story=story,
            expertise=story_analysis.get("expertise", []),
            unique_voice=story_analysis.get("voice_style", "authentic and relatable"),
            personality_traits=story_analysis.get("personality", []),
            hook_patterns=script_insights.get("hook_patterns", []),
            storytelling_style=script_insights.get("storytelling_style", "personal experience"),
            cta_preferences=script_insights.get("cta_patterns", []),
            script_structure=script_insights.get("structure", {}),
            target_audience=story_analysis.get("target_audience", "general audience"),
            audience_pain_points=story_analysis.get("audience_pain_points", []),
            audience_desires=story_analysis.get("audience_desires", []),
            audience_language=story_analysis.get("audience_language", "casual and friendly"),
            high_performing_topics=script_insights.get("best_topics", []),
            engagement_triggers=script_insights.get("engagement_triggers", []),
            optimal_script_length=script_insights.get("optimal_length", 75),  # Default 30-second script
            posting_insights={},
            primary_goal=story_analysis.get("primary_goal", "inspire and educate"),
            secondary_goals=story_analysis.get("secondary_goals", []),
            brand_message=story_analysis.get("brand_message", ""),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Store persona and patterns
        self.personas[user_id] = persona
        if script_patterns:
            self.patterns[user_id] = script_patterns
        
        # Save to disk
        self._save_persona(persona)
        
        logger.info(f"✅ Created intelligent persona for {name} (ID: {user_id})")
        return persona
    
    @traceable
    def generate_personalized_script(self, user_id: str, request: ContentRequest) -> Dict[str, Any]:
        """
        Generate a highly personalized script based on deep user understanding
        """
        logger.info(f"🎯 Generating personalized script for user {user_id}")
        
        if user_id not in self.personas:
            raise ValueError(f"User persona not found: {user_id}")
        
        persona = self.personas[user_id]
        user_patterns = self.patterns.get(user_id, [])
        
        # Get domain intelligence patterns
        domain_patterns = []
        if self.domain_intelligence and hasattr(persona, 'expertise') and persona.expertise:
            # Use first expertise as niche
            niche = persona.expertise[0] if persona.expertise else "general"
            try:
                domain_patterns = self.domain_intelligence.get_domain_intelligence(
                    niche=niche.lower(),
                    topic=request.topic,
                    content_type=request.content_type,
                    top_k=3
                )
                logger.info(f"🎯 Retrieved {len(domain_patterns)} domain intelligence patterns")
            except Exception as e:
                logger.warning(f"⚠️ Could not retrieve domain intelligence: {e}")
        
        # Calculate optimal script length based on request
        target_words = self._calculate_target_length(request.target_length)
        
        # Build intelligent generation prompt with domain intelligence
        generation_prompt = self._build_hybrid_intelligent_prompt(persona, user_patterns, domain_patterns, request, target_words)
        
        # Generate with multiple attempts for best result
        script_attempts = []
        for attempt in range(3):  # Try 3 times to get the best result
            try:
                response = openai.chat.completions.create(
                    model=MODEL_FINE_TUNED,
                    messages=[{"role": "user", "content": generation_prompt}],
                    temperature=0.7 + (attempt * 0.1),  # Slightly different temperature each time
                    max_tokens=1500
                )
                
                script = response.choices[0].message.content.strip()
                
                # Score this attempt
                script_score = self._score_script_quality(script, persona, request)
                script_attempts.append({
                    "script": script,
                    "score": script_score,
                    "attempt": attempt + 1
                })
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                continue
        
        if not script_attempts:
            raise Exception("All generation attempts failed")
        
        # Select best script
        best_script = max(script_attempts, key=lambda x: x["score"])
        
        # Optimize the best script
        optimized_script = self._optimize_script(best_script["script"], persona, request)
        
        # Final quality check and adjustments
        final_script = self._final_quality_pass(optimized_script, persona, request, target_words)
        
        # Create comprehensive result
        result = {
            "script": final_script,
            "user_id": user_id,
            "request": asdict(request),
            "persona_used": persona.name,
            "script_length_words": len(final_script.split()),
            "estimated_duration": self._estimate_duration(final_script),
            "personalization_score": self._calculate_personalization_score(final_script, persona),
            "viral_potential": self._estimate_viral_potential(final_script, persona),
            "optimization_applied": True,
            "generation_attempts": len(script_attempts),
            "best_attempt_score": best_script["score"],
            "generated_at": datetime.now().isoformat(),
            "success": True
        }
        
        logger.info(f"✅ Generated personalized script (Score: {best_script['score']:.1f})")
        return result
    
    def learn_from_performance(self, user_id: str, script: str, performance_data: Dict[str, Any]):
        """
        Learn from script performance to improve future generations
        """
        if user_id not in self.personas:
            return
        
        persona = self.personas[user_id]
        
        # Extract successful elements if performance was good
        if performance_data.get("engagement_rate", 0) > 0.05:  # 5% engagement is good
            # Extract and store successful patterns
            patterns = self._extract_successful_patterns(script, performance_data)
            
            for pattern in patterns:
                pattern.pattern_id = f"{user_id}_{len(self.patterns[user_id])}"
                self.patterns[user_id].append(pattern)
            
            # Update persona insights
            self._update_persona_insights(persona, script, performance_data)
            
            logger.info(f"📚 Learned {len(patterns)} new patterns from successful script")
    
    @traceable
    def _analyze_user_story(self, story: str) -> Dict[str, Any]:
        """
        Use AI to deeply analyze user's story and extract insights
        """
        analysis_prompt = f"""
        Analyze this person's story and extract deep insights for content creation:

        STORY:
        {story}

        Extract and return a JSON with:
        {{
            "expertise": ["list of their areas of expertise"],
            "voice_style": "their unique communication style",
            "personality": ["personality traits"],
            "target_audience": "who they speak to",
            "audience_pain_points": ["what their audience struggles with"],
            "audience_desires": ["what their audience wants"],
            "audience_language": "how their audience speaks",
            "primary_goal": "their main content goal",
            "secondary_goals": ["other goals"],
            "brand_message": "their core message",
            "content_niche": "their content category"
        }}

        Be specific and insightful. Focus on what makes them unique.
        """
        
        try:
            response = openai.chat.completions.create(
                model=MODEL_FINE_TUNED,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3
            )
            
            # Extract JSON from response
            response_text = response.choices[0].message.content.strip()
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback analysis
                return self._fallback_story_analysis(story)
                
        except Exception as e:
            logger.warning(f"AI story analysis failed: {e}")
            return self._fallback_story_analysis(story)
    
    def _analyze_user_scripts(self, scripts: List[str]) -> Dict[str, Any]:
        """
        Analyze user's example scripts to understand their patterns
        """
        if not scripts:
            return {}
        
        # Combine all scripts for analysis
        all_scripts = "\n\n---SCRIPT---\n\n".join(scripts)
        
        analysis_prompt = f"""
        Analyze these example scripts from a content creator to understand their unique patterns:

        SCRIPTS:
        {all_scripts}

        Extract and return JSON with:
        {{
            "hook_patterns": ["their typical hook styles/patterns"],
            "storytelling_style": "how they tell stories",
            "cta_patterns": ["their call-to-action styles"],
            "structure": {{"typical_structure": "their usual script format"}},
            "best_topics": ["topics they cover well"],
            "engagement_triggers": ["what gets audience engaged"],
            "optimal_length": 75,
            "voice_characteristics": ["unique voice elements"],
            "value_delivery": "how they deliver value"
        }}

        Focus on patterns that make their content unique and engaging.
        """
        
        try:
            response = openai.chat.completions.create(
                model=MODEL_FINE_TUNED,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._fallback_script_analysis(scripts)
                
        except Exception as e:
            logger.warning(f"Script analysis failed: {e}")
            return self._fallback_script_analysis(scripts)
    
    def _build_intelligent_prompt(self, persona: UserPersona, patterns: List[ScriptPattern], 
                                request: ContentRequest, target_words: int) -> str:
        """
        Build an intelligent generation prompt with deep personalization
        """
        
        # Get relevant patterns for this topic
        relevant_patterns = [p for p in patterns if any(topic in p.topic_relevance for topic in [request.topic.lower()])]
        
        prompt = f"""
        You are creating a highly personalized Instagram Reel script for {persona.name}.

        USER PERSONA DEEP DIVE:
        - Name: {persona.name}
        - Story: {persona.story}
        - Expertise: {', '.join(persona.expertise)}
        - Unique Voice: {persona.unique_voice}
        - Personality: {', '.join(persona.personality_traits)}
        - Primary Goal: {persona.primary_goal}
        - Brand Message: {persona.brand_message}

        AUDIENCE INTELLIGENCE:
        - Target Audience: {persona.target_audience}
        - Audience Pain Points: {', '.join(persona.audience_pain_points)}
        - Audience Desires: {', '.join(persona.audience_desires)}
        - Audience Language: {persona.audience_language}

        CONTENT REQUEST:
        - Topic: {request.topic}
        - Context: {request.context or 'Not specified'}
        - Target Length: {request.target_length} seconds (~{target_words} words)
        - Content Type: {request.content_type}
        - Special Requirements: {', '.join(request.specific_requirements) if request.specific_requirements else 'None'}

        LEARNED SUCCESS PATTERNS:
        """
        
        # Add learned patterns
        if relevant_patterns:
            prompt += "\nFrom their successful content:\n"
            for pattern in relevant_patterns[:3]:  # Top 3 relevant patterns
                prompt += f"- {pattern.pattern_type}: {pattern.content}\n"
        
        if persona.hook_patterns:
            prompt += f"\nHook Style: {', '.join(persona.hook_patterns[:3])}\n"
        
        if persona.cta_preferences:
            prompt += f"CTA Style: {', '.join(persona.cta_preferences[:3])}\n"
        
        prompt += f"""

SCRIPT GENERATION REQUIREMENTS:
1. **Perfect Length**: Exactly {target_words} words (±5 words) for {request.target_length}-second video
2. **Voice Match**: Write EXACTLY how {persona.name} would speak - use their voice, personality, and style
3. **Audience Connection**: Address their specific audience pain points and desires
4. **Value Delivery**: Provide clear, actionable value aligned with their expertise
5. **Viral Optimization**: Include proven engagement triggers and storytelling elements
6. **Authenticity**: Make it feel genuinely from {persona.name}, not generic

SCRIPT STRUCTURE (OPTIMIZE FOR {request.target_length} SECONDS):
HOOK: [Powerful opening that stops scrolling - use their hook style]

BODY: [Main content with their storytelling style, addressing audience needs]

CTA: [Strong call-to-action in their preferred style]

CAPTION: [Engaging caption under 125 characters]

VISUAL DIRECTIONS: [Clear filming directions for {request.target_length}-second video]

HASHTAGS: [15-20 strategic hashtags for maximum reach]

CRITICAL SUCCESS FACTORS:
- Sound EXACTLY like {persona.name} would speak
- Address specific pain points: {', '.join(persona.audience_pain_points[:2])}
- Deliver on audience desires: {', '.join(persona.audience_desires[:2])}
- Stay true to their brand message: {persona.brand_message}
- Make it instantly usable for a {request.target_length}-second Reel

Generate the perfect personalized script now:
        """
        
        return prompt
    
    def _build_hybrid_intelligent_prompt(self, persona: UserPersona, user_patterns: List[ScriptPattern], 
                                        domain_patterns: List[Dict[str, Any]], request: ContentRequest, 
                                        target_words: int) -> str:
        """
        Build hybrid prompt combining personal intelligence with domain intelligence
        """
        
        # Start with personal intelligence
        prompt = self._build_intelligent_prompt(persona, user_patterns, request, target_words)
        
        # Add domain intelligence if available
        if domain_patterns and self.domain_intelligence:
            niche = persona.expertise[0] if persona.expertise else "general"
            
            prompt += f"""

DOMAIN INTELLIGENCE - PROVEN {niche.upper()} SUCCESS PATTERNS:
Based on analysis of high-performing content in {niche} niche:

"""
            
            for i, pattern in enumerate(domain_patterns[:3], 1):
                metadata = pattern.get('metadata', {})
                similarity = pattern.get('similarity_score', 0)
                
                prompt += f"""
Success Pattern #{i} (Relevance: {similarity:.1f}):
- Viral Score: {metadata.get('viral_score', 0):.1f}/100
- Engagement Rate: {metadata.get('engagement_rate', 0):.1f}%
- Hook Type: {metadata.get('hook_type', 'N/A')}
- Content Type: {metadata.get('content_type', 'N/A')}
- CTA Type: {metadata.get('cta_type', 'N/A')}
- Performance: {metadata.get('likes', 0):,} likes, {metadata.get('views', 0):,} views
"""
            
            prompt += f"""
HYBRID GENERATION INSTRUCTIONS:
1. PERSONAL INTELLIGENCE: Use {persona.name}'s unique voice, style, and patterns
2. DOMAIN INTELLIGENCE: Apply proven {niche} success patterns above
3. OPTIMAL COMBINATION: Blend personal authenticity with domain expertise
4. VIRAL ELEMENTS: Include high-performing {niche} content characteristics
5. AUDIENCE MATCH: Ensure content resonates with both personal and niche audiences

Your goal: Create a script that sounds authentically like {persona.name} while using 
proven {niche} success patterns for maximum viral potential.
"""
        
        return prompt
    
    def _calculate_target_length(self, duration_seconds: int) -> int:
        """Calculate target word count for desired video duration"""
        # Find closest standard length
        closest_duration = min(self.length_standards.keys(), 
                             key=lambda x: abs(x - duration_seconds))
        
        # Interpolate if not exact match
        if duration_seconds not in self.length_standards:
            if duration_seconds < 15:
                return int(35 * (duration_seconds / 15))
            elif duration_seconds > 90:
                return int(225 * (duration_seconds / 90))
            else:
                # Linear interpolation between two closest points
                lower = max([d for d in self.length_standards.keys() if d <= duration_seconds])
                upper = min([d for d in self.length_standards.keys() if d >= duration_seconds])
                
                if lower == upper:
                    return self.length_standards[lower]
                
                # Interpolate
                lower_words = self.length_standards[lower]
                upper_words = self.length_standards[upper]
                ratio = (duration_seconds - lower) / (upper - lower)
                return int(lower_words + (upper_words - lower_words) * ratio)
        
        return self.length_standards[closest_duration]
    
    @traceable
    def _score_script_quality(self, script: str, persona: UserPersona, request: ContentRequest) -> float:
        """Score script quality based on multiple factors"""
        score = 0.0
        
        # Length appropriateness (0-20 points)
        target_words = self._calculate_target_length(request.target_length)
        actual_words = len(script.split())
        length_diff = abs(actual_words - target_words)
        length_score = max(0, 20 - (length_diff * 0.5))
        score += length_score
        
        # Structure completeness (0-20 points)
        required_sections = ['HOOK:', 'BODY:', 'CTA:', 'CAPTION:', 'HASHTAGS:']
        sections_found = sum(1 for section in required_sections if section in script)
        structure_score = (sections_found / len(required_sections)) * 20
        score += structure_score
        
        # Personalization (0-20 points)
        personalization_score = self._calculate_personalization_score(script, persona)
        score += personalization_score
        
        # Engagement elements (0-20 points) 
        engagement_score = self._score_engagement_elements(script)
        score += engagement_score
        
        # Topic relevance (0-20 points)
        topic_score = self._score_topic_relevance(script, request.topic)
        score += topic_score
        
        return min(100, score)
    
    def _calculate_personalization_score(self, script: str, persona: UserPersona) -> float:
        """Calculate how well the script matches user's persona"""
        score = 0.0
        script_lower = script.lower()
        
        # Check for expertise keywords
        expertise_matches = sum(1 for exp in persona.expertise 
                              if any(word in script_lower for word in exp.lower().split()))
        score += min(5, expertise_matches)
        
        # Check for personality traits
        personality_matches = sum(1 for trait in persona.personality_traits 
                                if trait.lower() in script_lower)
        score += min(5, personality_matches)
        
        # Check for audience language
        if persona.audience_language.lower() in script_lower:
            score += 5
        
        # Check for brand message alignment
        if persona.brand_message and any(word in script_lower 
                                       for word in persona.brand_message.lower().split()):
            score += 5
        
        return score
    
    def _score_engagement_elements(self, script: str) -> float:
        """Score script for engagement elements"""
        score = 0.0
        script_lower = script.lower()
        
        # Question hooks
        if '?' in script:
            score += 5
        
        # Emotional triggers
        emotion_words = ['amazing', 'incredible', 'shocking', 'secret', 'never', 'always', 'everyone']
        emotion_matches = sum(1 for word in emotion_words if word in script_lower)
        score += min(5, emotion_matches)
        
        # Call to action strength
        cta_words = ['comment', 'like', 'share', 'save', 'follow', 'tag', 'try']
        cta_matches = sum(1 for word in cta_words if word in script_lower)
        score += min(5, cta_matches)
        
        # Personal pronouns (relatability)
        personal_words = ['i', 'my', 'me', 'you', 'your', 'we', 'us']
        personal_matches = sum(script_lower.count(word) for word in personal_words)
        score += min(5, personal_matches * 0.5)
        
        return score
    
    def _score_topic_relevance(self, script: str, topic: str) -> float:
        """Score how relevant the script is to the requested topic"""
        script_lower = script.lower()
        topic_words = topic.lower().split()
        
        # Count topic word appearances
        relevance_score = 0
        for word in topic_words:
            if len(word) > 2:  # Skip very short words
                relevance_score += script_lower.count(word) * 5
        
        return min(20, relevance_score)
    
    def _optimize_script(self, script: str, persona: UserPersona, request: ContentRequest) -> str:
        """Apply intelligent optimizations to the script"""
        
        optimization_prompt = f"""
        Optimize this Instagram script for {persona.name} to maximize viral potential:

        CURRENT SCRIPT:
        {script}

        OPTIMIZATION REQUIREMENTS:
        - Perfect length for {request.target_length}-second video
        - Enhance hook for maximum stopping power
        - Improve storytelling flow
        - Strengthen call-to-action
        - Optimize for {persona.target_audience}
        - Maintain {persona.unique_voice} voice

        USER INSIGHTS:
        - Expertise: {', '.join(persona.expertise)}
        - Audience Pain Points: {', '.join(persona.audience_pain_points)}
        - Engagement Triggers: {', '.join(persona.engagement_triggers)}

        Return the optimized script with the same structure but enhanced for viral potential:
        """
        
        try:
            response = openai.chat.completions.create(
                model=MODEL_FINE_TUNED,
                messages=[{"role": "user", "content": optimization_prompt}],
                temperature=0.5
            )
            
            optimized = response.choices[0].message.content.strip()
            return optimized if len(optimized) > len(script) * 0.8 else script  # Safety check
            
        except Exception as e:
            logger.warning(f"Optimization failed: {e}")
            return script
    
    def _final_quality_pass(self, script: str, persona: UserPersona, 
                          request: ContentRequest, target_words: int) -> str:
        """Final quality check and length adjustment"""
        
        current_words = len(script.split())
        
        # Length adjustment if needed
        if abs(current_words - target_words) > 10:  # More than 10 words off
            adjustment_prompt = f"""
            Adjust this script to be exactly {target_words} words (±5) for a {request.target_length}-second video:

            CURRENT SCRIPT ({current_words} words):
            {script}

            Requirements:
            - Maintain the same structure and key messages
            - Keep the voice and style identical
            - {'Shorten by removing less essential details' if current_words > target_words else 'Expand with relevant details'}
            - Perfect for {request.target_length}-second Instagram Reel

            Return the adjusted script:
            """
            
            try:
                response = openai.chat.completions.create(
                    model=MODEL_FINE_TUNED,
                    messages=[{"role": "user", "content": adjustment_prompt}],
                    temperature=0.3
                )
                
                adjusted = response.choices[0].message.content.strip()
                adjusted_words = len(adjusted.split())
                
                # Use adjusted version if it's closer to target
                if abs(adjusted_words - target_words) < abs(current_words - target_words):
                    script = adjusted
                    
            except Exception as e:
                logger.warning(f"Length adjustment failed: {e}")
        
        return script
    
    def _estimate_duration(self, script: str) -> int:
        """Estimate video duration based on word count"""
        word_count = len(script.split())
        
        # Find closest match in standards
        for duration, words in self.length_standards.items():
            if abs(words - word_count) < 10:
                return duration
        
        # Linear approximation
        return int(word_count * 0.5)  # Rough estimate: 2 words per second
    
    def _estimate_viral_potential(self, script: str, persona: UserPersona) -> float:
        """Estimate viral potential of the script"""
        # This is a simplified version - could be enhanced with ML model
        
        score = 50  # Base score
        script_lower = script.lower()
        
        # Viral elements
        viral_words = ['secret', 'nobody', 'everyone', 'shocking', 'amazing', 'never', 'always']
        viral_matches = sum(1 for word in viral_words if word in script_lower)
        score += viral_matches * 5
        
        # Question hooks
        if script.startswith('?') or 'HOOK:' in script and '?' in script.split('BODY:')[0]:
            score += 10
        
        # Personal story elements
        story_words = ['i', 'my', 'me', 'when i', 'i was', 'i discovered']
        story_matches = sum(1 for word in story_words if word in script_lower)
        score += min(15, story_matches * 2)
        
        # Call to action strength
        strong_ctas = ['comment below', 'save this', 'share with', 'tag someone', 'try this']
        cta_matches = sum(1 for cta in strong_ctas if cta in script_lower)
        score += cta_matches * 8
        
        return min(100, score)
    
    def _extract_script_patterns(self, scripts: List[str], user_id: str) -> List[ScriptPattern]:
        """Extract successful patterns from user's scripts"""
        patterns = []
        
        for i, script in enumerate(scripts):
            # Extract hooks
            hook_match = re.search(r'HOOK:\s*(.*?)(?=\n\n|\nBODY:)', script, re.IGNORECASE)
            if hook_match:
                patterns.append(ScriptPattern(
                    pattern_id=f"{user_id}_hook_{i}",
                    pattern_type="hook",
                    content=hook_match.group(1).strip(),
                    performance_score=80.0,  # Default good score
                    topic_relevance=["general"],
                    extracted_at=datetime.now().isoformat()
                ))
            
            # Extract CTAs
            cta_match = re.search(r'CTA:\s*(.*?)(?=\n\n|\nCAPTION:)', script, re.IGNORECASE)
            if cta_match:
                patterns.append(ScriptPattern(
                    pattern_id=f"{user_id}_cta_{i}",
                    pattern_type="cta",
                    content=cta_match.group(1).strip(),
                    performance_score=80.0,
                    topic_relevance=["general"],
                    extracted_at=datetime.now().isoformat()
                ))
        
        return patterns
    
    def _extract_successful_patterns(self, script: str, performance_data: Dict[str, Any]) -> List[ScriptPattern]:
        """Extract patterns from high-performing scripts"""
        patterns = []
        performance_score = performance_data.get("engagement_rate", 0) * 100
        
        if performance_score > 5:  # Good performance
            # Extract hook if successful
            hook_match = re.search(r'HOOK:\s*(.*?)(?=\n\n|\nBODY:)', script, re.IGNORECASE)
            if hook_match:
                patterns.append(ScriptPattern(
                    pattern_id=f"perf_{datetime.now().timestamp()}",
                    pattern_type="successful_hook",
                    content=hook_match.group(1).strip(),
                    performance_score=performance_score,
                    topic_relevance=[performance_data.get("topic", "general")],
                    extracted_at=datetime.now().isoformat()
                ))
        
        return patterns
    
    def _update_persona_insights(self, persona: UserPersona, script: str, performance_data: Dict[str, Any]):
        """Update persona with insights from successful content"""
        # This would update the persona based on what worked
        # For now, just log the learning
        logger.info(f"📈 Learning from successful script for {persona.name}")
    
    def _fallback_story_analysis(self, story: str) -> Dict[str, Any]:
        """Fallback analysis if AI fails"""
        return {
            "expertise": ["content creation"],
            "voice_style": "authentic and relatable",
            "personality": ["helpful", "engaging"],
            "target_audience": "social media users",
            "audience_pain_points": ["lack of engagement", "content ideas"],
            "audience_desires": ["viral content", "audience growth"],
            "audience_language": "casual and friendly",
            "primary_goal": "educate and inspire",
            "secondary_goals": ["entertain"],
            "brand_message": "authentic content creation",
            "content_niche": "lifestyle"
        }
    
    def _fallback_script_analysis(self, scripts: List[str]) -> Dict[str, Any]:
        """Fallback script analysis if AI fails"""
        return {
            "hook_patterns": ["engaging questions", "surprising statements"],
            "storytelling_style": "personal experience",
            "cta_patterns": ["comment below", "share with friends"],
            "structure": {"typical_structure": "hook-body-cta"},
            "best_topics": ["general tips"],
            "engagement_triggers": ["questions", "personal stories"],
            "optimal_length": 75,
            "voice_characteristics": ["friendly", "authentic"],
            "value_delivery": "practical tips"
        }
    
    def _load_viral_intelligence(self) -> Dict[str, Any]:
        """Load viral intelligence data"""
        # This would load data about what makes content go viral
        return {
            "viral_hooks": ["secret that nobody tells you", "what if I told you", "stop doing this"],
            "engagement_triggers": ["questions", "shocking facts", "personal stories"],
            "optimal_lengths": self.length_standards,
            "trending_topics": ["productivity", "health", "money", "relationships"]
        }
    
    def _save_persona(self, persona: UserPersona):
        """Save persona to disk"""
        try:
            persona_file = os.path.join(self.data_dir, f"persona_{persona.user_id}.json")
            with open(persona_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(persona), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Could not save persona: {e}")
    
    def load_persona(self, user_id: str) -> Optional[UserPersona]:
        """Load persona from disk"""
        try:
            persona_file = os.path.join(self.data_dir, f"persona_{user_id}.json")
            if os.path.exists(persona_file):
                with open(persona_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                persona = UserPersona(**data)
                self.personas[user_id] = persona
                return persona
        except Exception as e:
            logger.warning(f"Could not load persona: {e}")
        return None
    
    def list_personas(self) -> List[Dict[str, str]]:
        """List all available personas"""
        personas = []
        try:
            for file in os.listdir(self.data_dir):
                if file.startswith("persona_") and file.endswith(".json"):
                    user_id = file.replace("persona_", "").replace(".json", "")
                    persona = self.load_persona(user_id)
                    if persona:
                        personas.append({
                            "user_id": user_id,
                            "name": persona.name,
                            "niche": getattr(persona, 'content_niche', 'general'),
                            "created_at": persona.created_at
                        })
        except Exception as e:
            logger.warning(f"Error listing personas: {e}")
        
        return sorted(personas, key=lambda x: x["created_at"], reverse=True)


# Convenience functions for easy usage

def create_intelligent_user(name: str, story: str, example_scripts: List[str] = None) -> UserPersona:
    """Create an intelligent user persona"""
    engine = IntelligentScriptEngine()
    return engine.create_user_persona(name, story, example_scripts)

def generate_intelligent_script(user_id: str, topic: str, duration: int = 30, 
                              context: str = None, content_type: str = "educational") -> Dict[str, Any]:
    """Generate an intelligent, personalized script"""
    engine = IntelligentScriptEngine()
    
    request = ContentRequest(
        topic=topic,
        context=context,
        target_length=duration,
        specific_requirements=[],
        content_type=content_type,
        urgency="normal"
    )
    
    return engine.generate_personalized_script(user_id, request)


if __name__ == "__main__":
    # Test the intelligent engine
    print("🧠 Testing Intelligent Script Engine...")
    
    # Create test user
    test_story = """
    I'm Sarah, a certified personal trainer and nutritionist with 5 years of experience. 
    I specialize in helping busy professionals stay fit with quick, effective workouts they can do at home. 
    My approach is all about making fitness accessible and sustainable. I believe everyone deserves to feel strong and confident.
    I struggled with my own fitness journey for years before finding what works, and now I want to help others avoid the same mistakes I made.
    """
    
    test_scripts = [
        """
        HOOK: Want to build muscle in just 15 minutes? Here's my secret weapon!

        BODY: As a trainer, I've discovered that compound movements are everything. You don't need hours at the gym - you need smart training. This 3-exercise routine hits every major muscle group and takes less time than your coffee break.

        CTA: Try this routine tomorrow morning and comment how you feel!

        CAPTION: 15-min muscle building routine that actually works ✨

        HASHTAGS: #Fitness #QuickWorkout #HomeGym #MuscleBuilding #BusyProfessionals
        """,
        """
        HOOK: I used to hate meal prep until I discovered this game-changing trick!

        BODY: Batch cooking proteins on Sunday changed everything for me. Now I prep 3 different proteins in 30 minutes and have variety all week. No more boring chicken and rice!

        CTA: What's your biggest meal prep struggle? Let me know below!

        CAPTION: Meal prep hack that saved my sanity 🙌

        HASHTAGS: #MealPrep #HealthyEating #Nutrition #MealPrepSunday #HealthyLifestyle
        """
    ]
    
    try:
        # Test persona creation
        engine = IntelligentScriptEngine()
        persona = engine.create_user_persona("Sarah", test_story, test_scripts)
        print(f"✅ Created persona for {persona.name}")
        
        # Test script generation
        request = ContentRequest(
            topic="morning workout routine for busy people",
            context="Help people who have no time for gym",
            target_length=30,
            specific_requirements=[],
            content_type="educational",
            urgency="normal"
        )
        
        result = engine.generate_personalized_script(persona.user_id, request)
        
        if result["success"]:
            print(f"✅ Generated personalized script!")
            print(f"📊 Script Length: {result['script_length_words']} words")
            print(f"⏱️ Estimated Duration: {result['estimated_duration']} seconds")
            print(f"🎯 Personalization Score: {result['personalization_score']:.1f}")
            print(f"🔥 Viral Potential: {result['viral_potential']:.1f}%")
            print("\n" + "="*50)
            print("GENERATED SCRIPT:")
            print("="*50)
            print(result["script"])
        else:
            print("❌ Script generation failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()