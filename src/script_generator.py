"""LLM-powered script generator for Self-Improvement / Motivation videos"""
import openai
import json
import os
import random
import config

# VIRAL EVERGREEN TOPICS: High-performing hooks for Stoic/Success niche
VIRAL_TOPICS = [
    "The power of disappearing for 6 months (Ghost Mode)",
    "Why you should never tell people your plans",
    "The psychology of silence",
    "Why waking up late is ruining your life",
    "Signs your friends are actually your enemies",
    "The cost of discipline vs the cost of regret",
    "How to detach from emotions like a Stoic",
    "The 1% Rule: Why you are still average",
    "Dopamine Detox: Reset your brain",
    "Why comfort is the enemy of growth",
    "The truth about being alone",
    "Why suffering makes you stronger",
    "Stop seeking validation from others",
    "The midnight law: Why winners work while others sleep",
    "How to become unrecognizable in 90 days"
]

def generate_script(topic=None):
    print("📝 Step 1: Generating motivational script")
    
    # SYSTEM PROMPT: Defines the persona
    system_prompt = """You are an Elite Performance Coach and Stoic Philosopher.
    Your goal is to write scripts that inspire action and keep viewers watching for at least 60 seconds.
    Use simple, direct, powerful language. Short sentences. Maximum impact.
    Tone: Authoritative, inspiring, masculine, no-nonsense.
    Focus on: Self-Improvement, Wealth Building, Mental Strength, Peak Performance.
    NO DATES or YEARS in keywords (e.g. use 'modern gym', NOT '2023 gym')."""
    
    # BASE PROMPT: Defines the structure (No f-strings here to avoid JSON conflicts)
    base_prompt = """
    Write a script for a viral YouTube Shorts/TikTok video about self-improvement, motivation, or wealth building.
    
    STRUCTURE (Total word count MUST be 130-140 words. Video MUST be under 55 seconds):
    1. The Hook (0-3s): Short, brutal question. Direct hit. (e.g., "Why are you still broke?" / "Wake up.")
    2. The Pain (3-15s): The painful reality. Why they are failing right now.
    3. The Solution (15-45s): Fast-paced, actionable advice. What they MUST do to change. Be concise and powerful.
    4. Call to Action (45-50s): "Subscribe for wealth." Short and commanding.

    OUTPUT FORMAT (JSON):
    {
        "hook": "The Hook text only...",
        "body": "The Pain text. The Solution text. The CTA.",
        "keywords": ["visual1", "visual2", "visual3", "visual4", "visual5", "visual6", "visual7", "visual8"]
    }
    
    CRITICAL RULES:
    - Total word count MUST be between 130-140 words exactly. The video MUST be under 55 seconds to fit YouTube Shorts limits.
    - Provide 8 visual keywords.
    - Keywords MUST be CONCRETE NOUNS from these categories ONLY: "Luxury", "Gym", "Nature", "Old Money", "Office", "Cyberpunk City".
    - Examples: 'luxury sports car', 'modern gym equipment', 'mountain peak sunrise', 'elegant office desk', 'neon city skyline', 'tailored suit'.
    - Do NOT use abstract concepts (e.g. 'success', 'motivation', 'wealth'). Use PHYSICAL OBJECTS and PLACES ONLY.
    - Do NOT use specific years in keywords.
    """

    # DYNAMIC TOPIC INSERTION
    if topic:
        print(f"  🎯 Using Custom Topic: {topic}")
        selected_topic = topic
    else:
        # Randomly select from viral topics list
        selected_topic = random.choice(VIRAL_TOPICS)
        print(f"  🎲 Selected Viral Topic: {selected_topic}")
    
    user_prompt = base_prompt + f"\n\nTOPIC: Write the script SPECIFICALLY about this: '{selected_topic}'. Make it powerful and viral."

    try:
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        script_data = json.loads(content)
        
        print("  ✓ Script generated successfully")
        print(f"  Hook: {script_data['hook']}")
        print(f"  Keywords: {', '.join(script_data['keywords'])}")
        
        return script_data
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        raise
