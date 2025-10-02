"""
Search Executor Node - Execute Tavily searches for each country
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from shared.tavily_client import TavilyClient
from config import SEARCH_DEPTH, MAX_RESULTS_PER_COUNTRY, DEFAULT_TIME_RANGE_DAYS
from state import SentimentAnalyzerState


async def search_executor(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Execute Tavily search for each country"""
    
    client = TavilyClient()
    query = state["query"]
    countries = state["countries"]
    time_range = state.get("time_range_days", DEFAULT_TIME_RANGE_DAYS)
    
    print(f"🔍 Search Executor: Searching {len(countries)} countries...")
    
    search_results = {}
    
    # Map country codes to full names for better search results
    country_names = {
        "US": "United States",
        "UK": "United Kingdom",
        "France": "France",
        "Germany": "Germany",
        "China": "China",
        "Russia": "Russia",
        "India": "India",
        "Iran": "Iran",
        "Israel": "Israel",
        "Japan": "Japan",
        "Canada": "Canada",
        "Australia": "Australia",
        "Brazil": "Brazil",
        "Mexico": "Mexico",
        "EU": "European Union"
    }
    
    for country in countries:
        # Create more specific query with full country name
        full_country_name = country_names.get(country, country)
        
        # Enhanced query construction for better results
        # Example: "nuclear policy" + "United States" -> "nuclear policy public opinion United States"
        country_query = f"{query} public opinion {full_country_name}"
        
        print(f"   Searching: {country_query[:60]}...")
        
        try:
            # Fixed: Removed incorrect 'country' parameter
            # The 'country' parameter in Tavily is for domain filtering (.com, .co.uk), 
            # not for filtering content about a country
            result = await client.search(
                query=country_query,
                search_depth=SEARCH_DEPTH,
                max_results=MAX_RESULTS_PER_COUNTRY,
                include_answer=True
            )
            
            if "results" in result:
                search_results[country] = result["results"]
                print(f"   ✅ {country}: {len(result['results'])} results")
            else:
                search_results[country] = []
                print(f"   ⚠️ {country}: No results")
                
        except Exception as e:
            print(f"   ❌ {country}: Error - {e}")
            search_results[country] = []
    
    total_results = sum(len(results) for results in search_results.values())
    print(f"   Total results: {total_results}")
    
    return {
        "search_results": search_results,
        "execution_log": state.get("execution_log", []) + [{
            "step": "search_executor",
            "action": f"Searched {len(countries)} countries, found {total_results} results"
        }]
    }

