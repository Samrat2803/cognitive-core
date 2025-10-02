"""
Synthesizer Node - Create final summary
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from openai import AsyncOpenAI
from ..config import MODEL, TEMPERATURE
from ..state import SentimentAnalyzerState
import json

client = AsyncOpenAI()


async def synthesizer(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Synthesize final response"""
    
    query = state["query"]
    sentiment_scores = state["sentiment_scores"]
    bias_analysis = state["bias_analysis"]
    
    print(f"📝 Synthesizer: Creating summary...")
    
    prompt = f"""Create a comprehensive sentiment analysis report.

Query: {query}

Sentiment Scores:
{json.dumps(sentiment_scores, indent=2)}

Bias Analysis:
{json.dumps(bias_analysis, indent=2)}

Create a report with:
1. Executive summary (2-3 sentences)
2. Country-by-country breakdown
3. Key patterns and differences
4. Bias findings
5. Overall confidence assessment

Format as markdown.
"""
    
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}]
        )
        
        summary = response.choices[0].message.content
        print(f"   ✅ Summary created ({len(summary)} chars)")
        
    except Exception as e:
        print(f"   ❌ Error creating summary: {e}")
        summary = f"# Sentiment Analysis: {query}\n\nError generating summary: {e}"
    
    # Extract key findings
    key_findings = []
    for country, scores in sentiment_scores.items():
        sentiment = scores.get('sentiment', 'unknown')
        score = scores.get('score', 0)
        key_findings.append(f"{country}: {sentiment} (score: {score:.2f})")
    
    # Calculate confidence
    valid_scores = [s for s in sentiment_scores.values() if s.get('score') is not None]
    confidence = len(valid_scores) / len(sentiment_scores) if sentiment_scores else 0.0
    
    print(f"   Key findings: {len(key_findings)}")
    print(f"   Confidence: {confidence:.2%}")
    
    return {
        "summary": summary,
        "key_findings": key_findings,
        "confidence": confidence,
        "execution_log": state.get("execution_log", []) + [{
            "step": "synthesizer",
            "action": "Generated final report"
        }]
    }

