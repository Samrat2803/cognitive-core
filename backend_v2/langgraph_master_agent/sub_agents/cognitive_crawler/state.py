"""
State Schema for Cognitive Crawler Agent
Generic web crawler with RAG chat capabilities
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class CognitiveCrawlerState(TypedDict):
    """State management for cognitive crawler agent"""
    
    # ========== INPUT (from user or master agent) ==========
    query: str                                # User's query (URL to crawl OR question to ask)
    action: str                               # "discover", "crawl", "chat"
    
    # ========== CRAWL CONFIGURATION ==========
    crawl_sources: Optional[List[str]]        # URLs to crawl (e.g., ["https://example.com/docs"])
    max_pages: int                            # Maximum pages to crawl (user-controlled)
    max_depth: int                            # Link depth (1=only specified URLs, 2=+1 hop, etc.)
    crawl_filters: Optional[Dict[str, Any]]   # Optional: domain restrictions, file types, etc.
    
    # ========== DISCOVERY RESULTS ==========
    pages_discovered: List[Dict]              # Discovered URLs from Tavily search
    sitemap_urls: List[str]                   # URLs from Tavily map
    
    # ========== CRAWL RESULTS ==========
    crawl_results: List[Dict]                 # Raw crawl results from Crawl4AI/Tavily
    pages_crawled: int                        # Count of successfully crawled pages
    crawl_complete: bool                      # Flag: ready for chat mode
    
    # ========== PROCESSING (intermediate results) ==========
    tenders_parsed: List[Dict]                # Parsed/processed documents (legacy name, works for any content)
    tenders_stored: int                       # Count of documents stored in MongoDB
    portals_discovered: List[Dict]            # Discovered portals from Tavily search
    listing_pages: List[str]                  # URLs from portal mapping
    thread_id: Optional[str]                  # Thread ID for session tracking
    
    # ========== EMBEDDING & STORAGE ==========
    embeddings_generated: int                 # Count of vector embeddings created
    documents_stored: int                     # Count of chunks stored in MongoDB
    
    # ========== CHAT MODE (RAG) ==========
    chat_history: List[Dict]                  # Conversation history for context
    relevant_chunks: List[Dict]               # RAG search results
    relevant_tenders: List[Dict]              # RAG search results (legacy name)
    similarity_scores: List[float]            # Similarity scores for chunks
    answer: str                               # LLM-generated answer
    sources: List[str]                        # Source URLs for answer
    
    # ========== OUTPUT ==========
    summary: str                              # Summary of results
    key_findings: List[str]                   # Important discoveries
    recommendations: List[str]                # Next steps or suggestions
    confidence: float                         # 0-1 confidence score
    
    # ========== ARTIFACTS ==========
    artifacts: List[Dict[str, Any]]           # Generated visualizations/exports
    
    # ========== METADATA ==========
    execution_log: List[Dict[str, str]]       # Step-by-step execution log
    error_log: List[str]                      # Errors encountered
    session_id: Optional[str]                 # Session ID for persistence
    execution_time: float                     # Total execution time in seconds

