# Media Bias Detector Agent

## 🎯 Purpose

Analyzes how different media sources cover the same political event/topic, detects framing bias, political lean, and loaded language usage.

---

## 📦 What This Agent Does

**Input:** Political topic/event to analyze  
**Output:** Multi-source bias analysis + 4 artifact types

**Example Query:**
```
"Compare how different media outlets covered the recent climate summit"
```

**Example Output:**
- Bias spectrum chart (left-center-right positioning)
- Source comparison matrix
- Loaded language word cloud
- Framing analysis report

---

## 🏗️ Architecture

### LangGraph Workflow
```
START → Query Analyzer → Multi-Source Search → Content Extractor → 
Bias Classifier → Language Analyzer → Synthesizer → Visualizer → END
```

###Files to Create

1. **`__init__.py`**
2. **`state.py`** - State schema
3. **`config.py`** - Configuration
4. **`graph.py`** - LangGraph workflow
5. **`nodes/query_analyzer.py`** - Query understanding
6. **`nodes/source_searcher.py`** - Search across multiple sources
7. **`nodes/bias_classifier.py`** - Political lean classification
8. **`nodes/language_analyzer.py`** - Detect loaded language
9. **`nodes/framing_analyzer.py`** - How story is framed
10. **`nodes/synthesizer.py`** - Final report
11. **`nodes/visualizer.py`** - Generate artifacts
12. **`tests/test_agent.py`**

---

## 📋 Implementation Steps

### Step 1: State Schema (`state.py`)

```python
from typing import TypedDict, List, Dict, Any, Optional

class MediaBiasDetectorState(TypedDict):
    """State for Media Bias Detector Agent"""
    
    # Input
    query: str                              # Topic to analyze
    sources: Optional[List[str]]            # Specific sources (optional)
    time_range_days: int                    # Default: 7
    
    # Search Results
    articles_by_source: Dict[str, List[Dict]]  # {source: [articles]}
    
    # Analysis
    bias_classification: Dict[str, Dict]    # {source: {lean, score, confidence}}
    loaded_language: Dict[str, List[str]]   # {source: [biased phrases]}
    framing_analysis: Dict[str, Dict]       # {source: {frame_type, examples}}
    
    # Comparison
    consensus_points: List[str]             # What all sources agree on
    divergence_points: List[str]            # Where sources disagree
    omission_analysis: Dict[str, List[str]] # What each source omits
    
    # Synthesis
    summary: str
    key_findings: List[str]
    confidence: float
    
    # Artifacts
    artifacts: List[Dict[str, Any]]
    
    # Metadata
    execution_log: List[Dict[str, str]]
    error_log: List[str]
```

---

### Step 2: Configuration (`config.py`)

```python
import os

# LLM Configuration
MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
TEMPERATURE = 0

# Sources to Analyze (if not specified by user)
DEFAULT_SOURCES = [
    "cnn.com",
    "foxnews.com",
    "bbc.com",
    "reuters.com",
    "nytimes.com"
]

# Search Configuration
MAX_SOURCES = 8
MAX_ARTICLES_PER_SOURCE = 3
DEFAULT_TIME_RANGE_DAYS = 7
SEARCH_DEPTH = "advanced"  # More thorough for media analysis

# Bias Classification
BIAS_SPECTRUM = {
    "far_left": -1.0,
    "left": -0.5,
    "center_left": -0.25,
    "center": 0.0,
    "center_right": 0.25,
    "right": 0.5,
    "far_right": 1.0
}

# Loaded Language Categories
LOADED_LANGUAGE_TYPES = [
    "emotionally_charged",
    "sensationalist",
    "fear_based",
    "propaganda_terms",
    "euphemisms",
    "dysphemisms"
]

# Framing Types
FRAMING_TYPES = [
    "conflict_frame",      # Us vs them
    "human_interest",      # Personal stories
    "economic",            # Financial impact
    "morality",            # Right vs wrong
    "responsibility",      # Who's to blame
    "progress"             # Innovation/change
]

# Visualization
ARTIFACT_DIR = "../../../artifacts/"
BIAS_COLOR_SCALE = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D"]  # Blue to Red spectrum
```

---

### Key Node: Bias Classifier (`nodes/bias_classifier.py`)

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from typing import Dict, Any
from openai import AsyncOpenAI
from ..config import MODEL, TEMPERATURE, BIAS_SPECTRUM
from ..state import MediaBiasDetectorState
import json

client = AsyncOpenAI()

async def bias_classifier(state: MediaBiasDetectorState) -> Dict[str, Any]:
    """Classify political lean of each source"""
    
    articles_by_source = state["articles_by_source"]
    query = state["query"]
    bias_classification = {}
    
    for source, articles in articles_by_source.items():
        if not articles:
            continue
        
        combined_text = "\n\n".join([
            f"Title: {a.get('title', '')}\nContent: {a.get('content', '')}"
            for a in articles[:3]
        ])
        
        prompt = f"""Analyze the political bias of {source} in their coverage of "{query}".

Articles:
{combined_text}

Classify their bias:
- Spectrum: far_left, left, center_left, center, center_right, right, far_right
- Bias score: -1.0 (far left) to +1.0 (far right)
- Confidence: 0.0 to 1.0
- Evidence: Specific examples showing bias
- Techniques: Bias techniques used (selective quotes, loaded language, etc.)

Return JSON: {{"spectrum": "center_left", "bias_score": -0.25, "confidence": 0.8, "evidence": ["example1", "example2"], "techniques": ["selective_quoting"]}}"""
        
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        bias_classification[source] = json.loads(response.choices[0].message.content)
    
    return {
        "bias_classification": bias_classification,
        "execution_log": state.get("execution_log", []) + [{
            "step": "bias_classifier",
            "action": f"Classified bias for {len(bias_classification)} sources"
        }]
    }
