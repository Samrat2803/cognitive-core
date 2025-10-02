# Sentiment Analyzer Enhancement Plan

## 📋 Overview

This plan details enhancements to `backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer` to:
1. ✅ Verify POC methodology compliance
2. 🗺️ Add Map Visualizer for sentiment maps
3. 📊 Add Table Visualizer with Excel export
4. 🎨 Change from 3 default visualizations to 1 + user choice

---

## 🔍 Part 1: POC Methodology Compliance Check

### Current Implementation vs POC

#### ✅ COMPLIANT (Already Following POC)
1. **Async Processing** - Using `async/await` throughout
2. **Temperature = 0** - LLM calls use temperature=0
3. **Multi-country Search** - Tavily country-specific searches
4. **Sentiment Scoring** - GPT-4o-mini with structured output
5. **Bias Detection** - 7 bias types analyzed
6. **Metadata Extraction** - Source type, credibility, dates
7. **Trimmed Mean Aggregation** - Robust country-level scores
8. **JSON/CSV Output** - Both formats supported

#### ⚠️ GAPS (Need to Add from POC)
1. **Bias Severity Scoring (0-1)** - POC has this, we don't
2. **Bias Notes/Explanations** - POC provides detailed bias reasoning
3. **Reasoning Field** - POC includes LLM reasoning for each sentiment score
4. **Source Type Classification** - POC classifies as govt/media/political_party/encyclopedia/other
5. **Recent-Only Aggregation** - POC has 30-day recent sentiment calculation
6. **Domain Extraction** - POC extracts domains from URLs for analysis
7. **CSV Export with All Metadata** - POC creates comprehensive CSV exports

### Files to Modify for POC Compliance
- `nodes/sentiment_scorer.py` - Add reasoning, source_type, date_published to LLM prompt
- `nodes/bias_detector.py` - Add bias_severity (0-1) and bias_notes fields
- `state.py` - Update schema to include new fields
- `nodes/synthesizer.py` - Include new metadata in synthesis

---

## 🗺️ Part 2: Add Map Visualizer

### Implementation Strategy

#### File: `backend_v2/shared/visualization_factory.py`

**Function to Add:**
```python
def create_sentiment_map(
    country_scores: Dict[str, Dict[str, Any]],
    query: str,
    output_dir: str,
    annotation_text: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Create annotated sentiment map with country-level sentiment scores
    
    Args:
        country_scores: {country: {score: float, sentiment: str, ...}}
        query: Query text for title
        output_dir: Where to save artifacts
        annotation_text: Optional custom annotations per country
    
    Returns:
        Artifact metadata dict with paths
    """
```

**Features:**
1. **Interactive Choropleth Map** - World map colored by sentiment
2. **Hover Tooltips** - Show country name, score, sentiment category
3. **Custom Annotations** - Optional text labels on countries
4. **Color Scale** - RdYlGn (Red=Negative, Yellow=Neutral, Green=Positive)
5. **ISO-3 Country Codes** - Auto-convert common names to codes (US→USA, UK→GBR)
6. **Export Formats** - Both HTML (interactive) and PNG (static)

**Map Features:**
- Natural Earth projection
- White country borders
- Color bar with sentiment scale (-1 to +1)
- Zoom/pan capabilities in HTML version
- Annotations for significant countries

#### Country Code Mapping Helper
Create helper function to convert country names to ISO-3 codes:
```python
COUNTRY_CODE_MAP = {
    "US": "USA", "USA": "USA", "United States": "USA",
    "UK": "GBR", "United Kingdom": "GBR", "Britain": "GBR",
    "France": "FRA", "Germany": "DEU", "Japan": "JPN",
    "China": "CHN", "India": "IND", "Russia": "RUS",
    # ... comprehensive mapping
}
```

#### Integration Points
1. `nodes/visualizer.py` - Add map creation as option
2. Master agent's artifact decision node - Suggest map for geo-sentiment queries
3. Frontend - Display map in artifact viewer

---

## 📊 Part 3: Add Table Visualizer with Excel Export

### Implementation Strategy

