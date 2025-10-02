"""
Synthesizer Node - Generates final report with insights and recommendations
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

from config import MODEL, TEMPERATURE
from state import MediaBiasDetectorState

client = AsyncOpenAI()


async def synthesizer(state: MediaBiasDetectorState) -> Dict[str, Any]:
    """
    Synthesize all analysis into:
    1. Executive summary
    2. Key findings
    3. Consensus vs divergence points
    4. Omission analysis
    5. Recommendations for news consumers
    """
    
    query = state["query"]
    bias_classification = state.get("bias_classification", {})
    loaded_language = state.get("loaded_language", {})
    framing_analysis = state.get("framing_analysis", {})
    overall_bias_range = state.get("overall_bias_range", {})
    
    print(f"\n[Synthesizer] Generating final report...")
    
    # Prepare analysis summary for LLM
    analysis_summary = f"""
Query: {query}

Bias Classification:
{json.dumps(bias_classification, indent=2)}

Overall Bias Range:
{json.dumps(overall_bias_range, indent=2)}

Loaded Language Count by Source:
{json.dumps({k: len(v) for k, v in loaded_language.items()}, indent=2)}

Framing Analysis:
{json.dumps({k: v.get('primary_frame', 'unknown') for k, v in framing_analysis.items()}, indent=2)}
"""
    
    prompt = f"""Analyze media bias across multiple sources for: "{query}"

Analysis:
{analysis_summary}

Generate comprehensive synthesis:

1. Executive Summary (2-3 sentences): Overall bias landscape
2. Key Findings (4-6 points): Most important insights about bias patterns
3. Consensus Points (2-3 items): What ALL sources agree on
4. Divergence Points (2-3 items): Where sources significantly differ
5. Omission Analysis: What each source might be leaving out
6. Recommendations (3-4 points): How news consumers should approach this topic
7. Confidence (0.0-1.0): Overall confidence in this analysis

Return JSON:
{{
    "summary": "Executive summary text",
    "key_findings": ["finding 1", "finding 2", "finding 3"],
    "consensus_points": ["consensus 1", "consensus 2"],
    "divergence_points": [
        {{"topic": "immigration policy", "positions": {{"cnn.com": "supportive", "foxnews.com": "critical"}}}}
    ],
    "omission_analysis": {{
        "source1.com": ["what they omit"],
        "source2.com": ["what they omit"]
    }},
    "recommendations": ["recommendation 1", "recommendation 2"],
    "confidence": 0.85
}}"""
    
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        synthesis = json.loads(response.choices[0].message.content)
        
        print(f"[Synthesizer] Generated report with {len(synthesis.get('key_findings', []))} findings")
        print(f"[Synthesizer] Confidence: {synthesis.get('confidence', 0.0):.2f}")
        
        return {
            "summary": synthesis.get("summary", ""),
            "key_findings": synthesis.get("key_findings", []),
            "consensus_points": synthesis.get("consensus_points", []),
            "divergence_points": synthesis.get("divergence_points", []),
            "omission_analysis": synthesis.get("omission_analysis", {}),
            "recommendations": synthesis.get("recommendations", []),
            "confidence": synthesis.get("confidence", 0.0),
            "execution_log": state.get("execution_log", []) + [{
                "step": "synthesizer",
                "action": f"Generated synthesis with {len(synthesis.get('key_findings', []))} findings",
                "details": f"Confidence: {synthesis.get('confidence', 0.0):.2f}"
            }]
        }
        
    except Exception as e:
        print(f"[Synthesizer] Error: {str(e)}")
        return {
            "summary": "Error generating synthesis",
            "key_findings": [],
            "consensus_points": [],
            "divergence_points": [],
            "omission_analysis": {},
            "recommendations": [],
            "confidence": 0.0,
            "execution_log": state.get("execution_log", []) + [{
                "step": "synthesizer",
                "action": "Error generating synthesis",
                "details": str(e)
            }],
            "error_log": state.get("error_log", []) + [f"Synthesizer error: {str(e)}"]
        }

