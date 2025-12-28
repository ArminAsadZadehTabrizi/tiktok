"""MoviePy-based video editor for High-Value Motivational Content"""
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, 
    CompositeAudioClip, TextClip, concatenate_videoclips
)
from moviepy.audio.AudioClip import AudioArrayClip
# We remove the problematic import and do it manually with numpy
import numpy as np
import json
import random
import config

def apply_high_contrast_filter(clip, contrast=1.2, saturation=1.3):
    """
    🎬 SUCCESS AESTHETIC: High Contrast Filter (MOBILE OPTIMIZED)
    Increases contrast (1.2x) and saturation (1.3x) to make colors POP on small screens.
    Creates eye-catching visuals for YouTube Shorts and TikTok.
    """
    def enhance(image):
        # Convert to float for processing
        img = image.astype(float)
        
        # Apply contrast: scale pixel values around middle gray (128)
        img = ((img - 128) * contrast) + 128
        
        # Apply saturation boost (convert to HSV-like processing)
        # Simple saturation: boost the distance from gray
        gray = np.mean(img, axis=2, keepdims=True)
        img = gray + (img - gray) * saturation
        
        # Clip to valid range and convert back
        return np.clip(img, 0, 255).astype('uint8')
    
    return clip.fl_image(enhance)

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
    
    # 🎬 SUCCESS AESTHETIC: Clean, Professional Typography
    # White text with black outline for maximum readability
    # Highlight important words in Gold or Emerald Green
    
    # Determine if word is significant (longer than 5 letters OR capitalized)
    clean_word = text.strip('.,!?;:')
    is_significant = len(clean_word) > 5 or (len(clean_word) > 0 and clean_word[0].isupper())
    
    # Color rotation for significant words: Gold and Emerald Green
    # Use time-based alternation for visual variety
    if is_significant:
        # Alternate between Gold and Emerald based on start time
        if int(start * 2) % 2 == 0:
            foreground_color = "#FFD700"  # Bright Yellow/Gold
        else:
            foreground_color = "#50C878"  # Emerald Green
        font_size = config.CAPTION_FONTSIZE + 15  # Larger for emphasis
    else:
        foreground_color = "white"  # Pure white for normal words
        font_size = config.CAPTION_FONTSIZE
    
    stroke_width = 6  # Consistent stroke for readability
    
    try:
        # 🎬 PREMIUM READABILITY: Drop Shadow / Glow
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

def create_headline_hook(text, start, duration):
    """
    🎬 HIGH-RETENTION HOOK: Massive Headline Style
    Renders the hook as a GIANT centered headline with attention-grabbing styling.
    - Bright Warning Colors (Red/Yellow) to stop the scroll
    - Heavy black background box for contrast
    - Pulse animation for dynamic effect
    - Much larger than normal text to dominate the screen
    """
    if duration < 0.3: duration = 0.3
    
    # 🚨 WARNING SIGN AESTHETIC: Bright Red for maximum attention
    foreground_color = "#FF0000"  # Bright Red
    font_size = config.CAPTION_FONTSIZE + 60  # MASSIVE size (140px typically)
    stroke_width = 12  # Extra thick stroke for "warning sign" effect
    
    try:
        # LAYER 1 (Heavy Background Box): Semi-transparent black rectangle
        # This creates the dark box behind the text for maximum contrast
        background_shadow = TextClip(
            text, fontsize=font_size + 6, color="black", font="Impact",
            stroke_color="black", stroke_width=stroke_width + 4, method='caption',
            size=(config.VIDEO_WIDTH-100, None), align='center'
        )
        
        # LAYER 2 (Bright Text): Red text with heavy black outline
        txt = TextClip(
            text, fontsize=font_size, color=foreground_color, font="Impact",
            stroke_color="black", stroke_width=stroke_width, method='caption',
            size=(config.VIDEO_WIDTH-100, None), align='center'
        )
        
        # Composite the layers
        composite = CompositeVideoClip([background_shadow, txt], size=txt.size)
        
        # 🎬 PULSE ANIMATION: Scale from 1.0 to 1.1 and back
        # Creates a "breathing" effect that grabs attention
        def pulse_effect(t):
            # Create a sine wave pulse effect over the duration
            progress = t / max(duration, 0.01)
            scale = 1.0 + 0.1 * np.sin(progress * np.pi * 2)  # Oscillate between 1.0 and 1.1
            return scale
        
        composite = composite.resize(lambda t: pulse_effect(t))
        
    except Exception as e:
        print(f"  ⚠️ Pulse effect failed: {e}. Using static headline.")
        # Fallback: Single layer without animation
        composite = TextClip(
            text, fontsize=font_size, color=foreground_color, font="Impact",
            stroke_color="black", stroke_width=stroke_width, method='caption',
            size=(config.VIDEO_WIDTH-100, None), align='center'
        )
    
    return composite.set_position(('center', 'center')).set_start(start).set_duration(duration)


