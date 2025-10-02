"""
Event Retriever Node

Retrieves explosive topics from Live Political Monitor output.
For standalone testing, loads from Live Monitor artifacts.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any
from state import SitRepState


def retrieve_events(state: SitRepState) -> Dict[str, Any]:
    """
    Retrieve events from Live Political Monitor
    
    For standalone testing: Loads from Live Monitor's test artifacts
    For production: Would query MongoDB/cache
    
    Args:
        state: Current state with period, region_focus, topic_focus
        
    Returns:
        Updated state with raw_events populated
    """
    
    print("\n" + "="*80)
    print("📥 NODE: Event Retriever")
    print("="*80)
    
    period = state.get("period", "daily")
    region_focus = state.get("region_focus")
    topic_focus = state.get("topic_focus")
    
    print(f"Period: {period}")
    print(f"Region Focus: {region_focus or 'All regions'}")
    print(f"Topic Focus: {topic_focus or 'All topics'}")
    
    # For standalone testing: Load from Live Monitor artifacts
    live_monitor_artifacts_dir = os.path.join(
        os.path.dirname(__file__),
        "../../live_political_monitor/artifacts"
    )
    
    events = []
    
    # Find most recent Live Monitor test output
    if os.path.exists(live_monitor_artifacts_dir):
        print(f"\n📂 Loading from Live Monitor artifacts: {live_monitor_artifacts_dir}")
        
        # Get all test_output JSON files
        json_files = [
            f for f in os.listdir(live_monitor_artifacts_dir)
            if f.startswith("test_output_") and f.endswith(".json")
        ]
        
        if json_files:
            # Use most recent file
            latest_file = sorted(json_files)[-1]
            file_path = os.path.join(live_monitor_artifacts_dir, latest_file)
            
            print(f"   Using: {latest_file}")
            
            try:
                with open(file_path, 'r') as f:
                    live_monitor_data = json.load(f)
                
                # Extract explosive topics as events
                explosive_topics = live_monitor_data.get("explosive_topics", [])
                
                print(f"   Found {len(explosive_topics)} explosive topics")
                
                # Convert Live Monitor topics to SitRep events
                for topic in explosive_topics:
                    event = {
                        "title": topic.get("topic", "Unknown Topic"),
                        "explosiveness_score": topic.get("explosiveness_score", 0),
                        "classification": topic.get("classification", "NOTABLE"),
                        "priority": topic.get("priority", 99),
                        "frequency": topic.get("frequency", 0),
                        "llm_rating": topic.get("llm_rating", 0),
                        "reasoning": topic.get("reasoning", ""),
                        "entities": topic.get("entities", {}),
                        "regions": topic.get("entities", {}).get("countries", ["Global"]),
                        "summary": topic.get("reasoning", "")[:500],  # First 500 chars
                        "source": "Live Political Monitor",
                        "timestamp": live_monitor_data.get("timestamp", datetime.now().isoformat())
                    }
                    
                    # Apply region filter if specified
                    if region_focus:
                        if region_focus in event["regions"] or "Global" in event["regions"]:
                            events.append(event)
                    else:
                        events.append(event)
                
                print(f"   ✅ Loaded {len(events)} events after filtering")
                
            except Exception as e:
                print(f"   ❌ Error loading Live Monitor data: {e}")
                state["error_log"].append(f"Failed to load Live Monitor data: {e}")
        else:
            print(f"   ⚠️  No Live Monitor test outputs found")
            state["error_log"].append("No Live Monitor test outputs found")
    else:
        print(f"   ⚠️  Live Monitor artifacts directory not found: {live_monitor_artifacts_dir}")
        state["error_log"].append(f"Live Monitor artifacts not found at {live_monitor_artifacts_dir}")
    
    # Calculate date range
    if period == "daily":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        date_range = f"{start_date.strftime('%B %d')}-{end_date.strftime('%d, %Y')}"
    elif period == "weekly":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        date_range = f"{start_date.strftime('%B %d')}-{end_date.strftime('%d, %Y')}"
    else:  # custom
        start_date_str = state.get("start_date", "")
        end_date_str = state.get("end_date", "")
        date_range = f"{start_date_str} to {end_date_str}"
    
    # Extract unique regions
    regions_covered = list(set([
        region
        for event in events
        for region in event.get("regions", ["Global"])
    ]))
    
    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")
    print(f"   Regions covered: {len(regions_covered)}")
    print(f"   Date range: {date_range}")
    
    # Update state
    state["raw_events"] = events
    state["event_count"] = len(events)
    state["date_range"] = date_range
    state["regions_covered"] = regions_covered
    state["source_count"] = len(events)  # Each event is from one source
    state["execution_log"].append(f"✅ Retrieved {len(events)} events from Live Monitor")
    
    return state

