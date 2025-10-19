"""
State Schema for RSS Realtime Monitor Agent

Manages state for the RSS-based real-time news monitoring system.
"""

from typing import TypedDict, List, Dict, Any, Optional


class RSSRealtimeMonitorState(TypedDict):
    """State management for RSS realtime monitor"""
    
    # ═══════════════════════════════════════════════════════════
    # INPUT (User-provided)
    # ═══════════════════════════════════════════════════════════
    keywords: List[str]              # ["TikTok", "ban", "ByteDance"]
    regions: Optional[List[str]]     # ["United States", "Europe"] or None (all)
    categories: Optional[List[str]]  # ["technology", "business"] or None (all)
    max_topics: int                  # Default: 10
    
    # ═══════════════════════════════════════════════════════════
    # PROCESSING (Intermediate data)
    # ═══════════════════════════════════════════════════════════
    all_cached_articles: List[Dict]  # From MongoDB (24-48h window)
    filtered_articles: List[Dict]    # After keyword + region + category filters
    embeddings: Any                  # Dict[url, np.ndarray] (created on-demand)
    clusters: List[int]              # Cluster assignments from DBSCAN
    topics: List[Dict]               # Topic metadata (before final scoring)
    
    # ═══════════════════════════════════════════════════════════
    # OUTPUT (Final results)
    # ═══════════════════════════════════════════════════════════
    explosive_topics: List[Dict]     # Ranked by velocity (NOT filtered)
    #   Each topic contains:
    #     - rank: 1, 2, 3...
    #     - topic: "TikTok Ban Legislation"
    #     - article_count: 15
    #     - velocity: 2.5 (articles/hour, for SORTING only, NOT filtering)
    #     - avg_age_hours: 4.2
    #     - sources: ["Reuters", "Bloomberg", ...]
    #     - regions: ["United States", "Europe"]
    #     - categories: ["technology", "business"]
    #     - headlines: [...] (top 5)
    #     - entities: {people: [...], companies: [...], locations: [...]}
    #     - explosiveness_score: 87 (0-100)
    #     - ready_for_tavily: true (score > 70 suggests deep dive)
    
    # ═══════════════════════════════════════════════════════════
    # METADATA
    # ═══════════════════════════════════════════════════════════
    total_articles_cached: int       # Total in MongoDB (before filtering)
    articles_analyzed: int           # After keyword filtering
    topics_found: int                # Number of clusters
    processing_time_seconds: float   # Performance tracking
    execution_log: List[str]         # Step-by-step log
    error_log: List[str]             # Errors encountered

