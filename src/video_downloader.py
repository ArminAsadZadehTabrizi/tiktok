"""Pexels Video API integration for downloading dark/moody footage"""
import requests
import time
from pathlib import Path
import config


def search_videos(keywords, num_videos=3):
    """
    Search for videos on Pexels using given keywords.
    
    Args:
        keywords (list): List of search terms
        num_videos (int): Number of videos to find
    
    Returns:
        list: Video data including download URLs
    """
    headers = {
        "Authorization": config.PEXELS_API_KEY
    }
    
    all_videos = []
    
    for keyword in keywords:
        print(f"  Searching Pexels for: '{keyword}'")
        
        params = {
            "query": f"{keyword} dark moody",  # Add dark/moody to search
            "orientation": config.PEXELS_ORIENTATION,
            "size": config.PEXELS_SIZE,
            "per_page": 5  # Get a few options
        }
        
        try:
            response = requests.get(
                config.PEXELS_API_URL,
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            videos = data.get("videos", [])
            
            if videos:
                # Get the first video from this keyword search
                video = videos[0]
                
                # Find the best quality vertical video file
                video_files = video.get("video_files", [])
                vertical_files = [
                    vf for vf in video_files 
                    if vf.get("height", 0) > vf.get("width", 0)  # Portrait orientation
                ]
                
                if vertical_files:
                    # Sort by quality (higher resolution first)
                    vertical_files.sort(
                        key=lambda x: x.get("height", 0) * x.get("width", 0),
                        reverse=True
                    )
                    
                    video_info = {
                        "url": vertical_files[0]["link"],
                        "width": vertical_files[0].get("width"),
                        "height": vertical_files[0].get("height"),
                        "keyword": keyword
                    }
                    all_videos.append(video_info)
                    print(f"    ✓ Found video ({video_info['width']}x{video_info['height']})")
            else:
                print(f"    ✗ No videos found for '{keyword}'")
            
            # Be nice to the API
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"    ✗ Error searching for '{keyword}': {e}")
            continue
    
    # Ensure we have enough videos
    if len(all_videos) < num_videos:
        print(f"  Warning: Only found {len(all_videos)} videos (requested {num_videos})")
    
    return all_videos[:num_videos]


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


def download_videos(keywords, num_videos=3):
    """
    Search and download videos for the given keywords.
    
    Args:
        keywords (list): Search terms from script generation
        num_videos (int): Number of videos to download
    
    Returns:
        list: Paths to downloaded video files
    """
    print(f"\n📹 Downloading videos from Pexels")
    
    # Search for videos
    videos = search_videos(keywords, num_videos)
    
    if not videos:
        raise Exception("No videos found. Check your Pexels API key and keywords.")
    
    # Download videos
    downloaded_paths = []
    for i, video in enumerate(videos):
        output_path = config.ASSETS_DIR / f"temp_video_{i}.mp4"
        
        if download_video(video["url"], output_path):
            downloaded_paths.append(output_path)
    
    if not downloaded_paths:
        raise Exception("Failed to download any videos")
    
    print(f"✓ Downloaded {len(downloaded_paths)} video(s)\n")
    return downloaded_paths


if __name__ == "__main__":
    # Test the video downloader
    test_keywords = ["dark ocean", "foggy forest", "night sky"]
    videos = download_videos(test_keywords, num_videos=2)
    print(f"Downloaded videos: {videos}")
