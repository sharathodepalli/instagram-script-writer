#!/usr/bin/env python3
"""
Test the Intelligent Script Engine
"""

import sys
sys.path.append('.')

from src.intelligent_script_engine import IntelligentScriptEngine, ContentRequest

def test_engine():
    """Test the intelligent engine with realistic data"""
    
    print("🧠 Testing Intelligent Script Engine...")
    print("="*60)
    
    # Test story - realistic user
    story = """
    Hi, I'm Alex! I'm a marketing professional turned content creator. 
    I've been working in digital marketing for 8 years and recently started sharing 
    my knowledge about social media growth, content strategy, and personal branding.
    
    My journey started when I helped my previous company grow from 1K to 100K followers 
    in just 6 months. Now I teach busy entrepreneurs and small business owners how to 
    create content that actually converts.
    
    What makes me different is that I focus on practical, no-BS strategies that work 
    even if you only have 30 minutes a day. I've been there - working 60-hour weeks 
    and trying to build a personal brand on the side. I know what actually works 
    when you're short on time but big on ambition.
    """
    
    # Example scripts from this user
    example_scripts = [
        """
        HOOK: Stop posting content that nobody cares about! Here's the 3-second rule that changed everything.

        BODY: I used to spend hours creating content that got 12 likes. Then I learned this: if you can't grab attention in 3 seconds, you've lost them forever. Now every post I create passes the 3-second test. Here's how: Start with a problem they're thinking about right now, promise a simple solution, and deliver it fast.

        CTA: Try the 3-second test on your next post and comment your results below!

        CAPTION: The 3-second rule that saves your content ⏰ Who's trying this?

        VISUAL DIRECTIONS: Show stopwatch, demonstrate bad vs good hooks, use text overlays for the rule

        HASHTAGS: #ContentCreator #SocialMediaTips #ContentMarketing #DigitalMarketing #ContentStrategy #SocialMediaGrowth #ContentTips #MarketingHacks
        """,
        
        """
        HOOK: I gained 50K followers using this posting schedule that nobody talks about.

        BODY: Everyone says "post consistently" but they don't tell you WHEN to post for maximum impact. After analyzing my best-performing posts, I discovered the golden window: 7 AM, 1 PM, and 7 PM in your audience's timezone. But here's the secret - it's not about the time, it's about catching people during their daily breaks. Morning coffee, lunch break, evening wind-down.

        CTA: What time do you usually post? Let me know if you're willing to try this schedule!

        CAPTION: The posting schedule that got me 50K followers 📈 Save this!

        VISUAL DIRECTIONS: Show calendar with optimal times highlighted, demonstrate phone usage patterns, include before/after analytics

        HASHTAGS: #SocialMediaGrowth #ContentStrategy #InstagramTips #ContentCreator #SocialMediaMarketing #InfluencerTips #ContentPlanning #DigitalMarketing
        """
    ]
    
    try:
        # Initialize engine
        engine = IntelligentScriptEngine()
        
        # Create persona
        print("🔍 Creating intelligent persona...")
        persona = engine.create_user_persona("Alex", story, example_scripts)
        
        print(f"✅ Created persona for {persona.name}")
        print(f"   Expertise: {', '.join(persona.expertise)}")
        print(f"   Voice Style: {persona.unique_voice}")
        print(f"   Target Audience: {persona.target_audience}")
        print(f"   Optimal Length: {persona.optimal_script_length} words")
        
        # Test different script requests
        test_requests = [
            {
                "topic": "how to create viral Instagram reels",
                "duration": 30,
                "context": "For small business owners who are new to reels",
                "type": "educational"
            },
            {
                "topic": "biggest mistake people make on social media",
                "duration": 45,
                "context": "Something that will get people to stop scrolling",
                "type": "educational"
            },
            {
                "topic": "my content creation morning routine",
                "duration": 60,
                "context": "Share personal workflow that others can copy",
                "type": "inspirational"
            }
        ]
        
        for i, req in enumerate(test_requests, 1):
            print(f"\n📝 Test {i}: Generating script for '{req['topic']}'")
            print("-" * 40)
            
            # Create request
            request = ContentRequest(
                topic=req["topic"],
                context=req["context"],
                target_length=req["duration"],
                specific_requirements=[],
                content_type=req["type"],
                urgency="normal"
            )
            
            # Generate script
            result = engine.generate_personalized_script(persona.user_id, request)
            
            if result["success"]:
                print(f"✅ Generated successfully!")
                print(f"   📊 Length: {result['script_length_words']} words (target: ~{engine._calculate_target_length(req['duration'])})")
                print(f"   ⏱️  Duration: {result['estimated_duration']} seconds")
                print(f"   🎯 Personalization: {result['personalization_score']:.1f}/20")
                print(f"   🔥 Viral Potential: {result['viral_potential']:.1f}%")
                print(f"   🚀 Overall Score: {result['best_attempt_score']:.1f}/100")
                
                print(f"\n📄 GENERATED SCRIPT:")
                print("="*50)
                print(result["script"])
                print("="*50)
            else:
                print(f"❌ Generation failed for test {i}")
        
        print(f"\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_engine()