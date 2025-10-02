# Sentiment Analyzer - Visualization Architecture

## 🏗️ System Architecture (After Enhancement)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER / MASTER AGENT                             │
│                                                                         │
│  Request: "Analyze sentiment and show map + table"                     │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SENTIMENT ANALYZER STATE                             │
│                                                                         │
│  query: "nuclear energy policy"                                        │
│  countries: ["US", "France", "Germany"]                                │
│  requested_visualizations: ["map", "table"]  ◄─── NEW!                │
│  default_visualization: "bar_chart"           ◄─── NEW!                │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     SENTIMENT ANALYZER GRAPH                            │
│                                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐       │
│  │ Analyzer │ → │  Search  │ → │  Scorer  │ → │ Bias Detector│       │
│  └──────────┘   └──────────┘   └──────────┘   └──────────────┘       │
│                                                                         │
│  ┌──────────────┐              ┌────────────────────────┐             │
│  │ Synthesizer  │ ──────────→  │  VISUALIZER (Enhanced) │             │
│  └──────────────┘              └────────────┬───────────┘             │
│                                              │                         │
│                            ┌─────────────────┴─────────────────┐       │
│                            │   Visualization Selection Logic   │       │
│                            │                                   │       │
│                            │  if requested_visualizations:     │       │
│                            │    create_only_requested()        │       │
│                            │  else:                           │       │
│                            │    create_default_only()         │       │
│                            └─────────────────┬─────────────────┘       │
└──────────────────────────────────────────────┼─────────────────────────┘
                                               │
                                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              SHARED VISUALIZATION FACTORY (Enhanced)                    │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────┐   │
│  │ create_bar_chart │  │create_radar_chart│  │create_choropleth_ │   │
│  │                  │  │                  │  │      map          │   │
│  │  [Existing]      │  │  [Existing]      │  │  [NEW! 🗺️]       │   │
│  └──────────────────┘  └──────────────────┘  └───────────────────┘   │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐                           │
│  │create_sentiment_ │  │ save_json_export │                           │
│  │     table        │  │                  │                           │
│  │  [NEW! 📊]       │  │  [Existing]      │                           │
│  └──────────────────┘  └──────────────────┘                           │
│                                                                         │
│  Features:                                                             │
│  • Country code mapping (US → USA, UK → GBR)                           │
│  • Multi-format export (HTML, PNG, Excel, CSV, JSON)                  │
│  • Consistent color schemes (RdYlGn for sentiment)                    │
│  • Responsive HTML tables with sorting/filtering                      │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ARTIFACTS GENERATED                             │
│                                                                         │
│  1. 🗺️ SENTIMENT MAP (if requested)                                   │
│     ├── sentiment_map_abc123.html (interactive)                       │
│     └── sentiment_map_abc123.png (static)                             │
│                                                                         │
│  2. 📊 DATA TABLE (if requested)                                       │
│     ├── sentiment_table_def456.xlsx (3 sheets: Summary, Articles,     │
│     │                                 Bias Analysis)                   │
│     ├── sentiment_table_def456.zip (CSV bundle)                       │
│     ├── sentiment_table_def456.json                                   │
│     └── sentiment_table_def456.html (interactive table)               │
│                                                                         │
│  3. 📊 BAR CHART (default or if requested)                             │
│     ├── sentiment_bar_chart_ghi789.html                               │
│     └── sentiment_bar_chart_ghi789.png                                │
│                                                                         │
│  4. 📊 RADAR CHART (if requested)                                      │
│     ├── sentiment_radar_jkl012.html                                   │
│     └── sentiment_radar_jkl012.png                                    │
│                                                                         │
│  5. 📄 JSON EXPORT (if requested)                                      │
│     └── sentiment_data_export_mno345.json                             │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND UI                                   │
│                                                                         │
│  Artifact Viewer:                                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ 🗺️ World Sentiment Map                         [View] [Download]  │ │
│  │ ├─ Interactive map with hover tooltips                            │ │
│  │ └─ Color scale: 🔴 Negative → 🟡 Neutral → 🟢 Positive            │ │
│  │                                                                    │ │
│  │ 📊 Data Table                            [View] [Download Excel]  │ │
│  │ ├─ Sheet 1: Country Summary                                       │ │
│  │ ├─ Sheet 2: Article Details                                       │ │
│  │ └─ Sheet 3: Bias Analysis                                         │ │
│  │                                                                    │ │
│  │ 📊 Sentiment Bar Chart                          [View] [Download]  │ │
│  │ └─ Countries ranked by sentiment score                            │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  Visualization Selector (Optional Future Feature):                     │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ Generate Additional Visualizations:                                │ │
│  │ ☐ Bar Chart   ☐ Radar Chart   ☐ World Map   ☐ Data Table         │ │
│  │ [Generate Selected]                                                │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow (Enhanced Visualizer Node)

