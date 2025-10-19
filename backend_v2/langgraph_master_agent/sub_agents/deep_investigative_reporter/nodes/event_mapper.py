"""Map timeline of events and find first articles"""

from typing import Dict, Any
from ..state import InvestigativeState
from ..strategies import InvestigationStrategies
from ..utils.entity_extraction import extract_entities_from_text, extract_timeline_events, create_entity_record


async def event_mapper(state: InvestigativeState) -> Dict[str, Any]:
    """
    Find first articles and build timeline of events.
    
    This establishes the cutoff date and chronological context.
    """
    print("\n📅 EVENT MAPPER: Building timeline...")
    
    strategies = InvestigationStrategies()
    query = state["query"]
    
    # Search for timeline and first articles
    result = await strategies.direct_search(query, "timeline first article earliest when did")
    
    # Extract timeline events
    timeline = extract_timeline_events(result.get("results", []))
    
    # Find first article URL
    first_article_url = None
    if result.get("results"):
        # Sort by date if available
        first_article_url = result["results"][0].get("url", "")
    
    # Extract initial entities from FULL CONTENT (not just event descriptions)
    entities = {}
    
    # Combine all content from search results
    full_content = "\n\n".join([
        f"{r.get('title', '')} {r.get('content', '')}"
        for r in result.get("results", [])[:5]  # Top 5 results
    ])
    
    # Extract entities from full content (GPT-5 will see context)
    if full_content:
        event_entities = extract_entities_from_text(full_content)
        for entity_data in event_entities:
            name = entity_data["name"]
            if name not in entities:
                entities[name] = create_entity_record(name, entity_data["type"], importance=0.7)
    
    # Create entity queue (prioritize by mention frequency)
    entity_queue = list(entities.keys())
    
    print(f"  ✓ Found {len(timeline)} timeline events")
    print(f"  ✓ Extracted {len(entities)} initial entities")
    print(f"  ✓ First article: {first_article_url[:50]}...")
    
    return {
        "timeline": timeline,
        "first_article_url": first_article_url,
        "entities": entities,
        "entity_queue": entity_queue
    }

