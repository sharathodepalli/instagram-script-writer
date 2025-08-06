"""Enhanced Instagram scraper for discovering top-performing viral content."""

import os
import json
import time
import instaloader
from typing import Dict, Any, List, Optional, Tuple, Set
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import random
import re
from collections import defaultdict

try:
    from .config import logger
    from .hashtag_optimizer import HashtagOptimizer
    from .user_profile import UserProfileManager
    from .content_collector import ContentCollector
    from .domain_intelligence import DomainIntelligenceEngine
except ImportError:
    from src.config import logger
    from src.hashtag_optimizer import HashtagOptimizer
    from src.user_profile import UserProfileManager
    from src.content_collector import ContentCollector
    from src.domain_intelligence import DomainIntelligenceEngine


@dataclass
class ViralContent:
    """Represents viral content with performance metrics."""
    post_id: str
    shortcode: str
    caption: str
    hashtags: List[str]
    likes: int
    comments: int
    engagement_rate: float
    viral_score: float
    post_type: str  # photo, video, reel
    created_at: str
    language: str
    niche: str
    performance_factors: Dict[str, Any]


@dataclass
class ContentAnalysis:
    """Analysis of content performance patterns."""
    top_hashtags: List[str]
    common_themes: List[str]
    optimal_posting_times: List[str]
    engagement_patterns: Dict[str, float]
    viral_elements: List[str]
    content_recommendations: List[str]


