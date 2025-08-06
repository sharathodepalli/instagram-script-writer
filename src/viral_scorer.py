"""Viral potential scoring system for optimizing content reach."""

import re
import math
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import Counter

try:
    from .config import logger
    from .user_profile import UserProfileManager
    from .hashtag_optimizer import HashtagOptimizer
except ImportError:
    from src.config import logger
    from src.user_profile import UserProfileManager
    from src.hashtag_optimizer import HashtagOptimizer


@dataclass
class ViralScore:
    """Viral potential score with detailed breakdown."""
    total_score: float
    max_score: float
    percentage: float
    grade: str  # A+, A, B+, B, C+, C, D
    breakdown: Dict[str, float]
    recommendations: List[str]
    viral_elements: List[str]
    missing_elements: List[str]


class ViralPotentialScorer:
    """Analyzes and scores content for viral potential."""
    
    def __init__(self):
        """Initialize the viral scorer."""
        self.profile_manager = UserProfileManager()
        self.hashtag_optimizer = HashtagOptimizer()
        
        # Viral content patterns and weights
        self.scoring_weights = {
            "hook_strength": 20,        # Strong opening hook
            "emotional_trigger": 18,    # Emotional response triggers
            "curiosity_gap": 15,        # Creates curiosity/intrigue
            "value_proposition": 12,    # Clear value to audience
            "call_to_action": 10,       # Strong CTA
            "hashtag_strategy": 8,      # Optimal hashtag usage
            "timing_relevance": 7,      # Current trends/timing
            "shareability": 6,          # Likely to be shared
            "authenticity": 4           # Genuine/authentic feel
        }
        
        # Viral triggers and emotional elements
        self.emotional_triggers = {
            "curiosity": ["secret", "hidden", "nobody", "everyone", "never", "always", "truth", "reality"],
            "urgency": ["now", "today", "immediately", "quick", "fast", "instant", "asap", "hurry"],
            "exclusivity": ["exclusive", "only", "special", "limited", "rare", "unique", "first"],
            "surprise": ["shocking", "unbelievable", "amazing", "incredible", "mind-blowing", "unexpected"],
            "fear": ["mistake", "wrong", "avoid", "danger", "warning", "careful", "beware"],
            "desire": ["want", "need", "must", "essential", "important", "crucial", "vital"],
            "social_proof": ["everyone", "millions", "thousands", "popular", "trending", "viral"],
            "achievement": ["success", "win", "achieve", "accomplish", "master", "expert", "pro"]
        }
        
        # Hook patterns that perform well
        self.viral_hooks = [
            r".*\bsecret\b.*\bthat\b.*",
            r".*\bnobody\b.*\btells\b.*",
            r".*\bwant to\b.*\bbut\b.*",
            r".*\bstop\b.*\bdoing\b.*",
            r".*\bmistake\b.*\bmaking\b.*",
            r".*\bthings?\b.*\bchanged\b.*",
            r".*\bwhy\b.*\bis\b.*",
            r".*\bhow\b.*\bwithout\b.*",
            r".*\bif you\b.*\bthen\b.*",
            r".*\bpeople don't\b.*"
        ]
        
        # Value proposition indicators
        self.value_indicators = [
            "tips", "hacks", "tricks", "guide", "how to", "step by step", "tutorial",
            "learn", "discover", "find out", "reveal", "show you", "teach you",
            "help you", "make you", "get you", "save", "earn", "improve", "boost"
        ]
        
        # Call-to-action patterns
        self.cta_patterns = [
            "comment", "like", "share", "save", "follow", "subscribe", "tag",
            "try this", "let me know", "tell me", "what do you think",
            "which one", "have you", "do you", "would you", "click the link"
        ]
        
        # Shareability indicators
        self.shareability_indicators = [
            "tag someone", "send this to", "share with", "show this to",
            "everyone needs", "must see", "viral", "trending",
            "repost", "story", "share if you", "tag if you"
        ]
    
    def calculate_viral_score(self, script: str, topic: str = "", 
                            user_context: Dict[str, Any] = None) -> ViralScore:
        """
        Calculate comprehensive viral potential score for content.
        
        Args:
            script: The script content to analyze
            topic: The topic/theme of the content
            user_context: User profile context
            
        Returns:
            ViralScore object with detailed analysis
        """
        logger.info("Calculating viral potential score")
        
        if not user_context and self.profile_manager.current_profile:
            user_context = self.profile_manager.get_context_for_generation()
        
        # Initialize scoring
        scores = {}
        recommendations = []
        viral_elements = []
        missing_elements = []
        
        # Extract script sections
        sections = self._extract_script_sections(script)
        
        # 1. Hook Strength (20 points)
        hook_score, hook_recs, hook_elements = self._score_hook_strength(sections.get("hook", ""))
        scores["hook_strength"] = hook_score
        recommendations.extend(hook_recs)
        viral_elements.extend(hook_elements)
        
        # 2. Emotional Trigger (18 points)
        emotion_score, emotion_recs, emotion_elements = self._score_emotional_triggers(script)
        scores["emotional_trigger"] = emotion_score
        recommendations.extend(emotion_recs)
        viral_elements.extend(emotion_elements)
        
        # 3. Curiosity Gap (15 points)
        curiosity_score, curiosity_recs, curiosity_elements = self._score_curiosity_gap(script)
        scores["curiosity_gap"] = curiosity_score
        recommendations.extend(curiosity_recs)
        viral_elements.extend(curiosity_elements)
        
        # 4. Value Proposition (12 points)
        value_score, value_recs, value_elements = self._score_value_proposition(script)
        scores["value_proposition"] = value_score
        recommendations.extend(value_recs)
        viral_elements.extend(value_elements)
        
        # 5. Call to Action (10 points)
        cta_score, cta_recs, cta_elements = self._score_call_to_action(sections.get("cta", ""))
        scores["call_to_action"] = cta_score
        recommendations.extend(cta_recs)
        viral_elements.extend(cta_elements)
        
        # 6. Hashtag Strategy (8 points)
        hashtag_score, hashtag_recs = self._score_hashtag_strategy(sections.get("hashtags", ""), topic, user_context)
        scores["hashtag_strategy"] = hashtag_score
        recommendations.extend(hashtag_recs)
        
        # 7. Timing Relevance (7 points)
        timing_score, timing_recs = self._score_timing_relevance(script, topic)
        scores["timing_relevance"] = timing_score
        recommendations.extend(timing_recs)
        
        # 8. Shareability (6 points)
        share_score, share_recs, share_elements = self._score_shareability(script)
        scores["shareability"] = share_score
        recommendations.extend(share_recs)
        viral_elements.extend(share_elements)
        
        # 9. Authenticity (4 points)
        auth_score, auth_recs = self._score_authenticity(script, user_context)
        scores["authenticity"] = auth_score
        recommendations.extend(auth_recs)
        
        # Calculate total score
        total_score = sum(scores.values())
        max_score = sum(self.scoring_weights.values())
        percentage = (total_score / max_score) * 100
        
        # Assign grade
        grade = self._assign_grade(percentage)
        
        # Identify missing elements
        missing_elements = self._identify_missing_elements(scores, viral_elements)
        
        return ViralScore(
            total_score=round(total_score, 1),
            max_score=max_score,
            percentage=round(percentage, 1),
            grade=grade,
            breakdown=scores,
            recommendations=list(set(recommendations)),  # Remove duplicates
            viral_elements=list(set(viral_elements)),
            missing_elements=missing_elements
        )
    
    def _extract_script_sections(self, script: str) -> Dict[str, str]:
        """Extract different sections from the script."""
        sections = {}
        
        # Common section patterns
        patterns = {
            "hook": r"HOOK:\s*(.*?)(?=\n\n|\nBODY:|\nCTA:|\nCAPTION:|$)",
            "body": r"BODY:\s*(.*?)(?=\n\n|\nCTA:|\nCAPTION:|\nVISUAL:|$)",
            "cta": r"CTA:\s*(.*?)(?=\n\n|\nCAPTION:|\nVISUAL:|\nHASHTAGS:|$)",
            "caption": r"CAPTION:\s*(.*?)(?=\n\n|\nVISUAL:|\nHASHTAGS:|$)",
            "hashtags": r"HASHTAGS:\s*(.*?)(?=\n\n|$)",
            "visual": r"VISUAL DIRECTIONS?:\s*(.*?)(?=\n\n|\nHASHTAGS:|$)"
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, script, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section] = match.group(1).strip()
        
        return sections
    
    def _score_hook_strength(self, hook: str) -> Tuple[float, List[str], List[str]]:
        """Score the strength of the opening hook."""
        if not hook:
            return 0.0, ["Add a strong opening hook to grab attention"], []
        
        score = 0.0
        recommendations = []
        viral_elements = []
        max_score = self.scoring_weights["hook_strength"]
        
        hook_lower = hook.lower()
        
        # Check for viral hook patterns
        pattern_matches = sum(1 for pattern in self.viral_hooks if re.search(pattern, hook_lower))
        if pattern_matches > 0:
            score += max_score * 0.4
            viral_elements.append("viral_hook_pattern")
        else:
            recommendations.append("Use proven viral hook patterns (e.g., 'The secret that nobody tells you...')")
        
        # Check for question hooks
        if "?" in hook:
            score += max_score * 0.2
            viral_elements.append("question_hook")
        
        # Check for emotional triggers in hook
        emotion_count = sum(1 for emotions in self.emotional_triggers.values() 
                          for trigger in emotions if trigger in hook_lower)
        if emotion_count > 0:
            score += max_score * 0.3
            viral_elements.append("emotional_hook")
        else:
            recommendations.append("Add emotional triggers to your hook (urgency, curiosity, surprise)")
        
        # Check hook length (optimal 10-20 words)
        word_count = len(hook.split())
        if 10 <= word_count <= 20:
            score += max_score * 0.1
        elif word_count < 10:
            recommendations.append("Hook is too short - aim for 10-20 words")
        else:
            recommendations.append("Hook is too long - keep it under 20 words")
        
        return min(score, max_score), recommendations, viral_elements
    
    def _score_emotional_triggers(self, script: str) -> Tuple[float, List[str], List[str]]:
        """Score emotional trigger usage throughout the script."""
        score = 0.0
        recommendations = []
        viral_elements = []
        max_score = self.scoring_weights["emotional_trigger"]
        
        script_lower = script.lower()
        
        # Count different types of emotional triggers
        trigger_types_found = set()
        
        for emotion_type, triggers in self.emotional_triggers.items():
            found_triggers = [trigger for trigger in triggers if trigger in script_lower]
            if found_triggers:
                trigger_types_found.add(emotion_type)
                viral_elements.extend([f"{emotion_type}_trigger" for _ in found_triggers])
        
        # Score based on variety and presence of emotional triggers
        trigger_variety_score = len(trigger_types_found) / len(self.emotional_triggers)
        score += max_score * trigger_variety_score * 0.8
        
        # Bonus for high-impact emotions
        high_impact = ["curiosity", "urgency", "surprise", "exclusivity"]
        high_impact_found = sum(1 for emotion in high_impact if emotion in trigger_types_found)
        if high_impact_found > 0:
            score += max_score * 0.2
        
        # Recommendations based on missing triggers
        missing_high_impact = [emotion for emotion in high_impact if emotion not in trigger_types_found]
        if missing_high_impact:
            recommendations.append(f"Add {missing_high_impact[0]} triggers for higher engagement")
        
        if len(trigger_types_found) < 3:
            recommendations.append("Include more emotional variety (curiosity, urgency, surprise)")
        
        return min(score, max_score), recommendations, viral_elements
    
    def _score_curiosity_gap(self, script: str) -> Tuple[float, List[str], List[str]]:
        """Score how well the script creates curiosity gaps."""
        score = 0.0
        recommendations = []
        viral_elements = []
        max_score = self.scoring_weights["curiosity_gap"]
        
        script_lower = script.lower()
        
        # Curiosity gap indicators
        curiosity_patterns = [
            r"but first",
            r"before (?:you|we|i)",
            r"the (?:secret|truth|reason|method)",
            r"what (?:if|you|nobody|everyone)",
            r"why (?:most|some|many|everyone)",
            r"how (?:to|you can|i)",
            r"never (?:knew|thought|realized)",
            r"until (?:i|you|we)",
            r"here's (?:what|why|how|the)",
            r"turns out"
        ]
        
        # Check for curiosity patterns
        pattern_matches = sum(1 for pattern in curiosity_patterns 
                            if re.search(pattern, script_lower))
        
        if pattern_matches > 0:
            score += max_score * min(pattern_matches * 0.2, 0.6)
            viral_elements.append("curiosity_gap")
        
        # Check for preview/teaser elements
        preview_words = ["first", "next", "then", "finally", "but", "however", "surprisingly"]
        preview_count = sum(1 for word in preview_words if word in script_lower)
        
        if preview_count >= 2:
            score += max_score * 0.2
            viral_elements.append("story_progression")
        
        # Check for incomplete information that builds suspense
        suspense_indicators = ["stay tuned", "keep watching", "wait for it", "but wait"]
        if any(indicator in script_lower for indicator in suspense_indicators):
            score += max_score * 0.2
            viral_elements.append("suspense_building")
        
        # Recommendations
        if pattern_matches == 0:
            recommendations.append("Create curiosity gaps with phrases like 'But here's what nobody tells you...'")
        
        if preview_count < 2:
            recommendations.append("Use progression words (first, then, but) to build curiosity")
        
        return min(score, max_score), recommendations, viral_elements
    
    def _score_value_proposition(self, script: str) -> Tuple[float, List[str], List[str]]:
        """Score how clear and strong the value proposition is."""
        score = 0.0
        recommendations = []
        viral_elements = []
        max_score = self.scoring_weights["value_proposition"]
        
        script_lower = script.lower()
        
        # Check for value indicators
        value_found = sum(1 for indicator in self.value_indicators 
                         if indicator in script_lower)
        
        if value_found > 0:
            score += max_score * min(value_found * 0.15, 0.7)
            viral_elements.append("clear_value")
        
        # Check for specific benefits mentioned
        benefit_patterns = [
            r"save (?:time|money|effort)",
            r"get (?:more|better|faster)",
            r"increase (?:your|productivity|success)",
            r"reduce (?:stress|time|effort)",
            r"improve (?:your|health|life)",
            r"learn (?:how|to|the)",
            r"discover (?:the|how|why)"
        ]
        
        benefit_matches = sum(1 for pattern in benefit_patterns 
                            if re.search(pattern, script_lower))
        
        if benefit_matches > 0:
            score += max_score * 0.3
            viral_elements.append("specific_benefits")
        
        # Recommendations
        if value_found == 0:
            recommendations.append("Clearly state what value/benefit you're providing")
        
        if benefit_matches == 0:
            recommendations.append("Mention specific benefits (save time, improve health, etc.)")
        
        return min(score, max_score), recommendations, viral_elements
    
    def _score_call_to_action(self, cta: str) -> Tuple[float, List[str], List[str]]:
        """Score the effectiveness of the call-to-action."""
        if not cta:
            return 0.0, ["Add a clear call-to-action to drive engagement"], []
        
        score = 0.0
        recommendations = []
        viral_elements = []
        max_score = self.scoring_weights["call_to_action"]
        
        cta_lower = cta.lower()
        
        # Check for CTA patterns
        cta_found = sum(1 for pattern in self.cta_patterns 
                       if pattern in cta_lower)
        
        if cta_found > 0:
            score += max_score * 0.5
            viral_elements.append("engagement_cta")
        
        # Check for multiple CTAs (but not too many)
        cta_count = cta_found
        if 1 <= cta_count <= 3:
            score += max_score * 0.3
        elif cta_count > 3:
            recommendations.append("Too many CTAs - focus on 1-3 main actions")
        
        # Check for urgency in CTA
        urgency_words = ["now", "today", "immediately", "quick", "don't wait"]
        if any(word in cta_lower for word in urgency_words):
            score += max_score * 0.2
            viral_elements.append("urgent_cta")
        
        # Recommendations
        if cta_found == 0:
            recommendations.append("Add engagement CTAs (comment, like, share, save)")
        
        if not any(word in cta_lower for word in urgency_words):
            recommendations.append("Add urgency to your CTA (try this now, comment below)")
        
        return min(score, max_score), recommendations, viral_elements
    
    def _score_hashtag_strategy(self, hashtags: str, topic: str, 
                               user_context: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Score hashtag strategy effectiveness."""
        score = 0.0
        recommendations = []
        max_score = self.scoring_weights["hashtag_strategy"]
        
        if not hashtags:
            return 0.0, ["Add relevant hashtags to increase discoverability"]
        
        # Extract hashtags
        hashtag_list = re.findall(r'#\w+', hashtags)
        hashtag_count = len(hashtag_list)
        
        # Optimal hashtag count (20-30)
        if 20 <= hashtag_count <= 30:
            score += max_score * 0.4
        elif 15 <= hashtag_count < 20:
            score += max_score * 0.3
            recommendations.append("Add more hashtags (aim for 20-30)")
        elif hashtag_count > 30:
            score += max_score * 0.2
            recommendations.append("Too many hashtags - focus on 20-30 most relevant")
        else:
            recommendations.append("Add more hashtags for better reach")
        
        # Check for mix of hashtag types (if we have hashtag optimizer data)
        # This would integrate with the hashtag optimizer for better scoring
        score += max_score * 0.3  # Placeholder for now
        
        # Check for trending hashtags
        trending_indicators = ["trend", "viral", "2024", "challenge"]
        trending_count = sum(1 for hashtag in hashtag_list 
                           for indicator in trending_indicators 
                           if indicator in hashtag.lower())
        
        if trending_count > 0:
            score += max_score * 0.3
        else:
            recommendations.append("Include trending hashtags for better reach")
        
        return min(score, max_score), recommendations
    
    def _score_timing_relevance(self, script: str, topic: str) -> Tuple[float, List[str]]:
        """Score how well the content aligns with current timing/trends."""
        score = 0.0
        recommendations = []
        max_score = self.scoring_weights["timing_relevance"]
        
        script_lower = script.lower()
        current_date = datetime.now()
        
        # Current year reference
        if str(current_date.year) in script:
            score += max_score * 0.3
        
        # Seasonal relevance
        month = current_date.month
        seasonal_terms = {
            1: ["new year", "resolution", "fresh start", "january"],
            2: ["valentine", "love", "february"],
            3: ["spring", "march", "renewal"],
            4: ["april", "easter", "spring"],
            5: ["may", "mother", "spring"],
            6: ["june", "summer", "father"],
            7: ["july", "summer", "vacation"],
            8: ["august", "summer", "back to school"],
            9: ["september", "fall", "autumn", "back to school"],
            10: ["october", "halloween", "fall"],
            11: ["november", "thanksgiving", "gratitude"],
            12: ["december", "christmas", "holiday", "year end"]
        }
        
        if month in seasonal_terms:
            seasonal_matches = sum(1 for term in seasonal_terms[month] 
                                 if term in script_lower)
            if seasonal_matches > 0:
                score += max_score * 0.4
        
        # Trending topic indicators
        trending_terms = ["trending", "viral", "latest", "new", "hot", "popular"]
        trending_matches = sum(1 for term in trending_terms if term in script_lower)
        
        if trending_matches > 0:
            score += max_score * 0.3
        else:
            recommendations.append("Reference current trends or timing for relevance")
        
        return min(score, max_score), recommendations
    
    def _score_shareability(self, script: str) -> Tuple[float, List[str], List[str]]:
        """Score how likely the content is to be shared."""
        score = 0.0
        recommendations = []
        viral_elements = []
        max_score = self.scoring_weights["shareability"]
        
        script_lower = script.lower()
        
        # Check for shareability indicators
        share_found = sum(1 for indicator in self.shareability_indicators 
                         if indicator in script_lower)
        
        if share_found > 0:
            score += max_score * 0.4
            viral_elements.append("share_encouragement")
        
        # Check for relatable content
        relatable_phrases = ["we all", "everyone", "you know", "happens to", "can relate"]
        relatable_count = sum(1 for phrase in relatable_phrases 
                            if phrase in script_lower)
        
        if relatable_count > 0:
            score += max_score * 0.3
            viral_elements.append("relatable_content")
        
        # Check for conversation starters
        conversation_starters = ["what do you think", "agree or disagree", "your experience", 
                               "comment below", "let me know", "tell me"]
        conversation_count = sum(1 for starter in conversation_starters 
                               if starter in script_lower)
        
        if conversation_count > 0:
            score += max_score * 0.3
            viral_elements.append("conversation_starter")
        
        # Recommendations
        if share_found == 0:
            recommendations.append("Add explicit sharing encouragement (tag someone who needs this)")
        
        if relatable_count == 0:
            recommendations.append("Make content more relatable (we all know, everyone does this)")
        
        return min(score, max_score), recommendations, viral_elements
    
    def _score_authenticity(self, script: str, user_context: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Score how authentic the content feels."""
        score = 0.0
        recommendations = []
        max_score = self.scoring_weights["authenticity"]
        
        script_lower = script.lower()
        
        # Check for personal elements
        personal_pronouns = ["i", "my", "me", "myself"]
        personal_count = sum(script_lower.count(pronoun) for pronoun in personal_pronouns)
        
        if personal_count > 0:
            score += max_score * 0.5
        else:
            recommendations.append("Add personal elements (I discovered, my experience)")
        
        # Check for story elements
        story_indicators = ["when i", "i remember", "happened to me", "my story", "i learned"]
        story_count = sum(1 for indicator in story_indicators if indicator in script_lower)
        
        if story_count > 0:
            score += max_score * 0.3
        
        # Check for vulnerability/honesty
        honest_phrases = ["honestly", "truth is", "i'll admit", "struggled with", "made mistakes"]
        honest_count = sum(1 for phrase in honest_phrases if phrase in script_lower)
        
        if honest_count > 0:
            score += max_score * 0.2
        else:
            recommendations.append("Add honest/vulnerable elements for authenticity")
        
        return min(score, max_score), recommendations
    
    def _assign_grade(self, percentage: float) -> str:
        """Assign letter grade based on percentage."""
        if percentage >= 95:
            return "A+"
        elif percentage >= 90:
            return "A"
        elif percentage >= 85:
            return "B+"
        elif percentage >= 80:
            return "B"
        elif percentage >= 75:
            return "C+"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
    
    def _identify_missing_elements(self, scores: Dict[str, float], 
                                 viral_elements: List[str]) -> List[str]:
        """Identify key viral elements that are missing."""
        missing = []
        
        # Check for critical missing elements
        if scores.get("hook_strength", 0) < self.scoring_weights["hook_strength"] * 0.5:
            missing.append("Strong attention-grabbing hook")
        
        if scores.get("emotional_trigger", 0) < self.scoring_weights["emotional_trigger"] * 0.5:
            missing.append("Emotional triggers (curiosity, urgency, surprise)")
        
        if scores.get("call_to_action", 0) < self.scoring_weights["call_to_action"] * 0.5:
            missing.append("Clear call-to-action")
        
        if "viral_hook_pattern" not in viral_elements:
            missing.append("Proven viral hook pattern")
        
        if "share_encouragement" not in viral_elements:
            missing.append("Shareability elements")
        
        return missing
    
    def optimize_for_virality(self, script: str, topic: str = "", 
                            user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Provide specific optimization suggestions for viral potential.
        
        Args:
            script: Original script
            topic: Content topic
            user_context: User profile context
            
        Returns:
            Dictionary with optimization suggestions and improved script elements
        """
        # Get current viral score
        current_score = self.calculate_viral_score(script, topic, user_context)
        
        # Generate specific improvements
        improvements = {
            "current_score": current_score,
            "optimization_plan": [],
            "suggested_improvements": {},
            "viral_score_potential": 0
        }
        
        # Priority improvements based on biggest score gaps
        score_gaps = {}
        for component, weight in self.scoring_weights.items():
            current = current_score.breakdown.get(component, 0)
            gap = weight - current
            score_gaps[component] = gap
        
        # Sort by biggest gaps first
        priority_improvements = sorted(score_gaps.items(), key=lambda x: x[1], reverse=True)
        
        for component, gap in priority_improvements[:5]:  # Top 5 improvements
            if gap > weight * 0.3:  # Only if significant gap
                improvement_plan = self._generate_improvement_plan(component, script, topic)
                if improvement_plan:
                    improvements["optimization_plan"].append(improvement_plan)
        
        # Calculate potential score after improvements
        potential_increase = sum(min(gap, weight * 0.8) for component, gap in priority_improvements[:3])
        improvements["viral_score_potential"] = current_score.total_score + potential_increase
        
        return improvements
    
    def _generate_improvement_plan(self, component: str, script: str, topic: str) -> Dict[str, Any]:
        """Generate specific improvement plan for a component."""
        plans = {
            "hook_strength": {
                "issue": "Weak opening hook",
                "solution": "Create a stronger attention-grabbing opening",
                "examples": [
                    f"The secret to {topic} that nobody tells you...",
                    f"Stop doing {topic} wrong - here's why...",
                    f"What if I told you {topic} could change everything?"
                ],
                "impact": "High - Strong hooks can increase engagement by 300%"
            },
            "emotional_trigger": {
                "issue": "Limited emotional engagement",
                "solution": "Add more emotional triggers throughout",
                "examples": [
                    "Add curiosity: 'But here's what most people don't realize...'",
                    "Add urgency: 'You need to try this before...'",
                    "Add surprise: 'The results will shock you...'"
                ],
                "impact": "High - Emotional content gets 2x more shares"
            },
            "call_to_action": {
                "issue": "Weak or missing call-to-action",
                "solution": "Add clear, compelling CTAs",
                "examples": [
                    "Comment below which tip you'll try first!",
                    "Save this post and tag someone who needs to see it!",
                    "Follow for more life-changing tips like this!"
                ],
                "impact": "Medium - Good CTAs increase engagement by 150%"
            }
        }
        
        return plans.get(component, {})


def format_viral_score_report(viral_score: ViralScore) -> str:
    """Format viral score into a readable report."""
    report = f"""
🎯 VIRAL POTENTIAL ANALYSIS
═══════════════════════════

📊 OVERALL SCORE: {viral_score.total_score}/{viral_score.max_score} ({viral_score.percentage}%)
🏆 GRADE: {viral_score.grade}

📈 BREAKDOWN:
"""
    
    for component, score in viral_score.breakdown.items():
        max_component_score = ViralPotentialScorer().scoring_weights[component]
        percentage = (score / max_component_score) * 100
        bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
        report += f"  {component.replace('_', ' ').title()}: {score:.1f}/{max_component_score} [{bar}] {percentage:.0f}%\n"
    
    report += f"""
✅ VIRAL ELEMENTS FOUND:
{chr(10).join(f"  • {element.replace('_', ' ').title()}" for element in viral_score.viral_elements)}

❌ MISSING ELEMENTS:
{chr(10).join(f"  • {element}" for element in viral_score.missing_elements)}

💡 RECOMMENDATIONS:
{chr(10).join(f"  • {rec}" for rec in viral_score.recommendations)}
"""
    
    return report