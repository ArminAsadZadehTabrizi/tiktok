"""MoviePy-based video editor with Hybrid Timing Engine - FIXED"""
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, 
    CompositeAudioClip, TextClip, concatenate_videoclips
)
from moviepy.audio.AudioClip import AudioArrayClip
# We remove the problematic import and do it manually with numpy
import numpy as np
import json
import config

def apply_darken_filter(clip, factor=0.7):
    """
    Darkens the clip manually using numpy to avoid import errors.
    Factor: 1.0 = Original, 0.0 = Black. 
    0.7 is a good 'Sunglasses' effect for readability.
    """
    def darken(image):
        # Convert to float to avoid overflow, multiply, convert back to uint8
        return (image.astype(float) * factor).astype('uint8')
    return clip.fl_image(darken)

def apply_ken_burns_zoom(clip, zoom_factor=1.05):
    """
    🎬 CINEMATIC POLISH: Safe Ken Burns Effect (Crop-Based Zoom)
    Creates a slow "creep forward" zoom by cropping progressively into an enlarged image.
    This creates a clear, visible zoom that starts wide and zooms in over time.
    """
    # Get original dimensions
    w, h = clip.w, clip.h
    
    # Calculate the maximum enlarged size (zoom_factor = final zoom, e.g., 1.2 = 20% zoom)
    max_w = int(w * zoom_factor)
    max_h = int(h * zoom_factor)
    
    # First, resize the clip to the MAXIMUM size (this is what we'll crop from)
    enlarged_clip = clip.resize((max_w, max_h))
    
    def crop_for_zoom(get_frame, t):
        """At each frame, crop from the enlarged clip to simulate zoom"""
        # Progress from 0 (start) to 1 (end) over the clip duration
        progress = t / clip.duration if clip.duration > 0 else 0
        
        # Reverse the logic: Start with MORE crop (zoomed out), end with LESS crop (zoomed in)
        # At t=0, crop_scale = zoom_factor (show full original size from enlarged)
        # At t=end, crop_scale = 1.0 (show zoomed portion)
        crop_scale = zoom_factor - (zoom_factor - 1.0) * progress
        
        # Calculate current crop dimensions
        current_w = int(w * crop_scale)
        current_h = int(h * crop_scale)
        
        # Calculate crop coordinates (centered)
        x1 = (max_w - current_w) // 2
        y1 = (max_h - current_h) // 2
        x2 = x1 + current_w
        y2 = y1 + current_h
        
        # Get the frame from the enlarged clip
        frame = get_frame(t)
        
        # Crop to the current window
        cropped = frame[y1:y2, x1:x2]
        
        # Resize back to target dimensions to maintain consistent output size
        from moviepy.video.fx.resize import resize
        # Use PIL/numpy resize to scale back to original dimensions
        import cv2
        resized = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
        
        return resized
    
    return enlarged_clip.fl(crop_for_zoom)

def apply_vignette(clip, intensity=0.4):
    """
    🎬 VIRAL POLISH #2: Vignette Overlay (Dark Corners)
    Creates a tunnel vision effect by darkening the edges/corners.
    Perfect for horror atmosphere and focusing attention on center content.
    """
    def create_vignette_mask(w, h):
        # Create coordinate grids
        y = np.linspace(-1, 1, h)
        x = np.linspace(-1, 1, w)
        X, Y = np.meshgrid(x, y)
        
        # Calculate distance from center (0 at center, ~1.4 at corners)
        radius = np.sqrt(X**2 + Y**2)
        
        # Create smooth vignette: 1 at center, fades to (1-intensity) at edges
        vignette = 1 - (np.clip(radius, 0, 1) ** 1.5) * intensity
        
        # Expand to 3 channels (RGB)
        return np.stack([vignette, vignette, vignette], axis=2)
    
    # Create the mask once for this clip size
    mask = create_vignette_mask(clip.w, clip.h)
    
    def apply_mask(image):
        # Multiply image by vignette mask
        return (image.astype(float) * mask).astype('uint8')
    
    return clip.fl_image(apply_mask)

def apply_film_grain(clip, intensity=0.08):
    """
    🎬 VIRAL RETENTION #1: Film Grain (Visual Noise)
    Adds dynamic per-frame noise to create a raw, cursed, "found footage" texture.
    Clean HD is boring for psychological horror - grain keeps it gritty.
    """
    def add_grain(image):
        # Generate random noise for this frame
        noise = np.random.randint(0, int(40 * intensity), image.shape, dtype='uint8')
        # Blend noise with original image (capped at 255)
        return np.clip(image.astype(int) + noise, 0, 255).astype('uint8')
    
    return clip.fl_image(add_grain)

