# 🚀 Infographic System - Quick Start Guide

**Status**: ✅ Complete, Tested, Ready to Use  
**Date**: October 2, 2025

---

## ⚡ 30-Second Overview

```python
# 1. Import
from infographic_schemas import KeyMetricsDashboard, MetricItem
from html_infographic_renderer import HTMLInfographicRenderer

# 2. Create Data
data = KeyMetricsDashboard(
    title="My Analysis",
    subtitle="Results",
    metrics=[
        MetricItem(value="75%", label="Score"),
        MetricItem(value="100", label="Items")
    ]
)

# 3. Render
renderer = HTMLInfographicRenderer()
result = renderer.render(data, "gradient_modern")

# 4. Done! ✨
print(f"Created: {result['path']}")
```

---

## 📦 What's Included

### **6 Data Schemas** (Pick what fits your data):
1. **Key Metrics Dashboard** - 2-6 KPIs/stats
2. **Comparison View** - Side-by-side A vs B
3. **Timeline/Progression** - Time-series data
4. **Ranking/Leaderboard** - Top N lists
5. **Hero Stat** - One big number + context
6. **Category Breakdown** - Geographic/demographic distribution

### **6 Visual Templates** (Pick the style you want):
1. **Gradient Modern** - Purple glassmorphism
2. **Minimalist Mono** - Black & white editorial
3. **Vibrant Cards** - Colorful gradient cards
4. **Neon Dark** - Cyberpunk cyan/magenta
5. **Clean Corporate** - Professional blue/white
6. **Playful Rounded** - Fun bubble design

### **= 36 Possible Combinations!**

---

## ✅ Installation (Already Done!)

```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2/backend_v2
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Installed Versions**:
- ✅ Pydantic: 2.11.9
- ✅ Pillow: 11.3.0
- ✅ MoviePy: 2.1.2
- ✅ python-pptx: 1.0.2

---

## 🎯 For Agents: How to Use

### **Step 1: Pick Your Schema**

```python
from infographic_schemas import (
    KeyMetricsDashboard,      # For KPIs, scores, statistics
    ComparisonView,           # For A vs B comparisons
    TimelineProgression,      # For time-series, trends
    RankingLeaderboard,       # For top N lists
    HeroStat,                 # For one big number
    CategoryBreakdown,        # For geographic/demographic
    MetricItem                # Helper for metrics
)
```

### **Step 2: Create Your Data**

```python
# Example: Sentiment Analyzer Agent
data = KeyMetricsDashboard(
    title="US Climate Policy Sentiment",
    subtitle="Real-time Analysis",
    metrics=[
        MetricItem(value="72%", label="Overall Support"),
        MetricItem(value="1.2M", label="Articles Analyzed"),
        MetricItem(value="+15%", label="Weekly Change")
    ],
    insight="Strong bipartisan support detected",
    footer="Sentiment Analyzer • Oct 2, 2025"
)
```

### **Step 3: Choose Visual Style**

```python
# Pick one:
template = "gradient_modern"     # Modern, premium
template = "minimalist_mono"     # Professional, editorial
template = "vibrant_cards"       # Colorful, social media
template = "neon_dark"           # Tech, cyberpunk
template = "clean_corporate"     # Business, formal
template = "playful_rounded"     # Fun, friendly
```

### **Step 4: Render**

```python
from html_infographic_renderer import HTMLInfographicRenderer

renderer = HTMLInfographicRenderer()
result = renderer.render(
    schema_data=data,
    visual_template=template
)

# Return as artifact
return {
    "artifacts": [result],
    "status": "complete"
}
```

---

## 🧪 Test It Now

```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2/backend_v2/shared

# Run the demo
python3 html_infographic_renderer.py

# Check output
ls -lh artifacts/infographic_*.html

# Open in browser
open artifacts/infographic_keymetricsdashboard_gradient_modern_*.html
```

---

## 📊 Example: Sentiment Analyzer Integration

```python
# In sentiment_analyzer/nodes/visualizer.py

