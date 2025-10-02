"""
Framing Analyzer Node - Analyzes how each source frames the story
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

from config import MODEL, TEMPERATURE, FRAMING_TYPES
from state import MediaBiasDetectorState

client = AsyncOpenAI()


async def framing_analyzer(state: MediaBiasDetectorState) -> Dict[str, Any]:
    """
    Analyze how each source frames the story
    Returns framing analysis with primary frame, techniques, and examples
    """
    
    articles_by_source = state.get("articles_by_source", {})
    query = state["query"]
    
    print(f"\n[Framing Analyzer] Analyzing framing for {len(articles_by_source)} sources...")
    
    if not articles_by_source:
        return {
            "framing_analysis": {},
            "execution_log": state.get("execution_log", []) + [{
                "step": "framing_analyzer",
                "action": "Skipped - no articles to analyze"
            }]
        }
    
    # Analyze each source in parallel
    framing_tasks = []
    for source, articles in articles_by_source.items():
        framing_tasks.append(_analyze_source_framing(source, articles, query))
    
    results = await asyncio.gather(*framing_tasks, return_exceptions=True)
    
    framing_analysis = {}
    
    for source, result in zip(articles_by_source.keys(), results):
        if isinstance(result, Exception):
            print(f"[Framing Analyzer] Error analyzing {source}: {str(result)}")
            framing_analysis[source] = {
                "primary_frame": "unknown",
                "secondary_frames": [],
                "techniques": [],
                "examples": []
            }
        else:
            framing_analysis[source] = result
            print(f"[Framing Analyzer] {source}: {result['primary_frame']} frame")
    
    return {
        "framing_analysis": framing_analysis,
        "execution_log": state.get("execution_log", []) + [{
            "step": "framing_analyzer",
            "action": f"Analyzed framing for {len(framing_analysis)} sources"
        }]
    }


async def _analyze_source_framing(source: str, articles: list, query: str) -> dict:
    """Analyze framing for a single source"""
    
    if not articles:
        return {
            "primary_frame": "unknown",
            "secondary_frames": [],
            "techniques": [],
            "examples": []
        }
    
    # Combine article content
    combined_text = ""
    for article in articles[:3]:
        title = article.get("title", "")
        content = article.get("content", "")[:500]
        combined_text += f"\nTitle: {title}\nContent: {content}\n"
    
    prompt = f"""Analyze how {source} frames the story about: "{query}"

Framing types:
{', '.join(FRAMING_TYPES)}

Articles:
{combined_text}

Identify:
1. Primary frame: The main way the story is presented
2. Secondary frames: Other framing approaches used (if any)
3. Techniques: How the framing is achieved
4. Examples: Specific quotes/passages showing the framing

Return JSON:
{{
    "primary_frame": "conflict_frame",
    "secondary_frames": ["responsibility"],
    "techniques": ["emphasizing disagreement", "us vs them language"],
    "examples": [
        "quote showing conflict framing",
        "another example"
    ],
    "explanation": "Brief explanation of how this source frames the story"
}}"""
    
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"[Framing Analyzer] Error for {source}: {str(e)}")
        return {
            "primary_frame": "unknown",
            "secondary_frames": [],
            "techniques": [],
            "examples": []
        }

