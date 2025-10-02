"""
Priority Ranker Node

Ranks and categorizes events by priority level based on explosiveness score.
"""

from typing import Dict, Any
from state import SitRepState
from config import PRIORITY_LEVELS, MAX_URGENT_EVENTS, MAX_HIGH_PRIORITY_EVENTS, MAX_NOTABLE_EVENTS


def rank_events_by_priority(state: SitRepState) -> Dict[str, Any]:
    """
    Rank events by priority and categorize them
    
    Priority levels based on explosiveness score:
    - URGENT (🔴): 80-100
    - HIGH PRIORITY (🟠): 60-79
    - NOTABLE (🟡): 40-59
    - ROUTINE (⚪): 0-39
    
    Args:
        state: Current state with raw_events
        
    Returns:
        Updated state with events categorized by priority
    """
    
    print("\n" + "="*80)
    print("📊 NODE: Priority Ranker")
    print("="*80)
    
    raw_events = state.get("raw_events", [])
    
    if not raw_events:
        print("⚠️  No events to rank")
        state["urgent_events"] = []
        state["high_priority_events"] = []
        state["notable_events"] = []
        state["execution_log"].append("⚠️  No events to rank")
        return state
    
    print(f"Ranking {len(raw_events)} events...")
    
    # Initialize priority lists
    urgent = []
    high_priority = []
    notable = []
    routine = []
    
    # Categorize events by explosiveness score
    for event in raw_events:
        score = event.get("explosiveness_score", 0)
        
        if score >= PRIORITY_LEVELS["urgent"]["min_score"]:
            urgent.append(event)
        elif score >= PRIORITY_LEVELS["high"]["min_score"]:
            high_priority.append(event)
        elif score >= PRIORITY_LEVELS["notable"]["min_score"]:
            notable.append(event)
        else:
            routine.append(event)
    
    # Sort each category by score (descending)
    urgent.sort(key=lambda x: x.get("explosiveness_score", 0), reverse=True)
    high_priority.sort(key=lambda x: x.get("explosiveness_score", 0), reverse=True)
    notable.sort(key=lambda x: x.get("explosiveness_score", 0), reverse=True)
    
    # Apply limits to prevent overly long reports
    urgent = urgent[:MAX_URGENT_EVENTS]
    high_priority = high_priority[:MAX_HIGH_PRIORITY_EVENTS]
    notable = notable[:MAX_NOTABLE_EVENTS]
    
    print(f"\n📈 Priority Distribution:")
    print(f"   🔴 URGENT: {len(urgent)} events (score >= 80)")
    if urgent:
        for event in urgent[:3]:  # Show top 3
            print(f"      • {event.get('title', 'Unknown')} (score: {event.get('explosiveness_score', 0)})")
    
    print(f"   🟠 HIGH PRIORITY: {len(high_priority)} events (score 60-79)")
    if high_priority:
        for event in high_priority[:2]:  # Show top 2
            print(f"      • {event.get('title', 'Unknown')} (score: {event.get('explosiveness_score', 0)})")
    
    print(f"   🟡 NOTABLE: {len(notable)} events (score 40-59)")
    if notable:
        for event in notable[:2]:  # Show top 2
            print(f"      • {event.get('title', 'Unknown')} (score: {event.get('explosiveness_score', 0)})")
    
    print(f"   ⚪ ROUTINE: {len(routine)} events (score < 40) [not included in report]")
    
    # Update state
    state["urgent_events"] = urgent
    state["high_priority_events"] = high_priority
    state["notable_events"] = notable
    state["execution_log"].append(
        f"✅ Ranked events: {len(urgent)} urgent, {len(high_priority)} high priority, {len(notable)} notable"
    )
    
    return state