def apply_start_glitch(clip, glitch_duration=0.5):
    """
    🚨 VISUAL PATTERN INTERRUPT: Start Glitch Effect
    Applies a strong visual disruption to the first 0.5 seconds to "wake up" the viewer.
    - Color inversion flash for 0.1s
    - Acts as a subliminal attention grabber
    - Prevents immediate scroll-away
    """
    def glitch_effect(get_frame, t):
        """Apply color inversion during the first 0.1 seconds"""
        frame = get_frame(t)
        
        # Apply color inversion for first 0.1 seconds only
        if t < 0.1:
            # Invert RGB values: 255 - original value
            inverted = 255 - frame.astype('uint8')
            return inverted
        else:
            # Normal video after glitch
            return frame
    
    return clip.fl(glitch_effect)


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
    print(f"🎬 Editing video (Success Aesthetic)...")
    
    audio = AudioFileClip(str(audio_path))
    main_duration = audio.duration  # Store main duration for reference
    
    # 1. CLEAN AUDIO (No jumpscares)
    final_audio = audio

    # 2. BACKGROUND MUSIC MIX (Random Track Selection)
    music_dir = config.ASSETS_DIR / "music"
    music_files = list(music_dir.glob("*.mp3")) if music_dir.exists() else []
    
    if music_files:
        try:
            # Pick a random track from available music files
            selected_music = random.choice(music_files)
            print(f"  🎵 Selected background track: {selected_music.name}")
            
            bg = AudioFileClip(str(selected_music))
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
    else:
        print(f"  ⚠️ No music files found in {music_dir} - proceeding without background music")
    
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
            # 🎬 SUCCESS AESTHETIC PIPELINE (Premium Instagram Look)
            clip = apply_ken_burns_zoom(clip, zoom_factor=1.25)  # FASTER ZOOM for mobile screens (25% zoom)
            # SAFETY: Force exact resolution to prevent 1-pixel rounding errors from zoom
            clip = clip.resize(newsize=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT))
            clip = apply_high_contrast_filter(clip, contrast=1.2, saturation=1.3)  # BOOSTED for mobile screens (eye-catching)
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
    
    # 3. SET AUDIO TO VIDEO
    video = video.set_audio(final_audio)
    
    # 4. CAPTIONS (HOOK vs BODY SPLIT)
    text_clips = []
    
    # 🎬 HOOK DETECTION: Find first sentence ending to separate hook from body
    hook_timings = []
    body_timings = []
    
    # Find index of first word ending with sentence punctuation
    hook_end_idx = -1
    for i, w in enumerate(word_timings):
        word_text = w['word'].rstrip()
        if any(word_text.endswith(p) for p in ['.', '?', '!']):
            hook_end_idx = i
            break
    
    # Split timings into hook and body
    if hook_end_idx >= 0:
        hook_timings = word_timings[:hook_end_idx + 1]
        body_timings = word_timings[hook_end_idx + 1:]
        print(f"  🎯 HOOK detected: {len(hook_timings)} words | BODY: {len(body_timings)} words")
    else:
        # Fallback: If no sentence ending found, treat all as body
        body_timings = word_timings
        print(f"  ⚠️ No hook punctuation found - using standard rendering")
    
    # HOOK: Render as single massive headline (if detected)
    if hook_timings:
        hook_text = ' '.join([w['word'] for w in hook_timings])
        hook_start = hook_timings[0]['start']
        hook_duration = hook_timings[-1]['end'] - hook_start
        print(f"  🚨 Rendering HOOK as headline: \"{hook_text}\" ({hook_duration:.2f}s)")
        text_clips.append(create_headline_hook(hook_text, hook_start, hook_duration))
    
    # BODY: Standard word-by-word karaoke
    for w in body_timings:
        text_clips.append(create_word_clip(w['word'], w['start'], w['end']-w['start'], is_exact=use_exact))
    
    # 5. COMPOSE FINAL VIDEO
    final_video = CompositeVideoClip([video] + text_clips)
    final_video = final_video.set_duration(main_duration)
    
    # 🚨 APPLY GLITCH EFFECT to opening frames
    print(f"  ⚡ Applying glitch effect to first 0.5s...")
    final_video = apply_start_glitch(final_video, glitch_duration=0.5)
    
    # 6. RENDER
    final_video.write_videofile(
        str(output_path), fps=30, codec='libx264', audio_codec='aac', 
        threads=4, preset='ultrafast'
    )
    
    # Cleanup
    video.close(); audio.close(); final_video.close()
    if 'bg' in locals(): bg.close()
    return output_path
