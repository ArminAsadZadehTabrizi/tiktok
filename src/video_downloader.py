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

# High-Adrenaline Action aesthetic fallback keywords for when specific searches fail
DARK_AESTHETIC_FALLBACKS = [
    "formula 1 racing car dark cinematic",
    "boxer training heavy bag sweat",
    "supercar night drive fast neon",
    "sprinter running fast track night",
    "gym bodybuilder lifting heavy dark",
    "drifting car smoke cinematic",
    "mma fighter training cage",
    "lamborghini driving night rain",
    "lion running slow motion dark",  # Kept one animal, but active
    "man sprinting city night"
]

# 🚫 STRICT FILTER: Block generic nature, weather, and PASSIVE human actions
WEAK_VISUAL_TERMS = [
    # Nature & Weather (Roots)
    "ocean", "sea", "water", "river", "lake", "beach", "sand",
    "forest", "tree", "wood", "nature", "flower", "garden",
    "sky", "cloud", "sun", "rain", "storm", "fog", "mist", "weather",
    "grass", "field", "mountain", "landscape", "hill", "cliff",
    
    # Passive/Boring Human Actions
    "sitting", "standing", "thinking", "walking alone", "looking", 
    "depressed", "sad", "lonely", "chair", "bench", "bed", "sleeping",
    "room", "wall", "window", "reading", "writing", "paper"
]

# ✅ ALLOWED STOIC CONCEPTS (Removed weather terms)
STOIC_EXCEPTIONS = [
    "statue", "marble", "sculpture", "bust",
    "chess", "king", "queen", "rook",
    "lion", "wolf", "eagle", "tiger", "panther",
    "hourglass", "skull" 
    # REMOVED: storm, rain, thunder (too generic)
]

HIGH_ACTION_FALLBACKS = [
    "luxury car night city drive",
    "boxer training dark gym sweat",
    "supercar accelerating flame",
    "money counting machine close up",
    "man in suit walking night rear view",
    "gym bodybuilder lifting heavy",
    "mma fighting cage slow motion",
    "neon city cyber aesthetics",
    "private jet interior luxury",
    "lamborghini driving fast"
]


