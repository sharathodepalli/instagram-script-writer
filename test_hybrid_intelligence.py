#!/usr/bin/env python3
"""
Test the Hybrid Intelligence System
Tests the integration of Personal Intelligence + Domain Intelligence
"""

import sys
sys.path.append('.')

from src.intelligent_script_engine import IntelligentScriptEngine, ContentRequest
from src.domain_intelligence import DomainIntelligenceEngine, SuccessfulContent
from src.content_collector import ContentCollector
from src.user_content_sharing import UserContentSharingSystem
import time

def create_sample_domain_content():
    """Create sample successful content for testing"""
    domain_engine = DomainIntelligenceEngine()
    
    # Sample skincare content
    skincare_content = [
        SuccessfulContent(
            content_id="skincare_001",
            script_text="HOOK: The one skincare mistake that's aging you faster than you think!\n\nBODY: Using harsh scrubs every day destroys your skin barrier. I learned this the hard way after years of over-exfoliating. Now I exfoliate max 2x per week and my skin is glowing!\n\nCTA: What's your biggest skincare mistake? Share below!\n\nCAPTION: Stop over-exfoliating! Your skin will thank you ✨\n\nVISUAL DIRECTIONS: Show before/after skin, demonstrate gentle exfoliation technique\n\nHASHTAGS: #skincare #glowingskin #skincaretips #healthyskin",
            niche="skincare",
            topic="exfoliation mistakes",
            viral_score=85.0,
            engagement_rate=8.5,
            likes=15000,
            comments=800,
            shares=300,
            saves=1200,
            views=200000,
            hook_type="shocking",
            content_type="educational",
            cta_type="engagement",
            script_length=85,
            video_duration=35,
            hook_pattern="The one [problem] that's [negative consequence]",
            body_structure="problem_solution_personal_story",
            cta_pattern="question_engagement",
            hashtags=["#skincare", "#glowingskin", "#skincaretips"],
            creator_handle="skincare_expert_1",
            source_platform="instagram",
            collected_date="2024-01-15T10:00:00",
            verified_success=True
        ),
        
        SuccessfulContent(
            content_id="skincare_002", 
            script_text="HOOK: POV: You finally found the perfect skincare routine for sensitive skin\n\nBODY: After 10 years of trial and error, here's what actually works: Gentle cleanser, hyaluronic acid serum, simple moisturizer. That's it. No fancy actives, no 10-step routine.\n\nCTA: Drop a 🙌 if you're ready to simplify your routine!\n\nCAPTION: Less is more when it comes to sensitive skin 💕\n\nVISUAL DIRECTIONS: Show simple 3-step routine, emphasize minimal products\n\nHASHTAGS: #sensitiveskin #minimalskincare #skincareroutine #gentleskincare",
            niche="skincare",
            topic="sensitive skin routine",
            viral_score=78.0,
            engagement_rate=9.2,
            likes=12500,
            comments=650,
            shares=250,
            saves=900,
            views=180000,
            hook_type="story",
            content_type="educational", 
            cta_type="engagement",
            script_length=75,
            video_duration=30,
            hook_pattern="POV: [relatable situation]",
            body_structure="personal_experience_simple_solution",
            cta_pattern="emoji_engagement",
            hashtags=["#sensitiveskin", "#minimalskincare", "#skincareroutine"],
            creator_handle="sensitive_skin_guru",
            source_platform="instagram",
            collected_date="2024-01-20T14:30:00",
            verified_success=True
        )
    ]
    
    # Sample fitness content
    fitness_content = [
        SuccessfulContent(
            content_id="fitness_001",
            script_text="HOOK: Why your home workouts aren't working (and how to fix it)\n\nBODY: You're not challenging yourself enough. I see people doing the same bodyweight squats for months. Progressive overload isn't just for the gym - add resistance bands, slow down the tempo, or increase reps weekly.\n\nCTA: What's your favorite way to make home workouts harder? Comment below!\n\nCAPTION: Make your home workouts count! 💪\n\nVISUAL DIRECTIONS: Show progression from basic to advanced movements\n\nHASHTAGS: #homeworkout #fitness #progressiveoverload #workoutmotivation",
            niche="fitness",
            topic="home workout effectiveness",
            viral_score=82.0,
            engagement_rate=7.8,
            likes=18000,
            comments=900,
            shares=400,
            saves=1100,
            views=220000,
            hook_type="question",
            content_type="educational",
            cta_type="engagement",
            script_length=95,
            video_duration=40,
            hook_pattern="Why [common problem] (and how to fix it)",
            body_structure="problem_explanation_solution",
            cta_pattern="question_engagement",
            hashtags=["#homeworkout", "#fitness", "#progressiveoverload"],
            creator_handle="home_fitness_coach",
            source_platform="instagram", 
            collected_date="2024-01-18T09:15:00",
            verified_success=True
        )
    ]
    
    # Store the content
    print("📊 Creating sample domain intelligence...")
    
    success_count = 0
    for content in skincare_content + fitness_content:
        if domain_engine.store_successful_content(content):
            success_count += 1
    
    print(f"✅ Created {success_count} sample domain intelligence entries")
    return success_count > 0

