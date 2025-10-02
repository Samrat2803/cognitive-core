# Map Visualization Guide

## Overview

The master agent now has a **simple map chart tool** that works just like any other visualization tool (bar charts, line charts, etc.).

## How It Works

### ✅ Correct Approach

1. **User asks for sentiment analysis** → Sentiment analyzer runs and returns data (table + bar chart)
2. **User asks for a map** → Master agent calls `create_map_chart()` with the existing data

### ❌ Wrong Approach (What We Fixed)

- ~~Sentiment analyzer detects "map" keyword~~
- ~~Sentiment analyzer creates map during analysis~~
- ~~Complex state management for visualization requests~~

## Usage

### In Python Code

```python
from langgraph_master_agent.tools.visualization_tools import create_map_chart

# Simple usage
artifact = create_map_chart(
    data={
        "countries": ["US", "Israel", "UK"],
        "values": [-0.4, -0.7, 0.3],
        "labels": ["US: Negative", "Israel: Very Negative", "UK: Positive"]  # optional
    },
    title="Sentiment on Hamas",
    legend_title="Sentiment Score"
)

# Access files
print(artifact['html_path'])  # Interactive map
print(artifact['png_path'])   # Static image
print(artifact['data']['mapped_countries'])  # ['USA', 'ISR', 'GBR']
```

### In Chat

```
User: "sentiment analysis on Hamas in US and Israel"
Agent: [Runs sentiment analyzer] → Returns table + bar chart

User: "create a map visualization of this data"
Agent: [Calls create_map_chart with sentiment data] → Returns map
```

## Tool Signature

```python
def create_map_chart(
    data: Dict[str, Any],
    title: str = "Geographic Map",
    legend_title: str = "Score"
) -> Dict[str, Any]:
    """
    Args:
        data: 
            - countries: List[str] (e.g., ["US", "Israel"])
            - values: List[float] (e.g., [-0.4, -0.7])
            - labels: List[str] (optional, e.g., ["US: Negative"])
        title: Chart title
        legend_title: Legend/colorbar title
    
    Returns:
        artifact: Dict with html_path, png_path, artifact_id, etc.
    """
```

## Country Code Mapping

The tool automatically maps country names to ISO 3-letter codes:
- `"US"` → `"USA"`
- `"Israel"` → `"ISR"`
- `"United Kingdom"` → `"GBR"`
- `"China"` → `"CHN"`

See `shared/visualization_factory.py::COUNTRY_CODE_MAP` for full list.

## Benefits of This Approach

1. **Simple**: Just another visualization tool, no special logic needed
2. **Flexible**: Master agent controls what to visualize and when
3. **Reusable**: Can be used with ANY geographic data, not just sentiment
4. **No duplication**: Sentiment analyzer doesn't re-run to create a map

## Example Flow

```
Step 1: Sentiment Analysis
------------------------
User: "sentiment on Hamas in US, Israel, UK"

Agent:
  → Calls sentiment_analyzer
  → Returns: {
      sentiment_scores: {
        "US": {score: -0.4, sentiment: "negative"},
        "Israel": {score: -0.7, sentiment: "very negative"},
        "UK": {score: 0.3, sentiment: "positive"}
      },
      artifacts: [table, bar_chart]
    }

Step 2: Map Visualization
-----------------------
User: "show me a map of this"

Agent:
  → Extracts sentiment_scores from previous result
  → Calls create_map_chart({
      countries: ["US", "Israel", "UK"],
      values: [-0.4, -0.7, 0.3]
    })
  → Returns: artifact (map)
```

## No More Keyword Detection

The sentiment analyzer **no longer** detects keywords like "map" or "choropleth". It always creates:
- ✅ Data table (Excel export)
- ✅ Bar chart

If the user wants a map, the master agent handles it using the map tool.

## Testing

```bash
cd backend_v2 && source .venv/bin/activate

# Test map tool directly
python -c "
from langgraph_master_agent.tools.visualization_tools import create_map_chart

artifact = create_map_chart(
    {'countries': ['US', 'Israel'], 'values': [-0.4, -0.7]},
    'Sentiment Map'
)
print('Map created:', artifact['artifact_id'])
"
```

## Files Modified

1. `backend_v2/langgraph_master_agent/tools/visualization_tools.py`
   - Added `MapChartTool` class
   - Added `create_map_chart()` function

2. `backend_v2/shared/visualization_factory.py`
   - Already has `COUNTRY_CODE_MAP` and `get_country_code()`

3. `backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/`
   - Cleaned up (removed unnecessary map logic)
   - Still creates table + bar chart by default

## Summary

**Map visualization is now a simple, standalone tool that the master agent can call with data from ANY source, not just the sentiment analyzer.**

No special keywords, no complex state management, no duplication of work. ✅

