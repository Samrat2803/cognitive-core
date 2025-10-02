"""
Bias Detector Node - Detect bias types in coverage
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from openai import AsyncOpenAI
from config import MODEL, TEMPERATURE, BIAS_TYPES
from state import SentimentAnalyzerState
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))

client = AsyncOpenAI()


async def bias_detector(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Detect bias types in coverage"""
    
    search_results = state["search_results"]
    query = state["query"]
    bias_analysis = {}
    
    print(f"⚖️  Bias Detector: Analyzing {len(search_results)} countries...")
    
    for country, results in search_results.items():
        print(f"   Analyzing: {country}...")
        
        if not results:
            bias_analysis[country] = {
                "bias_types": [],
                "overall_bias": "none",
                "bias_score": 0.0,
                "bias_severity": 0.0,
                "bias_notes": "No data available for bias analysis",
                "examples": []
            }
            print(f"   ⚠️ {country}: No results")
            continue
        
        combined_text = "\n\n".join([
            f"Source: {r.get('url', '')}\nTitle: {r.get('title', '')}\nContent: {r.get('content', '')[:500]}"
            for r in results[:2]  # Use top 2 results
        ])
        
        prompt = f"""Analyze bias in coverage of "{query}" from {country}.

Detect these bias types (methodological issues, NOT sentiment):
{', '.join(BIAS_TYPES)}

Sources:
{combined_text}

Return JSON with:
- bias_types: list of detected bias types (from the list above)
- overall_bias: "left", "right", "center", or "mixed"
- bias_score: float from -1 (left) to +1 (right), 0 for center
- bias_severity: float 0-1 indicating how much methodological issues affect reporting quality (1=severe, 0=minimal)
- bias_notes: string explaining the methodological problems found (2-3 sentences)
- examples: list of 1-2 specific biased phrases/framing found

Example: {{"bias_types": ["source_bias", "framing_bias"], "overall_bias": "left", "bias_score": -0.4, "bias_severity": 0.6, "bias_notes": "Coverage relies heavily on government-backed sources with limited independent voices. Framing consistently favors policy initiatives without presenting counter-arguments.", "examples": ["Government-backed sources dominate", "Positive framing of policy"]}}"""
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                temperature=TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            bias_analysis[country] = json.loads(response.choices[0].message.content)
            print(f"   ✅ {country}: {bias_analysis[country]['overall_bias']} ({len(bias_analysis[country].get('bias_types', []))} types)")
            
        except Exception as e:
            print(f"   ❌ {country}: Error - {e}")
            bias_analysis[country] = {
                "bias_types": [],
                "overall_bias": "unknown",
                "bias_score": 0.0,
                "bias_severity": 0.0,
                "bias_notes": f"Analysis error: {str(e)[:100]}",
                "examples": []
            }
    
    return {
        "bias_analysis": bias_analysis,
        "execution_log": state.get("execution_log", []) + [{
            "step": "bias_detector",
            "action": f"Detected bias for {len(bias_analysis)} countries"
        }]
    }