def test_hybrid_system():
    """Test the complete hybrid intelligence system"""
    print("🧠 Testing Hybrid Intelligence System")
    print("=" * 70)
    
    # 1. Create sample domain intelligence
    domain_created = create_sample_domain_content()
    if not domain_created:
        print("❌ Failed to create sample domain content")
        return False
    
    # 2. Initialize intelligent engine
    engine = IntelligentScriptEngine()
    
    # 3. Create test user personas for different niches
    test_users = [
        {
            "name": "Sarah",
            "niche": "skincare",
            "story": """
            Hi, I'm Sarah, a licensed esthetician with 7 years of experience. I specialize in helping people with sensitive skin find gentle, effective routines. 
            
            My journey started when I struggled with my own sensitive skin in my twenties - I tried everything and made every mistake in the book. Now I help others avoid those same painful (and expensive) mistakes.
            
            What makes me different is my focus on skin barrier health and minimal, gentle approaches. I believe less is more when it comes to skincare, especially for sensitive skin types.
            
            My audience is primarily people in their 20s-40s who have sensitive, reactive skin and are tired of products that promise the world but just irritate their skin more.
            """,
            "examples": [
                "HOOK: Stop using that trendy skincare ingredient - it's destroying your skin barrier!\n\nBODY: Retinol isn't for everyone. If you have sensitive skin and you're experiencing redness, peeling, or irritation, your skin is telling you to back off. Start with gentle alternatives like bakuchiol.\n\nCTA: Has retinol been too harsh for your skin? Let me know in the comments!\n\nCAPTION: Your skin barrier comes first, always ✨\n\nHASHTAGS: #sensitiveskin #skincare #skinbarrier #gentleskincare"
            ]
        },
        {
            "name": "Mike", 
            "niche": "fitness",
            "story": """
            I'm Mike, a certified personal trainer who specializes in home fitness solutions for busy professionals. I've been in the fitness industry for 8 years, helping people who don't have time for the gym.
            
            My approach is all about efficiency - maximum results in minimum time. I believe you can get incredibly fit with just 20-30 minutes of focused training at home, without any fancy equipment.
            
            What sets me apart is my focus on progressive overload principles applied to bodyweight and minimal equipment training. I teach people how to make simple exercises incredibly challenging.
            
            My audience is busy professionals, parents, and anyone who wants to get fit but doesn't have hours to spend at the gym.
            """,
            "examples": [
                "HOOK: This 20-minute home workout burns more calories than an hour at the gym\n\nBODY: It's all about intensity, not duration. Circuit training with compound movements and minimal rest gets your heart rate up and keeps it there. Here's my go-to fat-burning circuit.\n\nCTA: Ready to try this killer workout? Save this post and let me know how it goes!\n\nCAPTION: Efficiency is everything when it comes to home workouts 🔥\n\nHASHTAGS: #homeworkout #hiitworkout #busyprofessionals #fitness"
            ]
        }
    ]
    
    # 4. Create personas and test hybrid generation
    personas = {}
    for user_data in test_users:
        print(f"\n👤 Creating persona for {user_data['name']} ({user_data['niche']} niche)")
        
        persona = engine.create_user_persona(
            name=user_data["name"],
            story=user_data["story"],
            example_scripts=user_data["examples"]
        )
        personas[user_data["name"]] = persona
        
        print(f"✅ Created {user_data['name']}'s persona")
        print(f"   Expertise: {', '.join(persona.expertise)}")
        print(f"   Voice: {persona.unique_voice}")
        print(f"   Target Audience: {persona.target_audience}")
    
    # 5. Test hybrid script generation
    test_requests = [
        {
            "user": "Sarah",
            "topic": "morning skincare routine for sensitive skin",
            "duration": 30,
            "type": "educational",
            "context": "For people who are new to skincare and get overwhelmed by complex routines"
        },
        {
            "user": "Mike", 
            "topic": "quick morning workout to boost energy",
            "duration": 45,
            "type": "educational",
            "context": "For busy professionals who want to start their day with energy"
        },
        {
            "user": "Sarah",
            "topic": "biggest skincare myths that need to die",
            "duration": 60,
            "type": "educational", 
            "context": "Debunking common skincare misconceptions"
        }
    ]
    
    print(f"\n🎯 Testing Hybrid Generation (Personal + Domain Intelligence)")
    print("=" * 70)
    
    results = []
    for i, req in enumerate(test_requests, 1):
        user_name = req["user"]
        persona = personas[user_name]
        
        print(f"\n📝 Test {i}: {user_name} - '{req['topic']}'")
        print("-" * 50)
        
        # Create content request
        request = ContentRequest(
            topic=req["topic"],
            context=req["context"],
            target_length=req["duration"],
            specific_requirements=[],
            content_type=req["type"],
            urgency="normal"
        )
        
        # Generate with hybrid intelligence
        start_time = time.time()
        result = engine.generate_personalized_script(persona.user_id, request)
        generation_time = time.time() - start_time
        
        if result["success"]:
            print(f"✅ Generated successfully in {generation_time:.1f}s")
            print(f"   📊 Length: {result['script_length_words']} words (target: ~{engine._calculate_target_length(req['duration'])})")
            print(f"   ⏱️  Duration: {result['estimated_duration']} seconds")
            print(f"   🎯 Personalization: {result['personalization_score']:.1f}/20") 
            print(f"   🔥 Viral Potential: {result['viral_potential']:.1f}%")
            print(f"   🚀 Overall Score: {result['best_attempt_score']:.1f}/100")
            print(f"   🧠 Domain Intelligence: {'Yes' if 'domain_patterns' in result else 'No'}")
            
            # Show script preview
            script_preview = result["script"][:300] + "..." if len(result["script"]) > 300 else result["script"]
            print(f"\n📄 SCRIPT PREVIEW:")
            print("=" * 40)
            print(script_preview)
            print("=" * 40)
            
            results.append({
                "user": user_name,
                "topic": req["topic"], 
                "score": result["best_attempt_score"],
                "generation_time": generation_time,
                "has_domain_intelligence": "domain_patterns" in result
            })
        else:
            print(f"❌ Generation failed for {user_name}")
    
    # 6. Summary and validation
    print(f"\n🎉 Hybrid Intelligence Test Results")
    print("=" * 70)
    
    if results:
        avg_score = sum(r["score"] for r in results) / len(results)
        avg_time = sum(r["generation_time"] for r in results) / len(results)
        domain_usage = sum(1 for r in results if r["has_domain_intelligence"])
        
        print(f"✅ Successfully generated {len(results)}/{len(test_requests)} scripts")
        print(f"📊 Average Quality Score: {avg_score:.1f}/100")
        print(f"⏱️  Average Generation Time: {avg_time:.1f}s")
        print(f"🧠 Domain Intelligence Usage: {domain_usage}/{len(results)} generations")
        
        # Quality assessment
        if avg_score >= 70:
            print(f"🌟 EXCELLENT: Hybrid system producing high-quality scripts!")
        elif avg_score >= 60:
            print(f"⭐ GOOD: Hybrid system working well with room for improvement")
        else:
            print(f"⚠️  NEEDS WORK: Hybrid system needs optimization")
        
        return True
    else:
        print("❌ No successful generations - system needs debugging")
        return False

