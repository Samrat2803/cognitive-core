"""
Executive Summarizer Node

Generates 3-4 sentence executive summary using LLM.
"""

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI
from state import SitRepState
from config import DEFAULT_MODEL, TEMPERATURE, EXECUTIVE_SUMMARY_MAX_SENTENCES

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_executive_summary(state: SitRepState) -> Dict[str, Any]:
    """
    Generate executive summary for SitRep
    
    Creates a 3-4 sentence summary that answers:
    1. What were the most significant developments?
    2. What's the overall trend/pattern?
    3. What's the strategic implication?
    4. (Optional) Are there rapidly developing situations?
    
    Args:
        state: Current state with categorized events
        
    Returns:
        Updated state with executive_summary
    """
    
    print("\n" + "="*80)
    print("📝 NODE: Executive Summarizer")
    print("="*80)
    
    urgent_events = state.get("urgent_events", [])
    high_priority_events = state.get("high_priority_events", [])
    trending_topics = state.get("trending_topics", [])
    date_range = state.get("date_range", "")
    
    # Combine top events for context
    top_events = urgent_events[:5] + high_priority_events[:5]
    
    if not top_events:
        summary = "No significant political developments to report for this period."
        print(f"⚠️  No events to summarize")
        state["executive_summary"] = summary
        state["execution_log"].append("⚠️  Generated default summary (no events)")
        return state
    
    print(f"Generating executive summary from {len(top_events)} top events...")
    
    # Prepare context for LLM
    event_descriptions = []
    for i, event in enumerate(top_events, 1):
        event_desc = (
            f"{i}. [{', '.join(event.get('regions', ['Global']))}] "
            f"{event.get('title', 'Unknown')} "
            f"(Explosiveness: {event.get('explosiveness_score', 0)}/100)"
        )
        event_descriptions.append(event_desc)
    
    events_text = "\n".join(event_descriptions)
    topics_text = ", ".join(trending_topics[:5]) if trending_topics else "various topics"
    
    prompt = f"""You are writing an executive summary for a political situation report covering {date_range}.

TOP DEVELOPMENTS:
{events_text}

TRENDING TOPICS: {topics_text}

Write a {EXECUTIVE_SUMMARY_MAX_SENTENCES}-sentence executive summary that:
1. Highlights the most critical development (first sentence)
2. Identifies the overarching pattern or theme (second sentence)
3. Notes strategic implications or what decision-makers should focus on (third sentence)
4. Optional: Flags any rapidly developing situations (fourth sentence)

Style:
- Direct, factual, no speculation
- Written for senior policymakers/executives
- No phrases like "In conclusion" or "This report covers"
- Start with the most important fact
- Each sentence should be substantive and specific

Return ONLY valid JSON in this exact format:
{{"summary": "your 3-4 sentence summary here"}}"""
    
    try:
        print(f"\n🤖 Calling OpenAI {DEFAULT_MODEL}...")
        
        response = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        summary = result.get("summary", "")
        
        print(f"\n✅ Executive Summary Generated:")
        print(f"   {summary}")
        
        state["executive_summary"] = summary
        state["execution_log"].append(f"✅ Generated executive summary ({len(summary)} chars)")
        
    except Exception as e:
        print(f"\n❌ Error generating summary: {e}")
        
        # Fallback: Create basic summary without LLM
        if urgent_events:
            top_event = urgent_events[0]
            summary = (
                f"Critical development: {top_event.get('title', 'Unknown event')} "
                f"in {', '.join(top_event.get('regions', ['multiple regions']))}. "
                f"Multiple political developments tracked across {len(state.get('regions_covered', []))} regions. "
                f"Monitoring {len(top_events)} high-priority situations."
            )
        else:
            summary = (
                f"Political monitoring tracked {len(top_events)} significant developments "
                f"across {len(state.get('regions_covered', []))} regions during {date_range}."
            )
        
        print(f"\n⚠️  Using fallback summary:")
        print(f"   {summary}")
        
        state["executive_summary"] = summary
        state["error_log"].append(f"Failed to generate LLM summary: {e}")
        state["execution_log"].append("⚠️  Used fallback summary (LLM error)")
    
    return state

