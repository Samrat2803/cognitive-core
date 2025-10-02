# 🎨 Social Media Content Tools

**Three standalone tools for creating shareable political analysis content**

Created: October 2, 2025  
Location: `backend_v2/shared/`  
Status: ✅ All tools tested and working

---

## 📦 Tools Overview

### **Tool 1: Infographic Generator** 🎨
**File**: `infographic_generator.py`  
**Purpose**: Create Canva-style social media infographics

**Features**:
- 3 templates: minimalist, data_heavy, story
- 6 platform formats: Instagram, LinkedIn, Twitter, TikTok, etc.
- Aistra color palette integrated
- Stats cards, charts embedding, text zones
- Generates PNG images

**Test**: ✅ Passed - Generated 9 infographics (44 KB each)

---

### **Tool 2: Reel Generator** 🎬
**File**: `reel_generator.py`  
**Purpose**: Animate infographics into short videos (reels)

**Features**:
- Text animations: fade, slide, zoom, typewriter
- Multi-scene support
- Background music support
- Vertical format (Instagram Reels, TikTok, YouTube Shorts)
- Generates MP4 videos (H.264)

**Test**: ✅ Passed - Generated 5-second video (30 KB)

---

### **Tool 3: Deck Generator** 📊
**File**: `deck_generator.py`  
**Purpose**: Compile infographics into PowerPoint presentations

**Features**:
- Title slides, section dividers, summary slides
- Multi-section support with notes
- Dark/light themes
- Aistra branding
- Generates PPTX files

**Test**: ✅ Passed - Generated 11-slide deck (141 KB)

---

## 🚀 Quick Start

### Installation (Already Done)
```bash
cd backend_v2
source .venv/bin/activate
uv pip install Pillow moviepy imageio-ffmpeg python-pptx
```

### Test All Tools
```bash
cd backend_v2/shared

# Test Tool 1: Infographic Generator
python infographic_generator.py

# Test Tool 2: Reel Generator (simple test)
python test_reel_simple.py

# Test Tool 3: Deck Generator
python deck_generator.py
```

### Output Location
All generated files: `backend_v2/shared/artifacts/`

---

## 💻 Usage Examples

### Example 1: Create Infographic
```python
from infographic_generator import InfographicGenerator

gen = InfographicGenerator(output_dir="artifacts")

data = {
    "title": "US Sentiment Analysis",
    "subtitle": "Positive outlook on climate policy",
    "stats": [
        {"label": "Sentiment", "value": "+0.75", "color": "primary"},
        {"label": "Sources", "value": "45", "color": "accent"},
        {"label": "Confidence", "value": "92%", "color": "secondary"}
    ],
    "chart_path": "path/to/chart.png",  # Optional
    "footer": "Analysis Date: Oct 2, 2025"
}

result = gen.create_social_post(
    data=data,
    platform="instagram_post",  # or linkedin, twitter, etc.
    template="minimalist"       # or data_heavy, story
)

print(f"Created: {result['path']}")
# Output: artifacts/infographic_instagram_post_minimalist_20251002.png
```

---

### Example 2: Create Reel
```python
from reel_generator import ReelGenerator

reel = ReelGenerator(output_dir="artifacts")

config = {
    "duration": 15,  # seconds
    "style": "fade",
    "text_zones": [
        {
            "text": "Political Sentiment: +75%",
            "position": ("center", "center"),
            "start": 0,
            "duration": 5,
            "fontsize": 80,
            "color": "white"
        },
        {
            "text": "45 Sources Analyzed",
            "position": ("center", "bottom"),
            "start": 5,
            "duration": 10,
            "fontsize": 50,
            "color": "#d9f378"
        }
    ],
    "fps": 30,
    "format": "instagram_reel"
}

result = reel.animate_infographic(
    infographic_path="artifacts/infographic_instagram_post.png",
    animation_config=config
)

print(f"Created: {result['path']}")
# Output: artifacts/reel_instagram_reel_20251002.mp4
```

---

### Example 3: Create PowerPoint Deck
```python
from deck_generator import DeckGenerator

deck = DeckGenerator(output_dir="artifacts")

infographics = [
    "artifacts/sentiment_post_1.png",
    "artifacts/sentiment_post_2.png",
    "artifacts/bias_post_1.png",
    "artifacts/bias_post_2.png"
]

config = {
    "title": "Political Analysis Report",
    "subtitle": "Q4 2025 Comprehensive Analysis",
    "author": "AI Analysis Team",
    "date": "October 2, 2025",
    "add_title_slide": True,
    "add_section_dividers": True,
    "sections": [
        {
            "title": "Sentiment Analysis",
            "slides": [0, 1],
            "notes": "Regional sentiment trends and patterns"
        },
        {
            "title": "Bias Detection",
            "slides": [2, 3],
            "notes": "Media bias analysis across platforms"
        }
    ],
    "add_summary_slide": True,
    "theme": "dark",
    "summary": "Key findings: Positive sentiment trends observed across regions.",
    "contact": "Contact: analysis@political-ai.com"
}

result = deck.create_deck(
    infographic_paths=infographics,
    deck_config=config
)

print(f"Created: {result['path']}")
# Output: artifacts/deck_20251002.pptx
```

