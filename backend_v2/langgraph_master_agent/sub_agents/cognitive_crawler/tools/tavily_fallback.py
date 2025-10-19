"""
Tavily Extract Fallback - Used when Crawl4AI fails
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import List, Dict
from tavily_tools import TavilyTools


async def extract_with_tavily(urls: List[str]) -> List[Dict]:
    """
    Extract content using Tavily Extract API
    
    Used as fallback when Crawl4AI fails (CAPTCHA, blocked, etc.)
    Cost: $0.008 per call (can batch multiple URLs)
    
    Args:
        urls: List of URLs to extract
        
    Returns:
        List of extraction results with same format as Crawl4AI
    """
    
    tavily = TavilyTools()
    results = []
    
    try:
        # Tavily Extract can batch multiple URLs in one call
        extract_result = await tavily.tavily_extract(urls=urls)
        
        # Convert Tavily format to our standard format
        if extract_result and 'results' in extract_result:
            for item in extract_result['results']:
                results.append({
                    'url': item.get('url'),
                    'content': item.get('raw_content', ''),
                    'success': True,
                    'method': 'tavily_extract'
                })
        
        # Add failed URLs
        if extract_result and 'failed_results' in extract_result:
            for failed in extract_result['failed_results']:
                results.append({
                    'url': failed.get('url'),
                    'content': '',
                    'success': False,
                    'error': failed.get('error', 'Unknown error'),
                    'method': 'tavily_extract'
                })
                
    except Exception as e:
        # If Tavily Extract itself fails, return empty results
        for url in urls:
            results.append({
                'url': url,
                'content': '',
                'success': False,
                'error': str(e),
                'method': 'tavily_extract'
            })
    
    return results

