"""
Article Fetcher Node - Fetches articles from Tavily API
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../../.env'))

# Add shared path for TavilyClient
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../shared'))
sys.path.insert(0, shared_path)

from tavily_client import TavilyClient
from state import LiveMonitorState
from config import TAVILY_MAX_RESULTS_PER_QUERY, SEARCH_DEPTH

tavily = TavilyClient()


async def fetch_articles(state: LiveMonitorState) -> LiveMonitorState:
    """
    Fetch articles from Tavily for all generated queries
    
    Deduplicates by URL
    """
    
    print("\n📰 Fetching articles from Tavily...")
    
    queries = state['generated_queries']
    
    all_articles = []
    all_images = []  # Store images from all queries
    
    for i, query in enumerate(queries, 1):
        try:
            print(f"   Query {i}/{len(queries)}: '{query}'")
            
            results = await tavily.search(
                query=query,
                search_depth=SEARCH_DEPTH,
                max_results=TAVILY_MAX_RESULTS_PER_QUERY,
                include_images=True  # Fetch images for dashboard
            )
            
            articles = results.get('results', [])
            images = results.get('images', [])  # Get images array from Tavily
            
            all_articles.extend(articles)
            all_images.extend(images)
            
            print(f"      ✓ Retrieved {len(articles)} articles, {len(images)} images")
            
        except Exception as e:
            print(f"      ✗ Error: {str(e)[:100]}")
            error_log = state.get('error_log', [])
            error_log.append(f"Tavily query error for '{query}': {str(e)}")
            state['error_log'] = error_log
    
    # Deduplicate by URL
    unique_articles = []
    seen_urls = set()
    
    for article in all_articles:
        url = article.get('url', '')
        if url and url not in seen_urls:
            unique_articles.append(article)
            seen_urls.add(url)
    
    print(f"\n   📊 Total articles: {len(all_articles)}")
    print(f"   📊 Unique articles: {len(unique_articles)}")
    
    # Extract unique sources
    domains = []
    for article in unique_articles:
        url = article.get('url', '')
        if url:
            try:
                domain = url.split('/')[2]
                domains.append(domain)
            except:
                pass
    
    unique_sources = len(set(domains))
    print(f"   📊 Unique sources: {unique_sources}")
    print(f"   🖼️  Total images: {len(all_images)}")
    
    # Add to execution log
    execution_log = state.get('execution_log', [])
    execution_log.append({
        "step": "fetch_articles",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "total_articles": len(all_articles),
        "unique_articles": len(unique_articles),
        "unique_sources": unique_sources,
        "images_fetched": len(all_images)
    })
    
    return {
        **state,
        "raw_articles": unique_articles,
        "fetched_images": all_images,  # Store images for topics
        "total_articles_analyzed": len(unique_articles),
        "execution_log": execution_log
    }

