# Live Political Monitoring Agent

## 🎯 Purpose

**Foundational agent** that continuously monitors real-time political developments, identifies emerging topics, and feeds downstream agents (SitRep & Policy Brief generators).

This is the **"always-on" intelligence layer** that tracks:
- Breaking political news
- Legislative actions
- Diplomatic events  
- Policy announcements
- Election developments
- Crisis situations

---

## 📦 What This Agent Does

**Mode 1: Real-time Stream** (Background process)
- Continuously polls Tavily API every 5-15 minutes
- Identifies new/trending political topics
- Flags significant developments
- Stores in monitoring database

**Mode 2: On-Demand Query** (User-triggered)
- "What's happening in Middle East politics right now?"
- Returns curated list of current developments
- Grouped by region/topic/urgency

**Output:**
- **Structured event stream** (chronological feed)
- **Emerging topics list** (what's trending)
- **Significance scores** (urgency/importance ratings)
- **Topic clusters** (related events grouped)

---

## 🏗️ Architecture

### Real-Time Monitoring Loop
```
START → Search Latest News → Event Extraction → Deduplication → 
Significance Scoring → Topic Clustering → Storage → 
Alert Generation → END (repeat every 5-15 min)
```

### On-Demand Query Mode
```
START → Query Analysis → Time Range Selection → 
Retrieve Recent Events → Filter by Relevance → 
Topic Summarization → Return Structured Feed → END
```

---

## 📋 Files to Create

1. **`main.py`** - ⭐ Standalone runner (two modes: background loop, on-demand)
2. **`state.py`** - State schema
3. **`config.py`** - Monitoring settings, update frequency, regions
4. **`graph.py`** - LangGraph workflow
5. **`nodes/news_poller.py`** - Tavily polling with recency filter
6. **`nodes/event_extractor.py`** - Extract structured events from news
7. **`nodes/deduplicator.py`** - Remove duplicate/similar stories
8. **`nodes/significance_scorer.py`** - Score importance/urgency
9. **`nodes/topic_clusterer.py`** - Group related events
10. **`nodes/alert_generator.py`** - Generate alerts for major events
11. **`tools/event_storage.py`** - MongoDB storage for event stream
12. **`tools/trending_detector.py`** - Detect emerging topics
13. **`tests/test_agent.py`**

---

## 🔑 Key Configuration (`config.py`)

```python
import os

# Monitoring Settings
POLL_INTERVAL_MINUTES = 10  # How often to check for new developments
LOOKBACK_HOURS = 2          # Check news from last N hours
MAX_EVENTS_PER_POLL = 50    # Max events to process per cycle

# Geographic Regions to Monitor
MONITORING_REGIONS = [
    "Global",           # International developments
    "United States",
    "Europe",
    "Middle East",
    "Asia Pacific",
    "Latin America",
    "Africa"
]

# Topic Categories
MONITORING_TOPICS = [
    "elections",
    "legislation",
    "diplomacy",
    "conflicts",
    "economy",
    "protests",
    "policy_announcements",
    "leadership_changes",
    "scandals",
    "sanctions"
]

# Significance Scoring
SIGNIFICANCE_FACTORS = {
    "geographic_scope": {
        "local": 1,
        "national": 2,
        "regional": 3,
        "international": 4,
        "global": 5
    },
    "impact_level": {
        "minor": 1,
        "moderate": 2,
        "significant": 3,
        "major": 4,
        "critical": 5
    },
    "urgency": {
        "routine": 1,
        "developing": 2,
        "urgent": 3,
        "breaking": 4,
        "crisis": 5
    }
}

# Alert Thresholds
ALERT_THRESHOLD_SCORE = 12  # Combined score > 12 triggers alert
HIGH_PRIORITY_KEYWORDS = [
    "war", "coup", "assassination", "nuclear",
    "major election", "impeachment", "resignation",
    "terrorist attack", "military action"
]

# Storage
EVENT_DATABASE = "political_events"
EVENT_COLLECTION = "real_time_feed"
RETENTION_DAYS = 30  # Keep events for 30 days
```

---

## 🔍 Key Node: Event Extractor (`nodes/event_extractor.py`)

```python
"""
Extract structured events from news articles
"""

from typing import Dict, List, Any
from openai import AsyncOpenAI
import json
from datetime import datetime

client = AsyncOpenAI()

async def extract_events(articles: List[Dict]) -> List[Dict[str, Any]]:
    """
    Extract structured political events from news articles
    
    Returns: [
        {
            "event_id": "unique_id",
            "title": "US Senate passes infrastructure bill",
            "summary": "Brief 2-3 sentence summary",
            "event_type": "legislation",
            "regions": ["United States"],
            "entities": ["US Senate", "Infrastructure Bill"],
            "timestamp": "2025-10-02T14:30:00Z",
            "source_url": "https://...",
            "source_credibility": 0.85,
            "keywords": ["infrastructure", "senate", "legislation"]
        },
        ...
    ]
    """
    
    events = []
    
    for article in articles:
        prompt = f"""Extract a structured political event from this news article.

Title: {article.get('title', '')}
Content: {article.get('content', '')}
Published: {article.get('published_date', '')}
URL: {article.get('url', '')}

Extract:
- title: Clear event title (10 words max)
- summary: 2-3 sentence summary of what happened
- event_type: One of [elections, legislation, diplomacy, conflicts, economy, protests, policy_announcements, leadership_changes, scandals, sanctions]
- regions: List of affected regions/countries
- entities: Key people, organizations, countries involved
- keywords: 5-7 relevant keywords
- is_significant: true if major development, false if routine

Return JSON with these fields."""
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        event_data = json.loads(response.choices[0].message.content)
        
        # Add metadata
        event_data["event_id"] = f"evt_{datetime.now().timestamp()}_{hash(article['url'])}"
        event_data["timestamp"] = article.get('published_date', datetime.now().isoformat())
        event_data["source_url"] = article.get('url', '')
        event_data["source_credibility"] = article.get('score', 0.7)
        
        events.append(event_data)
    
    return events
```

---

## 🎯 Key Node: Significance Scorer (`nodes/significance_scorer.py`)

```python
"""
Score political events by significance
"""

from typing import Dict, Any
from ..config import SIGNIFICANCE_FACTORS, HIGH_PRIORITY_KEYWORDS
from openai import AsyncOpenAI
import json

client = AsyncOpenAI()

async def score_significance(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate significance score (0-15) based on:
    - Geographic scope (1-5)
    - Impact level (1-5)
    - Urgency (1-5)
    
    Returns: event with added fields:
        - significance_score: int (0-15)
        - significance_breakdown: dict
        - is_high_priority: bool
        - alert_level: "routine" | "monitor" | "alert" | "urgent"
    """
    
    # Quick keyword check for high priority
    contains_priority_keyword = any(
        keyword.lower() in event.get('title', '').lower() or 
        keyword.lower() in event.get('summary', '').lower()
        for keyword in HIGH_PRIORITY_KEYWORDS
    )
    
    # LLM-based significance assessment
    prompt = f"""Assess the political significance of this event:

Title: {event['title']}
Summary: {event['summary']}
Type: {event['event_type']}
Regions: {', '.join(event.get('regions', []))}
Entities: {', '.join(event.get('entities', []))}

Rate on 1-5 scale:
1. Geographic scope: local(1), national(2), regional(3), international(4), global(5)
2. Impact level: minor(1), moderate(2), significant(3), major(4), critical(5)
3. Urgency: routine(1), developing(2), urgent(3), breaking(4), crisis(5)

Also provide:
- rationale: Why this score?
- implications: What could this lead to?
- monitoring_recommendations: What to watch for next?

Return JSON."""
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    scoring = json.loads(response.choices[0].message.content)
    
    # Calculate total score
    total_score = (
        scoring.get('geographic_scope', 2) +
        scoring.get('impact_level', 2) +
        scoring.get('urgency', 2)
    )
    
    # Boost if contains high-priority keywords
    if contains_priority_keyword:
        total_score = min(15, total_score + 3)
    
    # Determine alert level
    if total_score >= 12:
        alert_level = "urgent"
    elif total_score >= 9:
        alert_level = "alert"
    elif total_score >= 6:
        alert_level = "monitor"
    else:
        alert_level = "routine"
    
    event["significance_score"] = total_score
    event["significance_breakdown"] = scoring
    event["is_high_priority"] = total_score >= 9
    event["alert_level"] = alert_level
    
    return event
```

---

## 🗄️ Key Tool: Event Storage (`tools/event_storage.py`)

```python
"""
MongoDB storage for real-time event stream
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pymongo import MongoClient
import os

class EventStorage:
    """Stores and retrieves political events"""
    
    def __init__(self):
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(mongo_uri)
        self.db = self.client["political_events"]
        self.collection = self.db["real_time_feed"]
        
        # Create indexes
        self.collection.create_index("event_id", unique=True)
        self.collection.create_index("timestamp")
        self.collection.create_index("significance_score")
        self.collection.create_index("regions")
        self.collection.create_index("event_type")
    
    async def store_events(self, events: List[Dict]) -> int:
        """Store new events (skip duplicates)"""
        stored_count = 0
        
        for event in events:
            try:
                self.collection.update_one(
                    {"event_id": event["event_id"]},
                    {"$set": event},
                    upsert=True
                )
                stored_count += 1
            except Exception as e:
                print(f"Error storing event: {e}")
        
        return stored_count
    
    async def get_recent_events(
        self,
        hours: int = 24,
        region: Optional[str] = None,
        event_type: Optional[str] = None,
        min_significance: int = 0,
        limit: int = 50
    ) -> List[Dict]:
        """Retrieve recent events with filters"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        query = {
            "timestamp": {"$gte": cutoff_time.isoformat()},
            "significance_score": {"$gte": min_significance}
        }
        
        if region:
            query["regions"] = region
        
        if event_type:
            query["event_type"] = event_type
        
        events = list(
            self.collection
            .find(query)
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        # Remove MongoDB _id field
        for event in events:
            event.pop("_id", None)
        
        return events
    
    async def get_trending_topics(self, hours: int = 24) -> List[Dict]:
        """Get trending topics (most mentioned entities/keywords)"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_time.isoformat()}}},
            {"$unwind": "$keywords"},
            {"$group": {
                "_id": "$keywords",
                "count": {"$sum": 1},
                "avg_significance": {"$avg": "$significance_score"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ]
        
        return list(self.collection.aggregate(pipeline))
    
    async def cleanup_old_events(self, days: int = 30):
        """Remove events older than N days"""
        
        cutoff_time = datetime.now() - timedelta(days=days)
        
        result = self.collection.delete_many({
            "timestamp": {"$lt": cutoff_time.isoformat()}
        })
        
        return result.deleted_count
```

---

## 🔄 Background Monitoring Mode (`main.py`)

```python
"""
Live Political Monitor - Continuous Background Mode
"""

import asyncio
from datetime import datetime
from graph import create_live_monitor_graph
from state import LiveMonitorState
from tools.event_storage import EventStorage
from config import POLL_INTERVAL_MINUTES, LOOKBACK_HOURS

async def background_monitor():
    """
    Run continuous monitoring loop
    This would run as a background service
    """
    
    graph = create_live_monitor_graph()
    storage = EventStorage()
    
    print("🔴 LIVE POLITICAL MONITOR - Starting...")
    print(f"Poll interval: Every {POLL_INTERVAL_MINUTES} minutes")
    print(f"Lookback window: {LOOKBACK_HOURS} hours")
    print("=" * 70)
    
    cycle_count = 0
    
    while True:
        cycle_count += 1
        cycle_start = datetime.now()
        
        print(f"\n🔄 Cycle {cycle_count} - {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Run monitoring cycle
            initial_state: LiveMonitorState = {
                "lookback_hours": LOOKBACK_HOURS,
                "regions": [],  # Monitor all regions
                "events": [],
                "high_priority_events": [],
                "trending_topics": [],
                "alerts": [],
                "execution_log": []
            }
            
            result = await graph.ainvoke(initial_state)
            
            # Store events
            if result["events"]:
                stored = await storage.store_events(result["events"])
                print(f"   📥 Stored {stored} new events")
            
            # Report high-priority events
            if result["high_priority_events"]:
                print(f"   🚨 {len(result['high_priority_events'])} high-priority events detected:")
                for event in result["high_priority_events"][:3]:
                    print(f"      - {event['title']} (score: {event['significance_score']})")
            
            # Report trending topics
            if result["trending_topics"]:
                print(f"   📈 Trending: {', '.join(result['trending_topics'][:5])}")
            
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            print(f"   ✅ Cycle completed in {cycle_duration:.1f}s")
            
        except Exception as e:
            print(f"   ❌ Error in monitoring cycle: {e}")
        
        # Wait until next cycle
        wait_seconds = POLL_INTERVAL_MINUTES * 60
        print(f"   ⏸️  Sleeping for {POLL_INTERVAL_MINUTES} minutes...")
        await asyncio.sleep(wait_seconds)

if __name__ == "__main__":
    # Run as background service
    asyncio.run(background_monitor())
```

---

## 📊 Output Format (Structured Event Stream)

```json
{
  "events": [
    {
      "event_id": "evt_1696284600_abc123",
      "title": "US Senate Passes Infrastructure Bill",
      "summary": "The Senate approved a $1.2 trillion infrastructure package with bipartisan support. The bill now moves to the House for final approval before reaching the President's desk.",
      "event_type": "legislation",
      "regions": ["United States"],
      "entities": ["US Senate", "Infrastructure Bill", "Biden Administration"],
      "timestamp": "2025-10-02T14:30:00Z",
      "source_url": "https://reuters.com/...",
      "source_credibility": 0.92,
      "keywords": ["infrastructure", "bipartisan", "senate", "legislation"],
      "significance_score": 11,
      "significance_breakdown": {
        "geographic_scope": 4,
        "impact_level": 4,
        "urgency": 3,
        "rationale": "Major legislative achievement with national impact",
        "implications": "Could boost construction sector, influence 2026 elections"
      },
      "is_high_priority": true,
      "alert_level": "alert"
    }
  ],
  "high_priority_events": [...],  // Events with score >= 9
  "trending_topics": ["infrastructure", "election", "sanctions"],
  "alerts": [
    {
      "title": "Breaking: Major Policy Shift in Middle East",
      "urgency": "urgent",
      "timestamp": "2025-10-02T15:00:00Z"
    }
  ]
}
```

---

## 🔌 Integration with Other Agents

### Consumed By:
1. **SitRep Generator** - Pulls events from last 24 hours for daily brief
2. **Policy Brief Generator** - Pulls related events for context/background
3. **Master Agent** - Provides real-time awareness

### Integration Method:
```python
# From SitRep or Policy Brief agents
from sub_agents.live_political_monitor.tools.event_storage import EventStorage

storage = EventStorage()
recent_events = await storage.get_recent_events(
    hours=24,
    region="Middle East",
    min_significance=6
)
```

---

## 🧪 Testing

### Standalone Test (One-time poll)
```bash
cd backend_v2/langgraph_master_agent/sub_agents/live_political_monitor
python main.py --mode single
```

### Background Test (Continuous)
```bash
python main.py --mode background
# Let it run for 30 minutes, observe cycles
```

### Query Test (On-demand)
```bash
python main.py --mode query --region "Middle East" --hours 12
```

---

## ⚠️ Production Considerations

### Deployment
- Run as **systemd service** or **Docker container**
- Set up **health checks** (ping every 5 minutes)
- Configure **restart policy** (auto-restart on failure)
- Use **PM2** or **supervisord** for process management

### Monitoring
- Log to file for debugging
- Track cycle duration (should be <60s)
- Alert if cycles start failing
- Monitor MongoDB storage size

### Rate Limiting
- Tavily API limits: ~100 requests/day on free tier
- Adjust `POLL_INTERVAL_MINUTES` based on plan
- Cache results to reduce API calls

### Scalability
- Current design: Single instance sufficient for most use cases
- For high-volume: Use message queue (Redis/RabbitMQ)
- Multiple workers for different regions

---

## ✅ Definition of Done

- [ ] Polls Tavily API continuously (background mode)
- [ ] Extracts structured events from news
- [ ] Scores events by significance
- [ ] Stores events in MongoDB
- [ ] Detects trending topics
- [ ] Generates alerts for high-priority events
- [ ] Can run standalone (no master agent)
- [ ] On-demand query mode works
- [ ] Event deduplication working
- [ ] Tests passing (single cycle test)
- [ ] Can run for 24+ hours without issues

**Effort:** 5-6 days (2 developers)  
**Impact:** ⭐⭐⭐⭐⭐ **FOUNDATIONAL** - Powers SitRep & Policy Brief agents  
**Priority:** 🔴 **CRITICAL** - Must be built first before SitRep/Policy Brief

