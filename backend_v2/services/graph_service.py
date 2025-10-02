"""
Graph Visualization Service
Extracts LangGraph structure and execution state for frontend visualization
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict, Any, List, Optional
from langgraph_master_agent.graph import create_master_agent_graph
from datetime import datetime


class GraphVisualizationService:
    """Service for extracting and formatting graph data for visualization"""
    
    def __init__(self):
        self.graph = create_master_agent_graph()
    
    def get_static_graph_structure(self) -> Dict[str, Any]:
        """
        Extract static graph structure (nodes and edges)
        Returns JSON-serializable format for frontend visualization
        """
        
        # Get the compiled graph
        compiled_graph = self.graph.get_graph()
        
        # Extract nodes
        nodes = []
        node_metadata = self._get_node_metadata()
        
        for node_id in compiled_graph.nodes:
            node_info = {
                "id": node_id,
                "label": self._format_node_label(node_id),
                "type": self._get_node_type(node_id),
                "description": node_metadata.get(node_id, {}).get("description", ""),
                "category": node_metadata.get(node_id, {}).get("category", "processing"),
                "metadata": node_metadata.get(node_id, {})
            }
            nodes.append(node_info)
        
        # Extract edges
        edges = []
        edge_id = 0
        
        # LangGraph edges can be in different formats
        if hasattr(compiled_graph, 'edges'):
            graph_edges = compiled_graph.edges
            
            # Handle list of edges
            if isinstance(graph_edges, list):
                for edge in graph_edges:
                    # Edge is tuple (source, target) or has attributes
                    if isinstance(edge, tuple) and len(edge) >= 2:
                        source, target = edge[0], edge[1]
                        label = edge[2] if len(edge) > 2 else ""
                        edges.append({
                            "id": f"edge_{edge_id}",
                            "source": source,
                            "target": target,
                            "type": "conditional" if label else "default",
                            "label": self._format_condition_label(label) if label else ""
                        })
                        edge_id += 1
                    elif hasattr(edge, 'source') and hasattr(edge, 'target'):
                        edges.append({
                            "id": f"edge_{edge_id}",
                            "source": edge.source,
                            "target": edge.target,
                            "type": "default",
                            "label": ""
                        })
                        edge_id += 1
            
            # Handle dict of edges
            elif isinstance(graph_edges, dict):
                for source_node, target_nodes in graph_edges.items():
                    if isinstance(target_nodes, list):
                        for target_node in target_nodes:
                            edges.append({
                                "id": f"edge_{edge_id}",
                                "source": source_node,
                                "target": target_node,
                                "type": "default",
                                "label": ""
                            })
                            edge_id += 1
                    elif isinstance(target_nodes, dict):
                        for condition, target_node in target_nodes.items():
                            edges.append({
                                "id": f"edge_{edge_id}",
                                "source": source_node,
                                "target": target_node,
                                "type": "conditional",
                                "label": self._format_condition_label(condition),
                                "condition": condition
                            })
                            edge_id += 1
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "graph_type": "state_machine",
                "description": "Master Political Analyst Agent - LangGraph Workflow"
            }
        }
    
    def get_execution_graph(self, session_id: str, execution_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get graph with execution state overlaid
        
        Args:
            session_id: Session identifier
            execution_log: Execution log from agent run
        
        Returns:
            Graph structure with execution state
        """
        
        # Get base graph structure
        graph_data = self.get_static_graph_structure()
        
        # Extract execution state
        execution_state = self._extract_execution_state(execution_log)
        
        # Overlay execution state on nodes
        for node in graph_data["nodes"]:
            node_id = node["id"]
            if node_id in execution_state["executed_nodes"]:
                node["execution"] = {
                    "executed": True,
                    "timestamp": execution_state["node_timestamps"].get(node_id),
                    "status": execution_state["node_status"].get(node_id, "completed"),
                    "duration_ms": execution_state["node_durations"].get(node_id),
                    "details": execution_state["node_details"].get(node_id, {})
                }
            else:
                node["execution"] = {
                    "executed": False
                }
        
        # Overlay execution state on edges
        for edge in graph_data["edges"]:
            edge_key = f"{edge['source']}→{edge['target']}"
            if edge_key in execution_state["traversed_edges"]:
                edge["execution"] = {
                    "traversed": True,
                    "count": execution_state["edge_counts"].get(edge_key, 1)
                }
            else:
                edge["execution"] = {
                    "traversed": False
                }
        
        # Add execution metadata
        graph_data["execution_metadata"] = {
            "session_id": session_id,
            "total_steps": len(execution_log),
            "executed_nodes": len(execution_state["executed_nodes"]),
            "start_time": execution_state.get("start_time"),
            "end_time": execution_state.get("end_time"),
            "total_duration_ms": execution_state.get("total_duration_ms"),
            "iterations": execution_state.get("iterations", 1)
        }
        
        return graph_data
    
    def _get_node_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata for each node type"""
        return {
            "__start__": {
                "description": "Entry point for the agent workflow",
                "category": "control",
                "color": "#4ade80",
                "icon": "play"
            },
            "conversation_manager": {
                "description": "Manages conversation context and message history",
                "category": "processing",
                "color": "#60a5fa",
                "icon": "message-circle",
                "responsibilities": [
                    "Initialize conversation history",
                    "Track artifacts from previous turns",
                    "Maintain session state"
                ]
            },
            "strategic_planner": {
                "description": "Analyzes query and selects appropriate tools",
                "category": "decision",
                "color": "#a78bfa",
                "icon": "brain",
                "responsibilities": [
                    "Understand user intent",
                    "Select tools/sub-agents",
                    "Plan execution strategy"
                ],
                "llm_used": True
            },
            "tool_executor": {
                "description": "Executes selected tools and sub-agents",
                "category": "processing",
                "color": "#f59e0b",
                "icon": "tool",
                "responsibilities": [
                    "Execute Tavily search",
                    "Call sub-agents",
                    "Aggregate results"
                ]
            },
            "decision_gate": {
                "description": "Decides whether to continue or synthesize response",
                "category": "decision",
                "color": "#ec4899",
                "icon": "git-branch",
                "responsibilities": [
                    "Evaluate if sufficient information gathered",
                    "Check iteration limits",
                    "Route to next step"
                ],
                "decision_logic": {
                    "max_iterations": 3,
                    "conditions": ["has_sufficient_info", "needs_more_tools"]
                }
            },
            "response_synthesizer": {
                "description": "Compiles results into final user response",
                "category": "processing",
                "color": "#10b981",
                "icon": "file-text",
                "responsibilities": [
                    "Synthesize tool results",
                    "Format response",
                    "Add citations"
                ],
                "llm_used": True
            },
            "artifact_decision": {
                "description": "Decides if visualization should be created",
                "category": "decision",
                "color": "#8b5cf6",
                "icon": "image",
                "responsibilities": [
                    "Detect visualization requests",
                    "Extract structured data",
                    "Determine chart type"
                ],
                "llm_used": True
            },
            "artifact_creator": {
                "description": "Creates visualizations and uploads to S3",
                "category": "processing",
                "color": "#06b6d4",
                "icon": "bar-chart",
                "responsibilities": [
                    "Generate Plotly charts",
                    "Upload to S3",
                    "Save metadata"
                ]
            },
            "__end__": {
                "description": "Workflow completion",
                "category": "control",
                "color": "#ef4444",
                "icon": "stop-circle"
            }
        }
    
    def _get_node_type(self, node_id: str) -> str:
        """Classify node type for visualization"""
        if node_id in ["__start__", "__end__"]:
            return "control"
        elif "decision" in node_id or "gate" in node_id:
            return "decision"
        elif "planner" in node_id or "synthesizer" in node_id:
            return "llm"
        else:
            return "processing"
    
    def _format_node_label(self, node_id: str) -> str:
        """Format node ID into human-readable label"""
        if node_id == "__start__":
            return "START"
        elif node_id == "__end__":
            return "END"
        else:
            # Convert snake_case to Title Case
            return node_id.replace("_", " ").title()
    
    def _format_condition_label(self, condition: str) -> str:
        """Format condition for edge labels"""
        if condition == "tool_executor":
            return "needs more tools"
        elif condition == "response_synthesizer":
            return "sufficient info"
        elif condition == "create_artifact":
            return "create artifact"
        elif condition == "end":
            return "no artifact"
        else:
            return condition.replace("_", " ")
    
    def _extract_execution_state(self, execution_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract execution state from execution log"""
        
        executed_nodes = set()
        node_timestamps = {}
        node_status = {}
        node_durations = {}
        node_details = {}
        traversed_edges = set()
        edge_counts = {}
        
        prev_node = None
        start_time = None
        end_time = None
        node_start_times = {}
        
        for i, log_entry in enumerate(execution_log):
            step = log_entry.get("step", "")
            timestamp = log_entry.get("timestamp", "")
            
            # Track executed nodes
            if step and step not in ["__start__", "__end__"]:
                executed_nodes.add(step)
                
                if not node_timestamps.get(step):
                    node_timestamps[step] = timestamp
                    if timestamp:
                        try:
                            node_start_times[step] = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except:
                            pass
                
                # Track node status
                if log_entry.get("error"):
                    node_status[step] = "error"
                else:
                    node_status[step] = "completed"
                
                # Extract node details
                node_details[step] = {
                    "action": log_entry.get("action", ""),
                    "input": log_entry.get("input", "")[:200] if log_entry.get("input") else "",
                    "output": log_entry.get("output", "")[:200] if log_entry.get("output") else ""
                }
            
            # Track edges (transitions between nodes)
            if prev_node and step and prev_node != step:
                edge_key = f"{prev_node}→{step}"
                traversed_edges.add(edge_key)
                edge_counts[edge_key] = edge_counts.get(edge_key, 0) + 1
                
                # Calculate duration
                if prev_node in node_start_times and step in node_start_times:
                    try:
                        duration = (node_start_times[step] - node_start_times[prev_node]).total_seconds() * 1000
                        node_durations[prev_node] = int(duration)
                    except:
                        pass
            
            prev_node = step
            
            # Track overall timing
            if i == 0 and timestamp:
                start_time = timestamp
            if i == len(execution_log) - 1 and timestamp:
                end_time = timestamp
        
        # Calculate total duration
        total_duration_ms = None
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                total_duration_ms = int((end_dt - start_dt).total_seconds() * 1000)
            except:
                pass
        
        # Detect iteration count (decision_gate executed multiple times)
        iterations = edge_counts.get("decision_gate→tool_executor", 0) + 1
        
        return {
            "executed_nodes": list(executed_nodes),
            "node_timestamps": node_timestamps,
            "node_status": node_status,
            "node_durations": node_durations,
            "node_details": node_details,
            "traversed_edges": list(traversed_edges),
            "edge_counts": edge_counts,
            "start_time": start_time,
            "end_time": end_time,
            "total_duration_ms": total_duration_ms,
            "iterations": iterations
        }
    
    def get_mermaid_diagram(self) -> str:
        """Get Mermaid diagram text (for backward compatibility)"""
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception as e:
            return f"Error generating Mermaid diagram: {str(e)}"


