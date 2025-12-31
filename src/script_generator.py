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
    NEVER GENERATE THESE GENERIC "DARK" OR ATMOSPHERIC CONCEPTS:
    ❌ NO clouds (slow, fast, or storm clouds)
    ❌ NO rain on windows (including car windows)
    ❌ NO forests, trees, or nature (ANY kind)
    ❌ NO abstract shadows, silhouettes, or dark figures
    ❌ NO ink in water, smoke, or abstract particles
    ❌ NO ocean, water, waves (generic atmosphere)
    ❌ NO slow atmospheric/moody footage
    ❌ NO literal re-enactments of the narration
    
    
    🎯 YOU MUST ONLY USE THESE 3 TATE/MAFIA AESTHETIC CATEGORIES:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    A. 💰🔫 WEALTH/MAFIA (Use 40% of segments - Luxury, Power, Dominance):
    - 'Supercar night drive fast tracking shot dark cinematic moody'
    - 'Lamborghini headlights close up night moody 4k'
    - 'Man in suit smoking cigar low angle dark dramatic cinematic'
    - 'Private jet interior luxury leather seats fast pan cinematic'
    - 'Counting money dark hands close up fast motion dramatic lighting'
    - 'Poker chips stack close up casino dark cinematic moody'
    - 'Gold watch close up wrist luxury dark moody 4k'
    - 'Luxury car interior leather steering wheel night cinematic'
    - 'Man suit walking confident night city low angle dark'
    
    B. 🥊💪 COMBAT/GRIND (Use 35% of segments - Aggression, Strength, Hustle):
    - 'Shadow boxing dark gym silhouette fast punches low angle moody'
    - 'Boxing training intense heavy bag fast motion dark cinematic'
    - 'Man sprinting night city rain fast tracking shot dramatic'
    - 'Hoodie workout gym dark close up intense moody lighting'
    - 'Sweat face gym close up struggle dark dramatic 4k'
    - 'Heavy deadlift veins dark gym low angle cinematic'
    - 'Hooded fighter shadow dark intense eyes close up moody'
    - 'Running stairs night fast motion dark city cinematic'
    
    C. 🗿🐺 STOIC/PHILOSOPHY (Use 25% of segments - Wisdom, Nature, Timeless):
    - 'Greek statue dark museum close up marble cinematic moody'
    - 'Marble sculpture face close up dark dramatic lighting'
    - 'Lion walking savanna dusk slow motion cinematic 4k'
    - 'Wolf pack forest night dark moody cinematic'
    - 'Stormy ocean waves dark dramatic sky 4k slow motion'
    - 'Chess board dark pieces moving close up cinematic'
    - 'Ancient Roman bust marble museum dark moody 4k'
    - 'Eagle flying mountain sunset cinematic slow motion dark'
    
    🔄 3-CATEGORY ROTATION RULE (MANDATORY):
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Rotate through categories - NEVER use the same category twice in a row:
    1. WEALTH/MAFIA → 2. COMBAT/GRIND → 3. STOIC/PHILOSOPHY → (repeat)
    
    Example sequence (10 segments):
    Segment 1: WEALTH/MAFIA (Lamborghini night)
    Segment 2: COMBAT/GRIND (Shadow boxing)
    Segment 3: STOIC/PHILOSOPHY (Greek statue)
    Segment 4: WEALTH/MAFIA (Man in suit smoking)
    Segment 5: COMBAT/GRIND (Heavy deadlift)
    Segment 6: STOIC/PHILOSOPHY (Wolf pack)
    Segment 7: WEALTH/MAFIA (Poker chips)
    Segment 8: COMBAT/GRIND (Hooded fighter)
    Segment 9: STOIC/PHILOSOPHY (Stormy ocean)
    Segment 10: WEALTH/MAFIA (Private jet)
    
    ⚡ MANDATORY: COMBINE WITH "DARK CINEMATIC" OR "MOODY":
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    EVERY visual query MUST include at least ONE of these mood keywords:
    - "dark cinematic"
    - "dark moody"
    - "moody 4k"
    - "dark dramatic"
    - "cinematic moody"
    
    🎥 MANDATORY KEYWORDS IN EVERY VISUAL:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    You MUST include ALL of these elements in EVERY visual query:
    
    1. ⚡ SPEED/MOTION (Pick ONE):
       'fast motion' | 'slow motion' | 'tracking shot' | 'fast' | 'quick' | 'action'
    
    2. 🎬 CAMERA MOVEMENT (Pick ONE - BE SPECIFIC):
       'low angle' | 'close up' | 'tracking shot' | 'fast pan' | 
       'slow zoom in' | 'tilt up' | 'dolly zoom'
    
    3. 💡 CINEMATIC QUALITY (MANDATORY):
       'dark cinematic' | 'dark moody' | 'moody 4k' | 'dark dramatic' | 'cinematic moody'
    
    📐 VISUAL QUERY STRUCTURE FORMULA:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    EVERY visual MUST follow this exact format:
    
    [SUBJECT] + [ACTION] + [CAMERA MOVE] + [DARK CINEMATIC/MOODY]
    
    ✅ GOOD EXAMPLES (TATE AESTHETIC):
    - "Man in suit smoking cigar slow motion low angle dark dramatic cinematic"
    - "Shadow boxing dark gym fast punches tracking shot moody 4k"
    - "Greek statue marble close up face tilt up dark cinematic moody"
    - "Lamborghini driving night speeding city lights tracking shot 4k dark"
    - "Heavy deadlift veins popping struggle close up dark dramatic"
    - "Wolf eyes close up night forest dark cinematic moody"
    
    ❌ BAD EXAMPLES (TOO VAGUE OR FORBIDDEN):
    - "money" (Missing action, camera, lighting)
    - "car driving" (Missing dark/moody keywords)
    - "gym workout" (Too generic, no specifics)
    - "rain window" (FORBIDDEN)
    - "smoke clouds" (FORBIDDEN)
    - "tree forest" (FORBIDDEN - use wolves/animals in forest instead)
    
    The visual must convey POWER, WEALTH, WISDOM, and DOMINANCE.
    Think: TATE LIFESTYLE meets DARK PHILOSOPHER - not generic stock footage."""
    
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
    
    ✅ CORRECT VISUAL EXAMPLES (3-CATEGORY TATE AESTHETIC):
    - "Man in suit smoking cigar slow motion low angle dark dramatic cinematic"
    - "Shadow boxing dark gym fast punches tracking shot moody 4k"
    - "Greek statue marble close up face tilt up dark cinematic moody"
    - "Lamborghini driving night speeding city lights tracking shot 4k dark"
    - "Heavy deadlift veins popping struggle close up dark dramatic"
    - "Wolf eyes close up night forest dark cinematic moody"
    
    ❌ WRONG VISUAL EXAMPLES (DO NOT USE):
    - "money" (too short)
    - "car driving" (no camera, no lighting, not specific)
    - "gym workout" (too vague)
    - "rain on window" (FORBIDDEN)
    - "smoke clouds" (FORBIDDEN)
    - "tree forest" (FORBIDDEN - use wolves/animals in forest instead)
    
    CRITICAL RULES:
    - NEVER use generic phrases like "Get uncomfortable" or "Hustle hard"
    - ALWAYS name the specific theory/law
    - The Hook MUST be MAXIMUM 7 words with ending punctuation
    - EVERY visual must be a COMPLETE query with Subject + Action + Camera + Lighting
    - Rotate through the 3 categories: WEALTH/MAFIA → COMBAT/GRIND → STOIC/PHILOSOPHY
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
