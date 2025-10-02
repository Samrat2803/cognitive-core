# Sentiment Analyzer Agent

## 🎯 Purpose

Analyzes political sentiment across multiple countries, detects bias types, and visualizes sentiment patterns through interactive maps and charts.

---

## 📦 What This Agent Does

**Input:** User query about a political topic + list of countries  
**Output:** Multi-country sentiment analysis with bias detection + 4 artifact types

**Example Query:**
```
"Analyze sentiment on nuclear energy policy across US, France, Germany, and Japan"
```

**Example Output:**
- Global sentiment map (choropleth)
- Multi-country radar chart
- Sentiment trend timeline
- Bias detection report with 7 bias types

---

## 🏗️ Architecture

### LangGraph Workflow
```
START → Query Analyzer → Multi-Country Search → Sentiment Scorer → 
Bias Detector → Synthesizer → Visualizer → END
```

### Files to Create

1. **`__init__.py`** - Package initialization
2. **`state.py`** - State schema for agent
3. **`config.py`** - Configuration constants
4. **`graph.py`** - LangGraph workflow definition
5. **`nodes/analyzer.py`** - Query analysis and country extraction
6. **`nodes/search_executor.py`** - Multi-country Tavily searches
7. **`nodes/sentiment_scorer.py`** - LLM-based sentiment scoring
8. **`nodes/bias_detector.py`** - Detect 7 bias types
9. **`nodes/synthesizer.py`** - Synthesize final response
10. **`nodes/visualizer.py`** - Generate 4 artifact types
11. **`tests/test_agent.py`** - Unit tests
12. **`tests/test_integration.py`** - Integration tests

---

## 📋 Implementation Steps

### Step 1: Define State Schema (`state.py`)

**File:** `state.py`

```python
from typing import TypedDict, List, Dict, Any, Optional

class SentimentAnalyzerState(TypedDict):
    """State for Sentiment Analyzer Agent"""
    
    # Input
    query: str                              # Original query
    countries: List[str]                    # Countries to analyze
    time_range_days: int                    # Recency filter (default: 7)
    
    # Search Results
    search_results: Dict[str, List[Dict]]   # {country: [search_results]}
    
    # Analysis Results
    sentiment_scores: Dict[str, Dict]       # {country: {positive, negative, neutral, score}}
    bias_analysis: Dict[str, Dict]          # {country: {bias_types, examples}}
    
    # Synthesis
    summary: str                            # Text summary
    key_findings: List[str]                 # Bullet points
    confidence: float                       # 0-1 confidence score
    
    # Artifacts
    artifacts: List[Dict[str, Any]]         # Generated artifacts
    
    # Metadata
    execution_log: List[Dict[str, str]]     # Step-by-step log
    error_log: List[str]                    # Errors encountered
```

---

### Step 2: Configuration (`config.py`)

**File:** `config.py`

```python
import os

# LLM Configuration
MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
TEMPERATURE = 0  # Always 0 for consistency

# Search Configuration
DEFAULT_COUNTRIES = ["US", "UK", "France", "Germany", "Japan"]
MAX_COUNTRIES = 10
DEFAULT_TIME_RANGE_DAYS = 7
SEARCH_DEPTH = "basic"
MAX_RESULTS_PER_COUNTRY = 5

# Sentiment Scoring
SENTIMENT_THRESHOLD_POSITIVE = 0.3
SENTIMENT_THRESHOLD_NEGATIVE = -0.3

# Bias Types to Detect
BIAS_TYPES = [
    "political_lean",      # Left/right political bias
    "source_bias",         # Government vs independent
    "temporal_bias",       # Recency bias
    "selection_bias",      # Cherry-picking facts
    "framing_bias",        # How story is presented
    "confirmation_bias",   # Supporting pre-existing views
    "cultural_bias"        # Cultural perspective
]

# Visualization
ARTIFACT_DIR = "../../../artifacts/"
MAP_COLOR_SCALE = "RdYlGn"  # Red-Yellow-Green
```

---

