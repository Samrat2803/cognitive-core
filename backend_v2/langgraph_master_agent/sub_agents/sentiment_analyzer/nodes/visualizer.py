"""
Visualizer Node - Generate artifacts using shared visualization tools
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from datetime import datetime
from config import ARTIFACT_DIR
from state import SentimentAnalyzerState

# Import shared visualization tools
from shared.visualization_factory import (
    VisualizationFactory,
    create_sentiment_bar_chart,
    create_sentiment_radar_chart,
    create_sentiment_table
)

# Import new infographic system
from shared.infographic_schemas import KeyMetricsDashboard, MetricItem, CategoryBreakdown, CategoryItem
from shared.html_infographic_renderer import HTMLInfographicRenderer


async def visualizer(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Generate artifacts using shared visualization tools
    
    DEFAULT BEHAVIOR: Creates ONLY 2 artifacts (Table + Bar Chart)
    
    Infographics are DISABLED by default and must be explicitly requested.
    For maps, infographics, and other visualizations, user must specifically ask.
    """
    
    sentiment_scores = state["sentiment_scores"]
    bias_analysis = state.get("bias_analysis", {})
    search_results = state.get("search_results", {})
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
    
    # NOTE: Infographics are DISABLED by default
    # User must explicitly request infographic visualizations via master agent
    # To enable infographics, uncomment the sections below:
    
    # # 3. HTML Infographics (Key Metrics Dashboard)
    # print(f"   🎨 Creating infographic...")
    # try:
    #     # Extract score values from sentiment_scores (which is Dict[str, Dict])
    #     # sentiment_scores[country] = {positive: X, negative: Y, neutral: Z, score: float}
    #     country_scores = {country: data.get('score', 0) if isinstance(data, dict) else data 
    #                      for country, data in sentiment_scores.items()}
    #     
    #     # Prepare metrics from sentiment scores
    #     sorted_scores = sorted(country_scores.items(), key=lambda x: x[1], reverse=True)[:4]
    #     
    #     # Calculate statistics
    #     total_articles = sum(len(search_results.get(country, [])) for country in sentiment_scores.keys())
    #     avg_sentiment = sum(country_scores.values()) / len(country_scores) if country_scores else 0
    #     top_country = sorted_scores[0] if sorted_scores else ("N/A", 0)
    #     
    #     # Create Key Metrics Dashboard
    #     infographic_data = KeyMetricsDashboard(
    #         title=f"{query}",
    #         subtitle="Sentiment Analysis Results",
    #         metrics=[
    #             MetricItem(value=f"{avg_sentiment:.1%}", label="Average Sentiment"),
    #             MetricItem(value=str(len(sentiment_scores)), label="Countries Analyzed"),
    #             MetricItem(value=str(total_articles), label="Articles Analyzed"),
    #             MetricItem(value=f"{top_country[0]}: {top_country[1]:.1%}", label="Top Country")
    #         ],
    #         insight=f"Overall sentiment is {'positive' if avg_sentiment > 0.5 else 'negative'} with {len(sentiment_scores)} countries analyzed across {total_articles} articles.",
    #         footer=f"Sentiment Analyzer • {datetime.now().strftime('%B %d, %Y')}"
    #     )
    #     
    #     # Render infographic
    #     renderer = HTMLInfographicRenderer(
    #         templates_dir=os.path.join(os.path.dirname(__file__), '../../../../shared/templates/html_samples'),
    #         output_dir=output_dir
    #     )
    #     
    #     artifact_infographic = renderer.render(
    #         schema_data=infographic_data,
    #         visual_template="gradient_modern"
    #     )
    #     
    #     artifacts.append(artifact_infographic)
    #     print(f"   ✅ Infographic created: {artifact_infographic['artifact_id']}")
    #     print(f"      File: {os.path.basename(artifact_infographic['path'])}")
    #     
    # except Exception as e:
    #     print(f"   ❌ Error creating infographic: {e}")
    #     import traceback
    #     traceback.print_exc()
    # 
    # # 4. Category Breakdown Infographic (if multiple countries)
    # if len(sentiment_scores) > 2:
    #     print(f"   🌍 Creating geographic breakdown infographic...")
    #     try:
    #         # Sort countries by sentiment (using country_scores from above)
    #         sorted_countries = sorted(country_scores.items(), key=lambda x: x[1], reverse=True)
    #         
    #         # Create category breakdown
    #         breakdown_data = CategoryBreakdown(
    #             title=f"{query}",
    #             subtitle="Geographic Sentiment Distribution",
    #             breakdown_type="Geographic",
    #             categories=[
    #                 CategoryItem(
    #                     name=country,
    #                     value=f"{score:.1%}",
    #                     description=f"Sentiment score"
    #                 ) for country, score in sorted_countries[:6]  # Top 6 countries
    #             ],
    #             total_label="Average Sentiment",
    #             total_value=f"{avg_sentiment:.1%}",
    #             insight=f"Highest support in {sorted_countries[0][0]} ({sorted_countries[0][1]:.1%}), lowest in {sorted_countries[-1][0]} ({sorted_countries[-1][1]:.1%})",
    #             footer=f"Sentiment Analyzer • {datetime.now().strftime('%B %d, %Y')}"
    #         )
    #         
    #         artifact_breakdown = renderer.render(
    #             schema_data=breakdown_data,
    #             visual_template="clean_corporate"
    #         )
    #         
    #         artifacts.append(artifact_breakdown)
    #         print(f"   ✅ Geographic breakdown created: {artifact_breakdown['artifact_id']}")
    #         
    #     except Exception as e:
    #         print(f"   ❌ Error creating breakdown infographic: {e}")
    
    print(f"   📦 Total artifacts created: {len(artifacts)}")
    print(f"      - Table (Excel export)")
    print(f"      - Bar chart")
    
    return {
        "artifacts": artifacts,
        "execution_log": state.get("execution_log", []) + [{
            "step": "visualizer",
            "action": f"Generated {len(artifacts)} default artifacts (table + bar chart)"
        }]
    }

