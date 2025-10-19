"""
Tavily Discovery Tools - Uses centralized TavilyDirectTools
"""

import sys
import os

# Add parent paths for imports
current_dir = os.path.dirname(__file__)
crawler_dir = os.path.abspath(os.path.join(current_dir, '../..'))
master_tools_dir = os.path.abspath(os.path.join(current_dir, '../../../tools'))

if crawler_dir not in sys.path:
    sys.path.insert(0, crawler_dir)
if master_tools_dir not in sys.path:
    sys.path.insert(0, master_tools_dir)

from typing import List, Dict
from tavily_direct import TavilyDirectTools


# Initialize centralized Tavily client
tavily = TavilyDirectTools()


async def discover_tender_portals(query: str, sources: List[str] = None, max_results: int = 5) -> List[Dict]:
    """
    Use Tavily to discover relevant web pages
    
    GENERAL PURPOSE - Works for any query:
    - News articles
    - Government documents  
    - Research papers
    - Any web content
    
    Args:
        query: User's natural language query (e.g., "drug regulations in India")
        sources: Optional list of suggested domains to focus on (e.g., ["gov.in", "wikipedia.org"])
        max_results: Maximum number of search results to return (default: 5)
        
    Returns:
        List of page dictionaries with url, title, score, etc.
    """
    
    # Intelligently build search parameters based on user intent
    query_lower = query.lower()
    
    # Detect specific domains mentioned
    wikipedia_mentioned = 'wikipedia' in query_lower
    govt_mentioned = any(kw in query_lower for kw in ['government', 'govt', 'official', 'ministry'])
    india_mentioned = any(kw in query_lower for kw in ['india', 'indian'])
    
    # Build include_domains list based on user intent
    include_domains = sources if sources else None
    
    # If user explicitly mentions domains, add them to include_domains
    if wikipedia_mentioned or govt_mentioned:
        include_domains = []
        if wikipedia_mentioned:
            include_domains.append("wikipedia.org")
            print(f"   📚 Including Wikipedia")
        if govt_mentioned and india_mentioned:
            include_domains.extend(["gov.in", "nic.in"])
            print(f"   🇮🇳 Including Indian government sites (.gov.in, .nic.in)")
        elif govt_mentioned:
            include_domains.extend(["gov", "gov.uk", "gov.au"])
            print(f"   🏛️  Including government sites")
    
    if not include_domains:
        print(f"   🌐 Searching all domains")
    
    print(f"   Tavily Search: {query} (max_results={max_results})")
    
    try:
        # Use centralized Tavily tool with intelligent parameters
        result = await tavily.search(
            query=query,
            max_results=max_results,  # Now dynamic!
            search_depth="basic",
            include_domains=include_domains
        )
        
        if not result.get("success"):
            print(f"   ❌ Tavily search error: {result.get('error')}")
            return []
        
        # Convert to the format expected by portal_mapper
        formatted_results = []
        for item in result.get("results", []):
            formatted_results.append({
                'url': item.get('url'),
                'title': item.get('title'),
                'content': item.get('content'),
                'score': item.get('score', 0)
            })
        
        return formatted_results
        
    except Exception as e:
        print(f"   ❌ Tavily search error: {e}")
        return []


async def map_portal_structure_with_instructions(url: str, instructions: str) -> Dict:
    """
    Use Tavily to map portal structure with keyword-based instructions
    
    Args:
        url: URL of the portal to map
        instructions: Natural language instructions to guide mapping
        
    Returns:
        Dictionary with portal structure and prioritized URLs
    """
    
    print(f"   Tavily Map (with instructions): {url}")
    print(f"   Instructions: {instructions[:80]}...")
    
    try:
        result = await tavily.map(
            url=url,
            instructions=instructions,
            max_depth=2,
            limit=100
        )
        
        if not result.get("success"):
            return {"results": []}
        
        # Convert to expected format
        return {
            "results": result.get("urls", [])
        }
        
    except Exception as e:
        print(f"   ❌ Tavily map error: {e}")
        return {"results": []}

