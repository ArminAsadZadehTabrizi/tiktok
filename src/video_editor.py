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
        # TODO: Disabled due to .resize(lambda) causing get_frame errors
        # def pulse_effect(t):
        #     # Create a sine wave pulse effect over the duration
        #     progress = t / max(duration, 0.01)
        #     scale = 1.0 + 0.1 * np.sin(progress * np.pi * 2)  # Oscillate between 1.0 and 1.1
        #     return scale
        # 
        # composite = composite.resize(lambda t: pulse_effect(t))
        
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
    🎬 CINEMATIC VISUAL HOOK: Enhanced Zoom Effect
    Creates a dramatic zoom-in effect for the hook scene.
    Now safe to use since clips remain open during rendering.
    """
    w, h = clip.w, clip.h
    
    def zoom_effect(get_frame, t):
        """Progressive zoom from 1.0 to zoom_factor"""
        progress = min(t / clip.duration, 1.0) if clip.duration > 0 else 0
        current_zoom = 1.0 + (zoom_factor - 1.0) * progress
        
        frame = get_frame(t)
        
        # Crop to simulate zoom
        import cv2
        new_w = int(w / current_zoom)
        new_h = int(h / current_zoom)
        x1 = (w - new_w) // 2
        y1 = (h - new_h) // 2
        cropped = frame[y1:y1+new_h, x1:x1+new_w]
        resized = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
        
        return resized
    
    return clip.fl(zoom_effect)


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
    
    🎚️ CINEMATIC AUDIO DUCKING: Triple volume (3.0x) to ensure SFX cuts through music.
    
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
        
        # 🎚️ CINEMATIC DUCKING: Triple volume for maximum impact
        sfx = sfx.volumex(3.0)
        
        # Composite: Mix SFX on top of voiceover
        composite_audio = CompositeAudioClip([audio_clip, sfx])
        composite_audio = composite_audio.set_duration(audio_clip.duration)
        
        print(f"  ✓ Hook SFX added successfully at 0.0s (duration: {sfx.duration:.2f}s, volume: 3.0x)")
        return composite_audio
        
    except Exception as e:
        print(f"  ⚠️ Failed to add hook SFX: {e} - proceeding without auditory hook")
        return audio_clip


def create_rhythmic_scenes(word_timings, total_duration, max_scene_duration=2.0):
    """
    🎬 HYPER-EDITING: Create scenes with aggressive time caps for high retention.
    Forces cuts every 2.0 seconds maximum, regardless of sentence boundaries.
    
    Args:
        word_timings: List of {'word': str, 'start': float, 'end': float}
        total_duration: Total audio duration for validation
        max_scene_duration: Maximum duration per scene (default 2.0s for dopamine pacing)
    
    Returns:
        List of scenes: [{'start_time': float, 'end_time': float, 'duration': float, 'text': str}]
        or None if word_timings is invalid
    """
    if not word_timings or len(word_timings) == 0:
        return None
    
    scenes = []
    current_scene_words = []
    scene_start_time = word_timings[0]['start']
    
    for i, word_data in enumerate(word_timings):
        word = word_data['word']
        current_scene_words.append(word)
        
        # Calculate current scene duration
        current_duration = word_data['end'] - scene_start_time
        
        # Force cut conditions:
        # 1. Duration exceeds max threshold (HARD PACING)
        should_cut_duration = current_duration >= max_scene_duration
        
        # 2. Natural sentence ending (if under threshold)
        is_sentence_end = word.rstrip().endswith(('.', '?', '!'))
        
        # 3. Last word
        is_last_word = (i == len(word_timings) - 1)
        
        # Execute cut if any condition met
        if should_cut_duration or is_sentence_end or is_last_word:
            scene_end_time = word_data['end']
            scene_duration = scene_end_time - scene_start_time
            scene_text = ' '.join(current_scene_words)
            
            scenes.append({
                'start_time': scene_start_time,
                'end_time': scene_end_time,
                'duration': scene_duration,
                'text': scene_text
            })
            
            # Log cut type for debugging
            if should_cut_duration:
                print(f"  ⚡ HARD CUT (2.0s max): \"{scene_text[:30]}...\" ({scene_duration:.2f}s)")
            elif scene_duration < 1.0:
                print(f"  ⚡ Fast cut: \"{scene_text[:30]}...\" ({scene_duration:.2f}s)")
            
            # Reset for next scene
            current_scene_words = []
            if i < len(word_timings) - 1:
                scene_start_time = word_timings[i + 1]['start']
    
    print(f"  📊 Hyper-Edit: {len(scenes)} scenes from {len(word_timings)} words (max {max_scene_duration}s each)")
    return scenes


def create_fixed_duration_scenes(total_duration, fixed_duration=2.0):
    """
    🎬 FALLBACK: Create scenes with fixed duration when word_timings is unavailable.
    Uses the same 2.0s max duration as rhythmic scenes for consistency.
    
    Args:
        total_duration: Total video duration
        fixed_duration: Duration for each scene (default 2.0s for hyper-editing)
    
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


