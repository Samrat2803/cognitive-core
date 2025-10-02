# Visualization Tools Documentation

Complete guide to creating professional, template-based visualizations for the Political Analyst Agent.

## Overview

The visualization tools provide three core chart types with automatic styling, template-based design, and export to both HTML (interactive) and PNG (static) formats.

## Quick Start

```python
from langgraph_master_agent.tools.visualization_tools import (
    create_bar_chart,
    create_line_chart,
    create_mind_map,
    auto_visualize
)

# Simple bar chart
artifact = create_bar_chart(
    data={"categories": ["US", "EU", "China"], "values": [85, 72, 45]},
    title="Global Sentiment"
)

# Access files
print(artifact['html_path'])  # artifacts/bar_xxx.html
print(artifact['png_path'])   # artifacts/bar_xxx.png
```

## Chart Types

### 1. Bar Chart

**Use for:** Categorical + Numerical data, comparisons, rankings

**Data Format:**
```python
{
    "categories": ["Category1", "Category2", "Category3"],
    "values": [10, 20, 15]
}
```

**Example:**
```python
from langgraph_master_agent.tools.visualization_tools import create_bar_chart

# Country sentiment scores
data = {
    "categories": ["United States", "European Union", "China", "India", "Brazil"],
    "values": [85, 72, 45, 60, 55]
}

artifact = create_bar_chart(
    data=data,
    title="Global Climate Policy Sentiment",
    x_label="Country/Region",
    y_label="Sentiment Score (%)",
    template="professional"  # or "colorful", "minimal"
)

# Files created:
# - artifacts/bar_xxxxx.html (interactive Plotly chart)
# - artifacts/bar_xxxxx.png (1200x600px static image)
```

**Templates:**
- `professional`: Single blue color (default)
- `colorful`: Multi-color palette
- `minimal`: Gray neutral tones

---

### 2. Line Chart

**Use for:** Trends, time-series, progression analysis

**Data Format:**
```python
# Single series
{
    "x": ["2020", "2021", "2022", "2023"],
    "y": [10, 15, 13, 17]
}

# Multiple series
{
    "x": ["Jan", "Feb", "Mar"],
    "series": [
        {"name": "Series 1", "y": [10, 15, 13]},
        {"name": "Series 2", "y": [12, 14, 16]}
    ]
}
```

**Example:**
```python
from langgraph_master_agent.tools.visualization_tools import create_line_chart

# India GDP growth
data = {
    "x": ["2020", "2021", "2022", "2023", "2024", "2025"],
    "y": [-5.78, 9.69, 6.99, 8.15, 7.5, 7.8]
}

artifact = create_line_chart(
    data=data,
    title="India GDP Growth Rate (2020-2025)",
    x_label="Year",
    y_label="Growth Rate (%)",
    template="professional"
)
```

**Multi-Series Example:**
```python
# Compare multiple countries
data = {
    "x": ["Q1", "Q2", "Q3", "Q4"],
    "series": [
        {"name": "US", "y": [2.3, 2.5, 2.7, 2.9]},
        {"name": "China", "y": [5.1, 5.3, 5.0, 5.2]},
        {"name": "India", "y": [6.5, 7.0, 7.2, 7.5]}
    ]
}

artifact = create_line_chart(data, title="Quarterly GDP Growth Comparison")
```

---

### 3. Mind Map

**Use for:** Concepts, hierarchies, relationships, structures

**Data Format:**
```python
{
    "root": "Main Concept",
    "children": [
        {
            "name": "Sub-Concept 1",
            "value": 10,
            "children": [
                {"name": "Detail 1.1", "value": 5},
                {"name": "Detail 1.2", "value": 5}
            ]
        },
        {
            "name": "Sub-Concept 2",
            "value": 15
        }
    ]
}
```

**Example:**
```python
from langgraph_master_agent.tools.visualization_tools import create_mind_map

# Political analysis framework
data = {
    "root": "Political Analysis",
    "children": [
        {
            "name": "Data Collection",
            "value": 10,
            "children": [
                {"name": "Web Search", "value": 5},
                {"name": "Source Verification", "value": 5}
            ]
        },
        {
            "name": "Analysis",
            "value": 15,
            "children": [
                {"name": "Sentiment Analysis", "value": 8},
                {"name": "Bias Detection", "value": 7}
            ]
        },
        {
            "name": "Reporting",
            "value": 8,
            "children": [
                {"name": "Visualizations", "value": 4},
                {"name": "Documents", "value": 4}
            ]
        }
    ]
}

artifact = create_mind_map(
    data=data,
    title="Political Analysis Framework"
)
```

