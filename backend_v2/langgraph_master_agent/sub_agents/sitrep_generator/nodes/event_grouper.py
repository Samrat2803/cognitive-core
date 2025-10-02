"""
Event Grouper Node

Groups events by region and identifies topic clusters.
"""

from typing import Dict, Any, List
from collections import Counter
from state import SitRepState
from config import MAX_TRENDING_TOPICS


def group_events(state: SitRepState) -> Dict[str, Any]:
    """
    Group events by region and identify trending topics
    
    Creates:
    - Regional breakdown (events grouped by region)
    - Topic clusters (events grouped by topic)
    - Trending topics list
    
    Args:
        state: Current state with categorized events
        
    Returns:
        Updated state with regional_breakdown, topic_clusters, trending_topics
    """
    
    print("\n" + "="*80)
    print("🗂️  NODE: Event Grouper")
    print("="*80)
    
    # Combine all events for grouping
    all_events = (
        state.get("urgent_events", []) +
        state.get("high_priority_events", []) +
        state.get("notable_events", [])
    )
    
    if not all_events:
        print("⚠️  No events to group")
        state["regional_breakdown"] = {}
        state["topic_clusters"] = {}
        state["trending_topics"] = []
        state["execution_log"].append("⚠️  No events to group")
        return state
    
    print(f"Grouping {len(all_events)} events...")
    
    # ============================================================================
    # GROUP BY REGION
    # ============================================================================
    
    regional_breakdown = {}
    
    for event in all_events:
        regions = event.get("regions", ["Global"])
        
        for region in regions:
            if region not in regional_breakdown:
                regional_breakdown[region] = []
            regional_breakdown[region].append(event)
    
    # Sort events within each region by score
    for region in regional_breakdown:
        regional_breakdown[region].sort(
            key=lambda x: x.get("explosiveness_score", 0),
            reverse=True
        )
    
    print(f"\n🌍 Regional Breakdown:")
    for region, events in sorted(regional_breakdown.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"   {region}: {len(events)} events")
        if events:
            top_event = events[0]
            print(f"      Top: {top_event.get('title', 'Unknown')} (score: {top_event.get('explosiveness_score', 0)})")
    
    # ============================================================================
    # IDENTIFY TRENDING TOPICS
    # ============================================================================
    
    # Extract keywords/topics from event titles
    topic_counter = Counter()
    
    for event in all_events:
        title = event.get("title", "")
        
        # Split title into words and count
        words = title.lower().split()
        
        # Filter out common words and short words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "by", "from", "with"}
        meaningful_words = [
            word.strip(".,!?;:")
            for word in words
            if len(word) > 4 and word.lower() not in stop_words
        ]
        
        topic_counter.update(meaningful_words)
    
    # Get top trending topics
    trending_topics = [topic for topic, count in topic_counter.most_common(MAX_TRENDING_TOPICS)]
    
    print(f"\n🔥 Trending Topics (Top {len(trending_topics)}):")
    for i, topic in enumerate(trending_topics, 1):
        count = topic_counter[topic]
        print(f"   {i}. {topic.capitalize()} ({count} mentions)")
    
    # ============================================================================
    # TOPIC CLUSTERS (simplified - group by keywords in title)
    # ============================================================================
    
    topic_clusters = {}
    
    for topic in trending_topics[:5]:  # Use top 5 topics
        topic_clusters[topic] = [
            event for event in all_events
            if topic.lower() in event.get("title", "").lower()
        ]
    
    # Update state
    state["regional_breakdown"] = regional_breakdown
    state["topic_clusters"] = topic_clusters
    state["trending_topics"] = trending_topics
    state["execution_log"].append(
        f"✅ Grouped events: {len(regional_breakdown)} regions, {len(trending_topics)} trending topics"
    )
    
    return state