def search_pexels(query, orientation="portrait", seen_video_urls=None):
    """
    Search for videos on Pexels with global deduplication.
    
    Args:
        query (str): Search query
        orientation (str): Video orientation (portrait/landscape)
        seen_video_urls (set): Set of already-used video URLs to avoid duplicates
    
    Returns:
        list: Video URLs found (unique only)
    """
    if seen_video_urls is None:
        seen_video_urls = set()
    
    headers = {"Authorization": config.PEXELS_API_KEY}
    params = {
        "query": query,
        "orientation": orientation,
        "size": config.PEXELS_SIZE,
        "per_page": 10  # Increased to account for duplicate filtering
    }
    
    try:
        response = requests.get(config.PEXELS_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        videos = data.get("videos", [])
        
        video_urls = []
        for video in videos:
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
                video_url = vertical_files[0]["link"]
                
                # 🔒 GLOBAL DEDUPLICATION: Skip if already used
                if video_url in seen_video_urls:
                    print(f"    ⊗ Duplicate detected, skipping")
                    continue
                
                video_urls.append(video_url)
                seen_video_urls.add(video_url)
                print(f"    ✓ Video duration: {duration}s (passed filter)")
                
                # Stop when we have enough unique videos
                if len(video_urls) >= config.SCENE_VIDEO_VARIATIONS:
                    break
        
        return video_urls
    
    except Exception as e:
        print(f"    ✗ Pexels error: {e}")
        return []


def search_pixabay(query, orientation="portrait", seen_video_urls=None):
    """
    Search for videos on Pixabay with global deduplication.
    
    Args:
        query (str): Search query
        orientation (str): Video orientation (vertical/horizontal)
        seen_video_urls (set): Set of already-used video URLs to avoid duplicates
    
    Returns:
        list: Video URLs found (unique only)
    """
    if seen_video_urls is None:
        seen_video_urls = set()
    
    # Map orientation to Pixabay format
    pixabay_orientation = "vertical" if orientation == "portrait" else "horizontal"
    
    params = {
        "key": config.PIXABAY_API_KEY,
        "q": query,
        "video_type": "film",
        "orientation": pixabay_orientation,
        "per_page": 10  # Increased to account for duplicate filtering
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
            video_url = None
            
            # Prefer large or medium quality
            if "large" in videos:
                video_url = videos["large"]["url"]
            elif "medium" in videos:
                video_url = videos["medium"]["url"]
            elif "small" in videos:
                video_url = videos["small"]["url"]
            
            if video_url:
                # 🔒 GLOBAL DEDUPLICATION: Skip if already used
                if video_url in seen_video_urls:
                    print(f"    ⊗ Duplicate detected, skipping")
                    continue
                
                video_urls.append(video_url)
                seen_video_urls.add(video_url)
                print(f"    ✓ Video duration: {duration}s (passed filter)")
                
                # Stop when we have enough unique videos
                if len(video_urls) >= config.SCENE_VIDEO_VARIATIONS:
                    break
        
        return video_urls
    
    except Exception as e:
        print(f"    ✗ Pixabay error: {e}")
        return []


def search_videos(visual_queries, fallback_topic=None):
    """
    🎬 A/B/C/D-ROLL SEARCH with GLOBAL DEDUPLICATION: Search for configurable video 
    variations per query. Each query returns up to config.SCENE_VIDEO_VARIATIONS different 
    videos to enable variation cycling in the editor.
    
    CRITICAL: Uses a global seen_video_urls set to ensure NO VIDEO IS EVER REUSED across 
    all segments, even if different queries return the same top results.
    
    Args:
        visual_queries (list): List of specific visual search queries (one per segment)
        fallback_topic (str): Generic topic keyword to use if specific search fails
    
    Returns:
        list of lists: Nested structure [[v1, v2, v3, v4], [v1, v2, v3, v4], ...] where each 
                       inner list contains up to config.SCENE_VIDEO_VARIATIONS video info dicts
    """
    all_segment_variations = []
    
    # 🔒 GLOBAL DEDUPLICATION: Track used URLs across ALL segments
    seen_video_urls = set()
    
    for i, visual_query in enumerate(visual_queries):
        # 🚫 STRICT ACTION ENFORCEMENT
        original_query = visual_query
        query_lower = visual_query.lower()
        
        # Check if query contains any weak term as a SUBSTRING
        # (e.g., "clouds" contains "cloud", "trees" contains "tree")
        has_weak_term = any(weak_term in query_lower for weak_term in WEAK_VISUAL_TERMS)
        
        # Check for stoic exceptions
        has_stoic_exception = any(stoic_term in query_lower for stoic_term in STOIC_EXCEPTIONS)
        
        # LOGIC: Block weak terms UNLESS it's a specific stoic object
        if has_weak_term and not has_stoic_exception:
            # Pick a random high-action fallback
            visual_query = random.choice(HIGH_ACTION_FALLBACKS)
            print(f"  🚫 Intercepted weak query '{original_query}'. Replaced with Action Fallback: '{visual_query}'")
        
        print(f"  🔍 Searching for segment {i} ({config.SCENE_VIDEO_VARIATIONS} variations): '{visual_query}'")
        
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
            video_urls = search_pixabay(visual_query, seen_video_urls=seen_video_urls)
        else:
            print(f"    → Pexels: '{visual_query}'")
            video_urls = search_pexels(visual_query, seen_video_urls=seen_video_urls)
        
        # Fallback to secondary source if primary returns nothing or not enough
        if len(video_urls) < config.SCENE_VIDEO_VARIATIONS:
            print(f"    ↪️  Trying {secondary_source.capitalize()} for more variations...")
            if secondary_source == "pixabay":
                additional = search_pixabay(visual_query, seen_video_urls=seen_video_urls)
            else:
                additional = search_pexels(visual_query, seen_video_urls=seen_video_urls)
            video_urls.extend(additional)
        
        # FALLBACK TIER 3 (Now prioritized): Aggressively try multiple dark aesthetic keywords until quota is filled
        fallback_attempts = 0
        while len(video_urls) < config.SCENE_VIDEO_VARIATIONS and fallback_attempts < len(DARK_AESTHETIC_FALLBACKS):
            dark_keyword = DARK_AESTHETIC_FALLBACKS[fallback_attempts]
            print(f"    🎬 Using aesthetic fallback #{fallback_attempts + 1}: '{dark_keyword}'")
            
            if primary_source == "pixabay":
                additional = search_pixabay(dark_keyword, seen_video_urls=seen_video_urls)
            else:
                additional = search_pexels(dark_keyword, seen_video_urls=seen_video_urls)
            
            video_urls.extend(additional)
            fallback_attempts += 1
            
            if len(video_urls) >= config.SCENE_VIDEO_VARIATIONS:
                print(f"    ✓ Quota filled with unique aesthetic footage")
                break
        
        # FALLBACK TIER 4 (Last resort): If aesthetic fallbacks fail, try generic topic keyword
        if len(video_urls) < config.SCENE_VIDEO_VARIATIONS and fallback_topic:
            print(f"    ⚠️  Need more variations, using generic topic fallback: '{fallback_topic}'")
            if primary_source == "pixabay":
                additional = search_pixabay(fallback_topic, seen_video_urls=seen_video_urls)
            else:
                additional = search_pexels(fallback_topic, seen_video_urls=seen_video_urls)
            video_urls.extend(additional)
        
        # 🎬 A/B/C/D-ROLL: Collect TOP variations for this segment (up to config limit)
        segment_variations = []
        if video_urls:
            # Take up to SCENE_VIDEO_VARIATIONS distinct videos
            for variation_num, url in enumerate(video_urls[:config.SCENE_VIDEO_VARIATIONS], start=1):
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
            
            print(f"    ✓ Found {len(segment_variations)} unique variation(s) (Global unique: {len(seen_video_urls)})")
        else:
            print(f"    ✗ No unique videos found for '{visual_query}' - all sources exhausted")
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
    print(f"  📊 Total: {total_videos} unique videos for {len(visual_queries)} segments")
    print(f"  🔒 Global deduplication: {len(seen_video_urls)} unique URLs tracked")
    
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
    🎬 A/B/C/D-ROLL DOWNLOAD with GLOBAL DEDUPLICATION: Download configurable variations 
    per segment for dynamic editing. Each segment gets up to config.SCENE_VIDEO_VARIATIONS 
    videos saved as segment_N_v1.mp4, segment_N_v2.mp4, ..., segment_N_vN.mp4.
    
    CRITICAL: Global deduplication ensures the same video URL is NEVER downloaded twice,
    even if different search queries return the same top results.
    
    Args:
        visual_queries (list): List of specific visual search queries (from script segments)
        fallback_topic (str): Generic topic keyword for fallback searches
    
    Returns:
        list of lists: [[path_v1, path_v2, ...], ...] nested structure where each
                       inner list contains paths to variations for one segment
    """
    print(f"\n📹 Downloading videos with A/B/C/D-roll variations + Global Deduplication")
    print(f"   Queries: {len(visual_queries)} segments")
    print(f"   Target: {config.SCENE_VIDEO_VARIATIONS} variations per segment")
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
