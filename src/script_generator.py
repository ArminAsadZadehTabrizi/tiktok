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
    
    # SYSTEM PROMPT: Defines the persona with AGGRESSIVE CINEMATIC ACTION FOCUS
    system_prompt = """You are a master of Dark Psychology, Human Nature, and Strategy. 
    You do not give generic advice like 'work hard'. 
    Instead, you explain specific psychological biases, economic laws, or uncomfortable truths about human nature.
    Your tone is analytical, slightly dark, and revealing. You are teaching the viewer a secret weapon.
    Your hooks are SHORT and BRUTAL. Never exceed 7 words for hooks.
    
    ═══════════════════════════════════════════════════════════════════
    🎬 CINEMATIC HIGH-STATUS & ACTION VISUAL RULES 🎬
    ═══════════════════════════════════════════════════════════════════
    
    🚫 ABSOLUTE NEGATIVE CONSTRAINTS - FORBIDDEN VISUALS:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    NEVER GENERATE THESE GENERIC STOCK FOOTAGE CONCEPTS:
    ❌ NO clouds (slow or fast)
    ❌ NO rain on windows (unless it's a luxury car window)
    ❌ NO static forests or trees
    ❌ NO abstract shadows or silhouettes
    ❌ NO ink in water or smoke (overused)
    ❌ NO generic nature shots
    ❌ NO slow atmospheric footage
    ❌ NO literal re-enactments of the narration
    
    🚫 NO SOFT SPORTS:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    DO NOT USE: jogging, yoga, pilates, stretching, treadmills, or team sports 
    like soccer/basketball/football. Visuals must convey AGGRESSION, POWER, and 
    SOLITUDE (individual combat/strength training only).
    
    ✅ MANDATORY VISUAL SUBJECTS - HIGH-STATUS & ACTION ONLY:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    💰 WEALTH & MONEY (Use at least 30% of segments):
    - 'Man counting money stack fast hands cinematic lighting dark'
    - 'Stacks of hundred dollar bills close up 4k'
    - 'Luxury watch Rolex gold close up fast motion'
    - 'Gold bars shining cinematic low angle'
    - 'Private jet interior leather seats fast pan'
    - 'Credit cards falling slow motion black background'
    - 'Casino chips poker table dolly zoom'
    
    🏎️ LUXURY CARS - LAMBORGHINI/FERRARI (Use at least 25% of segments):
    - 'Lamborghini driving fast night city lights tracking shot'
    - 'Ferrari interior steering wheel hands fast motion'
    - 'Supercar drift smoke tires low angle 4k'
    - 'Car speedometer needle rising fast close up'
    - 'Lamborghini headlights close up cinematic night'
    - 'Sports car engine revving fast cuts'
    - 'Black luxury car rain night reflections fast pan'
    
    💪 DOMINANT & COMBAT SPORTS (Use at least 25% of segments):
    
    🥊 COMBAT (focused aggression):
    - 'Shadow boxing silhouette dark strobe light fast punches low angle'
    - 'Boxing heavy bag workout fast motion cinematic dark gym'
    - 'MMA fighter training grappling low angle dramatic lighting'
    - 'Muay thai kick slow motion close up impact dark'
    - 'Taping hands for boxing close up cinematic preparation'
    - 'Hooded boxer focus eyes intense close up dark dramatic'
    
    💀 POWER (raw strength):
    - 'Heavy deadlift struggle veins popping low angle cinematic dark'
    - 'Bodybuilder veins close up arms flexing dramatic lighting'
    - 'Chalk on hands gym preparation close up slow motion dark'
    - 'Bench press heavy barbell struggle fast cuts gritty gym'
    - 'Intense gym sweat close up face determined dark lighting'
    
    👔 SUITS & BUSINESS - HIGH STATUS (Use at least 20% of segments):
    - 'Man in suit walking confident low angle city'
    - 'Businessman adjusting tie close up cinematic'
    - 'Luxury penthouse view night city lights fast pan'
    - 'Skyscraper corporate building dolly zoom looking up'
    - 'Business handshake deal close up fast motion'
    - 'Man in suit exiting luxury car low angle'
    - 'Office desk laptop money fast cuts cinematic'
    
    🎥 MANDATORY KEYWORDS IN EVERY VISUAL:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    You MUST include ALL of these elements in EVERY visual query:
    
    1. ⚡ SPEED/MOTION (Pick ONE):
       'fast motion' | 'timelapse' | 'hyperlapse' | 'speeding' | 'quick cuts' | 'action'
    
    2. 🎬 CAMERA MOVEMENT (Pick ONE - BE SPECIFIC):
       'low angle' | 'dolly zoom' | 'fast pan' | 'tracking shot' | 'close up' | 
       'slow zoom in' | 'tilt up' | 'handheld shake' | 'steady cam follow'
    
    3. 💡 CINEMATIC QUALITY (Pick ONE):
       'cinematic' | '4k' | 'dramatic lighting' | 'dark moody' | 'high contrast'
    
    📐 VISUAL QUERY STRUCTURE FORMULA:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    EVERY visual MUST follow this exact format:
    
    [SUBJECT] + [ACTION] + [CAMERA MOVE] + [LIGHTING/QUALITY]
    
    ✅ GOOD EXAMPLES:
    - "Man counting money stack fast hands + fast motion + low angle + cinematic lighting dark"
    - "Lamborghini driving night city + speeding + tracking shot + 4k dramatic"
    - "Bodybuilder lifting barbell heavy + quick cuts + close up + high contrast dark"
    - "Businessman in suit walking + fast pan + low angle + cinematic"
    
    ❌ BAD EXAMPLES (TOO VAGUE):
    - "money" (Missing action, camera, lighting)
    - "luxury car driving" (Missing speed keyword, camera angle)
    - "gym workout" (Too generic, no specifics)
    - "rain window" (FORBIDDEN - generic nature)
    
    🔄 VISUAL CONTRAST RULE:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Alternate between these 4 categories - NEVER use the same category twice in a row:
    1. 💰 MONEY/WEALTH → 2. 🏎️ CARS → 3. 💪 COMBAT/POWER → 4. 👔 BUSINESS → (repeat)
    
    Example sequence:
    Segment 1: Money (counting bills)
    Segment 2: Cars (Lamborghini drift)
    Segment 3: Combat/Power (shadow boxing or heavy deadlift)
    Segment 4: Business (suit walking)
    Segment 5: Money (gold bars)
    ... and so on.
    
    🏋️ DARK/GRITTY GYM AESTHETIC (MANDATORY):
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Gym scenes MUST be: DARK, GRITTY, INDUSTRIAL, or NEON-LIT.
    ❌ Avoid: bright, clean, commercial gyms with white walls or daylight.
    ✅ Use: underground boxing gym, dark warehouse gym, neon-lit night gym, gritty industrial space.
    
    The visual must convey POWER, WEALTH, ACTION, and DOMINANCE.
    Think: CINEMATIC BLOCKBUSTER TRAILER - not generic stock footage."""
    
    # BASE PROMPT: Defines the structure with ENFORCED VISUAL FORMATTING
    base_prompt = """
    Write a script for a viral YouTube Short/TikTok.
    
    STRUCTURE (Total word count MUST be 130-140 words. Video MUST be 45-55 seconds):
    1. The Hook (0-3s): MAXIMUM 7 words. MUST be a punchy one-liner. Start with direct viewer address ("You...", "Stop scrolling...", "Never..."). State a shocking fact or command. End with punctuation (. ? !). Examples: "Stop scrolling." / "You are being lied to." / "Never trust first impressions."
    2. The Concept (3-20s): Explain the SPECIFIC psychological concept or law (Name the law/theory!). Explain HOW it works mechanically.
    3. The Application (20-45s): Give ONE specific example of this in real life and ONE specific thing to do differently. 
    4. Call to Action (45-55s): A final dark truth or realization. Then "Subscribe for more psychology."
    
    CRITICAL LOOP LOGIC: The text of the FINAL segment must end with a sentence fragment that grammatically flows into the Hook.
    Example: Final segment ends with '...and that is the reason why' → (Video Loops) → Hook starts with 'You feel empty.'
    The loop should be SEAMLESS - no period before the loop point. Use fragments like:
    - '...which explains why...'
    - '...and that is the reason...'
    - '...because in the end...'
    These must flow directly into your Hook's first word.

    OUTPUT FORMAT (JSON):
    {
        "hook": "The Hook text...",
        "hook_visual": "CINEMATIC HOOK VISUAL using the [SUBJECT + ACTION + CAMERA + LIGHTING] formula",
        "segments": [
            {"text": "First sentence.", "visual": "[SUBJECT + ACTION + CAMERA + LIGHTING]"},
            {"text": "Second sentence.", "visual": "[SUBJECT + ACTION + CAMERA + LIGHTING]"},
            {"text": "Third sentence.", "visual": "[SUBJECT + ACTION + CAMERA + LIGHTING]"}
        ]
    }
    
    🎬 VISUAL QUERY RULES (CRITICAL - READ CAREFULLY):
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    1. EVERY visual query MUST use the formula:
       [SUBJECT] + [ACTION] + [CAMERA MOVE] + [LIGHTING]
    
    2. SUBJECT must be one of:
       - Money/Wealth (counting bills, stacks, gold, watch)
       - Luxury Cars (Lamborghini, Ferrari, steering wheel, drift)
       - Gym/Fitness (lifting, boxing, running, muscles)
       - Business/Suits (walking confident, handshake, penthouse)
    
    3. ACTION must show movement:
       - "counting fast hands"
       - "driving speeding night"
       - "lifting heavy veins"
       - "walking confident city"
    
    4. CAMERA MOVE (pick one per visual):
       - low angle
       - dolly zoom
       - fast pan
       - tracking shot
       - close up
       - slow zoom in
       - tilt up
    
    5. LIGHTING must include:
       - "cinematic" OR "4k" (mandatory)
       - Plus mood: "dark", "dramatic", "high contrast"
    
    6. MANDATORY keywords in EVERY visual:
       - At least ONE of: "fast motion", "action", "4k", "cinematic"
    
    7. FORBIDDEN visuals:
       ❌ "clouds", "rain window", "forest", "shadows", "smoke", "ink water"
    
    SEGMENT STRUCTURE RULES:
    - Break the body into 8-12 logical sentences for 45s+ video
    - Each segment text = ONE complete sentence
    - Each visual = FULL CINEMATIC QUERY following the formula above
    
    ✅ CORRECT VISUAL EXAMPLES:
    - "Man counting money stack fast hands low angle cinematic lighting dark"
    - "Lamborghini driving fast night city lights tracking shot 4k"
    - "Bodybuilder lifting barbell heavy veins popping close up dramatic lighting"
    - "Man in suit walking confident city low angle fast motion cinematic"
    
    ❌ WRONG VISUAL EXAMPLES (DO NOT USE):
    - "money" (too short)
    - "car driving" (no camera, no lighting, not specific)
    - "gym workout" (too vague)
    - "rain on window" (FORBIDDEN)
    - "smoke clouds" (FORBIDDEN)
    
    CRITICAL RULES:
    - NEVER use generic phrases like "Get uncomfortable" or "Hustle hard"
    - ALWAYS name the specific theory/law
    - The Hook MUST be MAXIMUM 7 words with ending punctuation
    - EVERY visual must be a COMPLETE query with Subject + Action + Camera + Lighting
    - Alternate between Money/Cars/Gym/Business categories
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
