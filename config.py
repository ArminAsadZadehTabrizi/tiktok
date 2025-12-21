"""Configuration settings for Dark Facts TikTok Generator"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

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
VIDEO_DURATION_MIN = 15  # Minimum video duration in seconds
VIDEO_DURATION_MAX = 60  # Maximum video duration in seconds

# Pexels API Settings
PEXELS_API_URL = "https://api.pexels.com/videos/search"
PEXELS_ORIENTATION = "portrait"
PEXELS_SIZE = "medium"  # or 'large' for higher quality

# Audio Settings
TTS_VOICE = "en-US-ChristopherNeural"
TTS_RATE = "+0%"  # Speech rate (can adjust: -50% to +100%)
TTS_VOLUME = "+0%"  # Volume (can adjust)

# Background Music Settings
BG_MUSIC_VOLUME = 0.15  # Background music volume (0.0 to 1.0)

# Text/Caption Settings
CAPTION_FONT = "Arial-Bold"
CAPTION_FONTSIZE = 70
CAPTION_COLOR = "white"
CAPTION_STROKE_COLOR = "black"
CAPTION_STROKE_WIDTH = 3
CAPTION_POSITION = "center"

# LLM Settings
LLM_MODEL = "gpt-4"
LLM_TEMPERATURE = 0.8
