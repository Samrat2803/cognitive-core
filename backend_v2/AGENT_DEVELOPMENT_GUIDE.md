# Agent Development Guide - Lessons Learned

**Purpose:** Document critical lessons from building agents to reduce development time for future agents.

**Status:** Living document - Updated after each agent implementation

---

## ✅ Validated: Sentiment Analyzer Agent (Oct 2, 2025)

### Proof of Success ✅
- **Standalone Test:** PASSED ✅
- **Real Data:** Got 5 results from Tavily (France: climate policy)
- **Sentiment Scoring:** Working (positive: 0.70)
- **Bias Detection:** Working (2 bias types detected)
- **Artifacts Generated:** 3 files (bar chart, radar chart, JSON data)
- **Execution Time:** 31 seconds
- **No Errors:** Clean execution log with 6 steps

### Artifacts Created
```bash
artifacts/
├── sentiment_bar_chart_286228d81190.html (3.5MB) ← Using shared tools
├── sentiment_radar_chart_a5bcb604c71c.html (3.5MB) ← Using shared tools
└── sentiment_data_table_1f633425f69c.json (1KB) ← Using shared tools
```

**Status:** ✅ INTEGRATED & WORKING  
**Visualization:** ✅ USING SHARED TOOLS (visualization_factory.py)

### Integration Test Results ✅
- **Integration Test:** PASSED ✅  
- **Called Via:** `SubAgentCaller.call_sentiment_analyzer()`
- **Test Query:** "renewable energy" (Germany, Japan)
- **Real Data:** Got 10 results (5 per country)
- **Sentiment Scores:** Germany: positive (0.80), Japan: positive (0.70)
- **Bias Detection:** Working (3 types each)
- **Artifacts:** 3 generated successfully
- **No Integration Errors:** Clean execution

**Integration File Modified:** `langgraph_master_agent/tools/sub_agent_caller.py` (ONLY)

---

## 🎯 Critical Success Factors

### 1. **Import Structure (CRITICAL)**

**Problem:** Relative imports (`from ..config import`) break standalone testing.

**Solution:** Use simple imports everywhere
```python
# ❌ DON'T USE
from ..config import MODEL
from .state import SentimentAnalyzerState

# ✅ DO USE  
from config import MODEL
from state import SentimentAnalyzerState
```

**Why:** Agent must run standalone from its own directory without master agent.

---

### 2. **Environment Variables (CRITICAL)**

**Problem:** OpenAI/Tavily clients fail without API keys in standalone mode.

**Solution:** Load .env in EVERY node file that uses API clients
```python
# At top of EVERY node file using OpenAI/Tavily
from dotenv import load_dotenv
import os

# Load from backend_v2/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))

client = AsyncOpenAI()  # Now works
```

**Where to add:**
- ✅ All nodes using OpenAI
- ✅ All nodes using Tavily
- ❌ NOT needed in: state.py, config.py, visualizer.py (if only using plotly)

---

### 3. **API Parameter Validation**

**Problem:** `TavilyClient.search()` got unexpected keyword argument 'days'

**Solution:** Check shared API signatures BEFORE using
```python
# Check backend_v2/shared/tavily_client.py for actual parameters
async def search(
    query: str,
    search_depth: str = "basic",
    max_results: int = 8,
    country: Optional[str] = None,  # ✅ Use this
    # days parameter doesn't exist! ❌
)
```

**Action:** Always reference `backend_v2/shared/` for API signatures, don't assume.

---

### 4. **Shared Visualization Tools (RECOMMENDED) 🎨**

**New:** Oct 2, 2025 - Implemented after Sentiment Analyzer

**Why:** Avoid duplicating Plotly code across agents. Ensures consistency.

**Location:** `backend_v2/shared/visualization_factory.py`