---

## 🎨 Aistra Branding (Built-in)

All tools use the Aistra color palette:

```python
COLORS = {
    "primary": "#d9f378",      # Bright green
    "secondary": "#5d535c",    # Purple-gray
    "dark": "#333333",         # Dark gray
    "darkest": "#1c1e20",      # Almost black
    "white": "#FFFFFF",
    "accent": "#00D9FF"        # Bright cyan
}
```

Font: Roboto Flex (with Helvetica fallback)

---

## 📊 Platform Dimensions

### Infographics
- **Instagram Post**: 1080x1080 (square)
- **Instagram Story**: 1080x1920 (vertical)
- **LinkedIn**: 1200x627 (horizontal)
- **Twitter**: 1200x675 (horizontal)
- **Facebook**: 1200x630 (horizontal)

### Reels
- **Instagram Reel**: 1080x1920 (vertical, 15-90s)
- **TikTok**: 1080x1920 (vertical, 15-60s)
- **YouTube Shorts**: 1080x1920 (vertical, up to 60s)

### Presentations
- **PowerPoint**: 16:9 ratio (1920x1080 equivalent)

---

## 🔧 Advanced Features

### Multi-Scene Reels
```python
scenes = [
    {
        "infographic_path": "scene1.png",
        "duration": 5,
        "text_overlays": [
            {"text": "Overview", "position": ("center", "top"), ...}
        ]
    },
    {
        "infographic_path": "scene2.png",
        "duration": 5,
        "text_overlays": [...]
    }
]

result = reel.create_multi_scene_reel(scenes)
```

### Embedding Charts in Infographics
```python
data = {
    "title": "Analysis Results",
    "chart_path": "artifacts/plotly_chart.png",  # From visualization_factory
    ...
}
```

### PowerPoint Sections
```python
"sections": [
    {
        "title": "Section Name",
        "slides": [0, 1, 2],  # Indices of infographics
        "notes": "Speaker notes for this section"
    }
]
```

---

## 🧪 Test Results

### Tool 1: Infographic Generator
- ✅ 9 infographics generated
- ✅ 3 templates × 3 platforms
- ✅ Size: ~40-55 KB per image
- ✅ Execution time: <1 second per image

### Tool 2: Reel Generator
- ✅ Video rendering working
- ✅ MP4 format (H.264)
- ✅ Size: ~30 KB for 5s video (15 FPS)
- ✅ Execution time: ~5 seconds for 5s video

### Tool 3: Deck Generator
- ✅ PowerPoint generation working
- ✅ 11-slide deck with sections
- ✅ Size: ~141 KB
- ✅ Execution time: <1 second

---

## 📂 File Structure

```
backend_v2/shared/
├── infographic_generator.py       ⭐ Tool 1
├── reel_generator.py              ⭐ Tool 2
├── deck_generator.py              ⭐ Tool 3
├── test_reel_simple.py            🧪 Simple test
├── visualization_factory.py       ✅ Already exists
├── artifacts/                     📁 Output folder
│   ├── infographic_*.png          (9 files)
│   ├── reel_*.mp4                 (1 file)
│   ├── deck_*.pptx                (2 files)
│   ├── infographic_test_results.json
│   └── deck_test_results.json
└── templates/                     📁 For future templates
    ├── infographic_templates/
    ├── fonts/
    └── assets/
```

---

## 🔌 Integration with Agents

### Use in Agent Nodes
```python
# In any agent's visualizer node
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../shared'))

from infographic_generator import InfographicGenerator
from reel_generator import ReelGenerator
from deck_generator import DeckGenerator

# Create social media content
gen = InfographicGenerator()
infographic = gen.create_social_post(data, platform="instagram_post")

# Animate it
reel = ReelGenerator()
video = reel.animate_infographic(infographic['path'], animation_config)

# Add to deck
deck = DeckGenerator()
presentation = deck.create_deck([infographic['path']], deck_config)
```

---

## 🎯 Next Steps

### For Agents to Use These Tools:
1. **Import tools** in agent visualizer nodes
2. **Generate infographics** with agent data
3. **Optionally animate** into reels
4. **Compile multiple infographics** into decks
5. **Return artifact paths** to master agent

### Potential Enhancements:
- [ ] Add more animation styles (bounce, rotate, etc.)
- [ ] Support for video backgrounds (instead of static images)
- [ ] Export deck to PDF
- [ ] Custom font support
- [ ] Template library expansion

---

## ❓ Troubleshooting

### Issue: Font not loading
**Solution**: Tools fall back to system fonts automatically (Helvetica)

### Issue: Video rendering slow
**Solution**: Reduce FPS (15 instead of 30) or duration

### Issue: MoviePy import error
**Solution**: Reinstall with `uv pip install moviepy imageio-ffmpeg`

### Issue: PowerPoint won't open
**Solution**: Check file wasn't corrupted, regenerate

---

## 📞 Support

These tools are standalone and don't modify any existing code.

Test commands:
```bash
python infographic_generator.py
python test_reel_simple.py
python deck_generator.py
```

Output: `backend_v2/shared/artifacts/`

---

**Status**: ✅ All tools operational  
**Last Updated**: October 2, 2025  
**Zero Impact**: No existing code was modified

