"""
Explosiveness Scorer Node

Scores topics by explosiveness metrics (velocity, recency, diversity).
IMPORTANT: This does NOT filter - it only scores and sorts!
"""

import os
import sys
from typing import Dict
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state import RSSRealtimeMonitorState
from config import (
    VELOCITY_WEIGHT, RECENCY_WEIGHT, DIVERSITY_WEIGHT,
    GEOGRAPHIC_WEIGHT, RELEVANCE_WEIGHT, TAVILY_READINESS_THRESHOLD,
    MAX_HEADLINES_PER_TOPIC
)


def calculate_relevance_score(topic: Dict, keywords: list) -> float:
    """Calculate keyword relevance score for topic"""
    articles = topic["articles"]
    
    if not articles:
        return 0.0
    
    # Average relevance score from filtering
    relevance_scores = [a.get("relevance_score", 0.5) for a in articles]
    avg_relevance = np.mean(relevance_scores)
    
    # Normalize to 0-RELEVANCE_WEIGHT
    return min(RELEVANCE_WEIGHT, avg_relevance * RELEVANCE_WEIGHT * 2)


def format_for_cognitive_core_ui(topic: Dict) -> Dict:
    """
    Transform RSS Monitor output to Cognitive Core UI format.
    Ensures backward compatibility with existing Tavily-based Live Political Monitor.
    
    This creates a "superset" format:
    - All REQUIRED fields match the existing Tavily monitor
    - Additional OPTIONAL fields enhance the UI (velocity, sources, etc.)
    - Frontend gracefully ignores optional fields if using old Tavily monitor
    
    Args:
        topic: RSS Monitor topic dict with cluster_id, label, scores, etc.
    
    Returns:
        UI-compatible topic dict with required + optional fields
    """
    
    # ═══════════════════════════════════════════════════════════
    # REQUIRED FIELDS (Tavily-compatible)
    # ═══════════════════════════════════════════════════════════
    
    # 1. Extract topic name from label (remove emoji/status prefix)
    topic_name = topic['label']
    if '|' in topic_name:
        # "📰 DEVELOPING | AI | Policy" → "AI | Policy"
        parts = topic_name.split('|')
        topic_name = ' | '.join(parts[1:]).strip()
    
    # 2. Extract classification from label
    label_upper = topic['label'].upper()
    if 'CRITICAL' in label_upper or 'BREAKING' in label_upper:
        classification = "🔴 CRITICAL"
        priority = 1
    elif 'EXPLOSIVE' in label_upper:
        classification = "🟠 EXPLOSIVE"
        priority = 2
    elif 'DEVELOPING' in label_upper or 'TRENDING' in label_upper:
        classification = "🟡 TRENDING"
        priority = 3
    else:
        classification = "🟢 EMERGING"
        priority = 4
    
    # 3. Generate reasoning text (human-readable explanation)
    breakdown = topic['score_breakdown']
    reasoning = (
        f"Scored {topic['explosiveness_score']}/100 based on: "
        f"velocity ({breakdown['velocity']:.0f}/20), "
        f"recency ({breakdown['recency']:.0f}/20), "
        f"diversity ({breakdown['diversity']:.0f}/20), "
        f"geographic spread ({breakdown['geographic']:.0f}/20), "
        f"and keyword relevance ({breakdown['relevance']:.0f}/10). "
        f"Currently tracking {topic['velocity']} articles/hour "
        f"from {len(topic['sources'])} sources."
    )
    
    # 4. Remap entities to match Tavily format
    entities_standardized = topic.get('entities', {})
    entities_ui = {
        "people": entities_standardized.get('people', []),
        "countries": entities_standardized.get('locations', []),  # locations → countries
        "organizations": (
            entities_standardized.get('organizations', []) + 
            entities_standardized.get('companies', [])
        )
    }
    
    # 5. Extract image_url from first headline (if available)
    image_url = None
    headlines = topic.get('headlines', [])
    # RSS feeds don't typically have images, but could be enhanced later
    # For now, leave None (frontend will handle gracefully)
    
    # ═══════════════════════════════════════════════════════════
    # BUILD OUTPUT (Required + Optional fields)
    # ═══════════════════════════════════════════════════════════
    
    return {
        # ───────────────────────────────────────────────────────
        # REQUIRED FIELDS (matching Tavily Live Political Monitor)
        # ───────────────────────────────────────────────────────
        "rank": topic['rank'],
        "topic": topic_name,
        "explosiveness_score": topic['explosiveness_score'],
        "classification": classification,
        "priority": priority,
        "frequency": topic['article_count'],
        "entities": entities_ui,
        "reasoning": reasoning,
        "image_url": image_url,  # Optional but expected field
        
        # ───────────────────────────────────────────────────────
        # OPTIONAL RSS-SPECIFIC FIELDS (bonus features for UI)
        # ───────────────────────────────────────────────────────
        "velocity": topic['velocity'],
        "average_age_hours": topic['avg_age_hours'],
        "score_breakdown": topic['score_breakdown'],
        "signal_breakdown": topic['score_breakdown'],  # Alias for compatibility
        "sources": topic['sources'],
        "source_diversity": topic['source_diversity'],
        "regions": topic['regions'],
        "geo_diversity": topic['geo_diversity'],
        "categories": topic['categories'],
        "ready_for_tavily": topic['ready_for_tavily'],
        "headlines": topic['headlines'][:3],  # Send top 3 only
        
        # LLM rating equivalent (for comparison with Tavily)
        "llm_rating": min(10, int(topic['explosiveness_score'] / 10))
    }


