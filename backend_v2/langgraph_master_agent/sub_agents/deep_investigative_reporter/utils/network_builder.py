"""
Network and causal diagram builders.

Generate visual artifacts:
1. Spider Web Network (entity connections)
2. Causal Diagram (cause → effect chains)
"""

from typing import Dict, List, Any
import json


def build_network_graph(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build spider web network graph showing entity connections.
    
    Returns JSON graph structure for visualization:
    - nodes: entities (people, orgs, events)
    - edges: relationships between entities
    """
    nodes = []
    edges = []
    
    entities = state.get("entities", {})
    funding_network = state.get("funding_network", {})
    relationships = state.get("relationships", {})
    
    # Build nodes
    for name, entity in entities.items():
        node = {
            "id": name,
            "label": name,
            "type": entity.get("type", "unknown"),
            "importance": entity.get("confidence", 0.5),
            "size": int(entity.get("confidence", 0.5) * 50) + 10,  # Visual size
            "color": get_node_color(entity),
            "metadata": {
                "facts_count": len(entity.get("facts", [])),
                "connections_count": len(entity.get("connections", [])),
                "corruption_charges": entity.get("corruption_charges", False),
                "arms_dealer": entity.get("arms_dealer", False)
            }
        }
        nodes.append(node)
    
    # Build edges from connections
    for name, entity in entities.items():
        connections = entity.get("connections", [])
        for connected_name in connections:
            if connected_name in entities:
                edges.append({
                    "source": name,
                    "target": connected_name,
                    "type": "connection",
                    "weight": 1,
                    "color": "#999999"
                })
    
    # Build edges from funding network
    for org_name, funders in funding_network.items():
        for funder in funders:
            if funder in entities or org_name in entities:
                edges.append({
                    "source": funder,
                    "target": org_name,
                    "type": "funding",
                    "weight": 2,  # Stronger edge
                    "color": "#ff6b6b",  # Red for funding
                    "label": "funds"
                })
    
    # Remove duplicate edges
    unique_edges = []
    seen_edges = set()
    for edge in edges:
        edge_key = (edge["source"], edge["target"], edge["type"])
        if edge_key not in seen_edges:
            seen_edges.add(edge_key)
            unique_edges.append(edge)
    
    graph = {
        "nodes": nodes,
        "edges": unique_edges,
        "metadata": {
            "total_entities": len(nodes),
            "total_connections": len(unique_edges),
            "investigation_depth": state.get("investigation_depth", 0),
            "overall_confidence": state.get("overall_confidence", 0.0)
        }
    }
    
    return graph


def get_node_color(entity: Dict[str, Any]) -> str:
    """Get color for node based on entity type and attributes"""
    entity_type = entity.get("type", "unknown")
    
    # Red for suspicious entities
    if entity.get("corruption_charges") or entity.get("arms_dealer"):
        return "#e74c3c"
    
    # Type-based colors
    color_map = {
        "person": "#3498db",  # Blue
        "organization": "#2ecc71",  # Green
        "funder": "#f39c12",  # Orange
        "event": "#9b59b6",  # Purple
        "claim": "#95a5a6"  # Gray
    }
    
    return color_map.get(entity_type, "#95a5a6")


def build_causal_diagram(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build causal diagram showing cause → effect chains.
    
    Returns structure for Mermaid flowchart or similar visualization.
    """
    causal_chains = state.get("causal_chains", [])
    timeline = state.get("timeline", [])
    
    # Build nodes (unique causes and effects)
    nodes = {}
    node_id = 0
    
    def get_or_create_node(text: str) -> str:
        """Get existing node ID or create new one"""
        nonlocal node_id
        
        # Check if node exists
        for nid, node in nodes.items():
            if node["text"].lower() == text.lower():
                return nid
        
        # Create new node
        nid = f"node_{node_id}"
        node_id += 1
        nodes[nid] = {
            "id": nid,
            "text": text,
            "type": "cause" if "underlying" in text.lower() or "root" in text.lower() else "effect"
        }
        return nid
    
    # Build edges from causal chains
    edges = []
    for chain in causal_chains:
        cause = chain.get("cause", "")
        effect = chain.get("effect", "")
        confidence = chain.get("confidence", 0.5)
        evidence = chain.get("evidence", [])
        
        if cause and effect:
            cause_id = get_or_create_node(cause)
            effect_id = get_or_create_node(effect)
            
            edges.append({
                "from": cause_id,
                "to": effect_id,
                "confidence": confidence,
                "evidence_count": len(evidence),
                "label": f"{int(confidence * 100)}%"
            })
    
    # Organize into layers (root → intermediate → trigger → event)
    layers = organize_into_layers(nodes, edges)
    
    # Generate Mermaid syntax
    mermaid_code = generate_mermaid_flowchart(nodes, edges, layers)
    
    diagram = {
        "nodes": list(nodes.values()),
        "edges": edges,
        "layers": layers,
        "mermaid_code": mermaid_code,
        "metadata": {
            "total_causes": len([n for n in nodes.values() if n["type"] == "cause"]),
            "total_effects": len([n for n in nodes.values() if n["type"] == "effect"]),
            "causal_links": len(edges)
        }
    }
    
    return diagram


def organize_into_layers(nodes: Dict[str, Dict], edges: List[Dict]) -> Dict[str, List[str]]:
    """
    Organize nodes into layers: root causes → intermediate → triggers → events
    """
    # Find root nodes (no incoming edges)
    incoming = {nid: 0 for nid in nodes.keys()}
    for edge in edges:
        incoming[edge["to"]] += 1
    
    root_nodes = [nid for nid, count in incoming.items() if count == 0]
    
    # Find leaf nodes (no outgoing edges)
    outgoing = {nid: 0 for nid in nodes.keys()}
    for edge in edges:
        outgoing[edge["from"]] += 1
    
    leaf_nodes = [nid for nid, count in outgoing.items() if count == 0]
    
    # Intermediate nodes
    intermediate_nodes = [nid for nid in nodes.keys() 
                         if nid not in root_nodes and nid not in leaf_nodes]
    
    return {
        "root_causes": root_nodes,
        "intermediate_causes": intermediate_nodes,
        "final_events": leaf_nodes
    }


def generate_mermaid_flowchart(nodes: Dict[str, Dict], edges: List[Dict], 
                               layers: Dict[str, List[str]]) -> str:
    """
    Generate Mermaid flowchart syntax for causal diagram.
    """
    lines = ["graph TD"]  # Top-Down flowchart
    
    # Add node definitions with styling
    for nid, node in nodes.items():
        text = node["text"][:50]  # Truncate long text
        
        # Style based on type
        if nid in layers["root_causes"]:
            lines.append(f'    {nid}["{text}"]:::rootCause')
        elif nid in layers["final_events"]:
            lines.append(f'    {nid}["{text}"]:::finalEvent')
        else:
            lines.append(f'    {nid}["{text}"]:::intermediate')
    
    # Add edges
    for edge in edges:
        from_id = edge["from"]
        to_id = edge["to"]
        label = edge.get("label", "")
        lines.append(f'    {from_id} -->|{label}| {to_id}')
    
    # Add styling
    lines.append("")
    lines.append("    classDef rootCause fill:#e74c3c,stroke:#c0392b,color:#fff")
    lines.append("    classDef intermediate fill:#f39c12,stroke:#e67e22,color:#fff")
    lines.append("    classDef finalEvent fill:#2ecc71,stroke:#27ae60,color:#fff")
    
    return "\n".join(lines)


def generate_html_visualization(network_graph: Dict, causal_diagram: Dict) -> str:
    """
    Generate standalone HTML file with both visualizations.
    
    Uses D3.js for network graph and Mermaid for causal diagram.
    """
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Deep Investigative Report</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1c1e20;
            color: #d9f378;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            color: #d9f378;
            text-align: center;
        }}
        .visualization {{
            background: #333333;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        #network {{
            width: 100%;
            height: 600px;
        }}
        .mermaid {{
            background: white;
            padding: 20px;
            border-radius: 8px;
        }}
        .metadata {{
            color: #5d535c;
            font-size: 14px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🕵️ Deep Investigative Report</h1>
        
        <div class="visualization">
            <h2>🕸️ Entity Network (Spider Web)</h2>
            <div id="network"></div>
            <div class="metadata">
                Total Entities: {network_graph['metadata']['total_entities']} | 
                Connections: {network_graph['metadata']['total_connections']} |
                Investigation Depth: {network_graph['metadata']['investigation_depth']}
            </div>
        </div>
        
        <div class="visualization">
            <h2>🔗 Causal Chain Diagram</h2>
            <div class="mermaid">
                {causal_diagram['mermaid_code']}
            </div>
            <div class="metadata">
                Root Causes: {causal_diagram['metadata']['total_causes']} |
                Final Events: {causal_diagram['metadata']['total_effects']} |
                Causal Links: {causal_diagram['metadata']['causal_links']}
            </div>
        </div>
    </div>
    
    <script>
        // Network graph data
        const graphData = {json.dumps(network_graph)};
        
        // Initialize Mermaid
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        
        // D3.js force-directed graph
        const width = document.getElementById('network').clientWidth;
        const height = 600;
        
        const svg = d3.select('#network')
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        const simulation = d3.forceSimulation(graphData.nodes)
            .force('link', d3.forceLink(graphData.edges).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2));
        
        // Draw edges
        const link = svg.append('g')
            .selectAll('line')
            .data(graphData.edges)
            .enter().append('line')
            .attr('stroke', d => d.color)
            .attr('stroke-width', d => d.weight)
            .attr('stroke-opacity', 0.6);
        
        // Draw nodes
        const node = svg.append('g')
            .selectAll('circle')
            .data(graphData.nodes)
            .enter().append('circle')
            .attr('r', d => d.size)
            .attr('fill', d => d.color)
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        // Node labels
        const label = svg.append('g')
            .selectAll('text')
            .data(graphData.nodes)
            .enter().append('text')
            .text(d => d.label)
            .attr('font-size', 12)
            .attr('fill', '#d9f378')
            .attr('dx', 15)
            .attr('dy', 4);
        
        // Update positions on simulation tick
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
            
            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>
"""
    return html_template