#### File: `backend_v2/shared/visualization_factory.py`

**Function to Add:**
```python
def create_sentiment_table(
    country_scores: Dict[str, Dict[str, Any]],
    articles: List[Dict[str, Any]],
    query: str,
    output_dir: str,
    bias_analysis: Optional[Dict[str, Dict]] = None
) -> Dict[str, Any]:
    """
    Create comprehensive data table with Excel export
    
    Creates 3 sheets:
    1. Country Summary - Aggregated sentiment by country
    2. Article Details - Individual article analysis
    3. Bias Analysis - Bias detection results
    
    Args:
        country_scores: {country: {score, sentiment, ...}}
        articles: List of article dicts with sentiment/bias data
        query: Query text
        output_dir: Where to save files
        bias_analysis: Optional bias detection results
    
    Returns:
        Artifact metadata with Excel/JSON/HTML paths
    """
```

**Excel Structure (3 Sheets):**

**Sheet 1: Country Summary**
| Country | Sentiment Score | Sentiment | Articles | Avg Credibility | Recent (30d) | Bias Types |
|---------|-----------------|-----------|----------|-----------------|--------------|------------|
| USA     | 0.65           | Positive  | 20       | 0.82            | 85%          | 2          |
| UK      | -0.32          | Negative  | 18       | 0.78            | 90%          | 3          |

**Sheet 2: Article Details**
| Country | Title | URL | Sentiment | Source Type | Date | Credibility | Bias Type | Bias Severity |
|---------|-------|-----|-----------|-------------|------|-------------|-----------|---------------|

**Sheet 3: Bias Analysis**
| Country | Bias Type | Severity | Count | Examples | Notes |
|---------|-----------|----------|-------|----------|-------|

**Additional Exports:**
1. **Excel (.xlsx)** - Full multi-sheet workbook using `openpyxl` or `pandas`
2. **CSV Bundle** - 3 separate CSV files zipped together
3. **JSON** - Complete structured data
4. **HTML Table** - Interactive table view with sorting/filtering

#### Required Libraries
```
openpyxl  # Excel file creation
pandas    # DataFrame operations
```

#### HTML Table Features
- **Sortable columns** - Click headers to sort
- **Search/filter** - Filter by country, sentiment, etc.
- **Pagination** - Handle large datasets
- **Download button** - Trigger Excel download from HTML
- **Responsive design** - Mobile-friendly

#### Integration Points
1. `nodes/visualizer.py` - Add table creation as option
2. Frontend - Add download button for Excel
3. API endpoint - Serve Excel files with proper MIME type

---

## 🎨 Part 4: User-Controlled Visualization Selection

### Current Behavior (❌ Issue)
```python
# In visualizer.py - Creates 3 artifacts by default
artifacts = []
artifacts.append(create_sentiment_bar_chart(...))      # Always created
artifacts.append(create_sentiment_radar_chart(...))    # Always created
artifacts.append(save_json_export(...))                # Always created
```

### New Behavior (✅ Solution)

#### Changes to State Schema
**File:** `backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/state.py`

```python
class SentimentAnalyzerState(TypedDict):
    # ... existing fields ...
    
    # NEW FIELDS for visualization control
    requested_visualizations: List[str]  # User-specified viz types
    default_visualizations: List[str]    # Default viz to create
    available_visualizations: List[str]  # What's available
```

#### Visualization Types
```python
AVAILABLE_VISUALIZATIONS = {
    "bar_chart": "Sentiment Bar Chart",
    "radar_chart": "Multi-Country Radar",
    "map": "Sentiment World Map",
    "table": "Data Table (Excel)",
    "json": "JSON Data Export",
    "timeline": "Sentiment Timeline (future)",
    "heatmap": "Bias Heatmap (future)"
}

DEFAULT_VISUALIZATIONS = ["table", "bar_chart"]  # Always create these 2 by default
```

#### Implementation: Modified Visualizer Node
**File:** `nodes/visualizer.py`

