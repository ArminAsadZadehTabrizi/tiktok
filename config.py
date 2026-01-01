"""Configuration settings for Dark Facts TikTok Generator"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "PLACEHOLDER_FOR_USER_KEY")

# Twitter API Keys
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Paths
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
BACKGROUND_MUSIC_PATH = ASSETS_DIR / "background_music.mp3"

# Ensure directories exist
ASSETS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Video Settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
VIDEO_DURATION_MIN = 60  # Minimum video duration in seconds
VIDEO_DURATION_MAX = 120  # Maximum video duration in seconds

# Pexels API Settings
PEXELS_API_URL = "https://api.pexels.com/videos/search"
PEXELS_ORIENTATION = "portrait"
PEXELS_SIZE = "medium"  # or 'large' for higher quality

# Pixabay API Settings
PIXABAY_BASE_URL = "https://pixabay.com/api/videos/"

# Audio Settings
TTS_VOICE = "en-US-GuyNeural"
TTS_RATE = "+0%"  # Speech rate (can adjust: -50% to +100%)
TTS_VOLUME = "+0%"  # Volume (can adjust)

# Background Music Settings
BG_MUSIC_VOLUME = 0.30  # Background music volume (0.0 to 1.0)

# Video Variation Settings
SCENE_VIDEO_VARIATIONS = 2  # Number of video variations to download per scene (A/B-roll)

# Text/Caption Settings
CAPTION_FONT = "Arial-Bold"
CAPTION_FONTSIZE = 80
CAPTION_COLOR = "white"
CAPTION_STROKE_COLOR = "black"
CAPTION_STROKE_WIDTH = 3
CAPTION_POSITION = "center"

# LLM Settings
LLM_MODEL = "gpt-4o"
LLM_TEMPERATURE = 0.8

# 🎥 YOUTUBE SOURCE POOLS (Long-Format Dark Aesthetics)
# Using 1-Hour+ loops ensures consistent visual style and higher availability.
YOUTUBE_SOURCES = {
    # 🏎️ FAST & AGGRESSIVE (Night Drives / Neon / Rain)
    "CARS": [
        "https://www.youtube.com/watch?v=eSYwD3YsXJw",  # 1 Hour Night Drive 4K (Relaxing/Dark)
        "https://www.youtube.com/watch?v=uL62i-Kk68s",  # Tokyo Night Drive 4K - 1 Hour
        "https://www.youtube.com/watch?v=21X5lGlDOfg",  # Cyberpunk City Night Drive
        "https://www.youtube.com/watch?v=rX372hwV65k",  # Night Drive in Rain (Heavy Atmosphere)
    ],
    # 🥊 COMBAT & DISCIPLINE (Training / Shadow Boxing)
    "COMBAT": [
        "https://www.youtube.com/watch?v=1qf8WJtD5QI",  # Mayweather Padwork (Clean/Technical)
        "https://www.youtube.com/watch?v=Xk_bVfk39jQ",  # Heavy Bag Workout Aesthetic (Dark)
        "https://www.youtube.com/watch?v=_YqgC7t87vY",  # Mike Tyson (Manchmal restricted, aber gut)
        "https://www.youtube.com/watch?v=vr7l2Xy_Zp8",  # Boxing Training Motivation (Compilation)
    ],
    # 💪 GYM & CALISTHENICS (Dark / Outdoor / Hood)
    "GYM": [
        "https://www.youtube.com/watch?v=q0vgbTnAJ4c",  # Brooklyn Night Calisthenics (Dark Vibe)
        "https://www.youtube.com/watch?v=J9f2g3Q9s4A",  # Street Workout Night
        "https://www.youtube.com/watch?v=3S8ZkS2V_5I",  # Dark Gym Aesthetic
    ],
    # 💰 WEALTH & EMPIRE (Old Money / Dark Luxury)
    "LUXURY": [
        "https://www.youtube.com/watch?v=hN7GYVqQJkA",  # Old Money Aesthetic (Dark/Moody)
        "https://www.youtube.com/watch?v=L_LUpNJxHXA",  # Dark Academia Atmosphere
        "https://www.youtube.com/watch?v=V7Y8qFqaLTY",  # Bruce Wayne Lifestyle (Dark Luxury)
        "https://www.youtube.com/watch?v=8I8og9a6dko",  # Luxury Lifestyle (Cars/Jets)
    ]
}