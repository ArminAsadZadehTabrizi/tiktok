"""Semantic Matching Helper Functions for Smart Clip Selection"""

import re


def extract_keywords(text):
    """
    Extract meaningful keywords from script text for semantic matching.
    
    Uses a simple but effective approach:
    - Splits text into words
    - Removes common stopwords
    - Filters out short words (< 3 chars)
    - Returns lowercase keywords
    
    Args:
        text (str): Script text to analyze
    
    Returns:
        list: List of lowercase keyword strings
    """
    # Common stopwords to filter out
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
        'when', 'where', 'why', 'how', 'your', 'our', 'their'
    }
    
    # Clean and split text
    text_lower = text.lower()
    # Remove punctuation
    text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
    words = text_clean.split()
    
    # Filter: remove stopwords and short words
    keywords = [w for w in words if w not in stopwords and len(w) >= 3]
    
    return keywords


def detect_clip_category(clip_metadata):
    """
    Detect the category of a clip from its metadata.
    
    Args:
        clip_metadata (dict): Video info dict with potential 'category' field
    
    Returns:
        str: Category name (e.g., 'CARS', 'COMBAT') or 'UNKNOWN'
    """
    # Direct category from metadata (manual YouTube or detected during download)
    if 'category' in clip_metadata and clip_metadata['category']:
        return clip_metadata['category']
    
    # Fallback: Infer from query/source
    query = clip_metadata.get('query', '').lower()
    
    # Use existing category detection logic from video_downloader
    try:
        from src.video_downloader import detect_category_from_query
        detected = detect_category_from_query(query)
        return detected if detected else 'UNKNOWN'
    except:
        return 'UNKNOWN'


def calculate_semantic_score(script_text, clip_metadata):
    """
    Calculate how well a clip matches the script's semantic content.
    
    Scoring System:
    - Exact keyword match: +10 points per match
    - Partial keyword match: +5 points per match
    - Category alignment: +15 points if clip category matches script sentiment
    - Fallback: Generic match based on query overlap
    
    Args:
        script_text (str): The script text for this scene (e.g., segment['text'])
        clip_metadata (dict): Video info dict with 'category', 'query', etc.
    
    Returns:
        int: Relevance score (0-100+)
    """
    score = 0
    
    # Extract keywords from script
    script_keywords = extract_keywords(script_text)
    
    if not script_keywords:
        return 5  # Minimal score for empty/generic text
    
    # Get clip's category
    clip_category = detect_clip_category(clip_metadata)
    
    # Get semantic keywords for all categories
    try:
        from config import (
            SEMANTIC_KEYWORDS, 
            SCORE_EXACT_KEYWORD_MATCH, 
            SCORE_PARTIAL_KEYWORD_MATCH, 
            SCORE_CATEGORY_ALIGNMENT
        )
    except ImportError:
        # Fallback if config doesn't have these yet
        SEMANTIC_KEYWORDS = {}
        SCORE_EXACT_KEYWORD_MATCH = 10
        SCORE_PARTIAL_KEYWORD_MATCH = 5
        SCORE_CATEGORY_ALIGNMENT = 15
    
    # Track which category has the most keyword matches in script
    category_match_counts = {}
    
    for category, keywords in SEMANTIC_KEYWORDS.items():
        match_count = 0
        
        for script_kw in script_keywords:
            for semantic_kw in keywords:
                # Exact match (whole word)
                if script_kw == semantic_kw:
                    score += SCORE_EXACT_KEYWORD_MATCH
                    match_count += 2
                # Partial match (substring)
                elif script_kw in semantic_kw or semantic_kw in script_kw:
                    score += SCORE_PARTIAL_KEYWORD_MATCH
                    match_count += 1
        
        category_match_counts[category] = match_count
    
    # Find the dominant category in the script
    if category_match_counts:
        dominant_category = max(category_match_counts, key=category_match_counts.get)
        
        # Bonus: If clip's category matches the script's dominant sentiment
        if clip_category == dominant_category and category_match_counts[dominant_category] > 0:
            score += SCORE_CATEGORY_ALIGNMENT
    
    return score
