import asyncio
import edge_tts
import json
from pathlib import Path
import config

async def generate_audio_with_timing(text, output_file):
    print(f"  ⚡️ Stream starting for voice: {config.TTS_VOICE}")
    print(f"  🔍 Attempting to capture word-level timing...")
    
    # 🎬 VIRAL RETENTION #3: Faster Speech Rate (+30% for Urgency)
    # AGGRESSIVE SPEED for YouTube Shorts and TikTok Growth - creates dominance and urgency
    communicate = edge_tts.Communicate(text, config.TTS_VOICE, rate="+30%")
    word_timings = []
    sentence_timings = []
    
    with open(output_file, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # Capture word-level timing (best case)
                start_time = chunk["offset"] / 10_000_000
                duration = chunk["duration"] / 10_000_000
                word_timings.append({
                    "word": chunk["text"],
                    "start": start_time,
                    "end": start_time + duration
                })
            elif chunk["type"] == "SentenceBoundary":
                # Capture sentence-level timing (fallback)
                start_time = chunk["offset"] / 10_000_000
                duration = chunk["duration"] / 10_000_000
                sentence_timings.append({
                    "text": chunk["text"],
                    "start": start_time,
                    "end": start_time + duration
                })
    
    # If we got word timings, use them directly
    if len(word_timings) > 0:
        print(f"  ✅ SUCCESS: Captured {len(word_timings)} word-level timestamps!")
        return word_timings
    
    # If we only got sentence timings, distribute words within sentences
    if len(sentence_timings) > 0:
        print(f"  ⚙️  Using {len(sentence_timings)} sentence timings to distribute words...")
        final_timings = []
        
        for sent in sentence_timings:
            words = sent["text"].split()
            if not words:
                continue
                
            # Calculate time per character for this sentence
            total_chars = sum(len(w) for w in words)
            if total_chars == 0:
                continue
                
            sent_duration = sent["end"] - sent["start"]
            time_per_char = sent_duration / total_chars
            
            current_time = sent["start"]
            for word in words:
                word_duration = len(word) * time_per_char
                if word_duration < 0.15:  # Minimum readable duration
                    word_duration = 0.15
                    
                final_timings.append({
                    "word": word,
                    "start": current_time,
                    "end": current_time + word_duration
                })
                current_time += word_duration
        
        print(f"  ✅ Generated {len(final_timings)} word timings from sentences!")
        return final_timings
    
    # No timings at all
    print("  ⚠️ CRITICAL WARNING: No timing data received from Edge TTS!")
    return []

def generate_audio(script_data):
    print(f"\n🎤 Generating voiceover...")
    
    # Reconstruct full text from new segment-based structure
    full_text = script_data['hook']
    if 'segments' in script_data:
        # Concatenate all segment texts
        body_text = ' '.join([seg['text'] for seg in script_data['segments']])
        full_text = f"{full_text} {body_text}"
    elif 'body' in script_data:
        # Fallback for old structure
        full_text = f"{full_text} {script_data['body']}"
    
    output_path = config.ASSETS_DIR / "temp_voiceover.mp3"
    
    try:
        timings = asyncio.run(generate_audio_with_timing(full_text, output_path))
        
        # Save timings
        timing_path = config.ASSETS_DIR / "temp_timing.json"
        with open(timing_path, "w") as f:
            json.dump(timings, f, indent=2)
            
        return output_path
    except Exception as e:
        print(f"✗ Error: {e}")
        raise
