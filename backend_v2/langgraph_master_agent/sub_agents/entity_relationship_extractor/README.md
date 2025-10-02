# Entity & Relationship Extractor Agent

## 🎯 Purpose
Extract political entities (people, organizations, countries) and map their relationships through interactive network graphs.

---

## 📦 Input/Output

**Input:** Political topic or region  
**Output:** Interactive network graph + relationship mappings

**Example Query:**
```
"Map relationships between NATO member states"
"Show connections between US political donors and candidates"
"Analyze Middle East political alliances"
```

**Artifacts:**
- Interactive network graph (HTML with physics simulation)
- Influence flow Sankey diagram
- Entity timeline (who-did-what-when)
- Geopolitical alliance map (world map with arcs)

---

## 🏗️ Architecture

```
START → Search & Extract → Entity Recognition → Relationship Classification → 
Graph Construction → Centrality Analysis → Visualizer → END
```

### Technology Stack
- **NetworkX:** Graph algorithms (centrality, clustering)
- **PyVis:** Interactive HTML network visualization
- **Plotly Sankey:** Influence/money flow diagrams
- **Plotly Geo:** Arc maps between countries

---

## 📋 Files to Create

1. **`main.py`** - ⭐ Standalone runner
2. **`state.py`** - State schema
3. **`config.py`** - Config (relationship types, node colors)
4. **`graph.py`** - LangGraph workflow
5. **`nodes/searcher.py`** - Tavily search for entity mentions
6. **`nodes/entity_extractor.py`** - LLM extraction of entities
7. **`nodes/relationship_classifier.py`** - Classify relationships
8. **`nodes/graph_builder.py`** - Build NetworkX graph
9. **`nodes/analyzer.py`** - Graph metrics (centrality, clusters)
10. **`nodes/visualizer.py`** - Generate 4 artifact types
11. **`tools/network_tools.py`** - NetworkX utilities
12. **`tests/test_agent.py`**

---

## 🔑 Key Implementation: Relationship Classification

```python
# nodes/relationship_classifier.py

from openai import AsyncOpenAI

RELATIONSHIP_TYPES = [
    "allies",           # Political/military alliance
    "opponents",        # Adversarial relationship
    "trade_partners",   # Economic ties
    "military_support", # Defense cooperation
    "diplomatic_ties",  # Embassy/diplomatic relations
    "funding",          # Financial support
    "member_of",        # Organizational membership
    "influences",       # Power/influence relationship
]

async def classify_relationships(entities: list, context: str) -> list:
    """
    Classify relationships between entities using LLM
    
    Returns: [
        {"source": "US", "target": "NATO", "type": "member_of", "strength": 1.0},
        {"source": "US", "target": "Russia", "type": "opponents", "strength": 0.7},
    ]
    """
    
    client = AsyncOpenAI()
    
    prompt = f"""Identify relationships between these entities in the context of {context}:

Entities: {', '.join(entities)}

For each relationship, provide:
- source: entity name
- target: entity name  
- type: one of {RELATIONSHIP_TYPES}
- strength: 0.0 to 1.0 (how strong is the relationship)
- evidence: brief description

Return as JSON array."""
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)["relationships"]
```

---

## 🎨 Key Artifacts

### 1. Interactive Network Graph (PyVis)

```python
from pyvis.network import Network
import networkx as nx

def create_interactive_network(G: nx.Graph, output_path: str):
    """
    Create interactive network with physics simulation
    """
    
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#1c1e20",
        font_color="#d9f378",
        notebook=False
    )
    
    # Node colors by type
    node_colors = {
        "country": "#5d535c",
        "organization": "#d9f378",
        "person": "#333333"
    }
    
    # Add nodes
    for node, data in G.nodes(data=True):
        net.add_node(
            node,
            label=node,
            color=node_colors.get(data.get("type"), "#5d535c"),
            size=data.get("centrality", 0.5) * 50,  # Size by importance
            title=f"{node}\n{data.get('type', 'unknown')}"
        )
    
    # Add edges
    for source, target, data in G.edges(data=True):
        net.add_edge(
            source,
            target,
            title=data.get("type", "related"),
            value=data.get("strength", 0.5),
            color={"color": "#d9f378", "opacity": data.get("strength", 0.5)}
        )
    
    # Physics settings for better layout
    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 200,
          "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {"iterations": 150}
      }
    }
    """)
    
    net.save_graph(output_path)
    return output_path
```

