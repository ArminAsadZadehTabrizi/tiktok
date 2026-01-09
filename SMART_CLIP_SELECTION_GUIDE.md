# Quick Start: Smart Clip Selection System

## What Changed?

Your TikTok bot now intelligently selects background clips based on:
1. **Script Content**: Matches "fighting" keywords → COMBAT clips
2. **Category Variety**: No more than 2 consecutive CARS clips
3. **Zero Repeats**: Each clip used only once per video

---

## Running Your Bot

**Nothing changes!** Use the same command:
```bash
python main.py
```

The smart selection happens automatically in the background.

---

## Understanding the Console Logs

### New Output You'll See:

```
🎥 Scene 1: "You must fight through pain..."

  📊 Variation 1: Score=35 (relevance:35 + penalty:0 + bonus:0) [COMBAT]
  📊 Variation 2: Score=20 (relevance:20 + penalty:0 + bonus:0) [LUXURY]
  🏆 Selected: Variation 1 with score 35 [COMBAT]
```

**What this means**:
- **Relevance score**: How well the clip matches the script (higher = better)
- **Penalty**: -50 if this category was used too much recently
- **Bonus**: +10 for smooth category transitions
- **Selected**: The clip with the highest final score wins

### Final Summary:
```
📊 Clip Selection Summary:
   Total scenes: 8
   Unique clips used: 8  ← Should match total scenes (no repeats!)
   Category distribution: {'COMBAT': 3, 'LUXURY': 2, 'GYM': 2, 'CARS': 1}
```

---

## Tuning the System

Edit **`config.py`** (bottom of file) to adjust behavior:

### Make Semantic Matching Stronger
```python
SCORE_EXACT_KEYWORD_MATCH = 15  # Default: 10 (increase for stronger matching)
```

### Allow More Variety (Weaker Penalties)
```python
MAX_CONSECUTIVE_SAME_CATEGORY = 3  # Default: 2 (1-5 range)
SCORE_VARIETY_PENALTY = -30  # Default: -50 (less negative = weaker penalty)
```

### Reward Category Switches More
```python
SCORE_NATURAL_TRANSITION_BONUS = 20  # Default: 10
```

---

## Testing Without Generating Videos

Run the test suite to verify everything works:
```bash
python3 test_smart_clip_selection.py
```

Expected output: All tests marked with ✓ (green checkmarks)

---

## Troubleshooting

### Issue: "All variations exhausted/blocked"
**Cause**: Not enough clip variations to avoid repeats  
**Solution**: 
- Increase `SCENE_VIDEO_VARIATIONS` in config.py (default: 2)
- Add more local footage files to `assets/my_footage/`
- The system will auto-reset `used_clip_ids` as a fallback

### Issue: Too Many CARS/COMBAT Clips
**Cause**: Script has many keywords matching that category  
**Solution**:
- Strengthen variety penalty: `SCORE_VARIETY_PENALTY = -70`
- Lower consecutive limit: `MAX_CONSECUTIVE_SAME_CATEGORY = 1`

### Issue: Clips Don't Match Script Well
**Cause**: Generic script text or missing keywords  
**Solution**:
- Add custom keywords to `SEMANTIC_KEYWORDS` in config.py
- Example: `"CARS": ["drive", "speed", "fast", "YOUR_KEYWORD_HERE"]`

---

## Advanced: Adding Custom Categories

Edit `config.py` and add a new category:

```python
SEMANTIC_KEYWORDS = {
    # ... existing categories ...
    "NATURE": [  # NEW CATEGORY
        "forest", "ocean", "mountain", "wildlife", "landscape"
    ]
}
```

Then ensure your video files or queries include the category:
```python
# In video_downloader.py - manual tagging example
video_info = {
    # ... other fields ...
    "category": "NATURE"  # Manually set
}
```

---

## Rollback to Old System

If you need to revert:
```bash
cd /Users/Armin/testprojekt/tiktok
cp src/video_editor.py.backup src/video_editor.py
```

---

## Questions?

Check the full documentation:
- **Implementation Plan**: `/Users/Armin/.gemini/antigravity/brain/.../implementation_plan.md`
- **Walkthrough**: `/Users/Armin/.gemini/antigravity/brain/.../walkthrough.md`
- **Task List**: `/Users/Armin/.gemini/antigravity/brain/.../task.md`