```python
async def visualizer(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Generate artifacts based on user selection or default"""
    
    sentiment_scores = state["sentiment_scores"]
    query = state["query"]
    requested = state.get("requested_visualizations", [])
    artifacts = []
    
    # If no specific request, create DEFAULT visualizations (table + bar chart)
    if not requested:
        requested = DEFAULT_VISUALIZATIONS  # ["table", "bar_chart"]
        print(f"🎨 No visualization requested, creating defaults: {', '.join(requested)}")
    else:
        print(f"🎨 Creating {len(requested)} requested visualizations")
    
    # Create only requested visualizations
    viz_creators = {
        "bar_chart": create_bar_chart_artifact,
        "radar_chart": create_radar_chart_artifact,
        "map": create_map_artifact,
        "table": create_table_artifact,
        "json": create_json_artifact
    }
    
    for viz_type in requested:
        if viz_type in viz_creators:
            try:
                artifact = viz_creators[viz_type](
                    sentiment_scores, query, output_dir, state
                )
                artifacts.append(artifact)
                print(f"   ✅ Created {viz_type}")
            except Exception as e:
                print(f"   ❌ Error creating {viz_type}: {e}")
    
    return {"artifacts": artifacts, ...}
```

#### User Interaction Flow

**Option A: Default Behavior (No Request)**

User query without specific visualization request:
- "Analyze sentiment on nuclear energy"
- "What's the sentiment on climate change in Europe?"

→ Creates **Table + Bar Chart** by default (2 visualizations)

**Option B: Via Master Agent (Additional Visualizations)**

User query requesting additional visualizations:
- "Analyze sentiment and **also show me a map**"
- "Give me the **radar chart** too"
- "Show **all visualizations**"

Master agent's artifact decision node parses intent and sets `requested_visualizations`.

**Option C: Via API Parameter**

```python
# API Request with specific visualizations
POST /api/agent/analyze
{
    "query": "nuclear energy sentiment",
    "countries": ["US", "France", "Germany"],
    "visualizations": ["map", "radar_chart"]  # Adds to defaults (table + bar)
}
# Returns: table, bar_chart, map, radar_chart (4 artifacts)

# API Request with defaults only
POST /api/agent/analyze
{
    "query": "nuclear energy sentiment",
    "countries": ["US", "France", "Germany"]
    # No "visualizations" parameter
}
# Returns: table, bar_chart (2 artifacts - defaults)
```

**Option D: Frontend UI Checkboxes**

```
Default Visualizations (Always Created):
☑ Data Table (Excel)
☑ Bar Chart

Additional Visualizations (Optional):
☐ Radar Chart
☐ World Map
☐ JSON Export

[Generate Additional Visualizations]
```

---

## 📁 Files to Modify/Create

### Files to Modify

1. **`backend_v2/shared/visualization_factory.py`**
   - Add `create_sentiment_map()` function
   - Add `create_sentiment_table()` function
   - Add country code mapping helper
   - ~200 lines of new code

2. **`backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/state.py`**
   - Add `requested_visualizations: List[str]`
   - Add `default_visualization: str`
   - Add POC compliance fields (reasoning, bias_notes, etc.)
   - ~10 lines modified

3. **`backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/nodes/visualizer.py`**
   - Complete rewrite to support dynamic visualization selection
   - Add individual creator functions for each viz type
   - ~150 lines (from 100 lines)

4. **`backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/nodes/sentiment_scorer.py`**
   - Update LLM prompt to include reasoning field (POC compliance)
   - Add source_type and date_published extraction
   - ~20 lines modified

5. **`backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/nodes/bias_detector.py`**
   - Add bias_severity scoring (0-1)
   - Add bias_notes field with explanations
   - ~30 lines modified

6. **`backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/config.py`**
   - Add visualization configuration
   - Add country code mappings
   - ~30 lines added

7. **`backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/README.md`**
   - Document new visualization options
   - Add usage examples
   - Update artifact list
   - ~50 lines added

### Files to Create

8. **`backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/utils/country_codes.py`**
   - Comprehensive country name → ISO-3 code mapping
   - ~150 lines (data file)