### Step 3: Nodes Implementation

#### **`nodes/analyzer.py`** - Query Analysis

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from typing import Dict, Any
from openai import AsyncOpenAI
from ..config import MODEL, TEMPERATURE, DEFAULT_COUNTRIES
from ..state import SentimentAnalyzerState

client = AsyncOpenAI()

async def query_analyzer(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """
    Analyze query and extract:
    - Main topic
    - Countries to analyze (if not provided)
    - Time range
    """
    
    query = state["query"]
    countries = state.get("countries", [])
    
    # If countries not provided, extract from query or use defaults
    if not countries:
        prompt = f"""Extract countries mentioned in this query. If none mentioned, return empty list.
        
Query: {query}

Return as JSON: {{"countries": ["US", "China", ...]}}"""
        
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        countries = result.get("countries", DEFAULT_COUNTRIES[:5])
    
    return {
        "countries": countries[:10],  # Max 10 countries
        "execution_log": state.get("execution_log", []) + [{
            "step": "query_analyzer",
            "action": f"Identified {len(countries)} countries to analyze"
        }]
    }
```

#### **`nodes/search_executor.py`** - Multi-Country Search

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from typing import Dict, Any
from shared.tavily_client import TavilyClient
from ..config import SEARCH_DEPTH, MAX_RESULTS_PER_COUNTRY, DEFAULT_TIME_RANGE_DAYS
from ..state import SentimentAnalyzerState

async def search_executor(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Execute Tavily search for each country"""
    
    client = TavilyClient()
    query = state["query"]
    countries = state["countries"]
    time_range = state.get("time_range_days", DEFAULT_TIME_RANGE_DAYS)
    
    search_results = {}
    
    for country in countries:
        # Search with country filter
        country_query = f"{query} {country}"
        
        result = await client.search(
            query=country_query,
            search_depth=SEARCH_DEPTH,
            max_results=MAX_RESULTS_PER_COUNTRY,
            include_answer=True,
            days=time_range
        )
        
        if "results" in result:
            search_results[country] = result["results"]
        else:
            search_results[country] = []
    
    return {
        "search_results": search_results,
        "execution_log": state.get("execution_log", []) + [{
            "step": "search_executor",
            "action": f"Searched {len(countries)} countries"
        }]
    }
```

#### **`nodes/sentiment_scorer.py`** - Sentiment Scoring

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from typing import Dict, Any
from openai import AsyncOpenAI
from ..config import MODEL, TEMPERATURE
from ..state import SentimentAnalyzerState
import json

client = AsyncOpenAI()

async def sentiment_scorer(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Score sentiment for each country using LLM"""
    
    search_results = state["search_results"]
    query = state["query"]
    sentiment_scores = {}
    
    for country, results in search_results.items():
        if not results:
            sentiment_scores[country] = {
                "sentiment": "neutral",
                "score": 0.0,
                "positive_pct": 0.33,
                "negative_pct": 0.33,
                "neutral_pct": 0.34
            }
            continue
        
        # Combine search results
        combined_text = "\n\n".join([
            f"Title: {r.get('title', '')}\nContent: {r.get('content', '')}"
            for r in results[:5]
        ])
        
        prompt = f"""Analyze sentiment towards "{query}" in {country} based on these sources.

Sources:
{combined_text}

Return JSON with:
- sentiment: "positive", "negative", or "neutral"
- score: float from -1 (very negative) to +1 (very positive)
- positive_pct: percentage positive (0-1)
- negative_pct: percentage negative (0-1)
- neutral_pct: percentage neutral (0-1)
- key_points: list of 2-3 key findings

Example: {{"sentiment": "positive", "score": 0.6, "positive_pct": 0.7, "negative_pct": 0.1, "neutral_pct": 0.2, "key_points": ["Strong support from government", "Public opinion divided"]}}"""
        
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        sentiment_scores[country] = json.loads(response.choices[0].message.content)
    
    return {
        "sentiment_scores": sentiment_scores,
        "execution_log": state.get("execution_log", []) + [{
            "step": "sentiment_scorer",
            "action": f"Scored sentiment for {len(sentiment_scores)} countries"
        }]
    }
```

#### **`nodes/bias_detector.py`** - Bias Detection

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from typing import Dict, Any
from openai import AsyncOpenAI
from ..config import MODEL, TEMPERATURE, BIAS_TYPES
from ..state import SentimentAnalyzerState
import json

client = AsyncOpenAI()

async def bias_detector(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Detect bias types in coverage"""
    
    search_results = state["search_results"]
    query = state["query"]
    bias_analysis = {}
    
    for country, results in search_results.items():
        if not results:
            bias_analysis[country] = {"bias_types": [], "overall_bias": "none"}
            continue
        
        combined_text = "\n\n".join([
            f"Source: {r.get('url', '')}\nTitle: {r.get('title', '')}\nContent: {r.get('content', '')}"
            for r in results[:3]
        ])
        
        prompt = f"""Analyze bias in coverage of "{query}" from {country}.

Detect these bias types:
{', '.join(BIAS_TYPES)}

Sources:
{combined_text}

Return JSON with:
- bias_types: list of detected bias types
- overall_bias: "left", "right", "center", or "mixed"
- bias_score: float from -1 (left) to +1 (right)
- examples: list of specific biased phrases/framing

Example: {{"bias_types": ["political_lean", "framing_bias"], "overall_bias": "left", "bias_score": -0.4, "examples": ["Government-backed sources dominate", "Positive framing of policy"]}}"""
        
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        bias_analysis[country] = json.loads(response.choices[0].message.content)
    
    return {
        "bias_analysis": bias_analysis,
        "execution_log": state.get("execution_log", []) + [{
            "step": "bias_detector",
            "action": f"Detected bias for {len(bias_analysis)} countries"
        }]
    }
```

#### **`nodes/synthesizer.py`** - Result Synthesis

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from typing import Dict, Any
from openai import AsyncOpenAI
from ..config import MODEL, TEMPERATURE
from ..state import SentimentAnalyzerState
import json

client = AsyncOpenAI()

async def synthesizer(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Synthesize final response"""
    
    query = state["query"]
    sentiment_scores = state["sentiment_scores"]
    bias_analysis = state["bias_analysis"]
    
    prompt = f"""Create a comprehensive sentiment analysis report.

Query: {query}

Sentiment Scores:
{json.dumps(sentiment_scores, indent=2)}

Bias Analysis:
{json.dumps(bias_analysis, indent=2)}

Create a report with:
1. Executive summary (2-3 sentences)
2. Country-by-country breakdown
3. Key patterns and differences
4. Bias findings
5. Overall confidence assessment

Format as markdown.
"""
    
    response = await client.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}]
    )
    
    summary = response.choices[0].message.content
    
    # Extract key findings
    key_findings = []
    for country, scores in sentiment_scores.items():
        key_findings.append(f"{country}: {scores['sentiment']} (score: {scores['score']:.2f})")
    
    # Calculate confidence
    valid_scores = [s for s in sentiment_scores.values() if s.get('score') is not None]
    confidence = len(valid_scores) / len(sentiment_scores) if sentiment_scores else 0.0
    
    return {
        "summary": summary,
        "key_findings": key_findings,
        "confidence": confidence,
        "execution_log": state.get("execution_log", []) + [{
            "step": "synthesizer",
            "action": "Generated final report"
        }]
    }
```

#### **`nodes/visualizer.py`** - Artifact Generation

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from typing import Dict, Any
import plotly.express as px
import plotly.graph_objects as go
from ..config import ARTIFACT_DIR, MAP_COLOR_SCALE
from ..state import SentimentAnalyzerState
import uuid
from datetime import datetime

async def visualizer(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Generate 4 artifact types"""
    
    sentiment_scores = state["sentiment_scores"]
    artifacts = []
    
    # Artifact 1: Global Sentiment Map (Choropleth)
    artifact_id_map = f"sentiment_map_{uuid.uuid4().hex[:12]}"
    
    countries_list = list(sentiment_scores.keys())
    scores_list = [sentiment_scores[c]['score'] for c in countries_list]
    
    fig_map = px.choropleth(
        locations=countries_list,
        locationmode="country names",
        color=scores_list,
        hover_name=countries_list,
        color_continuous_scale=MAP_COLOR_SCALE,
        range_color=[-1, 1],
        labels={"color": "Sentiment Score"},
        title=f"Sentiment Analysis: {state['query']}"
    )
    
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    html_path = os.path.join(ARTIFACT_DIR, f"{artifact_id_map}.html")
    png_path = os.path.join(ARTIFACT_DIR, f"{artifact_id_map}.png")
    
    fig_map.write_html(html_path)
    fig_map.write_image(png_path)
    
    artifacts.append({
        "artifact_id": artifact_id_map,
        "type": "sentiment_map",
        "title": "Global Sentiment Map",
        "html_path": html_path,
        "png_path": png_path
    })
    
    # Artifact 2: Radar Chart (Multi-dimensional comparison)
    artifact_id_radar = f"sentiment_radar_{uuid.uuid4().hex[:12]}"
    
    fig_radar = go.Figure()
    
    for country in countries_list:
        scores = sentiment_scores[country]
        fig_radar.add_trace(go.Scatterpolar(
            r=[scores['positive_pct'], scores['neutral_pct'], scores['negative_pct']],
            theta=['Positive', 'Neutral', 'Negative'],
            fill='toself',
            name=country
        ))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Sentiment Distribution by Country"
    )
    
    html_path = os.path.join(ARTIFACT_DIR, f"{artifact_id_radar}.html")
    png_path = os.path.join(ARTIFACT_DIR, f"{artifact_id_radar}.png")
    
    fig_radar.write_html(html_path)
    fig_radar.write_image(png_path)
    
    artifacts.append({
        "artifact_id": artifact_id_radar,
        "type": "radar_chart",
        "title": "Sentiment Distribution Radar",
        "html_path": html_path,
        "png_path": png_path
    })
    
    # Artifact 3: Bar Chart (Sentiment Scores)
    artifact_id_bar = f"sentiment_bar_{uuid.uuid4().hex[:12]}"
    
    fig_bar = px.bar(
        x=countries_list,
        y=scores_list,
        color=scores_list,
        color_continuous_scale=MAP_COLOR_SCALE,
        range_color=[-1, 1],
        labels={"x": "Country", "y": "Sentiment Score"},
        title="Sentiment Scores by Country"
    )
    
    html_path = os.path.join(ARTIFACT_DIR, f"{artifact_id_bar}.html")
    png_path = os.path.join(ARTIFACT_DIR, f"{artifact_id_bar}.png")
    
    fig_bar.write_html(html_path)
    fig_bar.write_image(png_path)
    
    artifacts.append({
        "artifact_id": artifact_id_bar,
        "type": "bar_chart",
        "title": "Sentiment Score Comparison",
        "html_path": html_path,
        "png_path": png_path
    })
    
    return {
        "artifacts": artifacts,
        "execution_log": state.get("execution_log", []) + [{
            "step": "visualizer",
            "action": f"Generated {len(artifacts)} artifacts"
        }]
    }
```

---

### Step 4: Graph Definition (`graph.py`)

**File:** `graph.py`

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from langgraph.graph import StateGraph, END
from .state import SentimentAnalyzerState
from .nodes.analyzer import query_analyzer
from .nodes.search_executor import search_executor
from .nodes.sentiment_scorer import sentiment_scorer
from .nodes.bias_detector import bias_detector
from .nodes.synthesizer import synthesizer
from .nodes.visualizer import visualizer

def create_sentiment_analyzer_graph():
    """Create sentiment analyzer LangGraph workflow"""
    
    workflow = StateGraph(SentimentAnalyzerState)
    
    # Add nodes
    workflow.add_node("analyzer", query_analyzer)
    workflow.add_node("search", search_executor)
    workflow.add_node("scorer", sentiment_scorer)
    workflow.add_node("bias_detector", bias_detector)
    workflow.add_node("synthesizer", synthesizer)
    workflow.add_node("visualizer", visualizer)
    
    # Define flow
    workflow.set_entry_point("analyzer")
    workflow.add_edge("analyzer", "search")
    workflow.add_edge("search", "scorer")
    workflow.add_edge("scorer", "bias_detector")
    workflow.add_edge("bias_detector", "synthesizer")
    workflow.add_edge("synthesizer", "visualizer")
    workflow.add_edge("visualizer", END)
    
    return workflow.compile()
```

---

### Step 5: Package Init (`__init__.py`)

**File:** `__init__.py`

```python
from .graph import create_sentiment_analyzer_graph
from .state import SentimentAnalyzerState

__all__ = ["create_sentiment_analyzer_graph", "SentimentAnalyzerState"]
```

---

### Step 6: Tests (`tests/test_agent.py`)

**File:** `tests/test_agent.py`

```python
import pytest
import asyncio
from ..graph import create_sentiment_analyzer_graph
from ..state import SentimentAnalyzerState

@pytest.mark.asyncio
async def test_sentiment_analyzer():
    """Test full sentiment analyzer flow"""
    
    graph = create_sentiment_analyzer_graph()
    
    initial_state: SentimentAnalyzerState = {
        "query": "nuclear energy policy",
        "countries": ["US", "France", "Germany"],
        "time_range_days": 7,
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
    
    # Assertions
    assert result["sentiment_scores"]
    assert len(result["sentiment_scores"]) == 3
    assert result["summary"]
    assert len(result["artifacts"]) >= 3
    assert result["confidence"] > 0

if __name__ == "__main__":
    asyncio.run(test_sentiment_analyzer())
```

---

## 🧪 Testing Locally

```bash
# Navigate to agent folder
cd backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer

# Run tests
python -m pytest tests/

# Test manually
python graph.py
```

---

## 📊 Expected Output

```json
{
  "summary": "Sentiment analysis shows divided opinion on nuclear energy...",
  "sentiment_scores": {
    "US": {"sentiment": "neutral", "score": 0.1, ...},
    "France": {"sentiment": "positive", "score": 0.7, ...},
    "Germany": {"sentiment": "negative", "score": -0.5, ...}
  },
  "artifacts": [
    {"artifact_id": "sentiment_map_abc123", "type": "sentiment_map", ...},
    {"artifact_id": "sentiment_radar_def456", "type": "radar_chart", ...},
    {"artifact_id": "sentiment_bar_ghi789", "type": "bar_chart", ...}
  ],
  "confidence": 0.95
}
```

---

## 🚀 Integration with Master Agent

Update `langgraph_master_agent/tools/sub_agent_caller.py`:

```python
from sub_agents.sentiment_analyzer import create_sentiment_analyzer_graph

async def call_sentiment_analyzer(self, query: str, countries: list = None, time_range_days: int = 7) -> Dict[str, Any]:
    """Call sentiment analyzer sub-agent"""
    
    graph = create_sentiment_analyzer_graph()
    
    initial_state = {
        "query": query,
        "countries": countries or [],
        "time_range_days": time_range_days,
        # ... rest of state
    }
    
    result = await graph.ainvoke(initial_state)
    return result
```

---

## ✅ Definition of Done

- [ ] All files created and functional
- [ ] Unit tests passing
- [ ] Generates 3+ artifact types (HTML + PNG)
- [ ] Response time <5 seconds (for 3-5 countries)
- [ ] Error handling for API failures
- [ ] Integration test with master agent passes
- [ ] Sample artifacts saved in `artifacts/` folder
- [ ] Code reviewed and merged

---

## 📞 Questions?

- **Architecture:** Ask tech lead before implementing
- **API Issues:** Check Tavily/OpenAI rate limits
- **Visualization:** See Plotly docs for chart customization

**Estimated Time:** 2-3 days (2 developers)

