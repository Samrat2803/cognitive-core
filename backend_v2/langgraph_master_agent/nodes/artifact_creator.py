"""
Artifact Creator Node
Creates visualizations and saves them
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from datetime import datetime
from typing import Dict, Any
from langgraph_master_agent.tools.visualization_tools import (
    BarChartTool,
    LineChartTool,
    MindMapTool,
    MapChartTool,
    auto_visualize
)
from shared.observability import ObservabilityManager
from shared.html_infographic_renderer import HTMLInfographicRenderer
from shared.infographic_schemas import INFOGRAPHIC_SCHEMAS

observe = ObservabilityManager.get_observe_decorator()

# Import S3 service (optional)
try:
    backend_path = os.path.join(os.path.dirname(__file__), '../../backend_server')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from services.s3_service import s3_service
    S3_AVAILABLE = s3_service is not None
    if S3_AVAILABLE:
        print("✅ S3 service available for artifact storage")
except ImportError as e:
    print(f"⚠️  S3 service not available: {e}")
    s3_service = None
    S3_AVAILABLE = False


@observe(name="artifact_creator_node")
async def artifact_creator(state: dict) -> dict:
    """
    Create and save visualization artifacts
    
    Args:
        state: Current agent state with artifact_type and data
    
    Returns:
        Updated state with created artifact
    """
    
    artifact_type = state.get("artifact_type")
    artifact_data = state.get("artifact_data")
    query = state.get("current_message", "")
    
    try:
        print(f"🎨 Artifact Creator: Creating {artifact_type}")
        print(f"   Artifact data provided: {artifact_data is not None}")
        
        # Prepare data based on type
        if artifact_type == "bar_chart":
            data_to_use = artifact_data if artifact_data else _extract_bar_data(state)
        elif artifact_type == "line_chart":
            data_to_use = artifact_data if artifact_data else _extract_line_data(state)
        elif artifact_type == "map_chart":
            data_to_use = artifact_data if artifact_data else _extract_map_data(state)
        elif artifact_type == "mind_map":
            data_to_use = artifact_data if artifact_data else _extract_mindmap_data(state)
        elif artifact_type == "infographic":
            data_to_use = artifact_data  # Infographic data already structured
        else:
            data_to_use = artifact_data if artifact_data else _extract_bar_data(state)
        
        print(f"   Data to use: {str(data_to_use)[:200]}...")  # Truncate to avoid format issues
        print(f"   Current working directory: {os.getcwd()}")
        
        # Get title from state or generate default
        title = state.get("artifact_title") or f"Visualization: {query[:50]}"
        
        # Create artifact based on type
        if artifact_type == "bar_chart":
            artifact = BarChartTool.create(
                data=data_to_use,
                title=title,
                x_label=data_to_use.get("x_label", "Category"),
                y_label=data_to_use.get("y_label", "Value")
            )
        
        elif artifact_type == "line_chart":
            artifact = LineChartTool.create(
                data=data_to_use,
                title=title,
                x_label=data_to_use.get("x_label", "Time"),
                y_label=data_to_use.get("y_label", "Value")
            )
        
        elif artifact_type == "map_chart":
            artifact = MapChartTool.create(
                data=data_to_use,
                title=title,
                legend_title=data_to_use.get("legend_title", "Score")
            )
        
        elif artifact_type == "mind_map":
            artifact = MindMapTool.create(
                data=data_to_use,
                title=title
            )
        
        elif artifact_type == "infographic":
            # Extract infographic type and schema data
            infographic_type = data_to_use.get("infographic_type", "key_metrics")
            schema_data_dict = data_to_use.get("schema_data", {})
            
            print(f"   Creating infographic: {infographic_type}")
            print(f"   Schema data keys: {list(schema_data_dict.keys())}")
            
            # Validate and create schema instance
            schema_class = INFOGRAPHIC_SCHEMAS.get(infographic_type)
            if not schema_class:
                raise ValueError(f"Unknown infographic type: {infographic_type}")
            
            schema_instance = schema_class(**schema_data_dict)
            
            # Render infographic
            renderer = HTMLInfographicRenderer()
            artifact_info = renderer.render(
                schema_data=schema_instance,
                visual_template="template_3",  # Default to template 3 (modern card-based)
                output_dir="langgraph_master_agent/artifacts/infographics"
            )
            
            # Convert to standard artifact format
            artifact = {
                "artifact_id": artifact_info["artifact_id"],
                "type": "infographic",
                "html_path": artifact_info["path"],
                "png_path": artifact_info["path"].replace('.html', '.png'),  # Will be generated
                "title": title,
                "metadata": {
                    "infographic_type": infographic_type,
                    "schema_type": artifact_info["schema_type"],
                    "visual_template": artifact_info["visual_template"]
                }
            }
        
        else:
            # Auto-detect
            artifact = auto_visualize(
                data=data_to_use,
                context=query,
                title=f"Visualization: {query[:50]}"
            )
        
        # Add query context to artifact
        artifact["query"] = query
        artifact["sources"] = state.get("citations", [])
        artifact["session_id"] = state.get("session_id", "N/A")
        
        # Upload to S3 if available
        if S3_AVAILABLE and s3_service:
            try:
                print(f"📤 Uploading artifact to S3...")
                # Upload and get presigned URLs (24 hour expiration)
                html_url, png_url = await s3_service.upload_artifact_pair(
                    html_path=artifact["html_path"],
                    png_path=artifact["png_path"],
                    artifact_id=artifact["artifact_id"],
                    artifact_type=artifact["type"],
                    generate_urls=True,
                    url_expiration=86400  # 24 hours
                )
                
                # Also get the S3 keys (without presigned URLs) for storage
                html_key = f"artifacts/{artifact['type']}/{artifact['artifact_id']}/{os.path.basename(artifact['html_path'])}"
                png_key = f"artifacts/{artifact['type']}/{artifact['artifact_id']}/{os.path.basename(artifact['png_path'])}"
                
                if html_url and png_url:
                    artifact["s3_html_key"] = html_key        # Store permanent S3 key
                    artifact["s3_png_key"] = png_key          # Store permanent S3 key
                    artifact["s3_html_url"] = html_url        # Presigned URL (temp, 24h)
                    artifact["s3_png_url"] = png_url          # Presigned URL (temp, 24h)
                    artifact["storage"] = "s3"
                    print(f"✅ Artifact uploaded to S3 (private, encrypted)")
                    print(f"   HTML Key: {html_key}")
                    print(f"   PNG Key: {png_key}")
                    print(f"   Presigned URLs valid for 24 hours")
                else:
                    artifact["storage"] = "local"
                    print("⚠️  S3 upload failed, using local storage")
                    
            except Exception as s3_error:
                print(f"⚠️  S3 upload error: {s3_error}, falling back to local storage")
                artifact["storage"] = "local"
        else:
            artifact["storage"] = "local"
            print("📁 Artifact stored locally (S3 not available)")
        
        # Store in state
        state["artifact"] = artifact
        state["artifact_id"] = artifact["artifact_id"]
        
        # Log creation
        data_points = len(data_to_use.get('categories', data_to_use.get('x', []))) if data_to_use else 0
        state["execution_log"].append({
            "step": "artifact_creator",
            "action": f"Created {artifact_type or 'auto'} visualization",
            "timestamp": datetime.now().isoformat(),
            "input": f"Type: {artifact_type}, Data points: {data_points}",
            "output": f"Artifact ID: {artifact['artifact_id']}, Files: HTML + PNG"
        })
        
        # Save to MongoDB (if configured)
        try:
            artifact_db_id = await _save_to_mongodb(artifact)
            state["artifact"]["mongodb_id"] = artifact_db_id
        except Exception as db_error:
            print(f"MongoDB save skipped: {db_error}")
            # Continue without DB - files are already saved
        
    except Exception as e:
        error_msg = f"Artifact creation failed: {str(e)}"
        state["error_log"] = state.get("error_log", [])
        state["error_log"].append(error_msg)
        
        state["execution_log"].append({
            "step": "artifact_creator",
            "action": "Error creating artifact",
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
            "input": f"Type: {artifact_type}",
            "output": f"Failed: {str(e)[:100]}"
        })
    
    return state


def _extract_bar_data(state: dict) -> Dict[str, Any]:
    """Extract data for bar chart from tool results"""
    tool_results = state.get("tool_results", {})
    
    # From Tavily search results
    if tool_results.get("tavily_search", {}).get("success"):
        results = tool_results["tavily_search"].get("results", [])
        return {
            "categories": [r.get("title", "")[:30] + "..." for r in results[:8]],
            "values": [r.get("score", 0.5) * 100 for r in results[:8]]
        }
    
    # Default sample data
    return {
        "categories": ["Result 1", "Result 2", "Result 3"],
        "values": [75, 85, 60]
    }


def _extract_line_data(state: dict) -> Dict[str, Any]:
    """Extract data for line chart"""
    # For now, return sample trend data
    # TODO: Extract temporal data from results
    return {
        "x": ["Jan", "Feb", "Mar", "Apr", "May"],
        "y": [10, 15, 13, 17, 20]
    }


def _extract_mindmap_data(state: dict) -> Dict[str, Any]:
    """Extract data for mind map"""
    query = state.get("current_message", "")
    
    # Simple hierarchical structure from query
    return {
        "root": query[:50],
        "children": [
            {"name": "Analysis", "value": 10},
            {"name": "Sources", "value": 8},
            {"name": "Insights", "value": 12}
        ]
    }


def _extract_map_data(state: dict) -> Dict[str, Any]:
    """Extract data for map chart from conversation history or state"""
    
    # Try to extract from sub-agent results first
    sub_agent_results = state.get("sub_agent_results", {})
    for agent_name, agent_result in sub_agent_results.items():
        if isinstance(agent_result, dict):
            agent_data = agent_result.get("data", {})
            sentiment_scores = agent_data.get("sentiment_scores", {})
            
            if sentiment_scores:
                # Extract countries and sentiment scores
                countries = list(sentiment_scores.keys())
                values = [scores.get("score", 0) for scores in sentiment_scores.values()]
                labels = [
                    f"{country}: {scores.get('sentiment', 'unknown')} ({scores.get('score', 0):+.2f})"
                    for country, scores in sentiment_scores.items()
                ]
                
                return {
                    "countries": countries,
                    "values": values,
                    "labels": labels,
                    "legend_title": "Sentiment Score"
                }
    
    # Default sample data if no sentiment data found
    return {
        "countries": ["US", "UK"],
        "values": [0.5, -0.3],
        "labels": ["US: Positive", "UK: Negative"],
        "legend_title": "Score"
    }


async def _save_to_mongodb(artifact: dict) -> str:
    """
    Save artifact metadata to MongoDB (optional)
    
    Returns:
        MongoDB document ID
    """
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        if not connection_string:
            raise Exception("MongoDB not configured")
        
        client = AsyncIOMotorClient(connection_string)
        db = client["political_analyst_db"]
        collection = db["artifacts"]
        
        result = await collection.insert_one(artifact)
        return str(result.inserted_id)
    
    except Exception as e:
        raise Exception(f"MongoDB save failed: {e}")

