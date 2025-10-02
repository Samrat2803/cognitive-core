"""
SitRep Generator State Schema

This defines the state structure for the Situation Report Generator agent.
"""

from typing import TypedDict, List, Dict, Any, Optional


class SitRepState(TypedDict):
    """
    State for SitRep Generator Agent
    
    This agent generates daily/weekly situation reports from Live Monitor events.
    """
    
    # Input parameters
    period: str  # "daily", "weekly", "custom"
    region_focus: Optional[str]  # Optional region filter (e.g., "Middle East", "Europe", None for all)
    topic_focus: Optional[str]  # Optional topic filter (e.g., "elections", "conflicts", None for all)
    start_date: Optional[str]  # For custom period (YYYY-MM-DD)
    end_date: Optional[str]  # For custom period (YYYY-MM-DD)
    
    # Retrieved events from Live Monitor
    raw_events: List[Dict[str, Any]]  # Events from Live Monitor storage
    event_count: int  # Total events retrieved
    
    # Processed events (priority ranking)
    urgent_events: List[Dict[str, Any]]  # Score >= 80 (CRITICAL)
    high_priority_events: List[Dict[str, Any]]  # Score 60-79 (EXPLOSIVE/IMPORTANT)
    notable_events: List[Dict[str, Any]]  # Score 40-59 (NOTABLE)
    
    # Event grouping
    regional_breakdown: Dict[str, List[Dict[str, Any]]]  # Events grouped by region
    topic_clusters: Dict[str, List[Dict[str, Any]]]  # Events grouped by topic
    
    # Analysis outputs
    executive_summary: str  # 3-4 sentence summary
    trending_topics: List[str]  # Most frequently mentioned topics
    watch_list: List[str]  # Items to monitor in next 24-48 hours
    
    # Report metadata
    date_range: str  # Human-readable date range (e.g., "October 1-2, 2025")
    regions_covered: List[str]  # List of regions in report
    source_count: int  # Number of sources analyzed
    
    # Generated artifacts
    artifacts: List[Dict[str, str]]  # List of generated files (HTML, PDF, TXT, JSON)
    
    # Execution tracking
    execution_log: List[str]  # Step-by-step execution log
    error_log: List[str]  # Any errors encountered

