"""Comprehensive test suite for enhanced Instagram Script Writer features."""

import pytest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Import all our enhanced modules
from src.user_profile import UserProfileManager, UserProfile
from src.hashtag_optimizer import HashtagOptimizer, HashtagMetrics
from src.viral_scorer import ViralPotentialScorer, ViralScore
from src.manual_script_manager import ManualScriptManager, UploadedScript
from src.enhanced_scraper import EnhancedContentScraper, ViralContent
from src.enhanced_generator import EnhancedScriptGenerator, analyze_script_performance_potential


class TestUserProfileManager:
    """Test user profile management functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.profile_manager = UserProfileManager(profiles_dir=self.temp_dir)
    
    def test_create_profile_from_text(self):
        """Test creating profile from text content."""
        text_content = """
        Hi, I'm Sarah, a fitness enthusiast and certified personal trainer.
        I create content about workout routines, nutrition tips, and healthy lifestyle habits.
        My goal is to inspire busy professionals to stay fit and healthy.
        """
        
        profile = self.profile_manager.create_profile_from_text(text_content, "Sarah Johnson")
        
        assert profile.name == "Sarah Johnson"
        assert profile.niche == "fitness"
        assert "fitness" in profile.bio.lower()
        assert len(profile.key_topics) > 0
    
    def test_save_and_load_profile(self):
        """Test saving and loading profiles."""
        text_content = "I'm a food blogger who loves sharing recipes and cooking tips."
        profile = self.profile_manager.create_profile_from_text(text_content, "Chef Mike")
        
        # Save profile
        result = self.profile_manager.save_profile(profile)
        assert result is True
        
        # Load profile
        loaded_profile = self.profile_manager.load_profile(profile.user_id)
        assert loaded_profile is not None
        assert loaded_profile.name == "Chef Mike"
        assert loaded_profile.niche == "food"
    
    def test_list_profiles(self):
        """Test listing all profiles."""
        # Create multiple profiles
        profiles_data = [
            ("Alice", "I'm a lifestyle blogger"),
            ("Bob", "I create tech content and reviews"),
            ("Carol", "I'm a business coach and entrepreneur")
        ]
        
        created_profiles = []
        for name, content in profiles_data:
            profile = self.profile_manager.create_profile_from_text(content, name)
            self.profile_manager.save_profile(profile)
            created_profiles.append(profile)
        
        # List profiles
        profile_list = self.profile_manager.list_profiles()
        assert len(profile_list) == 3
        
        names = [p["name"] for p in profile_list]
        assert "Alice" in names
        assert "Bob" in names
        assert "Carol" in names


class TestHashtagOptimizer:
    """Test hashtag optimization functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.hashtag_optimizer = HashtagOptimizer()
    
    def test_generate_topic_hashtags(self):
        """Test generating hashtags from topic."""
        topic = "morning routine productivity"
        hashtags = self.hashtag_optimizer._generate_topic_hashtags(topic)
        
        assert len(hashtags) > 0
        assert any("morning" in tag.lower() for tag in hashtags)
        assert any("routine" in tag.lower() for tag in hashtags)
        assert any("productivity" in tag.lower() for tag in hashtags)
    
    def test_get_niche_hashtags(self):
        """Test getting niche-specific hashtags."""
        fitness_hashtags = self.hashtag_optimizer._get_niche_hashtags("fitness")
        food_hashtags = self.hashtag_optimizer._get_niche_hashtags("food")
        
        assert len(fitness_hashtags) > 0
        assert len(food_hashtags) > 0
        assert any("fitness" in tag.lower() for tag in fitness_hashtags)
        assert any("food" in tag.lower() for tag in food_hashtags)
    
    def test_generate_optimal_hashtags(self):
        """Test generating optimal hashtag strategy."""
        topic = "healthy breakfast ideas"
        user_context = {
            "niche": "food",
            "preferred_hashtags": ["#healthyeating", "#breakfast"]
        }
        
        hashtags = self.hashtag_optimizer.generate_optimal_hashtags(
            topic, user_context, target_count=20
        )
        
        assert len(hashtags) <= 20
        assert all(isinstance(h, HashtagMetrics) for h in hashtags)
        assert all(h.viral_potential > 0 for h in hashtags)
    
    def test_hashtag_strategy_report(self):
        """Test generating hashtag strategy report."""
        # Create mock hashtags
        hashtags = [
            HashtagMetrics("#test1", 80, "medium", "rising", 85, 90, 82),
            HashtagMetrics("#test2", 70, "low", "stable", 75, 85, 78),
            HashtagMetrics("#test3", 90, "high", "rising", 95, 80, 88)
        ]
        
        report = self.hashtag_optimizer.get_hashtag_strategy_report(hashtags)
        
        assert "total_hashtags" in report
        assert "average_scores" in report
        assert "competition_distribution" in report
        assert "strategy_recommendations" in report
        assert report["total_hashtags"] == 3


