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

# ==============================================================================
# 📹 VIDEO SOURCE CONFIGURATION (PRIORITY SYSTEM)
# ==============================================================================
# Priority 1: Local Files (assets/my_footage/*.mp4)
# Priority 2: Curated YouTube List (Below) - NOW CATEGORY-BASED
# Priority 3: Automated Search (Fallback)

# 📹 VIDEO SOURCE CONFIGURATION (CATEGORIZED MANUAL LIST)
# Categories: "CARS", "COMBAT", "LUXURY", "STOIC" (matches detection logic)
MANUAL_YOUTUBE_URLS = {
    "STOIC": [
        "https://www.youtube.com/watch?v=OZBP9lP_WlU",  # Rome 4K
        "https://www.youtube.com/watch?v=zMQ3PYM-7lE",  # Greek Gods
    ],
    "COMBAT": [
        "https://www.youtube.com/watch?v=pIHpE3PX4Tg",  # Boxing Dark
        "https://www.youtube.com/watch?v=6Ny64-5xSk4",  # Go Again
        "https://www.youtube.com/watch?v=GUrr0vRGke0",  # Way of Life
        "https://www.youtube.com/watch?v=BH6zVRKSOD0",  # Training BMPCC
    ],
    "LUXURY": [
        "https://www.youtube.com/watch?v=S_X6WCZZSa8",  # Billionaire Empire
        "https://www.youtube.com/watch?v=w_0kDNPJ2oQ",  # Mansion
    ],
    "CARS": [
        "https://www.youtube.com/watch?v=_iHuB7tbdXQ",  # Porsche Night
        "https://www.youtube.com/watch?v=Vjd4NJaoxIs",  # Ferrari F40
        "https://www.youtube.com/watch?v=160tqFcKXZM",  # McLaren POV
    ]
}

# Fallback for unknown categories
DEFAULT_CATEGORY = "LUXURY"

# ⚙️ DOWNLOAD SETTINGS
YOUTUBE_DOWNLOAD_STRATEGY = "stable"  # 'stable' (pre-merged) or 'quality' (separate streams)
LOCAL_FOOTAGE_DIR = ASSETS_DIR / "my_footage"

# Ensure directories exist
ASSETS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
LOCAL_FOOTAGE_DIR.mkdir(exist_ok=True)  # Create manual footage directory

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

# 🎥 YOUTUBE CONFIGURATION
# Enable/disable dynamic search fallback when configured URLs fail
YOUTUBE_ENABLE_SEARCH = True

# Path to YouTube cookies file for age-restricted content (required for 1080p)
# To export cookies: Use browser extension "Get cookies.txt LOCALLY"
# The file will be automatically used when present to prevent 403 errors
YOUTUBE_COOKIE_FILE = BASE_DIR / "youtube_cookies.txt"

# Minimum video duration for search results (in seconds)
YOUTUBE_MIN_DURATION = 600  # 10 minutes

# Maximum search results to check per query
YOUTUBE_MAX_RESULTS = 5

# 🔍 YOUTUBE SEARCH QUERIES (Dynamic Fallback)
# These are used when configured URLs are unavailable
YOUTUBE_SEARCH_QUERIES = {
    "CARS": [
        "4k night drive city neon loop",
        "dark supercar tunnel cinematic",
        "cyberpunk night drive POV",
        "tokyo night drive rain 1 hour",
    ],
    "COMBAT": [
        "dark boxing training cinematic",
        "shadow boxing aesthetic noir",
        "heavy bag workout moody lighting",
        "mma training montage dark",
    ],
    "GYM": [
        "dark calisthenics workout night",
        "street workout aesthetic cinematic",
        "gym training moody lighting",
        "bodyweight training dark atmosphere",
    ],
    "LUXURY": [
        "old money aesthetic dark",
        "luxury lifestyle cinematic moody",
        "dark academia atmosphere",
        "private jet interior luxury dark",
    ]
}

# 🎥 YOUTUBE SOURCE POOLS (THE ANDREW TATE AESTHETIC)
# Focus: Dark Luxury, Night Cities, Faceless Power, Physical Dominance.
# URLs validated on: 2026-01-01
YOUTUBE_SOURCES = {
    # 🏎️ FAST & AGGRESSIVE (Night, Rain, Neon, Speed)
    "CARS": [
        "https://www.youtube.com/watch?v=rX372hwV65k",  # Night Drive in Rain (Heavy Atmosphere)
        "https://www.youtube.com/watch?v=21X5lGlDOfg",  # Cyberpunk/Neon City Drive
        "https://www.youtube.com/watch?v=eSYwD3YsXJw",  # 1 Hour Night Drive 4K (Dark)
        "https://www.youtube.com/watch?v=V7Y8qFqaLTY",  # Batman / Bruce Wayne Car Lifestyle
    ],
    # 🥊 COMBAT & DISCIPLINE (Shadow Boxing, Hood, Rain)
    "COMBAT": [
        "https://www.youtube.com/watch?v=vr7l2Xy_Zp8",  # Boxing Aesthetic (Dark/Gritty)
        "https://www. youtube.com/watch?v=Xk_bVfk39jQ",  # Heavy Bag Workout (Silhouette)
        "https://www.youtube.com/watch?v=1qf8WJtD5QI",  # Mayweather Technical (Clean)
        "https://www.youtube.com/watch?v=jY7Xn_s3nOU",  # Lomachenko Matrix (High Skill)
    ],
    # 💪 GYM & PAIN (No fancy gyms. Outdoor, Night, Sweat)
    "GYM": [
        "https://www.youtube.com/watch?v=q0vgbTnAJ4c",  # Brooklyn Night Calisthenics (PERFEKTER VIBE)
        "https://www.youtube.com/watch?v=J9f2g3Q9s4A",  # Street Workout Night
        "https://www.youtube.com/watch?v=3S8ZkS2V_5I",  # Dark Gym Aesthetic
    ],
    # 💰 WEALTH & EMPIRE (Old Money, Suits, Mafia, Chess)
    "LUXURY": [
        "https://www.youtube.com/watch?v=hN7GYVqQJkA",  # Old Money Aesthetic (Dark/Moody)
        "https://www.youtube.com/watch?v=L_LUpNJxHXA",  # Dark Academia / Mafia Atmosphere
        "https://www.youtube.com/watch?v=8I8og9a6dko",  # Luxury Lifestyle (Suits/Watches)
        "https://www.youtube.com/watch?v=Bearq7QeJk0",  # Billionaire Yacht (Darker parts)
    ]
}