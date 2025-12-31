"""LLM-powered script generator for Self-Improvement / Motivation videos"""
import openai
import json
import os
import random
import config

# DARK PSYCHOLOGY & HUMAN NATURE TOPICS: Specific psychological theories and paradoxes
VIRAL_TOPICS = [
    "The Crab Bucket Theory (Why friends hold you back)",
    "The Ben Franklin Effect (How to make enemies like you)",
    "The Spotlight Effect (Nobody actually cares about you)",
    "The Sunk Cost Fallacy (Why you stay in bad relationships)",
    "Parkinson's Law (Why you waste time)",
    "The 80/20 Rule (Pareto Principle) applied to social life",
    "The Doorway Effect (Why you forget things entering a room)",
    "Stoicism: Memento Mori (The power of remembering death)",
    "Dark Psychology: Triangulation in relationships"
]

def generate_script(topic=None):
    print("📝 Step 1: Generating motivational script")
    
    # SYSTEM PROMPT: Defines the persona
    system_prompt = """You are a master of Dark Psychology, Human Nature, and Strategy. 
    You do not give generic advice like 'work hard'. 
    Instead, you explain specific psychological biases, economic laws, or uncomfortable truths about human nature.
    Your tone is analytical, slightly dark, and revealing. You are teaching the viewer a secret weapon.
    Your hooks are SHORT and BRUTAL. Never exceed 7 words for hooks.
    
    CRITICAL: For every sentence, generate a specific, concrete visual search query for stock footage (Pexels/Pixabay style). 
    Describe the scene, lighting, and subject. Think cinematically: 'lonely man walking in crowd blur' not 'loneliness'.
    Use concrete nouns and visual descriptors, not abstract concepts."""
    
    # BASE PROMPT: Defines the structure (No f-strings here to avoid JSON conflicts)
    base_prompt = """
    Write a script for a viral YouTube Short/TikTok.
    
    STRUCTURE (Total word count MUST be 130-140 words. Video MUST be under 55 seconds):
    1. The Hook (0-3s): MAXIMUM 7 words. MUST be a punchy one-liner. Start with direct viewer address ("You...", "Stop scrolling...", "Never..."). State a shocking fact or command. End with punctuation (. ? !). Examples: "Stop scrolling." / "You are being lied to." / "Never trust first impressions."
    2. The Concept (3-20s): Explain the SPECIFIC psychological concept or law (Name the law/theory!). Explain HOW it works mechanically.
    3. The Application (20-45s): Give ONE specific example of this in real life and ONE specific thing to do differently. 
    4. Call to Action (45-55s): A final dark truth or realization. Then "Subscribe for more psychology."
    
    CRITICAL: The script MUST be a perfect loop. The last sentence must NOT be a goodbye or Call to Action. It must grammatically lead back into the Hook. Example End: 'And that is the terrifying reason...' (Loops to Start) '...why you are always tired.'

    OUTPUT FORMAT (JSON):
    {
        "hook": "The Hook text...",
        "hook_visual": "specific visual search query for the hook (e.g., 'alarm clock ringing close up dark')",
        "segments": [
            {"text": "First sentence of concept.", "visual": "specific visual search (e.g., 'lonely man walking in crowd blur')"},
            {"text": "Second sentence explaining mechanism.", "visual": "another specific visual (e.g., 'theater spotlight on dark stage')"},
            {"text": "Application example.", "visual": "concrete scene description"},
            {"text": "Final realization/CTA.", "visual": "closing visual scene"}
        ]
    }
    
    SEGMENT STRUCTURE RULES:
    - Break the body into 4-6 logical sentences (Concept → Mechanism → Application → CTA)
    - Each segment text should be ONE complete sentence (not a word, not a paragraph)
    - Each segment visual should be a CONCRETE search query for stock footage
    - Visual queries MUST describe actual filmable scenes: lighting, subjects, actions, mood
    - Example good visuals: "shadow boxing strobe light dark", "person running night street backlight", "gym weights close up sweat"
    - Example bad visuals: "motivation", "success", "loneliness" (too abstract for search)
    
    CRITICAL RULES:
    - NEVER use generic phrases like "Get uncomfortable", "Embrace the grind", or "Hustle hard".
    - ALWAYS name the specific theory/law (e.g. "This is called the Spotlight Effect").
    - Segment visuals MUST be CONCRETE, FILMABLE scenes matching Dark Discipline/Training aesthetic
    - Good visual examples: 'shadow boxing strobe light dark', 'hooded figure rain night street', 'gym workout intense sweat dark'
    - Bad visual examples: 'motivation', 'success', 'discipline' (too abstract - not searchable on stock sites)
    - The Hook MUST be MAXIMUM 7 words and formatted as a complete sentence with ending punctuation.
    - The Hook MUST be punchy and direct. Think: "Stop scrolling." or "You are being manipulated." - short, brutal, immediate.
    - The Hook MUST grab attention by directly addressing the viewer with "You", "Stop", "Never", or similar direct commands.
    - Each segment visual should describe: SUBJECT + ACTION/POSE + LIGHTING/MOOD (e.g., "person running" + "night backlight dark")
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
        print(f"  Hook Visual: {script_data.get('hook_visual', 'N/A')}")
        print(f"  Segments: {len(script_data.get('segments', []))} sentence(s)")
        
        return script_data
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        raise
