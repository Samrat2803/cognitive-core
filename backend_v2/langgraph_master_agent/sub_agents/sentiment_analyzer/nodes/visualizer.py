"""
Visualizer Node - Generate artifacts using shared visualization tools
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from config import ARTIFACT_DIR
from state import SentimentAnalyzerState

# Import shared visualization tools
from shared.visualization_factory import (
    VisualizationFactory,
    create_sentiment_bar_chart,
    create_sentiment_radar_chart,
    create_sentiment_table
)


async def visualizer(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Generate artifacts using shared visualization tools
    
    DEFAULT BEHAVIOR: Creates 2 artifacts (Table + Bar Chart)
    User can request additional visualizations via state['requested_visualizations']
    """
    
    sentiment_scores = state["sentiment_scores"]
    bias_analysis = state.get("bias_analysis", {})
    search_results = state.get("search_results", {})
    query = state["query"]
    requested_viz = state.get("requested_visualizations", [])
    artifacts = []
    
    print(f"🎨 Visualizer: Creating artifacts...")
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', ARTIFACT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    print(f"   Output directory: {output_dir}")
    
    if not sentiment_scores:
        print(f"   ⚠️ No sentiment scores to visualize")
        return {
            "artifacts": [],
            "execution_log": state.get("execution_log", []) + [{
                "step": "visualizer",
                "action": "No artifacts generated (no data)"
            }]
        }
    
    # DEFAULT ARTIFACTS (Always Created)
    # 1. Data Table with Excel Export (3 sheets)
    print(f"   📊 Creating default visualizations...")
    try:
        artifact_table = create_sentiment_table(
            country_scores=sentiment_scores,
            bias_analysis=bias_analysis,
            query=query,
            output_dir=output_dir,
            search_results=search_results
        )
        artifacts.append(artifact_table)
        print(f"   ✅ Data table created: {artifact_table['artifact_id']}")
        if 'excel_path' in artifact_table:
            print(f"      Excel: {os.path.basename(artifact_table['excel_path'])}")
        
    except Exception as e:
        print(f"   ❌ Error creating data table: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. Bar Chart (Sentiment Comparison)
    try:
        artifact_bar = create_sentiment_bar_chart(
            country_scores=sentiment_scores,
            query=query,
            output_dir=output_dir
        )
        artifacts.append(artifact_bar)
        print(f"   ✅ Bar chart created: {artifact_bar['artifact_id']}")
        
    except Exception as e:
        print(f"   ❌ Error creating bar chart: {e}")
    
    # OPTIONAL ARTIFACTS (User Requested)
    if requested_viz:
        print(f"   🎨 Creating {len(requested_viz)} additional visualizations...")
        
        if "radar_chart" in requested_viz:
            try:
                artifact_radar = create_sentiment_radar_chart(
                    country_scores=sentiment_scores,
                    query=query,
                    output_dir=output_dir,
                    max_countries=5
                )
                artifacts.append(artifact_radar)
                print(f"   ✅ Radar chart created: {artifact_radar['artifact_id']}")
            except Exception as e:
                print(f"   ❌ Error creating radar chart: {e}")
        
        if "json" in requested_viz:
            try:
                from datetime import datetime
                table_data = {
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "countries": list(sentiment_scores.keys()),
                    "scores": sentiment_scores,
                    "bias": bias_analysis
                }
                
                artifact_json = VisualizationFactory.save_json_export(
                    data=table_data,
                    output_dir=output_dir,
                    artifact_type="sentiment_data_export",
                    title="Sentiment Data Export (JSON)"
                )
                artifacts.append(artifact_json)
                print(f"   ✅ JSON export created: {artifact_json['artifact_id']}")
            except Exception as e:
                print(f"   ❌ Error creating JSON export: {e}")
    
    print(f"   📦 Total artifacts created: {len(artifacts)}")
    print(f"      - Defaults: 2 (table + bar chart)")
    if requested_viz:
        print(f"      - Additional: {len(requested_viz)} requested")
    
    return {
        "artifacts": artifacts,
        "execution_log": state.get("execution_log", []) + [{
            "step": "visualizer",
            "action": f"Generated {len(artifacts)} artifacts (2 default + {len(requested_viz)} requested)"
        }]
    }

