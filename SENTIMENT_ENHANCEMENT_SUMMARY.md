# Sentiment Analyzer Enhancement - Quick Summary

## 🎯 What We're Doing

Enhancing the sentiment_analyzer sub-agent with 4 major improvements:

---

## 📊 Current State vs. Proposed

### Visualizations

| Aspect | Current ❌ | Proposed ✅ |
|--------|-----------|-------------|
| **Default Behavior** | Creates 3 visualizations automatically | Creates 2 visualizations (table + bar chart) |
| **User Control** | None - always same 3 | User can request additional viz types |
| **Available Types** | Bar, Radar, JSON | Bar, Radar, Map, Table (Excel), JSON |
| **Map Support** | ❌ No | ✅ Interactive world map |
| **Excel Export** | ❌ No | ✅ Multi-sheet Excel workbook (always available!) |
| **Frontend UI** | Shows all 3 artifacts | Shows defaults + user can request more |

### POC Compliance

| Feature | POC Has ✅ | Current Agent Has | After Enhancement |
|---------|-----------|-------------------|-------------------|
| Sentiment scoring | ✅ | ✅ | ✅ |
| Bias detection | ✅ | ✅ | ✅ |
| **Reasoning field** | ✅ | ❌ | ✅ |
| **Bias severity (0-1)** | ✅ | ❌ | ✅ |
| **Bias notes/explanation** | ✅ | ❌ | ✅ |
| **Source type classification** | ✅ | ❌ | ✅ |
| Date published | ✅ | ✅ | ✅ |
| Credibility score | ✅ | ✅ | ✅ |
| **Domain extraction** | ✅ | ❌ | ✅ |
| **Recent-only aggregation** | ✅ | ❌ | ✅ |
| CSV export | ✅ | Partial | ✅ Full |

---

## 🗺️ New Feature: Sentiment Map

### What It Does
Creates an interactive world map showing sentiment by country using color coding.

### Visual Example
```
🌍 Interactive World Map
   ┌─────────────────────────────────────┐
   │                                     │
   │    🟢 USA: +0.65 (Positive)        │
   │    🟡 France: +0.12 (Neutral)      │
   │    🔴 Iran: -0.78 (Negative)       │
   │                                     │
   │  [Hover for details]                │
   │  [Zoom/Pan enabled]                 │
   └─────────────────────────────────────┘
   
   Color Scale: 🔴 Negative → 🟡 Neutral → 🟢 Positive
```

### Features
- ✅ Country colors match sentiment (-1 to +1)
- ✅ Hover tooltips with details
- ✅ Optional text annotations
- ✅ Both HTML (interactive) and PNG (static) export
- ✅ Supports 3-50 countries
- ✅ Natural Earth projection

### Use Cases
- Geopolitical sentiment analysis
- Policy perception across regions
- Crisis monitoring by location
- Comparative regional analysis

---

## 📊 New Feature: Excel Table Export

### What It Does
Creates a comprehensive Excel workbook with 3 sheets containing all analysis data.

### Excel Structure

**📄 Sheet 1: Country Summary**
```
╔════════════╦══════════════╦═══════════╦══════════╦════════════════╗
║  Country   ║   Sentiment  ║ Category  ║ Articles ║ Avg Credibility║
╠════════════╬══════════════╬═══════════╬══════════╬════════════════╣
║  USA       ║    +0.65     ║ Positive  ║    20    ║      0.82      ║
║  UK        ║    -0.32     ║ Negative  ║    18    ║      0.78      ║
║  France    ║    +0.12     ║ Neutral   ║    15    ║      0.85      ║
╚════════════╩══════════════╩═══════════╩══════════╩════════════════╝
```

**📄 Sheet 2: Article Details**
```
╔════════════╦═════════════════════════╦═══════════╦═════════════╦════════╗
║  Country   ║         Title           ║ Sentiment ║ Source Type ║  Date  ║
╠════════════╬═════════════════════════╬═══════════╬═════════════╬════════╣
║  USA       ║ Policy Update on...     ║   +0.8    ║    media    ║ 2024-10║
║  USA       ║ Expert Analysis of...   ║   +0.5    ║    media    ║ 2024-10║
╚════════════╩═════════════════════════╩═══════════╩═════════════╩════════╝
```

