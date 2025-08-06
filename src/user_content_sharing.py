"""
User-Driven Content Sharing System
Allows users to share their successful scripts and learn from community success patterns
"""

import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import streamlit as st
from langsmith import traceable

try:
    from .config import logger
    from .domain_intelligence import DomainIntelligenceEngine, SuccessfulContent
    from .intelligent_script_engine import UserPersona
except ImportError:
    from src.config import logger
    from src.domain_intelligence import DomainIntelligenceEngine, SuccessfulContent
    from src.intelligent_script_engine import UserPersona

@dataclass
class UserSharedContent:
    """Content shared by users with performance metrics"""
    content_id: str
    user_id: str
    user_name: str
    script_text: str
    topic: str
    niche: str
    
    # User-reported performance
    engagement_rate: float
    likes: int
    comments: int
    shares: int
    saves: int
    views: int
    video_duration: int
    
    # User experience data
    performance_description: str  # How well it performed
    audience_feedback: str       # What their audience said
    lessons_learned: str         # What they learned
    
    # Additional context
    hashtags_used: List[str]
    posting_time: str
    content_type: str
    target_audience: str
    
    # Verification and trust
    verification_score: float    # 0-100 based on user credibility
    community_votes: int        # Upvotes from other users
    reported_issues: int        # Reports of fake data
    
    # System metadata
    shared_at: str
    updated_at: str
    is_featured: bool = False
    is_verified: bool = False

