"""
Visualizer Node - Generate artifacts (simplified for testing)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
import plotly.graph_objects as go
import plotly.express as px
from ..config import ARTIFACT_DIR, MAP_COLOR_SCALE
from ..state import SentimentAnalyzerState
import uuid
from datetime import datetime


async def visualizer(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Generate artifacts"""
    
    sentiment_scores = state["sentiment_scores"]
    query = state["query"]
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
    
    countries_list = list(sentiment_scores.keys())
    scores_list = [sentiment_scores[c].get('score', 0) for c in countries_list]
    
    # Artifact 1: Bar Chart (Sentiment Scores) - Simple and reliable
    try:
        artifact_id_bar = f"sentiment_bar_{uuid.uuid4().hex[:12]}"
        
        fig_bar = go.Figure(data=[
            go.Bar(
                x=countries_list,
                y=scores_list,
                marker=dict(
                    color=scores_list,
                    colorscale='RdYlGn',
                    cmin=-1,
                    cmax=1,
                    colorbar=dict(title="Sentiment")
                )
            )
        ])
        
        fig_bar.update_layout(
            title=f"Sentiment Analysis: {query}",
            xaxis_title="Country",
            yaxis_title="Sentiment Score",
            height=500,
            template="plotly_white"
        )
        
        html_path = os.path.join(output_dir, f"{artifact_id_bar}.html")
        fig_bar.write_html(html_path)
        
        artifacts.append({
            "artifact_id": artifact_id_bar,
            "type": "bar_chart",
            "title": "Sentiment Score Comparison",
            "html_path": html_path
        })
        
        print(f"   ✅ Bar chart created: {artifact_id_bar}")
        
    except Exception as e:
        print(f"   ❌ Error creating bar chart: {e}")
    
    # Artifact 2: Radar Chart (Multi-dimensional comparison)
    try:
        artifact_id_radar = f"sentiment_radar_{uuid.uuid4().hex[:12]}"
        
        fig_radar = go.Figure()
        
        for country in countries_list[:5]:  # Limit to 5 countries for readability
            scores = sentiment_scores[country]
            fig_radar.add_trace(go.Scatterpolar(
                r=[
                    scores.get('positive_pct', 0.33),
                    scores.get('neutral_pct', 0.33),
                    scores.get('negative_pct', 0.33)
                ],
                theta=['Positive', 'Neutral', 'Negative'],
                fill='toself',
                name=country
            ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            title="Sentiment Distribution by Country",
            height=500
        )
        
        html_path = os.path.join(output_dir, f"{artifact_id_radar}.html")
        fig_radar.write_html(html_path)
        
        artifacts.append({
            "artifact_id": artifact_id_radar,
            "type": "radar_chart",
            "title": "Sentiment Distribution Radar",
            "html_path": html_path
        })
        
        print(f"   ✅ Radar chart created: {artifact_id_radar}")
        
    except Exception as e:
        print(f"   ❌ Error creating radar chart: {e}")
    
    # Artifact 3: Summary Table (JSON format for now)
    try:
        artifact_id_table = f"sentiment_table_{uuid.uuid4().hex[:12]}"
        
        import json
        table_data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "countries": countries_list,
            "scores": sentiment_scores
        }
        
        json_path = os.path.join(output_dir, f"{artifact_id_table}.json")
        with open(json_path, 'w') as f:
            json.dump(table_data, f, indent=2)
        
        artifacts.append({
            "artifact_id": artifact_id_table,
            "type": "data_table",
            "title": "Sentiment Data Export",
            "json_path": json_path
        })
        
        print(f"   ✅ Data export created: {artifact_id_table}")
        
    except Exception as e:
        print(f"   ❌ Error creating data export: {e}")
    
    print(f"   Total artifacts created: {len(artifacts)}")
    
    return {
        "artifacts": artifacts,
        "execution_log": state.get("execution_log", []) + [{
            "step": "visualizer",
            "action": f"Generated {len(artifacts)} artifacts"
        }]
    }

