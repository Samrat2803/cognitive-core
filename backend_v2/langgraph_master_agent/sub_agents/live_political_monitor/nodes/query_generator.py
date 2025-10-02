"""
Query Generator Node - Generates targeted Tavily queries from user keywords
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../../.env'))

from openai import AsyncOpenAI
from state import LiveMonitorState
from config import MODEL, TEMPERATURE, MAX_QUERIES_PER_REQUEST

client = AsyncOpenAI()


async def generate_queries(state: LiveMonitorState) -> LiveMonitorState:
    """
    Generate optimized Tavily search queries from user keywords
    
    Strategy:
    - Combine keywords intelligently
    - Add context words (latest, breaking, today)
    - Generate 2-3 variations for better coverage
    """
    
    print("\n🔍 Generating search queries from keywords...")
    
    keywords = state['keywords']
    
    # If keywords are empty, use defaults
    if not keywords:
        from config import DEFAULT_KEYWORDS
        keywords = DEFAULT_KEYWORDS
    
    print(f"   Keywords: {', '.join(keywords)}")
    
    # Use LLM to generate optimal queries
    prompt = f"""You are a search query optimizer for political news monitoring.

Given these keywords: {', '.join(keywords)}

Generate {MAX_QUERIES_PER_REQUEST} optimized search queries for Tavily API that will find the most relevant and recent political news articles.

Guidelines:
- Combine keywords naturally
- Add temporal context (today, latest, breaking, recent)
- Make queries specific enough to get relevant results
- Vary the query structure for better coverage

Return JSON format:
{{
    "queries": ["query 1", "query 2", "query 3"]
}}

Example:
Keywords: ["Bihar", "corruption", "India"]
Queries: ["Bihar corruption scandal latest", "Bihar government officials investigation", "India Bihar political corruption today"]
"""
    
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        generated_queries = result.get('queries', [])
        
        print(f"   ✓ Generated {len(generated_queries)} queries")
        for i, query in enumerate(generated_queries, 1):
            print(f"      {i}. {query}")
        
        # Add to execution log
        execution_log = state.get('execution_log', [])
        execution_log.append({
            "step": "generate_queries",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "queries_generated": len(generated_queries)
        })
        
        return {
            **state,
            "generated_queries": generated_queries,
            "execution_log": execution_log
        }
        
    except Exception as e:
        print(f"   ✗ Query generation failed: {e}")
        
        # Fallback: Simple combination
        fallback_queries = [
            " ".join(keywords) + " latest news",
            " ".join(keywords) + " breaking developments",
            " ".join(keywords[:2]) + " today"  # Use first 2 keywords
        ]
        
        print(f"   ⚠ Using fallback queries")
        
        error_log = state.get('error_log', [])
        error_log.append(f"Query generation error: {str(e)}")
        
        execution_log = state.get('execution_log', [])
        execution_log.append({
            "step": "generate_queries",
            "timestamp": datetime.now().isoformat(),
            "status": "fallback",
            "error": str(e)
        })
        
        return {
            **state,
            "generated_queries": fallback_queries,
            "execution_log": execution_log,
            "error_log": error_log
        }

