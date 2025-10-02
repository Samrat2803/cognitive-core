"""
Query Analyzer Node - Extract countries and validate input
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from openai import AsyncOpenAI
from ..config import MODEL, TEMPERATURE, DEFAULT_COUNTRIES
from ..state import SentimentAnalyzerState
import json

client = AsyncOpenAI()


async def query_analyzer(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """
    Analyze query and extract:
    - Main topic
    - Countries to analyze (if not provided)
    - Time range
    """
    
    query = state["query"]
    countries = state.get("countries", [])
    
    print(f"📝 Query Analyzer: Analyzing query...")
    
    # If countries not provided, extract from query or use defaults
    if not countries:
        prompt = f"""Extract countries mentioned in this query. If none mentioned, return empty list.
        
Query: {query}

Return as JSON: {{"countries": ["US", "China", ...]}}"""
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                temperature=TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            extracted_countries = result.get("countries", [])
            
            if not extracted_countries:
                countries = DEFAULT_COUNTRIES[:5]
                print(f"   No countries found, using defaults: {countries}")
            else:
                countries = extracted_countries
                print(f"   Extracted countries: {countries}")
                
        except Exception as e:
            print(f"   ⚠️ Error extracting countries: {e}")
            countries = DEFAULT_COUNTRIES[:5]
            print(f"   Using default countries: {countries}")
    
    # Limit to max countries
    countries = countries[:10]
    
    return {
        "countries": countries,
        "execution_log": state.get("execution_log", []) + [{
            "step": "query_analyzer",
            "action": f"Identified {len(countries)} countries to analyze"
        }]
    }

