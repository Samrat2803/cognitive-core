# Fact Checker Agent

## 🎯 Purpose
Verify political claims using multi-source cross-referencing and evidence chain construction.

---

## 📦 Input/Output

**Input:** Political claim or statement to verify  
**Output:** Verification report with truth score + evidence chain

**Example Query:**
```
"Verify: Country X increased defense spending by 40% in 2024"
"Fact-check: Prime Minister said unemployment is at record low"
"Is it true that the new policy reduced emissions by 30%?"
```

**Artifacts:**
- Truth score card (gauge chart)
- Evidence chain network (claim → sources → verification)
- Source credibility matrix (heatmap)
- Timeline verification chart (events on timeline)

---

## 🏗️ Architecture

```
START → Claim Extractor → Multi-Source Search → Evidence Collector → 
Cross-Verification → Credibility Assessment → Verdict Generator → 
Visualizer → END
```

### Verification Process
1. **Extract core claim** (what exactly is being claimed?)
2. **Search multiple sources** (5-10 independent sources)
3. **Cross-reference facts** (do sources agree?)
4. **Check source credibility** (government data, news, opinion?)
5. **Verify timeline** (when did event occur?)
6. **Generate verdict** (True, Mostly True, Misleading, False, Unverified)

---

## 📋 Files to Create

1. **`main.py`** - ⭐ Standalone runner
2. **`state.py`** - State schema
3. **`config.py`** - Verdict categories, credibility scores
4. **`graph.py`** - LangGraph workflow
5. **`nodes/claim_extractor.py`** - Extract verifiable claims
6. **`nodes/searcher.py`** - Multi-source Tavily search (advanced mode)
7. **`nodes/evidence_collector.py`** - Extract supporting/contradicting evidence
8. **`nodes/cross_verifier.py`** - Compare sources for consistency
9. **`nodes/credibility_assessor.py`** - Score source reliability
10. **`nodes/verdict_generator.py`** - Final verdict with confidence
11. **`nodes/visualizer.py`** - Generate artifacts
12. **`tests/test_agent.py`**

---

## 🔑 Key Configuration (`config.py`)

```python
# Verdict Categories
VERDICT_CATEGORIES = {
    "TRUE": {
        "score": 1.0,
        "color": "#2ECC71",  # Green
        "description": "Claim is accurate and supported by multiple credible sources"
    },
    "MOSTLY_TRUE": {
        "score": 0.75,
        "color": "#27AE60",
        "description": "Claim is largely accurate with minor inaccuracies or missing context"
    },
    "HALF_TRUE": {
        "score": 0.5,
        "color": "#F39C12",  # Orange
        "description": "Claim contains both accurate and inaccurate elements"
    },
    "MOSTLY_FALSE": {
        "score": 0.25,
        "color": "#E67E22",
        "description": "Claim is largely inaccurate but contains some truth"
    },
    "FALSE": {
        "score": 0.0,
        "color": "#E74C3C",  # Red
        "description": "Claim is factually incorrect or misleading"
    },
    "UNVERIFIED": {
        "score": None,
        "color": "#95A5A6",  # Gray
        "description": "Insufficient evidence to verify claim"
    }
}

# Source Credibility Tiers
SOURCE_CREDIBILITY = {
    "tier_1": {
        "score": 1.0,
        "types": ["government_data", "academic_research", "official_statistics"],
        "examples": ["census.gov", "worldbank.org", "peer-reviewed journals"]
    },
    "tier_2": {
        "score": 0.8,
        "types": ["established_news", "fact_checking_orgs"],
        "examples": ["reuters.com", "apnews.com", "factcheck.org"]
    },
    "tier_3": {
        "score": 0.6,
        "types": ["mainstream_media"],
        "examples": ["cnn.com", "bbc.com", "nytimes.com"]
    },
    "tier_4": {
        "score": 0.4,
        "types": ["opinion_pieces", "blogs", "social_media"]
    }
}

# Cross-Verification Thresholds
MIN_SOURCES_FOR_VERIFICATION = 3
CONSENSUS_THRESHOLD = 0.7  # 70% of sources must agree
```

---

## 🔍 Key Node: Cross-Verifier (`nodes/cross_verifier.py`)

```python
from typing import Dict, List, Any
from openai import AsyncOpenAI
import json

async def cross_verify_evidence(claim: str, evidence_by_source: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Cross-reference evidence from multiple sources
    
    Returns:
        {
            "consensus_level": 0.8,  # 80% agreement
            "supporting_sources": 4,
            "contradicting_sources": 1,
            "neutral_sources": 0,
            "key_agreements": ["All sources confirm date", ...],
            "key_disagreements": ["Numbers differ by source", ...],
            "verdict_suggestion": "MOSTLY_TRUE"
        }
    """
    
    client = AsyncOpenAI()
    
    # Prepare evidence summary
    evidence_summary = "\n\n".join([
        f"Source {i+1} ({source}):\n" + "\n".join(f"- {e}" for e in evidence)
        for i, (source, evidence) in enumerate(evidence_by_source.items())
    ])
    
    prompt = f"""Cross-verify this claim using evidence from multiple sources:

CLAIM: {claim}

EVIDENCE FROM SOURCES:
{evidence_summary}

Analyze:
1. How many sources support the claim?
2. How many contradict it?
3. What do sources agree on?
4. Where do they disagree?
5. What's the consensus level (0-1)?
6. Suggested verdict: TRUE, MOSTLY_TRUE, HALF_TRUE, MOSTLY_FALSE, FALSE, or UNVERIFIED

Return JSON with these fields."""
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)
```

