"""Pexels Video API integration for downloading luxury/motivational footage"""
import requests
import time
import math
import random
from pathlib import Path
import config

# Constants
CLIP_DURATION = 2.5  # Each video clip duration in seconds (matches video_editor.py)
MIN_VIDEO_DURATION = 15  # Minimum video duration in seconds to avoid looping with sped-up edits

# Tate/Mafia aesthetic fallback keywords for when specific searches fail
DARK_AESTHETIC_FALLBACKS = [
    "mafia aesthetic dark",
    "luxury car night drive cinematic",
    "boxing intense dark gym",
    "lamborghini night city lights",
    "man suit smoking dark",
    "private jet interior luxury",
    "shadow boxing dark moody",
    "greek statue dark marble",
    "wolf pack night moody",
    "stormy ocean dramatic 4k"
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
    🎬 A/B/C-ROLL SEARCH: Search for 3 distinct video variations per query.
    Each query returns up to 3 different videos to enable variation cycling in the editor.
    
    Args:
        visual_queries (list): List of specific visual search queries (one per segment)
        fallback_topic (str): Generic topic keyword to use if specific search fails
    
    Returns:
        list of lists: Nested structure [[v1, v2, v3], [v1, v2, v3], ...] where each 
                       inner list contains up to 3 video info dicts for one segment
    """
    all_segment_variations = []
    
    for i, visual_query in enumerate(visual_queries):
        print(f"  🔍 Searching for segment {i} (3 variations): '{visual_query}'")
        
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
        
        # 🎬 A/B/C-ROLL: Collect TOP 3 distinct variations for this segment
        segment_variations = []
        if video_urls:
            # Take up to 3 distinct videos
            for variation_num, url in enumerate(video_urls[:3], start=1):
                video_info = {
                    "url": url,
                    "width": 1080,
                    "height": 1920,
                    "query": visual_query,
                    "segment_index": i,
                    "variation_number": variation_num,
                    "source": primary_source if video_urls else secondary_source
                }
                segment_variations.append(video_info)
            
            print(f"    ✓ Found {len(segment_variations)} variation(s) from {segment_variations[0]['source'].capitalize()}")
        else:
            print(f"    ✗ No videos found for '{visual_query}' on either source")
            # Add empty list as placeholder to maintain segment order
            segment_variations = []
        
        all_segment_variations.append(segment_variations)
        
        # Be nice to the APIs
        time.sleep(0.5)
    
    # Filter out empty lists (failed searches) but warn user
    valid_segments = [seg for seg in all_segment_variations if len(seg) > 0]
    total_videos = sum(len(seg) for seg in all_segment_variations)
    if len(valid_segments) < len(visual_queries):
        print(f"  ⚠️  Warning: Only found variations for {len(valid_segments)}/{len(visual_queries)} segments")
    print(f"  📊 Total: {total_videos} videos for {len(visual_queries)} segments")
    
    return all_segment_variations


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
    🎬 A/B/C-ROLL DOWNLOAD: Download 3 variations per segment for dynamic editing.
    Each segment gets up to 3 videos saved as segment_N_v1.mp4, segment_N_v2.mp4, segment_N_v3.mp4.
    
    Args:
        visual_queries (list): List of specific visual search queries (from script segments)
        fallback_topic (str): Generic topic keyword for fallback searches
    
    Returns:
        list of lists: [[path_v1, path_v2, path_v3], ...] nested structure where each
                       inner list contains paths to variations for one segment
    """
    print(f"\n📹 Downloading videos with A/B/C-roll variations")
    print(f"   Queries: {len(visual_queries)} segments")
    print(f"   Target: 3 variations per segment")
    print(f"   Fallback topic: {fallback_topic or 'None'}")
    
    # Search for videos using semantic queries (returns nested list)
    all_segment_variations = search_videos(visual_queries, fallback_topic=fallback_topic)
    
    if not all_segment_variations or all(len(seg) == 0 for seg in all_segment_variations):
        raise Exception("No videos found. Check your API keys and visual queries.")
    
    # Download all variations with segment-based naming
    downloaded_segment_paths = []
    total_downloaded = 0
    
    for segment_variations in all_segment_variations:
        if not segment_variations:
            # No variations found for this segment - add empty list as placeholder
            print(f"  ⚠️  Segment {len(downloaded_segment_paths)}: No variations available")
            downloaded_segment_paths.append([])
            continue
        
        segment_index = segment_variations[0]["segment_index"]
        variation_paths = []
        
        print(f"\n  📥 Segment {segment_index}: Downloading {len(segment_variations)} variation(s)")
        
        for video_info in segment_variations:
            variation_num = video_info["variation_number"]
            output_path = config.ASSETS_DIR / f"segment_{segment_index}_v{variation_num}.mp4"
            
            if download_video(video_info["url"], output_path):
                variation_paths.append(output_path)
                total_downloaded += 1
                print(f"    ✓ v{variation_num}: '{video_info['query'][:50]}...'")
            else:
                print(f"    ✗ v{variation_num}: Download failed")
        
        if not variation_paths:
            print(f"    ⚠️  Warning: All downloads failed for segment {segment_index}")
        
        downloaded_segment_paths.append(variation_paths)
    
    # Validate that we have at least some videos
    valid_segments = [seg for seg in downloaded_segment_paths if len(seg) > 0]
    if not valid_segments:
        raise Exception("Failed to download any videos")
    
    # Ensure at least variation 1 exists for each segment (critical for fallback)
    segments_with_v1 = sum(1 for seg in downloaded_segment_paths if len(seg) > 0)
    
    print(f"\n✓ Download Summary:")
    print(f"  Total videos: {total_downloaded}")
    print(f"  Segments with variations: {len(valid_segments)}/{len(visual_queries)}")
    print(f"  Segments with v1 (required): {segments_with_v1}/{len(visual_queries)}")
    
    return downloaded_segment_paths


if __name__ == "__main__":
    # Test the video downloader
    test_keywords = ["dark ocean", "foggy forest", "night sky"]
    videos = download_videos(test_keywords, num_videos=2)
    print(f"Downloaded videos: {videos}")
