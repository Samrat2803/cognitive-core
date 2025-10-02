# Crisis Event Tracker Agent

## 🎯 Purpose
Track real-time political crises, map their geographic spread, analyze severity, and show cascading impacts.

---

## 📦 Input/Output

**Input:** Region, crisis type, or timeframe  
**Output:** Real-time crisis map + impact analysis

**Example Query:**
```
"Track current political crises in Middle East"
"Show recent protests in Latin America"
"Map conflict zones in Ukraine region"
```

**Artifacts:**
- Interactive crisis map with markers (Folium)
- Event timeline with severity indicators
- Impact ripple diagram (cascading effects)
- Multi-country response comparison

---

## 🏗️ Architecture

```
START → Real-time Search → Event Extractor → Geographic Mapper → 
Severity Classifier → Impact Analyzer → Timeline Builder → 
Visualizer → END
```

### Key Features
- **Real-time:** Uses Tavily with recency filter (last 24-48 hours)
- **Geographic:** Maps events to coordinates
- **Severity:** Classifies crisis level (1-5 scale)
- **Impact:** Identifies affected sectors (economic, humanitarian, security)

---

## 📋 Files to Create

1. **`main.py`** - ⭐ Standalone runner
2. **`state.py`** - State schema
3. **`config.py`** - Severity scales, crisis types, map settings
4. **`graph.py`** - LangGraph workflow
5. **`nodes/searcher.py`** - Real-time Tavily search
6. **`nodes/event_extractor.py`** - Extract crisis events
7. **`nodes/geo_mapper.py`** - Convert locations to coordinates
8. **`nodes/severity_classifier.py`** - Classify crisis severity
9. **`nodes/impact_analyzer.py`** - Analyze cascading impacts
10. **`nodes/visualizer.py`** - Generate maps and timelines
11. **`tools/geocoding.py`** - Location → coordinates
12. **`tests/test_agent.py`**

---

## 🔑 Key Configuration (`config.py`)

```python
# Crisis Types
CRISIS_TYPES = {
    "political_unrest": {
        "keywords": ["protest", "uprising", "coup", "demonstration"],
        "color": "#E74C3C",  # Red
        "icon": "exclamation-circle"
    },
    "armed_conflict": {
        "keywords": ["war", "military", "combat", "armed conflict"],
        "color": "#8B0000",  # Dark red
        "icon": "bomb"
    },
    "humanitarian": {
        "keywords": ["refugee", "famine", "disaster", "crisis"],
        "color": "#F39C12",  # Orange
        "icon": "users"
    },
    "election_dispute": {
        "keywords": ["election fraud", "contested election", "vote"],
        "color": "#9B59B6",  # Purple
        "icon": "vote-yea"
    },
    "diplomatic_crisis": {
        "keywords": ["sanctions", "embassy", "diplomatic", "relations"],
        "color": "#3498DB",  # Blue
        "icon": "handshake"
    }
}

# Severity Scale (1-5)
SEVERITY_SCALE = {
    1: {"label": "Low", "color": "#2ECC71", "description": "Limited local impact"},
    2: {"label": "Moderate", "color": "#F39C12", "description": "Regional concern"},
    3: {"label": "Serious", "color": "#E67E22", "description": "National significance"},
    4: {"label": "Severe", "color": "#E74C3C", "description": "Regional destabilization"},
    5: {"label": "Critical", "color": "#8B0000", "description": "International crisis"}
}

# Search Configuration
TIME_RANGE_HOURS = 48  # Last 48 hours for "real-time"
MAX_EVENTS = 20
SEARCH_DEPTH = "advanced"
```

---

## 🗺️ Key Artifact: Interactive Crisis Map (Folium)

```python
import folium
from folium.plugins import MarkerCluster, HeatMap

def create_crisis_map(events: list, output_path: str):
    """
    Create interactive Folium map with crisis markers
    """
    
    # Center map on region with most events
    center_lat = sum(e["coordinates"]["lat"] for e in events) / len(events)
    center_lon = sum(e["coordinates"]["lon"] for e in events) / len(events)
    
    # Create base map (dark theme)
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=5,
        tiles="CartoDB dark_matter"
    )
    
    # Add marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add events as markers
    for event in events:
        coords = event["coordinates"]
        severity = event["severity"]
        crisis_type = event["type"]
        
        # Marker color and size based on severity
        color = SEVERITY_SCALE[severity]["color"]
        radius = 10 + (severity * 5)
        
        # Popup with event details
        popup_html = f"""
        <div style="width: 250px; font-family: Arial;">
            <h4 style="color: {color}; margin: 0;">
                {event['title']}
            </h4>
            <p><strong>Type:</strong> {crisis_type}</p>
            <p><strong>Severity:</strong> {SEVERITY_SCALE[severity]['label']} ({severity}/5)</p>
            <p><strong>Date:</strong> {event['date']}</p>
            <p><strong>Location:</strong> {event['location']}</p>
            <hr>
            <p>{event['description'][:200]}...</p>
            <p><a href="{event['source_url']}" target="_blank">Read more</a></p>
        </div>
        """
        
        # Add circle marker
        folium.CircleMarker(
            location=[coords["lat"], coords["lon"]],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(marker_cluster)
        
        # Add icon marker for high severity
        if severity >= 4:
            folium.Marker(
                location=[coords["lat"], coords["lon"]],
                icon=folium.Icon(
                    color="red",
                    icon="exclamation-triangle",
                    prefix="fa"
                ),
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)
    
    # Add heatmap layer (optional, toggle)
    heat_data = [[e["coordinates"]["lat"], e["coordinates"]["lon"], e["severity"]] for e in events]
    HeatMap(heat_data, name="Severity Heatmap").add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save
    m.save(output_path)
    return output_path
```

