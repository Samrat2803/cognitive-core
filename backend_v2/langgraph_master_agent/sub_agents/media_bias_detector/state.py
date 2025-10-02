"""
State Schema for Media Bias Detector Agent
"""

from typing import TypedDict, List, Dict, Any, Optional


class MediaBiasDetectorState(TypedDict):
    """State management for media bias detector"""
    
    # Input
    query: str                                  # Topic to analyze
    sources: Optional[List[str]]                # Specific sources (optional)
    time_range_days: int                        # Recency filter (default: 7)
    
    # Search Results
    articles_by_source: Dict[str, List[Dict]]   # {source: [articles]}
    total_articles_found: int                   # Total articles retrieved
    
    # Analysis Results
    bias_classification: Dict[str, Dict]        # {source: {spectrum, bias_score, confidence, evidence, techniques}}
    loaded_language: Dict[str, List[Dict]]      # {source: [{phrase, type, context, why_biased}]}
    framing_analysis: Dict[str, Dict]           # {source: {primary_frame, techniques, examples}}
    
    # Comparison Analysis
    consensus_points: List[str]                 # What all sources agree on
    divergence_points: List[Dict]               # Where sources disagree {topic, positions}
    omission_analysis: Dict[str, List[str]]     # What each source omits
    overall_bias_range: Dict[str, float]        # {min, max, avg} bias scores
    
    # Synthesis
    summary: str                                # Executive summary
    key_findings: List[str]                     # Main insights
    confidence: float                           # Overall confidence (0-1)
    recommendations: List[str]                  # How to consume this news
    
    # Artifacts
    artifacts: List[Dict[str, Any]]             # Generated visualizations
    
    # Metadata
    execution_log: List[Dict[str, str]]         # Step-by-step log
    error_log: List[str]                        # Errors encountered