class EnhancedContentScraper:
    """Advanced Instagram content scraper for viral content discovery."""
    
    def __init__(self):
        """Initialize the enhanced scraper."""
        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=True,
            compress_json=False
        )
        
        self.hashtag_optimizer = HashtagOptimizer()
        self.profile_manager = UserProfileManager()
        self.content_collector = ContentCollector()
        self.domain_intelligence = DomainIntelligenceEngine()
        
        # Enhanced niche-specific hashtag sets
        self.niche_hashtags = {
            "fitness": [
                "fitness", "workout", "gym", "health", "exercise", "fitlife", "bodybuilding",
                "yoga", "cardio", "strength", "nutrition", "wellness", "fitfam", "healthy"
            ],
            "food": [
                "food", "recipe", "cooking", "foodie", "delicious", "yummy", "homemade",
                "chef", "foodporn", "instafood", "foodblogger", "cooking", "baking"
            ],
            "lifestyle": [
                "lifestyle", "daily", "life", "inspiration", "motivation", "selfcare",
                "mindfulness", "productivity", "routine", "wellness", "happiness"
            ],
            "business": [
                "business", "entrepreneur", "startup", "success", "marketing", "money",
                "investing", "leadership", "productivity", "growth", "hustle"
            ],
            "tech": [
                "technology", "tech", "ai", "innovation", "digital", "software", "coding",
                "programming", "gadgets", "startup", "techreview"
            ],
            "fashion": [
                "fashion", "style", "outfit", "ootd", "fashion", "trendy", "stylish",
                "fashionista", "shopping", "beauty", "makeup", "skincare"
            ],
            "travel": [
                "travel", "wanderlust", "adventure", "explore", "vacation", "trip",
                "traveling", "travelgram", "destination", "backpacking"
            ],
            "entertainment": [
                "entertainment", "funny", "comedy", "memes", "viral", "trending",
                "music", "dance", "celebrity", "movies", "tv", "humor"
            ]
        }
        
        # Language-specific popular hashtags
        self.language_hashtags = {
            "english": ["trending", "viral", "fyp", "foryou", "explore", "amazing", "incredible"],
            "hindi": ["bollywood", "india", "hindi", "desi", "indian", "mumbai", "delhi"],
            "telugu": ["telugu", "tollywood", "hyderabad", "andhra", "telangana", "telugucinema"],
            "tamil": ["tamil", "kollywood", "chennai", "tamilnadu", "tamilcinema"],
            "spanish": ["español", "latino", "mexico", "argentina", "colombia", "chile"],
            "portuguese": ["brasil", "portuguese", "brazil", "rio", "saopaulo"],
            "french": ["france", "français", "paris", "french"],
            "german": ["deutsch", "germany", "berlin", "german"],
            "japanese": ["japan", "japanese", "tokyo", "anime", "manga"],
            "korean": ["korean", "korea", "seoul", "kpop", "kdrama"]
        }
        
        # Viral content indicators
        self.viral_indicators = [
            "challenge", "trend", "hack", "secret", "amazing", "incredible", "shocking",
            "unbelievable", "must", "never", "always", "everyone", "nobody", "instant",
            "immediately", "quick", "fast", "easy", "simple", "proven", "guaranteed"
        ]
    
    def discover_trending_hashtags(self, niche: str = None, language: str = "english", 
                                 max_hashtags: int = 50) -> List[str]:
        """
        Discover trending hashtags for a specific niche and language.
        
        Args:
            niche: Target niche (fitness, food, lifestyle, etc.)
            language: Target language
            max_hashtags: Maximum number of hashtags to return
            
        Returns:
            List of trending hashtags
        """
        logger.info(f"Discovering trending hashtags for niche: {niche}, language: {language}")
        
        trending_hashtags = set()
        
        # Get base hashtags for the niche
        if niche and niche in self.niche_hashtags:
            base_hashtags = self.niche_hashtags[niche]
        else:
            # Use all niches if no specific niche
            base_hashtags = []
            for tags in self.niche_hashtags.values():
                base_hashtags.extend(tags[:3])  # Top 3 from each niche
        
        # Add language-specific hashtags
        if language in self.language_hashtags:
            base_hashtags.extend(self.language_hashtags[language])
        
        # Generate trending variations
        for base_tag in base_hashtags:
            # Add base tag
            trending_hashtags.add(f"#{base_tag}")
            
            # Add trending variations
            trending_variations = [
                f"#{base_tag}trending",
                f"#{base_tag}viral",
                f"#{base_tag}challenge",
                f"#{base_tag}tips",
                f"#{base_tag}hacks",
                f"#{base_tag}secrets",
                f"#{base_tag}motivation",
                f"#{base_tag}inspiration"
            ]
            
            trending_hashtags.update(trending_variations)
        
        # Add time-based trending hashtags
        current_date = datetime.now()
        month = current_date.strftime("%B").lower()
        day = current_date.strftime("%A").lower()
        year = current_date.year
        
        time_based = [
            f"#{month}vibes",
            f"#{day}motivation",
            f"#{year}goals",
            f"#{year}trends",
            "#todaystrend",
            "#latesttrand",
            "#hottrend"
        ]
        
        trending_hashtags.update(time_based)
        
        # Convert to list and limit
        result = list(trending_hashtags)[:max_hashtags]
        logger.info(f"Discovered {len(result)} trending hashtags")
        return result
    
    def scrape_viral_content(self, hashtags: List[str], max_posts_per_tag: int = 20,
                           min_engagement_rate: float = 0.03) -> List[ViralContent]:
        """
        Scrape viral content from multiple hashtags.
        
        Args:
            hashtags: List of hashtags to scrape
            max_posts_per_tag: Maximum posts to analyze per hashtag
            min_engagement_rate: Minimum engagement rate to consider content viral
            
        Returns:
            List of ViralContent objects
        """
        logger.info(f"Scraping viral content from {len(hashtags)} hashtags")
        
        viral_content = []
        
        for hashtag in hashtags[:10]:  # Limit to prevent rate limiting
            try:
                hashtag_clean = hashtag.replace('#', '')
                logger.info(f"Scraping hashtag: #{hashtag_clean}")
                
                # Get hashtag posts
                try:
                    hashtag_obj = instaloader.Hashtag.from_name(self.loader.context, hashtag_clean)
                except Exception as e:
                    logger.warning(f"Could not load hashtag #{hashtag_clean}: {e}")
                    continue
                
                posts_analyzed = 0
                
                for post in hashtag_obj.get_posts():
                    if posts_analyzed >= max_posts_per_tag:
                        break
                    
                    try:
                        # Calculate engagement metrics
                        engagement_rate = (post.likes + post.comments) / max(post.owner_profile.followers, 1)
                        
                        # Only consider high-engagement content
                        if engagement_rate < min_engagement_rate:
                            posts_analyzed += 1
                            continue
                        
                        # Extract content data
                        viral_content_obj = self._analyze_post(post, hashtag_clean)
                        
                        if viral_content_obj:
                            viral_content.append(viral_content_obj)
                        
                        posts_analyzed += 1
                        
                        # Rate limiting
                        time.sleep(random.uniform(1, 3))
                        
                    except Exception as e:
                        logger.warning(f"Error analyzing post: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error scraping hashtag #{hashtag_clean}: {e}")
                continue
        
        # Sort by viral score
        viral_content.sort(key=lambda x: x.viral_score, reverse=True)
        
        logger.info(f"Found {len(viral_content)} viral content pieces")
        return viral_content
    
    def _analyze_post(self, post, hashtag: str) -> Optional[ViralContent]:
        """Analyze a post and create ViralContent object."""
        try:
            # Extract hashtags from caption
            caption = post.caption or ""
            extracted_hashtags = re.findall(r'#\w+', caption)
            
            # Calculate engagement rate
            engagement_rate = (post.likes + post.comments) / max(post.owner_profile.followers, 1)
            
            # Calculate viral score
            viral_score = self._calculate_viral_score(post, caption, extracted_hashtags)
            
            # Detect language (simplified)
            language = self._detect_language(caption)
            
            # Detect niche
            niche = self._detect_niche(caption, extracted_hashtags)
            
            # Analyze performance factors
            performance_factors = self._analyze_performance_factors(post, caption, extracted_hashtags)
            
            return ViralContent(
                post_id=str(post.mediaid),
                shortcode=post.shortcode,
                caption=caption,
                hashtags=extracted_hashtags,
                likes=post.likes,
                comments=post.comments,
                engagement_rate=engagement_rate,
                viral_score=viral_score,
                post_type="reel" if post.is_video else "photo",
                created_at=post.date_utc.isoformat(),
                language=language,
                niche=niche,
                performance_factors=performance_factors
            )
            
        except Exception as e:
            logger.error(f"Error analyzing post: {e}")
            return None
    
    def _calculate_viral_score(self, post, caption: str, hashtags: List[str]) -> float:
        """Calculate viral score based on multiple factors."""
        score = 0.0
        
        # Engagement factor (0-40 points)
        engagement_rate = (post.likes + post.comments) / max(post.owner_profile.followers, 1)
        engagement_score = min(40, engagement_rate * 10000)  # Scale engagement rate
        score += engagement_score
        
        # Viral indicators in caption (0-20 points)
        caption_lower = caption.lower()
        viral_words_found = sum(1 for word in self.viral_indicators if word in caption_lower)
        viral_word_score = min(20, viral_words_found * 3)
        score += viral_word_score
        
        # Hashtag effectiveness (0-20 points)
        hashtag_score = min(20, len(hashtags))  # More hashtags can mean better reach
        score += hashtag_score
        
        # Recency bonus (0-10 points)
        post_age_hours = (datetime.now() - post.date_utc.replace(tzinfo=None)).total_seconds() / 3600
        if post_age_hours < 24:
            recency_score = 10 * (1 - post_age_hours / 24)
        else:
            recency_score = 0
        score += recency_score
        
        # Comment-to-like ratio (0-10 points)
        if post.likes > 0:
            comment_ratio = post.comments / post.likes
            comment_score = min(10, comment_ratio * 100)  # High comment ratio is good
            score += comment_score
        
        return round(score, 2)
    
    def _detect_language(self, caption: str) -> str:
        """Detect language of the caption (simplified)."""
        caption_lower = caption.lower()
        
        # Check for language-specific words/patterns
        language_patterns = {
            "hindi": ["के", "में", "है", "का", "को", "से", "पर", "और", "या"],
            "telugu": ["లో", "కు", "తో", "మీ", "నా", "ఈ", "అ", "ఉ"],
            "tamil": ["உம்", "இல்", "என்", "அந்த", "இந்த", "க்", "ப்"],
            "spanish": ["de", "la", "el", "en", "y", "a", "que", "es", "se", "no"],
            "portuguese": ["de", "da", "do", "em", "para", "com", "uma", "um", "é", "não"],
            "french": ["de", "la", "le", "et", "à", "un", "il", "être", "et", "en"],
            "german": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich"]
        }
        
        for lang, patterns in language_patterns.items():
            if any(pattern in caption_lower for pattern in patterns):
                return lang
        
        return "english"  # default
    
    def _detect_niche(self, caption: str, hashtags: List[str]) -> str:
        """Detect content niche based on caption and hashtags."""
        text_to_analyze = (caption + " " + " ".join(hashtags)).lower()
        
        niche_scores = {}
        
        for niche, keywords in self.niche_hashtags.items():
            score = sum(1 for keyword in keywords if keyword in text_to_analyze)
            niche_scores[niche] = score
        
        # Return niche with highest score
        if niche_scores:
            return max(niche_scores, key=niche_scores.get)
        
        return "lifestyle"  # default
    
    def _analyze_performance_factors(self, post, caption: str, hashtags: List[str]) -> Dict[str, Any]:
        """Analyze factors contributing to post performance."""
        factors = {}
        
        # Caption analysis
        factors["caption_length"] = len(caption)
        factors["hashtag_count"] = len(hashtags)
        factors["has_question"] = "?" in caption
        factors["has_call_to_action"] = any(cta in caption.lower() for cta in 
                                           ["comment", "like", "share", "follow", "save", "tag"])
        
        # Viral elements
        viral_elements = [word for word in self.viral_indicators if word in caption.lower()]
        factors["viral_elements"] = viral_elements
        factors["viral_element_count"] = len(viral_elements)
        
        # Timing analysis
        post_hour = post.date_utc.hour
        factors["post_hour"] = post_hour
        factors["is_peak_time"] = post_hour in [12, 18, 19, 20, 21]  # Peak engagement hours
        
        # Engagement analysis
        factors["engagement_rate"] = (post.likes + post.comments) / max(post.owner_profile.followers, 1)
        factors["comment_rate"] = post.comments / max(post.likes, 1)
        
        return factors
    
    def analyze_viral_patterns(self, viral_content: List[ViralContent]) -> ContentAnalysis:
        """Analyze patterns in viral content to extract insights."""
        logger.info(f"Analyzing patterns in {len(viral_content)} viral posts")
        
        if not viral_content:
            return ContentAnalysis([], [], [], {}, [], [])
        
        # Analyze hashtags
        hashtag_counter = defaultdict(int)
        for content in viral_content:
            for hashtag in content.hashtags:
                hashtag_counter[hashtag.lower()] += 1
        
        top_hashtags = [tag for tag, count in 
                       sorted(hashtag_counter.items(), key=lambda x: x[1], reverse=True)[:20]]
        
        # Analyze common themes
        all_captions = " ".join([content.caption for content in viral_content]).lower()
        theme_words = []
        for word in all_captions.split():
            if len(word) > 4 and word not in ["this", "that", "with", "from", "they", "have", "were"]:
                theme_words.append(word)
        
        theme_counter = Counter(theme_words)
        common_themes = [word for word, count in theme_counter.most_common(15)]
        
        # Analyze posting times
        post_hours = [datetime.fromisoformat(content.created_at.replace('Z', '+00:00')).hour 
                     for content in viral_content]
        hour_counter = Counter(post_hours)
        optimal_times = [f"{hour:02d}:00" for hour, count in 
                        sorted(hour_counter.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        # Engagement patterns
        engagement_patterns = {
            "avg_engagement_rate": sum(c.engagement_rate for c in viral_content) / len(viral_content),
            "avg_likes": sum(c.likes for c in viral_content) / len(viral_content),
            "avg_comments": sum(c.comments for c in viral_content) / len(viral_content),
            "avg_viral_score": sum(c.viral_score for c in viral_content) / len(viral_content)
        }
        
        # Extract viral elements
        all_viral_elements = []
        for content in viral_content:
            all_viral_elements.extend(content.performance_factors.get("viral_elements", []))
        
        viral_element_counter = Counter(all_viral_elements)
        viral_elements = [element for element, count in viral_element_counter.most_common(10)]
        
        # Generate recommendations
        recommendations = self._generate_content_recommendations(
            viral_content, top_hashtags, common_themes, viral_elements, engagement_patterns
        )
        
        return ContentAnalysis(
            top_hashtags=top_hashtags,
            common_themes=common_themes,
            optimal_posting_times=optimal_times,
            engagement_patterns=engagement_patterns,
            viral_elements=viral_elements,
            content_recommendations=recommendations
        )
    
    def _generate_content_recommendations(self, viral_content: List[ViralContent], 
                                        top_hashtags: List[str], common_themes: List[str],
                                        viral_elements: List[str], 
                                        engagement_patterns: Dict[str, float]) -> List[str]:
        """Generate actionable content recommendations."""
        recommendations = []
        
        # Hashtag recommendations
        if top_hashtags:
            recommendations.append(f"Use these high-performing hashtags: {', '.join(top_hashtags[:10])}")
        
        # Theme recommendations
        if common_themes:
            recommendations.append(f"Focus on these trending themes: {', '.join(common_themes[:5])}")
        
        # Viral element recommendations
        if viral_elements:
            recommendations.append(f"Include viral words like: {', '.join(viral_elements[:5])}")
        
        # Engagement recommendations
        avg_engagement = engagement_patterns.get("avg_engagement_rate", 0)
        if avg_engagement > 0.05:
            recommendations.append("Target high-engagement content - viral posts show 5%+ engagement rates")
        
        # Call-to-action recommendation
        cta_posts = sum(1 for c in viral_content if c.performance_factors.get("has_call_to_action", False))
        if cta_posts > len(viral_content) * 0.7:
            recommendations.append("Include clear call-to-actions - 70%+ of viral posts have CTAs")
        
        # Caption length recommendation
        avg_caption_length = sum(c.performance_factors.get("caption_length", 0) for c in viral_content) / len(viral_content)
        recommendations.append(f"Optimal caption length: {int(avg_caption_length)} characters based on viral content")
        
        return recommendations
    
    def get_niche_specific_content(self, niche: str, language: str = "english", 
                                 max_content: int = 50) -> Tuple[List[ViralContent], ContentAnalysis]:
        """
        Get viral content and analysis for a specific niche.
        
        Args:
            niche: Target niche
            language: Target language
            max_content: Maximum content pieces to analyze
            
        Returns:
            Tuple of (viral_content_list, content_analysis)
        """
        logger.info(f"Getting niche-specific content for: {niche} ({language})")
        
        # Discover trending hashtags for the niche
        trending_hashtags = self.discover_trending_hashtags(niche, language, 20)
        
        # Scrape viral content
        viral_content = self.scrape_viral_content(trending_hashtags, max_posts_per_tag=10)
        
        # Filter by niche if needed
        niche_content = [c for c in viral_content if c.niche == niche][:max_content]
        
        if not niche_content:
            # If no niche-specific content, use top viral content
            niche_content = viral_content[:max_content]
        
        # Analyze patterns
        analysis = self.analyze_viral_patterns(niche_content)
        
        return niche_content, analysis
    
    def save_viral_content(self, viral_content: List[ViralContent], 
                          analysis: ContentAnalysis, output_dir: str = "data/viral_content"):
        """Save viral content and analysis to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save viral content
        content_file = output_path / f"viral_content_{timestamp}.json"
        content_data = [asdict(content) for content in viral_content]
        
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        # Save analysis
        analysis_file = output_path / f"content_analysis_{timestamp}.json"
        analysis_data = asdict(analysis)
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(viral_content)} viral content pieces and analysis to {output_dir}")
        
        return content_file, analysis_file
    
    def collect_and_store_domain_intelligence(self, niche: str, max_posts_per_account: int = 50) -> Dict[str, Any]:
        """
        Collect successful content and store in domain intelligence system.
        
        Args:
            niche: Target niche for collection
            max_posts_per_account: Maximum posts to collect per account
            
        Returns:
            Collection results and statistics
        """
        logger.info(f"🧠 Collecting domain intelligence for {niche} niche")
        
        try:
            # Use the content collector to gather successful content
            result = self.content_collector.collect_niche_content(niche, max_posts_per_account)
            
            # Get analysis of collected patterns
            if result.get("successful_content_stored", 0) > 0:
                analysis = self.domain_intelligence.analyze_niche_patterns(niche)
                result["pattern_analysis"] = analysis
            
            logger.info(f"✅ Domain intelligence collection complete for {niche}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to collect domain intelligence for {niche}: {e}")
            return {"error": str(e), "niche": niche}
    
    def collect_all_domain_intelligence(self, max_posts_per_account: int = 30) -> Dict[str, Any]:
        """
        Collect domain intelligence for all supported niches.
        
        Args:
            max_posts_per_account: Maximum posts to collect per account
            
        Returns:
            Complete collection results
        """
        logger.info("🚀 Starting comprehensive domain intelligence collection")
        
        # Use the content collector for comprehensive collection
        results = self.content_collector.collect_all_niches(max_posts_per_account)
        
        # Add scraper-specific enhancements
        results["scraper_enhanced"] = True
        results["collection_method"] = "enhanced_scraper_with_domain_intelligence"
        
        # Get overall statistics
        stats = self.domain_intelligence.get_niche_statistics()
        results["final_statistics"] = stats
        
        logger.info(f"🎉 Domain intelligence collection complete! {stats.get('total_successful_content', 0)} pieces stored")
        return results
    
    def get_domain_intelligence_for_generation(self, user_niche: str, topic: str, content_type: str = None) -> List[Dict[str, Any]]:
        """
        Get domain intelligence patterns for script generation.
        
        Args:
            user_niche: User's content niche
            topic: Topic for content generation
            content_type: Type of content (optional)
            
        Returns:
            List of relevant successful patterns
        """
        logger.info(f"🎯 Retrieving domain intelligence for {user_niche} - {topic}")
        
        try:
            patterns = self.domain_intelligence.get_domain_intelligence(
                niche=user_niche,
                topic=topic,
                content_type=content_type,
                top_k=5
            )
            
            logger.info(f"📊 Retrieved {len(patterns)} domain intelligence patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve domain intelligence: {e}")
            return []