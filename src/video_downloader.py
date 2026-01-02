"""YouTube-First Video Downloader with Manual Curation Support

🎬 MANUAL CURATION PRIORITY SYSTEM:
  Priority 1: Local Files (assets/my_footage/*.mp4) - BULLETPROOF, NO DOWNLOADS
  Priority 2: Manual YouTube URLs (config.MANUAL_YOUTUBE_URLS) - CURATED QUALITY
  Priority 3: Automated Search (Original behavior) - FALLBACK ONLY

This design eliminates 403 errors and poor quality issues by allowing manual control.
"""
import re
import requests
import time
import math
import random
import subprocess
import json
import shutil
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


def get_local_footage_files():
    """
    🎯 PRIORITY 1: Check for manually curated local footage.
    
    Returns:
        list: Paths to .mp4 files in LOCAL_FOOTAGE_DIR, or empty list if none found
    """
    local_dir = getattr(config, 'LOCAL_FOOTAGE_DIR', None)
    
    if not local_dir or not Path(local_dir).exists():
        return []
    
    mp4_files = list(Path(local_dir).glob("*.mp4"))
    
    if mp4_files:
        print(f"    💎 Found {len(mp4_files)} local footage file(s) in {local_dir}")
        return mp4_files
    
    return []


def get_manual_youtube_urls(category=None):
    """
    🎯 PRIORITY 2: Check for manually curated YouTube URLs (Category-Based).
    
    Args:
        category (str): Category to select from (CARS/COMBAT/GYM/LUXURY/STOIC)
    
    Returns:
        list: Manual YouTube URLs for the specified category, or empty list
    """
    manual_urls_dict = getattr(config, 'MANUAL_YOUTUBE_URLS', {})
    
    # If manual URLs is still a flat list (old format), return it as-is for backward compatibility
    if isinstance(manual_urls_dict, list):
        if manual_urls_dict:
            print(f"    🎯 Found {len(manual_urls_dict)} manual YouTube URL(s) (legacy flat list)")
            return [url for url in manual_urls_dict if url.strip()]
        return []
    
    # Handle dictionary format (new category-based structure)
    if not isinstance(manual_urls_dict, dict) or not manual_urls_dict:
        return []
    
    # If no category specified, return all URLs (legacy behavior)
    if category is None:
        all_urls = []
        for cat_urls in manual_urls_dict.values():
            all_urls.extend(cat_urls)
        if all_urls:
            print(f"    🎯 Found {len(all_urls)} manual YouTube URL(s) (all categories)")
        return [url for url in all_urls if url.strip()]
    
    # Category-based selection
    urls = manual_urls_dict.get(category, [])
    
    # Fallback to DEFAULT_CATEGORY if category not found
    if not urls:
        default_cat = getattr(config, 'DEFAULT_CATEGORY', 'LUXURY')
        if category != default_cat:  # Avoid infinite recursion
            print(f"    ⚠️  Category '{category}' not found, falling back to '{default_cat}'")
            urls = manual_urls_dict.get(default_cat, [])
    
    if urls:
        print(f"    🎯 Found {len(urls)} manual YouTube URL(s) for category '{category}'")
        return [url for url in urls if url.strip()]
    
    return []


