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
    
    system_prompt = """You are a creative writer specializing in unsettling, creepy facts about the world, ocean, and space. 
Your job is to create viral TikTok scripts that hook viewers with disturbing truths."""
    
    user_prompt = """Create a dark, unsettling fact script for a TikTok video.

Requirements:
1. Hook: Must start with "Did you know..." or "You won't believe..." (10-15 words max)
2. Body: A scary/unsettling fact about the world, ocean, or space (approximately 40 words)
3. Visual Keywords: Provide exactly 3 search terms for dark/moody video footage (e.g., 'dark forest', 'deep ocean', 'foggy street', 'abandoned building', 'stormy night', 'dark space')

The fact should be:
- Scientifically accurate or based on real phenomena
- Genuinely unsettling or creepy
- Interesting enough to make people stop scrolling
- Related to nature, space, the ocean, or mysterious phenomena

Return ONLY a valid JSON object with this exact structure:
{
    "hook": "Your hook here...",
    "body": "Your unsettling fact here...",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}"""
    
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
        
        if len(script_data["keywords"]) != 3:
            raise ValueError("LLM must provide exactly 3 keywords")
        
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
