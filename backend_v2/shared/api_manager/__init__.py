"""
Unified API Management for Political Analyst Workbench

This module provides centralized management for all external API calls:
- Tavily (search, extract, QnA, crawl)
- OpenAI (LLM completions, embeddings)
- Caching layer for all API calls
- Cost tracking and optimization

Usage:
    from shared.api_manager import get_api_manager
    
    api = get_api_manager()
    
    # Tavily calls (automatically cached)
    results = await api.tavily_search("query")
    content = await api.tavily_extract(["url1", "url2"])
    
    # OpenAI calls (automatically cached if enabled)
    response = await api.llm_complete("prompt", cache_key="optional")
    embedding = await api.create_embedding("text")
    
    # Cost tracking
    stats = api.get_cost_stats()
"""

from .unified_api_manager import UnifiedAPIManager, get_api_manager

__all__ = ['UnifiedAPIManager', 'get_api_manager']