def apply_random_glitches(clip, glitch_interval=(4, 8)):
    """
    🎬 VIRAL RETENTION #2: Subliminal Glitch Frames (Pattern Interrupt)
    Randomly inserts brief visual glitches every 4-8 seconds to keep viewers alert.
    Prevents the brain from getting bored with predictable visuals.
    """
    import random
    
    # Generate random glitch timestamps throughout the video
    glitch_times = []
    current_time = random.uniform(*glitch_interval)
    while current_time < clip.duration:
        glitch_duration = random.choice([0.1, 0.15, 0.2])  # Brief flash
        glitch_type = random.choice(['invert', 'red_tint', 'shake'])
        glitch_times.append({
            'start': current_time,
            'end': current_time + glitch_duration,
            'type': glitch_type
        })
        current_time += random.uniform(*glitch_interval)
    
    def apply_glitch_at_time(get_frame, t):
        frame = get_frame(t)
        
        # Check if we're in a glitch window
        for glitch in glitch_times:
            if glitch['start'] <= t < glitch['end']:
                if glitch['type'] == 'invert':
                    # Negative/inverted colors
                    return 255 - frame
                elif glitch['type'] == 'red_tint':
                    # Boost red channel for creepy effect
                    red_frame = frame.copy()
                    red_frame[:, :, 0] = np.clip(red_frame[:, :, 0].astype(int) + 100, 0, 255).astype('uint8')
                    return red_frame
                elif glitch['type'] == 'shake':
                    # Horizontal shake - shift frame left or right
                    shift = random.randint(30, 60) * random.choice([-1, 1])
                    return np.roll(frame, shift, axis=1)
        
        return frame
    
    return clip.fl(apply_glitch_at_time)

def resize_to_vertical(clip):
    target_ratio = config.VIDEO_HEIGHT / config.VIDEO_WIDTH
    if clip.h / clip.w > target_ratio:
        new_width = config.VIDEO_WIDTH
        new_height = int(clip.h * (config.VIDEO_WIDTH / clip.w))
    else:
        new_height = config.VIDEO_HEIGHT
        new_width = int(clip.w * (config.VIDEO_HEIGHT / clip.h))
    clip = clip.resize((new_width, new_height))
    return clip.crop(x_center=new_width/2, y_center=new_height/2, width=config.VIDEO_WIDTH, height=config.VIDEO_HEIGHT)

def create_word_clip(text, start, duration, is_exact=False):
    if duration < 0.2: duration = 0.2
    
    # 🎬 PATTERN INTERRUPT #3: "MONSTER" TYPOGRAPHY HOOK (First 2 seconds)
    # The first sentence MUST be readable from 2 meters away WITHOUT GLASSES!
    # This is the HARD HOOK that stops scrolling dead in its tracks.
    is_monster_hook = start < 2.0
    
    if is_monster_hook:
        # MONSTER HOOK: MASSIVE, BRIGHT NEON RED, DROP SHADOW
        # Font Size: 130 (readable from across the room)
        # Color: Bright Neon Red (triggers urgency and danger)
        foreground_color = "#FF0044"  # Bright Neon Red
        font_size = 130
        stroke_width = 8
    elif start < 5.0:
        # NORMAL HOOK PHASE: Use BRIGHT RED or BRIGHT YELLOW with 20% larger font
        # Alternate between red and yellow for visual variety
        foreground_color = "#FF0044" if int(start * 2) % 2 == 0 else "#FFFF00"
        font_size = int(config.CAPTION_FONTSIZE * 1.2)
        stroke_width = 6
    else:
        # NORMAL PHASE: VIRAL HIGHLIGHT LOGIC
        # Significant = longer than 5 letters OR capitalized
        clean_word = text.strip('.,!?;:')
        is_significant = len(clean_word) > 5 or (len(clean_word) > 0 and clean_word[0].isupper())
        
        # Highlight significant words in BRIGHT YELLOW with larger font
        foreground_color = "#FFFF00" if is_significant else "white"
        font_size = (config.CAPTION_FONTSIZE + 15) if is_significant else config.CAPTION_FONTSIZE
        stroke_width = 6
    
    try:
        # 🎬 CINEMATIC POLISH: DROP SHADOW / GLOW for Readability
        # Create TWO layers: Black background shadow + Bright foreground text
        
        # LAYER 1 (Background Shadow): Slightly larger, black, offset for depth
        shadow = TextClip(
            text, fontsize=font_size + 4, color="black", font="Impact",
            stroke_color="black", stroke_width=stroke_width + 2, method='caption',
            size=(config.VIDEO_WIDTH-100, None), align='center'
        )
        
        # LAYER 2 (Foreground): Bright colored text
        txt = TextClip(
            text, fontsize=font_size, color=foreground_color, font="Impact",
            stroke_color="black", stroke_width=stroke_width, method='caption', 
            size=(config.VIDEO_WIDTH-100, None), align='center'
        )
        
        # Composite: Stack shadow beneath text for "glow" effect
        composite = CompositeVideoClip([shadow, txt], size=txt.size)
        
    except Exception:
        # Fallback: Single layer with enhanced stroke if composite fails
        composite = TextClip(
            text, fontsize=font_size, color=foreground_color, font="Impact",
            stroke_color="black", stroke_width=stroke_width + 2, align='center'
        )
        
    return composite.set_position(('center', 'center')).set_start(start).set_duration(duration)