# Singleton instance
graph_service = GraphVisualizationService()


if __name__ == "__main__":
    """Test the graph service"""
    import json
    
    print("Testing Graph Visualization Service\n")
    print("=" * 80)
    
    # Test static graph structure
    print("\n1. Static Graph Structure:")
    print("-" * 80)
    static_graph = graph_service.get_static_graph_structure()
    print(f"Nodes: {static_graph['metadata']['node_count']}")
    print(f"Edges: {static_graph['metadata']['edge_count']}")
    print(f"\nSample Node:")
    print(json.dumps(static_graph['nodes'][1], indent=2))
    print(f"\nSample Edge:")
    print(json.dumps(static_graph['edges'][0], indent=2))
    
    # Test with mock execution log
    print("\n\n2. Execution Graph (with mock execution):")
    print("-" * 80)
    mock_execution_log = [
        {"step": "conversation_manager", "action": "Context initialized", "timestamp": "2024-10-02T10:00:00"},
        {"step": "strategic_planner", "action": "Tools selected", "timestamp": "2024-10-02T10:00:01"},
        {"step": "tool_executor", "action": "Executing tavily_search", "timestamp": "2024-10-02T10:00:02"},
        {"step": "decision_gate", "action": "Decision: PROCEED", "timestamp": "2024-10-02T10:00:05"},
        {"step": "response_synthesizer", "action": "Response generated", "timestamp": "2024-10-02T10:00:08"},
        {"step": "artifact_decision", "action": "No artifact needed", "timestamp": "2024-10-02T10:00:09"}
    ]
    
    execution_graph = graph_service.get_execution_graph("test_session", mock_execution_log)
    print(f"Executed Nodes: {execution_graph['execution_metadata']['executed_nodes']}")
    print(f"Total Duration: {execution_graph['execution_metadata']['total_duration_ms']}ms")
    
    print("\n\n3. Mermaid Diagram:")
    print("-" * 80)
    mermaid = graph_service.get_mermaid_diagram()
    print(mermaid[:500] + "..." if len(mermaid) > 500 else mermaid)
    
    print("\n" + "=" * 80)
    print("✅ Graph Service Test Complete!")

