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


def generate_key_facts_infographic(
    facts: List[str],
    investigation_title: str = "Investigation",
    output_path: str = "key_facts_infographic.html"
) -> str:
    """
    Generate beautiful glassmorphism key facts infographic for social media
    
    Args:
        facts: List of key facts (top 4-6 most important)
        investigation_title: Title of the investigation
        output_path: Where to save the HTML file
        
    Returns:
        Path to generated HTML file
    """
    log(f"   📊 Generating glassmorphism key facts infographic...")
    
    # Select top 4 most important facts
    top_facts = facts[:4] if len(facts) >= 4 else facts
    
    # Pad with placeholder if less than 4 facts
    while len(top_facts) < 4:
        top_facts.append("Additional investigation ongoing...")
    
    # Fact icons (cycling through these)
    fact_icons = ["📄", "⚖️", "🔐", "📧", "💰", "🎯"]
    
    # Generate HTML with glassmorphism design
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Key Facts - {investigation_title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 0;
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .glass-container {{
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            position: relative;
            overflow: hidden;
            padding: 40px 20px;
        }}

        .glass-bg {{
            position: absolute;
            width: 400px;
            height: 400px;
            border-radius: 50%;
            filter: blur(100px);
            opacity: 0.5;
            pointer-events: none;
        }}

        .glass-bg.circle1 {{
            background: #ff6b6b;
            top: -100px;
            left: -100px;
        }}

        .glass-bg.circle2 {{
            background: #4ecdc4;
            bottom: -100px;
            right: -100px;
        }}

        .glass-content {{
            position: relative;
            z-index: 1;
            display: flex;
            flex-direction: column;
            gap: 30px;
        }}

        .glass-header {{
            text-align: center;
            color: white;
            margin-bottom: 10px;
        }}

        .glass-header h1 {{
            font-size: 2.5em;
            font-weight: 800;
            margin-bottom: 8px;
            text-shadow: 0 2px 20px rgba(0,0,0,0.2);
        }}

        .glass-header p {{
            font-size: 1.2em;
            font-weight: 300;
            opacity: 0.95;
        }}

        .glass-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }}

        .glass-card {{
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 25px;
            color: white;
            transition: all 0.3s ease;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}

        .glass-card:hover {{
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.2);
        }}

        .glass-card-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }}

        .glass-icon {{
            font-size: 2.5em;
            filter: drop-shadow(0 2px 8px rgba(0,0,0,0.2));
        }}

        .glass-number {{
            font-size: 0.75em;
            font-weight: 700;
            letter-spacing: 2px;
            opacity: 0.9;
        }}

        .glass-text {{
            font-size: 1.05em;
            line-height: 1.6;
            font-weight: 400;
        }}

        .glass-footer {{
            text-align: center;
            color: white;
            font-size: 0.95em;
            opacity: 0.9;
            margin-top: 20px;
        }}

        @media (max-width: 768px) {{
            .glass-header h1 {{
                font-size: 1.8em;
            }}
            
            .glass-cards {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="glass-container">
        <div class="glass-bg circle1"></div>
        <div class="glass-bg circle2"></div>
        
        <div class="glass-content">
            <div class="glass-header">
                <h1>🔍 {investigation_title}</h1>
                <p>Key Facts Uncovered</p>
            </div>

            <div class="glass-cards">"""
    
    # Add fact cards
    for i, fact in enumerate(top_facts, 1):
        icon = fact_icons[(i-1) % len(fact_icons)]
        html_content += f"""
                <div class="glass-card">
                    <div class="glass-card-header">
                        <div class="glass-icon">{icon}</div>
                        <div class="glass-number">FACT {i:02d}</div>
                    </div>
                    <div class="glass-text">
                        {fact}
                    </div>
                </div>"""
    
    html_content += """
            </div>

            <div class="glass-footer">
                Political Analyst Workbench • AI-Powered Investigation
            </div>
        </div>
    </div>
</body>
</html>"""
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    log(f"      ✅ Glassmorphism infographic saved to {output_path}")
    
    return output_path


def generate_entity_network_graph_OLD(
    entities: Dict[str, Any],
    connections: List[Dict[str, Any]],
    output_path: str = "entity_network.html"
) -> str:
    """
    OLD: Generate interactive entity network graph using pyvis
    REPLACED BY: generate_key_facts_infographic
    
    Args:
        entities: Dict of {name: {type, role, importance, investigated}}
        connections: List of {from, to, type}
        output_path: Where to save the HTML file
        
    Returns:
        Path to generated HTML file
    """
    log(f"   📊 Generating entity network graph...")
    
    # Initialize network with LIGHT background (dark was causing visibility issues in iframe)
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#ffffff",  # White background for better visibility
        font_color="#000000",  # Black text
        select_menu=True,
        filter_menu=True,
        notebook=False  # Disable notebook mode for better iframe compatibility
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
            "font": {"size": 16, "color": "#000000"},
            "borderWidth": 2,
            "borderWidthSelected": 4
        },
        "edges": {
            "color": {"color": "#666666", "highlight": "#d9f378"},
            "width": 2
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 100
        }
    }
    """)
    
    # Entity type colors (bright colors for white background)
    type_colors = {
        "person": "#4CAF50",       # Green for people
        "organization": "#2196F3", # Blue for organizations
        "location": "#FF9800",     # Orange for locations
        "substance": "#F44336",    # Red for substances
        "event": "#9C27B0",        # Purple for events
        "unknown": "#607D8B"       # Gray default
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
                color="#424242",  # Dark gray for visibility
                width=3,
                arrows="to"  # Add arrows to show direction
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
    Generate a modern card-based timeline with proper text wrapping and visual hierarchy
    
    Args:
        facts: List of fact strings
        iteration_count: Total iterations run (not used in new design)
        output_path: Where to save the HTML file
        
    Returns:
        Path to generated HTML file
    """
    log(f"   📊 Generating timeline visualization...")
    
    if not facts:
        log(f"      ⚠️  No facts to visualize")
        # Create empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No facts discovered yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="#5d535c")
        )
        fig.update_layout(
            title="Investigation Timeline",
            paper_bgcolor="#1c1e20",
            plot_bgcolor="#1c1e20",
            font=dict(color="white")
        )
        fig.write_html(output_path)
        return output_path
    
    # Generate custom HTML with card-based timeline
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Investigation Timeline</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Flex:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Roboto Flex', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1c1e20 0%, #2a2c2e 100%);
            color: #ffffff;
            padding: 40px 20px;
            min-height: 100vh;
        }}
        
        .timeline-container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .timeline-header {{
            text-align: center;
            margin-bottom: 50px;
        }}
        
        .branding {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-bottom: 20px;
            opacity: 0.8;
        }}
        
        .branding-text {{
            font-size: 14px;
            color: #5d535c;
            font-weight: 500;
            letter-spacing: 0.5px;
        }}
        
        .branding-logo {{
            font-size: 18px;
        }}
        
        .timeline-title {{
            font-size: 32px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 10px;
            letter-spacing: -0.02em;
        }}
        
        .timeline-subtitle {{
            font-size: 16px;
            color: #d9f378;
            font-weight: 500;
        }}
        
        .timeline {{
            position: relative;
            padding-left: 50px;
        }}
        
        /* Vertical timeline line */
        .timeline::before {{
            content: '';
            position: absolute;
            left: 20px;
            top: 0;
            bottom: 0;
            width: 4px;
            background: linear-gradient(180deg, #d9f378 0%, #5d535c 100%);
            border-radius: 2px;
        }}
        
        .timeline-item {{
            position: relative;
            margin-bottom: 40px;
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
        }}
        
        .timeline-item:nth-child(1) {{ animation-delay: 0.1s; }}
        .timeline-item:nth-child(2) {{ animation-delay: 0.2s; }}
        .timeline-item:nth-child(3) {{ animation-delay: 0.3s; }}
        .timeline-item:nth-child(4) {{ animation-delay: 0.4s; }}
        .timeline-item:nth-child(5) {{ animation-delay: 0.5s; }}
        .timeline-item:nth-child(n+6) {{ animation-delay: 0.6s; }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        /* Timeline marker */
        .timeline-marker {{
            position: absolute;
            left: -38px;
            top: 8px;
            width: 20px;
            height: 20px;
            background: #d9f378;
            border: 4px solid #1c1e20;
            border-radius: 50%;
            box-shadow: 0 0 0 4px rgba(217, 243, 120, 0.2);
            z-index: 2;
            transition: all 0.3s ease;
        }}
        
        .timeline-item:hover .timeline-marker {{
            transform: scale(1.3);
            box-shadow: 0 0 0 8px rgba(217, 243, 120, 0.3);
        }}
        
        /* Timeline number badge */
        .timeline-number {{
            position: absolute;
            left: -48px;
            top: 45px;
            width: 40px;
            height: 24px;
            background: #5d535c;
            color: #d9f378;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 700;
            z-index: 1;
        }}
        
        /* Fact card */
        .fact-card {{
            background: linear-gradient(135deg, #333333 0%, #2a2c2e 100%);
            border-left: 4px solid #d9f378;
            border-radius: 8px;
            padding: 20px 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .fact-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #d9f378 0%, transparent 100%);
        }}
        
        .timeline-item:hover .fact-card {{
            transform: translateX(8px);
            box-shadow: 0 8px 24px rgba(217, 243, 120, 0.2);
            border-left-color: #ffffff;
        }}
        
        .fact-text {{
            font-size: 15px;
            line-height: 1.7;
            color: #e8e8e8;
            font-weight: 400;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .timeline {{
                padding-left: 40px;
            }}
            
            .timeline::before {{
                left: 15px;
            }}
            
            .timeline-marker {{
                left: -33px;
            }}
            
            .timeline-number {{
                left: -43px;
            }}
            
            .fact-card {{
                padding: 16px 20px;
            }}
            
            .timeline-title {{
                font-size: 24px;
            }}
        }}
        
        /* Color accessibility */
        @media (prefers-contrast: high) {{
            .fact-card {{
                border-left-width: 6px;
            }}
        }}
    </style>
</head>
<body>
    <div class="timeline-container">
        <div class="timeline-header">
            <div class="branding">
                <span class="branding-logo">🧠</span>
                <span class="branding-text">COGNITIVE CORE</span>
            </div>
            <h1 class="timeline-title">Investigation Timeline</h1>
            <p class="timeline-subtitle">{len(facts)} facts discovered in chronological order</p>
        </div>
        
        <div class="timeline">
"""
    
    # Add each fact as a timeline item
    for idx, fact in enumerate(facts, start=1):
        html_content += f"""
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-number">#{idx}</div>
                <div class="fact-card">
                    <div class="fact-text">{fact}</div>
                </div>
            </div>
"""
    
    html_content += """
        </div>
    </div>
</body>
</html>
"""
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
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
    
    # 1. Key Facts Infographic (Glassmorphism)
    try:
        facts = state.get("facts", [])
        initial_query = state.get("initial_query", "Investigation")
        
        if facts and len(facts) > 0:
            # Extract top 4-6 most important facts
            top_facts = facts[:6] if len(facts) >= 6 else facts
            
            infographic_path = os.path.join(output_dir, f"key_facts_{investigation_id}_{timestamp}.html")
            generate_key_facts_infographic(top_facts, initial_query, infographic_path)
            artifacts.append({
                "type": "html",
                "name": "Key Facts Infographic",
                "path": infographic_path
            })
        else:
            log(f"   ⚠️  Skipping key facts infographic (no facts)")
    except Exception as e:
        log(f"   ❌ Error generating key facts infographic: {e}")
    
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