### 2. Influence Flow Sankey Diagram

```python
import plotly.graph_objects as go

def create_influence_flow(relationships: list):
    """
    Show influence/power flow between entities
    """
    
    # Filter for influence/funding relationships
    flow_relationships = [
        r for r in relationships 
        if r["type"] in ["influences", "funding", "supports"]
    ]
    
    # Create Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            label=[entity for entity in unique_entities],
            color="#d9f378"
        ),
        link=dict(
            source=[source_indices],
            target=[target_indices],
            value=[r["strength"] for r in flow_relationships],
            color="rgba(217, 243, 120, 0.4)"
        )
    )])
    
    fig.update_layout(
        title="Political Influence Flow",
        font=dict(size=12, color="#333333")
    )
    
    return fig
```

### 3. Geopolitical Alliance Map

```python
import plotly.graph_objects as go

def create_alliance_map(relationships: list, entity_coords: dict):
    """
    World map with arcs showing alliances between countries
    """
    
    fig = go.Figure()
    
    # Add country arcs
    for rel in relationships:
        if rel["type"] == "allies":
            source = entity_coords[rel["source"]]
            target = entity_coords[rel["target"]]
            
            fig.add_trace(go.Scattergeo(
                lon=[source["lon"], target["lon"]],
                lat=[source["lat"], target["lat"]],
                mode="lines",
                line=dict(width=2, color="#d9f378"),
                opacity=rel["strength"],
                name=f"{rel['source']} - {rel['target']}"
            ))
    
    fig.update_layout(
        geo=dict(
            projection_type="natural earth",
            bgcolor="#1c1e20",
            showland=True,
            landcolor="#333333"
        )
    )
    
    return fig
```

---

## 📊 Graph Metrics to Calculate

```python
import networkx as nx

def analyze_network(G: nx.Graph) -> dict:
    """Calculate important graph metrics"""
    
    return {
        "node_count": G.number_of_nodes(),
        "edge_count": G.number_of_edges(),
        "density": nx.density(G),
        "avg_clustering": nx.average_clustering(G),
        
        # Centrality (importance)
        "betweenness_centrality": nx.betweenness_centrality(G),
        "degree_centrality": nx.degree_centrality(G),
        "eigenvector_centrality": nx.eigenvector_centrality(G),
        
        # Communities/clusters
        "communities": list(nx.community.greedy_modularity_communities(G)),
        
        # Most connected nodes
        "hub_nodes": sorted(
            [(node, degree) for node, degree in G.degree()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
    }
```

---

## 🧪 Standalone Testing

```bash
cd backend_v2/langgraph_master_agent/sub_agents/entity_relationship_extractor
python main.py
```

**Test Queries:**
- "Map NATO member relationships"
- "Show Middle East political alliances"
- "Analyze G7 country connections"

---

## 📦 Required Packages

```bash
uv pip install networkx
uv pip install pyvis
# plotly already installed
```

---

## ✅ Definition of Done

- [ ] Extracts 10+ entities per query
- [ ] Identifies 15+ relationships
- [ ] Generates interactive HTML network
- [ ] Calculates centrality metrics
- [ ] Works standalone
- [ ] Response time <8s
- [ ] Tests passing (including mock entity extraction)

**Effort:** 4-5 days (2 developers)  
**Impact:** ⭐⭐⭐⭐⭐ Very High - **Most visually impressive** artifact

