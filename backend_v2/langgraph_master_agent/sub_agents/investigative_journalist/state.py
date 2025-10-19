"""
State Schema for Investigative Journalist Agent

Designed for deep, multi-iteration investigations with evidence tracking
"""

from typing import TypedDict, List, Dict, Any, Optional


class InvestigativeJournalistState(TypedDict):
    """State for investigative journalist agent"""
    
    # ============ INPUT & CONTROL ============
    initial_query: str                      # Original investigation query
    investigation_id: Optional[str]         # UUID for evidence repository
    session_id: Optional[str]               # Master agent session ID
    iteration: int                          # Current iteration number
    max_iterations: int                     # Maximum iterations allowed
    investigation_complete: bool            # Completion flag
    
    # ============ KNOWLEDGE BASE ============
    entities: Dict[str, Any]                # People, orgs, locations with metadata
    facts: List[str]                        # Verified facts with attribution
    hypotheses: List[Dict[str, Any]]        # Competing explanations being tested
    evidence: List[Dict[str, Any]]          # Evidence supporting/refuting hypotheses
    connections: List[Dict[str, Any]]       # Relationships between entities
    anomalies: List[str]                    # Unusual patterns/absences
    
    # ============ CACHE & EFFICIENCY ============
    seen_urls: List[str]                    # Already processed URLs
    extracted_cache: Dict[str, str]         # URL -> content cache (not used currently)
    previous_queries: List[str]             # All search queries (prevents repetition)
    
    # ============ WORKING VARIABLES ============
    next_action: str                        # "search" | "analyze_only"
    search_query: Optional[str]             # Current search query
    search_results: List[Dict[str, Any]]    # Results from current search
    extracted_content: List[Dict[str, Any]] # Extracted articles from current cycle
    
    # ============ OUTPUTS ============
    final_report: Optional[str]             # Final article (markdown format)
    artifacts: List[Dict[str, Any]]         # Generated artifacts (PDFs, etc.)
    
    # ============ METADATA ============
    execution_log: List[Dict[str, str]]     # Step-by-step execution log
    error_log: List[str]                    # Errors encountered
    cost_tracking: Dict[str, Any]           # Cost breakdown

