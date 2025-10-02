"""
Bias Classifier Node - Classifies political lean/bias of each source
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

from config import MODEL, TEMPERATURE, BIAS_SPECTRUM, BIAS_TECHNIQUES
from state import MediaBiasDetectorState

client = AsyncOpenAI()


async def bias_classifier(state: MediaBiasDetectorState) -> Dict[str, Any]:
    """
    Classify the political lean and bias of each source
    Returns bias classification with spectrum position, score, confidence, evidence
    """
    
    articles_by_source = state.get("articles_by_source", {})
    query = state["query"]
    
    print(f"\n[Bias Classifier] Classifying bias for {len(articles_by_source)} sources...")
    
    if not articles_by_source:
        return {
            "bias_classification": {},
            "execution_log": state.get("execution_log", []) + [{
                "step": "bias_classifier",
                "action": "Skipped - no articles to analyze"
            }]
        }
    
    # Classify each source in parallel
    classification_tasks = []
    for source, articles in articles_by_source.items():
        classification_tasks.append(_classify_source_bias(source, articles, query))
    
    results = await asyncio.gather(*classification_tasks, return_exceptions=True)
    
    bias_classification = {}
    for source, result in zip(articles_by_source.keys(), results):
        if isinstance(result, Exception):
            print(f"[Bias Classifier] Error classifying {source}: {str(result)}")
            bias_classification[source] = {
                "spectrum": "center",
                "bias_score": 0.0,
                "confidence": 0.0,
                "evidence": ["Error in classification"],
                "techniques": []
            }
        else:
            bias_classification[source] = result
            print(f"[Bias Classifier] {source}: {result['spectrum']} (score: {result['bias_score']:.2f})")
    
    # Calculate overall bias range
    scores = [v["bias_score"] for v in bias_classification.values()]
    overall_bias_range = {
        "min": min(scores) if scores else 0.0,
        "max": max(scores) if scores else 0.0,
        "avg": sum(scores) / len(scores) if scores else 0.0,
        "range": max(scores) - min(scores) if scores else 0.0
    }
    
    print(f"[Bias Classifier] Bias range: {overall_bias_range['min']:.2f} to {overall_bias_range['max']:.2f}")
    
    return {
        "bias_classification": bias_classification,
        "overall_bias_range": overall_bias_range,
        "execution_log": state.get("execution_log", []) + [{
            "step": "bias_classifier",
            "action": f"Classified {len(bias_classification)} sources",
            "details": f"Range: {overall_bias_range['min']:.2f} to {overall_bias_range['max']:.2f}"
        }]
    }


async def _classify_source_bias(source: str, articles: list, query: str) -> dict:
    """Classify bias for a single source"""
    
    if not articles:
        return {
            "spectrum": "center",
            "bias_score": 0.0,
            "confidence": 0.0,
            "evidence": [],
            "techniques": []
        }
    
    # Combine article content (limit to prevent token overflow)
    combined_text = ""
    for article in articles[:3]:
        title = article.get("title", "")
        content = article.get("content", "")[:500]  # Limit content length
        combined_text += f"\nTitle: {title}\nContent: {content}\n"
    
    prompt = f"""Analyze the political bias of {source} in their coverage of: "{query}"

Articles from {source}:
{combined_text}

Classify their political bias:
1. Spectrum position: {', '.join(BIAS_SPECTRUM.keys())}
2. Bias score: -1.0 (far left) to +1.0 (far right), 0.0 is center
3. Confidence: 0.0 to 1.0 in this classification
4. Evidence: 3-5 specific examples showing bias from the text
5. Techniques: Bias techniques detected from this list: {', '.join(BIAS_TECHNIQUES)}

Consider:
- Word choice and framing
- What facts are emphasized vs omitted
- Sources quoted and their political leanings
- Tone and emotional language
- Balance and fairness

Return JSON:
{{
    "spectrum": "center_left",
    "bias_score": -0.25,
    "confidence": 0.85,
    "evidence": ["example 1", "example 2", "example 3"],
    "techniques": ["selective_quoting", "labeling"]
}}"""
    
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Validate bias_score is within range
        bias_score = max(-1.0, min(1.0, result.get("bias_score", 0.0)))
        result["bias_score"] = bias_score
        
        return result
        
    except Exception as e:
        print(f"[Bias Classifier] Error for {source}: {str(e)}")
        return {
            "spectrum": "center",
            "bias_score": 0.0,
            "confidence": 0.0,
            "evidence": [f"Error: {str(e)}"],
            "techniques": []
        }

