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
    """Execute Tavily search for each country with dynamic params"""
    
    client = TavilyClient()
    query = state["query"]
    countries = state["countries"]
    time_range = state.get("time_range_days", DEFAULT_TIME_RANGE_DAYS)
    iteration = state.get("iteration", 0)
    search_params = state.get("search_params", {})  # NEW: Dynamic params from quality checker
    
    print(f"🔍 Search Executor: Searching {len(countries)} countries (iteration {iteration + 1})...")
    
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
        
        # NEW: Use dynamic search params if available (for iteration > 0)
        if search_params and country in search_params:
            country_config = search_params[country]
            country_query = country_config.get("query", f"{query} public opinion {full_country_name}")
            include_domains = country_config.get("include_domains", None)
            print(f"   Searching with targeted params: {country_query[:60]}...")
            if include_domains:
                print(f"      Domains: {', '.join(include_domains[:3])}...")
        else:
            # Default query (iteration 0)
            country_query = f"{query} public opinion {full_country_name}"
            include_domains = None
            print(f"   Searching: {country_query[:60]}...")
        
        try:
            # Build search kwargs
            search_kwargs = {
                "query": country_query,
                "search_depth": SEARCH_DEPTH,
                "max_results": MAX_RESULTS_PER_COUNTRY,
                "include_answer": True,
                "country": full_country_name  # NEW: Use country parameter (helps with domain filtering)
            }
            
            # NEW: Add domain filtering (use correct parameter name: 'domains')
            if include_domains and len(include_domains) > 0:
                search_kwargs["domains"] = include_domains  # ✅ Correct parameter name!
                print(f"      Domain filter: {', '.join(include_domains[:3])}...")
            
            result = await client.search(**search_kwargs)
            
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
            "action": f"Iteration {iteration + 1}: Searched {len(countries)} countries, found {total_results} results"
        }]
    }

