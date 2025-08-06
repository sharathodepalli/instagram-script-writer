"""
Successful Content Data Collection System
Collects high-performing Instagram content and processes it for domain intelligence
"""

import re
import json
import time
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import instaloader
from langsmith import traceable

try:
    from .config import logger
    from .domain_intelligence import DomainIntelligenceEngine, SuccessfulContent
except ImportError:
    from src.config import logger
    from src.domain_intelligence import DomainIntelligenceEngine, SuccessfulContent

@dataclass
class TargetAccount:
    """Target account for content collection"""
    username: str
    niche: str
    follower_count: int
    avg_engagement_rate: float
    content_quality: str  # high, medium, low
    verified: bool = False

class ContentCollector:
    """Collects successful content from various sources"""
    
    def __init__(self):
        self.domain_intelligence = DomainIntelligenceEngine()
        
        # High-performing accounts by niche
        self.target_accounts = {
            "skincare": [
                TargetAccount("skincarebyhyram", "skincare", 4200000, 8.5, "high", True),
                TargetAccount("glowwithava", "skincare", 1800000, 12.3, "high", True),
                TargetAccount("drdavin", "skincare", 2100000, 7.8, "high", True),
                TargetAccount("skincarisma", "skincare", 890000, 9.2, "high", False),
                TargetAccount("labeautyologist", "skincare", 1200000, 10.1, "high", True)
            ],
            "fitness": [
                TargetAccount("mrandmrsmuscle", "fitness", 3500000, 9.8, "high", True),
                TargetAccount("syattfitness", "fitness", 1600000, 11.2, "high", True),
                TargetAccount("meowmeix", "fitness", 2800000, 8.9, "high", True),
                TargetAccount("bretcontreras1", "fitness", 1400000, 7.5, "high", True),
                TargetAccount("buildingbeast", "fitness", 950000, 10.3, "high", False)
            ],
            "business": [
                TargetAccount("garyvee", "business", 10500000, 6.2, "high", True),
                TargetAccount("theshaderoom", "business", 19800000, 8.9, "high", True),
                TargetAccount("tailopez", "business", 5200000, 5.8, "high", True),
                TargetAccount("johnkrasinski", "business", 3800000, 12.4, "high", True),
                TargetAccount("entrepreneur", "business", 16200000, 4.8, "high", True)
            ],
            "food": [
                TargetAccount("feelgoodfoodie", "food", 2300000, 11.8, "high", True),
                TargetAccount("healthyfitnessmeals", "food", 4100000, 9.3, "high", True),
                TargetAccount("thefoodbabe", "food", 1900000, 8.7, "high", True),
                TargetAccount("minimalistbaker", "food", 3200000, 10.5, "high", True),
                TargetAccount("cookingwithayeh", "food", 1500000, 13.2, "high", True)
            ]
        }
        
        # Content quality thresholds
        self.quality_thresholds = {
            "min_likes_ratio": 0.05,  # 5% of followers
            "min_engagement_rate": 5.0,
            "min_absolute_likes": 10000,
            "min_comments": 200,
            "max_days_old": 90
        }
        
        logger.info("📊 Content Collector initialized")
    
    @traceable
    def collect_niche_content(self, niche: str, max_posts_per_account: int = 50) -> Dict[str, Any]:
        """Collect successful content from target accounts in a specific niche"""
        if niche not in self.target_accounts:
            logger.warning(f"Niche '{niche}' not configured")
            return {"error": f"Niche '{niche}' not supported"}
        
        collected_content = []
        total_processed = 0
        total_stored = 0
        
        accounts = self.target_accounts[niche]
        logger.info(f"🎯 Collecting {niche} content from {len(accounts)} accounts")
        
        for account in accounts:
            try:
                content_batch = self._collect_from_account(
                    account, 
                    max_posts_per_account
                )
                
                for content in content_batch:
                    total_processed += 1
                    
                    # Quality check and store
                    if self._meets_collection_criteria(content, account):
                        successful_content = self._convert_to_successful_content(
                            content, account, niche
                        )
                        
                        if self.domain_intelligence.store_successful_content(successful_content):
                            total_stored += 1
                            collected_content.append({
                                "content_id": successful_content.content_id,
                                "account": account.username,
                                "viral_score": successful_content.viral_score,
                                "engagement_rate": successful_content.engagement_rate
                            })
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to collect from {account.username}: {e}")
                continue
        
        result = {
            "niche": niche,
            "accounts_processed": len(accounts),
            "total_posts_processed": total_processed,
            "successful_content_stored": total_stored,
            "collection_rate": f"{(total_stored/total_processed)*100:.1f}%" if total_processed > 0 else "0%",
            "collected_content": collected_content[:10],  # Sample
            "collected_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Collected {total_stored}/{total_processed} successful {niche} posts")
        return result
    
    def _collect_from_account(self, account: TargetAccount, max_posts: int) -> List[Dict[str, Any]]:
        """Collect posts from a specific Instagram account"""
        try:
            # Use instaloader for content collection
            loader = instaloader.Instaloader()
            
            # Get profile
            profile = instaloader.Profile.from_username(loader.context, account.username)
            
            collected_posts = []
            post_count = 0
            
            # Iterate through posts
            for post in profile.get_posts():
                if post_count >= max_posts:
                    break
                
                # Skip old posts
                if (datetime.now() - post.date).days > self.quality_thresholds["max_days_old"]:
                    continue
                
                # Extract post data
                post_data = {
                    "post_id": post.shortcode,
                    "caption": post.caption or "",
                    "likes": post.likes,
                    "comments": post.comments,
                    "date": post.date.isoformat(),
                    "is_video": post.is_video,
                    "video_duration": post.video_duration if post.is_video else 0,
                    "url": f"https://instagram.com/p/{post.shortcode}/",
                    "hashtags": post.caption_hashtags if post.caption else []
                }
                
                collected_posts.append(post_data)
                post_count += 1
                
                # Rate limiting
                time.sleep(1)
            
            return collected_posts
            
        except Exception as e:
            logger.error(f"Failed to collect from {account.username}: {e}")
            return []
    
    def _meets_collection_criteria(self, post_data: Dict[str, Any], account: TargetAccount) -> bool:
        """Check if post meets quality criteria for collection"""
        try:
            likes = post_data.get("likes", 0)
            comments = post_data.get("comments", 0)
            
            # Calculate engagement rate
            engagement_rate = ((likes + comments) / account.follower_count) * 100
            
            # Check all criteria
            criteria_met = (
                likes >= self.quality_thresholds["min_absolute_likes"] and
                engagement_rate >= self.quality_thresholds["min_engagement_rate"] and
                comments >= self.quality_thresholds["min_comments"] and
                (likes / account.follower_count) >= self.quality_thresholds["min_likes_ratio"]
            )
            
            return criteria_met
            
        except Exception as e:
            logger.error(f"Error checking criteria: {e}")
            return False
    
    def _convert_to_successful_content(
        self, 
        post_data: Dict[str, Any], 
        account: TargetAccount, 
        niche: str
    ) -> SuccessfulContent:
        """Convert scraped post data to SuccessfulContent object"""
        
        caption = post_data.get("caption", "")
        likes = post_data.get("likes", 0)
        comments = post_data.get("comments", 0)
        
        # Calculate metrics
        engagement_rate = ((likes + comments) / account.follower_count) * 100
        viral_score = min(100, (engagement_rate * 8) + (likes / 1000))  # Custom scoring
        
        # Extract script structure
        hook, body, cta = self._extract_script_structure(caption)
        
        # Determine content characteristics
        hook_type = self._classify_hook_type(hook)
        content_type = self._classify_content_type(caption)
        cta_type = self._classify_cta_type(cta)
        
        # Generate content ID
        content_id = f"scraped_{niche}_{hashlib.md5(f'{account.username}_{post_data.get('post_id')}'.encode()).hexdigest()[:8]}"
        
        return SuccessfulContent(
            content_id=content_id,
            script_text=caption,
            niche=niche,
            topic=self._extract_topic(caption),
            viral_score=viral_score,
            engagement_rate=engagement_rate,
            likes=likes,
            comments=comments,
            shares=max(10, int(likes * 0.02)),  # Estimate
            saves=max(5, int(likes * 0.03)),   # Estimate  
            views=max(likes * 10, 50000),       # Estimate
            hook_type=hook_type,
            content_type=content_type,
            cta_type=cta_type,
            script_length=len(caption.split()),
            video_duration=post_data.get("video_duration", 30),
            hook_pattern=hook[:100] if hook else "",
            body_structure="structured" if len(caption) > 100 else "simple",
            cta_pattern=cta[:50] if cta else "",
            hashtags=post_data.get("hashtags", []),
            creator_handle=account.username,
            source_platform="instagram",
            collected_date=datetime.now().isoformat(),
            verified_success=True  # All scraped content is verified successful
        )
    
    def _extract_script_structure(self, caption: str) -> tuple:
        """Extract hook, body, and CTA from caption"""
        if not caption:
            return "", "", ""
        
        lines = caption.split('\n')
        clean_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
        
        if len(clean_lines) == 0:
            return "", "", ""
        elif len(clean_lines) == 1:
            return clean_lines[0], "", ""
        elif len(clean_lines) == 2:
            return clean_lines[0], clean_lines[1], ""
        else:
            hook = clean_lines[0]
            body = ' '.join(clean_lines[1:-1])
            cta = clean_lines[-1]
            return hook, body, cta
    
    def _classify_hook_type(self, hook: str) -> str:
        """Classify the type of hook used"""
        if not hook:
            return "unknown"
        
        hook_lower = hook.lower()
        
        if any(q in hook_lower for q in ["?", "how", "what", "why", "when", "where", "which"]):
            return "question"
        elif any(stat in hook_lower for stat in ["study", "research", "found", "%", "people", "million"]):
            return "statistic"
        elif any(story in hook_lower for q in ["i", "my", "when i", "story", "experience"]):
            return "story"
        elif any(shock in hook_lower for shock in ["shocking", "secret", "hidden", "truth", "revealed"]):
            return "shocking"
        else:
            return "statement"
    
    def _classify_content_type(self, caption: str) -> str:
        """Classify the overall content type"""
        if not caption:
            return "unknown"
        
        caption_lower = caption.lower()
        
        if any(ed in caption_lower for ed in ["how to", "learn", "tip", "guide", "step", "tutorial"]):
            return "educational"
        elif any(insp in caption_lower for insp in ["inspire", "motivat", "believ", "dream", "achieve", "success"]):
            return "inspirational"
        elif any(ent in caption_lower for ent in ["funny", "laugh", "joke", "hilarious", "comedy"]):
            return "entertainment"
        elif any(story in caption_lower for story in ["story", "experience", "journey", "life", "remember"]):
            return "story"
        else:
            return "educational"
    
    def _classify_cta_type(self, cta: str) -> str:
        """Classify the call-to-action type"""
        if not cta:
            return "none"
        
        cta_lower = cta.lower()
        
        if any(engage in cta_lower for engage in ["comment", "share", "tag", "tell me", "thoughts"]):
            return "engagement"
        elif any(follow in cta_lower for follow in ["follow", "subscribe", "join", "connect"]):
            return "follow"
        elif any(conv in cta_lower for conv in ["link", "bio", "dm", "message", "buy", "shop"]):
            return "conversion"
        elif any(save in cta_lower for save in ["save", "bookmark", "remember"]):
            return "save"
        else:
            return "engagement"
    
    def _extract_topic(self, caption: str) -> str:
        """Extract the main topic from caption"""
        if not caption:
            return "general"
        
        # Simple topic extraction - first meaningful sentence
        sentences = caption.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            # Remove common prefixes and clean up
            first_sentence = re.sub(r'^(hey|hi|hello|so|today|this|here|let me|i want to|i\'m going to)', '', first_sentence.lower()).strip()
            return first_sentence[:50] if first_sentence else "general"
        
        return "general"
    
    @traceable
    def collect_all_niches(self, max_posts_per_account: int = 30) -> Dict[str, Any]:
        """Collect successful content from all configured niches"""
        results = {}
        total_stored = 0
        
        logger.info(f"🚀 Starting collection from all {len(self.target_accounts)} niches")
        
        for niche in self.target_accounts.keys():
            logger.info(f"📊 Processing {niche} niche...")
            result = self.collect_niche_content(niche, max_posts_per_account)
            results[niche] = result
            total_stored += result.get("successful_content_stored", 0)
            
            # Brief pause between niches
            time.sleep(5)
        
        summary = {
            "total_niches_processed": len(results),
            "total_successful_content_stored": total_stored,
            "niche_results": results,
            "collection_completed_at": datetime.now().isoformat()
        }
        
        logger.info(f"🎉 Collection complete! Stored {total_stored} successful pieces of content")
        return summary
    
    def get_collection_statistics(self) -> Dict[str, Any]:
        """Get statistics about collected content"""
        return self.domain_intelligence.get_niche_statistics()
    
    def analyze_collected_content(self, niche: str) -> Dict[str, Any]:
        """Analyze patterns in collected content for a niche"""
        return self.domain_intelligence.analyze_niche_patterns(niche)