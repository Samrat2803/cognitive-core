"""Generate final investigative report with visual artifacts"""

from typing import Dict, Any
import json
from datetime import datetime
from ..state import InvestigativeState
from ..utils.network_builder import build_network_graph, build_causal_diagram, generate_html_visualization
from ..utils.causal_extraction import build_causal_chains


async def report_generator(state: InvestigativeState) -> Dict[str, Any]:
    """
    Generate final investigative report with two key artifacts:
    1. Spider Web Network (entity connections)
    2. Causal Diagram (cause → effect chains)
    """
    print("\n📊 REPORT GENERATOR: Creating visual artifacts...")
    
    # Build artifacts
    print("  → Building network graph...")
    network_graph = build_network_graph(state)
    
    print("  → Building causal diagram...")
    causal_diagram = build_causal_diagram(state)
    
    print("  → Generating HTML visualization...")
    html_report = generate_html_visualization(network_graph, causal_diagram)
    
    # Generate JSON artifacts
    artifacts = [
        {
            "type": "network_graph",
            "title": "Entity Network (Spider Web)",
            "format": "json",
            "data": network_graph,
            "description": "Interactive network showing all entities and their connections"
        },
        {
            "type": "causal_diagram",
            "title": "Causal Chain Diagram",
            "format": "mermaid",
            "data": causal_diagram,
            "description": "Flowchart showing cause → effect relationships"
        },
        {
            "type": "html_report",
            "title": "Complete Investigative Report",
            "format": "html",
            "data": html_report,
            "description": "Standalone HTML file with both visualizations"
        },
        {
            "type": "investigation_summary",
            "title": "Investigation Summary",
            "format": "json",
            "data": generate_summary(state),
            "description": "Text summary of findings"
        }
    ]
    
    print(f"  ✓ Generated {len(artifacts)} artifacts")
    print(f"  ✓ Network: {network_graph['metadata']['total_entities']} entities, {network_graph['metadata']['total_connections']} connections")
    print(f"  ✓ Causal: {causal_diagram['metadata']['causal_links']} causal links")
    
    return {
        "artifacts": artifacts,
        "should_continue": False  # Investigation complete
    }


def generate_summary(state: InvestigativeState) -> Dict[str, Any]:
    """Generate text summary of investigation"""
    entities = state.get("entities", {})
    funding_network = state.get("funding_network", {})
    hypotheses = state.get("investigation_hypotheses", [])
    suspicious_patterns = state.get("suspicious_patterns", [])
    
    # Key findings
    key_entities = [
        name for name, entity in entities.items()
        if entity.get("importance", 0) > 0.7
    ]
    
    suspicious_funders = []
    for org, funders in funding_network.items():
        for funder in funders:
            funder_entity = entities.get(funder, {})
            if funder_entity.get("corruption_charges") or funder_entity.get("arms_dealer"):
                suspicious_funders.append(f"{funder} → {org}")
    
    summary = {
        "investigation_query": state.get("query", ""),
        "investigation_depth": state.get("investigation_depth", 0),
        "overall_confidence": state.get("overall_confidence", 0.0),
        "total_entities_investigated": len([e for e in entities.values() if e.get("investigated")]),
        "key_entities": key_entities[:10],
        "funding_network_size": len(funding_network),
        "suspicious_funders": suspicious_funders,
        "top_hypotheses": [
            {
                "hypothesis": h["hypothesis"],
                "confidence": h["confidence"]
            }
            for h in sorted(hypotheses, key=lambda x: x["confidence"], reverse=True)[:3]
        ],
        "suspicious_patterns_found": len(suspicious_patterns),
        "critical_patterns": [
            p["description"] for p in suspicious_patterns
            if p["suspicion_level"] == "critical"
        ],
        "unanswered_questions": [
            q["question"] for q in state.get("generated_questions", [])
            if not q.get("answered")
        ][:5],
        "investigation_timestamp": datetime.utcnow().isoformat()
    }
    
    return summary