---

## 🎨 Key Artifacts

### 1. Truth Score Gauge

```python
import plotly.graph_objects as go

def create_truth_gauge(verdict: str, confidence: float):
    """
    Create gauge chart showing truth score
    """
    
    verdict_data = VERDICT_CATEGORIES[verdict]
    score = verdict_data["score"] if verdict_data["score"] is not None else 0.5
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Truth Score: {verdict}", 'font': {'size': 24}},
        delta={'reference': 50, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#333333"},
            'bar': {'color': verdict_data["color"]},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#333333",
            'steps': [
                {'range': [0, 25], 'color': '#FFE0E0'},
                {'range': [25, 50], 'color': '#FFE5CC'},
                {'range': [50, 75], 'color': '#FFF5CC'},
                {'range': [75, 100], 'color': '#E0FFE0'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': confidence * 100
            }
        }
    ))
    
    fig.update_layout(height=400, font={'color': "#333333", 'family': "Arial"})
    
    return fig
```

### 2. Evidence Chain Network

```python
import networkx as nx
from pyvis.network import Network

def create_evidence_chain(claim: str, evidence_by_source: dict, verdict: str):
    """
    Network showing: Claim → Sources → Evidence → Verdict
    """
    
    G = nx.DiGraph()
    
    # Central claim node
    G.add_node("CLAIM", type="claim", label=claim[:50] + "...")
    
    # Source nodes
    for source, evidence_list in evidence_by_source.items():
        G.add_node(source, type="source")
        G.add_edge("CLAIM", source, relation="verified_by")
        
        # Evidence nodes
        for i, evidence in enumerate(evidence_list[:3]):  # Top 3 pieces
            evidence_id = f"{source}_evidence_{i}"
            G.add_node(evidence_id, type="evidence", label=evidence[:30] + "...")
            G.add_edge(source, evidence_id, relation="provides")
    
    # Verdict node
    G.add_node("VERDICT", type="verdict", label=verdict)
    for source in evidence_by_source.keys():
        G.add_edge(source, "VERDICT", relation="leads_to")
    
    # Create PyVis network
    net = Network(height="600px", width="100%", directed=True)
    
    # Node colors by type
    colors = {
        "claim": "#d9f378",
        "source": "#5d535c",
        "evidence": "#333333",
        "verdict": VERDICT_CATEGORIES[verdict]["color"]
    }
    
    for node, data in G.nodes(data=True):
        net.add_node(
            node,
            label=data.get("label", node),
            color=colors[data["type"]],
            size=30 if data["type"] == "claim" else 20
        )
    
    for source, target, data in G.edges(data=True):
        net.add_edge(source, target, title=data["relation"])
    
    return net
```

### 3. Source Credibility Matrix

```python
import plotly.graph_objects as go

def create_credibility_matrix(sources_credibility: dict):
    """
    Heatmap showing source credibility scores
    """
    
    sources = list(sources_credibility.keys())
    metrics = ["Tier", "Fact Record", "Bias Score", "Overall"]
    
    values = [
        [sources_credibility[s][m] for s in sources]
        for m in metrics
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=values,
        x=sources,
        y=metrics,
        colorscale='RdYlGn',
        text=[[f"{v:.2f}" for v in row] for row in values],
        texttemplate="%{text}",
        textfont={"size": 12},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Source Credibility Assessment",
        xaxis_title="Source",
        yaxis_title="Metric",
        height=400
    )
    
    return fig
```

---

## 🧪 Standalone Testing

```bash
cd backend_v2/langgraph_master_agent/sub_agents/fact_checker
python main.py
```

**Test Claims:**
- "India's GDP grew by 7.2% in 2023"
- "Renewable energy provides 40% of EU electricity"
- "Country X has the highest inflation rate in 50 years"

---

## ⚠️ Important Considerations

### Handling Unverifiable Claims
- Opinion statements ("Policy X is bad")
- Future predictions ("Economy will crash")
- Subjective claims ("Most people believe...")

### Confidence Scoring
```python
confidence = min(
    source_count / MIN_SOURCES_FOR_VERIFICATION,
    consensus_level,
    avg_source_credibility
)
```

### Limitations to Document
- Can't verify claims requiring specialized expertise
- Relies on publicly available information
- May miss very recent events (search lag)
- Subject to source availability

---

## ✅ Definition of Done

- [ ] Extracts verifiable claims from input
- [ ] Searches 5+ independent sources
- [ ] Cross-verifies evidence
- [ ] Assesses source credibility
- [ ] Generates verdict with confidence score
- [ ] Creates 4 artifact types
- [ ] Works standalone
- [ ] Response time <8s
- [ ] Handles edge cases (unverifiable, insufficient data)
- [ ] Tests passing

**Effort:** 4-5 days (2 developers)  
**Impact:** ⭐⭐⭐⭐⭐ Very High - **Highest trust value** for users