9. **`backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/tests/test_visualizations.py`**
   - Unit tests for new map and table visualizers
   - ~100 lines

10. **`backend_v2/requirements.txt`** (update)
    - Add: `openpyxl` (Excel export)
    - Add: `pandas` (if not already there)

---

## 🧪 Testing Strategy

### Unit Tests

1. **Map Visualizer Tests**
   - Test with 3 countries (US, UK, France)
   - Test with 20+ countries (full world map)
   - Test country code conversion
   - Test color scale correctness
   - Test annotation rendering

2. **Table Visualizer Tests**
   - Test Excel file creation (3 sheets)
   - Test CSV export
   - Test JSON export
   - Test HTML table rendering
   - Test with 0 articles (edge case)
   - Test with 100+ articles (performance)

3. **Visualization Selection Tests**
   - Test default (single bar chart)
   - Test single custom selection
   - Test multiple selections
   - Test invalid selection (should skip gracefully)
   - Test "all" option

### Integration Tests

1. **End-to-End Test**
   ```python
   query = "nuclear energy policy"
   countries = ["US", "France", "Germany"]
   visualizations = ["map", "table"]
   
   result = await run_sentiment_analyzer(query, countries, visualizations)
   
   assert len(result["artifacts"]) == 2
   assert result["artifacts"][0]["type"] == "sentiment_map"
   assert result["artifacts"][1]["type"] == "sentiment_table"
   assert os.path.exists(result["artifacts"][1]["excel_path"])
   ```

2. **POC Compliance Test**
   - Run same query as POC (`geo_sentiment_poc.py`)
   - Compare outputs: sentiment scores, bias detection, metadata
   - Verify all POC fields are present

### Manual Testing

1. Test map with 5 countries
2. Download Excel and verify all 3 sheets
3. Test in frontend artifact viewer
4. Test with mobile device (responsive)

---

## 📊 Implementation Timeline

### Phase 1: POC Compliance (2 hours)
- [ ] Update `sentiment_scorer.py` for reasoning field
- [ ] Update `bias_detector.py` for severity/notes
- [ ] Update state schema
- [ ] Test compliance with POC

### Phase 2: Map Visualizer (3 hours)
- [ ] Create `create_sentiment_map()` in shared factory
- [ ] Add country code mapping utility
- [ ] Integrate into visualizer node
- [ ] Write unit tests
- [ ] Test with 5 and 20 countries

### Phase 3: Table Visualizer (4 hours)
- [ ] Create `create_sentiment_table()` in shared factory
- [ ] Implement Excel export with 3 sheets
- [ ] Create HTML table view
- [ ] Add CSV bundle option
- [ ] Write unit tests

### Phase 4: Dynamic Visualization Selection (2 hours)
- [ ] Modify visualizer node for dynamic selection
- [ ] Update state schema
- [ ] Create visualization config
- [ ] Test default (single) behavior
- [ ] Test multiple selections

### Phase 5: Testing & Documentation (2 hours)
- [ ] Write comprehensive tests
- [ ] Update README
- [ ] Add usage examples
- [ ] Test in frontend
- [ ] Performance testing

**Total Estimated Time: 13 hours**

---

## 🎯 Success Criteria

### POC Compliance
- ✅ All POC fields present in output
- ✅ Bias severity and notes included
- ✅ Reasoning for sentiment scores
- ✅ Source type classification

### Map Visualizer
- ✅ Interactive world map generated
- ✅ Country colors match sentiment
- ✅ Hover tooltips work
- ✅ Both HTML and PNG exported
- ✅ Works with 3-50 countries

### Table Visualizer
- ✅ Excel file with 3 sheets generated
- ✅ All metadata included
- ✅ File downloads correctly from frontend
- ✅ CSV bundle option works
- ✅ HTML table is sortable/filterable

### Dynamic Selection
- ✅ Only 1 viz created by default (bar chart)
- ✅ User can request specific viz types
- ✅ Multiple selections work
- ✅ No breaking changes to existing code
- ✅ Frontend supports selection UI

---

## ⚠️ Risks & Mitigations

