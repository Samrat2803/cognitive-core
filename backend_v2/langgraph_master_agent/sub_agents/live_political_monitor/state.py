"""
State Schema for Live Political Monitor Agent
"""

from typing import TypedDict, List, Dict, Any, Optional


class LiveMonitorState(TypedDict):
    """State management for live political monitor"""
    
    # Input
    keywords: List[str]                     # User's focus keywords (e.g., ["Bihar", "corruption"])
    cache_hours: int                        # Cache duration (default: 3)
    max_results: int                        # Max topics to return (default: 10)
    
    # Generated Queries
    generated_queries: List[str]            # Tavily queries generated from keywords
    
    # Search Results
    raw_articles: List[Dict]                # All articles from Tavily
    fetched_images: List[str]               # Image URLs from Tavily (for topics)
    relevant_articles: List[Dict]           # After keyword filtering
    irrelevant_articles: List[Dict]         # Filtered out
    
    # Topic Extraction
    extracted_topics: List[Dict]            # Topics extracted by LLM
    
    # Scoring
    scored_topics: List[Dict]               # Topics with explosiveness scores
    
    # Final Output
    explosive_topics: List[Dict]            # Top N ranked topics
    
    # Metadata
    total_articles_analyzed: int            # Count
    processing_time_seconds: float          # Performance tracking
    execution_log: List[Dict[str, str]]     # Step-by-step log
    error_log: List[str]                    # Errors encountered

