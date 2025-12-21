# Dark Facts TikTok Generator 🌑

Fully automated Python script that generates creepy, unsettling "Dark Facts" TikTok videos using AI.

## Features

- 🤖 **AI Script Generation**: Uses OpenAI GPT to create compelling dark facts about the world, ocean, and space
- 🎥 **Automatic Video Sourcing**: Downloads moody, dark vertical videos from Pexels API
- 🎤 **Professional Voiceover**: Deep, serious TTS using Edge TTS (Christopher Neural voice)
- 🎨 **Cinematic Effects**: Black & white high-contrast filters for a scary aesthetic
- 📝 **Stylized Captions**: Bold white text with black outline, centered on screen
- 🎵 **Background Music**: Optional dark ambient soundtrack mixing
- 📱 **TikTok-Ready**: Outputs vertical 9:16 format (1080x1920) videos

## Quick Start

### 1. Installation

```bash
# Clone the repository (if applicable)
cd tiktok

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:
```
OPENAI_API_KEY=your_openai_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Pexels: https://www.pexels.com/api/ (free)

### 3. Add Background Music (Optional)

Place your dark ambient/drone music file at:
```
assets/background_music.mp3
```

### 4. Generate Your First Video

```bash
python main.py
```

That's it! The script will:
1. Generate a creepy fact script
2. Download 2-3 dark/moody videos from Pexels
3. Create a voiceover
4. Edit everything together with filters and captions
5. Output the final video to `output/dark_facts_TIMESTAMP.mp4`

## Project Structure

```
tiktok/
├── main.py                 # Main orchestration script
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create this)
├── .env.example          # Template for .env
├── src/
│   ├── script_generator.py    # LLM script generation
│   ├── video_downloader.py    # Pexels video API
│   ├── audio_generator.py     # Edge TTS voiceover
│   └── video_editor.py        # MoviePy editing pipeline
├── assets/
│   └── background_music.mp3   # Your dark ambient music
└── output/
    └── dark_facts_*.mp4       # Generated videos
```

## Customization

Edit `config.py` to customize:
- Video dimensions and FPS
- Caption font, size, and colors
- TTS voice and speech rate
- Background music volume
- LLM model and temperature
- Pexels search preferences

## Example Output

The script generates videos with:
- **Hook**: "Did you know..."
- **Body**: An unsettling 40-word fact
- **Visuals**: Dark, moody footage matching the theme
- **Audio**: Deep voiceover + optional background music
- **Effects**: B&W filter, bold captions, professional editing

## Troubleshooting

**No videos downloading:**
- Check your Pexels API key in `.env`
- Ensure you have internet connection
- Try different keywords in the script

**Audio not generating:**
- Edge TTS requires internet connection
- Check if the voice `en-US-ChristopherNeural` is available

**Video rendering fails:**
- Ensure all dependencies are installed
- Check that MoviePy has necessary codecs
- Try reducing video quality in config

**Missing font errors:**
- The script will fallback to default fonts
- Install Arial or modify `CAPTION_FONT` in config.py

## Requirements

- Python 3.8+
- Internet connection (for APIs)
- ~500MB disk space for video processing

## License

This project is for educational and creative purposes. Ensure you comply with:
- OpenAI's usage policies
- Pexels' license terms
- TikTok's content guidelines

## Tips for Viral Content

1. **Timing**: Keep videos 15-30 seconds for best engagement
2. **Hook**: First 2 seconds are crucial - make them shocking
3. **Music**: Dark ambient creates the perfect mood
4. **Frequency**: Post consistently (1-2 videos per day)
5. **Hashtags**: Use #darkfacts #creepyfacts #didyouknow

---

Made with 🌑 for creating viral Dark Facts content