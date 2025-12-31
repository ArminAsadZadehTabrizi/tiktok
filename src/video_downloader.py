"""Pexels Video API integration for downloading luxury/motivational footage"""
import requests
import time
import math
import random
from pathlib import Path
import config

# Constants
CLIP_DURATION = 2.5  # Each video clip duration in seconds (matches video_editor.py)
MIN_VIDEO_DURATION = 10  # Minimum video duration in seconds to avoid looping issues

# Dark aesthetic fallback keywords for when specific searches fail
DARK_AESTHETIC_FALLBACKS = [
    "dark moody atmosphere",
    "cinematic noir",
    "abstract shadows",
    "dark silhouette",
    "moody lighting",
    "gritty urban night",
    "dark smoke abstract"
]


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
            # Check video duration first (fix for short video looping)
            duration = video.get("duration", 0)
            if duration < MIN_VIDEO_DURATION:
                print(f"    ✗ Video duration: {duration}s (too short, skipped)")
                continue
            
            video_files = video.get("video_files", [])
            vertical_files = [
                vf for vf in video_files 
                if vf.get("height", 0) > vf.get("width", 0)
            ]
            
            if vertical_files:
                target_height = 1920
                vertical_files.sort(key=lambda x: abs(x.get("height", 0) - target_height))
                video_urls.append(vertical_files[0]["link"])
                print(f"    ✓ Video duration: {duration}s (passed filter)")
        
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
            # Check video duration first (fix for short video looping)
            duration = hit.get("duration", 0)
            if duration < MIN_VIDEO_DURATION:
                print(f"    ✗ Video duration: {duration}s (too short, skipped)")
                continue
            
            videos = hit.get("videos", {})
            # Prefer large or medium quality
            if "large" in videos:
                video_urls.append(videos["large"]["url"])
                print(f"    ✓ Video duration: {duration}s (passed filter)")
            elif "medium" in videos:
                video_urls.append(videos["medium"]["url"])
                print(f"    ✓ Video duration: {duration}s (passed filter)")
            elif "small" in videos:
                video_urls.append(videos["small"]["url"])
                print(f"    ✓ Video duration: {duration}s (passed filter)")
        
        return video_urls
    
    except Exception as e:
        print(f"    ✗ Pixabay error: {e}")
        return []


def search_videos(visual_queries, fallback_topic=None):
    """
    🎬 SEMANTIC VISUAL SEARCH: Search for videos using specific visual queries.
    Each query should already contain full scene description (e.g., "lonely man walking in crowd blur").
    
    Args:
        visual_queries (list): List of specific visual search queries (one per segment)
        fallback_topic (str): Generic topic keyword to use if specific search fails
    
    Returns:
        list: Video data including download URLs, one per query
    """
    all_videos = []
    
    for i, visual_query in enumerate(visual_queries):
        print(f"  🔍 Searching for segment {i}: '{visual_query}'")
        
        # HYBRID SEARCH: Randomly choose between Pexels and Pixabay
        if random.random() > 0.5:
            primary_source = "pixabay"
            secondary_source = "pexels"
        else:
            primary_source = "pexels"
            secondary_source = "pixabay"
        
        video_urls = []
        
        # Try primary source first with the specific visual query
        if primary_source == "pixabay":
            print(f"    → Pixabay: '{visual_query}'")
            video_urls = search_pixabay(visual_query)
        else:
            print(f"    → Pexels: '{visual_query}'")
            video_urls = search_pexels(visual_query)
        
        # Fallback to secondary source if primary returns nothing
        if not video_urls:
            print(f"    ↪️  Trying {secondary_source.capitalize()}...")
            if secondary_source == "pixabay":
                video_urls = search_pixabay(visual_query)
            else:
                video_urls = search_pexels(visual_query)
        
        # FALLBACK TIER 3: If specific query fails, try generic topic keyword
        if not video_urls and fallback_topic:
            print(f"    ⚠️  Specific search failed, using fallback: '{fallback_topic}'")
            if primary_source == "pixabay":
                video_urls = search_pixabay(fallback_topic)
            else:
                video_urls = search_pexels(fallback_topic)
        
        # FALLBACK TIER 4: Dark aesthetic keywords (final fallback for consistent vibe)
        if not video_urls:
            dark_keyword = random.choice(DARK_AESTHETIC_FALLBACKS)
            print(f"    🎬 All searches failed, using dark aesthetic fallback: '{dark_keyword}'")
            if primary_source == "pixabay":
                video_urls = search_pixabay(dark_keyword)
            else:
                video_urls = search_pexels(dark_keyword)
        
        # Process found videos - take the FIRST/BEST match only
        if video_urls:
            url = video_urls[0]  # Take best match (first result)
            video_info = {
                "url": url,
                "width": 1080,
                "height": 1920,
                "query": visual_query,
                "segment_index": i,
                "source": primary_source if video_urls else secondary_source
            }
            all_videos.append(video_info)
            print(f"    ✓ Found video from {video_info['source'].capitalize()}")
        else:
            print(f"    ✗ No videos found for '{visual_query}' on either source")
            # Add placeholder to maintain segment order
            all_videos.append(None)
        
        # Be nice to the APIs
        time.sleep(0.5)
    
    # Filter out None values (failed searches) but warn user
    valid_videos = [v for v in all_videos if v is not None]
    if len(valid_videos) < len(visual_queries):
        print(f"  ⚠️  Warning: Only found {len(valid_videos)}/{len(visual_queries)} videos")
    
    return valid_videos


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


def download_videos(visual_queries, fallback_topic=None):
    """
    🎬 SEMANTIC VISUAL DOWNLOAD: Download videos for specific visual queries.
    Each video is saved as segment_N.mp4 to match script segment order.
    
    Args:
        visual_queries (list): List of specific visual search queries (from script segments)
        fallback_topic (str): Generic topic keyword for fallback searches
    
    Returns:
        list: Paths to downloaded video files (segment_0.mp4, segment_1.mp4, etc.)
    """
    print(f"\n📹 Downloading {len(visual_queries)} segment-specific videos")
    print(f"   Fallback topic: {fallback_topic or 'None'}")
    
    # Search for videos using semantic queries
    videos = search_videos(visual_queries, fallback_topic=fallback_topic)
    
    if not videos:
        raise Exception("No videos found. Check your API keys and visual queries.")
    
    # Download videos with segment-based naming
    downloaded_paths = []
    for video in videos:
        segment_index = video["segment_index"]
        output_path = config.ASSETS_DIR / f"segment_{segment_index}.mp4"
        
        if download_video(video["url"], output_path):
            downloaded_paths.append(output_path)
            print(f"  ✓ segment_{segment_index}.mp4: '{video['query']}'")
    
    if not downloaded_paths:
        raise Exception("Failed to download any videos")
    
    # Sort by segment index to ensure correct order
    downloaded_paths.sort(key=lambda p: int(p.stem.split('_')[1]))
    
    print(f"✓ Downloaded {len(downloaded_paths)} segment video(s)\n")
    return downloaded_paths


if __name__ == "__main__":
    # Test the video downloader
    test_keywords = ["dark ocean", "foggy forest", "night sky"]
    videos = download_videos(test_keywords, num_videos=2)
    print(f"Downloaded videos: {videos}")
