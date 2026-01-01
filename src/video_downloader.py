"""YouTube-First Video Downloader with Pexels/Pixabay Fallback"""
import re
import requests
import time
import math
import random
import subprocess
import json
from pathlib import Path
try:
    import yt_dlp
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    print("⚠️  yt-dlp not installed. YouTube downloads will be skipped.")
import config

# Constants
CLIP_DURATION = 2.5  # Each video clip duration in seconds (matches video_editor.py)
MIN_VIDEO_DURATION = 15  # Minimum video duration in seconds to avoid looping with sped-up edits

# High-End Luxury aesthetic fallback keywords - Cars, Combat, AND Wealth/Empire
DARK_AESTHETIC_FALLBACKS = [
    "supercar night drive fast neon city",
    "shadow boxing silhouette night street rain",
    "counting money cash hands dark luxury",
    "private jet interior night luxury",
    "mafia boss suit dark lighting",
    "boxer training heavy bag sweat",
    "lamborghini driving night rain",
    "chess board game strategy dark",
    "black panther walking dark",
    "man in suit adjusting tie dark"
]

# 🚫 STRICT FILTER: Block generic nature and PASSIVE human actions
WEAK_VISUAL_TERMS = [
    # Nature (Strict Ban)
    "ocean", "sea", "water", "river", "lake", "beach", "sand",
    "forest", "tree", "wood", "nature", "flower", "garden",
    "grass", "field", "mountain", "hill", "cliff",
    # Note: 'sky' and 'cloud' are kept to prevent generic daytime sky shots, 
    # but 'rain' is removed to allow "Night City Rain" aesthetics.
    "sky", "cloud", "sun", "sunrise", "sunset",
    
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
    "shadow boxing night street silhouette",
    "muay thai training dark smoke",
    "calisthenics muscle up night park",
    "supercar night city drive neon",
    "drifting car night smoke tires",
    "mma fighter cage training dark",
    "boxer heavy bag workout sweat",
    "street workout pull ups night",
    "lamborghini tunnel run night fast",
    "kickboxing sparring dark cinematic"
]


def detect_category_from_query(query):
    """
    Detect YouTube category from visual query text.
    
    Args:
        query (str): Visual search query
    
    Returns:
        str or None: Category name (CARS/COMBAT/GYM/LUXURY) or None if no match
    """
    query_lower = query.lower()
    
    # Category detection rules (order matters - more specific first)
    if any(keyword in query_lower for keyword in [
        "car", "drive", "speed", "supercar", "ferrari", "lamborghini", 
        "porsche", "mclaren", "bugatti", "drift", "racing", "tunnel", "highway"
    ]):
        return "CARS"
    
    if any(keyword in query_lower for keyword in [
        "fight", "box", "punch", "combat", "mma", "kickbox", "spar", 
        "heavy bag", "cage", "ring", "fighter"
    ]):
        return "COMBAT"
    
    if any(keyword in query_lower for keyword in [
        "gym", "train", "muscle", "calisthenics", "workout", "pullup", 
        "pushup", "pull up", "push up", "bodyweight", "street workout"
    ]):
        return "GYM"
    
    if any(keyword in query_lower for keyword in [
        "money", "rich", "yacht", "villa", "jet", "luxury", "wealth", 
        "cash", "mansion", "penthouse", "private", "champagne"
    ]):
        return "LUXURY"
    
    return None


