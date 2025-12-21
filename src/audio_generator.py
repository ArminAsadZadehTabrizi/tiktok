"""Text-to-speech generation using Edge TTS"""
import asyncio
import edge_tts
from pathlib import Path
import config


async def generate_audio_async(text, output_path):
    """
    Asynchronously generate TTS audio.
    
    Args:
        text (str): The text to convert to speech
        output_path (Path): Where to save the audio file
    """
    communicate = edge_tts.Communicate(
        text=text,
        voice=config.TTS_VOICE,
        rate=config.TTS_RATE,
        volume=config.TTS_VOLUME
    )
    
    await communicate.save(str(output_path))


def generate_audio(script_data):
    """
    Generate TTS audio from script using Edge TTS.
    
    Args:
        script_data (dict): Script with 'hook' and 'body' keys
    
    Returns:
        Path: Path to the generated audio file
    """
    print(f"\n🎤 Generating voiceover")
    
    # Combine hook and body for full script
    full_text = f"{script_data['hook']} {script_data['body']}"
    
    output_path = config.ASSETS_DIR / "temp_voiceover.mp3"
    
    try:
        # Run the async function
        asyncio.run(generate_audio_async(full_text, output_path))
        
        print(f"✓ Audio generated: {config.TTS_VOICE}")
        print(f"  Output: {output_path.name}\n")
        
        return output_path
    
    except Exception as e:
        print(f"✗ Error generating audio: {e}")
        raise


def get_audio_duration(audio_path):
    """
    Get the duration of an audio file using MoviePy.
    
    Args:
        audio_path (Path): Path to audio file
    
    Returns:
        float: Duration in seconds
    """
    from moviepy.editor import AudioFileClip
    
    audio = AudioFileClip(str(audio_path))
    duration = audio.duration
    audio.close()
    
    return duration


if __name__ == "__main__":
    # Test the audio generator
    test_script = {
        "hook": "Did you know that the ocean is full of terrifying creatures?",
        "body": "In the deepest parts of the ocean, there are creatures that have never seen sunlight. Some have teeth longer than their entire body, and many produce their own eerie bioluminescent light to lure prey in the eternal darkness."
    }
    
    audio_path = generate_audio(test_script)
    duration = get_audio_duration(audio_path)
    print(f"Audio duration: {duration:.2f} seconds")