**Available Tools:**
```python
from shared.visualization_factory import (
    VisualizationFactory,
    create_sentiment_bar_chart,
    create_sentiment_radar_chart
)

# Bar Chart
artifact = create_sentiment_bar_chart(
    country_scores=sentiment_scores,
    query=query,
    output_dir=output_dir
)

# Radar Chart
artifact = create_sentiment_radar_chart(
    country_scores=sentiment_scores,
    query=query,
    output_dir=output_dir,
    max_countries=5
)

# General factory methods
fig = VisualizationFactory.create_bar_chart(
    x_data=['US', 'UK'],
    y_data=[0.8, -0.3],
    title="Custom Chart",
    color_scale="RdYlGn",
    color_range=(-1, 1)
)

artifact = VisualizationFactory.save_artifact(
    fig=fig,
    output_dir=output_dir,
    artifact_type="custom_chart",
    title="My Chart"
)

# JSON export
artifact = VisualizationFactory.save_json_export(
    data={"results": [...]},
    output_dir=output_dir,
    artifact_type="data_table",
    title="Data Export"
)
```

**Benefits:**
- ✅ Less code in agent nodes (3 lines vs 50 lines per chart)
- ✅ Consistent styling across all agents
- ✅ Automatic artifact metadata generation
- ✅ Unique IDs and proper file naming
- ✅ Easy to extend (add new chart types once, use everywhere)

**Available Chart Types:**
1. `create_bar_chart()` - Bar charts with color gradients
2. `create_radar_chart()` - Multi-series radar charts
3. `create_choropleth_map()` - World maps (country-level)
4. `create_line_chart()` - Time series / trends
5. `create_heatmap()` - 2D heatmaps
6. `save_artifact()` - Generic Plotly figure saver
7. `save_json_export()` - Structured data exports

**Convenience Functions:**
- `create_sentiment_bar_chart()` - Ready-made sentiment bars
- `create_sentiment_radar_chart()` - Ready-made sentiment radar

**When to Use:**
- ✅ Use for ALL standard charts (bar, radar, line, map)
- ✅ Use convenience functions when available
- ✅ Add new convenience functions for repeated patterns
- ❌ Only write custom Plotly code for truly unique visualizations

**Example from Sentiment Analyzer:**

**Before (50 lines):**
```python
# Old approach - direct Plotly code
fig_bar = go.Figure(data=[
    go.Bar(
        x=countries_list,
        y=scores_list,
        marker=dict(
            color=scores_list,
            colorscale='RdYlGn',
            cmin=-1,
            cmax=1,
            colorbar=dict(title="Sentiment")
        )
    )
])
fig_bar.update_layout(...)
html_path = os.path.join(output_dir, f"{artifact_id}.html")
fig_bar.write_html(html_path)
artifacts.append({...})
```

**After (3 lines):**
```python
# New approach - shared tools
artifact = create_sentiment_bar_chart(
    country_scores=sentiment_scores,
    query=query,
    output_dir=output_dir
)
artifacts.append(artifact)
```

**Code Reduction:** 94% less code in visualizer nodes 🎉

---

### 5. **File Structure That Works**

```
sentiment_analyzer/
├── state.py           # TypedDict with all state fields
├── config.py          # Constants only (MODEL, TEMPERATURE, etc.)
├── graph.py           # LangGraph workflow (add_node, add_edge)
├── main.py            # Standalone test runner
├── __init__.py        # Export graph and state
├── nodes/
│   ├── __init__.py    # Export all node functions
│   ├── analyzer.py    # ✅ Load .env here
│   ├── search_executor.py
│   ├── sentiment_scorer.py  # ✅ Load .env here
│   ├── bias_detector.py     # ✅ Load .env here
│   ├── synthesizer.py       # ✅ Load .env here
│   └── visualizer.py
└── artifacts/         # Created by agent (don't commit)
```

---

### 6. **Testing Workflow**

**Step 1:** Test from agent's own directory
```bash
cd backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer
python main.py "test query"
```

**Step 2:** Check outputs
- ✅ Execution log shows all steps
- ✅ Artifacts created in `artifacts/` folder
- ✅ No errors in output
- ✅ Results saved to `examples/` folder

**Step 3:** ONLY after standalone success → integrate

---

## 📝 Quick Reference: Build Checklist