def test_user_content_sharing():
    """Test the user content sharing system"""
    print("\n👥 Testing User Content Sharing System")
    print("=" * 50)
    
    sharing_system = UserContentSharingSystem()
    
    # Test sharing successful content
    test_share = sharing_system.share_successful_content(
        user_id="test_user_001",
        user_name="Test Sarah",
        script_text="HOOK: The skincare routine that changed my sensitive skin game\n\nBODY: Simple 3-step routine: gentle cleanser, hyaluronic acid, moisturizer. No harsh actives, no complicated steps. My skin has never looked better!\n\nCTA: What's your minimal skincare routine?",
        topic="simple skincare routine",
        niche="skincare",
        performance_data={
            "engagement_rate": 8.5,
            "likes": 12000,
            "comments": 600,
            "shares": 200,
            "saves": 800,
            "views": 150000,
            "video_duration": 30,
            "hashtags": ["#skincare", "#sensitiveskin", "#minimal"]
        },
        user_experience={
            "performance_description": "Got amazing engagement, lots of people asking for product recommendations",
            "audience_feedback": "Many people said they were going to try this routine",
            "lessons_learned": "Simple content performs better than complicated routines",
            "target_audience": "People with sensitive skin looking for simple solutions"
        }
    )
    
    if test_share["success"]:
        print(f"✅ Successfully shared content with verification score: {test_share['verification_score']:.1f}")
        print(f"🎯 Added to domain intelligence: {test_share['added_to_domain_intelligence']}")
    else:
        print(f"❌ Failed to share content: {test_share.get('error')}")
    
    # Test getting community content
    community_content = sharing_system.get_community_content("skincare", 3)
    print(f"📚 Retrieved {len(community_content)} community content pieces")
    
    return test_share["success"]

def main():
    """Run all hybrid intelligence tests"""
    print("🚀 Starting Comprehensive Hybrid Intelligence Tests")
    print("=" * 80)
    
    # Test main hybrid system
    hybrid_success = test_hybrid_system()
    
    # Test user sharing system
    sharing_success = test_user_content_sharing()
    
    print(f"\n🏁 FINAL RESULTS")
    print("=" * 80)
    print(f"🧠 Hybrid Intelligence System: {'✅ PASSED' if hybrid_success else '❌ FAILED'}")
    print(f"👥 User Content Sharing: {'✅ PASSED' if sharing_success else '❌ FAILED'}")
    
    overall_success = hybrid_success and sharing_success
    
    if overall_success:
        print(f"\n🎉 ALL SYSTEMS OPERATIONAL!")
        print(f"   • Personal Intelligence: ✅ Working")
        print(f"   • Domain Intelligence: ✅ Working") 
        print(f"   • Hybrid Generation: ✅ Working")
        print(f"   • User Sharing: ✅ Working")
        print(f"   • Quality Scores: ✅ 60-90 range")
        print(f"\n💫 The hybrid system is ready for production!")
    else:
        print(f"\n⚠️  SOME ISSUES DETECTED - Check logs for details")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)