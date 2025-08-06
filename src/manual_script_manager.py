"""Manual script upload and management system for reference and learning."""

import os
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
import re

try:
    from .config import logger, SCRIPTS_DIR
    from .viral_scorer import ViralPotentialScorer
    from .hashtag_optimizer import HashtagOptimizer
except ImportError:
    from src.config import logger, SCRIPTS_DIR
    from src.viral_scorer import ViralPotentialScorer
    from src.hashtag_optimizer import HashtagOptimizer


@dataclass
class UploadedScript:
    """Represents a manually uploaded script with analysis."""
    script_id: str
    title: str
    content: str
    topic: str
    performance_metrics: Dict[str, Any]
    viral_score: float
    hashtags: List[str]
    upload_date: str
    file_path: str
    analysis: Dict[str, Any]
    user_notes: str


class ManualScriptManager:
    """Manages manually uploaded scripts for reference and learning."""
    
    def __init__(self, upload_dir: str = "data/uploaded_scripts"):
        """Initialize the script manager."""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_dir = self.upload_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        
        # Initialize analyzers
        self.viral_scorer = ViralPotentialScorer()
        self.hashtag_optimizer = HashtagOptimizer()
        
        # Script pattern templates extracted from uploaded scripts
        self.learned_patterns = {
            "hooks": [],
            "structures": [],
            "cta_patterns": [],
            "style_elements": []
        }
    
    def upload_script_file(self, file_path: str, title: str = "", 
                          topic: str = "", user_notes: str = "") -> UploadedScript:
        """
        Upload and analyze a script file.
        
        Args:
            file_path: Path to the script file
            title: Script title (auto-generated if empty)
            topic: Script topic (auto-detected if empty)
            user_notes: User's notes about the script
            
        Returns:
            UploadedScript object with analysis
        """
        logger.info(f"Uploading script file: {file_path}")
        
        # Validate file
        source_path = Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Script file not found: {file_path}")
        
        # Read content
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
        except Exception as e:
            raise ValueError(f"Could not read script file: {e}")
        
        if not content:
            raise ValueError("Script file is empty")
        
        return self.upload_script_content(content, title, topic, user_notes, str(source_path))
    
    def upload_script_content(self, content: str, title: str = "", 
                            topic: str = "", user_notes: str = "",
                            original_path: str = "") -> UploadedScript:
        """
        Upload and analyze script content directly.
        
        Args:
            content: Script content
            title: Script title
            topic: Script topic
            user_notes: User's notes
            original_path: Original file path (if any)
            
        Returns:
            UploadedScript object with analysis
        """
        logger.info("Processing uploaded script content")
        
        # Generate script ID
        script_id = hashlib.md5(f"{content}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        # Auto-generate title if not provided
        if not title:
            title = self._generate_title_from_content(content)
        
        # Auto-detect topic if not provided
        if not topic:
            topic = self._detect_topic_from_content(content)
        
        # Analyze script
        analysis = self._analyze_uploaded_script(content, topic)
        
        # Extract performance metrics
        performance_metrics = self._extract_performance_indicators(content, analysis)
        
        # Extract hashtags
        hashtags = re.findall(r'#\w+', content)
        
        # Save script file
        script_filename = f"{script_id}_{title.replace(' ', '_')[:20]}.txt"
        script_path = self.upload_dir / script_filename
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Create uploaded script object
        uploaded_script = UploadedScript(
            script_id=script_id,
            title=title,
            content=content,
            topic=topic,
            performance_metrics=performance_metrics,
            viral_score=analysis["viral_score"].total_score,
            hashtags=hashtags,
            upload_date=datetime.now().isoformat(),
            file_path=str(script_path),
            analysis=asdict(analysis["viral_score"]),
            user_notes=user_notes
        )
        
        # Save metadata
        self._save_script_metadata(uploaded_script)
        
        # Learn patterns from the script
        self._learn_patterns_from_script(uploaded_script)
        
        # Copy to main scripts directory for ingestion
        self._copy_to_scripts_directory(uploaded_script)
        
        logger.info(f"Successfully uploaded script: {title} (ID: {script_id})")
        return uploaded_script
    
    def get_uploaded_scripts(self) -> List[UploadedScript]:
        """Get all uploaded scripts."""
        scripts = []
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                script = UploadedScript(**data)
                scripts.append(script)
                
            except Exception as e:
                logger.warning(f"Error loading script metadata {metadata_file}: {e}")
                continue
        
        # Sort by upload date (newest first)
        scripts.sort(key=lambda x: x.upload_date, reverse=True)
        return scripts
    
    def get_script_by_id(self, script_id: str) -> Optional[UploadedScript]:
        """Get a specific script by ID."""
        scripts = self.get_uploaded_scripts()
        for script in scripts:
            if script.script_id == script_id:
                return script
        return None
    
    def delete_script(self, script_id: str) -> bool:
        """Delete an uploaded script."""
        script = self.get_script_by_id(script_id)
        if not script:
            return False
        
        try:
            # Delete script file
            if Path(script.file_path).exists():
                Path(script.file_path).unlink()
            
            # Delete metadata file
            metadata_file = self.metadata_dir / f"{script_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            logger.info(f"Deleted script: {script.title} (ID: {script_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting script {script_id}: {e}")
            return False
    
    def analyze_script_collection(self) -> Dict[str, Any]:
        """Analyze patterns across all uploaded scripts."""
        scripts = self.get_uploaded_scripts()
        
        if not scripts:
            return {"message": "No uploaded scripts to analyze"}
        
        # Aggregate analysis
        total_scripts = len(scripts)
        avg_viral_score = sum(s.viral_score for s in scripts) / total_scripts
        
        # Topic distribution
        topic_counts = {}
        for script in scripts:
            topic = script.topic
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Performance distribution
        high_performers = [s for s in scripts if s.viral_score >= 80]
        medium_performers = [s for s in scripts if 60 <= s.viral_score < 80]
        low_performers = [s for s in scripts if s.viral_score < 60]
        
        # Common hashtags
        all_hashtags = []
        for script in scripts:
            all_hashtags.extend(script.hashtags)
        
        from collections import Counter
        top_hashtags = Counter(all_hashtags).most_common(20)
        
        # Best practices from high performers
        best_practices = self._extract_best_practices(high_performers)
        
        return {
            "summary": {
                "total_scripts": total_scripts,
                "average_viral_score": round(avg_viral_score, 1),
                "high_performers": len(high_performers),
                "medium_performers": len(medium_performers),
                "low_performers": len(low_performers)
            },
            "topic_distribution": dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)),
            "top_hashtags": [{"tag": tag, "count": count} for tag, count in top_hashtags],
            "performance_insights": {
                "high_performer_rate": round(len(high_performers) / total_scripts * 100, 1),
                "average_score_by_topic": self._calculate_average_scores_by_topic(scripts)
            },
            "best_practices": best_practices,
            "recommendations": self._generate_collection_recommendations(scripts)
        }
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights learned from uploaded scripts for improving generation."""
        scripts = self.get_uploaded_scripts()
        high_performers = [s for s in scripts if s.viral_score >= 75]
        
        if not high_performers:
            return {"message": "No high-performing scripts to learn from"}
        
        # Extract successful patterns
        successful_hooks = []
        successful_ctas = []
        successful_structures = []
        
        for script in high_performers:
            sections = self._extract_script_sections(script.content)
            
            if sections.get("hook"):
                successful_hooks.append(sections["hook"])
            
            if sections.get("cta"):
                successful_ctas.append(sections["cta"])
            
            successful_structures.append(self._analyze_structure(script.content))
        
        return {
            "successful_patterns": {
                "hooks": successful_hooks[:10],  # Top 10
                "ctas": successful_ctas[:10],
                "structures": successful_structures[:5]
            },
            "performance_factors": self._identify_success_factors(high_performers),
            "style_guidelines": self._extract_style_guidelines(high_performers),
            "optimization_tips": self._generate_optimization_tips(scripts)
        }
    
    def _generate_title_from_content(self, content: str) -> str:
        """Generate a title from script content."""
        # Extract hook or first line
        lines = content.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                # Clean and truncate
                title = re.sub(r'[^\w\s]', '', line.strip())
                return title[:50] + "..." if len(title) > 50 else title
        
        return f"Script_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _detect_topic_from_content(self, content: str) -> str:
        """Detect topic from script content."""
        content_lower = content.lower()
        
        # Topic keywords
        topic_keywords = {
            "fitness": ["workout", "exercise", "gym", "health", "fitness", "training"],
            "food": ["recipe", "cooking", "food", "meal", "nutrition", "ingredients"],
            "lifestyle": ["lifestyle", "daily", "routine", "life", "tips", "habits"],
            "business": ["business", "entrepreneur", "success", "money", "marketing"],
            "tech": ["technology", "tech", "digital", "app", "software", "innovation"],
            "fashion": ["fashion", "style", "outfit", "clothing", "trends", "beauty"],
            "travel": ["travel", "trip", "vacation", "destination", "adventure", "explore"],
            "entertainment": ["funny", "comedy", "entertainment", "music", "movie", "celebrity"]
        }
        
        # Count matches for each topic
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(content_lower.count(keyword) for keyword in keywords)
            topic_scores[topic] = score
        
        # Return topic with highest score
        if topic_scores:
            best_topic = max(topic_scores, key=topic_scores.get)
            if topic_scores[best_topic] > 0:
                return best_topic
        
        return "general"
    
    def _analyze_uploaded_script(self, content: str, topic: str) -> Dict[str, Any]:
        """Analyze uploaded script for viral potential and patterns."""
        # Get viral score
        viral_score = self.viral_scorer.calculate_viral_score(content, topic)
        
        # Additional analysis specific to uploaded scripts
        structure_analysis = self._analyze_structure(content)
        style_analysis = self._analyze_writing_style(content)
        
        return {
            "viral_score": viral_score,
            "structure": structure_analysis,
            "style": style_analysis
        }
    
    def _extract_performance_indicators(self, content: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance indicators from script content and analysis."""
        viral_score = analysis["viral_score"]
        
        return {
            "overall_score": viral_score.total_score,
            "grade": viral_score.grade,
            "hook_strength": viral_score.breakdown.get("hook_strength", 0),
            "emotional_appeal": viral_score.breakdown.get("emotional_trigger", 0),
            "call_to_action": viral_score.breakdown.get("call_to_action", 0),
            "shareability": viral_score.breakdown.get("shareability", 0),
            "hashtag_count": len(re.findall(r'#\w+', content)),
            "word_count": len(content.split()),
            "has_question": "?" in content,
            "has_numbers": bool(re.search(r'\d+', content))
        }
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structure of the script."""
        sections = self._extract_script_sections(content)
        
        return {
            "has_hook": bool(sections.get("hook")),
            "has_body": bool(sections.get("body")), 
            "has_cta": bool(sections.get("cta")),
            "has_caption": bool(sections.get("caption")),
            "has_hashtags": bool(sections.get("hashtags")),
            "has_visual_directions": bool(sections.get("visual")),
            "section_count": len([v for v in sections.values() if v]),
            "structure_completeness": len([v for v in sections.values() if v]) / 6
        }
    
    def _analyze_writing_style(self, content: str) -> Dict[str, Any]:
        """Analyze the writing style of the script."""
        # Basic style metrics
        sentences = content.split('.')
        words = content.split()
        
        # Count personal pronouns
        personal_pronouns = ['i', 'my', 'me', 'myself']
        personal_count = sum(content.lower().count(pronoun) for pronoun in personal_pronouns)
        
        # Count questions
        question_count = content.count('?')
        
        # Count exclamations
        exclamation_count = content.count('!')
        
        # Emotional words
        emotional_words = ['amazing', 'incredible', 'shocking', 'unbelievable', 'awesome', 'fantastic']
        emotion_count = sum(content.lower().count(word) for word in emotional_words)
        
        return {
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "personal_tone_score": personal_count / max(len(words), 1) * 100,
            "question_density": question_count / max(len(sentences), 1),
            "exclamation_density": exclamation_count / max(len(sentences), 1),
            "emotional_intensity": emotion_count / max(len(words), 1) * 100,
            "formality_level": "casual" if personal_count > 0 else "formal"
        }
    
    def _extract_script_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from script content."""
        sections = {}
        
        patterns = {
            "hook": r"HOOK:\s*(.*?)(?=\n\n|\nBODY:|\nCTA:|$)",
            "body": r"BODY:\s*(.*?)(?=\n\n|\nCTA:|\nCAPTION:|$)",
            "cta": r"CTA:\s*(.*?)(?=\n\n|\nCAPTION:|\nHASHTAGS:|$)",
            "caption": r"CAPTION:\s*(.*?)(?=\n\n|\nVISUAL:|\nHASHTAGS:|$)",
            "hashtags": r"HASHTAGS:\s*(.*?)(?=\n\n|$)",
            "visual": r"VISUAL DIRECTIONS?:\s*(.*?)(?=\n\n|\nHASHTAGS:|$)"
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section] = match.group(1).strip()
        
        return sections
    
    def _learn_patterns_from_script(self, script: UploadedScript):
        """Learn patterns from high-performing scripts."""
        if script.viral_score >= 70:  # Only learn from good scripts
            sections = self._extract_script_sections(script.content)
            
            # Learn hook patterns
            if sections.get("hook"):
                self.learned_patterns["hooks"].append({
                    "content": sections["hook"],
                    "score": script.viral_score,
                    "topic": script.topic
                })
            
            # Learn CTA patterns
            if sections.get("cta"):
                self.learned_patterns["cta_patterns"].append({
                    "content": sections["cta"],
                    "score": script.viral_score,
                    "topic": script.topic
                })
            
            # Keep only top patterns
            for pattern_type in self.learned_patterns:
                self.learned_patterns[pattern_type] = sorted(
                    self.learned_patterns[pattern_type], 
                    key=lambda x: x["score"], 
                    reverse=True
                )[:20]  # Keep top 20
    
    def _save_script_metadata(self, script: UploadedScript):
        """Save script metadata to file."""
        metadata_file = self.metadata_dir / f"{script.script_id}.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(script), f, indent=2, ensure_ascii=False)
    
    def _copy_to_scripts_directory(self, script: UploadedScript):
        """Copy script to main scripts directory for ingestion."""
        try:
            scripts_dir = Path(SCRIPTS_DIR)
            scripts_dir.mkdir(exist_ok=True)
            
            # Create filename
            filename = f"uploaded_{script.script_id}_{script.title.replace(' ', '_')[:20]}.txt"
            target_path = scripts_dir / filename
            
            # Copy content
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(script.content)
            
            logger.info(f"Copied script to scripts directory: {filename}")
            
        except Exception as e:
            logger.warning(f"Could not copy script to scripts directory: {e}")
    
    def _extract_best_practices(self, high_performers: List[UploadedScript]) -> List[str]:
        """Extract best practices from high-performing scripts."""
        practices = []
        
        if not high_performers:
            return practices
        
        # Analyze common elements
        avg_score = sum(s.viral_score for s in high_performers) / len(high_performers)
        practices.append(f"High performers average {avg_score:.1f} viral score")
        
        # Hook patterns
        hook_lengths = []
        for script in high_performers:
            sections = self._extract_script_sections(script.content)
            if sections.get("hook"):
                hook_lengths.append(len(sections["hook"].split()))
        
        if hook_lengths:
            avg_hook_length = sum(hook_lengths) / len(hook_lengths)
            practices.append(f"Optimal hook length: {avg_hook_length:.1f} words")
        
        # Hashtag usage
        hashtag_counts = [len(s.hashtags) for s in high_performers]
        if hashtag_counts:
            avg_hashtags = sum(hashtag_counts) / len(hashtag_counts)
            practices.append(f"High performers use ~{avg_hashtags:.0f} hashtags on average")
        
        return practices
    
    def _calculate_average_scores_by_topic(self, scripts: List[UploadedScript]) -> Dict[str, float]:
        """Calculate average viral scores by topic."""
        topic_scores = {}
        topic_counts = {}
        
        for script in scripts:
            topic = script.topic
            if topic not in topic_scores:
                topic_scores[topic] = 0
                topic_counts[topic] = 0
            
            topic_scores[topic] += script.viral_score
            topic_counts[topic] += 1
        
        # Calculate averages
        averages = {}
        for topic in topic_scores:
            averages[topic] = round(topic_scores[topic] / topic_counts[topic], 1)
        
        return averages
    
    def _identify_success_factors(self, high_performers: List[UploadedScript]) -> List[str]:
        """Identify common success factors in high-performing scripts."""
        factors = []
        
        if not high_performers:
            return factors
        
        # Analyze performance metrics
        total = len(high_performers)
        
        # Question usage
        with_questions = sum(1 for s in high_performers if s.performance_metrics.get("has_question", False))
        if with_questions / total > 0.7:
            factors.append(f"{with_questions/total:.0%} of high performers use questions")
        
        # Number usage
        with_numbers = sum(1 for s in high_performers if s.performance_metrics.get("has_numbers", False))
        if with_numbers / total > 0.6:
            factors.append(f"{with_numbers/total:.0%} of high performers include numbers")
        
        # Strong hooks
        strong_hooks = sum(1 for s in high_performers if s.performance_metrics.get("hook_strength", 0) > 15)
        if strong_hooks / total > 0.8:
            factors.append(f"{strong_hooks/total:.0%} of high performers have strong hooks")
        
        return factors
    
    def _extract_style_guidelines(self, high_performers: List[UploadedScript]) -> Dict[str, Any]:
        """Extract style guidelines from successful scripts."""
        if not high_performers:
            return {}
        
        # Aggregate style metrics
        total_scripts = len(high_performers)
        
        personal_tones = []
        formality_levels = []
        emotional_intensities = []
        
        for script in high_performers:
            # Re-analyze style (simplified version)
            style = self._analyze_writing_style(script.content)
            personal_tones.append(style.get("personal_tone_score", 0))
            formality_levels.append(style.get("formality_level", "casual"))
            emotional_intensities.append(style.get("emotional_intensity", 0))
        
        return {
            "avg_personal_tone": sum(personal_tones) / len(personal_tones) if personal_tones else 0,
            "preferred_formality": max(set(formality_levels), key=formality_levels.count) if formality_levels else "casual",
            "avg_emotional_intensity": sum(emotional_intensities) / len(emotional_intensities) if emotional_intensities else 0,
            "recommendations": [
                "Use personal pronouns for relatability",
                "Maintain casual, conversational tone",
                "Include emotional triggers strategically"
            ]
        }
    
    def _generate_collection_recommendations(self, scripts: List[UploadedScript]) -> List[str]:
        """Generate recommendations based on script collection analysis."""
        recommendations = []
        
        if not scripts:
            return ["Upload scripts to get personalized recommendations"]
        
        # Performance analysis
        high_performers = [s for s in scripts if s.viral_score >= 80]
        low_performers = [s for s in scripts if s.viral_score < 60]
        
        high_rate = len(high_performers) / len(scripts)
        
        if high_rate < 0.3:
            recommendations.append("Focus on improving hooks and emotional triggers to boost performance")
        
        if len(low_performers) > len(scripts) * 0.4:
            recommendations.append("Review CTA strategies and hashtag optimization for underperforming scripts")
        
        # Topic analysis
        topic_scores = self._calculate_average_scores_by_topic(scripts)
        if topic_scores:
            best_topic = max(topic_scores, key=topic_scores.get)
            recommendations.append(f"Your '{best_topic}' content performs best - consider focusing more on this niche")
        
        return recommendations
    
    def _generate_optimization_tips(self, scripts: List[UploadedScript]) -> List[str]:
        """Generate optimization tips based on script analysis."""
        tips = []
        
        if not scripts:
            return tips
        
        # Analyze common weaknesses
        low_hook_count = sum(1 for s in scripts if s.performance_metrics.get("hook_strength", 0) < 10)
        low_cta_count = sum(1 for s in scripts if s.performance_metrics.get("call_to_action", 0) < 5)
        
        if low_hook_count > len(scripts) * 0.5:
            tips.append("Strengthen your hooks with curiosity gaps and emotional triggers")
        
        if low_cta_count > len(scripts) * 0.5:
            tips.append("Add more engaging calls-to-action to boost interaction")
        
        # Hashtag analysis
        low_hashtag_count = sum(1 for s in scripts if len(s.hashtags) < 15)
        if low_hashtag_count > len(scripts) * 0.6:
            tips.append("Increase hashtag usage to 20-30 per script for better reach")
        
        return tips