def score_explosiveness(state: RSSRealtimeMonitorState) -> RSSRealtimeMonitorState:
    """
    Score topics by explosiveness
    
    IMPORTANT: This does NOT filter! It scores and sorts ALL topics.
    
    Scoring factors (0-100):
    - Velocity (40): Articles per hour in last 6h
    - Recency (20): Average age of articles
    - Diversity (20): Number of unique sources
    - Geographic (10): Regional coverage
    - Relevance (10): Keyword match quality
    """
    
    print("\n[5] Scoring topic explosiveness...")
    
    try:
        topics = state["topics"]
        keywords = state["keywords"]
        
        if not topics:
            print("  ⚠️  No topics to score")
            state["explosive_topics"] = []
            return state
        
        scored_topics = []
        
        for topic in topics:
            articles = topic["articles"]
            
            if not articles:
                continue
            
            # ═══════════════════════════════════════════════════════════
            # 1. VELOCITY (40 points) - Articles per hour in last 6h
            # ═══════════════════════════════════════════════════════════
            recent_articles = [a for a in articles if a.get('age_hours', 48) < 6]
            velocity = len(recent_articles) / 6  # articles per hour
            
            # Scoring: 2/hr = max (40 pts), 1/hr = 20 pts, 0.5/hr = 10 pts
            velocity_score = min(VELOCITY_WEIGHT, velocity * 20)
            
            # ═══════════════════════════════════════════════════════════
            # 2. RECENCY (20 points) - Average age of articles
            # ═══════════════════════════════════════════════════════════
            ages = [a.get('age_hours', 48) for a in articles]
            avg_age = np.mean(ages)
            min_age = min(ages)
            
            # Scoring: <3h = 20 pts, <6h = 15 pts, <12h = 10 pts, <24h = 5 pts
            recency_score = RECENCY_WEIGHT * (1 - min(1, avg_age / 24))
            
            # ═══════════════════════════════════════════════════════════
            # 3. DIVERSITY (20 points) - Unique sources
            # ═══════════════════════════════════════════════════════════
            unique_sources = len(set(a.get('source', '') for a in articles))
            
            # Scoring: 10+ sources = 20 pts, 5 = 10 pts, 2 = 4 pts
            diversity_score = min(DIVERSITY_WEIGHT, unique_sources * 2)
            
            # ═══════════════════════════════════════════════════════════
            # 4. GEOGRAPHIC (10 points) - Regional spread
            # ═══════════════════════════════════════════════════════════
            unique_regions = len(set(a.get('source_region', '') for a in articles))
            
            # Scoring: 5+ regions = 10 pts, 3 = 6 pts, 1 = 2 pts
            geographic_score = min(GEOGRAPHIC_WEIGHT, unique_regions * 2)
            
            # ═══════════════════════════════════════════════════════════
            # 5. RELEVANCE (10 points) - Keyword match quality
            # ═══════════════════════════════════════════════════════════
            relevance_score = calculate_relevance_score(topic, keywords)
            
            # ═══════════════════════════════════════════════════════════
            # TOTAL SCORE (0-100)
            # ═══════════════════════════════════════════════════════════
            explosiveness_score = int(
                velocity_score + recency_score + diversity_score +
                geographic_score + relevance_score
            )
            
            # ═══════════════════════════════════════════════════════════
            # Metadata
            # ═══════════════════════════════════════════════════════════
            sources_list = list(set(a.get('source', '') for a in articles))
            regions_list = list(set(a.get('source_region', '') for a in articles))
            categories_list = list(set(a.get('source_category', '') for a in articles))
            
            # Get top headlines (sorted by recency)
            articles_sorted = sorted(articles, key=lambda x: x.get('age_hours', 48))
            headlines = [
                {
                    "title": a.get("title", ""),
                    "source": a.get("source", ""),
                    "age_hours": a.get("age_hours", 0),
                    "url": a.get("url", "")
                }
                for a in articles_sorted[:MAX_HEADLINES_PER_TOPIC]
            ]
            
            # ═══════════════════════════════════════════════════════════
            # Build topic result
            # ═══════════════════════════════════════════════════════════
            topic_result = {
                "cluster_id": topic["cluster_id"],
                "label": topic.get("label", "Unknown Topic"),
                "article_count": len(articles),
                
                # Metrics
                "velocity": round(velocity, 2),
                "avg_age_hours": round(avg_age, 1),
                "min_age_hours": round(min_age, 1),
                
                # Scores
                "explosiveness_score": explosiveness_score,
                "score_breakdown": {
                    "velocity": round(velocity_score, 1),
                    "recency": round(recency_score, 1),
                    "diversity": round(diversity_score, 1),
                    "geographic": round(geographic_score, 1),
                    "relevance": round(relevance_score, 1)
                },
                
                # Metadata
                "sources": sources_list,
                "source_diversity": unique_sources,
                "regions": regions_list,
                "geo_diversity": unique_regions,
                "categories": categories_list,
                
                # Content
                "headlines": headlines,
                
                # Tavily readiness flag (NOT a filter!)
                "ready_for_tavily": explosiveness_score > TAVILY_READINESS_THRESHOLD
            }
            
            scored_topics.append(topic_result)
        
        # ═══════════════════════════════════════════════════════════
        # SORT by explosiveness (NOT filter!)
        # ═══════════════════════════════════════════════════════════
        scored_topics.sort(key=lambda x: x['explosiveness_score'], reverse=True)
        
        # Add rank
        for rank, topic in enumerate(scored_topics, 1):
            topic['rank'] = rank
        
        # Return top N for final output (this is the ONLY place we limit)
        max_topics = state.get("max_topics", 10)
        top_topics = scored_topics[:max_topics]
        
        # ═══════════════════════════════════════════════════════════
        # TRANSFORM for Cognitive Core UI compatibility
        # ═══════════════════════════════════════════════════════════
        explosive_topics_ui_format = [
            format_for_cognitive_core_ui(topic) for topic in top_topics
        ]
        
        state["explosive_topics"] = explosive_topics_ui_format
        
        print(f"  ✓ Scored {len(scored_topics)} topics, returning top {max_topics}")
        print(f"    Top score: {scored_topics[0]['explosiveness_score']}/100")
        print(f"    Transformed to Cognitive Core UI format (backward compatible)")
        if scored_topics:
            ready_count = sum(1 for t in scored_topics if t['ready_for_tavily'])
            print(f"    Ready for Tavily: {ready_count}/{len(scored_topics)}")
        
        state["execution_log"].append(
            f"Scored {len(scored_topics)} topics, top score: {scored_topics[0]['explosiveness_score']}/100"
        )
    
    except Exception as e:
        error_msg = f"Error scoring explosiveness: {str(e)}"
        print(f"  ✗ {error_msg}")
        state["error_log"].append(error_msg)
        state["explosive_topics"] = []
    
    return state

