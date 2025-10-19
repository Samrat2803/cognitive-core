# RSS Realtime Monitor Sub-Agent

**Status:** ✅ Standalone Ready | ⏸️ Integration Pending

Real-time news monitoring using RSS feeds, semantic clustering, and explosiveness scoring.

## Features

- 🔄 **MongoDB-backed RSS polling** with 48h TTL
- 🧠 **Semantic keyword filtering** using embeddings
- 🎯 **DBSCAN topic clustering** (auto-detects topic count)
- 📊 **Explosiveness scoring** (velocity + diversity + recency)
- 🏷️ **TF-IDF topic labeling**
- 👤 **LLM entity extraction** (people, companies, locations)
- ✅ **Zero filtering** (scores and sorts, doesn't filter)

## Architecture

```
Input: keywords, regions, categories
  ↓
[1] Load articles from MongoDB (24-48h window)
  ↓
[2] Filter by keywords (semantic + exact match)
  ↓
[3] Cluster into topics (DBSCAN)
  ↓
[4] Generate topic labels (TF-IDF)
  ↓
[5] Score explosiveness (0-100)
  ↓
[6] Extract entities (LLM)
  ↓
Output: Ranked explosive topics
```

## Usage

### Standalone

```bash
cd rss_realtime_monitor

# Default keywords
python main.py

# Custom keywords
python main.py "TikTok, ban, ByteDance"

# With filters
python main.py "AI regulation" --regions "United States" --categories "technology"

# Limit results
python main.py "climate change" --max-topics 5
```

### As Sub-Agent (After Integration)

```python
from rss_realtime_monitor import create_rss_realtime_monitor_graph

graph = create_rss_realtime_monitor_graph()

result = await graph.ainvoke({
    "keywords": ["TikTok", "ban"],
    "regions": ["United States"],
    "categories": ["technology"],
    "max_topics": 10,
    # ... initialize all state fields
})

explosive_topics = result["explosive_topics"]
```

## Output Format

```json
{
  "explosive_topics": [
    {
      "rank": 1,
      "label": "TikTok Ban | ByteDance | Legislation",
      "article_count": 18,
      "velocity": 3.0,
      "avg_age_hours": 4.2,
      "explosiveness_score": 92,
      "score_breakdown": {
        "velocity": 40,
        "recency": 18,
        "diversity": 18,
        "geographic": 8,
        "relevance": 8
      },
      "sources": ["Reuters", "Bloomberg", "CNN"],
      "regions": ["United States", "Europe"],
      "entities": {
        "people": ["Biden", "Xi"],
        "companies": ["ByteDance", "TikTok"],
        "locations": ["Washington", "Beijing"]
      },
      "headlines": [...],
      "ready_for_tavily": true
    }
  ]
}
```

## Dependencies

```bash
pip install feedparser pymongo sentence-transformers scikit-learn langgraph openai python-dotenv
```

## Environment Variables

```bash
MONGODB_URI=mongodb+srv://...
OPENAI_API_KEY=sk-...
```

## Integration Checklist

- [x] Phase 1: Shared tools (rss_sources, rss_collector, rss_embedder)
- [x] Phase 2: Sub-agent nodes (all 6 nodes)
- [x] Phase 3: Standalone testing
- [ ] Phase 4: Integration with exp_2 master agent

## Scoring Algorithm

**Explosiveness Score (0-100):**

- **Velocity (40 pts)**: Articles per hour in last 6 hours
  - 2+/hr = 40pts, 1/hr = 20pts, 0.5/hr = 10pts

- **Recency (20 pts)**: Average article age
  - <3h = 20pts, <6h = 15pts, <12h = 10pts, <24h = 5pts

- **Diversity (20 pts)**: Unique sources
  - 10+ sources = 20pts, 5 = 10pts, 2 = 4pts

- **Geographic (10 pts)**: Regional spread
  - 5+ regions = 10pts, 3 = 6pts, 1 = 2pts

- **Relevance (10 pts)**: Keyword match quality
  - Semantic similarity score

**Tavily Readiness**: Score > 70 → `ready_for_tavily: true`

## Notes

- No velocity filtering - topics are sorted, not filtered
- 48-hour lookback is fixed (not user-configurable)
- Embeddings created on-demand and cached in MongoDB
- Deduplication handled at RSS feed level (by URL)

