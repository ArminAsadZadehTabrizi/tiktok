"""Pexels Video API integration for downloading luxury/motivational footage"""
import requests
import time
import math
import random
from pathlib import Path
import config

# Constants
CLIP_DURATION = 2.5  # Each video clip duration in seconds (matches video_editor.py)


def search_pexels(query, orientation="portrait"):
    """
    Search for videos on Pexels.
    
    Args:
        query (str): Search query
        orientation (str): Video orientation (portrait/landscape)
    
    Returns:
        list: Video URLs found
    """
    headers = {"Authorization": config.PEXELS_API_KEY}
    params = {
        "query": query,
        "orientation": orientation,
        "size": config.PEXELS_SIZE,
        "per_page": 5
    }
    
    try:
        response = requests.get(config.PEXELS_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        videos = data.get("videos", [])
        
        video_urls = []
        for video in videos[:3]:  # Get up to 3 videos
            video_files = video.get("video_files", [])
            vertical_files = [
                vf for vf in video_files 
                if vf.get("height", 0) > vf.get("width", 0)
            ]
            
            if vertical_files:
                target_height = 1920
                vertical_files.sort(key=lambda x: abs(x.get("height", 0) - target_height))
                video_urls.append(vertical_files[0]["link"])
        
        return video_urls
    
    except Exception as e:
        print(f"    ✗ Pexels error: {e}")
        return []


def search_pixabay(query, orientation="portrait"):
    """
    Search for videos on Pixabay.
    
    Args:
        query (str): Search query
        orientation (str): Video orientation (vertical/horizontal)
    
    Returns:
        list: Video URLs found
    """
    # Map orientation to Pixabay format
    pixabay_orientation = "vertical" if orientation == "portrait" else "horizontal"
    
    params = {
        "key": config.PIXABAY_API_KEY,
        "q": query,
        "video_type": "film",
        "orientation": pixabay_orientation,
        "per_page": 3
    }
    
    try:
        response = requests.get(config.PIXABAY_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        hits = data.get("hits", [])
        
        video_urls = []
        for hit in hits:
            videos = hit.get("videos", {})
            # Prefer large or medium quality
            if "large" in videos:
                video_urls.append(videos["large"]["url"])
            elif "medium" in videos:
                video_urls.append(videos["medium"]["url"])
            elif "small" in videos:
                video_urls.append(videos["small"]["url"])
        
        return video_urls
    
    except Exception as e:
        print(f"    ✗ Pixabay error: {e}")
        return []


def search_videos(keywords, num_videos=3):
    """
    Search for videos using HYBRID approach (Pexels + Pixabay).
    
    Args:
        keywords (list): List of search terms
        num_videos (int): Number of videos to find
    
    Returns:
        list: Video data including download URLs
    """
    all_videos = []
    
    # DARK DISCIPLINE FILTER: Training, grind, and moody athletic visuals
    # Goal: Faceless, disciplined training aesthetic for motivation content
    success_suffixes = [
        "shadow boxing silhouette",
        "hooded figure training dark",
        "running in rain night",
        "heavy bag workout dark",
        "gym workout night mood",
        "person training alone dark"
    ]
    
    for keyword in keywords:
        # Pick a random success suffix for this search
        style = random.choice(success_suffixes)
        search_query = f"{keyword} {style}"
        
        # HYBRID SEARCH: Randomly choose between Pexels and Pixabay
        if random.random() > 0.5:
            primary_source = "pixabay"
            secondary_source = "pexels"
        else:
            primary_source = "pexels"
            secondary_source = "pixabay"
        
        video_urls = []
        
        # Try primary source first
        if primary_source == "pixabay":
            print(f"  🔍 Searching Pixabay for: '{search_query}'")
            video_urls = search_pixabay(search_query)
        else:
            print(f"  🔍 Searching Pexels for: '{search_query}'")
            video_urls = search_pexels(search_query)
        
        # Fallback to secondary source if primary returns nothing
        if not video_urls:
            print(f"    ↪️  Falling back to {secondary_source.capitalize()}...")
            if secondary_source == "pixabay":
                video_urls = search_pixabay(search_query)
            else:
                video_urls = search_pexels(search_query)
        
        # Process found videos
        if video_urls:
            for idx, url in enumerate(video_urls):
                keyword_variant = f"{keyword}_var{idx+1}"
                video_info = {
                    "url": url,
                    "width": 1080,  # Default values for hybrid sources
                    "height": 1920,
                    "keyword": keyword_variant,
                    "source": primary_source if video_urls else secondary_source
                }
                all_videos.append(video_info)
                print(f"    ✓ Found video {idx+1} from {video_info['source'].capitalize()}")
        else:
            print(f"    ✗ No videos found for '{keyword}' on either source")
        
        # Be nice to the APIs
        time.sleep(0.5)
    
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
