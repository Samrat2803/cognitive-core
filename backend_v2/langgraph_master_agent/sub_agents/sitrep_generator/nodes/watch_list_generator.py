"""
Watch List Generator Node

Identifies items to monitor in the next 24-48 hours.
"""

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI
from state import SitRepState
from config import DEFAULT_MODEL, TEMPERATURE, MAX_WATCH_LIST_ITEMS, WATCH_LIST_TIMEFRAME_HOURS

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_watch_list(state: SitRepState) -> Dict[str, Any]:
    """
    Generate watch list of items to monitor in next 24-48 hours
    
    Identifies:
    - Developing situations that could escalate
    - Scheduled events (votes, summits, deadlines)
    - Potential flashpoints
    
    Args:
        state: Current state with events and analysis
        
    Returns:
        Updated state with watch_list
    """
    
    print("\n" + "="*80)
    print("👁️  NODE: Watch List Generator")
    print("="*80)
    
    urgent_events = state.get("urgent_events", [])
    high_priority_events = state.get("high_priority_events", [])
    
    # Focus on events that are ongoing or developing
    watch_candidates = urgent_events + high_priority_events[:5]
    
    if not watch_candidates:
        print("⚠️  No events for watch list")
        state["watch_list"] = []
        state["execution_log"].append("⚠️  No items for watch list")
        return state
    
    print(f"Generating watch list from {len(watch_candidates)} events...")
    
    # Prepare context for LLM
    event_descriptions = []
    for i, event in enumerate(watch_candidates, 1):
        event_desc = (
            f"{i}. {event.get('title', 'Unknown')} "
            f"[{', '.join(event.get('regions', ['Global']))}] "
            f"- {event.get('reasoning', '')[:200]}"
        )
        event_descriptions.append(event_desc)
    
    events_text = "\n".join(event_descriptions)
    
    prompt = f"""You are analyzing political developments to create a watch list for the next {WATCH_LIST_TIMEFRAME_HOURS} hours.

CURRENT DEVELOPMENTS:
{events_text}

Generate a watch list of {MAX_WATCH_LIST_ITEMS} items that decision-makers should monitor. For each item:
- Identify what could happen next
- Note when it might happen (if time-sensitive)
- Explain why it matters

Focus on:
- Situations that could escalate
- Scheduled events (votes, meetings, deadlines)
- Potential turning points
- Diplomatic developments

Format: Each item should be a single sentence starting with what to watch, then why it matters.

Example format:
- "[Event/Development] - [Why it matters and what could happen]"

Return ONLY valid JSON:
{{
  "watch_items": [
    "item 1 text",
    "item 2 text",
    ...
  ]
}}"""
    
    try:
        print(f"\n🤖 Calling OpenAI {DEFAULT_MODEL}...")
        
        response = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        watch_items = result.get("watch_items", [])[:MAX_WATCH_LIST_ITEMS]
        
        print(f"\n✅ Watch List Generated ({len(watch_items)} items):")
        for i, item in enumerate(watch_items, 1):
            print(f"   {i}. {item[:100]}...")
        
        state["watch_list"] = watch_items
        state["execution_log"].append(f"✅ Generated watch list ({len(watch_items)} items)")
        
    except Exception as e:
        print(f"\n❌ Error generating watch list: {e}")
        
        # Fallback: Create basic watch list
        watch_items = []
        for event in watch_candidates[:MAX_WATCH_LIST_ITEMS]:
            item = (
                f"{event.get('title', 'Unknown situation')} in "
                f"{', '.join(event.get('regions', ['affected region']))} - "
                f"Monitor for escalation or resolution"
            )
            watch_items.append(item)
        
        print(f"\n⚠️  Using fallback watch list ({len(watch_items)} items)")
        
        state["watch_list"] = watch_items
        state["error_log"].append(f"Failed to generate LLM watch list: {e}")
        state["execution_log"].append("⚠️  Used fallback watch list (LLM error)")
    
    return state

