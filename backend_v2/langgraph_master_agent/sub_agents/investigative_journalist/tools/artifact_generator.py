"""
Artifact Generator for Investigative Journalist
Generates visualizations: Entity Network, Timeline, Evidence Chain
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Visualization libraries
from pyvis.network import Network
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def log(message: str):
    """Print with flush for real-time logging"""
    print(message)
    sys.stdout.flush()


def generate_entity_network_graph(
    entities: Dict[str, Any],
    connections: List[Dict[str, Any]],
    output_path: str = "entity_network.html"
) -> str:
    """
    Generate interactive entity network graph using pyvis
    
    Args:
        entities: Dict of {name: {type, role, importance, investigated}}
        connections: List of {from, to, type}
        output_path: Where to save the HTML file
        
    Returns:
        Path to generated HTML file
    """
    log(f"   📊 Generating entity network graph...")
    
    # Initialize network with dark theme
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#1a1a1a",
        font_color="white",
        select_menu=True,
        filter_menu=True
    )
    
    # Configure physics for better layout
    net.set_options("""
    {
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 100,
                "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {"iterations": 150}
        },
        "nodes": {
            "font": {"size": 14}
        }
    }
    """)
    
    # Entity type colors (matching Aistra palette)
    type_colors = {
        "person": "#d9f378",      # Bright green for people
        "organization": "#5d535c", # Gray for organizations
        "location": "#333333",     # Dark gray for locations
        "substance": "#FF6B6B",    # Red for substances
        "event": "#4ECDC4",        # Teal for events
        "unknown": "#95a5a6"       # Default gray
    }
    
    # Add nodes (entities)
    for name, entity in entities.items():
        entity_type = entity.get("type", "unknown")
        importance = entity.get("importance", 0.5)
        role = entity.get("role", "No description")
        investigated = entity.get("investigated", False)
        
        # Size based on importance (10-50 range)
        node_size = 10 + (importance * 40)
        
        # Color based on type
        color = type_colors.get(entity_type, type_colors["unknown"])
        
        # Title shows on hover
        hover_text = f"<b>{name}</b><br>Type: {entity_type}<br>Role: {role}<br>Importance: {importance:.2f}<br>Investigated: {investigated}"
        
        net.add_node(
            name,
            label=name,
            title=hover_text,
            size=node_size,
            color=color,
            borderWidth=3 if investigated else 1,
            borderWidthSelected=5
        )
    
    log(f"      ✅ Added {len(entities)} entity nodes")
    
    # Add edges (connections)
    for conn in connections:
        source = conn.get("from") or conn.get("entity1")
        target = conn.get("to") or conn.get("entity2")
        rel_type = conn.get("type") or conn.get("relationship", "related to")
        
        if source and target and source in entities and target in entities:
            net.add_edge(
                source,
                target,
                title=rel_type,
                color="#666666",
                width=2
            )
    
    log(f"      ✅ Added {len(connections)} connections")
    
    # Save to file
    net.save_graph(output_path)
    log(f"      ✅ Network graph saved to {output_path}")
    
    return output_path


def generate_timeline_visualization(
    facts: List[str],
    iteration_count: int,
    output_path: str = "timeline.html"
) -> str:
    """
    Generate timeline visualization using iteration numbers as X-axis
    
    Args:
        facts: List of fact strings
        iteration_count: Total iterations run
        output_path: Where to save the HTML file
        
    Returns:
        Path to generated HTML file
    """
    log(f"   📊 Generating timeline visualization...")
    
    # Convert facts to timeline events (use iteration number as proxy for time)
    # Distribute facts evenly across iterations
    timeline_data = []
    
    if not facts:
        log(f"      ⚠️  No facts to visualize")
        # Create empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No facts discovered yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        fig.update_layout(
            title="Investigation Timeline",
            paper_bgcolor="#1a1a1a",
            plot_bgcolor="#1a1a1a",
            font=dict(color="white")
        )
        fig.write_html(output_path)
        return output_path
    
    facts_per_iteration = max(len(facts) // max(iteration_count, 1), 1)
    
    for idx, fact in enumerate(facts):
        # Estimate which iteration this fact was discovered
        estimated_iteration = min((idx // facts_per_iteration) + 1, iteration_count)
        
        # Truncate long facts for display
        fact_short = fact[:80] + "..." if len(fact) > 80 else fact
        
        timeline_data.append({
            "Fact": fact_short,
            "Full_Fact": fact,
            "Iteration": estimated_iteration,
            "Category": "Discovery"
        })
    
    df = pd.DataFrame(timeline_data)
    
    # Create scatter plot (since we don't have start/end times)
    fig = px.scatter(
        df,
        x="Iteration",
        y="Fact",
        hover_data=["Full_Fact"],
        title=f"Investigation Timeline ({len(facts)} facts discovered)",
        color="Category",
        color_discrete_map={"Discovery": "#d9f378"}
    )
    
    # Update layout for dark theme
    fig.update_layout(
        paper_bgcolor="#1a1a1a",
        plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        xaxis=dict(
            gridcolor="#333333",
            title="Iteration Number"
        ),
        yaxis=dict(
            gridcolor="#333333",
            title="Discovered Facts",
            autorange="reversed"  # Top to bottom
        ),
        hovermode="closest"
    )
    
    # Update markers
    fig.update_traces(
        marker=dict(size=12, line=dict(width=2, color="white"))
    )
    
    fig.write_html(output_path)
    log(f"      ✅ Timeline saved to {output_path} ({len(facts)} facts)")
    
    return output_path


def generate_evidence_chain_sankey(
    hypotheses: List[Dict[str, Any]],
    facts: List[str],
    output_path: str = "evidence_chain.html"
) -> str:
    """
    Generate Sankey diagram showing evidence flow to hypotheses
    
    Args:
        hypotheses: List of hypothesis dicts with {id, statement, status, questions, evidence}
        facts: List of fact strings
        output_path: Where to save the HTML file
        
    Returns:
        Path to generated HTML file
    """
    log(f"   📊 Generating evidence chain Sankey diagram...")
    
    if not hypotheses:
        log(f"      ⚠️  No hypotheses to visualize")
        # Create empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No hypotheses formed yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        fig.update_layout(
            title="Evidence Flow",
            paper_bgcolor="#1a1a1a",
            plot_bgcolor="#1a1a1a",
            font=dict(color="white")
        )
        fig.write_html(output_path)
        return output_path
    
    # Build Sankey diagram structure with better labels
    # Layers: Investigation → Hypotheses → Status
    
    labels = []
    sources = []
    targets = []
    values = []
    colors = []
    
    # Node indices
    node_idx = {}
    current_idx = 0
    
    # Layer 1: Investigation source
    labels.append("🔬 Investigation<br>Evidence Gathered")
    node_idx["Investigation"] = current_idx
    current_idx += 1
    
    # Layer 2: Hypotheses (middle layer) with truncated statements
    for hyp in hypotheses:
        hyp_id = hyp.get("id", "unknown")
        statement = hyp.get("statement", "")
        
        # Truncate statement to fit better
        truncated = statement[:60] + "..." if len(statement) > 60 else statement
        
        # Add status icon
        status = hyp.get("status", "exploring")
        if status in ["proven", "confirmed"]:
            icon = "✅"
        elif status in ["disproven", "refuted"]:
            icon = "❌"
        else:
            icon = "🔄"
        
        hyp_label = f"{icon} {hyp_id}<br>{truncated}"
        labels.append(hyp_label)
        node_idx[hyp_id] = current_idx
        current_idx += 1
    
    # Layer 3: Status nodes (proven, exploring, disproven)
    labels.append("✅ Proven<br>Confirmed")
    node_idx["Proven"] = current_idx
    current_idx += 1
    
    labels.append("🔄 Exploring<br>Being Investigated")
    node_idx["Exploring"] = current_idx
    current_idx += 1
    
    labels.append("❌ Disproven<br>Refuted")
    node_idx["Disproven"] = current_idx
    current_idx += 1
    
    # Build connections
    # Investigation → Hypotheses (based on questions count)
    for hyp in hypotheses:
        hyp_id = hyp.get("id")
        questions = hyp.get("questions", [])
        evidence_count = len(questions)  # Use questions as proxy for evidence
        
        if evidence_count > 0:
            sources.append(node_idx["Investigation"])
            targets.append(node_idx[hyp_id])
            values.append(evidence_count)
            colors.append("rgba(217, 243, 120, 0.4)")  # Yellow-green flow
    
    # Hypotheses → Status (based on status)
    for hyp in hypotheses:
        hyp_id = hyp.get("id")
        status = hyp.get("status", "exploring")
        questions = hyp.get("questions", [])
        evidence_count = len(questions) or 1
        
        # Map status to status node
        if status in ["proven", "confirmed"]:
            target_status = "Proven"
            color = "rgba(76, 175, 80, 0.6)"  # Green
        elif status in ["disproven", "refuted"]:
            target_status = "Disproven"
            color = "rgba(244, 67, 54, 0.6)"  # Red
        else:
            target_status = "Exploring"
            color = "rgba(255, 193, 7, 0.6)"  # Yellow
        
        sources.append(node_idx[hyp_id])
        targets.append(node_idx[target_status])
        values.append(evidence_count)
        colors.append(color)
    
    # Create Sankey diagram with better styling
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="white", width=2),
            label=labels,
            color="#5d535c",  # Aistra gray for nodes
            customdata=[f"Node {i}" for i in range(len(labels))],
            hovertemplate='%{label}<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors,
            hovertemplate='%{value} pieces of evidence<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title={
            'text': f"Evidence Flow ({len(hypotheses)} hypotheses, {len(facts)} facts)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': 'white'}
        },
        font=dict(size=12, color="white"),
        paper_bgcolor="#1a1a1a",
        plot_bgcolor="#1a1a1a",
        height=700,  # Taller for better visibility
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    fig.write_html(output_path)
    log(f"      ✅ Evidence chain saved to {output_path}")
    
    return output_path


async def generate_all_artifacts(
    state: Dict[str, Any],
    output_dir: str = "artifacts"
) -> List[Dict[str, str]]:
    """
    Generate all 3 artifacts and return their paths
    
    Args:
        state: Investigation state with entities, facts, hypotheses, connections
        output_dir: Directory to save artifacts
        
    Returns:
        List of artifact dicts with {type, name, path}
    """
    log(f"\n📦 Generating investigation artifacts...")
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Generate unique filenames with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    investigation_id = state.get("investigation_id", "unknown")
    
    artifacts = []
    
    # 1. Entity Network Graph
    try:
        entities = state.get("entities", {})
        connections = state.get("connections", [])
        
        if entities:
            network_path = os.path.join(output_dir, f"entity_network_{investigation_id}_{timestamp}.html")
            generate_entity_network_graph(entities, connections, network_path)
            artifacts.append({
                "type": "html",
                "name": "Entity Network Graph",
                "path": network_path
            })
        else:
            log(f"   ⚠️  Skipping entity network (no entities)")
    except Exception as e:
        log(f"   ❌ Error generating entity network: {e}")
    
    # 2. Timeline Visualization
    try:
        facts = state.get("facts", [])
        iteration = state.get("iteration", 1)
        
        if facts:
            timeline_path = os.path.join(output_dir, f"timeline_{investigation_id}_{timestamp}.html")
            generate_timeline_visualization(facts, iteration, timeline_path)
            artifacts.append({
                "type": "html",
                "name": "Investigation Timeline",
                "path": timeline_path
            })
        else:
            log(f"   ⚠️  Skipping timeline (no facts)")
    except Exception as e:
        log(f"   ❌ Error generating timeline: {e}")
    
    # 3. Evidence Chain Sankey
    try:
        hypotheses = state.get("hypotheses", [])
        facts = state.get("facts", [])
        
        if hypotheses:
            sankey_path = os.path.join(output_dir, f"evidence_chain_{investigation_id}_{timestamp}.html")
            generate_evidence_chain_sankey(hypotheses, facts, sankey_path)
            artifacts.append({
                "type": "html",
                "name": "Evidence Flow Diagram",
                "path": sankey_path
            })
        else:
            log(f"   ⚠️  Skipping evidence chain (no hypotheses)")
    except Exception as e:
        log(f"   ❌ Error generating evidence chain: {e}")
    
    log(f"   ✅ Generated {len(artifacts)} artifacts")
    return artifacts


if __name__ == "__main__":
    # Test the artifact generators
    print("Testing artifact generators...")
    
    # Sample data
    test_state = {
        "investigation_id": "test_123",
        "iteration": 5,
        "entities": {
            "John Doe": {
                "type": "person",
                "role": "CEO of TechCorp",
                "importance": 0.9,
                "investigated": True
            },
            "TechCorp": {
                "type": "organization",
                "role": "Technology company",
                "importance": 0.8,
                "investigated": True
            },
            "Jane Smith": {
                "type": "person",
                "role": "Regulator",
                "importance": 0.7,
                "investigated": False
            }
        },
        "connections": [
            {"from": "John Doe", "to": "TechCorp", "type": "CEO of"},
            {"from": "Jane Smith", "to": "TechCorp", "type": "regulates"}
        ],
        "facts": [
            "TechCorp received $10M funding in 2023",
            "John Doe appointed as CEO in January 2024",
            "Regulatory review initiated in March 2024"
        ],
        "hypotheses": [
            {
                "id": "h1",
                "statement": "Funding influenced regulatory decisions",
                "status": "exploring",
                "confidence": 0.6,
                "questions": [
                    {"q": "Who funded TechCorp?", "a": "VentureX Partners"},
                    {"q": "When was the review started?", "a": "March 2024"}
                ]
            },
            {
                "id": "h2",
                "statement": "CEO has conflicts of interest",
                "status": "proven",
                "confidence": 0.85,
                "questions": [
                    {"q": "Does CEO own other companies?", "a": "Yes, 3 companies"}
                ]
            }
        ]
    }
    
    # Generate artifacts synchronously for testing
    import asyncio
    artifacts = asyncio.run(generate_all_artifacts(test_state, "test_artifacts"))
    
    print(f"\n✅ Generated {len(artifacts)} test artifacts:")
    for artifact in artifacts:
        print(f"   - {artifact['name']}: {artifact['path']}")

