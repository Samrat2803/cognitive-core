# Sentiment Map Visualizer Implementation

**Date:** October 2, 2025  
**Status:** ✅ Complete

## Overview

Added geographic sentiment visualization capability to the sentiment analyzer. Users can now request an interactive choropleth map showing sentiment scores across countries.

---

## Implementation Details

### 1. Country Code Mapping (`shared/visualization_factory.py`)

**Added:** `COUNTRY_CODE_MAP` dictionary with 90+ country mappings
- Maps common country name variations to ISO 3-letter codes
- Supports abbreviations (US → USA, UK → GBR)
- Handles common variations (Britain → GBR, América → USA)
- Covers major regions: Americas, Europe, Middle East, Asia, Africa, Oceania

**Function:** `get_country_code(country_name: str) -> Optional[str]`
- Converts country names to ISO codes for map rendering
- Case-insensitive matching
- Returns `None` for unknown countries (graceful degradation)

### 2. Map Creation Function

**Function:** `create_sentiment_map(country_scores, query, output_dir)`
- Creates interactive Plotly choropleth map
- Color-coded by sentiment score (Red-Yellow-Green scale)
- Automatically converts country names to ISO codes
- Skips countries without valid ISO codes with warnings
- Returns artifact metadata with mapped/skipped country lists

### 3. Integration with Sentiment Analyzer

**File:** `backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/nodes/visualizer.py`
- Added map as optional user-requested visualization
- Triggered by keywords: "map" or "choropleth"
- Example query: *"show me a map of sentiment analysis"*

---

## Features

✅ **Automatic Country Mapping**
- Handles 90+ countries with common name variations
- Gracefully handles unmappable countries

✅ **Interactive Visualization**
- Hover tooltips show country name and sentiment score
- Color gradient from red (negative) to green (positive)
- Natural Earth projection for better geographic representation

✅ **Error Handling**
- Warns when countries can't be mapped to ISO codes
- Continues with valid countries if some are skipped
- Returns error artifact if NO countries can be mapped

✅ **Metadata Tracking**
- Lists successfully mapped countries
- Lists skipped countries (for debugging)
- Includes annotations with sentiment details

---

## Usage

### Default Behavior (Always Created)
```
Query: "sentiment analysis on Israel in US and UK"
```
**Creates:**
1. Data Table (Excel export)
2. Bar Chart

### Request Map Visualization
```
Query: "sentiment analysis on Israel in US, UK, Germany. Show me a map."
```
**Creates:**
1. Data Table (Excel export)
2. Bar Chart
3. **Sentiment Map** (choropleth)

### Via State Parameter
```python
state["requested_visualizations"] = ["map"]  # or ["choropleth"]
```

---

## Technical Stack

- **Plotly** `go.Choropleth` for map rendering
- **ISO 3166-1 alpha-3** country codes (USA, GBR, ISR, etc.)
- **RdYlGn** color scale (Red-Yellow-Green)
- **Natural Earth** projection

---

## Testing

```bash
✅ Country code mapping: 7/7 tests passed
✅ Map creation with 5 countries: SUCCESS
✅ HTML artifact generated
✅ Mapped countries: ['USA', 'ISR', 'GBR', 'DEU', 'FRA']
✅ Graceful handling of invalid countries
```

---

## Example Country Codes

| Input | ISO Code |
|-------|----------|
| US, USA, United States | USA |
| UK, United Kingdom, Britain | GBR |
| Israel | ISR |
| Germany, Deutschland | DEU |
| France | FRA |
| China, PRC | CHN |
| Iran | IRN |

---

## Future Enhancements (Optional)

- [ ] Add regional zoom (Middle East, Europe, etc.)
- [ ] Support custom color scales per user preference
- [ ] Add click interactions to show detailed breakdown
- [ ] Support sub-region analysis (US states, EU countries)

---

## Files Modified

1. `backend_v2/shared/visualization_factory.py`
   - Added `COUNTRY_CODE_MAP` (90+ mappings)
   - Added `get_country_code()` function
   - Added `create_sentiment_map()` convenience function

2. `backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/nodes/visualizer.py`
   - Imported `create_sentiment_map`
   - Added map creation in optional visualizations section

---

## Supported Regions

- ✅ **North America** (US, Canada, Mexico)
- ✅ **Europe** (25+ countries)
- ✅ **Middle East** (Israel, Iran, Saudi Arabia, UAE, etc.)
- ✅ **Asia** (China, Japan, India, Korea, etc.)
- ✅ **South America** (Brazil, Argentina, Chile, etc.)
- ✅ **Africa** (South Africa, Nigeria, Kenya, etc.)
- ✅ **Oceania** (Australia, New Zealand)
- ✅ **Russia & Former USSR** (Russia, Ukraine, Belarus)

---

## Map Visualizer Complete! 🗺️✨