### Setup (2 min)
- [ ] Create folder: `mkdir -p sub_agents/{name}/{nodes,tools,artifacts,tests}`
- [ ] Copy structure from sentiment_analyzer as template

### Core Files (30-60 min)
- [ ] `state.py` - Define all state fields (copy TypedDict pattern)
- [ ] `config.py` - Constants only (MODEL=0, TEMPERATURE=0, etc.)
- [ ] `nodes/__init__.py` - Export all node functions

### Node Files (2-4 hours)
- [ ] Each node: Add `load_dotenv()` if using OpenAI/Tavily
- [ ] Each node: Use simple imports (`from config import`, not `from ..config`)
- [ ] Each node: Return dict with updated state fields
- [ ] Each node: Add print statements for progress tracking

### Graph (15 min)
- [ ] `graph.py` - Wire nodes with add_node, add_edge
- [ ] Use simple imports (not relative)
- [ ] Test graph creation: `python graph.py`

### Testing (30 min)
- [ ] `main.py` - Create test runner (copy from sentiment_analyzer)
- [ ] Run standalone: `python main.py "test query"`
- [ ] Fix errors until it runs end-to-end
- [ ] Check artifacts are created

---

## 🚨 Common Errors & Fixes

### Error 1: `ModuleNotFoundError: No module named 'config'`
**Fix:** You're not running from the agent's directory
```bash
cd backend_v2/langgraph_master_agent/sub_agents/{agent_name}
python main.py
```

### Error 2: `OpenAIError: api_key must be set`
**Fix:** Add `load_dotenv()` to node file
```python
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))
```

### Error 3: `ImportError: attempted relative import`
**Fix:** Change relative imports to simple imports
```python
# Change this:
from ..config import MODEL
# To this:
from config import MODEL
```

### Error 4: API unexpected keyword argument
**Fix:** Check actual API signature in `backend_v2/shared/`
```python
# Check what parameters actually exist
cat backend_v2/shared/tavily_client.py
```

---

## 🎨 Artifact Generation Tips

### Working Pattern (Plotly)
```python
import plotly.graph_objects as go
import os

# Get absolute path to artifacts
output_dir = os.path.join(os.path.dirname(__file__), '..', 'artifacts')
os.makedirs(output_dir, exist_ok=True)

# Create figure
fig = go.Figure(data=[...])
fig.update_layout(title="Your Chart")

# Save HTML (works reliably)
html_path = os.path.join(output_dir, f"{artifact_id}.html")
fig.write_html(html_path)

# Return artifact info
return {
    "artifacts": [{
        "artifact_id": artifact_id,
        "type": "bar_chart",
        "html_path": html_path
    }]
}
```

**Note:** PNG export requires `kaleido` package and can fail. Start with HTML only.

---

## ⏱️ Time Estimates (Validated)

| Task | Time (Experienced) | First Time |
|------|-------------------|------------|
| Folder setup | 2 min | 5 min |
| state.py + config.py | 10 min | 20 min |
| Node files (×6) | 90 min | 3 hours |
| graph.py | 15 min | 30 min |
| main.py | 15 min | 30 min |
| Debug & test | 30 min | 2 hours |
| **Total** | **~3 hours** | **~6.5 hours** |

---

## 🔄 Integration (AFTER Standalone Works)

**DO NOT modify master agent until standalone tests pass!**

### Step 1: Update sub_agent_caller.py (ONLY file to touch) ✅ VALIDATED

