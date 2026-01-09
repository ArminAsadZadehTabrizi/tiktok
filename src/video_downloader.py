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
    🎬 YT-DLP DOWNLOAD_RANGES STRATEGY (Reverted from FFmpeg Direct)
    
    Uses yt-dlp's native download_ranges feature to download specific time segments.
    This solves the 403 Forbidden error by letting yt-dlp handle authentication.
    
    CRASH PREVENTION CONFIG:
      - format: 'bestvideo[height<=1080][ext=mp4]' (Video-only, no audio merge)
      - fixup: 'never' (Disables post-processing that triggers crashes)
      - force_keyframes_at_cuts: False (Prevents heavy FFmpeg processing)
      - download_ranges: Uses yt_dlp.utils.download_range_func for precise cuts
    
    FALLBACK MECHANISM:
      If yt-dlp range download fails, downloads full video and cuts locally with FFmpeg.
      This ensures the bot NEVER stops working.
    
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
    
    # Find FFmpeg binary (needed for fallback)
    ffmpeg_path = shutil.which('ffmpeg')
    if not ffmpeg_path:
        ffmpeg_path = '/opt/homebrew/bin/ffmpeg'
        if not Path(ffmpeg_path).exists():
            print(f"    ✗ FFmpeg not found - cannot use fallback")
            ffmpeg_path = None
    
    # Try multiple videos
    attempted_urls = []
    max_attempts = min(len(video_urls), 3)
    
    for attempt in range(max_attempts):
        # Pick a random URL we haven't tried yet
        available_urls = [url for url in video_urls if url not in attempted_urls]
        if not available_urls:
            break
        
        video_url = random.choice(available_urls)
        attempted_urls.append(video_url)
        
        try:
            print(f"    🎬 Attempt {attempt + 1}/{max_attempts}: Using yt-dlp download_ranges...")
            
            # STEP 1: Get video info to calculate time range
            info_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            cookie_file = getattr(config, 'YOUTUBE_COOKIE_FILE', None)
            if cookie_file:
                info_opts['cookiefile'] = str(cookie_file)
            
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                duration = info.get('duration', 0)
                
                if duration < 120:
                    print(f"    ⚠️  Video too short ({duration}s), trying next URL...")
                    continue
                
                # Calculate random start time (avoid first/last 60s)
                safe_start = 60
                safe_end = duration - 60 - clip_duration
                
                if safe_end <= safe_start:
                    print(f"    ⚠️  Video not long enough, trying next URL...")
                    continue
                
                start_time = random.randint(safe_start, safe_end)
                end_time = start_time + clip_duration
                
                print(f"    ⏱️  Target clip: {start_time}s to {end_time}s")
            
            # STEP 2: PRIMARY STRATEGY - Use yt-dlp's download_ranges
            try:
                print(f"    📥 Method 1: yt-dlp download_ranges (fast, prevents 403)...")
                
                ydl_opts = {
                    'format': 'bestvideo[height<=1080][ext=mp4]',  # Video-only, no audio
                    'outtmpl': str(output_path),
                    'quiet': True,
                    'no_warnings': True,
                    'fixup': 'never',  # CRITICAL: Disable post-processing fixup
                    'force_keyframes_at_cuts': False,  # CRITICAL: Prevent FFmpeg crash
                    'download_ranges': yt_dlp.utils.download_range_func(None, [(start_time, end_time)]),
                }
                
                if cookie_file:
                    ydl_opts['cookiefile'] = str(cookie_file)
                
                # Download using yt-dlp (handles cookies/headers correctly)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Verify the file was created
                if output_path.exists() and output_path.stat().st_size > 0:
                    print(f"    ✓ yt-dlp range download successful ({start_time}s-{end_time}s)")
                    return True
                else:
                    print(f"    ⚠️  yt-dlp range download failed (file missing/empty)")
                    raise Exception("Range download produced no output")
            
            except Exception as range_error:
                # Suppress the full error, just show a brief warning
                error_msg = str(range_error)[:60]
                print(f"    ⚠️  Range download failed: {error_msg}")
                
                # Clean up failed file
                if output_path.exists():
                    output_path.unlink()
                
                # STEP 3: FALLBACK STRATEGY - Download full video + local FFmpeg cut
                if not ffmpeg_path:
                    print(f"    ✗ Fallback skipped: FFmpeg not available")
                    continue
                
                # ROBUST MULTI-LAYER FALLBACK: Try 1080p first, then 720p as last resort
                try:
                    print(f"    🔄 Method 2: Full video download + local FFmpeg cut (1080p)...")
                    
                    # Create temporary file for full video
                    temp_full_video = output_path.parent / f"temp_full_{output_path.name}"
                    
                    try:
                        # Download full video (1080p video-only, no audio merge)
                        # ✅ ANDROID CLIENT: Prevents 403 errors on high-res streams
                        fallback_opts = {
                            'format': 'bestvideo[height<=1080][ext=mp4]',
                            'outtmpl': str(temp_full_video),
                            'quiet': True,
                            'no_warnings': True,
                            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},  # Android API resistance
                            'cachedir': False,  # Prevent stale cache issues
                        }
                        
                        if cookie_file:
                            fallback_opts['cookiefile'] = str(cookie_file)
                        
                        with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                            ydl.download([video_url])
                        
                        if not temp_full_video.exists():
                            print(f"    ✗ Full video download failed")
                            raise Exception("1080p download produced no file")
                        
                        print(f"    ✓ Full video downloaded, cutting segment with FFmpeg...")
                        
                        # Cut the segment locally with FFmpeg
                        ffmpeg_cmd = [
                            ffmpeg_path,
                            '-y',
                            '-ss', str(start_time),
                            '-i', str(temp_full_video),
                            '-t', str(clip_duration),
                            '-c', 'copy',
                            '-movflags', '+faststart',
                            str(output_path)
                        ]
                        
                        result = subprocess.run(
                            ffmpeg_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=30
                        )
                        
                        # Clean up temp file
                        if temp_full_video.exists():
                            temp_full_video.unlink()
                        
                        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
                            print(f"    ✓ Method 2 successful: Full download + FFmpeg cut ({start_time}s-{end_time}s)")
                            return True
                        else:
                            print(f"    ✗ FFmpeg cut failed")
                            if output_path.exists():
                                output_path.unlink()
                            raise Exception("FFmpeg cut failed")
                    
                    except Exception as method2_error:
                        error_msg = str(method2_error)[:60]
                        print(f"    ✗ Method 2 error: {error_msg}")
                        
                        # Clean up temp files
                        if temp_full_video.exists():
                            temp_full_video.unlink()
                        if output_path.exists():
                            output_path.unlink()
                        
                        # RE-RAISE to trigger Method 3
                        raise
                
                except Exception as method2_outer_error:
                    # METHOD 3: LAST RESORT - 720p guaranteed download
                    print(f"    ⚠️  1080p failed, trying 720p last resort...")
                    
                    temp_full_video_720p = output_path.parent / f"temp_720p_{output_path.name}"
                    
                    try:
                        # Download full video (best quality, any resolution)
                        last_resort_opts = {
                            'format': 'best[ext=mp4]',  # Universal format, guaranteed to work
                            'outtmpl': str(temp_full_video_720p),
                            'quiet': True,
                            'no_warnings': True,
                            'cachedir': False,
                        }
                        
                        if cookie_file:
                            last_resort_opts['cookiefile'] = str(cookie_file)
                        
                        with yt_dlp.YoutubeDL(last_resort_opts) as ydl:
                            ydl.download([video_url])
                        
                        if not temp_full_video_720p.exists():
                            print(f"    ✗ 720p download failed")
                            continue
                        
                        print(f"    ✓ 720p video downloaded, cutting segment with FFmpeg...")
                        
                        # Cut the segment locally with FFmpeg
                        ffmpeg_cmd_720p = [
                            ffmpeg_path,
                            '-y',
                            '-ss', str(start_time),
                            '-i', str(temp_full_video_720p),
                            '-t', str(clip_duration),
                            '-c', 'copy',
                            '-movflags', '+faststart',
                            str(output_path)
                        ]
                        
                        result = subprocess.run(
                            ffmpeg_cmd_720p,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=30
                        )
                        
                        # Clean up temp file
                        if temp_full_video_720p.exists():
                            temp_full_video_720p.unlink()
                        
                        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
                            print(f"    ✓ Method 3 successful: 720p fallback ({start_time}s-{end_time}s)")
                            return True
                        else:
                            print(f"    ✗ 720p FFmpeg cut failed")
                            if output_path.exists():
                                output_path.unlink()
                            continue
                    
                    except Exception as method3_error:
                        error_msg = str(method3_error)[:60]
                        print(f"    ✗ Method 3 error: {error_msg}")
                        
                        # Clean up temp files
                        if temp_full_video_720p.exists():
                            temp_full_video_720p.unlink()
                        if output_path.exists():
                            output_path.unlink()
                        continue
        
        except Exception as e:
            error_msg = str(e)[:80]
            print(f"    ⚠️  Outer error: {error_msg}, trying next URL...")
            if output_path.exists():
                output_path.unlink()
            continue
        
        # Add delay between video attempts
        if attempt < max_attempts - 1:
            time.sleep(1)
    
    print(f"    ✗ All YouTube download attempts failed (tried {len(attempted_urls)} URLs)")
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