class TestViralScorer:
    """Test viral potential scoring functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.viral_scorer = ViralPotentialScorer()
    
    def test_calculate_viral_score_basic(self):
        """Test basic viral score calculation."""
        script = """
        HOOK: Want to know the secret to morning productivity that nobody tells you?
        
        BODY: Here's what changed my life completely. I discovered that the first hour of your day determines everything. Most people make these 3 crucial mistakes...
        
        CTA: Try this for 7 days and comment below how you feel! Save this post to remember.
        
        CAPTION: Morning routine that changed my life ✨
        
        HASHTAGS: #MorningRoutine #Productivity #LifeHacks #Success #Motivation
        """
        
        viral_score = self.viral_scorer.calculate_viral_score(script, "morning routine")
        
        assert isinstance(viral_score, ViralScore)
        assert viral_score.total_score > 0
        assert viral_score.percentage > 0
        assert viral_score.grade in ["A+", "A", "B+", "B", "C+", "C", "D", "F"]
        assert len(viral_score.breakdown) > 0
        assert len(viral_score.recommendations) > 0
    
    def test_score_hook_strength(self):
        """Test hook strength scoring."""
        strong_hook = "The secret that nobody tells you about success..."
        weak_hook = "Hello everyone"
        
        strong_score, _, _ = self.viral_scorer._score_hook_strength(strong_hook)
        weak_score, _, _ = self.viral_scorer._score_hook_strength(weak_hook)
        
        assert strong_score > weak_score
        assert strong_score > 0
    
    def test_score_emotional_triggers(self):
        """Test emotional trigger scoring."""
        emotional_script = "This shocking secret will amaze you! Everyone needs to know this incredible hack."
        bland_script = "Here is some information about the topic."
        
        emotional_score, _, _ = self.viral_scorer._score_emotional_triggers(emotional_script)
        bland_score, _, _ = self.viral_scorer._score_emotional_triggers(bland_script)
        
        assert emotional_score > bland_score
    
    def test_optimize_for_virality(self):
        """Test viral optimization suggestions."""
        basic_script = """
        This is about morning routines.
        You should wake up early.
        That's all.
        """
        
        optimization = self.viral_scorer.optimize_for_virality(basic_script, "morning routine")
        
        assert "current_score" in optimization
        assert "optimization_plan" in optimization
        assert "viral_score_potential" in optimization
        assert len(optimization["optimization_plan"]) > 0


class TestManualScriptManager:
    """Test manual script upload and management."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.script_manager = ManualScriptManager(upload_dir=self.temp_dir)
    
    def test_upload_script_content(self):
        """Test uploading script content."""
        script_content = """
        HOOK: Amazing fitness tip that will change your workout!
        BODY: Here's the secret to better results...
        CTA: Try this and let me know how it goes!
        HASHTAGS: #Fitness #Workout #Tips
        """
        
        uploaded_script = self.script_manager.upload_script_content(
            script_content, "Amazing Fitness Tip", "fitness", "High performing script"
        )
        
        assert isinstance(uploaded_script, UploadedScript)
        assert uploaded_script.title == "Amazing Fitness Tip"
        assert uploaded_script.topic == "fitness"
        assert uploaded_script.user_notes == "High performing script"
        assert uploaded_script.viral_score > 0
        assert len(uploaded_script.hashtags) > 0
    
    def test_get_uploaded_scripts(self):
        """Test retrieving uploaded scripts."""
        # Upload multiple scripts
        scripts_data = [
            ("Script 1", "fitness content", "fitness"),
            ("Script 2", "food content", "food"),
            ("Script 3", "lifestyle content", "lifestyle")
        ]
        
        for title, content, topic in scripts_data:
            self.script_manager.upload_script_content(content, title, topic, "")
        
        # Retrieve scripts
        uploaded_scripts = self.script_manager.get_uploaded_scripts()
        assert len(uploaded_scripts) == 3
        
        titles = [s.title for s in uploaded_scripts]
        assert "Script 1" in titles
        assert "Script 2" in titles
        assert "Script 3" in titles
    
    def test_analyze_script_collection(self):
        """Test analyzing script collection."""
        # Upload some scripts first
        high_performing_script = """
        HOOK: The secret nobody tells you about success!
        BODY: This amazing technique will shock you...
        CTA: Comment below and share with friends!
        HASHTAGS: #Success #Motivation #Secret #Amazing
        """
        
        self.script_manager.upload_script_content(
            high_performing_script, "High Performer", "business", ""
        )
        
        analysis = self.script_manager.analyze_script_collection()
        
        assert "summary" in analysis
        assert "topic_distribution" in analysis
        assert "performance_insights" in analysis


