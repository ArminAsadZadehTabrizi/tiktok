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

# 🎥 YOUTUBE SOURCE POOLS (Verified High-Quality Sources)
# The bot will pick a random video, random timestamp, and rip a 4s clip.
YOUTUBE_SOURCES = {
    # 🏎️ FAST & AGGRESSIVE (Autos)
    "CARS": [
        "https://www.youtube.com/watch?v=ppqH2tYyY6o",  # Woyshnis Media (Best Car Edits)
        "https://www.youtube.com/watch?v=0pLd8V0GzZw",  # Night Run (High Quality)
        "https://www.youtube.com/watch?v=WJ93MQy_6F0",  # Tokyo Night Drive
    ],
    # 🥊 COMBAT & DISCIPLINE (Kampfsport)
    "COMBAT": [
        "https://www.youtube.com/watch?v=_YqgC7t87vY",  # Mike Tyson Training (Official)
        "https://www.youtube.com/watch?v=k9X7X5G7zZw",  # Canelo Training
        "https://www.youtube.com/watch?v=jY7Xn_s3nOU",  # Lomachenko (Matrix style)
    ],
    # 💪 GYM & CALISTHENICS (Nacht/Outdoor Training)
    "GYM": [
        "https://www.youtube.com/watch?v=J9f2g3Q9s4A",  # Street Workout Night
        "https://www.youtube.com/watch?v=VR1-10B5dBY",  # David Goggins Motivation
        "https://www.youtube.com/watch?v=P28dgyW7WQA",  # Chris Heria Night Training
    ],
    # 💰 WEALTH & EMPIRE (Villen, Yachten, Jets)
    "LUXURY": [
        "https://www.youtube.com/watch?v=OpZ_gW-z_ME",  # Monaco Luxury Lifestyle
        "https://www.youtube.com/watch?v=1M7a65978rU",  # Private Jet Cinematic
        "https://www.youtube.com/watch?v=vUgOZzLktTU",  # Dark Luxury Mansion
    ]
}
