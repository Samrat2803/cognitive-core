"""
Language Analyzer Node - Detects loaded/biased language
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from typing import Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv
import json
import asyncio

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))

from config import MODEL, TEMPERATURE, LOADED_LANGUAGE_TYPES
from state import MediaBiasDetectorState

client = AsyncOpenAI()


async def language_analyzer(state: MediaBiasDetectorState) -> Dict[str, Any]:
    """
    Detect loaded/biased language in articles from each source
    Returns loaded language examples with categories
    """
    
    articles_by_source = state.get("articles_by_source", {})
    
    print(f"\n[Language Analyzer] Analyzing language for {len(articles_by_source)} sources...")
    
    if not articles_by_source:
        return {
            "loaded_language": {},
            "execution_log": state.get("execution_log", []) + [{
                "step": "language_analyzer",
                "action": "Skipped - no articles to analyze"
            }]
        }
    
    # Analyze each source in parallel
    analysis_tasks = []
    for source, articles in articles_by_source.items():
        analysis_tasks.append(_analyze_source_language(source, articles))
    
    results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
    
    loaded_language = {}
    total_loaded_phrases = 0
    
    for source, result in zip(articles_by_source.keys(), results):
        if isinstance(result, Exception):
            print(f"[Language Analyzer] Error analyzing {source}: {str(result)}")
            loaded_language[source] = []
        else:
            loaded_language[source] = result
            total_loaded_phrases += len(result)
            print(f"[Language Analyzer] {source}: Found {len(result)} loaded phrases")
    
    print(f"[Language Analyzer] Total loaded phrases found: {total_loaded_phrases}")
    
    return {
        "loaded_language": loaded_language,
        "execution_log": state.get("execution_log", []) + [{
            "step": "language_analyzer",
            "action": f"Detected {total_loaded_phrases} loaded phrases across {len(loaded_language)} sources"
        }]
    }


async def _analyze_source_language(source: str, articles: list) -> list:
    """Analyze loaded language for a single source"""
    
    if not articles:
        return []
    
    # Combine article content
    combined_text = ""
    for article in articles[:3]:
        title = article.get("title", "")
        content = article.get("content", "")[:500]
        combined_text += f"\n{title}\n{content}\n"
    
    prompt = f"""Identify loaded/biased language from {source}.

Types to detect: {', '.join(LOADED_LANGUAGE_TYPES)}

Text:
{combined_text}

Find words and phrases that:
- Emotionally manipulate readers
- Use sensationalist language
- Create fear or panic
- Are propaganda terms
- Use euphemisms (soften reality) or dysphemisms (harsh language)
- Are loaded adjectives with bias

For each phrase found:
- phrase: The exact biased text
- type: Which category it falls into
- context: Surrounding context (brief)
- why_biased: Explanation of the bias

Return JSON with up to 10 most significant examples:
{{
    "loaded_phrases": [
        {{
            "phrase": "regime",
            "type": "dysphemism",
            "context": "referring to the government",
            "why_biased": "Uses negative connotation instead of neutral 'government'"
        }}
    ]
}}"""
    
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("loaded_phrases", [])
        
    except Exception as e:
        print(f"[Language Analyzer] Error for {source}: {str(e)}")
        return []