**Implementation Details:**
- Uses **Graphviz/pydot** for true hierarchical layout (if available)
- Falls back to **Plotly treemap** if Graphviz binary not installed
- Automatic color coding by depth level
- Supports unlimited nesting

---

## Auto-Detection

The system can automatically choose the best chart type based on context:

```python
from langgraph_master_agent.tools.visualization_tools import auto_visualize

# Agent automatically detects chart type from context
artifact = auto_visualize(
    data=your_data,
    context="Show me the trend over time",  # → Line chart
    title="Auto-Generated Visualization"
)

# Detection keywords:
# - "trend", "over time", "timeline" → Line chart
# - "compare", "versus", "comparison" → Bar chart  
# - "concept", "hierarchy", "structure" → Mind map
# - Default → Bar chart
```

---

## Return Format

All functions return the same artifact structure:

```python
{
    "artifact_id": "bar_abc123def456",    # Unique identifier
    "type": "bar_chart",                  # Chart type
    "title": "My Chart Title",            # Chart title
    "html_path": "artifacts/bar_xxx.html", # Interactive HTML
    "png_path": "artifacts/bar_xxx.png",   # Static PNG
    "data": {...},                        # Original data
    "created_at": "2025-10-01T12:00:00Z"  # ISO timestamp
}
```

---

## Integration with Agent

### Artifact Decision Node

The agent automatically detects when to create visualizations:

```python
# User queries that trigger artifact creation:
"Create a bar chart of sentiment scores"
"Visualize the trend over time"
"Show me a mind map of concepts"
"Generate a graph comparing countries"

# Agent detects keywords:
# - "chart", "graph", "visualize", "plot" → Create artifact
# - "trend", "over time" → Line chart
# - "concept", "hierarchy", "mind" → Mind map
# - Default → Bar chart
```

### Manual Artifact Request

```python
from langgraph_master_agent.nodes.artifact_creator import artifact_creator

state = {
    "artifact_type": "line_chart",
    "artifact_data": {
        "x": ["2020", "2021", "2022"],
        "y": [10, 15, 13]
    },
    "current_message": "GDP growth trend"
}

result = await artifact_creator(state)
artifact = result['artifact']
```

---

## Styling & Templates

### Color Palette

```python
COLORS = {
    "primary": "#2E86AB",      # Blue - main data
    "secondary": "#A23B72",    # Purple - secondary series
    "accent": "#F18F01",       # Orange - highlights
    "success": "#06A77D",      # Green - positive values
    "warning": "#F77F00",      # Dark Orange - warnings
    "danger": "#D62828",       # Red - negative values
    "neutral": "#6C757D"       # Gray - neutral/minimal
}
```

### Font & Layout

```python
THEME = {
    "font_family": "Arial, sans-serif",
    "title_font_size": 18,
    "axis_font_size": 12,
    "background_color": "#FFFFFF",
    "grid_color": "#E5E5E5"
}
```

### Custom Styling

To modify templates, edit `VisualizationTemplates` class:

```python
# In visualization_tools.py

class VisualizationTemplates:
    COLORS = {
        "primary": "#YOUR_COLOR",  # Change colors here
        # ...
    }
    
    THEME = {
        "font_family": "Your Font",  # Change fonts here
        # ...
    }
```

---

## File Output

### HTML Files
- **Interactive Plotly charts**
- Can be embedded in web pages
- Support hover tooltips
- Zoom/pan functionality
- Size: ~50KB - 500KB

### PNG Files
- **Static images**
- 1200x600px (bar/line) or 1200x800px (mind map)
- High-resolution for presentations
- Transparent background option
- Size: ~50KB - 200KB

### Storage Location
```
Political_Analyst_Workbench/
└── artifacts/
    ├── bar_abc123.html
    ├── bar_abc123.png
    ├── line_def456.html
    ├── line_def456.png
    ├── mindmap_ghi789.html
    └── mindmap_ghi789.png
```

---

## Advanced Usage

### Batch Creation

```python
charts = []

for dataset in my_datasets:
    artifact = create_bar_chart(
        data=dataset,
        title=f"Analysis: {dataset['name']}"
    )
    charts.append(artifact)
```

### Error Handling

```python
try:
    artifact = create_line_chart(data, title="My Chart")
    print(f"Created: {artifact['artifact_id']}")
except Exception as e:
    print(f"Chart creation failed: {e}")
    # Fallback to text-only response
```

### Data Validation