def insert_subliminal_flash(video_clip, flash_position_percent=0.55, flash_duration=0.12):
    """
    🎬 SUBLIMINAL INTERRUPT: Insert brief flash at mid-video to reset attention.
    Creates a "pattern interrupt" for viewer retention by breaking visual monotony.
    
    Args:
        video_clip: The composed video clip
        flash_position_percent: Position in video where flash occurs (0.55 = 55%)
        flash_duration: Duration of flash effect in seconds (0.12s = 120ms)
    
    Returns:
        Video clip with subliminal flash effect applied
    """
    total_duration = video_clip.duration
    flash_start = total_duration * flash_position_percent
    flash_end = flash_start + flash_duration
    
    print(f"  ⚡ Inserting subliminal flash at {flash_start:.2f}s ({flash_position_percent*100:.0f}% mark)")
    
    # Store original get_frame method
    original_get_frame = video_clip.get_frame
    
    def flash_get_frame(t):
        """Modified get_frame that applies flash effect at specific time"""
        frame = original_get_frame(t)
        
        # Apply inversion during flash window
        if flash_start <= t < flash_end:
            inverted = 255 - frame.astype(np.uint8)
            return inverted
        else:
            return frame
    
    # Create new clip with modified get_frame
    from moviepy.video.VideoClip import VideoClip
    flashed_clip = VideoClip(make_frame=flash_get_frame, duration=video_clip.duration)
    
    # Preserve audio if exists
    if video_clip.audio is not None:
        flashed_clip = flashed_clip.set_audio(video_clip.audio)
    
    return flashed_clip


