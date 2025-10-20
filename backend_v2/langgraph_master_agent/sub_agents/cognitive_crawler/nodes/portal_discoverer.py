"""
Portal Discoverer Node - Uses Tavily to discover tender portals
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from state import CognitiveCrawlerState
from tools.tavily_discovery import discover_tender_portals


async def portal_discoverer(state: CognitiveCrawlerState) -> Dict[str, Any]:
    """
    Discover relevant web pages using Tavily search
    
    GENERAL PURPOSE - Works for any query:
    - News articles
    - Government documents
    - Research papers
    - Company websites
    - Any web content
    """
    
    query = state["query"]
    sources = state.get("sources", [])  # Optional suggested domains
    max_pages = state.get("max_pages", 20)  # User's max_pages becomes max_results for search
    
    print("🔍 Portal Discoverer: Searching for relevant pages...")
    
    # Log what we're searching for
    if sources:
        action_msg = f"Discovering pages for: {query} (focusing on {', '.join(sources[:3])}, max_results={max_pages})"
    else:
        action_msg = f"Discovering pages for: {query} (max_results={max_pages})"
    
    state["execution_log"].append({
        "step": "portal_discoverer",
        "action": action_msg
    })
    
    try:
        # Use Tavily to discover pages (pass max_pages as max_results)
        portals = await discover_tender_portals(query, sources, max_results=max_pages)
        
        state["portals_discovered"] = portals
        print(f"   ✅ Discovered {len(portals)} relevant pages")
        
        # Log each discovered URL
        for i, portal in enumerate(portals, 1):
            title = portal.get('title', 'Unknown')
            url = portal.get('url', 'N/A')
            print(f"   {i}. {title}")
            print(f"      URL: {url}")
            
            # Add to execution log for frontend display
            state["execution_log"].append({
                "step": "portal_discoverer",
                "action": f"Found: {title}",
                "url": url
            })
        
    except Exception as e:
        error_msg = f"portal_discoverer error: {str(e)}"
        print(f"   ❌ {error_msg}")
        state["error_log"].append(error_msg)
        state["portals_discovered"] = []
    
    return state