```python
def validate_bar_data(data):
    """Ensure data format is correct"""
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    
    if "categories" not in data or "values" not in data:
        raise ValueError("Data must have 'categories' and 'values'")
    
    if len(data["categories"]) != len(data["values"]):
        raise ValueError("Categories and values must have same length")
    
    return True

# Use before creating chart
if validate_bar_data(my_data):
    artifact = create_bar_chart(my_data)
```

---

## Dependencies

Required packages:
```bash
pip install plotly         # Charts
pip install kaleido        # PNG export
pip install pydot          # Mind maps (optional)
pip install graphviz       # Mind maps (optional)
```

System dependencies (for mind maps):
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows
choco install graphviz
```

---

## Troubleshooting

### PNG Export Fails

**Error:** `ValueError: Image export using the "kaleido" engine requires kaleido to be installed`

**Solution:**
```bash
pip install -U kaleido
```

### Mind Map Shows Treemap Instead

**Reason:** Graphviz binary not installed (fallback to Plotly treemap)

**Solution:**
```bash
# Install Graphviz system package
brew install graphviz  # macOS

# Then verify
dot -V  # Should show version
```

### Charts Look Different

**Reason:** Template/style settings

**Solution:** Explicitly set template:
```python
artifact = create_bar_chart(data, template="professional")
```

---

## Best Practices

### 1. Data Preparation
```python
# ✅ Good: Clean, labeled data
data = {
    "categories": ["United States", "China", "India"],
    "values": [85, 72, 60]
}

# ❌ Bad: Unclear labels
data = {
    "categories": ["US", "CN", "IN"],  # Too short
    "values": [0.85, 0.72, 0.60]       # Inconsistent scale
}
```

### 2. Title Clarity
```python
# ✅ Good: Descriptive title
title="Global Climate Policy Sentiment by Country (2025)"

# ❌ Bad: Vague title
title="Chart"
```

### 3. Limit Data Points
```python
# ✅ Good: Readable number of bars
data = {"categories": [...], "values": [...]}  # 5-10 items

# ❌ Bad: Too many bars
data = {"categories": [...], "values": [...]}  # 50+ items (use line chart)
```

### 4. Choose Right Chart Type
- **Comparison** → Bar chart
- **Trends** → Line chart
- **Hierarchy** → Mind map
- **Proportions** → Consider adding pie chart tool

---

## Examples Gallery

### Political Sentiment Analysis
```python
artifact = create_bar_chart(
    data={
        "categories": ["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"],
        "values": [12, 35, 28, 18, 7]
    },
    title="Public Sentiment Distribution on Healthcare Reform",
    y_label="Percentage (%)"
)
```

### Economic Indicators
```python
artifact = create_line_chart(
    data={
        "x": ["Q1 2023", "Q2 2023", "Q3 2023", "Q4 2023", "Q1 2024"],
        "series": [
            {"name": "GDP Growth", "y": [2.3, 2.5, 2.7, 2.9, 3.1]},
            {"name": "Unemployment", "y": [5.5, 5.3, 5.1, 4.9, 4.7]}
        ]
    },
    title="Key Economic Indicators"
)
```

### Policy Framework
```python
artifact = create_mind_map(
    data={
        "root": "Climate Policy Framework",
        "children": [
            {"name": "Mitigation", "value": 10},
            {"name": "Adaptation", "value": 8},
            {"name": "Finance", "value": 12},
            {"name": "Technology", "value": 9}
        ]
    },
    title="Climate Action Components"
)
```

---

## API Reference

### create_bar_chart()
```python
create_bar_chart(
    data: Dict[str, List],
    title: str = "Bar Chart Analysis",
    x_label: str = "Category",
    y_label: str = "Value",
    template: str = "professional"
) -> Dict[str, Any]
```

### create_line_chart()
```python
create_line_chart(
    data: Dict[str, List],
    title: str = "Trend Analysis",
    x_label: str = "Time",
    y_label: str = "Value",
    template: str = "professional"
) -> Dict[str, Any]
```

### create_mind_map()
```python
create_mind_map(
    data: Dict[str, Any],
    title: str = "Concept Mind Map",
    template: str = "professional"
) -> Dict[str, Any]
```

### auto_visualize()
```python
auto_visualize(
    data: Dict[str, Any],
    context: str = "",
    title: Optional[str] = None
) -> Dict[str, Any]
```

---

## Future Enhancements

Planned features:
- [ ] Pie/Donut charts
- [ ] Scatter plots
- [ ] Heatmaps
- [ ] Network graphs
- [ ] Geographic maps
- [ ] Custom color palettes
- [ ] Animation support
- [ ] PDF export

---

**Version:** 1.0  
**Last Updated:** October 1, 2025  
**Maintainer:** Political Analyst Workbench Team