def assign_clips_to_scenes(scenes, video_paths):
    """
    🎬 SMART SUB-CLIPPING: Treat video_paths as a material pool.
    Randomly select clips from different positions for maximum variety.
    
    Args:
        scenes: List of scene dictionaries from create_rhythmic_scenes
        video_paths: List of video file paths (treated as raw material pool)
    
    Returns:
        List of positioned video clips ready for concatenation
    """
    positioned_clips = []
    
    for i, scene in enumerate(scenes):
        duration = scene['duration']
        
        # 🎲 RANDOM VIDEO SELECTION: Pick from material pool
        video_path = random.choice(video_paths)
        
        try:
            clip = VideoFileClip(str(video_path))
            video_duration = clip.duration
            
            # 🎲 RANDOM START TIME: Extract subclip from random position
            if video_duration > duration:
                # Calculate safe random start point
                max_start = video_duration - duration
                random_start = random.uniform(0, max_start)
                subclip = clip.subclip(random_start, random_start + duration)
                print(f"  🎲 Random subclip: {video_path.name} [{random_start:.1f}s - {random_start+duration:.1f}s]")
            else:
                # Video too short - loop it
                num_loops = int(np.ceil(duration / video_duration))
                looped = concatenate_videoclips([clip] * num_loops, method="compose")
                subclip = looped.subclip(0, duration)
                print(f"  🔁 Looped short clip: {video_path.name} ({video_duration:.1f}s) x{num_loops}")
            
            # Apply visual transformations
            subclip = resize_to_vertical(subclip)
            
            # 🚨 HOOK OPTIMIZATION: Extra aggressive effect for first scene (0-1.5s)
            if i == 0:
                print(f"  🎯 HOOK SCENE: Applying aggressive flash zoom")
                subclip = apply_flash_zoom(subclip, flash_duration=0.3, zoom_factor=1.15)
                subclip = subclip.resize(newsize=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT))
                subclip = apply_high_contrast_filter(subclip, contrast=1.4, saturation=1.5)
            else:
                # Standard scenes: Ken Burns zoom for cinematic motion
                print(f"  🎬 STANDARD SCENE: Applying Ken Burns zoom")
                subclip = apply_ken_burns_zoom(subclip, zoom_factor=1.25)
                subclip = subclip.resize(newsize=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT))
                subclip = apply_high_contrast_filter(subclip, contrast=1.2, saturation=1.3)
            
            subclip = subclip.without_audio()
            subclip = subclip.set_duration(duration)
            
            positioned_clips.append(subclip)
            # CRITICAL: Do NOT close clips here - MoviePy needs them open for lazy evaluation
            # Closing clips breaks .fl() and other effects, causing 'NoneType' get_frame errors
            
            print(f"  🎥 Scene {i+1}/{len(scenes)}: {duration:.2f}s - \"{scene['text'][:40]}...\"")
            
        except Exception as e:
            print(f"  ⚠️ Error processing {video_path}: {e}")
            # Graceful fallback: reuse previous clip if available
            if positioned_clips:
                fallback = positioned_clips[-1].set_duration(duration)
                positioned_clips.append(fallback)
                print(f"  🔄 Using fallback clip for scene {i+1}")
            continue
    
    return positioned_clips


