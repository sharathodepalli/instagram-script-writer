"""Advanced hashtag discovery and optimization system for viral content."""

import re
import requests
import json
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import time
import random
from dataclasses import dataclass

try:
    from .config import logger
    from .user_profile import UserProfileManager
except ImportError:
    from src.config import logger
    from src.user_profile import UserProfileManager


@dataclass
class HashtagMetrics:
    """Hashtag performance metrics."""
    tag: str
    popularity_score: float
    competition_level: str  # low, medium, high
    growth_trend: str  # rising, stable, declining
    engagement_potential: float
    niche_relevance: float
    viral_potential: float


class HashtagOptimizer:
    """Advanced hashtag discovery and optimization for maximum reach."""
    
    def __init__(self):
        """Initialize the hashtag optimizer."""
        self.profile_manager = UserProfileManager()
        
        # Hashtag categories for strategic mixing
        self.hashtag_categories = {
            "mega": 1000000,      # 1M+ posts (high competition, massive reach)
            "macro": 100000,      # 100K-1M posts (medium-high competition)
            "moderate": 10000,    # 10K-100K posts (medium competition)
            "niche": 1000,        # 1K-10K posts (low competition, targeted)
            "micro": 100          # 100-1K posts (very low competition)
        }
        
        # Industry-specific hashtag databases
        self.niche_hashtags = {
            "fitness": {
                "trending": ["#FitnessMotivation", "#WorkoutWednesday", "#FitLife", "#GymLife", "#HealthyLifestyle"],
                "evergreen": ["#Fitness", "#Workout", "#Health", "#Exercise", "#FitFam"],
                "engagement": ["#TransformationTuesday", "#MotivationMonday", "#FitnessJourney", "#StrongNotSkinny"],
                "community": ["#FitnessCommunity", "#FitFamily", "#WorkoutBuddy", "#FitnessGoals"]
            },
            "food": {
                "trending": ["#FoodieLife", "#RecipeOfTheDay", "#FoodPhotography", "#HomeCooking", "#FoodLover"],
                "evergreen": ["#Food", "#Recipe", "#Cooking", "#Foodie", "#Delicious"],
                "engagement": ["#RecipeShare", "#CookingTips", "#FoodHacks", "#MealPrep"],
                "community": ["#FoodCommunity", "#CookingWithLove", "#HomeCook", "#FoodBlogger"]
            },
            "lifestyle": {
                "trending": ["#LifestyleBlogger", "#DailyInspiration", "#SelfCare", "#Mindfulness", "#LifeHacks"],
                "evergreen": ["#Lifestyle", "#Life", "#Inspiration", "#Motivation", "#SelfImprovement"],
                "engagement": ["#LifeTips", "#DailyRoutine", "#SelfLove", "#PersonalGrowth"],
                "community": ["#LifestyleCommunity", "#LifestyleBlog", "#Inspiring", "#PositiveVibes"]
            },
            "business": {
                "trending": ["#Entrepreneur", "#BusinessTips", "#StartupLife", "#DigitalMarketing", "#BusinessGrowth"],
                "evergreen": ["#Business", "#Success", "#Leadership", "#Marketing", "#Productivity"],
                "engagement": ["#BusinessHacks", "#EntrepreneurLife", "#SuccessTips", "#BusinessMindset"],
                "community": ["#BusinessCommunity", "#Entrepreneurs", "#SmallBusiness", "#BusinessOwner"]
            },
            "tech": {
                "trending": ["#TechNews", "#Innovation", "#DigitalTransformation", "#AI", "#TechTips"],
                "evergreen": ["#Technology", "#Tech", "#Digital", "#Software", "#Programming"],
                "engagement": ["#TechHacks", "#CodeLife", "#TechReview", "#DigitalTrends"],
                "community": ["#TechCommunity", "#Developers", "#TechStartup", "#Innovation"]
            }
        }
        
        # Viral hashtag patterns
        self.viral_patterns = [
            "#Challenge", "#Trend", "#Viral", "#ForYou", "#Trending",
            "#Reel", "#Reels", "#Instagram", "#Insta", "#IG",
            "#Explore", "#Discover", "#Amazing", "#Incredible", "#MustSee"
        ]
    
    def generate_optimal_hashtags(self, topic: str, user_context: Dict[str, Any] = None, 
                                target_count: int = 30) -> List[HashtagMetrics]:
        """
        Generate optimized hashtags for maximum viral potential.
        
        Args:
            topic: Main topic/theme for the content
            user_context: User profile context
            target_count: Number of hashtags to generate
            
        Returns:
            List of HashtagMetrics with optimized hashtags
        """
        logger.info(f"Generating optimal hashtags for topic: {topic}")
        
        # Get user profile context
        if not user_context and self.profile_manager.current_profile:
            user_context = self.profile_manager.get_context_for_generation()
        
        niche = user_context.get("niche", "lifestyle") if user_context else "lifestyle"
        
        # Generate hashtag candidates
        candidates = []
        
        # 1. Topic-specific hashtags
        topic_hashtags = self._generate_topic_hashtags(topic)
        candidates.extend(topic_hashtags)
        
        # 2. Niche-specific hashtags
        niche_hashtags = self._get_niche_hashtags(niche)
        candidates.extend(niche_hashtags)
        
        # 3. Trending hashtags
        trending_hashtags = self._get_trending_hashtags()
        candidates.extend(trending_hashtags)
        
        # 4. User's preferred hashtags
        if user_context and user_context.get("preferred_hashtags"):
            candidates.extend(user_context["preferred_hashtags"])
        
        # 5. Viral potential hashtags
        viral_hashtags = self._get_viral_hashtags(topic, niche)
        candidates.extend(viral_hashtags)
        
        # Remove duplicates and clean hashtags
        unique_candidates = list(set([self._clean_hashtag(tag) for tag in candidates]))
        
        # Score and rank hashtags
        scored_hashtags = []
        for hashtag in unique_candidates:
            metrics = self._calculate_hashtag_metrics(hashtag, topic, niche, user_context)
            scored_hashtags.append(metrics)
        
        # Sort by viral potential and return top hashtags
        scored_hashtags.sort(key=lambda x: x.viral_potential, reverse=True)
        
        # Strategic selection: mix different competition levels
        final_hashtags = self._strategic_hashtag_selection(scored_hashtags, target_count)
        
        logger.info(f"Generated {len(final_hashtags)} optimized hashtags")
        return final_hashtags
    
    def _generate_topic_hashtags(self, topic: str) -> List[str]:
        """Generate hashtags based on the specific topic."""
        topic_words = re.findall(r'\b\w+\b', topic.lower())
        hashtags = []
        
        # Single word hashtags
        for word in topic_words:
            if len(word) > 2:
                hashtags.append(f"#{word.capitalize()}")
        
        # Combined hashtags
        if len(topic_words) >= 2:
            # Two-word combinations
            for i in range(len(topic_words) - 1):
                combined = f"#{topic_words[i].capitalize()}{topic_words[i+1].capitalize()}"
                hashtags.append(combined)
        
        # Topic variations
        topic_clean = re.sub(r'[^\w\s]', '', topic)
        hashtags.append(f"#{topic_clean.replace(' ', '').title()}")
        
        return hashtags
    
    def _get_niche_hashtags(self, niche: str) -> List[str]:
        """Get hashtags specific to the user's niche."""
        if niche not in self.niche_hashtags:
            niche = "lifestyle"  # fallback
        
        niche_tags = self.niche_hashtags[niche]
        hashtags = []
        
        # Mix different types of niche hashtags
        hashtags.extend(niche_tags.get("trending", []))
        hashtags.extend(niche_tags.get("evergreen", []))
        hashtags.extend(niche_tags.get("engagement", []))
        hashtags.extend(niche_tags.get("community", []))
        
        return hashtags
    
    def _get_trending_hashtags(self) -> List[str]:
        """Get currently trending hashtags."""
        # In a real implementation, this would connect to Instagram API or scrape trending data
        # For now, return simulated trending hashtags
        
        current_month = datetime.now().strftime("%B").lower()
        current_day = datetime.now().strftime("%A").lower()
        
        trending = [
            f"#{current_month.capitalize()}Vibes",
            f"#{current_day.capitalize()}Motivation",
            "#TrendingNow",
            "#ViralContent",
            "#ForYouPage",
            "#Trending2024",
            "#InstagramReels",
            "#ContentCreator",
            "#InfluencerLife",
            "#SocialMedia"
        ]
        
        return trending
    
    def _get_viral_hashtags(self, topic: str, niche: str) -> List[str]:
        """Get hashtags with high viral potential."""
        viral_tags = self.viral_patterns.copy()
        
        # Add niche-specific viral tags
        viral_tags.extend([
            f"#{niche.capitalize()}Viral",
            f"#{niche.capitalize()}Challenge",
            f"#{niche.capitalize()}Trending"
        ])
        
        # Add topic-specific viral tags
        topic_word = topic.split()[0] if topic else "Life"
        viral_tags.extend([
            f"#{topic_word.capitalize()}Challenge",
            f"#{topic_word.capitalize()}Trend"
        ])
        
        return viral_tags
    
    def _clean_hashtag(self, hashtag: str) -> str:
        """Clean and format hashtag."""
        # Remove extra characters and spaces
        cleaned = re.sub(r'[^\w]', '', hashtag)
        
        # Ensure it starts with #
        if not cleaned.startswith('#'):
            cleaned = f"#{cleaned}"
        
        # Capitalize properly
        if len(cleaned) > 1:
            cleaned = f"#{cleaned[1:].title()}"
        
        return cleaned
    
    def _calculate_hashtag_metrics(self, hashtag: str, topic: str, niche: str, 
                                 user_context: Dict[str, Any] = None) -> HashtagMetrics:
        """Calculate comprehensive metrics for a hashtag."""
        
        # Simulated metrics calculation (in real app, would use Instagram API)
        tag_lower = hashtag.lower()
        
        # Popularity score (0-100)
        popularity_score = self._estimate_popularity(hashtag)
        
        # Competition level
        competition_level = self._estimate_competition(popularity_score)
        
        # Growth trend
        growth_trend = self._estimate_growth_trend(hashtag, niche)
        
        # Engagement potential (0-100)
        engagement_potential = self._calculate_engagement_potential(hashtag, topic, niche)
        
        # Niche relevance (0-100)
        niche_relevance = self._calculate_niche_relevance(hashtag, niche, user_context)
        
        # Viral potential (weighted score)
        viral_potential = self._calculate_viral_potential(
            popularity_score, engagement_potential, niche_relevance, competition_level
        )
        
        return HashtagMetrics(
            tag=hashtag,
            popularity_score=popularity_score,
            competition_level=competition_level,
            growth_trend=growth_trend,
            engagement_potential=engagement_potential,
            niche_relevance=niche_relevance,
            viral_potential=viral_potential
        )
    
    def _estimate_popularity(self, hashtag: str) -> float:
        """Estimate hashtag popularity (simulated)."""
        # In real implementation, would query Instagram API
        
        # Simulate based on hashtag characteristics
        tag_length = len(hashtag)
        
        # Shorter, generic tags tend to be more popular
        if tag_length < 10:
            base_score = 80
        elif tag_length < 15:
            base_score = 60
        else:
            base_score = 40
        
        # Add randomness for simulation
        return min(100, base_score + random.uniform(-20, 20))
    
    def _estimate_competition(self, popularity_score: float) -> str:
        """Estimate competition level based on popularity."""
        if popularity_score > 80:
            return "high"
        elif popularity_score > 60:
            return "medium"
        elif popularity_score > 40:
            return "low"
        else:
            return "very_low"
    
    def _estimate_growth_trend(self, hashtag: str, niche: str) -> str:
        """Estimate growth trend for hashtag."""
        # Simulated trend analysis
        trends = ["rising", "stable", "declining"]
        
        # Newer/trending keywords tend to be rising
        if any(word in hashtag.lower() for word in ["2024", "trend", "viral", "new"]):
            return "rising"
        
        # Random for simulation
        return random.choice(trends)
    
    def _calculate_engagement_potential(self, hashtag: str, topic: str, niche: str) -> float:
        """Calculate engagement potential for hashtag."""
        score = 50  # base score
        
        # Topic relevance bonus
        if any(word in hashtag.lower() for word in topic.lower().split()):
            score += 20
        
        # Niche relevance bonus
        if niche in hashtag.lower():
            score += 15
        
        # Engagement-focused hashtags bonus
        engagement_words = ["challenge", "tips", "hack", "secret", "amazing", "incredible"]
        if any(word in hashtag.lower() for word in engagement_words):
            score += 25
        
        return min(100, score)
    
    def _calculate_niche_relevance(self, hashtag: str, niche: str, 
                                 user_context: Dict[str, Any] = None) -> float:
        """Calculate how relevant hashtag is to user's niche."""
        score = 0
        
        # Direct niche match
        if niche.lower() in hashtag.lower():
            score += 40
        
        # User's key topics match
        if user_context and user_context.get("key_topics"):
            for topic in user_context["key_topics"]:
                if topic.lower() in hashtag.lower():
                    score += 10
        
        # Niche-related keywords
        niche_keywords = {
            "fitness": ["fit", "gym", "workout", "health", "exercise"],
            "food": ["food", "recipe", "cook", "meal", "delicious"],
            "lifestyle": ["life", "daily", "routine", "inspire", "motivation"],
            "business": ["business", "success", "entrepreneur", "money", "growth"],
            "tech": ["tech", "digital", "innovation", "software", "ai"]
        }
        
        if niche in niche_keywords:
            for keyword in niche_keywords[niche]:
                if keyword in hashtag.lower():
                    score += 5
        
        return min(100, score)
    
    def _calculate_viral_potential(self, popularity: float, engagement: float, 
                                 relevance: float, competition: str) -> float:
        """Calculate overall viral potential score."""
        
        # Weight factors
        weights = {
            "popularity": 0.3,
            "engagement": 0.4,
            "relevance": 0.2,
            "competition": 0.1
        }
        
        # Competition score (lower competition = higher score)
        competition_scores = {
            "very_low": 100,
            "low": 80,
            "medium": 60,
            "high": 40
        }
        
        competition_score = competition_scores.get(competition, 50)
        
        # Calculate weighted score
        viral_score = (
            popularity * weights["popularity"] +
            engagement * weights["engagement"] +
            relevance * weights["relevance"] +
            competition_score * weights["competition"]
        )
        
        return round(viral_score, 2)
    
    def _strategic_hashtag_selection(self, scored_hashtags: List[HashtagMetrics], 
                                   target_count: int) -> List[HashtagMetrics]:
        """Strategically select hashtags for optimal reach."""
        
        # Strategic distribution:
        # 20% mega hashtags (massive reach)
        # 30% macro hashtags (good reach, less competition)
        # 30% moderate hashtags (targeted reach)
        # 20% niche hashtags (highly targeted)
        
        selected = []
        
        # Sort by different criteria for strategic selection
        by_popularity = sorted(scored_hashtags, key=lambda x: x.popularity_score, reverse=True)
        by_engagement = sorted(scored_hashtags, key=lambda x: x.engagement_potential, reverse=True)
        by_relevance = sorted(scored_hashtags, key=lambda x: x.niche_relevance, reverse=True)
        by_viral = sorted(scored_hashtags, key=lambda x: x.viral_potential, reverse=True)
        
        # Mix different types
        selections = [
            (by_viral[:target_count//3], "viral"),  # Top viral potential
            (by_engagement[:target_count//3], "engagement"),  # High engagement
            (by_relevance[:target_count//3], "relevance")   # High relevance
        ]
        
        used_hashtags = set()
        
        for hashtag_list, selection_type in selections:
            for hashtag in hashtag_list:
                if hashtag.tag not in used_hashtags and len(selected) < target_count:
                    selected.append(hashtag)
                    used_hashtags.add(hashtag.tag)
        
        # Fill remaining slots with best overall
        remaining_count = target_count - len(selected)
        for hashtag in by_viral:
            if hashtag.tag not in used_hashtags and remaining_count > 0:
                selected.append(hashtag)
                used_hashtags.add(hashtag.tag)
                remaining_count -= 1
        
        return selected[:target_count]
    
    def get_hashtag_strategy_report(self, hashtags: List[HashtagMetrics]) -> Dict[str, Any]:
        """Generate a comprehensive hashtag strategy report."""
        
        total_hashtags = len(hashtags)
        
        # Competition distribution
        competition_dist = Counter([h.competition_level for h in hashtags])
        
        # Average scores
        avg_viral = sum(h.viral_potential for h in hashtags) / total_hashtags
        avg_engagement = sum(h.engagement_potential for h in hashtags) / total_hashtags
        avg_relevance = sum(h.niche_relevance for h in hashtags) / total_hashtags
        
        # Growth trends
        growth_dist = Counter([h.growth_trend for h in hashtags])
        
        # Top performers
        top_viral = sorted(hashtags, key=lambda x: x.viral_potential, reverse=True)[:5]
        top_engagement = sorted(hashtags, key=lambda x: x.engagement_potential, reverse=True)[:5]
        
        return {
            "total_hashtags": total_hashtags,
            "average_scores": {
                "viral_potential": round(avg_viral, 2),
                "engagement_potential": round(avg_engagement, 2),
                "niche_relevance": round(avg_relevance, 2)
            },
            "competition_distribution": dict(competition_dist),
            "growth_distribution": dict(growth_dist),
            "top_performers": {
                "viral": [{"tag": h.tag, "score": h.viral_potential} for h in top_viral],
                "engagement": [{"tag": h.tag, "score": h.engagement_potential} for h in top_engagement]
            },
            "strategy_recommendations": self._generate_strategy_recommendations(hashtags)
        }
    
    def _generate_strategy_recommendations(self, hashtags: List[HashtagMetrics]) -> List[str]:
        """Generate strategic recommendations based on hashtag analysis."""
        recommendations = []
        
        # Competition analysis
        high_comp = len([h for h in hashtags if h.competition_level == "high"])
        if high_comp > len(hashtags) * 0.5:
            recommendations.append("Consider reducing high-competition hashtags and focus more on niche-specific tags.")
        
        # Engagement potential
        avg_engagement = sum(h.engagement_potential for h in hashtags) / len(hashtags)
        if avg_engagement < 60:
            recommendations.append("Add more engagement-focused hashtags like challenges, tips, or questions.")
        
        # Growth trends
        rising_count = len([h for h in hashtags if h.growth_trend == "rising"])
        if rising_count < len(hashtags) * 0.3:
            recommendations.append("Include more trending/rising hashtags to catch viral waves.")
        
        # Niche relevance
        avg_relevance = sum(h.niche_relevance for h in hashtags) / len(hashtags)
        if avg_relevance < 50:
            recommendations.append("Increase niche-specific hashtags to better target your audience.")
        
        return recommendations