### Before (Current Implementation)
```
┌─────────────────────────┐
│  Visualizer Node        │
│                         │
│  artifacts = []         │
│  artifacts.append(      │
│    create_bar_chart()   │ ◄─── Always created
│  )                      │
│  artifacts.append(      │
│    create_radar_chart() │ ◄─── Always created
│  )                      │
│  artifacts.append(      │
│    save_json_export()   │ ◄─── Always created
│  )                      │
│  return artifacts       │
└─────────────────────────┘
```

### After (New Implementation)
```
┌──────────────────────────────────────────┐
│  Visualizer Node (Enhanced)              │
│                                          │
│  requested = state.get(                  │
│    "requested_visualizations", []        │
│  )                                       │
│                                          │
│  if not requested:                       │
│    requested = [DEFAULT_VIZ]  ◄────── Only 1 by default
│                                          │
│  viz_creators = {                        │
│    "bar_chart": create_bar_chart,        │
│    "radar_chart": create_radar_chart,    │
│    "map": create_map,         ◄────────── NEW!
│    "table": create_table,     ◄────────── NEW!
│    "json": create_json                   │
│  }                                       │
│                                          │
│  artifacts = []                          │
│  for viz_type in requested:              │
│    artifact = viz_creators[viz_type]()   │
│    artifacts.append(artifact)            │
│                                          │
│  return artifacts                        │
└──────────────────────────────────────────┘
```

---