def get_smart_timings(script_data, audio_duration):
    """Calculates timing based on character count with punctuation-aware pauses for natural flow."""
    full_text = f"{script_data['hook']} {script_data['body']}"
    words = full_text.split()
    
    # Calculate total characters to distribute time weighted by length
    total_chars = sum(len(w) for w in words)
    if total_chars == 0: total_chars = 1
    
    # Time per character (subtracting 0.5s buffer for silence)
    time_per_char = (audio_duration - 0.5) / total_chars
    
    segments = []
    current_time = 0.1
    
    # Chunk by 2 words for readability
    chunk_size = 2
    
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i+chunk_size]
        chunk_text = " ".join(chunk_words)
        
        # Duration depends on how many letters are in this chunk
        chunk_len = sum(len(w) for w in chunk_words)
        duration = chunk_len * time_per_char
        
        # Minimum duration to be readable
        if duration < 0.5: duration = 0.5
        
        # PUNCTUATION-AWARE TIMING: Add natural pauses
        last_word = chunk_words[-1]
        if last_word.endswith(','):
            duration += 0.15  # Small pause for comma
        elif last_word.endswith(('.', '?', '!')):
            duration += 0.3  # Longer pause for sentence end
        
        segments.append({
            "word": chunk_text,
            "start": current_time,
            "end": current_time + duration
        })
        current_time += duration
        
    return segments

