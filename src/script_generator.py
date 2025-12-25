"""LLM-powered script generator for Dark Facts videos"""
import json
from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)


def generate_script():
    """
    Generate a 3-part script for a Dark Facts video using LLM.
    
    Returns:
        dict: Contains 'hook', 'body', and 'keywords' for the video
    """
    
    system_prompt = """You are a Master Storyteller for 'Dark Facts' videos. 
    Your goal is to write scripts that keep viewers watching for at least 65 seconds.
    Use simple, spoken English. No complex sentences.
    Focus on: Mystery, Fear, and Curiosity."""
    
    user_prompt = """Write a script for a TikTok video about a scary/dark fact.
    
    STRUCTURE (Total ~170 words):
    1. The Hook (0-8s): A terrifying question or statement.
    2. The Context (8-20s): Where and when? Set the scene atmospherically.
    3. The Details (20-50s): 3 distinct, unsettling details. Build the tension.
    4. The Mindblow (50-60s): The scariest realization or twist.
    5. CTA (60s+): "Follow for more dark files."

    OUTPUT FORMAT (JSON):
    {
        "hook": "The Hook text only...",
        "body": "The Context text. The Details text. The Mindblow text. The CTA.",
        "keywords": ["visual1", "visual2", "visual3", "visual4", "visual5", "visual6", "visual7", "visual8"]
    }
    
    CRITICAL RULES:
    - The 'body' MUST be long enough to last 50-60 seconds when read aloud.
    - Provide 8 visual keywords (since the video is longer).
    - Keywords must be CONCRETE VISUALS (e.g. 'stormy ocean night', 'abandoned hospital hallway')."""
    
    try:
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=config.LLM_TEMPERATURE,
            response_format={"type": "json_object"}
        )
        
        script_data = json.loads(response.choices[0].message.content)
        
        # Validate the response
        required_keys = ["hook", "body", "keywords"]
        if not all(key in script_data for key in required_keys):
            raise ValueError("LLM response missing required keys")
        
        if len(script_data["keywords"]) < 3:
            raise ValueError("LLM must provide at least 3 keywords")
        
        print(f"✓ Script generated successfully")
        print(f"  Hook: {script_data['hook']}")
        print(f"  Keywords: {', '.join(script_data['keywords'])}")
        
        return script_data
    
    except Exception as e:
        print(f"✗ Error generating script: {e}")
        raise


if __name__ == "__main__":
    # Test the script generator
    script = generate_script()
    print("\nGenerated Script:")
    print(json.dumps(script, indent=2))