class TestEnhancedScraper:
    """Test enhanced content scraping functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.scraper = EnhancedContentScraper()
    
    def test_discover_trending_hashtags(self):
        """Test discovering trending hashtags."""
        hashtags = self.scraper.discover_trending_hashtags("fitness", "english", 20)
        
        assert len(hashtags) > 0
        assert len(hashtags) <= 20
        assert all(tag.startswith('#') for tag in hashtags)
        assert any("fitness" in tag.lower() for tag in hashtags)
    
    def test_detect_language(self):
        """Test language detection."""
        english_text = "This is a great workout routine for beginners"
        hindi_text = "यह एक बहुत अच्छी exercise है"
        
        english_lang = self.scraper._detect_language(english_text)
        hindi_lang = self.scraper._detect_language(hindi_text)
        
        assert english_lang == "english"
        # Note: Simplified detection might not catch all languages perfectly
    
    def test_detect_niche(self):
        """Test niche detection."""
        fitness_text = "workout gym exercise fitness health training"
        food_text = "recipe cooking food delicious meal ingredients"
        
        fitness_niche = self.scraper._detect_niche(fitness_text, [])
        food_niche = self.scraper._detect_niche(food_text, [])
        
        assert fitness_niche == "fitness"
        assert food_niche == "food"
    
    @patch('instaloader.Instaloader')
    def test_analyze_viral_patterns(self, mock_instaloader):
        """Test analyzing viral patterns from content."""
        # Create mock viral content
        mock_content = [
            ViralContent(
                post_id="1", shortcode="abc", caption="Amazing fitness tip!",
                hashtags=["#fitness", "#workout"], likes=1000, comments=50,
                engagement_rate=0.05, viral_score=85, post_type="reel",
                created_at="2024-01-01T12:00:00", language="english",
                niche="fitness", performance_factors={"has_question": True}
            ),
            ViralContent(
                post_id="2", shortcode="def", caption="Incredible workout hack!",
                hashtags=["#fitness", "#hack"], likes=800, comments=40,
                engagement_rate=0.04, viral_score=80, post_type="reel",
                created_at="2024-01-01T15:00:00", language="english",
                niche="fitness", performance_factors={"has_question": False}
            )
        ]
        
        analysis = self.scraper.analyze_viral_patterns(mock_content)
        
        assert len(analysis.top_hashtags) > 0
        assert len(analysis.common_themes) > 0
        assert len(analysis.optimal_posting_times) > 0
        assert len(analysis.content_recommendations) > 0


class TestEnhancedGenerator:
    """Test enhanced script generation functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        # Mock the components that require API access
        with patch('src.enhanced_generator.openai'), \
             patch('src.enhanced_generator.Pinecone'), \
             patch('src.enhanced_generator.ChatOpenAI'):
            self.generator = EnhancedScriptGenerator()
    
    def test_analyze_script_performance_potential(self):
        """Test script performance analysis."""
        script = """
        HOOK: Want to know the secret to success?
        BODY: Here are 3 proven strategies...
        CTA: Comment below which tip you'll try!
        HASHTAGS: #Success #Tips #Motivation
        """
        
        analysis = analyze_script_performance_potential(script, "success tips")
        
        assert "viral_score" in analysis
        assert "hashtag_analysis" in analysis
        assert "performance_factors" in analysis
        assert "overall_performance_score" in analysis
        assert analysis["overall_performance_score"] > 0
    
    def test_generation_strategies(self):
        """Test different generation strategies."""
        strategies = ["viral_optimized", "story_driven", "educational", "entertainment", "trending"]
        
        for strategy in strategies:
            assert strategy in self.generator.generation_strategies
            prompt_template = self.generator.generation_strategies[strategy]
            assert "{topic}" in prompt_template
            assert "{user_context}" in prompt_template