**📄 Sheet 3: Bias Analysis**
```
╔════════════╦═══════════════╦══════════╦═══════╦═══════════════════════╗
║  Country   ║   Bias Type   ║ Severity ║ Count ║        Notes          ║
╠════════════╬═══════════════╬══════════╬═══════╬═══════════════════════╣
║  USA       ║ source_bias   ║   0.4    ║   5   ║ Mostly govt sources...║
║  UK        ║ framing_bias  ║   0.6    ║   8   ║ Negative framing...   ║
╚════════════╩═══════════════╩══════════╩═══════╩═══════════════════════╝
```

### Export Formats
- ✅ **Excel (.xlsx)** - Multi-sheet workbook
- ✅ **CSV Bundle** - 3 separate CSV files (zipped)
- ✅ **JSON** - Complete structured data
- ✅ **HTML Table** - Interactive web view with sorting

### Features
- ✅ Download button in frontend
- ✅ Sortable columns in HTML view
- ✅ Search/filter capabilities
- ✅ Formatted headers and borders
- ✅ Auto-width columns
- ✅ Mobile-responsive HTML

---

## 🎨 New Feature: User-Controlled Visualization

### Current Behavior ❌
```python
# Agent ALWAYS creates these 3:
1. Bar Chart
2. Radar Chart  
3. JSON Export

# User has no control
# Creates artifacts user might not need
# Wastes processing time
```

### New Behavior ✅
```python
# Option 1: Default (if user doesn't specify)
→ Creates Table + Bar Chart (2 viz)
→ Excel always downloadable!

# Option 2: User requests additional visualizations
User: "Also show me a map"
→ Creates Table + Bar Chart + Map

# Option 3: User wants everything
User: "Show all visualizations"
→ Creates Table + Bar + Radar + Map + JSON
```

### How User Specifies

**Method 1: Natural Language (Master Agent)**
```
User: "Analyze nuclear energy sentiment and also show me a world map"
      ↓
Master Agent parses: requested_visualizations = ["map"]
      ↓
Sentiment Analyzer creates: Table + Bar Chart + Map (3 viz)
```

**Method 2: API Parameter**
```python
POST /api/sentiment/analyze
{
  "query": "nuclear energy",
  "countries": ["US", "France", "Germany"],
  "visualizations": ["map", "radar_chart"]  ← Adds to defaults
}
# Returns: table, bar_chart, map, radar_chart (4 viz)
```

**Method 3: Frontend UI**
```
After analysis complete, show:

┌───────────────────────────────────────┐
│ Default Visualizations (Included):   │
│ ☑ Data Table (Excel)                 │
│ ☑ Bar Chart                           │
│                                       │
│ Additional Visualizations:            │
│ ☐ Radar Chart                         │
│ ☐ World Map                           │
│ ☐ JSON Export                         │
│                                       │
│   [Generate Additional Visualizations]│
└───────────────────────────────────────┘
```

### Benefits
- ✅ Excel always available (no need to request)
- ✅ Bar chart for quick visual review
- ✅ Can add more visualizations as needed
- ✅ Better UX (user gets essentials + options)
- ✅ Backwards compatible (still fast)

---

## 📝 POC Compliance Gaps & Fixes

### Gap 1: Reasoning Field Missing
**POC Has:**
```json
{
  "sentiment": -0.5,
  "reasoning": "Article uses negative language and critical tone toward Hamas"
}
```

**Current Agent Has:**
```json
{
  "sentiment": -0.5
}
```

**Fix:** Update LLM prompt in `sentiment_scorer.py` to include reasoning

---

### Gap 2: Bias Severity & Notes Missing
**POC Has:**
```json
{
  "bias_type": ["source_bias", "selection_bias"],
  "bias_severity": 0.6,
  "bias_notes": "Only government sources cited, no independent voices"
}
```

**Current Agent Has:**
```json
{
  "bias_type": ["source_bias", "selection_bias"]
}
```

