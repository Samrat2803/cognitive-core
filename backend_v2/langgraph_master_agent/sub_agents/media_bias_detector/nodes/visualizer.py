"""
Visualizer Node - Generates artifacts using shared visualization tools
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from typing import Dict, Any
import json
import uuid

from state import MediaBiasDetectorState
from config import ARTIFACT_DIR

# Import shared visualization factory
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))
from shared.visualization_factory import VisualizationFactory

viz_factory = VisualizationFactory()


async def visualizer(state: MediaBiasDetectorState) -> Dict[str, Any]:
    """
    Generate visualization artifacts:
    1. Bias spectrum chart (diverging bar chart)
    2. Source comparison matrix (heatmap)
    3. Framing comparison chart (grouped bar)
    4. JSON data export
    """
    
    bias_classification = state.get("bias_classification", {})
    loaded_language = state.get("loaded_language", {})
    framing_analysis = state.get("framing_analysis", {})
    
    print(f"\n[Visualizer] Generating artifacts...")
    
    # Create artifact directory if it doesn't exist
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    
    artifacts = []
    
    # Artifact 1: Bias Spectrum Chart (diverging bar)
    if bias_classification:
        try:
            bias_artifact = _create_bias_spectrum_chart(bias_classification)
            artifacts.append(bias_artifact)
            print(f"[Visualizer] Created bias spectrum chart: {bias_artifact['artifact_id']}")
        except Exception as e:
            print(f"[Visualizer] Error creating bias spectrum chart: {str(e)}")
    
    # Artifact 2: Comparison Matrix (showing multiple metrics)
    if bias_classification and loaded_language:
        try:
            matrix_artifact = _create_comparison_matrix(bias_classification, loaded_language)
            artifacts.append(matrix_artifact)
            print(f"[Visualizer] Created comparison matrix: {matrix_artifact['artifact_id']}")
        except Exception as e:
            print(f"[Visualizer] Error creating comparison matrix: {str(e)}")
    
    # Artifact 3: Framing Analysis Chart
    if framing_analysis:
        try:
            framing_artifact = _create_framing_chart(framing_analysis)
            artifacts.append(framing_artifact)
            print(f"[Visualizer] Created framing chart: {framing_artifact['artifact_id']}")
        except Exception as e:
            print(f"[Visualizer] Error creating framing chart: {str(e)}")
    
    # Artifact 4: JSON Data Export
    try:
        json_artifact = _create_json_export(state)
        artifacts.append(json_artifact)
        print(f"[Visualizer] Created JSON export: {json_artifact['artifact_id']}")
    except Exception as e:
        print(f"[Visualizer] Error creating JSON export: {str(e)}")
    
    print(f"[Visualizer] Generated {len(artifacts)} artifacts")
    
    return {
        "artifacts": artifacts,
        "execution_log": state.get("execution_log", []) + [{
            "step": "visualizer",
            "action": f"Generated {len(artifacts)} artifacts"
        }]
    }


def _create_bias_spectrum_chart(bias_classification: dict) -> dict:
    """Create bias spectrum diverging bar chart"""
    
    # Prepare data for diverging bar chart
    sources = list(bias_classification.keys())
    scores = [bias_classification[s]["bias_score"] for s in sources]
    spectrums = [bias_classification[s]["spectrum"] for s in sources]
    
    # Sort by bias score
    sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i])
    sources = [sources[i] for i in sorted_indices]
    scores = [scores[i] for i in sorted_indices]
    spectrums = [spectrums[i] for i in sorted_indices]
    
    # Create horizontal bar chart
    fig = viz_factory.create_bar_chart(
        x_data=sources,
        y_data=scores,
        title="Media Bias Spectrum Analysis",
        x_label="Source",
        y_label="Bias Score",
        color_scale="RdBu_r",  # Red-Blue diverging
        color_range=(-1, 1),
        height=400 + len(sources) * 30
    )
    
    # Save artifact
    artifact = viz_factory.save_artifact(
        fig=fig,
        output_dir=ARTIFACT_DIR,
        artifact_type="bias_spectrum",
        title="Media Bias Spectrum",
        data={
            "sources": sources,
            "scores": scores,
            "spectrums": spectrums
        }
    )
    
    # Add extra metadata
    artifact["description"] = "Political lean of each source (-1.0 = far left, +1.0 = far right)"
    artifact["metadata"] = {
        "sources_analyzed": len(sources),
        "bias_range": f"{min(scores):.2f} to {max(scores):.2f}"
    }
    
    return artifact


def _create_comparison_matrix(bias_classification: dict, loaded_language: dict) -> dict:
    """Create comparison matrix showing multiple bias metrics"""
    
    sources = list(bias_classification.keys())
    
    # Prepare matrix data
    metrics = ["Bias Score", "Loaded Language", "Confidence"]
    z_data = []
    
    for source in sources:
        row = [
            bias_classification[source]["bias_score"],
            len(loaded_language.get(source, [])) / 10.0,  # Normalize to 0-1 range
            bias_classification[source]["confidence"]
        ]
        z_data.append(row)
    
    # Create heatmap
    fig = viz_factory.create_heatmap(
        z_data=z_data,
        x_labels=metrics,
        y_labels=sources,
        title="Source Comparison Matrix",
        color_scale="RdYlGn",
        height=300 + len(sources) * 40
    )
    
    # Save artifact
    artifact = viz_factory.save_artifact(
        fig=fig,
        output_dir=ARTIFACT_DIR,
        artifact_type="comparison_matrix",
        title="Source Comparison Matrix",
        data={
            "sources": sources,
            "metrics": metrics,
            "values": z_data
        }
    )
    
    # Add extra metadata
    artifact["description"] = "Comparison of bias metrics across sources"
    artifact["metadata"] = {
        "sources_analyzed": len(sources),
        "metrics": metrics
    }
    
    return artifact


def _create_framing_chart(framing_analysis: dict) -> dict:
    """Create chart showing framing types used by each source"""
    
    sources = list(framing_analysis.keys())
    primary_frames = [framing_analysis[s]["primary_frame"] for s in sources]
    
    # Count frame types
    frame_counts = {}
    for frame in primary_frames:
        frame_counts[frame] = frame_counts.get(frame, 0) + 1
    
    # Prepare data for bar chart
    frames = list(frame_counts.keys())
    counts = list(frame_counts.values())
    
    # Create bar chart
    fig = viz_factory.create_bar_chart(
        x_data=frames,
        y_data=counts,
        title="Story Framing Distribution",
        x_label="Frame Type",
        y_label="Number of Sources",
        color_scale="Viridis",
        color_range=(0, max(counts)),
        height=400
    )
    
    # Save artifact
    artifact = viz_factory.save_artifact(
        fig=fig,
        output_dir=ARTIFACT_DIR,
        artifact_type="framing_chart",
        title="Story Framing Analysis",
        data={
            "frames": frames,
            "counts": counts,
            "sources": sources
        }
    )
    
    # Add extra metadata
    artifact["description"] = "How different sources frame the story"
    artifact["metadata"] = {
        "sources_analyzed": len(sources),
        "frame_types": frames
    }
    
    return artifact


def _create_json_export(state: MediaBiasDetectorState) -> dict:
    """Export all data as JSON"""
    
    artifact_id = f"bias_data_{uuid.uuid4().hex[:12]}"
    json_path = os.path.join(ARTIFACT_DIR, f"{artifact_id}.json")
    
    export_data = {
        "query": state.get("query", ""),
        "sources_analyzed": list(state.get("bias_classification", {}).keys()),
        "total_articles": state.get("total_articles_found", 0),
        "bias_classification": state.get("bias_classification", {}),
        "loaded_language": state.get("loaded_language", {}),
        "framing_analysis": state.get("framing_analysis", {}),
        "overall_bias_range": state.get("overall_bias_range", {}),
        "consensus_points": state.get("consensus_points", []),
        "divergence_points": state.get("divergence_points", []),
        "key_findings": state.get("key_findings", []),
        "recommendations": state.get("recommendations", []),
        "confidence": state.get("confidence", 0.0)
    }
    
    with open(json_path, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    return {
        "artifact_id": artifact_id,
        "type": "json_export",
        "title": "Bias Analysis Data",
        "description": "Complete analysis data in JSON format",
        "json_path": json_path,
        "metadata": {
            "sources_analyzed": len(export_data["sources_analyzed"]),
            "file_size_kb": os.path.getsize(json_path) / 1024
        }
    }