def create_visualization(state):
    """Create sentiment analysis infographic"""
    
    from infographic_schemas import KeyMetricsDashboard, MetricItem
    from html_infographic_renderer import HTMLInfographicRenderer
    
    # Extract sentiment data from state
    sentiment_scores = state.get("sentiment_scores", {})
    article_count = state.get("article_count", 0)
    
    # Create schema data
    data = KeyMetricsDashboard(
        title=f"{state['query']} - Sentiment Analysis",
        subtitle="Multi-Source Analysis Results",
        metrics=[
            MetricItem(
                value=f"{sentiment_scores.get('overall', 0):.1%}",
                label="Overall Sentiment"
            ),
            MetricItem(
                value=str(article_count),
                label="Articles Analyzed"
            ),
            MetricItem(
                value=f"{sentiment_scores.get('positive', 0):.1%}",
                label="Positive Coverage"
            ),
            MetricItem(
                value=f"{sentiment_scores.get('negative', 0):.1%}",
                label="Negative Coverage"
            )
        ],
        insight=state.get("key_insight", "Analysis complete"),
        footer=f"Sentiment Analyzer • {datetime.now().strftime('%B %d, %Y')}"
    )
    
    # Render
    renderer = HTMLInfographicRenderer()
    result = renderer.render(
        schema_data=data,
        visual_template="gradient_modern"  # or user preference
    )
    
    # Update state
    state["artifacts"] = state.get("artifacts", []) + [result]
    
    return state
```

---

## 🎨 Schema Reference Card

| Schema | Fields | Use Case |
|--------|--------|----------|
| **KeyMetricsDashboard** | title, subtitle, metrics (2-6), insight | KPIs, scores, summaries |
| **ComparisonView** | title, subtitle, left_side, right_side, conclusion | A vs B, source comparison |
| **TimelineProgression** | title, subtitle, timeline_points (2-6), trend | Time-series, evolution |
| **RankingLeaderboard** | title, subtitle, ranked_items (2-10), methodology | Top N, credibility |
| **HeroStat** | title, hero_value, hero_label, supporting_stats, context | Big number announcement |
| **CategoryBreakdown** | title, subtitle, categories (2-8), insight | Geographic, demographic |

---

## 🔧 Validation is Automatic

```python
# ✅ This works
data = KeyMetricsDashboard(
    title="Test",
    subtitle="Test",
    metrics=[
        MetricItem(value="1", label="A"),
        MetricItem(value="2", label="B")
    ]
)

# ❌ This fails automatically (need min 2 metrics)
data = KeyMetricsDashboard(
    title="Test",
    subtitle="Test",
    metrics=[
        MetricItem(value="1", label="Only One")
    ]
)
# ValidationError: List should have at least 2 items after validation
```

---

## 📁 File Locations

```
backend_v2/shared/
├── infographic_schemas.py              ← Import schemas from here
├── html_infographic_renderer.py        ← Import renderer from here
├── templates/html_samples/             ← Visual templates (don't modify)
│   ├── template_1_gradient_modern.html
│   ├── template_2_minimalist_mono.html
│   ├── template_3_vibrant_cards.html
│   ├── template_4_neon_dark.html
│   ├── template_5_clean_corporate.html
│   └── template_6_playful_rounded.html
└── artifacts/                          ← Generated infographics go here
```

---

## 🚀 Next Steps

1. **Start Simple**: Use `KeyMetricsDashboard` for your first agent
2. **Pick a Style**: Try `gradient_modern` or `minimalist_mono`
3. **Test It**: Run your agent and check the output
4. **Iterate**: Try different schemas and templates
5. **Production**: Once happy, use in all your agents!

---

## 📚 Full Documentation

- **SCHEMA_SYSTEM_GUIDE.md** - Complete schema reference
- **TEMPLATE_CATALOG.md** - Visual template showcase
- **INFOGRAPHIC_SYSTEM_COMPLETE.md** - System architecture

---

## ✅ System Status

- [x] Dependencies installed
- [x] 6 schemas defined
- [x] 6 templates created
- [x] Renderer implemented
- [x] Validation working
- [x] Tests passing
- [x] Documentation complete
- [x] Examples working
- [x] Ready for production

---

**🎉 You're Ready to Create Beautiful Infographics! 🎉**

Start with:
```bash
python3 html_infographic_renderer.py
```

And watch the magic happen! ✨

