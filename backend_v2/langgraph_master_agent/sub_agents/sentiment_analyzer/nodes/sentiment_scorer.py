"""
Sentiment Scorer Node - Score sentiment for each country using LLM
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from openai import AsyncOpenAI
from config import MODEL, TEMPERATURE
from state import SentimentAnalyzerState
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))

client = AsyncOpenAI()


async def sentiment_scorer(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Score sentiment for each country using LLM"""
    
    search_results = state["search_results"]
    query = state["query"]
    sentiment_scores = {}
    
    print(f"🎭 Sentiment Scorer: Scoring {len(search_results)} countries...")
    
    for country, results in search_results.items():
        print(f"   Scoring: {country}...")
        
        if not results:
            sentiment_scores[country] = {
                "sentiment": "neutral",
                "score": 0.0,
                "reasoning": "No data available for analysis",
                "positive_pct": 0.33,
                "negative_pct": 0.33,
                "neutral_pct": 0.34,
                "key_points": ["No data available"],
                "source_type": "other",
                "credibility_score": 0.0
            }
            print(f"   ⚠️ {country}: No results to analyze")
            continue
        
        # Combine search results
        combined_text = "\n\n".join([
            f"Title: {r.get('title', '')}\nContent: {r.get('content', '')[:500]}"
            for r in results[:3]  # Use top 3 results
        ])
        
        prompt = f"""Analyze sentiment towards "{query}" in {country} based on these sources.

Sources:
{combined_text}

Return JSON with:
- sentiment: "positive", "negative", or "neutral"
- score: float from -1 (very negative) to +1 (very positive)
- reasoning: string explaining WHY this sentiment score was assigned (2-3 sentences)
- positive_pct: percentage positive (0-1)
- negative_pct: percentage negative (0-1)
- neutral_pct: percentage neutral (0-1)
- key_points: list of 2-3 key findings
- source_type: classify dominant source as "media", "govt", "political_party", "encyclopedia", or "other"
- credibility_score: float 0-1 indicating source reliability (1=high, 0=low)

Example: {{"sentiment": "positive", "score": 0.6, "reasoning": "Sources show strong government support and positive policy initiatives, though public opinion remains divided.", "positive_pct": 0.7, "negative_pct": 0.1, "neutral_pct": 0.2, "key_points": ["Strong government support", "Public opinion divided"], "source_type": "media", "credibility_score": 0.8}}"""
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                temperature=TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            sentiment_scores[country] = json.loads(response.choices[0].message.content)
            print(f"   ✅ {country}: {sentiment_scores[country]['sentiment']} (score: {sentiment_scores[country]['score']:.2f})")
            
        except Exception as e:
            print(f"   ❌ {country}: Error - {e}")
            sentiment_scores[country] = {
                "sentiment": "neutral",
                "score": 0.0,
                "reasoning": f"Analysis error: {str(e)[:100]}",
                "positive_pct": 0.33,
                "negative_pct": 0.33,
                "neutral_pct": 0.34,
                "key_points": [f"Error: {str(e)[:100]}"],
                "source_type": "other",
                "credibility_score": 0.0
            }
    
    return {
        "sentiment_scores": sentiment_scores,
        "execution_log": state.get("execution_log", []) + [{
            "step": "sentiment_scorer",
            "action": f"Scored sentiment for {len(sentiment_scores)} countries"
        }]
    }

