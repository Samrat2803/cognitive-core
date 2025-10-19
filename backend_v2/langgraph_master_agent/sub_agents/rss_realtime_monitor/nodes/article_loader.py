"""
Article Loader Node

Loads articles from MongoDB RSS cache based on filters.
"""

import os
import sys
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.rss_collector import RSSCollector
from rss_realtime_monitor.state import RSSRealtimeMonitorState
from rss_realtime_monitor.config import MAX_ARTICLE_AGE_HOURS


async def load_articles(state: RSSRealtimeMonitorState) -> RSSRealtimeMonitorState:
    """
    Load articles from MongoDB cache
    
    Applies:
    - Time filter (48h window - fixed)
    - Region filter (if specified)
    - Category filter (if specified)
    
    Does NOT apply keyword filtering (that's next node)
    """
    
    print("\n[1] Loading articles from MongoDB...")
    
    try:
        collector = RSSCollector()
        
        # Apply region/category filters if provided
        region = state.get("regions", [None])[0] if state.get("regions") else None
        category = state.get("categories", [None])[0] if state.get("categories") else None
        
        # Load articles
        articles = await collector.get_articles(
            max_age_hours=MAX_ARTICLE_AGE_HOURS,
            region=region,
            category=category,
            limit=1000
        )
        
        state["all_cached_articles"] = articles
        state["total_articles_cached"] = len(articles)
        
        print(f"  ✓ Loaded {len(articles)} articles from cache")
        if region:
            print(f"    Region filter: {region}")
        if category:
            print(f"    Category filter: {category}")
        
        state["execution_log"].append(
            f"Loaded {len(articles)} articles (region={region}, category={category})"
        )
    
    except Exception as e:
        error_msg = f"Error loading articles: {str(e)}"
        print(f"  ✗ {error_msg}")
        state["error_log"].append(error_msg)
        state["all_cached_articles"] = []
        state["total_articles_cached"] = 0
    
    return state