def download_youtube_clip(category, output_path, clip_duration=4):
    """
    Download a random 4-second clip from a YouTube compilation video.
    
    Args:
        category (str): Category name (CARS/COMBAT/GYM/LUXURY)
        output_path (Path): Where to save the clip
        clip_duration (int): Duration of clip to extract in seconds
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not YOUTUBE_AVAILABLE:
        return False
    
    # Check if category exists
    if category not in config.YOUTUBE_SOURCES:
        print(f"    ✗ Unknown category: {category}")
        return False
    
    urls = config.YOUTUBE_SOURCES[category]
    if not urls:
        print(f"    ✗ No URLs configured for category: {category}")
        return False
    
    # Try up to 3 random videos from the category
    attempted_urls = []
    for attempt in range(min(1, len(urls))):
        # Pick a random URL we haven't tried yet
        available_urls = [url for url in urls if url not in attempted_urls]
        if not available_urls:
            break
        
        video_url = random.choice(available_urls)
        attempted_urls.append(video_url)
        
        try:
            print(f"    🎬 Attempting YouTube clip from {category} (attempt {attempt + 1})")
            
            # Get video info without downloading
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                duration = info.get('duration', 0)
                
                if duration < 120:  # Video too short
                    print(f"    ✗ Video too short ({duration}s), need at least 2 minutes")
                    continue
                
                # Calculate random start time (avoid first/last 60s)
                safe_start = 60
                safe_end = duration - 60 - clip_duration
                
                if safe_end <= safe_start:
                    print(f"    ✗ Video not long enough for safe clip extraction")
                    continue
                
                start_time = random.randint(safe_start, safe_end)
                end_time = start_time + clip_duration
                
                print(f"    ⏱️  Video duration: {duration}s, extracting {start_time}s-{end_time}s")
                
                # Download only the specific segment
                download_opts = {
                    # Force single file download (no merging) to prevent ffmpeg errors on partials
                    'format': 'best[height<=1080][ext=mp4]/best[ext=mp4]',
                    'outtmpl': str(output_path),
                    'quiet': True,
                    'no_warnings': True,
                    # Ensure we get the exact time range
                    'download_ranges': yt_dlp.utils.download_range_func(None, [(start_time, end_time)]),
                    'force_keyframes_at_cuts': True,
                }
                
                with yt_dlp.YoutubeDL(download_opts) as ydl_download:
                    ydl_download.download([video_url])
                
                # Verify the file was created
                if output_path.exists() and output_path.stat().st_size > 0:
                    print(f"    ✓ YouTube clip downloaded successfully ({category})")
                    return True
                else:
                    print(f"    ✗ Download failed - file not created")
                    continue
                    
        except Exception as e:
            print(f"    ✗ YouTube download error: {str(e)[:100]}")
            continue
    
    print(f"    ✗ All YouTube download attempts failed for {category}")
    return False


def clean_and_map_query(query):
    """
    Simplifies LLM queries into high-performance stock footage tags.
    Removes ONLY technical fluff, KEEPS aesthetic keywords.
    """
    query = query.lower()
    
    # 1. REMOVE ONLY TECHNICAL FLUFF (Keep style keywords!)
    remove_words = [
        "4k", "8k", "ultra hd", "hd", "60fps", "detailed", "realistic", 
        "photorealistic", "shot", "angle", "view", "camera", "lens"
    ]
    for word in remove_words:
        query = query.replace(word, "")
    
    # 2. MAP TERMS TO HIGH-END TAGS
    replacements = {
        "ferrari": "supercar",
        "lamborghini": "supercar",
        "porsche": "sportscar",
        "mclaren": "supercar",
        "muay thai": "kickboxing",
        "mma": "mixed martial arts",
        "calisthenics": "street workout",
        "money": "money cash luxury",  # Force luxury context
        "jet": "private jet luxury",   # Force luxury context
        "chess": "chess dark"
    }
    
    for key, value in replacements.items():
        if key in query:
            query = query.replace(key, value)
            
    # Clean up spaces
    query = " ".join(query.split())
    return query


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
    
    for i, raw_query in enumerate(visual_queries):
        print(f"  🔍 Searching for segment {i}: '{raw_query}'")
        segment_variations = []  # <--- INITIALIZE HERE (Prevents crash if YouTube fails)
        
        # ✨ CLEAN THE QUERY FIRST
        visual_query = clean_and_map_query(raw_query)
        print(f"  🧹 Cleaned Query: '{raw_query}' -> '{visual_query}'")
        
        # 🚫 STRICT ACTION ENFORCEMENT (FIXED REGEX LOGIC)
        original_query = visual_query
        query_lower = visual_query.lower()
        
        # Check for weak terms using WHOLE WORD boundaries only
        # This prevents "training" from triggering "rain", or "skyline" from triggering "sky"
        has_weak_term = False
        for weak_term in WEAK_VISUAL_TERMS:
            # Escape the term just in case, and look for word boundaries
            if re.search(r'\b' + re.escape(weak_term) + r'\b', query_lower):
                has_weak_term = True
                print(f"    🔍 Found blocked term: '{weak_term}'")
                break
        
        # Check for stoic exceptions (also using regex for safety)
        has_stoic_exception = False
        for stoic_term in STOIC_EXCEPTIONS:
            if re.search(r'\b' + re.escape(stoic_term) + r'\b', query_lower):
                has_stoic_exception = True
                break
        
        # LOGIC: Block weak terms UNLESS it's a specific stoic object
        if has_weak_term and not has_stoic_exception:
            # Pick a random high-action fallback
            visual_query = random.choice(HIGH_ACTION_FALLBACKS)
            print(f"  🚫 Intercepted weak query '{original_query}'. Replaced with Action Fallback: '{visual_query}'")
        
        print(f"  🔍 Searching for segment {i} ({config.SCENE_VIDEO_VARIATIONS} variations): '{visual_query}'")
        
        # 🎬 YOUTUBE-FIRST STRATEGY: Try to download from YouTube before falling back to stock
        category = detect_category_from_query(visual_query)
        youtube_success_count = 0
        
        if category and YOUTUBE_AVAILABLE:
            print(f"    🎯 Detected category: {category}")
            # Try to fill variations with YouTube clips
            for variation_num in range(1, config.SCENE_VIDEO_VARIATIONS + 1):
                temp_output = config.ASSETS_DIR / f"segment_{i}_v{variation_num}_temp.mp4"
                if download_youtube_clip(category, temp_output):
                    # Create video_info dict for this YouTube clip
                    video_info = {
                        "url": "youtube",  # Special marker
                        "local_path": temp_output,
                        "width": 1080,
                        "height": 1920,
                        "query": visual_query,
                        "segment_index": i,
                        "variation_number": variation_num,
                        "source": "youtube"
                    }
                    segment_variations.append(video_info)
                    youtube_success_count += 1
            
            if youtube_success_count > 0:
                print(f"    ✓ YouTube provided {youtube_success_count}/{config.SCENE_VIDEO_VARIATIONS} variations")
        
        # If we have enough variations from YouTube, skip stock footage
        if len(segment_variations) >= config.SCENE_VIDEO_VARIATIONS:
            all_segment_variations.append(segment_variations)
            print(f"    ✓ Quota filled with YouTube clips ({len(segment_variations)} variations)")
            time.sleep(0.5)
            continue
        
        # 📦 STOCK FOOTAGE FALLBACK: Use Pexels/Pixabay if YouTube didn't provide enough
        remaining_needed = config.SCENE_VIDEO_VARIATIONS - len(segment_variations)
        print(f"    📦 Need {remaining_needed} more variation(s), falling back to stock footage...")
        
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
        # Note: segment_variations may already have YouTube clips, so we append stock footage
        if video_urls:
            # Calculate how many more variations we need and what numbers to use
            start_variation_num = len(segment_variations) + 1
            remaining_slots = config.SCENE_VIDEO_VARIATIONS - len(segment_variations)
            
            # Add stock footage to fill remaining variations
            for idx, url in enumerate(video_urls[:remaining_slots]):
                variation_num = start_variation_num + idx
                video_info = {
                    "url": url,
                    "width": 1080,
                    "height": 1920,
                    "query": visual_query,
                    "segment_index": i,
                    "variation_number": variation_num,
                    "source": primary_source if idx == 0 else secondary_source
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
    🎬 YOUTUBE-FIRST DOWNLOAD with Stock Footage Fallback: Download configurable variations 
    per segment for dynamic editing. Prioritizes YouTube clips, falls back to Pexels/Pixabay.
    Each segment gets up to config.SCENE_VIDEO_VARIATIONS videos saved as 
    segment_N_v1.mp4, segment_N_v2.mp4, ..., segment_N_vN.mp4.
    
    CRITICAL: Global deduplication ensures the same video URL is NEVER downloaded twice,
    even if different search queries return the same top results.
    
    Args:
        visual_queries (list): List of specific visual search queries (from script segments)
        fallback_topic (str): Generic topic keyword for fallback searches
    
    Returns:
        list of lists: [[path_v1, path_v2, ...], ...] nested structure where each
                       inner list contains paths to variations for one segment
    """
    print(f"\n📹 YouTube-First Download Strategy + Stock Footage Fallback")
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
            
            # Check if this is a YouTube clip that was already downloaded
            if video_info.get("source") == "youtube" and "local_path" in video_info:
                # Rename the temp file to the proper name
                temp_path = video_info["local_path"]
                if temp_path.exists():
                    # Move/rename temp file to final destination
                    import shutil
                    shutil.move(str(temp_path), str(output_path))
                    variation_paths.append(output_path)
                    total_downloaded += 1
                    print(f"    ✓ v{variation_num} (YouTube): '{video_info['query'][:50]}...'")
                else:
                    print(f"    ✗ v{variation_num}: YouTube temp file missing")
            # Otherwise download from stock footage URL
            elif download_video(video_info["url"], output_path):
                variation_paths.append(output_path)
                total_downloaded += 1
                print(f"    ✓ v{variation_num} (Stock): '{video_info['query'][:50]}...'")
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