## 🗺️ Map Visualizer - Internal Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              create_sentiment_map()                             │
│                                                                 │
│  INPUT:                                                         │
│  ┌────────────────────────────────────┐                        │
│  │ country_scores = {                 │                        │
│  │   "US": {                          │                        │
│  │     "score": 0.65,                 │                        │
│  │     "sentiment": "positive"         │                        │
│  │   },                               │                        │
│  │   "UK": {...}, "France": {...}     │                        │
│  │ }                                  │                        │
│  └────────────────────────────────────┘                        │
│                                                                 │
│  STEP 1: Convert country names to ISO-3 codes                  │
│  ┌────────────────────────────────────┐                        │
│  │ "US" → "USA"                       │                        │
│  │ "UK" → "GBR"                       │                        │
│  │ "France" → "FRA"                   │                        │
│  │ "United States" → "USA"            │                        │
│  └────────────────────────────────────┘                        │
│                                                                 │
│  STEP 2: Create Plotly choropleth                              │
│  ┌────────────────────────────────────┐                        │
│  │ fig = go.Figure(                   │                        │
│  │   data=go.Choropleth(              │                        │
│  │     locations=["USA", "GBR", ...], │                        │
│  │     z=[0.65, -0.32, ...],         │                        │
│  │     colorscale="RdYlGn",          │                        │
│  │     zmin=-1, zmax=1               │                        │
│  │   )                               │                        │
│  │ )                                 │                        │
│  └────────────────────────────────────┘                        │
│                                                                 │
│  STEP 3: Add annotations (optional)                            │
│  ┌────────────────────────────────────┐                        │
│  │ for country, text in annotations:  │                        │
│  │   fig.add_annotation(              │                        │
│  │     text=text,                     │                        │
│  │     x=lon, y=lat                   │                        │
│  │   )                                │                        │
│  └────────────────────────────────────┘                        │
│                                                                 │
│  STEP 4: Save multiple formats                                 │
│  ┌────────────────────────────────────┐                        │
│  │ • HTML (interactive)               │                        │
│  │ • PNG (static, 1200x800)           │                        │
│  │ • JSON metadata                    │                        │
│  └────────────────────────────────────┘                        │
│                                                                 │
│  OUTPUT:                                                        │
│  ┌────────────────────────────────────┐                        │
│  │ {                                  │                        │
│  │   "type": "sentiment_map",         │                        │
│  │   "artifact_id": "map_abc123",     │                        │
│  │   "html_path": "...",              │                        │
│  │   "png_path": "...",               │                        │
│  │   "title": "Sentiment Map: ...",   │                        │
│  │   "countries": ["USA", "GBR", ...],│                        │
│  │   "metadata": {...}                │                        │
│  │ }                                  │                        │
│  └────────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Table Visualizer - Internal Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│              create_sentiment_table()                            │
│                                                                  │
│  INPUT:                                                          │
│  • country_scores (aggregated)                                  │
│  • articles (raw article data)                                  │
│  • bias_analysis (bias detection results)                       │
│                                                                  │
│  STEP 1: Create DataFrame for Sheet 1 (Country Summary)         │
│  ┌──────────────────────────────────────────┐                   │
│  │ df_summary = pd.DataFrame([              │                   │
│  │   {                                      │                   │
│  │     "Country": "USA",                    │                   │
│  │     "Sentiment_Score": 0.65,            │                   │
│  │     "Sentiment": "Positive",            │                   │
│  │     "Articles": 20,                     │                   │
│  │     "Avg_Credibility": 0.82,            │                   │
│  │     "Recent_30d": "85%",                │                   │
│  │     "Bias_Types": 2                     │                   │
│  │   },                                    │                   │
│  │   {...}, {...}                          │                   │
│  │ ])                                      │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                  │
│  STEP 2: Create DataFrame for Sheet 2 (Article Details)         │
│  ┌──────────────────────────────────────────┐                   │
│  │ df_articles = pd.DataFrame([             │                   │
│  │   {                                      │                   │
│  │     "Country": "USA",                    │                   │
│  │     "Title": "Policy Update...",         │                   │
│  │     "URL": "https://...",                │                   │
│  │     "Sentiment": 0.8,                    │                   │
│  │     "Reasoning": "Positive tone...",     │ ◄── NEW from POC
│  │     "Source_Type": "media",              │ ◄── NEW from POC
│  │     "Date": "2024-10-01",                │                   │
│  │     "Credibility": 0.85,                 │                   │
│  │     "Bias_Type": "source_bias",          │                   │
│  │     "Bias_Severity": 0.4                 │ ◄── NEW from POC
│  │   },                                    │                   │
│  │   {...}, {...}                          │                   │
│  │ ])                                      │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                  │
│  STEP 3: Create DataFrame for Sheet 3 (Bias Analysis)           │
│  ┌──────────────────────────────────────────┐                   │
│  │ df_bias = pd.DataFrame([                 │                   │
│  │   {                                      │                   │
│  │     "Country": "USA",                    │                   │
│  │     "Bias_Type": "source_bias",          │                   │
│  │     "Severity": 0.4,                     │ ◄── NEW from POC
│  │     "Count": 5,                          │                   │
│  │     "Examples": "Source1, Source2...",   │                   │
│  │     "Notes": "Mostly govt sources..."    │ ◄── NEW from POC
│  │   },                                    │                   │
│  │   {...}, {...}                          │                   │
│  │ ])                                      │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                  │
│  STEP 4: Export to multiple formats                             │
│  ┌──────────────────────────────────────────┐                   │
│  │ • Excel (.xlsx):                         │                   │
│  │   with pd.ExcelWriter() as writer:       │                   │
│  │     df_summary.to_excel(                 │                   │
│  │       writer, sheet_name='Summary'       │                   │
│  │     )                                    │                   │
│  │     df_articles.to_excel(                │                   │
│  │       writer, sheet_name='Articles'      │                   │
│  │     )                                    │                   │
│  │     df_bias.to_excel(                    │                   │
│  │       writer, sheet_name='Bias'          │                   │
│  │     )                                    │                   │
│  │                                          │                   │
│  │ • CSV Bundle (zip):                      │                   │
│  │   - summary.csv                          │                   │
│  │   - articles.csv                         │                   │
│  │   - bias.csv                             │                   │
│  │                                          │                   │
│  │ • JSON (structured):                     │                   │
│  │   {                                      │                   │
│  │     "summary": [...],                    │                   │
│  │     "articles": [...],                   │                   │
│  │     "bias": [...]                        │                   │
│  │   }                                      │                   │
│  │                                          │                   │
│  │ • HTML Table (interactive):              │                   │
│  │   - Tabs for each sheet                  │                   │
│  │   - Sortable columns                     │                   │
│  │   - Search functionality                 │                   │
│  │   - Download buttons                     │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                  │
│  OUTPUT:                                                         │
│  ┌──────────────────────────────────────────┐                   │
│  │ {                                        │                   │
│  │   "type": "sentiment_table",             │                   │
│  │   "artifact_id": "table_def456",         │                   │
│  │   "excel_path": "...xlsx",               │                   │
│  │   "csv_bundle_path": "...zip",           │                   │
│  │   "json_path": "...json",                │                   │
│  │   "html_path": "...html",                │                   │
│  │   "title": "Sentiment Data Table",       │                   │
│  │   "sheets": ["Summary", "Articles",      │                   │
│  │              "Bias"],                    │                   │
│  │   "row_counts": {                        │                   │
│  │     "summary": 3,                        │                   │
│  │     "articles": 53,                      │                   │
│  │     "bias": 8                            │                   │
│  │   }                                      │                   │
│  │ }                                        │                   │
│  └──────────────────────────────────────────┘                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow Examples

