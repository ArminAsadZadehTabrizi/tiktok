#!/usr/bin/env python3
"""
Quick test to verify category-based URL selection is working correctly
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from src.video_downloader import detect_category_from_query, get_manual_youtube_urls

def test_category_detection():
    """Test category detection from queries"""
    print("=" * 60)
    print("TESTING CATEGORY DETECTION")
    print("=" * 60)
    
    test_cases = [
        ("shadow boxing night street", "COMBAT"),
        ("supercar night drive neon", "CARS"),
        ("ancient rome temple marble", "STOIC"),
        ("private jet luxury interior", "LUXURY"),
        ("gym workout training", "GYM"),
        ("random unknown query", None),
    ]
    
    for query, expected in test_cases:
        detected = detect_category_from_query(query)
        status = "✓" if detected == expected else "✗"
        print(f"{status} Query: '{query}'")
        print(f"   Expected: {expected}, Got: {detected}")
        print()

def test_url_selection():
    """Test URL selection for each category"""
    print("=" * 60)
    print("TESTING CATEGORY-BASED URL SELECTION")
    print("=" * 60)
    
    categories = ["CARS", "COMBAT", "LUXURY", "STOIC", "GYM", "UNKNOWN"]
    
    for category in categories:
        print(f"\n🎯 Testing category: {category}")
        urls = get_manual_youtube_urls(category)
        if urls:
            print(f"   ✓ Found {len(urls)} URL(s)")
            for i, url in enumerate(urls):
                print(f"      {i+1}. {url}")
        else:
            print(f"   ⚠️  No URLs found")
        print()

def test_manual_urls_structure():
    """Test that manual URLs are properly structured"""
    print("=" * 60)
    print("TESTING CONFIG STRUCTURE")
    print("=" * 60)
    
    manual_urls = getattr(config, 'MANUAL_YOUTUBE_URLS', None)
    default_cat = getattr(config, 'DEFAULT_CATEGORY', None)
    
    print(f"\n✓ MANUAL_YOUTUBE_URLS type: {type(manual_urls)}")
    
    if isinstance(manual_urls, dict):
        print(f"✓ Dictionary structure detected")
        total_urls = sum(len(urls) for urls in manual_urls.values())
        print(f"✓ Total categories: {len(manual_urls.keys())}")
        print(f"✓ Categories: {', '.join(manual_urls.keys())}")
        print(f"✓ Total URLs: {total_urls}")
        
        for cat, urls in manual_urls.items():
            print(f"   • {cat}: {len(urls)} URL(s)")
    else:
        print(f"⚠️  Legacy flat list detected")
    
    print(f"\n✓ DEFAULT_CATEGORY: {default_cat}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CATEGORY-BASED VIDEO SELECTION TEST")
    print("=" * 60 + "\n")
    
    test_manual_urls_structure()
    print()
    test_category_detection()
    print()
    test_url_selection()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE ✓")
    print("=" * 60 + "\n")