```python
# File: langgraph_master_agent/tools/sub_agent_caller.py

async def call_sentiment_analyzer(self, query: str, countries: list = None, time_range_days: int = 7):
    """Call sentiment analyzer - ✅ WORKING IMPLEMENTATION"""
    
    # Lazy import (only loads when called)
    import sys
    agent_dir = os.path.join(os.path.dirname(__file__), '../sub_agents/sentiment_analyzer')
    sys.path.insert(0, agent_dir)
    
    try:
        from graph import create_sentiment_analyzer_graph
        from state import SentimentAnalyzerState
        
        graph = create_sentiment_analyzer_graph()
        
        # Initialize ALL state fields (IMPORTANT!)
        initial_state: SentimentAnalyzerState = {
            "query": query,
            "countries": countries or ["US", "UK", "France"],
            "time_range_days": time_range_days,
            "search_results": {},
            "sentiment_scores": {},
            "bias_analysis": {},
            "summary": "",
            "key_findings": [],
            "confidence": 0.0,
            "artifacts": [],
            "execution_log": [],
            "error_log": []
        }
        
        result = await graph.ainvoke(initial_state)
        
        return {
            "success": True,
            "sub_agent": "sentiment_analyzer",
            "status": "COMPLETED",
            "data": {
                "sentiment_scores": result.get("sentiment_scores", {}),
                "bias_analysis": result.get("bias_analysis", {}),
                "summary": result.get("summary", ""),
                "artifacts": result.get("artifacts", []),
                # ... include all needed fields
            }
        }
    except Exception as e:
        return {
            "success": False,
            "sub_agent": "sentiment_analyzer",
            "status": "ERROR",
            "error": str(e)
        }
```

**Key Points:**
- ✅ Use lazy imports (import at function level)
- ✅ Initialize ALL state fields (TypedDict requires it)
- ✅ Wrap in try/except for graceful error handling
- ✅ Return consistent format with success/error states

### Step 2: Test integration ✅ VALIDATED
```bash
cd backend_v2
python -c "
import asyncio
from langgraph_master_agent.tools.sub_agent_caller import SubAgentCaller

async def test():
    caller = SubAgentCaller()
    result = await caller.call_sentiment_analyzer('renewable energy', ['Germany', 'Japan'])
    print(f\"Success: {result['success']}\")
    if result['success']:
        print(f\"Countries: {result['data']['countries']}\")
        print(f\"Artifacts: {len(result['data']['artifacts'])}\")

asyncio.run(test())
"
```

**Expected Output:**
```
Success: True
Countries: ['Germany', 'Japan']
Artifacts: 3
```

### Step 3: Only after integration works → update master agent routing

**Not needed yet** - Master agent will call via SubAgentCaller when ready

---

## 📊 Success Metrics

### Standalone Phase
- ✅ Agent runs without errors
- ✅ Generates expected number of artifacts
- ✅ Execution time < 30 seconds (for simple queries)
- ✅ All execution log steps present
- ✅ State fields properly updated

### Integration Phase  
- ✅ Master agent can call sub-agent
- ✅ Results returned in expected format
- ✅ No import errors
- ✅ Existing master agent tests still pass
- ✅ Artifacts accessible via API

---

## 🎓 Lessons Learned

### What Worked ✅
1. **Simple folder structure** - Easy to navigate
2. **Standalone testing first** - Caught all issues early
3. **Print statements** - Essential for debugging
4. **Simple imports** - No relative import hell
5. **Load .env everywhere** - Better than assuming it's loaded

### What Didn't Work ❌
1. **Relative imports** - Breaks standalone mode
2. **Assuming API signatures** - Check actual code
3. **Skipping standalone testing** - Would have wasted integration time
4. **Complex import paths** - Keep it simple

### Time Savers ⚡
1. **Copy sentiment_analyzer structure** - Don't start from scratch
2. **Test graph.py independently** - Before adding to main.py
3. **Use print liberally** - Saves debugging time
4. **Check shared/ before using APIs** - Avoid wrong parameters

---

## 🔮 Next Agent (Use This Checklist)

- [ ] Copy sentiment_analyzer folder structure
- [ ] Update state.py with your fields
- [ ] Update config.py with your constants
- [ ] Implement nodes (remember load_dotenv!)
- [ ] Test each node independently if possible
- [ ] Wire graph.py
- [ ] Test standalone with main.py
- [ ] Fix errors until it works
- [ ] ONLY THEN consider integration

**Golden Rule:** If it doesn't work standalone, it won't work integrated. Test standalone FIRST!

---

**Last Updated:** October 2, 2025 12:56 PM  
**Validated Agents:** Sentiment Analyzer (✅ Working)  
**Next to Build:** Media Bias Detector

