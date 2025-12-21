# Dark Facts TikTok Generator - Quick Reference

## 🚀 Quick Start (2 Steps)

```bash
# 1. Setup (one time)
bash setup.sh

# 2. Generate video
python main.py
```

## 📁 Project Layout

```
tiktok/
├── main.py              # Run this to generate videos
├── config.py            # Edit settings here
├── requirements.txt     # Dependencies
├── .env                 # YOUR API KEYS (create this!)
├── src/                 # Source code (don't touch unless customizing)
├── assets/              # Put background_music.mp3 here
└── output/              # Generated videos appear here
```

## 🔑 Required API Keys

Create `.env` file with:
```
OPENAI_API_KEY=sk-...          # Get from: platform.openai.com/api-keys
PEXELS_API_KEY=...             # Get from: pexels.com/api (FREE!)
```

## ⚙️ Common Customizations

All settings in `config.py`:

**Change video length:**
```python
VIDEO_DURATION_MIN = 15
VIDEO_DURATION_MAX = 60
```

**Change voice:**
```python
TTS_VOICE = "en-US-ChristopherNeural"
# Try: en-US-GuyNeural, en-GB-RyanNeural, etc.
```

**Adjust background music volume:**
```python
BG_MUSIC_VOLUME = 0.15  # 0.0 to 1.0
```

**Change caption style:**
```python
CAPTION_FONTSIZE = 70
CAPTION_COLOR = "white"
CAPTION_STROKE_COLOR = "black"
CAPTION_STROKE_WIDTH = 3
```

## 🎨 Video Specs

- **Format**: 1080x1920 (9:16 vertical)
- **FPS**: 30
- **Codec**: H.264 (compatible with all platforms)
- **Audio**: AAC
- **Duration**: Matches voiceover length

## 🐛 Troubleshooting

**"OPENAI_API_KEY not found"**
→ Create `.env` file with your API key

**"No videos found"**
→ Check Pexels API key, try different keywords

**Font errors**
→ Script will use default font automatically

**Audio not generating**
→ Need internet connection for Edge TTS

**Video render slow**
→ Normal! First video takes 2-3 minutes

## 📊 Expected Runtime

- Script generation: 5-10 seconds
- Video download: 10-30 seconds
- Audio generation: 3-5 seconds
- Video editing: 1-3 minutes
- **Total**: ~2-4 minutes per video

## 🎯 Pro Tips

1. **Batch generation**: Run multiple times for content library
2. **Test keywords**: Edit script_generator.py to influence topics
3. **Music matters**: Dark ambient music increases watch time
4. **Hook is key**: First 2 seconds determine virality
5. **Post timing**: Upload 6-9 PM for best engagement

## 📝 Output Example

```
output/dark_facts_20251221_201845.mp4
```

Format: `dark_facts_YYYYMMDD_HHMMSS.mp4`

## 🔄 Clean Start

If something goes wrong:
```bash
# Remove temp files
rm -f assets/temp_*

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## 📚 Documentation

- Full README: `README.md`
- Setup details: `walkthrough.md` (in artifacts)
- Implementation plan: `implementation_plan.md` (in artifacts)

---

**Need help?** Check the detailed README or review the walkthrough documentation.
