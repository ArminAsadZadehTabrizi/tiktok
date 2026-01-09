# Fixed Functions - video_downloader.py

## ✅ All Syntax Errors Fixed!

The corrupted Unicode sequences (`\u003e` and `\u003c`) have been successfully replaced with the correct comparison operators (`>` and `<`).

## Verification

✓ Module compiles successfully  
✓ All functions import without errors  
✓ No syntax errors detected

---

## Fixed Functions

### 1. `get_video_duration(file_path)`

```python
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
```

**Fixed**: No corrupted sequences in this function

---

### 2. `find_best_matching_local_file(query, local_files)`

```python
def find_best_matching_local_file(query, local_files):
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
    query_keywords = [kw.strip() for kw in query_lower.split() if len(kw.strip()) >= 3]  # ✅ FIXED
    
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
        
        if score > 0:  # ✅ FIXED
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
```

**Fixed**: 
- Line 1227: `>=` operator (was `\u003e=`)
- Line 1254: `>` operator (was `\u003e`)

---

### 3. `download_videos(visual_queries, fallback_topic=None)`

```python
def download_videos(visual_queries, fallback_topic=None):
    """
    🎬 PRIORITY 1: LOCAL FILES (SMART CUT & MATCHING)
    
    Smart Matching: Analyzes filename keywords to find best match for each query.
    Smart Random Cut: Extracts random 4-second clips using ffprobe + ffmpeg stream-copy.
    
    Features:
      - Keyword-based matching (e.g., "Lamborghini" → "lamborghini_compilation.mp4")
      - Random start time selection with safe buffers
      - Stream-copy (-c copy) for instant, lossless cutting
      - Fallback to full copy for videos <10 seconds  # ✅ FIXED
    
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
                if duration > 10.0:  # ✅ FIXED
                    # Calculate safe random start time
                    # Buffer: 5s from start, 2s from end (to ensure full 4s clip fits)
                    min_start = 5.0
                    max_start = duration - clip_duration - 2.0
                    
                    if max_start < min_start:  # ✅ FIXED
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
                    
                    if cut_result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:  # ✅ FIXED
                        print(f"    ✓ Smart cut successful ({output_path.stat().st_size // 1024} KB)")
                        variation_paths.append(output_path)
                    else:
                        # FFmpeg cut failed, fallback to full copy
                        print(f"    ⚠️  FFmpeg cut failed, falling back to full copy")
                        shutil.copy(str(source_file), str(output_path))
                        variation_paths.append(output_path)
                
                else:
                    # ===================================================================
                    # FALLBACK: Video too short (<10s), copy full file  # ✅ FIXED
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
```

**Fixed**: 
- Line 1289 (comment): `<` operator (was `\u003c`)
- Line 1369: `>` operator (was `\u003e`)
- Line 1375: `<` operator (was `\u003c`)
- Line 1401: `>` operator (was `\u003e`)
- Line 1412 (comment): `<` operator (was `\u003c`)

---

## Summary of Changes

All corrupted Unicode escape sequences have been replaced:
- `\u003e` → `>` (greater than)
- `\u003c` → `<` (less than)
- `\u003e=` → `>=` (greater than or equal)

The file now compiles and imports successfully with no syntax errors!
