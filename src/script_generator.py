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
    system_prompt = """You are NOT a teacher. You are a ruthless mentor waking up a sleeping soldier. Your language is sharp, absolute, and offensive to the weak.
    You are a master of Dark Psychology, Human Nature, and Strategy. 
    You do not give generic advice like 'work hard'. 
    Instead, you explain specific psychological biases, economic laws, or uncomfortable truths about human nature.
    Your tone is analytical, slightly dark, and revealing. You are teaching the viewer a secret weapon.
    Your hooks are SHORT and BRUTAL. Never exceed 7 words for hooks.
    
    ═══════════════════════════════════════════════════════════════════
    🎬 CINEMATIC HIGH-STATUS & ACTION VISUAL RULES 🎬
    ═══════════════════════════════════════════════════════════════════
    
    🚫 ABSOLUTE NEGATIVE CONSTRAINTS - HARD BAN LIST:
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
    ❌ NO guns, drugs, dirty rooms, grunge, horror, or prison cells
    
    🚫 HARD BAN - FOOD & CONSUMPTION:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ❌ NO food of any kind (chocolate, candy, sweets, eating, restaurants)
    ❌ NO drugs or substances
    ❌ NO alcohol consumption (champagne pouring is OK as a LUXURY STATUS symbol ONLY)
    
    🚫 HARD BAN - SOFT ANIMALS:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ❌ NO small animals (birds, rabbits, squirrels, pets)
    ❌ NO cute/soft animals of ANY kind
    ✅ ONLY ALLOW: Lion, Wolf, Doberman, Snake, Black Panther - and ONLY in dark/aggressive/night settings
    
    🚫 HARD BAN - BRIGHT & CHEERFUL:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ❌ NO bright daylight, blue sky, green grass
    ❌ NO flowers, gardens, or happy families
    ❌ NO cheerful/uplifting/positive vibes
    
    🎯 VISUAL TRANSLATION RULE (CRITICAL):
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Visuals must represent STATUS and POWER, NOT the literal word.
    
    ❌ WRONG: Text mentions "pleasure" → Shows chocolate/food
    ✅ CORRECT: Text mentions "pleasure" → Shows "Man checking luxury Patek Philippe watch stoic dark office 4k expensive"
    
    ❌ WRONG: Text mentions "temptation" → Shows candy/sweets
    ✅ CORRECT: Text mentions "temptation" → Shows "Counting money hands close up night luxury expensive 4k"
    
    ❌ WRONG: Text mentions "addiction" → Shows drugs/alcohol
    ✅ CORRECT: Text mentions "addiction" → Shows "Man staring stoically dark luxury penthouse night expensive 4k"
    
    RULE: If the text is abstract or metaphorical, translate it into POWER VISUALS (wealth, discipline, dominance).
    
    🎯 DARKNESS FROM CONTRAST, NOT GRIME: Use premium black backgrounds, night cityscapes, and high-contrast luxury settings.
    
    
    🎯 YOU MUST ONLY USE THESE 3 ULTRA-LUXURY AESTHETIC CATEGORIES:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    A. 💎🏆 ULTRA-LUXURY & STATUS (Use 40% of segments - Extreme Wealth, High Status, Power):
    - 'Bugatti interior leather seats night luxury 4k cinematic expensive'
    - 'Ferrari dashboard close up night city lights luxury 4k'
    - 'Dubai skyline night skyscrapers luxury cinematic 4k expensive'
    - 'Monaco yacht harbor sunset luxury boats 4k cinematic'
    - 'Private jet leather seats close up luxury expensive 4k'
    - 'Rolls Royce steering wheel close up night luxury 4k'
    - 'Penthouse view night city lights luxury expensive cinematic'
    - 'Man bespoke suit checking Rolex watch luxury close up 4k'
    - 'Champagne pouring luxury glass slow motion expensive 4k'
    - 'Luxury penthouse interior marble gold accents 4k expensive'
    
    B. 🥊⚡ COMBAT & DISCIPLINE (Use 35% of segments - Professional Training, Power, Focus):
    - 'Kickboxing training professional gym discipline 4k luxury'
    - 'Heavy bag workout shirtless muscles slow motion luxury gym 4k'
    - 'Sprinting hill night city lights discipline luxury 4k'
    - 'Shadow boxing luxury gym mirrors professional 4k expensive'
    - 'Boxing gloves close up taping hands discipline luxury 4k'
    - 'Athletic training professional focus intensity luxury gym 4k'
    - 'Bodybuilder posing luxury gym professional 4k expensive'
    - 'Martial arts training professional discipline luxury 4k'
    
    C. 🏛️♟️ STOIC & OLD MONEY (Use 25% of segments - Wisdom, Timeless Elegance, Class):
    - 'Greek statue marble museum close up luxury 4k expensive'
    - 'Classic architecture marble columns night luxury 4k cinematic'
    - 'Chess board marble pieces close up dark luxury 4k expensive'
    - 'Dark library leather books shadows luxury 4k expensive cinematic'
    - 'Marble statue in shadows dramatic lighting luxury 4k expensive'
    - 'Chess board close up night luxury expensive 4k cinematic'
    - 'Classic architecture night moonlight luxury expensive 4k'
    - 'Ancient Roman bust marble dramatic shadows luxury 4k expensive'
    - 'Lion walking dark night luxury 4k cinematic'
    - 'Wolf eyes close up night dark luxury 4k expensive'
    
    🔄 3-CATEGORY ROTATION RULE (MANDATORY):
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Rotate through categories - NEVER use the same category twice in a row:
    1. ULTRA-LUXURY & STATUS → 2. COMBAT & DISCIPLINE → 3. STOIC & OLD MONEY → (repeat)
    
    Example sequence (10 segments):
    Segment 1: ULTRA-LUXURY & STATUS (Bugatti interior)
    Segment 2: COMBAT & DISCIPLINE (Kickboxing professional)
    Segment 3: STOIC & OLD MONEY (Greek statue)
    Segment 4: ULTRA-LUXURY & STATUS (Dubai skyline night)
    Segment 5: COMBAT & DISCIPLINE (Heavy bag workout)
    Segment 6: STOIC & OLD MONEY (Dark library shadows)
    Segment 7: ULTRA-LUXURY & STATUS (Monaco yacht harbor)
    Segment 8: COMBAT & DISCIPLINE (Shadow boxing luxury gym)
    Segment 9: STOIC & OLD MONEY (Classic architecture night)
    Segment 10: ULTRA-LUXURY & STATUS (Penthouse view)
    
    🌙 FORCE NIGHT/DARK MODE:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    80% of visuals should include the keyword "night" or "dark" to maintain the aesthetic.
    Even luxury and combat shots should prioritize night settings whenever possible.
    
    ⚡ MANDATORY: COMBINE WITH LUXURY QUALITY KEYWORDS:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    EVERY visual query MUST include at least TWO of these high-quality keywords:
    - "luxury"
    - "expensive"
    - "4k"
    - "cinematic"
    - "premium"
    
    This filters out low-quality stock footage and ensures premium aesthetic.
    
    🎥 MANDATORY KEYWORDS IN EVERY VISUAL:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    You MUST include ALL of these elements in EVERY visual query:
    
    1. ⚡ SPEED/MOTION (Pick ONE):
       'fast motion' | 'slow motion' | 'tracking shot' | 'fast' | 'quick' | 'action'
    
    2. 🎬 CAMERA MOVEMENT (Pick ONE - BE SPECIFIC):
       'low angle' | 'close up' | 'tracking shot' | 'fast pan' | 
       'slow zoom in' | 'tilt up' | 'dolly zoom'
    
    3. 💎 LUXURY QUALITY (MANDATORY - Pick TWO):
       'luxury' | 'expensive' | '4k' | 'cinematic' | 'premium'
    
    📐 VISUAL QUERY STRUCTURE FORMULA:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    EVERY visual MUST follow this exact format:
    
    [SUBJECT] + [ACTION] + [CAMERA MOVE] + [DARK CINEMATIC/MOODY]
    
    ✅ GOOD EXAMPLES (ULTRA-LUXURY AESTHETIC):
    - "Bugatti interior leather seats night luxury expensive 4k cinematic"
    - "Kickboxing training professional gym discipline luxury 4k expensive"
    - "Greek statue marble close up museum luxury expensive 4k"
    - "Dubai skyline night skyscrapers luxury expensive cinematic 4k"
    - "Heavy bag workout shirtless muscles luxury gym 4k expensive"
    - "Monaco yacht harbor luxury boats sunset cinematic 4k expensive"
    
    ❌ BAD EXAMPLES (TOO VAGUE OR FORBIDDEN):
    - "money" (Missing action, camera, luxury keywords)
    - "car driving" (no luxury brand, no 4k/expensive keywords)
    - "gym workout" (too vague, missing luxury/expensive)
    - "rain window" (FORBIDDEN)
    - "guns" (FORBIDDEN)
    - "prison cells" (FORBIDDEN)
    
    The visual must convey EXTREME WEALTH, DISCIPLINE, TIMELESS CLASS, and HIGH STATUS.
    Think: BILLIONAIRE LIFESTYLE + PROFESSIONAL ATHLETE + OLD MONEY - not crime movies or generic stock footage."""
    
    # BASE PROMPT: Defines the structure with ENFORCED VISUAL FORMATTING
    base_prompt = """
    Write a script for a viral YouTube Short/TikTok.
    
    STRUCTURE (Total word count MUST be 130-140 words. Video MUST be 45-55 seconds):
    1. The Hook (0-3s): MAXIMUM 7 words. MUST be a "Pattern Interrupt" or "Status Attack".
       - RULES:
         - DO NOT use generic openers like "Did you know".
         - ATTACK the viewer's status quo ("You are weak", "You stay poor").
         - Or REVEAL a conspiracy ("They lied to you", "The Matrix is real").
         - MUST trigger an immediate emotional response (Anger, Fear, Ambition).
       - EXAMPLES:
         - "Poverty is a choice."
         - "Your friends secretly hate you."
         - "You are being programmed."
         - "Stop being a victim."
         - "They want you weak."
    2. The Concept (5-10s):
       - EXPLAIN the dark truth immediately.
       - RULE: Use SHORT sentences (Max 10 words).
       - RULE: No passive voice. Use active, aggressive verbs.
       - RULE: No moralizing (\"It's bad to...\"). State facts (\"Poverty is a sin.\").
       - STYLE: Staccato rhythm. \"They lied to you. Money is freedom. You are a slave.\"
    
    3. The Application (10-20s):
       - GIVE 3 actionable, ruthless steps.
       - FORMAT: \"Step 1: [Command]. Step 2: [Command]. Step 3: [Command].\"
       - RULE: Use Imperatives. \"Cut them off.\" \"Build the business.\" \"Train daily.\"
       - NO \"Try to\" or \"You should\". ONLY \"Do\". 
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
       - Ultra-Luxury (Bugatti/Ferrari/Rolls Royce interior, Dubai skyline, Monaco harbor, Penthouse)
       - High-Status Fashion (Bespoke suit, Rolex watch, designer items)
       - Professional Training (Kickboxing, Heavy bag, Athletic performance)
       - Old Money (Classic architecture, Marble, Chess, Vintage luxury)
    
    3. ACTION must show movement or premium detail:
       - "interior leather seats night"
       - "skyline night city lights"
       - "training professional discipline"
       - "checking watch luxury close up"
    
    4. CAMERA MOVE (pick one per visual):
       - low angle
       - dolly zoom
       - fast pan
       - tracking shot
       - close up
       - slow zoom in
       - tilt up
    
    5. LUXURY QUALITY must include (pick TWO):
       - "luxury"
       - "expensive"
       - "4k"
       - "cinematic"
       - "premium"
    
    6. MANDATORY keywords in EVERY visual:
       - At least TWO of: "luxury", "expensive", "4k", "cinematic", "premium"
    
    7. FORBIDDEN visuals:
       ❌ "clouds", "rain window", "forest", "shadows", "smoke", "ink water"
       ❌ "guns", "drugs", "dirty rooms", "grunge", "horror", "prison cells"
    
    SEGMENT STRUCTURE RULES:
    - Break the body into 8-12 logical sentences for 45s+ video
    - Each segment text = ONE complete sentence
    - Each visual = FULL CINEMATIC QUERY following the formula above
    
    ✅ CORRECT VISUAL EXAMPLES (3-CATEGORY ULTRA-LUXURY AESTHETIC):
    - "Bugatti interior leather seats night luxury expensive 4k cinematic"
    - "Kickboxing training professional gym discipline luxury 4k expensive"
    - "Greek statue marble close up museum luxury expensive 4k cinematic"
    - "Dubai skyline night skyscrapers luxury expensive cinematic 4k"
    - "Heavy bag workout shirtless muscles luxury gym 4k expensive"
    - "Monaco yacht harbor luxury boats sunset cinematic 4k expensive"
    
    ❌ WRONG VISUAL EXAMPLES (DO NOT USE):
    - "money" (too short, missing luxury keywords)
    - "car driving" (no brand, no luxury/expensive)
    - "gym workout" (too vague, missing luxury/expensive)
    - "rain on window" (FORBIDDEN)
    - "guns" (FORBIDDEN)
    - "prison" (FORBIDDEN)
    
    CRITICAL RULES:
    - NEVER use generic phrases like "Get uncomfortable" or "Hustle hard"
    - ALWAYS name the specific theory/law
    - The Hook MUST be MAXIMUM 7 words with ending punctuation
    - EVERY visual must be a COMPLETE query with Subject + Action + Camera + Luxury Keywords (TWO of: luxury/expensive/4k/cinematic/premium)
    - Rotate through the 3 categories: ULTRA-LUXURY & STATUS → COMBAT & DISCIPLINE → STOIC & OLD MONEY
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
