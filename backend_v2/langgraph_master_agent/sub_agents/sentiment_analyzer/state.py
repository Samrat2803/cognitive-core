"""
State Schema for Sentiment Analyzer Agent
"""

from typing import TypedDict, List, Dict, Any, Optional


class SentimentAnalyzerState(TypedDict):
    """State management for sentiment analyzer"""
    
    # Input
    query: str                              # Original query
    countries: List[str]                    # Countries to analyze
    time_range_days: int                    # Recency filter (default: 7)
    
    # Search Results
    search_results: Dict[str, List[Dict]]   # {country: [search_results]}
    
    # Analysis Results
    sentiment_scores: Dict[str, Dict]       # {country: {positive, negative, neutral, score}}
    bias_analysis: Dict[str, Dict]          # {country: {bias_types, examples}}
    
    # Synthesis
    summary: str                            # Text summary
    key_findings: List[str]                 # Bullet points
    confidence: float                       # 0-1 confidence score
    
    # Artifacts
    artifacts: List[Dict[str, Any]]         # Generated artifacts
    
    # Metadata
    execution_log: List[Dict[str, str]]     # Step-by-step log
    error_log: List[str]                    # Errors encountered

