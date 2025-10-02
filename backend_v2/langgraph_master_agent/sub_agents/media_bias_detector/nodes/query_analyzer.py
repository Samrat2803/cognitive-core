"""
Query Analyzer Node - Analyzes user query to optimize search strategy
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from typing import Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))

from config import MODEL, TEMPERATURE, DEFAULT_SOURCES
from state import MediaBiasDetectorState

client = AsyncOpenAI()


async def query_analyzer(state: MediaBiasDetectorState) -> Dict[str, Any]:
    """
    Analyze user query to:
    1. Extract core topic
    2. Identify key entities/people
    3. Determine if specific sources should be targeted
    4. Generate optimized search keywords
    """
    
    query = state["query"]
    specified_sources = state.get("sources", [])
    
    print(f"\n[Query Analyzer] Analyzing query: {query}")
    
    # Use LLM to analyze query
    prompt = f"""Analyze this news/media query for bias detection:
Query: "{query}"

Extract:
1. Core topic (what is being discussed)
2. Key entities (people, organizations, countries mentioned)
3. Suggested search keywords (for finding relevant articles)
4. Recommended news sources (if query mentions specific outlets or regions)
5. Time sensitivity (is this breaking news, recent, or historical?)

Return JSON:
{{
    "core_topic": "string",
    "entities": ["entity1", "entity2"],
    "search_keywords": ["keyword1", "keyword2"],
    "recommended_sources": ["source1.com", "source2.com"],
    "time_sensitive": true/false,
    "suggested_time_range_days": 7
}}"""
    
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        # Determine final sources to search
        if specified_sources:
            sources_to_search = specified_sources[:8]  # User-specified
        elif analysis.get("recommended_sources"):
            # Mix recommended with defaults
            sources_to_search = list(set(
                analysis["recommended_sources"][:4] + DEFAULT_SOURCES[:4]
            ))[:8]
        else:
            sources_to_search = DEFAULT_SOURCES[:8]
        
        # Update time range if query is time-sensitive
        time_range = state.get("time_range_days", 7)
        if analysis.get("time_sensitive") and not state.get("time_range_days"):
            time_range = min(analysis.get("suggested_time_range_days", 3), 3)
        
        print(f"[Query Analyzer] Core topic: {analysis['core_topic']}")
        print(f"[Query Analyzer] Will search {len(sources_to_search)} sources")
        print(f"[Query Analyzer] Time range: {time_range} days")
        
        return {
            "sources": sources_to_search,
            "time_range_days": time_range,
            "execution_log": state.get("execution_log", []) + [{
                "step": "query_analyzer",
                "action": f"Analyzed query, targeting {len(sources_to_search)} sources",
                "details": analysis["core_topic"]
            }]
        }
        
    except Exception as e:
        print(f"[Query Analyzer] Error: {str(e)}")
        # Fallback to defaults
        return {
            "sources": DEFAULT_SOURCES[:8],
            "time_range_days": state.get("time_range_days", 7),
            "execution_log": state.get("execution_log", []) + [{
                "step": "query_analyzer",
                "action": "Using default sources (analysis failed)",
                "details": str(e)
            }],
            "error_log": state.get("error_log", []) + [f"Query analysis error: {str(e)}"]
        }