**Fix:** Update `bias_detector.py` to score severity (0-1) and provide explanations

---

### Gap 3: Source Type Classification Missing
**POC Has:**
```json
{
  "source_type": "media",  // or "govt", "political_party", "encyclopedia"
}
```

**Current Agent Has:**
```json
{
  // No source_type field
}
```

**Fix:** Add source type classification to LLM prompt

---

## 📊 Implementation Phases

### Phase 1: POC Compliance (2 hours)
- Update sentiment scorer for reasoning
- Update bias detector for severity/notes
- Add source type classification
- Update state schema

### Phase 2: Map Visualizer (3 hours)
- Create map function in shared factory
- Add country code mapping
- Integrate into visualizer node
- Write tests

### Phase 3: Table Visualizer (4 hours)
- Create table function in shared factory
- Implement Excel export (3 sheets)
- Add CSV bundle option
- Write tests

### Phase 4: Dynamic Selection (2 hours)
- Modify visualizer node
- Update state schema
- Add configuration
- Test default + custom behavior

### Phase 5: Testing & Docs (2 hours)
- Comprehensive tests
- Update README
- Integration testing
- Frontend testing

**Total: ~13 hours**

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| Default viz count | 2 (table + bar chart) |
| Available viz types | 5 (up from 3) |
| POC compliance | 100% (up from ~70%) |
| Excel export quality | 3 sheets with full metadata |
| **Excel always available** | ✅ Every analysis includes downloadable data |
| Map rendering time | <2 seconds for 10 countries |
| User satisfaction | Can request additional viz |
| Backwards compatibility | 100% (no breaking changes) |

---

## 🔄 Migration Path

### For Existing Code
```python
# Old code continues to work
result = await run_sentiment_analyzer("query", ["US", "UK"])
# Now creates 2 viz (table + bar) instead of 3
# Excel data now always available for download!
```

### For New Features
```python
# New code can request additional viz (adds to defaults)
result = await run_sentiment_analyzer(
    "query", 
    ["US", "UK"],
    visualizations=["map", "radar_chart"]
)
# Returns: table, bar_chart, map, radar_chart (4 viz)
```

### For Frontend
- Old artifact viewer continues to work
- New artifacts (map, table) render automatically
- Add optional UI for viz selection

---

## 📦 Dependencies

### New Libraries Needed
```bash
uv pip install openpyxl  # For Excel export
```

### Existing Libraries Used
- `plotly` - Map and charts
- `pandas` - Data manipulation
- `httpx` - Async HTTP
- `openai` - LLM calls

---

## ⚡ Performance Impact

### Before
```
Time to generate 3 artifacts: ~4-6 seconds
- Bar chart: ~1.5s
- Radar chart: ~1.5s  
- JSON export: ~1s
```

### After (Default - 2 viz)
```
Time to generate 2 artifacts: ~4.5 seconds
- Table (Excel): ~3s
- Bar chart: ~1.5s
[Similar speed, but Excel always available! 📊]
```

### After (All 5 viz)
```
Time to generate 5 artifacts: ~9 seconds
- Table: ~3s
- Bar chart: ~1.5s
- Radar chart: ~1.5s
- Map: ~2s
- JSON: ~1s
```

---

## 🎓 Learning from POC

The POC (`geo_sentiment_poc.py`) taught us:

1. ✅ **Reasoning is crucial** - Helps debug and validate sentiment scores
2. ✅ **Bias needs quantification** - Severity scores (0-1) make it actionable
3. ✅ **Metadata matters** - Source type, dates, domains provide context
4. ✅ **Multiple outputs** - JSON + CSV serve different use cases
5. ✅ **Trimmed mean** - Robust aggregation handles outliers

All these lessons are being incorporated into the enhancement.

---

## 📞 Next Steps

1. ✅ Review this plan
2. ✅ Ask clarifying questions
3. ✅ Approve implementation
4. 🚀 Start coding!

**Questions? See the full plan in `SENTIMENT_ANALYZER_ENHANCEMENT_PLAN.md`**