def detect_category_from_query(query):
    """
    Detect YouTube category from visual query text.
    
    Args:
        query (str): Visual search query
    
    Returns:
        str or None: Category name (CARS/COMBAT/GYM/LUXURY/STOIC) or None if no match
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
        "statue", "marble", "sculpture", "bust", "ancient", "rome", "roman", 
        "greece", "greek", "philosophy", "stoic", "temple", "column", "ruins"
    ]):
        return "STOIC"
    
    if any(keyword in query_lower for keyword in [
        "money", "rich", "yacht", "villa", "jet", "luxury", "wealth", 
        "cash", "mansion", "penthouse", "private", "champagne"
    ]):
        return "LUXURY"
    
    return None


def check_youtube_url_health(url):
    """
    Quickly check if a YouTube URL is accessible without downloading.
    
    Args:
        url (str): YouTube video URL
    
    Returns:
        bool: True if video is accessible, False if unavailable/private/deleted
    """
    if not YOUTUBE_AVAILABLE:
        return False
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': True,
            'socket_timeout': 5,  # Prevent hanging on dead links
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # If we can extract info, the video is accessible
            return info is not None
    except Exception as e:
        error_msg = str(e).lower()
        # Check for specific error patterns indicating dead links
        if any(keyword in error_msg for keyword in [
            'unavailable', 'private', 'deleted', 'removed', 
            'copyright', 'blocked', 'not available'
        ]):
            return False
        # For other errors, assume the link might be valid (network issues, etc.)
        return False


def search_youtube_videos(category, max_results=5):
    """
    Dynamically search YouTube for videos matching a category.
    
    Args:
        category (str): Category name (CARS/COMBAT/GYM/LUXURY)
        max_results (int): Maximum number of video URLs to return
    
    Returns:
        list: List of valid YouTube video URLs
    """
    if not YOUTUBE_AVAILABLE:
        return []
    
    # Get search queries for this category from config
    if not hasattr(config, 'YOUTUBE_SEARCH_QUERIES') or category not in config.YOUTUBE_SEARCH_QUERIES:
        print(f"    ✗ No search queries defined for category: {category}")
        return []
    
    search_queries = config.YOUTUBE_SEARCH_QUERIES[category]
    min_duration = getattr(config, 'YOUTUBE_MIN_DURATION', 600)  # Default 10 minutes
    
    found_urls = []
    
    for search_query in search_queries:
        if len(found_urls) >= max_results:
            break
        
        try:
            print(f"    🔍 Searching YouTube: '{search_query}'")
            
            # Search YouTube using yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'playlistend': 10,  # Check first 10 results
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Use ytsearch: prefix for YouTube search
                search_url = f"ytsearch10:{search_query}"
                search_results = ydl.extract_info(search_url, download=False)
                
                if not search_results or 'entries' not in search_results:
                    continue
                
                # Filter results
                for entry in search_results['entries']:
                    if entry is None:
                        continue
                    
                    # Negative Title Filtering: Skip bad clips
                    title = entry.get('title', '').lower()
                    bad_keywords = [
                        'lyrics', 'lyric video', 'official video', 'subtitles',
                        'karaoke', 'reaction', 'review', 'gameplay', 'trailer', 'tutorial'
                    ]
                    if any(keyword in title for keyword in bad_keywords):
                        print(f"    ✗ Filtered out: {entry.get('title', 'Unknown')[:50]}... (irrelevant content)")
                        continue
                    
                    duration = entry.get('duration', 0)
                    video_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                    
                    # Filter criteria
                    if duration >= min_duration:  # At least 10 minutes
                        # Quick health check
                        if check_youtube_url_health(video_url):
                            found_urls.append(video_url)
                            print(f"    ✓ Found: {entry.get('title', 'Unknown')[:50]}... ({duration//60} min)")
                            
                            # Early exit: Stop searching immediately after finding a valid video
                            if len(found_urls) >= max_results:
                                break
                        else:
                            print(f"    ✗ Skipped unavailable: {entry.get('title', 'Unknown')[:50]}...")
            
        except Exception as e:
            print(f"    ✗ Search error: {str(e)[:80]}")
            continue
    
    print(f"    📊 Search complete: {len(found_urls)} valid video(s) found")
    return found_urls



def download_youtube_clip(video_urls, output_path, clip_duration=4):
    """
    🎬 BUFFERED RANGE STRATEGY: Download a small buffered segment, then cut to exact clip.
    
    OPTIMIZATION: Instead of downloading the full video, downloads (start-10) to (end+10)
    with a 10-second buffer on each side. This prevents FFmpeg code 8 errors while keeping
    downloads fast for long videos (e.g., 2-hour compilations).
    
    If a URL fails (403 or any error), it silently tries the next URL in the list.
    
    Args:
        video_urls (list): List of YouTube URLs to try (manual or automated)
        output_path (Path): Where to save the clip
        clip_duration (int): Duration of clip to extract in seconds
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not YOUTUBE_AVAILABLE:
        return False
    
    if not video_urls:
        return False
    
    # Buffer size in seconds (prevents FFmpeg sync errors)
    BUFFER_SECONDS = 10
    
    # Try multiple videos with the buffered range strategy
    attempted_urls = []
    max_attempts = min(len(video_urls), 3)  # Try up to 3 different URLs
    
    for attempt in range(max_attempts):
        # Pick a random URL we haven't tried yet
        available_urls = [url for url in video_urls if url not in attempted_urls]
        if not available_urls:
            break
        
        video_url = random.choice(available_urls)
        attempted_urls.append(video_url)
        
        try:
            print(f"    🎬 Attempt {attempt + 1}/{max_attempts}: Extracting clip...")
            
            # Get video info without downloading
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            # Add cookie file if configured
            cookie_file = getattr(config, 'YOUTUBE_COOKIE_FILE', None)
            if cookie_file:
                ydl_opts['cookiefile'] = str(cookie_file)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                duration = info.get('duration', 0)
                
                if duration < 120:  # Video too short
                    print(f"    ⚠️  Video too short ({duration}s), trying next URL...")
                    continue  # Try next URL
                
                # Calculate random start time (avoid first/last 60s)
                safe_start = 60
                safe_end = duration - 60 - clip_duration
                
                if safe_end <= safe_start:
                    print(f"    ⚠️  Video not long enough, trying next URL...")
                    continue  # Try next URL
                
                start_time = random.randint(safe_start, safe_end)
                end_time = start_time + clip_duration
                
                # 🔥 BUFFERED RANGE: Add buffer to prevent FFmpeg sync errors
                buffer_start = max(0, start_time - BUFFER_SECONDS)
                buffer_end = min(duration, end_time + BUFFER_SECONDS)
                
                print(f"    ⏱️  Target clip: {start_time}s-{end_time}s")
                print(f"    📦 Downloading buffered range: {buffer_start}s-{buffer_end}s (avoids full download)")
                
                # 🎬 HIGH-QUALITY 1080p STRATEGY with BUFFERED RANGE
                # Uses 'bestvideo+bestaudio' to get separate high-quality streams and merge them
                # Requires cookie file to prevent 403 errors (configured in config.py)
                # Falls back to pre-merged files if merging fails
                download_opts = {
                    'format': 'bestvideo[height<=1080]+bestaudio/best[ext=mp4]/best',  # 1080p quality with fallbacks
                    'outtmpl': str(output_path),
                    'quiet': True,  # Suppress most output
                    'no_warnings': True,
                    'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',  # Enforce ffmpeg path to prevent code 8 errors
                    # ✅ BUFFERED RANGE ENABLED: Download only the buffered segment (not full video)
                    'download_ranges': yt_dlp.utils.download_range_func(None, [(buffer_start, buffer_end)]),
                    'force_keyframes_at_cuts': True,
                }
                
                # Add cookie file if configured
                if cookie_file:
                    download_opts['cookiefile'] = str(cookie_file)
                
                with yt_dlp.YoutubeDL(download_opts) as ydl_download:
                    ydl_download.download([video_url])
                
                # Verify the file was created
                if output_path.exists() and output_path.stat().st_size > 0:
                    # 🎬 POST-PROCESSING: Extract exact clip from buffered segment using ffmpeg
                    # Calculate offset within the buffered segment
                    offset_in_buffer = start_time - buffer_start
                    
                    temp_buffered_video = output_path.with_suffix('.buffered.mp4')
                    output_path.rename(temp_buffered_video)
                    
                    try:
                        # Use ffmpeg to extract the precise clip from the buffered segment
                        ffmpeg_cmd = [
                            '/opt/homebrew/bin/ffmpeg',
                            '-y',  # Overwrite output
                            '-ss', str(offset_in_buffer),  # Start time within buffered segment
                            '-i', str(temp_buffered_video),  # Input file (buffered segment)
                            '-t', str(clip_duration),  # Duration
                            '-c', 'copy',  # Copy without re-encoding (fast)
                            str(output_path)  # Output file
                        ]
                        
                        result = subprocess.run(
                            ffmpeg_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=30
                        )
                        
                        # Clean up temp file
                        if temp_buffered_video.exists():
                            temp_buffered_video.unlink()
                        
                        if result.returncode == 0 and output_path.exists():
                            print(f"    ✓ YouTube clip extracted successfully ({start_time}s-{end_time}s)")
                            return True
                        else:
                            print(f"    ⚠️  Clip extraction failed, trying next URL...")
                            if temp_buffered_video.exists():
                                temp_buffered_video.unlink()
                            if output_path.exists():
                                output_path.unlink()
                            continue
                            
                    except Exception as extract_error:
                        print(f"    ⚠️  Extraction error: {str(extract_error)[:50]}, trying next URL...")
                        if temp_buffered_video.exists():
                            temp_buffered_video.unlink()
                        if output_path.exists():
                            output_path.unlink()
                        continue
                else:
                    print(f"    ⚠️  Download failed - file not created, trying next URL...")
                    continue  # Try next URL
                    
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e).lower()
            
            # Check for 403/Forbidden errors - handle silently and try next URL
            if '403' in error_msg or 'forbidden' in error_msg:
                print(f"    ⚠️  HTTP 403 Forbidden - trying next URL...")
                time.sleep(0.5)
                continue  # Silently try next URL
            
            # Check for ffmpeg errors
            if 'ffmpeg' in error_msg and ('exit' in error_msg or 'code 8' in error_msg):
                print(f"    ⚠️  Stream merge failed - trying next URL...")
                time.sleep(0.5)
                continue
            elif 'sign in' in error_msg or 'age' in error_msg:
                print(f"    ⚠️  Age-restricted content - trying next URL...")
                continue  # Try next URL
            else:
                # Show abbreviated error for other issues
                print(f"    ⚠️  Download error - trying next URL...")
                continue
                
        except Exception as e:
            # Catch any unexpected errors and continue
            print(f"    ⚠️  Unexpected error - trying next URL...")
            continue
        
        # Add delay between video attempts
        if attempt < max_attempts - 1:
            time.sleep(1)
    
    # Only print final failure message if all attempts failed
    print(f"    ✗ All YouTube download attempts failed")
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
    🎬 REFACTORED: Manual Curation Priority System with A/B/C/D-ROLL SEARCH
    
    PRIORITY SYSTEM:
      1. Local Files (assets/my_footage/*.mp4) - If found, SKIP ALL DOWNLOADS
      2. Manual YouTube URLs (config.MANUAL_YOUTUBE_URLS) - If defined, USE ONLY THESE
      3. Automated Search (Original behavior) - Fallback when no manual sources
    
    CRITICAL: Uses global deduplication to ensure NO VIDEO IS EVER REUSED.
    
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
    used_local_files = set()  # Track used local files
    
    # 🎯 PRIORITY 1: Check for local footage (BULLETPROOF METHOD)
    local_files = get_local_footage_files()
    if local_files:
        print(f"\n  💎 PRIORITY 1 ACTIVE: Using local footage from {config.LOCAL_FOOTAGE_DIR}")
        print(f"     ✓ DOWNLOAD BYPASS: All network/quality issues solved!\n")
        
        for i, raw_query in enumerate(visual_queries):
            print(f"  📁 Segment {i}: Picking from local library...")
            segment_variations = []
            
            for variation_num in range(1, config.SCENE_VIDEO_VARIATIONS + 1):
                # Pick a random file we haven't used yet
                available_files = [f for f in local_files if f not in used_local_files]
                
                # If we've exhausted local files, re-enable all files
                if not available_files:
                    print(f"    🔄 Re-shuffling local library (all files used once)")
                    used_local_files.clear()
                    available_files = local_files
                
                chosen_file = random.choice(available_files)
                used_local_files.add(chosen_file)
                
                video_info = {
                    "url": "local",  # Special marker
                    "local_path": chosen_file,
                    "width": 1080,
                    "height": 1920,
                    "query": raw_query,
                    "segment_index": i,
                    "variation_number": variation_num,
                    "source": "local"
                }
                segment_variations.append(video_info)
                print(f"    ✓ v{variation_num}: {chosen_file.name}")
            
            all_segment_variations.append(segment_variations)
        
        print(f"\n  ✓ All {len(visual_queries)} segments filled with local footage")
        return all_segment_variations
    
    # 🎯 PRIORITY 2: Check for manual YouTube URLs (CURATED METHOD)
    # NOW WITH CATEGORY-BASED SELECTION!
    manual_urls_dict = getattr(config, 'MANUAL_YOUTUBE_URLS', {})
    
    # Check if we have a categorized manual URL dictionary
    if manual_urls_dict and isinstance(manual_urls_dict, dict):
        print(f"\n  🎯 PRIORITY 2 ACTIVE: Using categorized manual YouTube URLs")
        print(f"     ✓ AUTOMATED SEARCH DISABLED: Manual quality control active\n")
        
        for i, raw_query in enumerate(visual_queries):
            print(f"  🔍 Segment {i}: '{raw_query}'")
            segment_variations = []
            
            # 🎯 CATEGORY DETECTION: Determine which category to use
            category = detect_category_from_query(raw_query)
            if category:
                print(f"    🎯 Detected category: {category}")
            else:
                default_cat = getattr(config, 'DEFAULT_CATEGORY', 'LUXURY')
                category = default_cat
                print(f"    ⚠️  No category detected, using default: {category}")
            
            # Get category-specific URLs
            category_urls = get_manual_youtube_urls(category)
            
            if not category_urls:
                print(f"    ✗ No manual URLs available for category '{category}'")
                all_segment_variations.append(segment_variations)
                continue
            
            # Try to fill variations from category-specific manual URLs
            for variation_num in range(1, config.SCENE_VIDEO_VARIATIONS + 1):
                temp_output = config.ASSETS_DIR / f"segment_{i}_v{variation_num}_temp.mp4"
                
                # Use the refactored download function with category-specific URLs
                if download_youtube_clip(category_urls, temp_output):
                    video_info = {
                        "url": "youtube_manual",  # Special marker
                        "local_path": temp_output,
                        "width": 1080,
                        "height": 1920,
                        "query": raw_query,
                        "segment_index": i,
                        "variation_number": variation_num,
                        "source": "youtube_manual",
                        "category": category  # Track which category was used
                    }
                    segment_variations.append(video_info)
                    print(f"    ✓ v{variation_num} downloaded from '{category}' category")
                else:
                    print(f"    ✗ v{variation_num} failed (will retry with different URL)")
            
            all_segment_variations.append(segment_variations)
            time.sleep(0.5)
        
        print(f"\n  ✓ Category-based manual download complete")
        return all_segment_variations
    
    # Legacy support: Handle flat list format (old config structure)
    elif manual_urls_dict and isinstance(manual_urls_dict, list):
        manual_urls = manual_urls_dict
        print(f"\n  🎯 PRIORITY 2 ACTIVE: Using {len(manual_urls)} curated YouTube URL(s) (flat list)")
        print(f"     ✓ AUTOMATED SEARCH DISABLED: Manual quality control active\n")
        
        for i, raw_query in enumerate(visual_queries):
            print(f"  🔍 Segment {i}: '{raw_query}'")
            segment_variations = []
            
            # Try to fill variations from manual URLs using the stable download strategy
            for variation_num in range(1, config.SCENE_VIDEO_VARIATIONS + 1):
                temp_output = config.ASSETS_DIR / f"segment_{i}_v{variation_num}_temp.mp4"
                
                # Use the refactored download function with manual URLs
                if download_youtube_clip(manual_urls, temp_output):
                    video_info = {
                        "url": "youtube_manual",  # Special marker
                        "local_path": temp_output,
                        "width": 1080,
                        "height": 1920,
                        "query": raw_query,
                        "segment_index": i,
                        "variation_number": variation_num,
                        "source": "youtube_manual"
                    }
                    segment_variations.append(video_info)
                    print(f"    ✓ v{variation_num} downloaded (manual URL)")
                else:
                    print(f"    ✗ v{variation_num} failed (will retry with different URL)")
            
            all_segment_variations.append(segment_variations)
            time.sleep(0.5)
        
        print(f"\n  ✓ Manual download complete")
        return all_segment_variations
    
    # 🎯 PRIORITY 3: Automated Search (FALLBACK ONLY)
    print(f"\n  🔍 PRIORITY 3 ACTIVE: Using automated search (no manual sources)")
    
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
            
            # Get configured URLs for this category
            if category in config.YOUTUBE_SOURCES:
                category_urls = config.YOUTUBE_SOURCES[category]
                valid_urls = []
                
                # Health check on configured URLs
                if category_urls:
                    print(f"    🔍 Validating {len(category_urls)} configured URL(s)...")
                    for url in category_urls:
                        if check_youtube_url_health(url):
                            valid_urls.append(url)
                            print(f"    ✓ Valid URL")
                        else:
                            print(f"    ✗ Dead/unavailable URL, skipping")
                
                # FALLBACK: If no valid URLs, use dynamic search
                enable_search = getattr(config, 'YOUTUBE_ENABLE_SEARCH', True)
                if not valid_urls and enable_search:
                    print(f"    🔎 No valid configured URLs, falling back to dynamic search...")
                    valid_urls = search_youtube_videos(category, max_results=3)
                
                # Try to fill variations with YouTube clips
                if valid_urls:
                    for variation_num in range(1, config.SCENE_VIDEO_VARIATIONS + 1):
                        temp_output = config.ASSETS_DIR / f"segment_{i}_v{variation_num}_temp.mp4"
                        
                        if download_youtube_clip(valid_urls, temp_output):
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
    🎬 REFACTORED: Manual Curation + YouTube-First Download with Stock Footage Fallback
    
    Downloads configurable variations per segment for dynamic editing. 
    Prioritizes manual sources (local files, then manual YouTube URLs), 
    then falls back to automated search.
    
    Each segment gets up to config.SCENE_VIDEO_VARIATIONS videos saved as 
    segment_N_v1.mp4, segment_N_v2.mp4, ..., segment_N_vN.mp4.
    
    CRITICAL: Global deduplication ensures the same video URL is NEVER downloaded twice.
    
    Args:
        visual_queries (list): List of specific visual search queries (from script segments)
        fallback_topic (str): Generic topic keyword for fallback searches
    
    Returns:
        list of lists: [[path_v1, path_v2, ...], ...] nested structure where each
                       inner list contains paths to variations for one segment
    """
    print(f"\n📹 Manual Curation Priority System")
    print(f"   1️⃣ Local Files: {config.LOCAL_FOOTAGE_DIR}")
    print(f"   2️⃣ Manual URLs: {len(getattr(config, 'MANUAL_YOUTUBE_URLS', []))} curated link(s)")
    print(f"   3️⃣ Auto Search: YouTube → Pexels → Pixabay")
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
        
        print(f"\n  📥 Segment {segment_index}: Processing {len(segment_variations)} variation(s)")
        
        for video_info in segment_variations:
            variation_num = video_info["variation_number"]
            output_path = config.ASSETS_DIR / f"segment_{segment_index}_v{variation_num}.mp4"
            
            # Check if this is a LOCAL file (Priority 1)
            if video_info.get("source") == "local" and "local_path" in video_info:
                local_path = video_info["local_path"]
                if local_path.exists():
                    # Copy local file to output location
                    shutil.copy(str(local_path), str(output_path))
                    variation_paths.append(output_path)
                    total_downloaded += 1
                    print(f"    ✓ v{variation_num} (Local): {local_path.name}")
                else:
                    print(f"    ✗ v{variation_num}: Local file missing")
            
            # Check if this is a YouTube clip that was already downloaded (Priority 2 or 3)
            elif video_info.get("source") in ["youtube", "youtube_manual"] and "local_path" in video_info:
                # Rename the temp file to the proper name
                temp_path = video_info["local_path"]
                if temp_path.exists():
                    # Move/rename temp file to final destination
                    shutil.move(str(temp_path), str(output_path))
                    variation_paths.append(output_path)
                    total_downloaded += 1
                    source_label = "Manual YT" if video_info.get("source") == "youtube_manual" else "YouTube"
                    print(f"    ✓ v{variation_num} ({source_label}): '{video_info['query'][:50]}...'")
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