class UserContentSharingSystem:
    """Manages user-generated successful content sharing"""
    
    def __init__(self):
        self.domain_intelligence = DomainIntelligenceEngine()
        self.shared_content_dir = Path("data/user_shared_content")
        self.shared_content_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing shared content
        self.shared_content = self._load_shared_content()
        
        # User credibility tracking
        self.user_credibility = self._load_user_credibility()
        
        logger.info("👥 User Content Sharing System initialized")
    
    def _load_shared_content(self) -> Dict[str, UserSharedContent]:
        """Load previously shared content"""
        shared_content = {}
        
        for file_path in self.shared_content_dir.glob("shared_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content = UserSharedContent(**data)
                    shared_content[content.content_id] = content
            except Exception as e:
                logger.warning(f"Failed to load shared content {file_path}: {e}")
        
        logger.info(f"📚 Loaded {len(shared_content)} shared content pieces")
        return shared_content
    
    def _load_user_credibility(self) -> Dict[str, Dict[str, Any]]:
        """Load user credibility scores"""
        credibility_file = self.shared_content_dir / "user_credibility.json"
        
        if credibility_file.exists():
            try:
                with open(credibility_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load user credibility: {e}")
        
        return {}
    
    def _save_user_credibility(self):
        """Save user credibility scores"""
        credibility_file = self.shared_content_dir / "user_credibility.json"
        
        try:
            with open(credibility_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_credibility, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user credibility: {e}")
    
    @traceable
    def share_successful_content(
        self,
        user_id: str,
        user_name: str,
        script_text: str,
        topic: str,
        niche: str,
        performance_data: Dict[str, Any],
        user_experience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Allow user to share their successful content"""
        
        try:
            # Generate content ID
            content_id = f"user_shared_{user_id}_{hashlib.md5(script_text.encode()).hexdigest()[:8]}"
            
            # Calculate verification score based on user credibility
            verification_score = self._calculate_verification_score(user_id, performance_data)
            
            # Create shared content object
            shared_content = UserSharedContent(
                content_id=content_id,
                user_id=user_id,
                user_name=user_name,
                script_text=script_text,
                topic=topic,
                niche=niche,
                engagement_rate=performance_data.get("engagement_rate", 0),
                likes=performance_data.get("likes", 0),
                comments=performance_data.get("comments", 0),
                shares=performance_data.get("shares", 0),
                saves=performance_data.get("saves", 0),
                views=performance_data.get("views", 0),
                video_duration=performance_data.get("video_duration", 30),
                performance_description=user_experience.get("performance_description", ""),
                audience_feedback=user_experience.get("audience_feedback", ""),
                lessons_learned=user_experience.get("lessons_learned", ""),
                hashtags_used=performance_data.get("hashtags", []),
                posting_time=performance_data.get("posting_time", ""),
                content_type=performance_data.get("content_type", "educational"),
                target_audience=user_experience.get("target_audience", ""),
                verification_score=verification_score,
                community_votes=0,
                reported_issues=0,
                shared_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                is_featured=verification_score > 80,
                is_verified=verification_score > 90
            )
            
            # Save shared content
            self._save_shared_content(shared_content)
            
            # Store in shared content dictionary
            self.shared_content[content_id] = shared_content
            
            # If high quality, add to domain intelligence
            if verification_score > 70:
                successful_content = self._convert_to_domain_intelligence(shared_content)
                self.domain_intelligence.store_successful_content(successful_content)
                logger.info(f"✅ Added high-quality shared content to domain intelligence")
            
            # Update user credibility
            self._update_user_credibility(user_id, shared_content)
            
            result = {
                "success": True,
                "content_id": content_id,
                "verification_score": verification_score,
                "added_to_domain_intelligence": verification_score > 70,
                "is_featured": shared_content.is_featured,
                "is_verified": shared_content.is_verified,
                "message": self._get_sharing_message(shared_content)
            }
            
            logger.info(f"👥 User {user_name} shared successful content: {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to share user content: {e}")
            return {"success": False, "error": str(e)}
    
    def _save_shared_content(self, content: UserSharedContent):
        """Save shared content to file"""
        file_path = self.shared_content_dir / f"shared_{content.content_id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(content), f, indent=2, ensure_ascii=False)
    
    def _calculate_verification_score(self, user_id: str, performance_data: Dict[str, Any]) -> float:
        """Calculate verification score for shared content"""
        score = 50.0  # Base score
        
        # User credibility factor
        user_cred = self.user_credibility.get(user_id, {})
        credibility_score = user_cred.get("credibility_score", 50)
        score += (credibility_score - 50) * 0.5
        
        # Performance data consistency
        engagement_rate = performance_data.get("engagement_rate", 0)
        likes = performance_data.get("likes", 0)
        views = performance_data.get("views", 1)
        
        # Check if engagement rate matches likes/views ratio
        calculated_engagement = (likes / views) * 100 if views > 0 else 0
        consistency = min(100, abs(engagement_rate - calculated_engagement))
        
        if consistency < 10:  # Very consistent
            score += 20
        elif consistency < 25:  # Somewhat consistent
            score += 10
        else:  # Inconsistent
            score -= 10
        
        # Performance quality
        if engagement_rate > 10:
            score += 25
        elif engagement_rate > 5:
            score += 15
        elif engagement_rate > 2:
            score += 5
        
        # Minimum viable metrics
        if likes < 100 or views < 1000:
            score -= 20
        
        return max(0, min(100, score))
    
    def _convert_to_domain_intelligence(self, shared_content: UserSharedContent) -> SuccessfulContent:
        """Convert shared content to domain intelligence format"""
        return SuccessfulContent(
            content_id=f"shared_{shared_content.content_id}",
            script_text=shared_content.script_text,
            niche=shared_content.niche,
            topic=shared_content.topic,
            viral_score=min(100, shared_content.verification_score + (shared_content.engagement_rate * 5)),
            engagement_rate=shared_content.engagement_rate,
            likes=shared_content.likes,
            comments=shared_content.comments,
            shares=shared_content.shares,
            saves=shared_content.saves,
            views=shared_content.views,
            hook_type=self._classify_hook_type(shared_content.script_text),
            content_type=shared_content.content_type,
            cta_type=self._classify_cta_type(shared_content.script_text),
            script_length=len(shared_content.script_text.split()),
            video_duration=shared_content.video_duration,
            hook_pattern=shared_content.script_text[:100],
            body_structure="user_verified",
            cta_pattern="user_verified",
            hashtags=shared_content.hashtags_used,
            creator_handle=f"user_{shared_content.user_name}",
            source_platform="user_shared",
            collected_date=shared_content.shared_at,
            verified_success=True
        )
    
    def _classify_hook_type(self, script: str) -> str:
        """Classify hook type from script"""
        if not script:
            return "unknown"
        
        first_line = script.split('\n')[0].lower()
        
        if any(q in first_line for q in ["?", "how", "what", "why", "when"]):
            return "question"
        elif any(stat in first_line for stat in ["study", "research", "%", "found"]):
            return "statistic"
        elif any(story in first_line for story in ["i", "my", "story", "when i"]):
            return "story"
        else:
            return "statement"
    
    def _classify_cta_type(self, script: str) -> str:
        """Classify CTA type from script"""
        if not script:
            return "none"
        
        script_lower = script.lower()
        
        if any(engage in script_lower for engage in ["comment", "share", "tag", "tell me"]):
            return "engagement"
        elif any(follow in script_lower for follow in ["follow", "subscribe"]):
            return "follow"
        elif any(conv in script_lower for conv in ["link", "bio", "dm", "buy"]):
            return "conversion"
        else:
            return "engagement"
    
    def _update_user_credibility(self, user_id: str, content: UserSharedContent):
        """Update user credibility based on shared content"""
        if user_id not in self.user_credibility:
            self.user_credibility[user_id] = {
                "credibility_score": 50,
                "content_shared": 0,
                "total_engagement": 0,
                "avg_verification_score": 50,
                "last_updated": datetime.now().isoformat()
            }
        
        user_cred = self.user_credibility[user_id]
        user_cred["content_shared"] += 1
        user_cred["total_engagement"] += content.likes + content.comments
        
        # Update average verification score
        current_avg = user_cred.get("avg_verification_score", 50)
        new_avg = (current_avg + content.verification_score) / 2
        user_cred["avg_verification_score"] = new_avg
        
        # Update credibility score
        if content.verification_score > 80:
            user_cred["credibility_score"] = min(100, user_cred["credibility_score"] + 5)
        elif content.verification_score < 30:
            user_cred["credibility_score"] = max(0, user_cred["credibility_score"] - 10)
        
        user_cred["last_updated"] = datetime.now().isoformat()
        
        # Save updated credibility
        self._save_user_credibility()
    
    def _get_sharing_message(self, content: UserSharedContent) -> str:
        """Generate message for user after sharing"""
        if content.is_verified:
            return "🌟 Excellent! Your content has been verified and featured in our community showcase!"
        elif content.is_featured:
            return "⭐ Great content! Your script is featured and added to our domain intelligence."
        elif content.verification_score > 60:
            return "✅ Thank you for sharing! Your content has been added to the community library."
        else:
            return "📝 Content shared! Consider adding more performance details to help others learn."
    
    def get_community_content(self, niche: str = None, top_k: int = 20) -> List[Dict[str, Any]]:
        """Get top community-shared content"""
        content_list = list(self.shared_content.values())
        
        # Filter by niche if specified
        if niche:
            content_list = [c for c in content_list if c.niche.lower() == niche.lower()]
        
        # Sort by verification score and community votes
        content_list.sort(
            key=lambda x: (x.verification_score, x.community_votes, x.engagement_rate),
            reverse=True
        )
        
        # Return top content with essential information
        result = []
        for content in content_list[:top_k]:
            result.append({
                "content_id": content.content_id,
                "user_name": content.user_name,
                "topic": content.topic,
                "niche": content.niche,
                "script_preview": content.script_text[:200] + "...",
                "verification_score": content.verification_score,
                "engagement_rate": content.engagement_rate,
                "performance_description": content.performance_description,
                "is_featured": content.is_featured,
                "is_verified": content.is_verified,
                "shared_at": content.shared_at
            })
        
        return result
    
    def vote_on_content(self, content_id: str, user_id: str, vote: str) -> Dict[str, Any]:
        """Allow users to vote on shared content"""
        if content_id not in self.shared_content:
            return {"success": False, "error": "Content not found"}
        
        if vote not in ["up", "down", "report"]:
            return {"success": False, "error": "Invalid vote type"}
        
        content = self.shared_content[content_id]
        
        if vote == "up":
            content.community_votes += 1
        elif vote == "report":
            content.reported_issues += 1
        
        # Update verification score based on community feedback
        if content.community_votes > 10:
            bonus = min(10, content.community_votes / 2)
            content.verification_score = min(100, content.verification_score + bonus)
        
        if content.reported_issues > 5:
            penalty = content.reported_issues * 2
            content.verification_score = max(0, content.verification_score - penalty)
        
        content.updated_at = datetime.now().isoformat()
        
        # Save updated content
        self._save_shared_content(content)
        
        return {
            "success": True,
            "new_votes": content.community_votes,
            "new_verification_score": content.verification_score
        }
    
    def get_user_contributions(self, user_id: str) -> Dict[str, Any]:
        """Get user's contribution statistics"""
        user_content = [c for c in self.shared_content.values() if c.user_id == user_id]
        
        if not user_content:
            return {"error": "No contributions found"}
        
        total_engagement = sum(c.likes + c.comments for c in user_content)
        avg_verification = sum(c.verification_score for c in user_content) / len(user_content)
        featured_count = sum(1 for c in user_content if c.is_featured)
        
        return {
            "user_id": user_id,
            "total_contributions": len(user_content),
            "total_engagement": total_engagement,
            "average_verification_score": avg_verification,
            "featured_content": featured_count,
            "credibility_score": self.user_credibility.get(user_id, {}).get("credibility_score", 50),
            "recent_contributions": [
                {
                    "topic": c.topic,
                    "verification_score": c.verification_score,
                    "engagement_rate": c.engagement_rate,
                    "shared_at": c.shared_at
                }
                for c in sorted(user_content, key=lambda x: x.shared_at, reverse=True)[:5]
            ]
        }
    
    def get_niche_insights(self, niche: str) -> Dict[str, Any]:
        """Get insights from community shared content for a niche"""
        niche_content = [c for c in self.shared_content.values() if c.niche.lower() == niche.lower()]
        
        if not niche_content:
            return {"error": f"No community content found for {niche}"}
        
        # Calculate insights
        avg_engagement = sum(c.engagement_rate for c in niche_content) / len(niche_content)
        top_topics = {}
        all_hashtags = []
        
        for content in niche_content:
            # Count topics
            topic = content.topic.lower()
            top_topics[topic] = top_topics.get(topic, 0) + 1
            
            # Collect hashtags
            all_hashtags.extend(content.hashtags_used)
        
        # Get top hashtags
        hashtag_counts = {}
        for tag in all_hashtags:
            hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
        
        top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_topics_sorted = sorted(top_topics.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "niche": niche,
            "total_community_content": len(niche_content),
            "average_engagement_rate": avg_engagement,
            "top_topics": [topic for topic, count in top_topics_sorted],
            "top_hashtags": [tag for tag, count in top_hashtags],
            "success_patterns": [
                c.lessons_learned for c in niche_content 
                if c.lessons_learned and c.verification_score > 80
            ][:5]
        }