def stitch_and_edit_video(video_paths, audio_path, script_data, output_path):
    print(f"🎬 Editing video (Success Aesthetic)...")
    
    audio = AudioFileClip(str(audio_path))
    main_duration = audio.duration  # Store main duration for reference
    
    # 1. VOICEOVER POLISH: Slight volume boost for clarity against loud music
    audio = audio.volumex(1.1)
    
    # 2. HOOK SFX OVERLAY (Auditory Hook)
    audio = add_hook_sfx(audio)

    # 3. TRANSITION SFX: Add whoosh/boom sounds at scene changes
    sfx_dir = config.ASSETS_DIR / "sfx"
    sfx_files = [f for f in sfx_dir.glob("*.mp3") if f.name != ".DS_Store"] if sfx_dir.exists() else []
    
    if sfx_files:
        print(f"  🔊 Found {len(sfx_files)} transition SFX files")
    
    final_audio = audio

    # 4. BACKGROUND MUSIC MIX (Random Track Selection + Cinematic Fade-In)
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
            
            # 🎚️ CINEMATIC AUDIO DUCKING: Randomized Start + Fast Fade-In
            # Randomize music start to avoid silent intros (songs often have 2-3s silence at 0.0s)
            start_time = random.uniform(0, max(0, bg.duration - main_duration))
            bg = bg.subclip(start_time, min(start_time + main_duration, bg.duration))
            bg = bg.audio_fadein(0.5)  # 0.5-second fade-in for immediate impact
            bg = bg.volumex(config.BG_MUSIC_VOLUME)  # Apply final volume level
            bg = bg.set_duration(main_duration)  # Explicit duration
            
            print(f"  🎬 Music randomized: start={start_time:.2f}s, fade-in=0.5s for instant impact")
            
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
        
    # 2. VISUALS - HYPER-EDITING WITH RHYTHMIC SCENES
    print(f"  🎬 Creating rhythmic scenes (max 2.0s each) for high retention...")
    
    # Create scenes with aggressive 2.0s pacing
    scenes = create_rhythmic_scenes(word_timings, main_duration, max_scene_duration=2.0)
    
    # Fallback to fixed duration if no word_timings available
    if scenes is None:
        print(f"  ⚠️ No word timings available - using fallback fixed duration")
        scenes = create_fixed_duration_scenes(main_duration, fixed_duration=2.0)
    
    # Assign video clips to scenes
    video_clips = assign_clips_to_scenes(scenes, video_paths)
    
    # 🎬 ADD TRANSITION SFX AT SCENE CHANGES (Dopamine Triggers)
    # Overlay random whoosh/boom sounds at each cut for engagement
    transition_audio_clips = []
    if sfx_files and scenes:
        print(f"  🔊 Adding transition SFX at {len(scenes)-1} scene changes...")
        for i in range(len(scenes) - 1):  # Add SFX at every cut (except last scene)
            scene_end_time = scenes[i]['end_time']
            try:
                # Pick random SFX from pool
                sfx_path = random.choice(sfx_files)
                sfx = AudioFileClip(str(sfx_path))
                
                # 🎬 TIGHTER OFFSET: Start SFX 0.1s BEFORE the visual cut
                # Tighter timing for fast-paced edits - peak aligns with the cut
                start_time = max(0, scene_end_time - 0.1)
                
                # Trim SFX if longer than 1.0s for quick punchy effect
                sfx_duration = min(sfx.duration, 1.0)
                sfx = sfx.subclip(0, sfx_duration)
                
                # 🎚️ SOFT FADES: Apply tight fades to prevent clicking
                sfx = sfx.audio_fadein(0.1).audio_fadeout(0.1)
                
                # Very low volume (0.2x) - subtle texture, felt not heard
                sfx = sfx.volumex(0.2)
                
                sfx = sfx.set_start(start_time)
                
                transition_audio_clips.append(sfx)
                print(f"    🎚️ Transition {i+1}: {sfx_path.name} at {start_time:.2f}s (pre-roll: -0.1s)")
            except Exception as e:
                print(f"  ⚠️ Failed to add transition SFX at {scene_end_time:.2f}s: {e}")
    
    # Mix transition SFX into final audio
    if transition_audio_clips:
        final_audio = CompositeAudioClip([final_audio] + transition_audio_clips)
        final_audio = final_audio.set_duration(main_duration)
        print(f"  ✓ {len(transition_audio_clips)} transition SFX added to audio mix")
    
    if not video_clips:
        raise Exception("No valid video clips could be loaded.")
    
    # Concatenate all positioned clips
    video = concatenate_videoclips(video_clips, method="compose")
    
    # Ensure exact duration match with audio
    # TODO: Duration adjustment via subclip causes get_frame errors - disabled for now
    # if video.duration != main_duration:
    #     print(f"  ⚠️ Adjusting video duration from {video.duration:.2f}s to {main_duration:.2f}s")
    #     video = video.subclip(0, min(video.duration, main_duration))
    #     video = video.set_duration(main_duration)
    
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
    
    # 🎬 SUBLIMINAL INTERRUPT: Insert pattern-breaking flash at mid-video
    print(f"  ⚡ Applying subliminal flash interrupt...")
    final_video = insert_subliminal_flash(final_video, flash_position_percent=0.55, flash_duration=0.12)
    
    # 6. RENDER
    final_video.write_videofile(
        str(output_path), fps=30, codec='libx264', audio_codec='aac', 
        threads=4, preset='ultrafast'
    )
    
    # Cleanup
    video.close(); audio.close(); final_video.close()
    if 'bg' in locals(): bg.close()
    return output_path
