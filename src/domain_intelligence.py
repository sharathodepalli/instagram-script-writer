"""
Domain Intelligence System
Stores and retrieves high-performing content patterns from Pinecone for niche-specific expertise
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from langsmith import traceable

try:
    from .config import PINECONE_API_KEY, PINECONE_INDEX, PINECONE_HOST, logger
except ImportError:
    from src.config import PINECONE_API_KEY, PINECONE_INDEX, PINECONE_HOST, logger

@dataclass
class SuccessfulContent:
    """High-performing content with rich metadata"""
    content_id: str
    script_text: str
    niche: str
    topic: str
    
    # Performance metrics
    viral_score: float  # 0-100
    engagement_rate: float  # percentage
    likes: int
    comments: int
    shares: int
    saves: int
    views: int
    
    # Content analysis
    hook_type: str  # question, statement, story, statistic
    content_type: str  # educational, entertainment, inspirational
    cta_type: str  # engagement, conversion, follow
    script_length: int  # word count
    video_duration: int  # seconds
    
    # Pattern metadata
    hook_pattern: str
    body_structure: str
    cta_pattern: str
    hashtags: List[str]
    
    # Source information
    creator_handle: str
    source_platform: str
    collected_date: str
    verified_success: bool  # User-verified or scraped
    
    created_at: str = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class DomainIntelligenceEngine:
    """Manages domain-specific content intelligence using Pinecone"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_name = PINECONE_INDEX
        self.namespace_prefix = "domain_intelligence"
        
        # Initialize Pinecone
        self._initialize_pinecone()
        
        # Content quality thresholds
        self.quality_thresholds = {
            "min_viral_score": 70.0,
            "min_engagement_rate": 5.0,
            "min_likes": 1000,
            "min_views": 10000
        }
        
        logger.info("🧠 Domain Intelligence Engine initialized")
    
    def _initialize_pinecone(self):
        """Initialize Pinecone connection"""
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            
            # Get index
            self.index = self.pc.Index(self.index_name)
            logger.info("✅ Connected to Pinecone for domain intelligence")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Pinecone: {e}")
            raise
    
    @traceable
    def store_successful_content(self, content: SuccessfulContent) -> bool:
        """Store high-performing content in Pinecone"""
        try:
            # Quality check
            if not self._meets_quality_threshold(content):
                logger.warning(f"Content {content.content_id} doesn't meet quality thresholds")
                return False
            
            # Generate embedding
            embedding = self.embedding_model.encode(content.script_text).tolist()
            
            # Prepare metadata
            metadata = {
                "niche": content.niche,
                "topic": content.topic,
                "viral_score": content.viral_score,
                "engagement_rate": content.engagement_rate,
                "hook_type": content.hook_type,
                "content_type": content.content_type,
                "cta_type": content.cta_type,
                "script_length": content.script_length,
                "video_duration": content.video_duration,
                "creator_handle": content.creator_handle,
                "source_platform": content.source_platform,
                "verified_success": content.verified_success,
                "created_at": content.created_at,
                "likes": content.likes,
                "comments": content.comments,
                "shares": content.shares,
                "saves": content.saves,
                "views": content.views
            }
            
            # Store in Pinecone
            namespace = f"{self.namespace_prefix}_{content.niche}"
            
            self.index.upsert(
                vectors=[(content.content_id, embedding, metadata)],
                namespace=namespace
            )
            
            logger.info(f"✅ Stored successful content {content.content_id} in {content.niche} domain")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store content {content.content_id}: {e}")
            return False
    
    @traceable
    def get_domain_intelligence(
        self, 
        niche: str, 
        topic: str, 
        content_type: str = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve high-performing content patterns for a specific domain and topic"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(topic).tolist()
            
            # Build filter
            filter_conditions = {
                "viral_score": {"$gte": self.quality_thresholds["min_viral_score"]}
            }
            
            if content_type:
                filter_conditions["content_type"] = content_type
            
            # Search in domain-specific namespace
            namespace = f"{self.namespace_prefix}_{niche}"
            
            results = self.index.query(
                vector=query_embedding,
                filter=filter_conditions,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace
            )
            
            # Process results
            domain_patterns = []
            for match in results.matches:
                domain_patterns.append({
                    "content_id": match.id,
                    "similarity_score": match.score,
                    "metadata": match.metadata,
                    "relevance": "high" if match.score > 0.8 else "medium" if match.score > 0.6 else "low"
                })
            
            logger.info(f"🎯 Retrieved {len(domain_patterns)} domain patterns for {niche} - {topic}")
            return domain_patterns
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve domain intelligence: {e}")
            return []
    
    @traceable
    def analyze_niche_patterns(self, niche: str) -> Dict[str, Any]:
        """Analyze successful patterns within a specific niche"""
        try:
            namespace = f"{self.namespace_prefix}_{niche}"
            
            # Get high-performing content stats
            stats = self.index.describe_index_stats()
            niche_stats = stats.namespaces.get(namespace, {})
            
            if not niche_stats:
                return {"error": f"No data found for niche: {niche}"}
            
            # Sample some content for pattern analysis
            sample_results = self.index.query(
                vector=[0.0] * 384,  # Dummy vector for sampling
                filter={"viral_score": {"$gte": 80}},
                top_k=50,
                include_metadata=True,
                namespace=namespace
            )
            
            # Analyze patterns
            hook_types = {}
            content_types = {}
            cta_types = {}
            avg_metrics = {
                "viral_score": 0,
                "engagement_rate": 0,
                "script_length": 0
            }
            
            for match in sample_results.matches:
                meta = match.metadata
                
                # Count patterns
                hook_types[meta.get("hook_type", "unknown")] = hook_types.get(meta.get("hook_type", "unknown"), 0) + 1
                content_types[meta.get("content_type", "unknown")] = content_types.get(meta.get("content_type", "unknown"), 0) + 1
                cta_types[meta.get("cta_type", "unknown")] = cta_types.get(meta.get("cta_type", "unknown"), 0) + 1
                
                # Calculate averages
                avg_metrics["viral_score"] += meta.get("viral_score", 0)
                avg_metrics["engagement_rate"] += meta.get("engagement_rate", 0)
                avg_metrics["script_length"] += meta.get("script_length", 0)
            
            # Finalize averages
            count = len(sample_results.matches)
            if count > 0:
                for key in avg_metrics:
                    avg_metrics[key] = avg_metrics[key] / count
            
            analysis = {
                "niche": niche,
                "total_successful_content": niche_stats.get("vector_count", 0),
                "top_hook_types": sorted(hook_types.items(), key=lambda x: x[1], reverse=True)[:3],
                "top_content_types": sorted(content_types.items(), key=lambda x: x[1], reverse=True)[:3],
                "top_cta_types": sorted(cta_types.items(), key=lambda x: x[1], reverse=True)[:3],
                "average_metrics": avg_metrics,
                "analyzed_at": datetime.now().isoformat()
            }
            
            logger.info(f"📊 Analyzed {niche} niche patterns: {count} samples")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze niche patterns: {e}")
            return {"error": str(e)}
    
    def _meets_quality_threshold(self, content: SuccessfulContent) -> bool:
        """Check if content meets quality thresholds for storage"""
        return (
            content.viral_score >= self.quality_thresholds["min_viral_score"] and
            content.engagement_rate >= self.quality_thresholds["min_engagement_rate"] and
            content.likes >= self.quality_thresholds["min_likes"] and
            content.views >= self.quality_thresholds["min_views"]
        )
    
    def get_niche_statistics(self) -> Dict[str, Any]:
        """Get statistics across all stored niches"""
        try:
            stats = self.index.describe_index_stats()
            namespaces = stats.namespaces
            
            niche_stats = {}
            for namespace, data in namespaces.items():
                if namespace.startswith(self.namespace_prefix):
                    niche_name = namespace.replace(f"{self.namespace_prefix}_", "")
                    niche_stats[niche_name] = {
                        "content_count": data.vector_count,
                        "last_updated": datetime.now().isoformat()
                    }
            
            return {
                "total_niches": len(niche_stats),
                "niche_breakdown": niche_stats,
                "total_successful_content": sum(data["content_count"] for data in niche_stats.values())
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get niche statistics: {e}")
            return {"error": str(e)}
    
    @traceable  
    def store_user_successful_content(
        self, 
        script: str, 
        user_niche: str, 
        topic: str,
        performance_data: Dict[str, Any],
        user_id: str
    ) -> bool:
        """Store user-reported successful content"""
        try:
            content_id = f"user_{user_id}_{hashlib.md5(script.encode()).hexdigest()[:8]}"
            
            # Create SuccessfulContent object
            successful_content = SuccessfulContent(
                content_id=content_id,
                script_text=script,
                niche=user_niche,
                topic=topic,
                viral_score=performance_data.get("viral_score", 75),
                engagement_rate=performance_data.get("engagement_rate", 6.0),
                likes=performance_data.get("likes", 1500),
                comments=performance_data.get("comments", 100),
                shares=performance_data.get("shares", 50),
                saves=performance_data.get("saves", 75),
                views=performance_data.get("views", 15000),
                hook_type=performance_data.get("hook_type", "question"),
                content_type=performance_data.get("content_type", "educational"),
                cta_type=performance_data.get("cta_type", "engagement"),
                script_length=len(script.split()),
                video_duration=performance_data.get("video_duration", 30),
                hook_pattern=script.split('\n')[0] if script else "",
                body_structure="structured",
                cta_pattern=performance_data.get("cta_pattern", "question_based"),
                hashtags=performance_data.get("hashtags", []),
                creator_handle=f"user_{user_id}",
                source_platform="user_upload",
                collected_date=datetime.now().isoformat(),
                verified_success=True  # User-verified content is high trust
            )
            
            return self.store_successful_content(successful_content)
            
        except Exception as e:
            logger.error(f"❌ Failed to store user successful content: {e}")
            return False