"""MoviePy-based video editor for creating Dark Facts TikTok videos"""
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, 
    CompositeAudioClip, TextClip, concatenate_videoclips,
    ColorClip
)
from moviepy.video.fx import resize, colorx
import numpy as np
from pathlib import Path
import config


def apply_dark_filter(clip):
    """
    Apply a dark, high-contrast black and white filter.
    
    Args:
        clip: MoviePy VideoClip
    
    Returns:
        VideoClip with dark filter applied
    """
    # Convert to grayscale and increase contrast
    def grayscale_high_contrast(image):
        # Convert to grayscale
        gray = np.dot(image[...,:3], [0.299, 0.587, 0.114])
        
        # Increase contrast (darken darks, lighten lights)
        gray = np.clip((gray - 128) * 1.5 + 128, 0, 255)
        
        # Convert back to RGB
        return np.stack([gray, gray, gray], axis=-1).astype('uint8')
    
    return clip.fl_image(grayscale_high_contrast)


def resize_to_vertical(clip):
    """
    Resize and crop video to vertical 9:16 format.
    
    Args:
        clip: MoviePy VideoClip
    
    Returns:
        VideoClip resized to 1080x1920
    """
    target_width = config.VIDEO_WIDTH
    target_height = config.VIDEO_HEIGHT
    target_ratio = target_height / target_width
    
    clip_ratio = clip.h / clip.w
    
    if clip_ratio > target_ratio:
        # Video is too tall, fit to width
        new_width = target_width
        new_height = int(clip.h * (target_width / clip.w))
    else:
        # Video is too wide, fit to height
        new_height = target_height
        new_width = int(clip.w * (target_height / clip.h))
    
    # Resize
    clip = clip.resize((new_width, new_height))
    
    # Center crop to exact dimensions
    x_center = new_width / 2
    y_center = new_height / 2
    
    clip = clip.crop(
        x_center=x_center,
        y_center=y_center,
        width=target_width,
        height=target_height
    )
    
    return clip


def create_caption_clip(text, duration, start_time):
    """
    Create a text caption with typewriter effect.
    
    Args:
        text (str): Caption text
        duration (float): How long to display
        start_time (float): When to start
    
    Returns:
        TextClip with styling
    """
    try:
        # Try to create text clip with custom font
        txt_clip = TextClip(
            text,
            fontsize=config.CAPTION_FONTSIZE,
            color=config.CAPTION_COLOR,
            font=config.CAPTION_FONT,
            stroke_color=config.CAPTION_STROKE_COLOR,
            stroke_width=config.CAPTION_STROKE_WIDTH,
            method='caption',
            size=(config.VIDEO_WIDTH - 100, None),  # Leave margin
            align='center'
        )
    except Exception as e:
        # Fallback to default font if custom font fails
        print(f"  Warning: Custom font failed, using default: {e}")
        txt_clip = TextClip(
            text,
            fontsize=config.CAPTION_FONTSIZE,
            color=config.CAPTION_COLOR,
            stroke_color=config.CAPTION_STROKE_COLOR,
            stroke_width=config.CAPTION_STROKE_WIDTH,
            method='caption',
            size=(config.VIDEO_WIDTH - 100, None),
            align='center'
        )
    
    txt_clip = txt_clip.set_duration(duration).set_start(start_time)
    
    # Position in center
    txt_clip = txt_clip.set_position(('center', 'center'))
    
    return txt_clip


def split_text_for_timing(script_data, audio_duration):
    """
    Split script into segments for caption timing.
    
    Args:
        script_data (dict): Script with 'hook' and 'body'
        audio_duration (float): Total audio length
    
    Returns:
        list: Tuples of (text, start_time, duration)
    """
    segments = []
    
    # Split into sentences/phrases
    hook = script_data['hook']
    body = script_data['body']
    
    # Simple approach: show hook first, then body
    hook_duration = audio_duration * 0.2  # Hook takes ~20% of time
    body_duration = audio_duration * 0.8
    
    segments.append((hook, 0, hook_duration))
    segments.append((body, hook_duration, body_duration))
    
    return segments


def stitch_and_edit_video(video_paths, audio_path, script_data, output_path):
    """
    Main video editing function: stitch videos, add filters, captions, and audio.
    
    Args:
        video_paths (list): Paths to downloaded videos
        audio_path (Path): Path to voiceover audio
        script_data (dict): Script data with text
        output_path (Path): Where to save final video
    
    Returns:
        Path: Path to the final video
    """
    print(f"\n🎬 Editing video")
    
    try:
        # Load audio to get duration
        audio = AudioFileClip(str(audio_path))
        target_duration = audio.duration
        
        print(f"  Audio duration: {target_duration:.2f}s")
        
        # Load and process video clips
        clips = []
        for video_path in video_paths:
            print(f"  Processing: {video_path.name}")
            clip = VideoFileClip(str(video_path))
            
            # Resize to vertical format
            clip = resize_to_vertical(clip)
            
            # Apply dark filter
            clip = apply_dark_filter(clip)
            
            # Remove original audio
            clip = clip.without_audio()
            
            clips.append(clip)
        
        # Concatenate and loop clips to match audio duration
        video = concatenate_videoclips(clips)
        
        # Loop video if it's shorter than audio
        if video.duration < target_duration:
            num_loops = int(np.ceil(target_duration / video.duration))
            video = concatenate_videoclips([video] * num_loops)
        
        # Trim to exact audio duration
        video = video.subclip(0, target_duration)
        
        print(f"  ✓ Videos stitched and filtered")
        
        # Add background music if available
        if config.BACKGROUND_MUSIC_PATH.exists():
            print(f"  Adding background music")
            bg_music = AudioFileClip(str(config.BACKGROUND_MUSIC_PATH))
            
            # Loop background music if needed
            if bg_music.duration < target_duration:
                num_loops = int(np.ceil(target_duration / bg_music.duration))
                bg_music = concatenate_videoclips([bg_music] * num_loops)
            
            bg_music = bg_music.subclip(0, target_duration)
            bg_music = bg_music.volumex(config.BG_MUSIC_VOLUME)
            
            # Mix voiceover and background music
            final_audio = CompositeAudioClip([audio, bg_music])
        else:
            print(f"  No background music found at {config.BACKGROUND_MUSIC_PATH}")
            final_audio = audio
        
        video = video.set_audio(final_audio)
        
        # Create captions
        print(f"  Adding captions")
        text_segments = split_text_for_timing(script_data, target_duration)
        text_clips = []
        
        for text, start_time, duration in text_segments:
            text_clip = create_caption_clip(text, duration, start_time)
            text_clips.append(text_clip)
        
        # Composite video with text overlays
        final_video = CompositeVideoClip([video] + text_clips)
        
        print(f"  ✓ Captions added")
        
        # Export final video
        print(f"  Rendering final video...")
        final_video.write_videofile(
            str(output_path),
            fps=config.VIDEO_FPS,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(config.ASSETS_DIR / 'temp-audio.m4a'),
            remove_temp=True,
            threads=4,
            preset='medium'
        )
        
        # Clean up
        for clip in clips:
            clip.close()
        video.close()
        audio.close()
        if config.BACKGROUND_MUSIC_PATH.exists():
            bg_music.close()
        final_video.close()
        
        print(f"✓ Video editing complete\n")
        
        return output_path
    
    except Exception as e:
        print(f"✗ Error during video editing: {e}")
        raise


if __name__ == "__main__":
    print("Video editor module - run main.py to generate videos")
