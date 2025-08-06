"""User profile management system for personalized script generation."""

import os
import json
import hashlib
import PyPDF2
import docx
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from .config import logger
except ImportError:
    from src.config import logger


@dataclass
class UserProfile:
    """User profile data structure."""
    user_id: str
    name: str
    bio: str
    niche: str
    target_audience: str
    content_style: str
    tone: str
    key_topics: List[str]
    personal_story: str
    unique_selling_points: List[str]
    preferred_hashtags: List[str]
    content_goals: str
    created_at: str
    updated_at: str


class UserProfileManager:
    """Manages user profiles and context for personalized script generation."""
    
    def __init__(self, profiles_dir: str = "data/user_profiles"):
        """Initialize the profile manager."""
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.current_profile: Optional[UserProfile] = None
    
    def create_profile_from_text(self, text_content: str, user_name: str = "User") -> UserProfile:
        """
        Create a user profile from text content using AI analysis.
        
        Args:
            text_content: The user's bio/description text
            user_name: User's name
            
        Returns:
            UserProfile object
        """
        # Generate unique user ID
        user_id = hashlib.md5(f"{user_name}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        # Analyze text content to extract profile information
        profile_data = self._analyze_user_content(text_content)
        
        profile = UserProfile(
            user_id=user_id,
            name=user_name,
            bio=profile_data.get("bio", text_content[:200]),
            niche=profile_data.get("niche", "lifestyle"),
            target_audience=profile_data.get("target_audience", "general audience"),
            content_style=profile_data.get("content_style", "informative and engaging"),
            tone=profile_data.get("tone", "friendly and approachable"),
            key_topics=profile_data.get("key_topics", []),
            personal_story=profile_data.get("personal_story", text_content),
            unique_selling_points=profile_data.get("unique_selling_points", []),
            preferred_hashtags=profile_data.get("preferred_hashtags", []),
            content_goals=profile_data.get("content_goals", "engage and inspire audience"),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        return profile
    
    def upload_profile_document(self, file_path: str, user_name: str = "User") -> UserProfile:
        """
        Create user profile from uploaded document (PDF, DOCX, or TXT).
        
        Args:
            file_path: Path to the uploaded document
            user_name: User's name
            
        Returns:
            UserProfile object
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text_content = self._extract_pdf_text(file_path)
        elif file_path.suffix.lower() == '.docx':
            text_content = self._extract_docx_text(file_path)
        elif file_path.suffix.lower() == '.txt':
            text_content = self._extract_txt_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        if not text_content.strip():
            raise ValueError("No text content found in the uploaded file")
        
        return self.create_profile_from_text(text_content, user_name)
    
    def save_profile(self, profile: UserProfile) -> bool:
        """
        Save user profile to disk.
        
        Args:
            profile: UserProfile object to save
            
        Returns:
            bool: True if saved successfully
        """
        try:
            profile_file = self.profiles_dir / f"{profile.user_id}.json"
            profile_data = asdict(profile)
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Profile saved: {profile.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            return False
    
    def load_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Load user profile from disk.
        
        Args:
            user_id: User ID to load
            
        Returns:
            UserProfile object or None if not found
        """
        try:
            profile_file = self.profiles_dir / f"{user_id}.json"
            
            if not profile_file.exists():
                return None
            
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            profile = UserProfile(**profile_data)
            logger.info(f"Profile loaded: {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error loading profile: {e}")
            return None
    
    def list_profiles(self) -> List[Dict[str, str]]:
        """
        List all available user profiles.
        
        Returns:
            List of profile summaries
        """
        profiles = []
        
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                profiles.append({
                    "user_id": data.get("user_id", ""),
                    "name": data.get("name", "Unknown"),
                    "niche": data.get("niche", "Unknown"),
                    "created_at": data.get("created_at", "")
                })
            except Exception as e:
                logger.warning(f"Error reading profile {profile_file}: {e}")
                continue
        
        return sorted(profiles, key=lambda x: x["created_at"], reverse=True)
    
    def set_active_profile(self, user_id: str) -> bool:
        """
        Set the active user profile.
        
        Args:
            user_id: User ID to set as active
            
        Returns:
            bool: True if profile was set successfully
        """
        profile = self.load_profile(user_id)
        if profile:
            self.current_profile = profile
            logger.info(f"Active profile set: {user_id}")
            return True
        return False
    
    def get_context_for_generation(self) -> Dict[str, Any]:
        """
        Get user context for script generation.
        
        Returns:
            Dictionary with user context for AI generation
        """
        if not self.current_profile:
            return {}
        
        return {
            "user_name": self.current_profile.name,
            "user_bio": self.current_profile.bio,
            "niche": self.current_profile.niche,
            "target_audience": self.current_profile.target_audience,
            "content_style": self.current_profile.content_style,
            "tone": self.current_profile.tone,
            "key_topics": self.current_profile.key_topics,
            "personal_story": self.current_profile.personal_story,
            "unique_selling_points": self.current_profile.unique_selling_points,
            "preferred_hashtags": self.current_profile.preferred_hashtags,
            "content_goals": self.current_profile.content_goals
        }
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            return ""
    
    def _extract_txt_text(self, file_path: Path) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error extracting TXT text: {e}")
            return ""
    
    def _analyze_user_content(self, text_content: str) -> Dict[str, Any]:
        """
        Analyze user content to extract profile information.
        This is a simplified version - could be enhanced with AI analysis.
        
        Args:
            text_content: Raw text content
            
        Returns:
            Dictionary with extracted profile data
        """
        # Basic keyword-based analysis (can be enhanced with AI)
        content_lower = text_content.lower()
        
        # Detect niche
        niche_keywords = {
            "fitness": ["fitness", "workout", "gym", "exercise", "health"],
            "food": ["food", "recipe", "cooking", "meal", "nutrition"],
            "lifestyle": ["lifestyle", "daily", "routine", "tips", "life"],
            "business": ["business", "entrepreneur", "marketing", "success"],
            "tech": ["technology", "tech", "coding", "software", "digital"],
            "fashion": ["fashion", "style", "outfit", "clothing", "trendy"],
            "travel": ["travel", "adventure", "explore", "journey", "destination"]
        }
        
        niche = "lifestyle"  # default
        for n, keywords in niche_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                niche = n
                break
        
        # Extract key topics (simple word frequency analysis)
        words = content_lower.split()
        common_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "a", "an", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "her", "its", "our", "their"]
        
        filtered_words = [word for word in words if len(word) > 3 and word not in common_words]
        from collections import Counter
        key_topics = [word for word, count in Counter(filtered_words).most_common(10)]
        
        return {
            "bio": text_content[:200] + "..." if len(text_content) > 200 else text_content,
            "niche": niche,
            "target_audience": "engaged followers interested in " + niche,
            "content_style": "authentic and relatable",
            "tone": "friendly and inspiring",
            "key_topics": key_topics,
            "personal_story": text_content,
            "unique_selling_points": [f"Expert in {niche}", "Authentic storytelling", "Practical advice"],
            "preferred_hashtags": [f"#{niche}", "#authentic", "#inspiration"],
            "content_goals": f"Inspire and educate audience about {niche}"
        }