### Risk 1: Country Code Mapping
**Problem:** Country names vary (US, USA, United States)
**Mitigation:** Comprehensive mapping dictionary + fuzzy matching fallback

### Risk 2: Excel File Size
**Problem:** Large datasets might create huge Excel files
**Mitigation:** Pagination (max 1000 rows per sheet), offer CSV for large datasets

### Risk 3: Frontend Compatibility
**Problem:** New viz types might not render correctly
**Mitigation:** Use existing artifact viewer structure, add fallbacks

### Risk 4: Breaking Changes
**Problem:** Changing default behavior might break existing workflows
**Mitigation:** Keep backwards compatibility, default to "all" if state field missing

### Risk 5: Performance
**Problem:** Creating multiple visualizations might be slow
**Mitigation:** Run viz creation in parallel (asyncio.gather), cache country codes

---

## 🔄 Backwards Compatibility

To ensure no breaking changes:

1. **State Field Defaults**
   ```python
   requested = state.get("requested_visualizations", None)
   if requested is None:
       # Old behavior: create default only
       requested = [DEFAULT_VISUALIZATION]
   ```

2. **API Compatibility**
   - Old API calls without `visualizations` param → create default
   - New API calls with param → create requested ones

3. **Master Agent Integration**
   - If master agent doesn't set `requested_visualizations` → default behavior
   - If master agent sets it → new behavior

---

## 📝 Example Usage

### Before (Current)
```python
# Always creates 3 visualizations
result = await run_sentiment_analyzer("nuclear energy", ["US", "UK", "France"])
assert len(result["artifacts"]) == 3  # bar, radar, json
```

### After (New)
```python
# Option 1: Default (2 visualizations - table + bar chart)
result = await run_sentiment_analyzer("nuclear energy", ["US", "UK", "France"])
assert len(result["artifacts"]) == 2  # table and bar chart

# Option 2: Request additional visualizations (adds to defaults)
result = await run_sentiment_analyzer(
    "nuclear energy", 
    ["US", "UK", "France"],
    visualizations=["map", "radar_chart"]
)
assert len(result["artifacts"]) == 4  # table, bar_chart, map, radar_chart

# Option 3: All visualizations
result = await run_sentiment_analyzer(
    "nuclear energy", 
    ["US", "UK", "France"],
    visualizations=["bar_chart", "radar_chart", "map", "table", "json"]
)
assert len(result["artifacts"]) == 5  # all viz types (table + bar already included)
```

---

## 📦 Deliverables

1. ✅ POC-compliant sentiment analyzer
2. 🗺️ Interactive world map visualizer
3. 📊 Excel table exporter (3 sheets)
4. 🎨 User-controlled viz selection
5. 📚 Updated documentation
6. 🧪 Comprehensive test suite
7. 🎥 Demo video showing new features

---

## 🚀 Next Steps After Approval

1. **Confirm Priorities**
   - Which part should we implement first?
   - Any modifications to the plan?

2. **Set Up Environment**
   - Install openpyxl: `uv pip install openpyxl`
   - Verify pandas is installed

3. **Create Feature Branch**
   ```bash
   cd backend_v2
   git checkout -b feature/sentiment-viz-enhancements
   ```

4. **Start Implementation**
   - Begin with Phase 1 (POC compliance)
   - Then Phase 2, 3, 4, 5 sequentially

---

## 💬 Questions for Clarification

1. **Map Annotations**: Should we automatically annotate countries with extreme sentiment (±0.7+), or let user specify?

2. **Excel Styling**: Should the Excel file have formatting (colors, bold headers, borders)?

3. **Default Visualization**: Do you prefer `bar_chart` as default, or should it be `map` for geo-sentiment queries?

4. **Frontend Changes**: Should we also modify Frontend_v2 to add visualization selection UI, or just backend API?

5. **POC Data**: Should we backfill existing sentiment analyzer outputs with POC-compliant fields, or only for new analyses?

6. **Performance**: Max how many countries should map support? (Currently planning for 50, but could do 195 all countries)

---

**Ready to implement once approved! 🚀**