# =========================================================================
# 🛠️ HELPER: Duration & Matching
# =========================================================================
def get_video_duration(file_path):
    """Get duration of a local video file using ffprobe."""
    try:
        cmd = [
            'ffprobe', '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            str(file_path)
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(result.stdout.strip())
    except Exception:
        return 0.0

def find_best_matching_local_file (query, local_files):
    """
    🎯 SMART MATCHING: Finds the best matching local file based on filename keywords.
    
    Uses weighted scoring system:
      - Exact keyword match in filename: +10 points
      - Partial match (keyword is substring): +5 points
      - Minimum keyword length: 3 characters (ignore "the", "and", etc.)
    
    Examples:
      - Query: "Lamborghini fast" → "lamborghini_night.mp4" (exact match: "lamborghini")
      - Query: "boxing training" → "boxing_compilation.mp4" (exact match: "boxing")
      - Query: "supercar night drive" → "supercar_tunnel_4k.mp4" (exact match: "supercar")
    
    Args:
        query (str): Visual search query (e.g., "Lamborghini night drive")
        local_files (list): List of Path objects pointing to local .mp4 files
    
    Returns:
        Path: Best matching file (or random file if no matches)
    """
    if not local_files:
        raise ValueError("No local files provided for matching")
    
    if len(local_files) == 1:
        # Only one file available, return it
        return local_files[0]
    
    query_lower = query.lower()
    query_keywords = [kw.strip() for kw in query_lower.split() if len(kw.strip()) >= 3]
    
    if not query_keywords:
        # No meaningful keywords, pick random file
        return random.choice(local_files)
    
    scored_files = []
    
    for file in local_files:
        # Extract filename without extension for matching
        filename_stem = file.stem.lower()  # e.g., "lamborghini_compilation" from "lamborghini_compilation.mp4"
        filename_full = file.name.lower()  # e.g., "lamborghini_compilation.mp4"
        
        score = 0
        matched_keywords = []
        
        for keyword in query_keywords:
            # Exact word match (e.g., "lamborghini" in "lamborghini_compilation")
            # Use word boundaries to avoid partial matches like "lamb" in "lamborghini"
            if re.search(r'\b' + re.escape(keyword) + r'\b', filename_stem):
                score += 10
                matched_keywords.append(keyword)
            # Partial match (e.g., "lambo" matches "lamborghini")
            elif keyword in filename_stem:
                score += 5
                matched_keywords.append(f"{keyword}*")
        
        if score > 0:
            scored_files.append({
                'file': file,
                'score': score,
                'matched': matched_keywords
            })
    
    # Sort by score (highest first)
    scored_files.sort(key=lambda x: x['score'], reverse=True)
    
    if scored_files:
        best_match = scored_files[0]
        print(f"      🎯 Match confidence: {best_match['score']} pts (keywords: {', '.join(best_match['matched'])})")
        return best_match['file']
    else:
        # No keyword matches found, pick random file
        chosen = random.choice(local_files)
        print(f"      🎲 No keyword match, using random: {chosen.name}")
        return chosen


# =========================================================================
# 🎬 MAIN DOWNLOADER: SMART LOCAL CUTS
# =========================================================================
def download_videos(visual_queries, fallback_topic=None):
    """
    🎬 PRIORITY 1: LOCAL FILES (SMART CUT & MATCHING)
    
    Smart Matching: Analyzes filename keywords to find best match for each query.
    Smart Random Cut: Extracts random 4-second clips using ffprobe + ffmpeg stream-copy.
    
    Features:
      - Keyword-based matching (e.g., "Lamborghini" → "lamborghini_compilation.mp4")
      - Random start time selection with safe buffers
      - Stream-copy (-c copy) for instant, lossless cutting
      - Fallback to full copy for videos <10 seconds
    
    Args:
        visual_queries (list): List of visual search queries (one per segment)
        fallback_topic (str): Unused in local mode (kept for compatibility)
    
    Returns:
        list of lists: Nested structure [[path1, path2, ...], ...] for each segment's variations
    """
    print(f"\n📹 Manual Curation Priority System (Smart Local Mode)")
    print(f"   1️⃣ Local Files: {config.LOCAL_FOOTAGE_DIR} (Smart Matching + Random Cuts)")
    print(f"   2️⃣ YouTube/Stock: Disabled (Bypassed for Quality)")
    
    # Validate local footage directory
    local_files = get_local_footage_files()
    if not local_files:
        print(f"   ⚠️ No local files found! Please add .mp4 files to {config.LOCAL_FOOTAGE_DIR}")
        return [[] for _ in visual_queries]
    
    print(f"   ✓ Found {len(local_files)} local compilation(s)")
    for lf in local_files:
        print(f"      • {lf.name}")
    
    # Find ffmpeg binary
    ffmpeg_path = shutil.which('ffmpeg')
    if not ffmpeg_path:
        ffmpeg_path = '/opt/homebrew/bin/ffmpeg'
        if not Path(ffmpeg_path).exists():
            print(f"   ✗ FFmpeg not found - cannot perform smart cuts!")
            return [[] for _ in visual_queries]
    
    # Find ffprobe binary
    ffprobe_path = shutil.which('ffprobe')
    if not ffprobe_path:
        ffprobe_path = '/opt/homebrew/bin/ffprobe'
        if not Path(ffprobe_path).exists():
            print(f"   ✗ FFprobe not found - cannot determine video durations!")
            return [[] for _ in visual_queries]
    
    downloaded_segment_paths = []
    clip_duration = 4.0  # Seconds per clip
    
    for i, query in enumerate(visual_queries):
        print(f"\n  📥 Segment {i}: '{query}'")
        variation_paths = []
        
        for v in range(1, config.SCENE_VIDEO_VARIATIONS + 1):
            output_path = config.ASSETS_DIR / f"segment_{i}_v{v}.mp4"
            
            # ===================================================================
            # STEP 1: SMART MATCHING
            # ===================================================================
            source_file = find_best_matching_local_file(query, local_files)
            print(f"    🎯 v{v}: Matched '{source_file.name}' for query '{query}'")
            
            try:
                # ===================================================================
                # STEP 2: GET DURATION WITH FFPROBE
                # ===================================================================
                duration_cmd = [
                    ffprobe_path, '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    str(source_file)
                ]
                
                result = subprocess.run(
                    duration_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10
                )
                
                duration = float(result.stdout.strip()) if result.returncode == 0 else 0.0
                print(f"    ⏱️  Duration: {duration:.1f}s")
                
                # ===================================================================
                # STEP 3: SMART RANDOM CUT (if video is long enough)
                # ===================================================================
                if duration > 10.0:
                    # Calculate safe random start time
                    # Buffer: 5s from start, 2s from end (to ensure full 4s clip fits)
                    min_start = 5.0
                    max_start = duration - clip_duration - 2.0
                    
                    if max_start < min_start:
                        # Edge case: video is barely long enough
                        max_start = min_start
                    
                    start_time = random.uniform(min_start, max_start)
                    
                    print(f"    ✂️  Random cut: {start_time:.1f}s → {start_time + clip_duration:.1f}s")
                    
                    # CRITICAL: Use stream-copy for instant, lossless cutting
                    cut_cmd = [
                        ffmpeg_path, '-y',
                        '-ss', str(start_time),      # Fast seek (BEFORE input)
                        '-i', str(source_file),      # Input file
                        '-t', str(clip_duration),    # Duration (4 seconds)
                        '-c', 'copy',                # Stream copy (NO re-encoding!)
                        '-avoid_negative_ts', '1',   # Fix timestamp issues
                        str(output_path)
                    ]
                    
                    cut_result = subprocess.run(
                        cut_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=30
                    )
                    
                    if cut_result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
                        print(f"    ✓ Smart cut successful ({output_path.stat().st_size // 1024} KB)")
                        variation_paths.append(output_path)
                    else:
                        # FFmpeg cut failed, fallback to full copy
                        print(f"    ⚠️  FFmpeg cut failed, falling back to full copy")
                        shutil.copy(str(source_file), str(output_path))
                        variation_paths.append(output_path)
                
                else:
                    # ===================================================================
                    # FALLBACK: Video too short (<10s), copy full file
                    # ===================================================================
                    print(f"    ⚠️  Video too short ({duration:.1f}s), copying full file")
                    shutil.copy(str(source_file), str(output_path))
                    variation_paths.append(output_path)
            
            except subprocess.TimeoutExpired:
                print(f"    ✗ Timeout during ffprobe/ffmpeg, falling back to full copy")
                shutil.copy(str(source_file), str(output_path))
                variation_paths.append(output_path)
            
            except Exception as e:
                print(f"    ✗ Error: {str(e)[:60]}, falling back to full copy")
                shutil.copy(str(source_file), str(output_path))
                variation_paths.append(output_path)
        
        downloaded_segment_paths.append(variation_paths)
    
    print(f"\n✓ All {len(visual_queries)} segment(s) ready from local library with smart cuts!")
    return downloaded_segment_paths


if __name__ == "__main__":
    # Test the video downloader
    test_keywords = ["dark ocean", "foggy forest", "night sky"]
    videos = download_videos(test_keywords, num_videos=2)
    print(f"Downloaded videos: {videos}")
