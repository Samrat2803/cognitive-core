"""
Source Searcher Node - Searches multiple news sources for the topic
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from typing import Dict, Any
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))

from state import MediaBiasDetectorState
from config import MAX_ARTICLES_PER_SOURCE

# Import shared Tavily client
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))
from shared.tavily_client import TavilyClient

tavily_client = TavilyClient()


async def source_searcher(state: MediaBiasDetectorState) -> Dict[str, Any]:
    """
    Search each news source for articles about the topic
    Returns articles grouped by source
    """
    
    query = state["query"]
    sources = state.get("sources", [])
    time_range_days = state.get("time_range_days", 7)
    
    print(f"\n[Source Searcher] Searching {len(sources)} sources...")
    
    articles_by_source = {}
    total_articles = 0
    
    # Search each source
    search_tasks = []
    for source in sources:
        search_tasks.append(_search_source(query, source, time_range_days))
    
    # Execute searches in parallel
    search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
    
    # Process results
    for source, result in zip(sources, search_results):
        if isinstance(result, Exception):
            print(f"[Source Searcher] Error searching {source}: {str(result)}")
            articles_by_source[source] = []
        else:
            articles_by_source[source] = result
            total_articles += len(result)
            print(f"[Source Searcher] Found {len(result)} articles from {source}")
    
    print(f"[Source Searcher] Total articles found: {total_articles}")
    
    # Filter out sources with no results
    articles_by_source = {k: v for k, v in articles_by_source.items() if v}
    
    if not articles_by_source:
        return {
            "articles_by_source": {},
            "total_articles_found": 0,
            "execution_log": state.get("execution_log", []) + [{
                "step": "source_searcher",
                "action": "No articles found",
                "details": "Try broader search terms or longer time range"
            }],
            "error_log": state.get("error_log", []) + ["No articles found from any source"]
        }
    
    return {
        "articles_by_source": articles_by_source,
        "total_articles_found": total_articles,
        "execution_log": state.get("execution_log", []) + [{
            "step": "source_searcher",
            "action": f"Found {total_articles} articles from {len(articles_by_source)} sources"
        }]
    }


async def _search_source(query: str, source: str, days: int) -> list:
    """Search a specific source using domain filter"""
    
    try:
        # Add domain filter to query
        domain_query = f"{query} site:{source}"
        
        response = await tavily_client.search(
            query=domain_query,
            search_depth="advanced",
            max_results=MAX_ARTICLES_PER_SOURCE,
            domains=[source]  # Use domains parameter instead of days
        )
        
        # Extract relevant fields from response
        results = response.get("results", [])
        articles = []
        for item in results:
            articles.append({
                "title": item.get("title", ""),
                "content": item.get("content", ""),
                "url": item.get("url", ""),
                "published_date": item.get("published_date", ""),
                "score": item.get("score", 0.0)
            })
        
        return articles
        
    except Exception as e:
        print(f"[Source Searcher] Error searching {source}: {str(e)}")
        return []