---

## 📅 Key Artifact: Event Timeline

```python
import plotly.graph_objects as go
from datetime import datetime

def create_event_timeline(events: list):
    """
    Timeline with events sized/colored by severity
    """
    
    # Sort by date
    events = sorted(events, key=lambda e: e["date"])
    
    fig = go.Figure()
    
    for event in events:
        severity = event["severity"]
        color = SEVERITY_SCALE[severity]["color"]
        
        fig.add_trace(go.Scatter(
            x=[event["date"]],
            y=[event["location"]],
            mode="markers+text",
            marker=dict(
                size=15 + severity * 5,
                color=color,
                line=dict(width=2, color="#333333")
            ),
            text=event["title"],
            textposition="top center",
            name=event["title"],
            hovertemplate=(
                f"<b>{event['title']}</b><br>"
                f"Location: {event['location']}<br>"
                f"Severity: {SEVERITY_SCALE[severity]['label']}<br>"
                f"Date: {event['date']}<br>"
                "<extra></extra>"
            )
        ))
    
    fig.update_layout(
        title="Crisis Event Timeline",
        xaxis_title="Date",
        yaxis_title="Location",
        showlegend=False,
        height=600,
        hovermode="closest"
    )
    
    return fig
```

---

## 🌊 Key Artifact: Impact Ripple Diagram

```python
import plotly.graph_objects as go

def create_impact_ripple(event: dict, impacts: dict):
    """
    Sunburst chart showing cascading impacts
    
    impacts = {
        "economic": ["trade disruption", "market volatility"],
        "humanitarian": ["refugee crisis", "food shortage"],
        "security": ["military mobilization", "border closure"],
        "diplomatic": ["sanctions", "embassy closures"]
    }
    """
    
    labels = [event["title"]]  # Root
    parents = [""]
    values = [10]
    
    for sector, sector_impacts in impacts.items():
        # Add sector
        labels.append(sector.title())
        parents.append(event["title"])
        values.append(len(sector_impacts))
        
        # Add specific impacts
        for impact in sector_impacts:
            labels.append(impact)
            parents.append(sector.title())
            values.append(1)
    
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(
            colorscale="Reds",
            line=dict(width=2)
        )
    ))
    
    fig.update_layout(
        title="Crisis Impact Analysis",
        height=600
    )
    
    return fig
```

---

## 📍 Geocoding Tool (`tools/geocoding.py`)

```python
from typing import Dict, Optional
import re

# Hardcoded major cities/regions (fallback)
LOCATION_COORDS = {
    "ukraine": {"lat": 48.3794, "lon": 31.1656},
    "kyiv": {"lat": 50.4501, "lon": 30.5234},
    "middle east": {"lat": 29.2985, "lon": 47.4979},
    "gaza": {"lat": 31.3547, "lon": 34.3088},
    # ... add more as needed
}

async def geocode_location(location: str) -> Optional[Dict[str, float]]:
    """
    Convert location name to coordinates
    
    Options:
    1. Hardcoded lookup (fast, limited)
    2. Use OpenStreetMap Nominatim API (free, rate-limited)
    3. Use Google Maps API (paid, accurate)
    """
    
    location_lower = location.lower().strip()
    
    # Try hardcoded first
    if location_lower in LOCATION_COORDS:
        return LOCATION_COORDS[location_lower]
    
    # Try fuzzy match
    for key, coords in LOCATION_COORDS.items():
        if key in location_lower or location_lower in key:
            return coords
    
    # Fallback: Use Nominatim (free geocoding)
    try:
        import requests
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": location, "format": "json"},
            headers={"User-Agent": "PoliticalAnalystApp/1.0"}
        )
        if response.json():
            result = response.json()[0]
            return {"lat": float(result["lat"]), "lon": float(result["lon"])}
    except:
        pass
    
    return None  # Could not geocode
```

---

## 🧪 Standalone Testing

```bash
cd backend_v2/langgraph_master_agent/sub_agents/crisis_event_tracker
python main.py
```

**Test Queries:**
- "Track crises in Middle East"
- "Show recent protests globally"
- "Map conflict zones in Eastern Europe"

---

## ⚠️ Important Considerations

### Real-time Challenges
- News lag (events take time to be reported)
- False reports (verify with multiple sources)
- Rapidly evolving situations (data may be outdated)

### Severity Classification
```python
# Factors for severity scoring
- Casualties (deaths/injuries)
- Geographic scope (local/regional/international)
- Duration (hours/days/weeks)
- International response (diplomatic actions)
- Economic impact
```

### Ethical Considerations
- Sensitive content (violence, casualties)
- Avoid sensationalism
- Cite credible sources
- Include disclaimers on real-time data

---

## ✅ Definition of Done

- [ ] Searches real-time data (last 24-48 hours)
- [ ] Maps events geographically (coordinates)
- [ ] Classifies severity (1-5 scale)
- [ ] Generates interactive Folium map
- [ ] Creates event timeline
- [ ] Shows impact analysis
- [ ] Works standalone
- [ ] Response time <6s (for 10-20 events)
- [ ] Handles missing coordinates gracefully
- [ ] Tests passing

**Effort:** 3-4 days (1-2 developers)  
**Impact:** ⭐⭐⭐⭐ High - **Time-sensitive value** for breaking news

