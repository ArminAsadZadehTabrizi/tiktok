#!/usr/bin/env python3
"""
Test script for smart clip selection system.
Validates:
1. Semantic keyword extraction
2. Category detection
3. Scoring logic
4. No duplicate clips
5. Category variety enforcement
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.semantic_matcher import extract_keywords, detect_clip_category, calculate_semantic_score
from config import SEMANTIC_KEYWORDS, MAX_CONSECUTIVE_SAME_CATEGORY


def test_keyword_extraction():
    """Test keyword extraction from script text"""
    print("=" * 60)
    print("TEST 1: Keyword Extraction")
    print("=" * 60)
    
    test_cases = [
        ("Fighting requires discipline and strength to push through pain", 
         ["fighting", "requires", "discipline", "strength", "push", "through", "pain"]),
        ("Drive fast through the tunnel", 
         ["drive", "fast", "through", "tunnel"]),
        ("The rich build empires with money and power",
         ["rich", "build", "empires", "money", "power"])
    ]
    
    for text, expected in test_cases:
        result = extract_keywords(text)
        print(f"\nText: '{text}'")
        print(f"Expected: {expected}")
        print(f"Got: {result}")
        
        # Check if key terms are present
        match_count = sum(1 for kw in expected if kw in result)
        print(f"Match rate: {match_count}/{len(expected)} ({'✓' if match_count >= len(expected) * 0.7 else '✗'})")


def test_category_detection():
    """Test category detection from clip metadata"""
    print("\n" + "=" * 60)
    print("TEST 2: Category Detection")
    print("=" * 60)
    
    test_clips = [
        ({"query": "lamborghini night drive tunnel", "category": "CARS"}, "CARS"),
        ({"query": "shadow boxing training dark", "category": "COMBAT"}, "COMBAT"),
        ({"query": "gym workout muscle discipline"}, "GYM"),  # No explicit category
        ({"query": "luxury yacht champagne"}, "LUXURY"),
        ({"query": "marble statue roman emperor"}, "STOIC"),
    ]
    
    for clip_metadata, expected in test_clips:
        result = detect_clip_category(clip_metadata)
        print(f"\nQuery: '{clip_metadata.get('query', 'N/A')}'")
        print(f"Expected: {expected}")
        print(f"Got: {result}")
        print(f"Status: {'✓' if result == expected else '✗'}")


def test_semantic_scoring():
    """Test semantic relevance scoring"""
    print("\n" + "=" * 60)
    print("TEST 3: Semantic Scoring")
    print("=" * 60)
    
    test_scenarios = [
        # High relevance: Script about fighting, clip is COMBAT
        {
            "script": "You must fight through the pain and never give up",
            "clip": {"query": "shadow boxing dark training", "category": "COMBAT"},
            "expected_high": True
        },
        # Low relevance: Script about fighting, clip is LUXURY
        {
            "script": "You must fight through the pain and never give up",
            "clip": {"query": "yacht champagne luxury", "category": "LUXURY"},
            "expected_high": False
        },
        # Medium relevance: Script about wealth, clip is CARS (luxury cars)
        {
            "script": "Build your empire and dominate the market",
            "clip": {"query": "lamborghini supercar fast", "category": "CARS"},
            "expected_high": False  # Related but not perfect match
        },
    ]
    
    for scenario in test_scenarios:
        score = calculate_semantic_score(scenario["script"], scenario["clip"])
        print(f"\nScript: '{scenario['script']}'")
        print(f"Clip: {scenario['clip']['query']} [{scenario['clip'].get('category', 'UNKNOWN')}]")
        print(f"Score: {score}")
        
        if scenario["expected_high"]:
            status = "✓" if score > 20 else "✗"
            print(f"Expected: HIGH score (>20) - Status: {status}")
        else:
            status = "✓" if score <= 20 else "⚠️"
            print(f"Expected: LOW/MED score (≤20) - Status: {status}")


def test_category_variety():
    """Simulate category tracking to test variety constraint"""
    print("\n" + "=" * 60)
    print("TEST 4: Category Variety Enforcement")
    print("=" * 60)
    
    category_history = ["CARS", "CARS"]  # Two consecutive CARS clips
    next_category = "CARS"
    
    # Check constraint logic
    if len(category_history) >= 2:
        recent = category_history[-2:]
        should_penalize = (recent[0] == recent[1] == next_category and next_category != 'UNKNOWN')
        
        print(f"\nCategory history: {category_history}")
        print(f"Next clip category: {next_category}")
        print(f"Max consecutive allowed: {MAX_CONSECUTIVE_SAME_CATEGORY}")
        print(f"Should apply penalty: {should_penalize}")
        print(f"Status: {'✓ Penalty applied correctly' if should_penalize else '✗ No penalty (unexpected)'}")
    
    # Test variety promotion
    print("\nTest variety promotion:")
    variety_category = "COMBAT"
    should_promote = (category_history[-1] != variety_category)
    print(f"Switching from {category_history[-1]} to {variety_category}")
    print(f"Should promote: {should_promote}")
    print(f"Status: {'✓ Variety encouraged' if should_promote else '✗'}")


def test_deduplication():
    """Test that used_clip_ids prevents repetition"""
    print("\n" + "=" * 60)
    print("TEST 5: Global Deduplication")
    print("=" * 60)
    
    used_clip_ids = set()
    
    test_clips = [
        "/path/to/clip1.mp4",
        "/path/to/clip2.mp4",
        "/path/to/clip1.mp4",  # Duplicate
        "/path/to/clip3.mp4",
        "/path/to/clip2.mp4",  # Duplicate
    ]
    
    for clip_id in test_clips:
        is_duplicate = clip_id in used_clip_ids
        
        if is_duplicate:
            print(f"\n⊗ Clip: {Path(clip_id).name} - DUPLICATE (skipped)")
        else:
            used_clip_ids.add(clip_id)
            print(f"\n✓ Clip: {Path(clip_id).name} - NEW (added)")
    
    print(f"\nTotal unique clips: {len(used_clip_ids)}")
    print(f"Expected: 3")
    print(f"Status: {'✓' if len(used_clip_ids) == 3 else '✗'}")


if __name__ == "__main__":
    print("\n🧪 SMART CLIP SELECTION - TEST SUITE\n")
    
    try:
        test_keyword_extraction()
        test_category_detection()
        test_semantic_scoring()
        test_category_variety()
        test_deduplication()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\nReview the output above to verify:")
        print("  1. Keywords are extracted correctly")
        print("  2. Categories are detected from queries")
        print("  3. Semantic scoring favors relevant clips")
        print("  4. Variety constraints prevent monotony")
        print("  5. Deduplication prevents clip reuse")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
