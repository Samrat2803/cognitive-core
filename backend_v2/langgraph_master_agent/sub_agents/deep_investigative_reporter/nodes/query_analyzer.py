"""Parse user query and extract investigation goals"""

from typing import Dict, Any
from ..state import InvestigativeState


async def query_analyzer(state: InvestigativeState) -> Dict[str, Any]:
    """
    Analyze user query to understand investigation goal.
    
    Extract:
    - Investigation type ("why", "who funds", "what happened")
    - Key entities mentioned
    - Time constraints
    """
    print("\n🔍 QUERY ANALYZER: Parsing investigation request...")
    
    query = state["query"].lower()
    
    # Determine investigation goal
    if any(word in query for word in ["why", "reason", "cause"]):
        investigation_goal = "causal_analysis"
    elif any(word in query for word in ["fund", "money", "sponsor", "donor"]):
        investigation_goal = "funding_investigation"
    elif any(word in query for word in ["who", "behind", "actors"]):
        investigation_goal = "actor_mapping"
    elif any(word in query for word in ["network", "connection", "relationship"]):
        investigation_goal = "network_mapping"
    else:
        investigation_goal = "comprehensive_investigation"
    
    print(f"  ✓ Investigation type: {investigation_goal}")
    
    # Extract cutoff date if mentioned
    cutoff_date = state.get("cutoff_date")
    if not cutoff_date:
        # Look for date mentions in query
        import re
        date_pattern = r'(\d{4}-\d{2}-\d{2})|(\d{1,2} [A-Za-z]+ \d{4})'
        match = re.search(date_pattern, state["query"])
        if match:
            cutoff_date = match.group(0)
            print(f"  ✓ Using cutoff date: {cutoff_date}")
    
    return {
        "investigation_goal": investigation_goal,
        "cutoff_date": cutoff_date,
        "max_depth": 5,  # Default max recursion depth
        "overall_confidence": 0.0,
        "investigation_depth": 0,
        "entities": {},
        "entity_queue": [],
        "generated_questions": [],
        "potential_connections": [],
        "investigation_hypotheses": [],
        "knowledge_gaps": [],
        "suspicious_patterns": [],
        "causal_chains": [],
        "funding_network": {},
        "relationships": {},
        "timeline": [],
        "artifacts": [],
        "should_continue": True
    }