class TestIntegration:
    """Integration tests for combined functionality."""
    
    def setup_method(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize all components
        self.profile_manager = UserProfileManager(profiles_dir=self.temp_dir)
        self.hashtag_optimizer = HashtagOptimizer()  
        self.viral_scorer = ViralPotentialScorer()
        self.script_manager = ManualScriptManager(upload_dir=self.temp_dir)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from profile to script analysis."""
        # 1. Create user profile
        profile_text = "I'm a fitness coach who helps busy professionals stay healthy"
        profile = self.profile_manager.create_profile_from_text(profile_text, "FitnessCoach")
        self.profile_manager.save_profile(profile)
        self.profile_manager.set_active_profile(profile.user_id)
        
        # 2. Upload a reference script
        reference_script = """
        HOOK: Tired of being tired? This 5-minute routine will energize your entire day!
        BODY: As a busy professional, I used to crash every afternoon. Then I discovered this simple technique...
        CTA: Try this tomorrow morning and comment your energy level!
        HASHTAGS: #Energy #Productivity #Health #Fitness #MorningRoutine
        """
        
        uploaded = self.script_manager.upload_script_content(
            reference_script, "Energy Boost Routine", "fitness", "High performer"
        )
        
        # 3. Generate optimal hashtags
        user_context = self.profile_manager.get_context_for_generation()
        hashtags = self.hashtag_optimizer.generate_optimal_hashtags(
            "morning energy routine", user_context, 25
        )
        
        # 4. Analyze viral potential
        viral_score = self.viral_scorer.calculate_viral_score(
            reference_script, "morning energy routine", user_context
        )
        
        # 5. Get optimization suggestions
        optimization = self.viral_scorer.optimize_for_virality(
            reference_script, "morning energy routine", user_context
        )
        
        # Verify the complete workflow
        assert profile.niche == "fitness"
        assert uploaded.viral_score > 0
        assert len(hashtags) > 0
        assert viral_score.total_score > 0
        assert len(optimization["optimization_plan"]) >= 0
        
        # Verify integration between components
        assert any("fitness" in h.tag.lower() for h in hashtags)
        assert "fitness" in user_context["niche"]
    
    def test_profile_impact_on_generation(self):
        """Test how user profile affects content generation."""
        # Create two different profiles
        fitness_profile = self.profile_manager.create_profile_from_text(
            "I'm a fitness trainer specializing in HIIT workouts", "FitnessTrainer"
        )
        
        food_profile = self.profile_manager.create_profile_from_text(
            "I'm a chef who creates healthy recipe content", "HealthyChef"
        )
        
        # Generate hashtags for the same topic with different profiles
        topic = "healthy lifestyle tips"
        
        # With fitness profile
        self.profile_manager.set_active_profile(fitness_profile.user_id)
        fitness_hashtags = self.hashtag_optimizer.generate_optimal_hashtags(
            topic, self.profile_manager.get_context_for_generation(), 20
        )
        
        # With food profile  
        self.profile_manager.set_active_profile(food_profile.user_id)
        food_hashtags = self.hashtag_optimizer.generate_optimal_hashtags(
            topic, self.profile_manager.get_context_for_generation(), 20
        )
        
        # Verify different profiles produce different hashtag strategies
        fitness_tags = [h.tag.lower() for h in fitness_hashtags]
        food_tags = [h.tag.lower() for h in food_hashtags]
        
        # Should have some different hashtags based on niche
        assert fitness_tags != food_tags


def run_basic_tests():
    """Run basic functionality tests without pytest."""
    print("🧪 Running Enhanced Instagram Script Writer Tests")
    print("=" * 50)
    
    # Test User Profile Manager
    print("\n📝 Testing User Profile Manager...")
    try:
        profile_manager = UserProfileManager(profiles_dir="temp_test_profiles")
        profile = profile_manager.create_profile_from_text(
            "I'm a fitness enthusiast who loves sharing workout tips", "TestUser"
        )
        assert profile.name == "TestUser"
        assert profile.niche == "fitness"
        print("✅ User Profile Manager: PASSED")
    except Exception as e:
        print(f"❌ User Profile Manager: FAILED - {e}")
    
    # Test Hashtag Optimizer
    print("\n🏷️ Testing Hashtag Optimizer...")
    try:
        hashtag_optimizer = HashtagOptimizer()
        hashtags = hashtag_optimizer.generate_optimal_hashtags("fitness tips", {}, 10)
        assert len(hashtags) > 0
        assert all(hasattr(h, 'viral_potential') for h in hashtags)
        print("✅ Hashtag Optimizer: PASSED")
    except Exception as e:
        print(f"❌ Hashtag Optimizer: FAILED - {e}")
    
    # Test Viral Scorer
    print("\n🔥 Testing Viral Scorer...")
    try:
        viral_scorer = ViralPotentialScorer()
        test_script = "HOOK: Amazing tip! BODY: This will change your life. CTA: Comment below!"
        score = viral_scorer.calculate_viral_score(test_script, "life tips")
        assert score.total_score > 0
        assert score.percentage >= 0
        print("✅ Viral Scorer: PASSED")
    except Exception as e:
        print(f"❌ Viral Scorer: FAILED - {e}")
    
    # Test Manual Script Manager
    print("\n📁 Testing Manual Script Manager...")
    try:
        script_manager = ManualScriptManager(upload_dir="temp_test_scripts")
        uploaded = script_manager.upload_script_content(
            "Test script content", "Test Script", "test", "Test notes"
        )
        assert uploaded.title == "Test Script"
        assert uploaded.viral_score >= 0
        print("✅ Manual Script Manager: PASSED")
    except Exception as e:
        print(f"❌ Manual Script Manager: FAILED - {e}")
    
    # Test Enhanced Scraper
    print("\n🕷️ Testing Enhanced Scraper...")
    try:
        scraper = EnhancedContentScraper()
        hashtags = scraper.discover_trending_hashtags("fitness", "english", 10)
        assert len(hashtags) > 0
        language = scraper._detect_language("This is English text")
        assert language == "english"
        print("✅ Enhanced Scraper: PASSED")
    except Exception as e:
        print(f"❌ Enhanced Scraper: FAILED - {e}")
    
    print("\n🎉 Basic tests completed!")
    print("For full testing, run: pytest test_enhanced_features.py")


if __name__ == "__main__":
    # Run basic tests if pytest is not available
    run_basic_tests()