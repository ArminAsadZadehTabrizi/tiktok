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
    Your tone is analytical, slightly dark, and revealing. You are teaching the viewer a secret weapon."""
    
    # BASE PROMPT: Defines the structure (No f-strings here to avoid JSON conflicts)
    base_prompt = """
    Write a script for a viral YouTube Short/TikTok.
    
    STRUCTURE (Total word count MUST be 130-140 words. Video MUST be under 55 seconds):
    1. The Hook (0-3s): State a counter-intuitive fact or question. (e.g. "Your friends secretly want you to fail.")
    2. The Concept (3-20s): Explain the SPECIFIC psychological concept or law (Name the law/theory!). Explain HOW it works mechanically.
    3. The Application (20-45s): Give ONE specific example of this in real life and ONE specific thing to do differently. 
    4. Call to Action (45-55s): A final dark truth or realization. Then "Subscribe for more psychology."

    OUTPUT FORMAT (JSON):
    {
        "hook": "The Hook text...",
        "body": "The Concept text. The Application text. The CTA.",
        "keywords": ["visual1", "visual2", "visual3", "visual4", "visual5", "visual6", "visual7", "visual8"]
    }
    
    CRITICAL RULES:
    - NEVER use generic phrases like "Get uncomfortable", "Embrace the grind", or "Hustle hard".
    - ALWAYS name the specific theory/law (e.g. "This is called the Spotlight Effect").
    - Keywords MUST be CONCRETE NOUNS (e.g., 'chess board', 'mirror', 'wolf pack', 'ancient statue', 'stormy ocean'). No abstract concepts.
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
