#!/usr/bin/env python
"""Add sample Instagram scripts to Pinecone index."""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ingest import ScriptIngester
from langchain.schema import Document

def create_sample_scripts():
    """Create sample Instagram scripts."""
    sample_scripts = [
        {
            "content": """
HOOK: Ready for the secret to glowing skin? ✨

BODY: 
Start your day with a gentle cleanser - it's like giving your face a fresh start! 
Follow up with vitamin C serum for that natural glow.
Don't forget SPF - your future self will thank you!
And here's the game changer: drink water like it's your job! 💧

CTA: What's your go-to skincare tip? Drop it below! 👇

CAPTION: Glowing skin secrets revealed! ✨ #skincare #glowup #beauty

VISUAL DIRECTIONS: Close-up shots of skincare routine, natural lighting

HASHTAGS: #skincare #beauty #glowup #selfcare #skincareroutine #beautytips #healthyskin
            """,
            "metadata": {"source_file": "skincare_routine.txt", "category": "beauty"}
        },
        {
            "content": """
HOOK: This morning routine will change your life! 🌅

BODY:
Wake up 15 minutes earlier - trust me on this one.
Hydrate first thing with a big glass of water 💧
5-minute stretch or yoga to wake up your body
Write down 3 things you're grateful for
Set your top 3 priorities for the day

CTA: Which tip are you going to try tomorrow? Let me know! 

CAPTION: Morning routine that actually works ⏰ #morningroutine #productivity

VISUAL DIRECTIONS: Time-lapse of morning routine, soft morning light

HASHTAGS: #morningroutine #productivity #selfcare #wellness #mindfulness #goodvibes #motivation
            """,
            "metadata": {"source_file": "morning_routine.txt", "category": "lifestyle"}
        },
        {
            "content": """
HOOK: POV: You just discovered the easiest dinner hack 🍽️

BODY:
Sheet pan dinners are your new best friend!
Throw veggies and protein on one pan
Season everything with olive oil, salt, and herbs
Pop it in the oven for 25 minutes
Boom! Dinner is served with minimal cleanup 🙌

CTA: What's your favorite easy dinner recipe? Share below!

CAPTION: Dinner made simple! Who else loves one-pan meals? 🍳 #cooking #easydinner

VISUAL DIRECTIONS: Overhead shots of food prep, final plated dish

HASHTAGS: #cooking #easydinner #foodhacks #dinnerideas #healthyeating #mealprep #quickmeals
            """,
            "metadata": {"source_file": "easy_dinner.txt", "category": "food"}
        },
        {
            "content": """
HOOK: The workout that takes only 15 minutes but hits EVERYTHING! 💪

BODY:
No gym? No problem! All you need is your body weight.
Start with 30 seconds each:
- Jumping jacks (cardio boost)
- Push-ups (upper body power)
- Squats (leg day vibes)
- Plank (core strength)
Repeat 3 rounds and you're done!

CTA: Did you try it? How did it feel? Tell me in the comments! 

CAPTION: 15-min full body workout ✅ No equipment needed! #homeworkout #fitness

VISUAL DIRECTIONS: Split screen showing correct form for each exercise

HASHTAGS: #homeworkout #fitness #quickworkout #bodyweight #fitnessmotivation #exercise #healthylifestyle
            """,
            "metadata": {"source_file": "quick_workout.txt", "category": "fitness"}
        },
        {
            "content": """
HOOK: This organization hack will save you 30 minutes every morning! ⏰

BODY:
Sunday prep is the secret sauce!
Lay out your outfits for the entire week
Prep your breakfast containers 
Set up your work bag the night before
Make a quick to-do list for Monday
Your future self will be SO grateful 🙏

CTA: What's your best organization tip? Drop it below! 

CAPTION: Sunday prep = stress-free week ahead! 📋 #organization #productivity

VISUAL DIRECTIONS: Aesthetic flat lay of organized items, time-lapse of prep

HASHTAGS: #organization #productivity #sundayprep #lifehacks #organized #planning #efficiency
            """,
            "metadata": {"source_file": "organization.txt", "category": "productivity"}
        }
    ]
    
    return sample_scripts

def add_scripts_to_index():
    """Add sample scripts to Pinecone index."""
    try:
        print("🚀 Adding sample scripts to Pinecone index...")
        
        # Create ingester
        ingester = ScriptIngester()
        
        # Get sample scripts
        sample_scripts = create_sample_scripts()
        
        # Convert to Document objects
        documents = []
        for script_data in sample_scripts:
            doc = Document(
                page_content=script_data["content"],
                metadata=script_data["metadata"]
            )
            documents.append(doc)
        
        print(f"📝 Adding {len(documents)} sample scripts...")
        
        # Add to index using ingest_documents method
        result = ingester.ingest_documents(documents)
        
        if result["success"]:
            print(f"✅ Successfully added {result['documents_processed']} scripts to the index!")
            print(f"📊 Total chunks created: {result['chunks_created']}")
        else:
            print(f"❌ Failed to add scripts: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function."""
    print("📚 Setting up sample Instagram scripts for your index...")
    add_scripts_to_index()
    print("\n🎉 Setup complete! You can now use retrieval-augmented generation.")

if __name__ == "__main__":
    main()
