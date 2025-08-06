"""Enhanced script generation with viral optimization and context awareness."""

import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import openai
from openai import APIError, RateLimitError
import tenacity
from pinecone import Pinecone
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.schema import Document

try:
    from .config import (
        OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_HOST, PINECONE_INDEX,
        MODEL_FINE_TUNED, TEMPERATURE, RETRIEVAL_TOP_K, logger
    )
    from .user_profile import UserProfileManager
    from .hashtag_optimizer import HashtagOptimizer
    from .viral_scorer import ViralPotentialScorer
    from .enhanced_scraper import EnhancedContentScraper
except ImportError:
    from src.config import (
        OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_HOST, PINECONE_INDEX,
        MODEL_FINE_TUNED, TEMPERATURE, RETRIEVAL_TOP_K, logger
    )
    from src.user_profile import UserProfileManager
    from src.hashtag_optimizer import HashtagOptimizer
    from src.viral_scorer import ViralPotentialScorer
    from src.enhanced_scraper import EnhancedContentScraper


class EnhancedScriptGenerator:
    """Advanced script generator with viral optimization and context awareness."""
    
    def __init__(self):
        """Initialize the enhanced generator with all components."""
        # Initialize OpenAI
        openai.api_key = OPENAI_API_KEY
        self.chat_model = ChatOpenAI(
            model=MODEL_FINE_TUNED,
            temperature=TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Initialize Pinecone for retrieval
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Initialize enhancement components
        self.profile_manager = UserProfileManager()
        self.hashtag_optimizer = HashtagOptimizer()
        self.viral_scorer = ViralPotentialScorer()
        self.scraper = EnhancedContentScraper()
        
        # Advanced prompts for different generation strategies
        self.generation_strategies = {
            "viral_optimized": self._get_viral_optimized_prompt(),
            "story_driven": self._get_story_driven_prompt(), 
            "educational": self._get_educational_prompt(),
            "entertainment": self._get_entertainment_prompt(),
            "trending": self._get_trending_prompt()
        }
    
    def generate_viral_script(self, topic: str, strategy: str = "viral_optimized",
                            use_trending_data: bool = True, 
                            optimize_iterations: int = 2) -> Dict[str, Any]:
        """
        Generate a script optimized for viral potential.
        
        Args:
            topic: Main topic for the script
            strategy: Generation strategy to use
            use_trending_data: Whether to use trending content analysis
            optimize_iterations: Number of optimization iterations
            
        Returns:
            Comprehensive result with script, analysis, and optimizations
        """
        logger.info(f"Generating viral script for topic: {topic}")
        
        # Get user context
        user_context = self.profile_manager.get_context_for_generation()
        
        # Get trending insights if requested
        trending_insights = None
        if use_trending_data:
            trending_insights = self._get_trending_insights(topic, user_context)
        
        # Generate initial script
        initial_script = self._generate_base_script(topic, strategy, user_context, trending_insights)
        
        # Optimize through iterations
        optimized_script = initial_script
        optimization_history = []
        
        for iteration in range(optimize_iterations):
            logger.info(f"Optimization iteration {iteration + 1}")
            
            # Score current script
            viral_score = self.viral_scorer.calculate_viral_score(
                optimized_script["script"], topic, user_context
            )
            
            # Get optimization suggestions
            optimization = self.viral_scorer.optimize_for_virality(
                optimized_script["script"], topic, user_context
            )
            
            # Apply optimizations
            improved_script = self._apply_optimizations(
                optimized_script["script"], optimization, topic, user_context
            )
            
            optimization_history.append({
                "iteration": iteration + 1,
                "score_before": viral_score.total_score,
                "improvements_applied": len(optimization["optimization_plan"]),
                "script": improved_script
            })
            
            optimized_script["script"] = improved_script
        
        # Generate optimal hashtags
        optimal_hashtags = self.hashtag_optimizer.generate_optimal_hashtags(
            topic, user_context, 30
        )
        
        # Final viral score
        final_viral_score = self.viral_scorer.calculate_viral_score(
            optimized_script["script"], topic, user_context
        )
        
        # Enhance script with hashtags
        final_script = self._integrate_hashtags(optimized_script["script"], optimal_hashtags)
        
        return {
            "success": True,
            "script": final_script,
            "topic": topic,
            "strategy": strategy,
            "viral_score": final_viral_score,
            "hashtag_strategy": {
                "hashtags": [h.tag for h in optimal_hashtags],
                "strategy_report": self.hashtag_optimizer.get_hashtag_strategy_report(optimal_hashtags)
            },
            "optimization_history": optimization_history,
            "trending_insights": trending_insights,
            "user_context": user_context,
            "generation_metadata": {
                "model_used": MODEL_FINE_TUNED,
                "temperature": TEMPERATURE,
                "optimization_iterations": optimize_iterations,
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def generate_multiple_variants(self, topic: str, variant_count: int = 3,
                                 strategies: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate multiple script variants for A/B testing.
        
        Args:
            topic: Main topic for scripts
            variant_count: Number of variants to generate
            strategies: List of strategies to use (random if None)
            
        Returns:
            List of script variants with analysis
        """
        logger.info(f"Generating {variant_count} script variants for: {topic}")
        
        if not strategies:
            strategies = list(self.generation_strategies.keys())
        
        variants = []
        
        for i in range(variant_count):
            # Use different strategies for variety
            strategy = strategies[i % len(strategies)]
            
            # Add some randomness to temperature for variety
            original_temp = self.chat_model.temperature
            self.chat_model.temperature = TEMPERATURE + random.uniform(-0.1, 0.1)
            
            try:
                variant = self.generate_viral_script(
                    topic, strategy=strategy, optimize_iterations=1
                )
                variant["variant_number"] = i + 1
                variant["strategy_used"] = strategy
                variants.append(variant)
                
            except Exception as e:
                logger.error(f"Error generating variant {i+1}: {e}")
                continue
            finally:
                # Restore original temperature
                self.chat_model.temperature = original_temp
        
        # Rank variants by viral potential
        variants.sort(key=lambda x: x["viral_score"].total_score, reverse=True)
        
        logger.info(f"Generated {len(variants)} variants successfully")
        return variants
    
    def _get_trending_insights(self, topic: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get insights from trending content related to the topic."""
        try:
            niche = user_context.get("niche", "lifestyle") if user_context else "lifestyle"
            
            # Get viral content and analysis
            viral_content, analysis = self.scraper.get_niche_specific_content(
                niche, max_content=20
            )
            
            return {
                "viral_content_count": len(viral_content),
                "top_hashtags": analysis.top_hashtags[:10],
                "common_themes": analysis.common_themes[:8],
                "viral_elements": analysis.viral_elements[:8],
                "content_recommendations": analysis.content_recommendations,
                "optimal_posting_times": analysis.optimal_posting_times
            }
            
        except Exception as e:
            logger.warning(f"Could not fetch trending insights: {e}")
            return {}
    
    def _generate_base_script(self, topic: str, strategy: str, 
                            user_context: Dict[str, Any], 
                            trending_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the base script using the specified strategy."""
        
        # Get similar scripts for context
        similar_scripts = self._retrieve_similar_scripts(topic, k=RETRIEVAL_TOP_K)
        
        # Build comprehensive prompt context
        prompt_context = {
            "topic": topic,
            "user_context": user_context or {},
            "similar_scripts": similar_scripts,
            "trending_insights": trending_insights or {},
            "strategy": strategy
        }
        
        # Select and format prompt
        prompt_template = self.generation_strategies[strategy]
        prompt = prompt_template.format(**prompt_context)
        
        # Generate script
        try:
            response = self.chat_model.invoke(prompt)
            script_content = response.content.strip()
            
            return {
                "script": script_content,
                "prompt_used": prompt,
                "similar_scripts_used": len(similar_scripts),
                "trending_data_used": bool(trending_insights)
            }
            
        except Exception as e:
            logger.error(f"Error generating base script: {e}")
            raise
    
    def _retrieve_similar_scripts(self, topic: str, k: int = 3) -> List[str]:
        """Retrieve similar scripts from vector database."""
        try:
            # Create query embedding
            query_embedding = self.embeddings.embed_query(topic)
            
            # Search in Pinecone
            index = self.pc.Index(PINECONE_INDEX)
            results = index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True
            )
            
            # Extract script content
            scripts = []
            for match in results.matches:
                if match.metadata and "text" in match.metadata:
                    scripts.append(match.metadata["text"])
            
            return scripts
            
        except Exception as e:
            logger.warning(f"Could not retrieve similar scripts: {e}")
            return []
    
    def _apply_optimizations(self, script: str, optimization: Dict[str, Any],
                           topic: str, user_context: Dict[str, Any]) -> str:
        """Apply viral optimization suggestions to improve the script."""
        
        optimization_plan = optimization.get("optimization_plan", [])
        
        if not optimization_plan:
            return script
        
        # Create optimization prompt
        optimization_prompt = f"""
ORIGINAL SCRIPT:
{script}

OPTIMIZATION REQUIREMENTS:
{chr(10).join(f"• {plan['issue']}: {plan['solution']}" for plan in optimization_plan[:3])}

IMPROVEMENT EXAMPLES:
{chr(10).join(f"- {example}" for plan in optimization_plan[:3] for example in plan.get('examples', [])[:2])}

Please rewrite the script incorporating these optimizations while maintaining the original structure and message. Focus on the highest-impact improvements first.

OPTIMIZED SCRIPT:
"""
        
        try:
            response = self.chat_model.invoke(optimization_prompt)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Error applying optimizations: {e}")
            return script
    
    def _integrate_hashtags(self, script: str, hashtags: List[Any]) -> str:
        """Integrate optimized hashtags into the script."""
        
        # Extract hashtag tags
        hashtag_tags = [h.tag for h in hashtags]
        
        # Check if script already has hashtags section
        if "HASHTAGS:" in script:
            # Replace existing hashtags
            parts = script.split("HASHTAGS:")
            if len(parts) == 2:
                before_hashtags = parts[0]
                hashtag_string = " ".join(hashtag_tags)
                return f"{before_hashtags}HASHTAGS:\n{hashtag_string}"
        
        # Add hashtags section if not present
        hashtag_string = " ".join(hashtag_tags)
        return f"{script}\n\nHASHTAGS:\n{hashtag_string}"
    
    def _get_viral_optimized_prompt(self) -> str:
        """Get prompt template optimized for viral content."""
        return """
You are an expert Instagram script writer specializing in viral content. Create a high-performing Instagram Reel script that maximizes engagement and reach.

TOPIC: {topic}

USER CONTEXT:
{user_context}

TRENDING INSIGHTS:
{trending_insights}

SIMILAR HIGH-PERFORMING SCRIPTS:
{similar_scripts}

VIRAL OPTIMIZATION REQUIREMENTS:
1. Hook: Start with a powerful attention-grabbing hook using proven patterns
2. Emotional Triggers: Include curiosity, urgency, or surprise elements
3. Value: Provide clear, actionable value to the audience
4. Structure: Use the format below with engaging transitions
5. CTA: Include strong calls-to-action for maximum engagement
6. Authenticity: Make it feel personal and genuine

SCRIPT FORMAT:
HOOK: [Powerful opening that stops scrolling - use curiosity/urgency/surprise]

BODY:
[Valuable content with emotional triggers and story elements. Include:]
- Personal anecdotes or experiences
- Surprising facts or insights
- Clear, actionable advice
- Smooth transitions between points

CTA: [Strong call-to-action encouraging engagement - comment, share, save, follow]

CAPTION: [Compelling caption under 125 characters with hook continuation]

VISUAL DIRECTIONS: [Clear filming directions for maximum visual impact]

Write a script that feels authentic to the user's voice while incorporating viral elements. Focus on stopping power, emotional engagement, and shareability.
"""
    
    def _get_story_driven_prompt(self) -> str:
        """Get prompt template for story-driven content."""
        return """
Create an engaging Instagram Reel script that uses storytelling to connect with the audience emotionally.

TOPIC: {topic}
USER CONTEXT: {user_context}
TRENDING INSIGHTS: {trending_insights}
SIMILAR SCRIPTS: {similar_scripts}

STORYTELLING REQUIREMENTS:
1. Personal narrative or relatable scenario
2. Clear beginning, middle, and end
3. Emotional journey or transformation
4. Relatable characters or situations
5. Surprise twist or revelation
6. Strong emotional payoff

SCRIPT FORMAT:
HOOK: [Story opening that creates immediate intrigue]

BODY:
[Story development with:]
- Setting and characters
- Conflict or challenge
- Journey/struggle
- Resolution or insight
- Lesson learned

CTA: [Encourage audience to share their own stories]

CAPTION: [Story hook that entices viewing]

VISUAL DIRECTIONS: [Cinematic storytelling directions]

Make the story feel authentic and relatable while delivering value around the topic.
"""
    
    def _get_educational_prompt(self) -> str:
        """Get prompt template for educational content."""
        return """
Create an informative Instagram Reel script that educates while entertaining.

TOPIC: {topic}
USER CONTEXT: {user_context}
TRENDING INSIGHTS: {trending_insights}
SIMILAR SCRIPTS: {similar_scripts}

EDUCATIONAL REQUIREMENTS:
1. Clear learning objective
2. Step-by-step breakdown
3. Easy-to-follow structure
4. Practical examples
5. Actionable takeaways
6. Expert credibility

SCRIPT FORMAT:
HOOK: [Educational promise - "Learn how to..." or "Master the art of..."]

BODY:
[Educational content with:]
- Clear explanation of concept
- Step-by-step instructions
- Examples and demonstrations
- Common mistakes to avoid
- Pro tips and insider knowledge

CTA: [Encourage questions, sharing experiences, or trying the technique]

CAPTION: [Educational value proposition]

VISUAL DIRECTIONS: [Clear demonstration and teaching visuals]

Balance education with entertainment to maintain engagement throughout.
"""
    
    def _get_entertainment_prompt(self) -> str:
        """Get prompt template for entertainment-focused content."""
        return """
Create a fun, entertaining Instagram Reel script that brings joy and laughter.

TOPIC: {topic}
USER CONTEXT: {user_context}
TRENDING INSIGHTS: {trending_insights}
SIMILAR SCRIPTS: {similar_scripts}

ENTERTAINMENT REQUIREMENTS:
1. Humor or fun element
2. Relatable situations
3. Surprise or unexpected elements
4. High energy and enthusiasm
5. Shareable moments
6. Feel-good factor

SCRIPT FORMAT:
HOOK: [Fun, energetic opening that promises entertainment]

BODY:
[Entertaining content with:]
- Humorous observations
- Relatable scenarios
- Funny comparisons
- Unexpected twists
- Energetic delivery
- Interactive elements

CTA: [Encourage sharing, tagging friends, or participating in fun]

CAPTION: [Fun, engaging caption that extends the entertainment]

VISUAL DIRECTIONS: [Dynamic, energetic filming with visual comedy]

Keep it light, fun, and highly shareable while staying relevant to the topic.
"""
    
    def _get_trending_prompt(self) -> str:
        """Get prompt template that leverages current trends."""
        return """
Create an Instagram Reel script that taps into current trends and viral patterns.

TOPIC: {topic}
USER CONTEXT: {user_context}
TRENDING INSIGHTS: {trending_insights}
SIMILAR SCRIPTS: {similar_scripts}

TRENDING REQUIREMENTS:
1. Current viral elements and phrases
2. Trending audio/music compatibility
3. Popular format or challenge adaptation
4. Timely references
5. Hashtag trend integration
6. Cultural moment relevance

SCRIPT FORMAT:
HOOK: [Trending opener that signals current relevance]

BODY:
[Trend-aware content with:]
- Current viral phrases or formats
- Timely references
- Popular culture connections
- Trending challenges adaptation
- Community inside jokes
- Moment-specific relevance

CTA: [Trend-specific engagement encouragement]

CAPTION: [Trending caption with relevant cultural references]

VISUAL DIRECTIONS: [Trend-compatible visual style and editing]

Blend trending elements naturally with valuable content to maximize both reach and engagement.
"""


def analyze_script_performance_potential(script: str, topic: str) -> Dict[str, Any]:
    """
    Analyze a script's potential performance across multiple dimensions.
    
    Args:
        script: Script content to analyze
        topic: Script topic
        
    Returns:
        Comprehensive performance analysis
    """
    # Initialize analyzers
    viral_scorer = ViralPotentialScorer()
    hashtag_optimizer = HashtagOptimizer()
    
    # Get viral score
    viral_score = viral_scorer.calculate_viral_score(script, topic)
    
    # Extract hashtags for analysis
    import re
    hashtags_found = re.findall(r'#\w+', script)
    
    # Analyze hashtag effectiveness (simplified)
    hashtag_analysis = {
        "count": len(hashtags_found),
        "hashtags": hashtags_found,
        "recommendations": []
    }
    
    if len(hashtags_found) < 20:
        hashtag_analysis["recommendations"].append("Add more hashtags (aim for 20-30)")
    elif len(hashtags_found) > 30:
        hashtag_analysis["recommendations"].append("Reduce hashtags to 20-30 most relevant")
    
    # Overall performance prediction
    performance_factors = {
        "viral_potential": viral_score.percentage,
        "hashtag_optimization": min(100, (len(hashtags_found) / 25) * 100),
        "content_quality": viral_score.breakdown.get("value_proposition", 0) / 12 * 100,
        "engagement_likelihood": viral_score.breakdown.get("call_to_action", 0) / 10 * 100
    }
    
    overall_performance = sum(performance_factors.values()) / len(performance_factors)
    
    return {
        "viral_score": viral_score,
        "hashtag_analysis": hashtag_analysis,
        "performance_factors": performance_factors,
        "overall_performance_score": round(overall_performance, 1),
        "performance_grade": viral_score.grade,
        "improvement_priority": viral_score.recommendations[:3]
    }