# Comparative Analysis Agent

## 🎯 Purpose
Compare multiple entities (countries, policies, politicians) across multiple dimensions.

---

## 📦 Input/Output

**Input:** List of entities to compare + comparison dimensions  
**Output:** Multi-dimensional comparison with 4+ artifact types

**Example Query:**
```
"Compare India's and China's climate policies"
"Compare Biden vs Trump immigration positions"
```

**Artifacts:**
- Multi-dimensional radar chart
- Side-by-side comparison table
- Diverging bar chart (differences)
- Statistical significance report

---

## 🏗️ Architecture

```
START → Entity Extractor → Data Collector (reuse Sentiment + Bias agents) → 
Normalizer → Comparator → Statistical Analyzer → Visualizer → END
```

### Key Innovation
**Reuses existing agents:** Calls Sentiment Analyzer and Bias Detector for each entity, then compares results.

---

## 📋 Files to Create

1. **`main.py`** - ⭐ Standalone runner (test without master)
2. **`state.py`** - State schema
3. **`config.py`** - Config
4. **`graph.py`** - LangGraph workflow
5. **`nodes/entity_extractor.py`** - Extract entities from query
6. **`nodes/data_collector.py`** - Call other agents for data
7. **`nodes/normalizer.py`** - Normalize scores for comparison
8. **`nodes/comparator.py`** - Identify similarities/differences
9. **`nodes/visualizer.py`** - Generate radar chart, tables
10. **`tests/test_agent.py`** - Unit tests

---

## 🎨 Key Artifacts

### 1. Radar Chart (Multi-dimensional)
```python
import plotly.graph_objects as go

fig = go.Figure()

for entity in entities:
    fig.add_trace(go.Scatterpolar(
        r=[scores[entity][dim] for dim in dimensions],
        theta=dimensions,
        fill='toself',
        name=entity
    ))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    title="Multi-Dimensional Comparison"
)
```

### 2. Comparison Table (Side-by-side)
```python
import plotly.graph_objects as go

fig = go.Figure(data=[go.Table(
    header=dict(values=['Dimension'] + entities),
    cells=dict(values=[
        dimensions,
        [scores[entity] for entity in entities]
    ])
)])
```

---

## 🧪 Standalone Testing

```bash
cd backend_v2/langgraph_master_agent/sub_agents/comparative_analysis
python main.py
```

**Test Queries:**
- "Compare US vs China economic policies"
- "Compare Modi vs Khan leadership styles"
- "Compare EU vs UK post-Brexit policies"

---

## 🔌 Integration Points

**Dependencies:**
- Sentiment Analyzer (optional, for sentiment dimension)
- Media Bias Detector (optional, for bias dimension)
- Tavily Search (for factual data)

**Called by:** Master agent when query contains "compare", "vs", "versus", "difference between"

---

## ✅ Definition of Done

- [ ] Compares 2-5 entities
- [ ] Works standalone (no master agent)
- [ ] Generates 4 artifact types
- [ ] Response time <5s
- [ ] Can reuse other agents' data
- [ ] Tests passing

**Effort:** 1-2 days (1 developer)  
**Impact:** ⭐⭐⭐⭐ High - natural extension of existing agents

