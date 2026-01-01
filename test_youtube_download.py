#!/usr/bin/env python3
"""
Test script for YouTube download functionality with dynamic search and error handling.
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.video_downloader import check_youtube_url_health, search_youtube_videos, download_youtube_clip
import config

def test_url_health_check():
    """Test URL validation functionality"""
    print("\n🧪 TEST 1: URL Health Check")
    print("="*50)
    
    # Test a known working URL
    test_url = "https://www.youtube.com/watch?v=rX372hwV65k"
    print(f"Testing URL: {test_url}")
    is_valid = check_youtube_url_health(test_url)
    print(f"Result: {'✓ Valid' if is_valid else '✗ Invalid/Dead'}")
    return is_valid

def test_dynamic_search():
    """Test dynamic YouTube search"""
    print("\n🧪 TEST 2: Dynamic YouTube Search")
    print("="*50)
    
    category = "CARS"
    print(f"Searching for category: {category}")
    results = search_youtube_videos(category, max_results=3)
    
    print(f"\nFound {len(results)} video(s):")
    for i, url in enumerate(results, 1):
        print(f"  {i}. {url}")
    
    return len(results) > 0

def test_download_clip():
    """Test downloading a YouTube clip"""
    print("\n🧪 TEST 3: Download YouTube Clip")
    print("="*50)
    
    category = "CARS"
    output_path = config.ASSETS_DIR / "test_youtube_clip.mp4"
    
    print(f"Attempting to download {category} clip to: {output_path}")
    success = download_youtube_clip(category, output_path, clip_duration=5)
    
    if success and output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"✓ Download successful! File size: {size_mb:.2f} MB")
        # Clean up test file
        output_path.unlink()
        print("✓ Test file cleaned up")
        return True
    else:
        print("✗ Download failed")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("YouTube Download Functionality Test Suite")
    print("="*50)
    
    results = {}
    
    # Run tests
    try:
        results['health_check'] = test_url_health_check()
    except Exception as e:
        print(f"✗ Health check error: {e}")
        results['health_check'] = False
    
    try:
        results['dynamic_search'] = test_dynamic_search()
    except Exception as e:
        print(f"✗ Search error: {e}")
        results['dynamic_search'] = False
    
    try:
        results['download_clip'] = test_download_clip()
    except Exception as e:
        print(f"✗ Download error: {e}")
        results['download_clip'] = False
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\n{total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
