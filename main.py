#!/usr/bin/env python3
"""
Dark Facts TikTok Generator
Fully automated script to create creepy/unsettling fact videos for TikTok.

Usage:
    python main.py

Requirements:
    - .env file with OPENAI_API_KEY and PEXELS_API_KEY
    - Optional: background_music.mp3 in assets/ folder
"""

import sys
from pathlib import Path
from datetime import datetime
import config

# Import our modules
from src.script_generator import generate_script
from src.video_downloader import download_videos
from src.audio_generator import generate_audio
from src.video_editor import stitch_and_edit_video


def cleanup_temp_files():
    """Remove temporary files from assets folder."""
    print("🧹 Cleaning up temporary files")
    
    temp_files = list(config.ASSETS_DIR.glob("temp_*"))
    for temp_file in temp_files:
        try:
            temp_file.unlink()
            print(f"  Deleted: {temp_file.name}")
        except Exception as e:
            print(f"  Warning: Could not delete {temp_file.name}: {e}")


def validate_setup():
    """Validate that all required API keys and settings are configured."""
    errors = []
    
    if not config.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY not found in .env file")
    
    if not config.PEXELS_API_KEY:
        errors.append("PEXELS_API_KEY not found in .env file")
    
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease create a .env file with your API keys.")
        print("See .env.example for the required format.")
        sys.exit(1)
    
    # Check for background music (warning only)
    if not config.BACKGROUND_MUSIC_PATH.exists():
        print("⚠️  Warning: No background music found")
        print(f"   Place your .mp3 file at: {config.BACKGROUND_MUSIC_PATH}")
        print("   Continuing without background music...\n")


def main():
    """Main orchestration function."""
    print("=" * 60)
    print("🎬 DARK FACTS TIKTOK GENERATOR")
    print("=" * 60)
    print()
    
    # Validate setup
    validate_setup()
    
    # Get custom topic from user
    topic = input("🔥 Enter a specific Trend/Topic (or press Enter for random): ").strip()
    if not topic:
        topic = None
    print()
    
    try:
        # Step 1: Generate script using LLM
        print("📝 Step 1: Generating dark fact script")
        script_data = generate_script(topic)
        
        # Step 2: Generate TTS audio (moved before video download)
        print("🎤 Step 2: Generating voiceover")
        audio_path = generate_audio(script_data)
        
        # Step 3: Download videos from Pexels (now with exact clip calculation)
        print("📹 Step 3: Downloading videos from Pexels")
        from moviepy.editor import AudioFileClip
        audio_clip = AudioFileClip(str(audio_path))
        audio_duration = audio_clip.duration
        audio_clip.close()
        
        video_paths = download_videos(script_data['keywords'], audio_duration=audio_duration)
        
        # Step 4: Edit and compose final video
        print("🎬 Step 4: Editing and composing video")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = config.OUTPUT_DIR / f"dark_facts_{timestamp}.mp4"
        
        final_video = stitch_and_edit_video(
            video_paths=video_paths,
            audio_path=audio_path,
            script_data=script_data,
            output_path=output_path
        )
        
        # Success!
        print("=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"\n📹 Your Dark Facts video is ready:")
        print(f"   {final_video}")
        print()
        print("Script used:")
        print(f"  Hook: {script_data['hook']}")
        print(f"  Body: {script_data['body']}")
        print()
        
        # Twitter Automation (Optional)
        twitter_posted = False
        try:
            user_choice = input("🐦 Post to Twitter? (y/n): ").strip().lower()
            
            if user_choice == 'y':
                print()
                from src.twitter_manager import TwitterManager
                
                # Initialize Twitter manager
                twitter_manager = TwitterManager()
                
                # Generate thread from script
                thread_content = twitter_manager.generate_thread_from_script(script_data)
                
                # Preview thread for user
                print("\n" + "=" * 60)
                print("📋 THREAD PREVIEW")
                print("=" * 60)
                for i, tweet in enumerate(thread_content, 1):
                    print(f"\nTweet {i}/{len(thread_content)} ({len(tweet)} chars):")
                    print(f"  {tweet}")
                print("\n" + "=" * 60)
                print()
                
                # Post to Twitter
                thread_url = twitter_manager.post_thread(final_video, thread_content)
                twitter_posted = True
                
                print("\n🎉 Video and thread posted to Twitter successfully!")
                print(f"🔗 View thread: {thread_url}")
                print()
            else:
                print("\n⏭️  Skipping Twitter posting")
                print()
        
        except KeyboardInterrupt:
            print("\n\n⏭️  Twitter posting cancelled by user")
            print()
        except Exception as e:
            print(f"\n⚠️  Twitter posting failed: {e}")
            print("   Your video was still generated successfully!")
            print()
        
        # Cleanup (always runs, even if Twitter fails)
        cleanup_temp_files()
        
        if twitter_posted:
            print("🎉 Done! Video generated and posted to Twitter!")
        else:
            print("🎉 Done! Ready to upload to TikTok!")
        print()
        
    except KeyboardInterrupt:
        print("\n\n❌ Generation cancelled by user")
        cleanup_temp_files()
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nGeneration failed. Check the error message above.")
        cleanup_temp_files()
        sys.exit(1)


if __name__ == "__main__":
    main()
