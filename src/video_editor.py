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

def apply_darken_filter(clip, factor=0.6):
    """
    Darkens the clip manually using numpy to avoid import errors.
    Factor: 1.0 = Original, 0.0 = Black. 
    0.6 creates a strong 'Dark Aesthetic' for white text to pop aggressively.
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


def apply_flash_zoom(clip, flash_duration=0.3, zoom_factor=1.08):
    """
    🎬 CINEMATIC VISUAL HOOK: Flash + Zoom Effect
    Creates a revelatory "white flash" exposure effect combined with a slow zoom-in.
    - Brightness starts high and fades to normal over 0.3s (cinematic reveal)
    - Slow zoom-in for "creeping realization" effect
    - Feels more philosophical/revelatory rather than broken/horror
    """
    def flash_effect(get_frame, t):
        """Apply white flash fade during the first 0.3 seconds"""
        frame = get_frame(t)
        
        if t < flash_duration:
            # Calculate flash intensity (starts at 1.5, fades to 1.0)
            progress = t / flash_duration  # 0 to 1
            flash_intensity = 1.5 - (0.5 * progress)  # 1.5 to 1.0
            
            # Apply brightness boost (overexposure effect)
            flashed = np.clip(frame * flash_intensity, 0, 255).astype('uint8')
            return flashed
        else:
            return frame
    
    # Apply flash effect
    flashed_clip = clip.fl(flash_effect)
    
    # Apply slow zoom-in effect (reuse Ken Burns logic)
    # Zoom progresses over the entire clip duration
    def zoom_effect(get_frame, t):
        """Progressive zoom-in effect"""
        frame = get_frame(t)
        h, w = frame.shape[:2]
        
        # Calculate zoom progress (slow and subtle)
        duration = clip.duration
        progress = min(t / duration, 1.0)  # 0 to 1
        current_zoom = 1 + (zoom_factor - 1) * progress  # 1.0 to zoom_factor
        
        # Calculate crop dimensions
        new_h = int(h / current_zoom)
        new_w = int(w / current_zoom)
        
        # Center crop
        y_offset = (h - new_h) // 2
        x_offset = (w - new_w) // 2
        
        # Crop and resize back to original dimensions
        cropped = frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w]
        from PIL import Image
        img = Image.fromarray(cropped)
        resized = img.resize((w, h), Image.LANCZOS)
        
        return np.array(resized)
    
    return flashed_clip.fl(zoom_effect)


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

def add_hook_sfx(audio_clip):
    """
    🎬 AUDITORY HOOK: Add a sound effect at the very start (0.0s) of the video.
    Overlays hook_sfx.mp3 on top of the voiceover for a startle trigger.
    
    Args:
        audio_clip: The base audio clip (voiceover)
    
    Returns:
        CompositeAudioClip with SFX overlaid, or original audio if SFX file not found
    """
    sfx_path = config.ASSETS_DIR / "hook_sfx.mp3"
    
    if not sfx_path.exists():
        print(f"  ⚠️ Hook SFX not found at {sfx_path} - proceeding without auditory hook")
        return audio_clip
    
    try:
        print(f"  🔊 Loading hook SFX: {sfx_path.name}")
        sfx = AudioFileClip(str(sfx_path))
        
        # Position SFX at the very start (0.0s)
        sfx = sfx.set_start(0.0)
        
        # Trim SFX if it's longer than the audio clip
        if sfx.duration > audio_clip.duration:
            sfx = sfx.subclip(0, audio_clip.duration)
        
        # Composite: Mix SFX on top of voiceover
        composite_audio = CompositeAudioClip([audio_clip, sfx])
        composite_audio = composite_audio.set_duration(audio_clip.duration)
        
        print(f"  ✓ Hook SFX added successfully at 0.0s (duration: {sfx.duration:.2f}s)")
        return composite_audio
        
    except Exception as e:
        print(f"  ⚠️ Failed to add hook SFX: {e} - proceeding without auditory hook")
        return audio_clip


def analyze_sentences_from_timings(word_timings, total_duration):
    """
    🎬 DYNAMIC CUTTING: Analyze word timings to identify sentence boundaries.
    Creates "scenes" based on natural sentence endings for better video flow.
    
    Args:
        word_timings: List of {'word': str, 'start': float, 'end': float}
        total_duration: Total audio duration for validation
    
    Returns:
        List of scenes: [{'start_time': float, 'end_time': float, 'duration': float, 'text': str}]
        or None if word_timings is invalid
    """
    if not word_timings or len(word_timings) == 0:
        return None
    
    # Sentence-ending punctuation
    sentence_endings = ('.', '?', '!')
    
    scenes = []
    current_scene_words = []
    scene_start_time = word_timings[0]['start']
    
    for i, word_data in enumerate(word_timings):
        word = word_data['word']
        current_scene_words.append(word)
        
        # Check if this word ends a sentence
        is_sentence_end = any(word.rstrip().endswith(punct) for punct in sentence_endings)
        is_last_word = (i == len(word_timings) - 1)
        
        if is_sentence_end or is_last_word:
            # Complete this scene
            scene_end_time = word_data['end']
            scene_duration = scene_end_time - scene_start_time
            scene_text = ' '.join(current_scene_words)
            
            # 🎬 LONG SENTENCE HANDLING: Split if >5 seconds
            if scene_duration > 5.0 and len(current_scene_words) > 2:
                # Split at the middle word boundary
                mid_point = len(current_scene_words) // 2
                
                # First half
                first_half_words = current_scene_words[:mid_point]
                first_half_end_idx = i - (len(current_scene_words) - mid_point)
                first_half_end_time = word_timings[first_half_end_idx]['end']
                first_duration = first_half_end_time - scene_start_time
                
                scenes.append({
                    'start_time': scene_start_time,
                    'end_time': first_half_end_time,
                    'duration': first_duration,
                    'text': ' '.join(first_half_words)
                })
                
                # Second half
                second_half_words = current_scene_words[mid_point:]
                second_half_start_time = word_timings[first_half_end_idx + 1]['start']
                
                scenes.append({
                    'start_time': second_half_start_time,
                    'end_time': scene_end_time,
                    'duration': scene_end_time - second_half_start_time,
                    'text': ' '.join(second_half_words)
                })
                
                print(f"  ✂️ Split long sentence ({scene_duration:.2f}s) into 2 clips: {first_duration:.2f}s + {scene_end_time - second_half_start_time:.2f}s")
            else:
                # Normal scene (including short sentences <1.5s)
                scenes.append({
                    'start_time': scene_start_time,
                    'end_time': scene_end_time,
                    'duration': scene_duration,
                    'text': scene_text
                })
                
                if scene_duration < 1.5:
                    print(f"  ⚡ Fast cut: \"{scene_text[:30]}...\" ({scene_duration:.2f}s)")
            
            # Reset for next sentence
            current_scene_words = []
            if i < len(word_timings) - 1:
                scene_start_time = word_timings[i + 1]['start']
    
    print(f"  📊 Analyzed {len(scenes)} scenes from {len(word_timings)} words")
    return scenes


def create_fixed_duration_scenes(total_duration, fixed_duration=2.5):
    """
    🎬 FALLBACK: Create scenes with fixed duration when word_timings is unavailable.
    
    Args:
        total_duration: Total video duration
        fixed_duration: Duration for each scene (default 2.5s)
    
    Returns:
        List of scenes with fixed intervals
    """
    scenes = []
    current_time = 0.0
    scene_index = 1
    
    while current_time < total_duration:
        end_time = min(current_time + fixed_duration, total_duration)
        scenes.append({
            'start_time': current_time,
            'end_time': end_time,
            'duration': end_time - current_time,
            'text': f"Scene {scene_index}"
        })
        current_time = end_time
        scene_index += 1
    
    print(f"  📊 Fallback: Created {len(scenes)} fixed-duration scenes ({fixed_duration}s each)")
    return scenes


def assign_clips_to_scenes(scenes, video_paths):
    """
    🎬 CLIP ASSIGNMENT: Match video clips to sentence scenes dynamically.
    
    Args:
        scenes: List of scene dictionaries from analyze_sentences_from_timings
        video_paths: List of video file paths
    
    Returns:
        List of positioned video clips ready for concatenation
    """
    positioned_clips = []
    
    for i, scene in enumerate(scenes):
        # Circular rotation through available videos
        video_path = video_paths[i % len(video_paths)]
        duration = scene['duration']
        
        try:
            clip = VideoFileClip(str(video_path))
            clip = resize_to_vertical(clip)
            
            # Apply visual effects (Success Aesthetic Pipeline)
            clip = apply_ken_burns_zoom(clip, zoom_factor=1.25)
            clip = clip.resize(newsize=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT))
            clip = apply_high_contrast_filter(clip, contrast=1.2, saturation=1.3)
            clip = clip.without_audio()
            
            # Match clip duration to scene duration
            if clip.duration < duration:
                # Loop clip if too short
                num_loops = int(np.ceil(duration / clip.duration))
                looped_clips = [clip] * num_loops
                clip = concatenate_videoclips(looped_clips, method="compose")
            
            # Trim to exact duration needed
            if clip.duration > duration:
                start_offset = 0
                clip = clip.subclip(start_offset, start_offset + duration)
            
            # Set exact duration
            clip = clip.set_duration(duration)
            positioned_clips.append(clip)
            
            print(f"  🎥 Scene {i+1}: {duration:.2f}s - \"{scene['text'][:40]}...\"")
            
        except Exception as e:
            print(f"  ⚠️ Error loading video {video_path}: {e}")
            # Skip this clip, will reuse previous or next
            continue
    
    return positioned_clips


def stitch_and_edit_video(video_paths, audio_path, script_data, output_path):
    print(f"🎬 Editing video (Success Aesthetic)...")
    
    audio = AudioFileClip(str(audio_path))
    main_duration = audio.duration  # Store main duration for reference
    
    # 1. HOOK SFX OVERLAY (Auditory Hook)
    audio = add_hook_sfx(audio)

    # 2. CLEAN AUDIO (No jumpscares)
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
        
    # 2. VISUALS - DYNAMIC SENTENCE-BASED CUTTING
    print(f"  🎬 Analyzing scenes for dynamic cutting...")
    
    # Analyze sentences from word timings to create dynamic scenes
    scenes = analyze_sentences_from_timings(word_timings, main_duration)
    
    # Fallback to fixed duration if no word_timings available
    if scenes is None:
        print(f"  ⚠️ No word timings available - using fallback fixed duration")
        scenes = create_fixed_duration_scenes(main_duration, fixed_duration=2.5)
    
    # Assign video clips to scenes
    video_clips = assign_clips_to_scenes(scenes, video_paths)
    
    if not video_clips:
        raise Exception("No valid video clips could be loaded.")
    
    # Concatenate all positioned clips
    video = concatenate_videoclips(video_clips, method="compose")
    
    # Ensure exact duration match with audio
    if video.duration != main_duration:
        print(f"  ⚠️ Adjusting video duration from {video.duration:.2f}s to {main_duration:.2f}s")
        video = video.subclip(0, min(video.duration, main_duration))
        video = video.set_duration(main_duration)
    
    # 3. SET AUDIO TO VIDEO
    video = video.set_audio(final_audio)
    
    # 4. CAPTIONS (HOOK vs BODY SPLIT)
    text_clips = []
    
    # 🎬 HOOK DETECTION: Use explicit hook text from script_data instead of guessing
    hook_timings = []
    body_timings = []
    
    # Get the explicit hook text from the LLM
    hook_text = script_data['hook'].strip()
    hook_words = hook_text.split()
    
    # Match words from word_timings to hook_words
    hook_end_idx = -1
    matched_count = 0
    
    for i, w in enumerate(word_timings):
        # Clean word for comparison (remove punctuation)
        clean_word = w['word'].strip().rstrip('.,!?;:').lower()
        
        if matched_count < len(hook_words):
            hook_word = hook_words[matched_count].strip().rstrip('.,!?;:').lower()
            if clean_word == hook_word:
                matched_count += 1
                # If we've matched all hook words, mark this as the end
                if matched_count == len(hook_words):
                    hook_end_idx = i
                    break
    
    # Split timings into hook and body based on matched index
    if hook_end_idx >= 0:
        hook_timings = word_timings[:hook_end_idx + 1]
        body_timings = word_timings[hook_end_idx + 1:]
        print(f"  🎯 HOOK detected (exact match): {len(hook_timings)} words | BODY: {len(body_timings)} words")
    else:
        # Fallback: If no match found, treat all as body
        body_timings = word_timings
        print(f"  ⚠️ No hook match found - using standard rendering for all text")
    
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
    final_video = apply_flash_zoom(final_video, flash_duration=0.3, zoom_factor=1.08)
    
    # 6. RENDER
    final_video.write_videofile(
        str(output_path), fps=30, codec='libx264', audio_codec='aac', 
        threads=4, preset='ultrafast'
    )
    
    # Cleanup
    video.close(); audio.close(); final_video.close()
    if 'bg' in locals(): bg.close()
    return output_path
