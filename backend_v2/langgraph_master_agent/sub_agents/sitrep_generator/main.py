"""
SitRep Generator - Standalone Test Runner

Usage:
    python main.py                           # Daily report, all regions
    python main.py --period weekly           # Weekly report
    python main.py --region "Middle East"    # Focus on specific region
"""

import asyncio
import sys
import json
from datetime import datetime
from graph import create_sitrep_graph
from state import SitRepState
from config import DEFAULT_PERIOD


async def run_sitrep(period="daily", region=None, topic=None):
    """
    Run the SitRep Generator agent
    
    Args:
        period: "daily", "weekly", or "custom"
        region: Optional region focus (e.g., "Middle East", "Europe")
        topic: Optional topic focus (e.g., "elections", "conflicts")
    """
    
    print("=" * 80)
    print("📋 SITUATION REPORT GENERATOR")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Period: {period}")
    print(f"Region Focus: {region or 'All regions'}")
    print(f"Topic Focus: {topic or 'All topics'}")
    print("=" * 80)
    
    start_time = datetime.now()
    
    # Create graph
    print("\n🔧 Initializing SitRep Generator graph...")
    graph = create_sitrep_graph()
    print("✅ Graph initialized")
    
    # Initialize state
    initial_state: SitRepState = {
        # Input parameters
        "period": period,
        "region_focus": region,
        "topic_focus": topic,
        "start_date": None,
        "end_date": None,
        
        # Data containers (will be populated by nodes)
        "raw_events": [],
        "event_count": 0,
        "urgent_events": [],
        "high_priority_events": [],
        "notable_events": [],
        "regional_breakdown": {},
        "topic_clusters": {},
        
        # Analysis outputs
        "executive_summary": "",
        "trending_topics": [],
        "watch_list": [],
        
        # Metadata
        "date_range": "",
        "regions_covered": [],
        "source_count": 0,
        
        # Artifacts
        "artifacts": [],
        
        # Logs
        "execution_log": [],
        "error_log": []
    }
    
    print("\n🚀 Running SitRep Generator workflow...\n")
    
    # Run agent
    try:
        result = await graph.ainvoke(initial_state)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("✅ SITREP GENERATION COMPLETE")
        print("=" * 80)
        print(f"Duration: {duration:.1f}s")
        print(f"Events Analyzed: {result.get('event_count', 0)}")
        print(f"Regions Covered: {len(result.get('regions_covered', []))}")
        
        # Display execution log
        print("\n📝 Execution Log:")
        for log_entry in result.get("execution_log", []):
            print(f"   {log_entry}")
        
        # Display errors if any
        if result.get("error_log"):
            print("\n⚠️  Errors Encountered:")
            for error in result.get("error_log", []):
                print(f"   ❌ {error}")
        
        # Display executive summary
        print("\n" + "=" * 80)
        print("EXECUTIVE SUMMARY")
        print("=" * 80)
        print(result.get("executive_summary", "No summary generated"))
        
        # Display priority breakdown
        print("\n" + "=" * 80)
        print("PRIORITY BREAKDOWN")
        print("=" * 80)
        print(f"🔴 URGENT: {len(result.get('urgent_events', []))} events")
        print(f"🟠 HIGH PRIORITY: {len(result.get('high_priority_events', []))} events")
        print(f"🟡 NOTABLE: {len(result.get('notable_events', []))} events")
        
        # Display trending topics
        if result.get("trending_topics"):
            print("\n" + "=" * 80)
            print("TRENDING TOPICS")
            print("=" * 80)
            for i, topic in enumerate(result.get("trending_topics", [])[:10], 1):
                print(f"   {i}. {topic.capitalize()}")
        
        # Display watch list
        if result.get("watch_list"):
            print("\n" + "=" * 80)
            print("👁️  WATCH LIST - Next 24-48 Hours")
            print("=" * 80)
            for i, item in enumerate(result.get("watch_list", []), 1):
                print(f"   {i}. {item}")
        
        # Display artifacts generated
        print("\n" + "=" * 80)
        print("📄 ARTIFACTS GENERATED")
        print("=" * 80)
        for artifact in result.get("artifacts", []):
            print(f"   {artifact['type'].upper()}: {artifact['path']} ({artifact['size_kb']:.1f} KB)")
        
        print("\n" + "=" * 80)
        print(f"✅ SitRep saved to: artifacts/")
        print("=" * 80)
        
        # Save full result to JSON for inspection
        output_file = f"artifacts/sitrep_test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            # Convert to serializable format
            output_data = {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "period": result.get("period"),
                "region_focus": result.get("region_focus"),
                "date_range": result.get("date_range"),
                "event_count": result.get("event_count"),
                "executive_summary": result.get("executive_summary"),
                "urgent_events_count": len(result.get("urgent_events", [])),
                "high_priority_events_count": len(result.get("high_priority_events", [])),
                "notable_events_count": len(result.get("notable_events", [])),
                "trending_topics": result.get("trending_topics", []),
                "watch_list": result.get("watch_list", []),
                "regions_covered": result.get("regions_covered", []),
                "artifacts": result.get("artifacts", []),
                "execution_log": result.get("execution_log", []),
                "error_log": result.get("error_log", [])
            }
            json.dump(output_data, f, indent=2)
        
        print(f"\n📊 Test output saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Parse simple arguments
    period = DEFAULT_PERIOD
    region = None
    topic = None
    
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:]):
            if arg == "--period" and i + 2 < len(sys.argv):
                period = sys.argv[i + 2]
            elif arg == "--region" and i + 2 < len(sys.argv):
                region = sys.argv[i + 2]
            elif arg == "--topic" and i + 2 < len(sys.argv):
                topic = sys.argv[i + 2]
    
    # Run the agent
    asyncio.run(run_sitrep(period=period, region=region, topic=topic))