### Example 1: Default Behavior (No Request Specified)
```
User Request
    ↓
"Analyze nuclear energy sentiment in US, France, Germany"
    ↓
Master Agent (doesn't specify viz)
    ↓
Sentiment Analyzer State
    requested_visualizations: []  ← Empty
    ↓
Visualizer Node
    if not requested:
        requested = ["bar_chart"]  ← Use default
    ↓
Creates ONLY bar chart
    ↓
Returns 1 artifact (fast! ⚡)
```

### Example 2: Specific Request via Natural Language
```
User Request
    ↓
"Analyze nuclear energy sentiment and show me a world map and Excel table"
    ↓
Master Agent (parses intent)
    ↓
Sentiment Analyzer State
    requested_visualizations: ["map", "table"]  ← Parsed
    ↓
Visualizer Node
    creates map: ✅
    creates table: ✅
    ↓
Returns 2 artifacts (map + Excel)
```

### Example 3: API Request with Multiple Viz
```
API Request
POST /api/sentiment/analyze
{
    "query": "climate change",
    "countries": ["US", "UK", "India"],
    "visualizations": ["bar_chart", "map", "table", "json"]
}
    ↓
Sentiment Analyzer State
    requested_visualizations: ["bar_chart", "map", "table", "json"]
    ↓
Visualizer Node
    creates bar_chart: ✅
    creates map: ✅
    creates table: ✅
    creates json: ✅
    ↓
Returns 4 artifacts
```

---

## 🎨 Frontend Integration

### Artifact Viewer Component Changes

```typescript
// src/components/ArtifactViewer.tsx

interface Artifact {
  type: "sentiment_bar_chart" | "sentiment_radar_chart" | 
        "sentiment_map" | "sentiment_table" | "sentiment_data_export";
  artifact_id: string;
  html_path?: string;
  png_path?: string;
  excel_path?: string;     // NEW for table
  csv_bundle_path?: string; // NEW for table
  json_path?: string;
}

function ArtifactViewer({ artifact }: { artifact: Artifact }) {
  switch (artifact.type) {
    case "sentiment_map":
      // Render interactive map (iframe with HTML)
      return <MapArtifact artifact={artifact} />;
      
    case "sentiment_table":
      // Render table with download buttons
      return <TableArtifact artifact={artifact} />;
      
    case "sentiment_bar_chart":
      // Existing bar chart renderer
      return <ChartArtifact artifact={artifact} />;
      
    // ... other cases
  }
}

function TableArtifact({ artifact }: { artifact: Artifact }) {
  return (
    <div className="table-artifact">
      {/* Interactive HTML table */}
      <iframe src={artifact.html_path} />
      
      {/* Download buttons */}
      <div className="download-buttons">
        <button onClick={() => download(artifact.excel_path)}>
          📥 Download Excel
        </button>
        <button onClick={() => download(artifact.csv_bundle_path)}>
          📥 Download CSV Bundle
        </button>
        <button onClick={() => download(artifact.json_path)}>
          📥 Download JSON
        </button>
      </div>
    </div>
  );
}
```

---

## 📊 Performance Characteristics

### Visualization Creation Times

| Visualization | Time (avg) | Size | Notes |
|---------------|-----------|------|-------|
| Bar Chart | 1.5s | ~200KB HTML | Fast, lightweight |
| Radar Chart | 1.5s | ~200KB HTML | Fast, lightweight |
| **Map** (NEW) | 2.0s | ~300KB HTML | Slightly slower due to geography data |
| **Table** (NEW) | 3.0s | ~500KB Excel | Slower due to multi-sheet Excel creation |
| JSON Export | 1.0s | ~50KB JSON | Fastest |

### Resource Usage

| Scenario | Artifacts | Time | Memory | Disk |
|----------|-----------|------|--------|------|
| **Default** (1 viz) | 1 | ~1.5s | ~50MB | ~200KB |
| **Current** (3 viz) | 3 | ~4.0s | ~80MB | ~450KB |
| **All** (5 viz) | 5 | ~9.0s | ~120MB | ~1.2MB |

---

**Ready to implement! 🚀**

See `SENTIMENT_ANALYZER_ENHANCEMENT_PLAN.md` for detailed implementation steps.