```

---

### Key Node: Language Analyzer (`nodes/language_analyzer.py`)

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from typing import Dict, Any
from openai import AsyncOpenAI
from ..config import MODEL, TEMPERATURE, LOADED_LANGUAGE_TYPES
from ..state import MediaBiasDetectorState
import json

client = AsyncOpenAI()

async def language_analyzer(state: MediaBiasDetectorState) -> Dict[str, Any]:
    """Detect loaded/biased language in articles"""
    
    articles_by_source = state["articles_by_source"]
    loaded_language = {}
    
    for source, articles in articles_by_source.items():
        if not articles:
            continue
        
        combined_text = "\n\n".join([
            f"{a.get('title', '')}\n{a.get('content', '')}"
            for a in articles[:3]
        ])
        
        prompt = f"""Identify loaded/biased language from {source}.

Types to detect: {', '.join(LOADED_LANGUAGE_TYPES)}

Text:
{combined_text}

Extract:
- Biased phrases with their category
- Context for each phrase
- Why it's biased

Return JSON: {{"loaded_phrases": [{{"phrase": "regime", "type": "dysphemism", "context": "referring to government", "why_biased": "negative connotation"}}]}}"""
        
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        loaded_language[source] = [p["phrase"] for p in result.get("loaded_phrases", [])]
    
    return {
        "loaded_language": loaded_language,
        "execution_log": state.get("execution_log", []) + [{
            "step": "language_analyzer",
            "action": f"Analyzed language for {len(loaded_language)} sources"
        }]
    }
```

---

### Key Artifact: Bias Spectrum Chart (`nodes/visualizer.py` excerpt)

```python
import plotly.graph_objects as go

def create_bias_spectrum_chart(bias_classification, artifact_dir):
    """Create horizontal bias spectrum chart"""
    
    sources = list(bias_classification.keys())
    scores = [bias_classification[s]["bias_score"] for s in sources]
    
    # Create diverging bar chart
    fig = go.Figure()
    
    colors = ['#2E86AB' if score < 0 else '#C73E1D' for score in scores]
    
    fig.add_trace(go.Bar(
        x=scores,
        y=sources,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{score:.2f}" for score in scores],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Media Bias Spectrum Analysis",
        xaxis=dict(
            title="Political Lean",
            range=[-1, 1],
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["Far Left", "Left", "Center", "Right", "Far Right"]
        ),
        yaxis=dict(title="Source"),
        showlegend=False,
        height=400 + len(sources) * 30
    )
    
    # Add vertical line at center
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
    
    artifact_id = f"bias_spectrum_{uuid.uuid4().hex[:12]}"
    html_path = os.path.join(artifact_dir, f"{artifact_id}.html")
    png_path = os.path.join(artifact_dir, f"{artifact_id}.png")
    
    fig.write_html(html_path)
    fig.write_image(png_path)
    
    return {
        "artifact_id": artifact_id,
        "type": "bias_spectrum",
        "title": "Media Bias Spectrum",
        "html_path": html_path,
        "png_path": png_path
    }
```

---

### Key Artifact: Word Cloud (`nodes/visualizer.py` excerpt)

```python
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def create_loaded_language_wordcloud(loaded_language, artifact_dir):
    """Create word cloud of biased terms"""
    
    all_phrases = []
    for source, phrases in loaded_language.items():
        all_phrases.extend(phrases)
    
    text = " ".join(all_phrases)
    
    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color='white',
        colormap='RdYlBu_r',  # Red for loaded language
        max_words=50
    ).generate(text)
    
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Loaded Language Across Sources', fontsize=16)
    
    artifact_id = f"loaded_language_{uuid.uuid4().hex[:12]}"
    png_path = os.path.join(artifact_dir, f"{artifact_id}.png")
    
    plt.savefig(png_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return {
        "artifact_id": artifact_id,
        "type": "word_cloud",
        "title": "Loaded Language Word Cloud",
        "png_path": png_path
    }
```

---

## 🧪 Testing

```bash
# Test query
python -m pytest tests/ -v

# Manual test
python graph.py
```

**Test Queries:**
- "Compare coverage of the recent election debate"
- "Analyze bias in climate change reporting"
- "How do sources cover immigration policy?"

---

## 📊 Expected Output

```json
{
  "summary": "Analysis of 5 sources shows significant bias variation...",
  "bias_classification": {
    "cnn.com": {"spectrum": "center_left", "bias_score": -0.3, ...},
    "foxnews.com": {"spectrum": "right", "bias_score": 0.6, ...},
    "reuters.com": {"spectrum": "center", "bias_score": 0.05, ...}
  },
  "loaded_language": {
    "cnn.com": ["regime", "controversial", ...],
    "foxnews.com": ["radical", "crisis", ...]
  },
  "artifacts": [
    {"type": "bias_spectrum", ...},
    {"type": "comparison_matrix", ...},
    {"type": "word_cloud", ...}
  ]
}
```

---

## ✅ Definition of Done

- [ ] Classifies bias on spectrum (-1 to +1)
- [ ] Detects loaded language
- [ ] Compares 3+ sources
- [ ] Generates 4 artifact types
- [ ] Response time <6 seconds
- [ ] Tests passing
- [ ] Code reviewed

**Estimated Time:** 2-3 days (2 developers)

