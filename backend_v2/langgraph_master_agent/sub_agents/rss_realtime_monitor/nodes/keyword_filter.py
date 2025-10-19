"""
Keyword Filter Node

Filters articles using semantic search + exact keyword matching.
"""

import os
import sys
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.rss_embedder import RSSEmbedder
from rss_realtime_monitor.state import RSSRealtimeMonitorState
from rss_realtime_monitor.config import SEMANTIC_SEARCH_TOP_K, SEMANTIC_MIN_SIMILARITY, EXACT_MATCH_BOOST


async def filter_by_keywords(state: RSSRealtimeMonitorState) -> RSSRealtimeMonitorState:
    """
    Filter articles by keywords using hybrid approach:
    1. Semantic search (embeddings + cosine similarity)
    2. Exact match boosting
    
    This combines broad semantic matching with precision keyword matching.
    """
    
    print("\n[2] Filtering by keywords...")
    
    try:
        articles = state["all_cached_articles"]
        keywords = state["keywords"]
        
        if not articles:
            print("  ⚠️  No articles to filter")
            state["filtered_articles"] = []
            state["articles_analyzed"] = 0
            return state
        
        if not keywords:
            print("  ⚠️  No keywords provided, using all articles")
            state["filtered_articles"] = articles
            state["articles_analyzed"] = len(articles)
            return state
        
        print(f"  Keywords: {', '.join(keywords)}")
        print(f"  Searching {len(articles)} articles...")
        
        # Initialize embedder
        embedder = RSSEmbedder()
        
        # Get article URLs
        article_urls = [a["url"] for a in articles]
        
        # Semantic search for each keyword
        all_matches = {}  # {url: max_score}
        
        for keyword in keywords:
            print(f"    Searching for: '{keyword}'")
            results = await embedder.semantic_search(
                query=keyword,
                article_urls=article_urls,
                top_k=SEMANTIC_SEARCH_TOP_K,
                min_similarity=SEMANTIC_MIN_SIMILARITY
            )
            
            for url, score in results:
                # Track best score for each article
                if url not in all_matches or score > all_matches[url]:
                    all_matches[url] = score
        
        # Apply exact match boosting
        keyword_lower = [k.lower() for k in keywords]
        
        for article in articles:
            if article["url"] not in all_matches:
                continue
            
            # Check for exact matches in title or summary
            title_lower = article.get("title", "").lower()
            summary_lower = article.get("summary", "").lower()
            
            for keyword in keyword_lower:
                if keyword in title_lower or keyword in summary_lower:
                    all_matches[article["url"]] += EXACT_MATCH_BOOST
                    break
        
        # Filter articles that matched
        filtered = []
        for article in articles:
            if article["url"] in all_matches:
                article["relevance_score"] = all_matches[article["url"]]
                filtered.append(article)
        
        # Sort by relevance score (highest first)
        filtered.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        state["filtered_articles"] = filtered
        state["articles_analyzed"] = len(filtered)
        
        print(f"  ✓ Filtered to {len(filtered)} relevant articles")
        
        state["execution_log"].append(
            f"Keyword filtering: {len(filtered)} articles matched (semantic + exact)"
        )
    
    except Exception as e:
        error_msg = f"Error filtering keywords: {str(e)}"
        print(f"  ✗ {error_msg}")
        state["error_log"].append(error_msg)
        # Fallback: use all articles
        state["filtered_articles"] = state["all_cached_articles"]
        state["articles_analyzed"] = len(state["all_cached_articles"])
    
    return state