def stitch_and_edit_video(video_paths, audio_path, script_data, output_path):
    print(f"🎬 Editing video (Hybrid Mode - Fixed)...")
    
    audio = AudioFileClip(str(audio_path))
    main_duration = audio.duration  # Store main duration for reference
    
    # 1. JUMPSCARE AUDIO (Robust Stereo Fix)
    print("  🔊 Generating white noise jumpscare...")
    try:
        duration = 0.3  # seconds - Shorter, punchier to match red strobe
        rate = 44100    # Hz
        # Generate stereo noise: Shape must be (N, 2)
        noise_data = np.random.uniform(-0.5, 0.5, (int(duration * rate), 2))
        
        # Create AudioArrayClip (Safe method)
        jumpscare_audio = AudioArrayClip(noise_data, fps=rate)
        jumpscare_audio = jumpscare_audio.set_duration(duration).volumex(0.4)  # Explicit duration
        
        # Overlay jumpscare at t=0
        final_audio = CompositeAudioClip([audio, jumpscare_audio])
        final_audio = final_audio.set_duration(main_duration)  # Enforce duration
    except Exception as e:
        print(f"  ⚠️ Could not generate jumpscare audio: {e}")
        final_audio = audio  # Fallback if numpy fails

    # 2. BACKGROUND MUSIC MIX
    if config.BACKGROUND_MUSIC_PATH.exists():
        try:
            print("  🎵 Adding background music...")
            bg = AudioFileClip(str(config.BACKGROUND_MUSIC_PATH))
            # Loop background music if shorter than voiceover
            if bg.duration < main_duration:
                num_loops = int(np.ceil(main_duration / bg.duration))
                bg_clips = [bg] * num_loops
                # Concatenate audio clips, not video clips
                from moviepy.editor import concatenate_audioclips
                bg = concatenate_audioclips(bg_clips)
            bg = bg.subclip(0, main_duration).volumex(config.BG_MUSIC_VOLUME)
            bg = bg.set_duration(main_duration)  # Explicit duration
            final_audio = CompositeAudioClip([final_audio, bg])
            final_audio = final_audio.set_duration(main_duration)  # Re-enforce duration
        except Exception as e:
            print(f"  ⚠️ Could not add background music: {e}")
    
    # 1. TIMING LOGIC
    word_timings = []
    timing_file = config.ASSETS_DIR / "temp_timing.json"
    
    # Try to load timings, but be safe
    if timing_file.exists():
        try:
            with open(timing_file, "r") as f:
                content = f.read()
                if content:
                    word_timings = json.loads(content)
        except Exception as e:
            print(f"  ⚠️ Warning: Could not read timing file: {e}")
            
    if len(word_timings) > 0:
        print(f"  ✅ EXACT TIMING found ({len(word_timings)} words)")
        use_exact = True
    else:
        print(f"  ⚠️ NO TIMING found - Switching to MATHEMATICAL BACKUP")
        word_timings = get_smart_timings(script_data, audio.duration)
        use_exact = False
        
    # 2. VISUALS
    clips = []
    scene_duration = 2.5 
    
    for video_path in video_paths:
        try:
            clip = VideoFileClip(str(video_path))
            clip = resize_to_vertical(clip)
            # 🎬 VIRAL POLISH PIPELINE (Enhanced for Psychological Horror)
            clip = apply_darken_filter(clip, factor=0.7)  # Sunglasses filter
            clip = apply_ken_burns_zoom(clip, zoom_factor=1.20)  # Boosted 20% zoom for visible movement
            # SAFETY: Force exact resolution to prevent 1-pixel rounding errors from zoom
            clip = clip.resize(newsize=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT))
            clip = apply_film_grain(clip, intensity=0.08)  # Add gritty texture
            clip = apply_random_glitches(clip, glitch_interval=(4, 8))  # Subliminal interrupts
            clip = apply_vignette(clip, intensity=0.4)  # Dark corners for atmosphere
            clip = clip.without_audio()
            
            if clip.duration > scene_duration:
                start_t = 0
                clip = clip.subclip(start_t, start_t + scene_duration)
            clips.append(clip)
        except Exception as e:
            print(f"  Skipping bad video file: {e}")

    if not clips:
        raise Exception("No valid video clips could be loaded.")

    final_visuals = []
    curr_t = 0
    idx = 0
    while curr_t < main_duration:
        clip = clips[idx % len(clips)]
        final_visuals.append(clip)
        curr_t += clip.duration
        idx += 1
        
    video = concatenate_videoclips(final_visuals, method="compose")
    video = video.subclip(0, main_duration)
    video = video.set_duration(main_duration)  # Explicit duration enforcement
    
    # 🎬 PATTERN INTERRUPT #2: "RED STROBE & SHAKE" (1.0 seconds)
    # Creates a "Red Alert" warning pulse with camera shake for maximum impact.
    print("  ⚡ Applying red strobe with camera shake...")
    import random
    def apply_red_strobe_and_shake(get_frame, t):
        frame = get_frame(t)
        if t < 1.0:
            # RED STROBE: Alternate every 0.1s between normal and red-tinted
            cycle_time = t % 0.2  # 0.2s cycle = 0.1s normal + 0.1s red
            if cycle_time < 0.1:
                # Red tint phase: boost red channel dramatically
                red_frame = frame.copy()
                red_frame[:, :, 0] = np.clip(red_frame[:, :, 0].astype(int) + 120, 0, 255).astype('uint8')
                frame = red_frame
            
            # CAMERA SHAKE: Random +/- 5 pixel shift (horizontal and vertical)
            h_shift = random.randint(-5, 5)
            v_shift = random.randint(-5, 5)
            frame = np.roll(frame, h_shift, axis=1)  # Horizontal shake
            frame = np.roll(frame, v_shift, axis=0)  # Vertical shake
        
        return frame
    
    video = video.fl(apply_red_strobe_and_shake)
    video = video.set_duration(main_duration)  # Re-enforce duration after transformation
    
    # 3. SET AUDIO TO VIDEO
    video = video.set_audio(final_audio)
    
    # 4. CAPTIONS
    text_clips = []
    for w in word_timings:
        text_clips.append(create_word_clip(w['word'], w['start'], w['end']-w['start'], is_exact=use_exact))
        
    final_video = CompositeVideoClip([video] + text_clips)
    final_video = final_video.set_duration(main_duration)  # Final duration enforcement
    
    final_video.write_videofile(
        str(output_path), fps=30, codec='libx264', audio_codec='aac', 
        threads=4, preset='ultrafast'
    )
    
    # Cleanup
    video.close(); audio.close(); final_video.close()
    if 'bg' in locals(): bg.close()
    return output_path
