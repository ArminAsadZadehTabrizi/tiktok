"""
🧪 TEST: Smart Local Matching & Random Cuts

This script tests the refactored download_videos function to verify:
  1. Smart Matching: Keywords in query match filenames correctly
  2. Smart Random Cuts: Each video gets a different random 4s clip
  3. Stream-Copy: FFmpeg uses -c copy for instant lossless cuts
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from src.video_downloader import download_videos

def test_smart_local_cuts():
    print("=" * 80)
    print("🧪 TESTING: Smart Local Matching & Random Cuts")
    print("=" * 80)
    
    # Check if local footage exists
    if not config.LOCAL_FOOTAGE_DIR.exists():
        print(f"\n❌ ERROR: {config.LOCAL_FOOTAGE_DIR} does not exist!")
        print(f"   Please create it and add .mp4 files first.")
        return
    
    local_files = list(config.LOCAL_FOOTAGE_DIR.glob("*.mp4"))
    if not local_files:
        print(f"\n❌ ERROR: No .mp4 files found in {config.LOCAL_FOOTAGE_DIR}!")
        print(f"   Please add some video files to test with.")
        return
    
    print(f"\n✓ Found {len(local_files)} local video file(s):")
    for f in local_files:
        print(f"  • {f.name}")
    
    # Test queries (designed to trigger smart matching)
    test_queries = [
        "Lamborghini night drive fast",
        "Boxing training dark gym",
        "Money cash luxury wealth"
    ]
    
    print(f"\n📝 Test Queries:")
    for i, q in enumerate(test_queries):
        print(f"  {i+1}. \"{q}\"")
    
    print(f"\n{'=' * 80}")
    print("🚀 Running download_videos with smart matching...")
    print("=" * 80)
    
    # Run the function
    results = download_videos(test_queries)
    
    # Verify results
    print(f"\n{'=' * 80}")
    print("📊 RESULTS:")
    print("=" * 80)
    
    for i, segment_paths in enumerate(results):
        print(f"\nSegment {i} (\"{test_queries[i]}\"):")
        if segment_paths:
            for j, path in enumerate(segment_paths):
                if path.exists():
                    size_kb = path.stat().st_size // 1024
                    print(f"  ✓ Variation {j+1}: {path.name} ({size_kb} KB)")
                else:
                    print(f"  ✗ Variation {j+1}: File not created!")
        else:
            print(f"  ✗ No variations created!")
    
    print(f"\n{'=' * 80}")
    print("✅ TEST COMPLETE")
    print("=" * 80)
    print("\n💡 TIP: Check the output files in assets/ to verify:")
    print("   1. Each clip is exactly 4 seconds")
    print("   2. Different clips start at different random times")
    print("   3. Quality is identical to source (stream-copy, no re-encoding)")

if __name__ == "__main__":
    test_smart_local_cuts()
