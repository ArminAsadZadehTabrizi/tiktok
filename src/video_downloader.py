"""Pexels Video API integration for downloading dark/moody footage"""
import requests
import time
import math
from pathlib import Path
import config

# Constants
CLIP_DURATION = 2.5  # Each video clip duration in seconds (matches video_editor.py)


def search_videos(keywords, num_videos=3):
    """
    Search for videos on Pexels using given keywords.
    
    Args:
        keywords (list): List of search terms
        num_videos (int): Number of videos to find
    
    Returns:
        list: Video data including download URLs
    """
    headers = {
        "Authorization": config.PEXELS_API_KEY
    }
    
    all_videos = []
    
    for keyword in keywords:
        print(f"  Searching Pexels for: '{keyword}'")
        
        params = {
            "query": f"{keyword} horror creepy dark close up",  # HORROR AESTHETIC: Enforce scary visuals
            "orientation": config.PEXELS_ORIENTATION,
            "size": config.PEXELS_SIZE,
            "per_page": 5  # Get a few options
        }
        
        try:
            response = requests.get(
                config.PEXELS_API_URL,
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            videos = data.get("videos", [])
            
            if videos:
                # Get up to 3 videos from this keyword search for variety
                videos_to_process = min(3, len(videos))
                
                for idx in range(videos_to_process):
                    video = videos[idx]
                    
                    # Find the best quality vertical video file
                    video_files = video.get("video_files", [])
                    vertical_files = [
                        vf for vf in video_files 
                        if vf.get("height", 0) > vf.get("width", 0)  # Portrait orientation
                    ]
                    
                    if vertical_files:
                        # SMART SORT: Prioritize files closest to 1920px height (1080p)
                        # This prevents downloading massive 4K files.
                        target_height = 1920
                        vertical_files.sort(key=lambda x: abs(x.get("height", 0) - target_height))
                        
                        # Add unique suffix to keyword to prevent duplicate filtering
                        keyword_variant = f"{keyword}_var{idx+1}"
                        
                        video_info = {
                            "url": vertical_files[0]["link"],
                            "width": vertical_files[0].get("width"),
                            "height": vertical_files[0].get("height"),
                            "keyword": keyword_variant
                        }
                        all_videos.append(video_info)
                        print(f"    ✓ Found video {idx+1} ({video_info['width']}x{video_info['height']}) - Optimized for TikTok")
                    
                    # Be nice to the API between videos from same keyword
                    if idx < videos_to_process - 1:
                        time.sleep(0.3)
            else:
                print(f"    ✗ No videos found for '{keyword}'")
            
            # Be nice to the API
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"    ✗ Error searching for '{keyword}': {e}")
            continue
    
    # Ensure we have enough videos
    if len(all_videos) < num_videos:
        print(f"  Warning: Only found {len(all_videos)} videos (requested {num_videos})")
    
    return all_videos[:num_videos]


def download_video(video_url, output_path):
    """
    Download a video from URL to local path.
    
    Args:
        video_url (str): URL of the video to download
        output_path (Path): Where to save the video
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"    Downloading: {output_path.name}")
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"    ✓ Download complete")
        return True
    
    except Exception as e:
        print(f"    ✗ Download failed: {e}")
        return False


def download_videos(keywords, audio_duration=None, num_videos=None):
    """
    Search and download videos for the given keywords.
    
    Args:
        keywords (list): Search terms from script generation
        audio_duration (float): Duration of audio in seconds (to calculate exact clips needed)
        num_videos (int): Number of videos to download (optional, overrides calculation)
    
    Returns:
        list: Paths to downloaded video files
    """
    print(f"\n📹 Downloading videos from Pexels")
    
    # Calculate exact number of clips needed to avoid repetition
    if num_videos is None and audio_duration is not None:
        num_videos = math.ceil(audio_duration / CLIP_DURATION)
        print(f"  📊 Calculated need for {num_videos} unique clips (audio: {audio_duration:.1f}s, clip duration: {CLIP_DURATION}s)")
    elif num_videos is None:
        num_videos = 3  # Fallback default
    
    # Search for videos
    videos = search_videos(keywords, num_videos)
    
    if not videos:
        raise Exception("No videos found. Check your Pexels API key and keywords.")
    
    # Download videos
    downloaded_paths = []
    for i, video in enumerate(videos):
        output_path = config.ASSETS_DIR / f"temp_video_{i}.mp4"
        
        if download_video(video["url"], output_path):
            downloaded_paths.append(output_path)
    
    if not downloaded_paths:
        raise Exception("Failed to download any videos")
    
    print(f"✓ Downloaded {len(downloaded_paths)} video(s)\n")
    return downloaded_paths


if __name__ == "__main__":
    # Test the video downloader
    test_keywords = ["dark ocean", "foggy forest", "night sky"]
    videos = download_videos(test_keywords, num_videos=2)
    print(f"Downloaded videos: {videos}")
