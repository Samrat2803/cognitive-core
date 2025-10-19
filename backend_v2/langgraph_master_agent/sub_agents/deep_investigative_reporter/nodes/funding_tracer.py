"""Trace funding sources - Follow the money"""

from typing import Dict, Any
from ..state import InvestigativeState
from ..strategies import InvestigationStrategies
from ..utils.entity_extraction import extract_funding_entities, create_entity_record


async def funding_tracer(state: InvestigativeState) -> Dict[str, Any]:
    """
    FOLLOW THE MONEY.
    
    Investigate funding sources for organizations and movements.
    """
    print("\n💰 FUNDING TRACER: Following the money...")
    
    strategies = InvestigationStrategies()
    entities = state.get("entities", {})
    funding_network = state.get("funding_network", {})
    
    # Find organizations that need funding investigation
    orgs_to_trace = [
        name for name, entity in entities.items()
        if entity.get("type") == "organization" and not entity.get("funding_traced")
    ]
    
    if not orgs_to_trace:
        print("  ℹ️  No organizations need funding investigation")
        return {}
    
    new_funders = {}
    total_funders_found = 0
    
    for org_name in orgs_to_trace[:3]:  # Limit to 3 orgs per iteration
        print(f"  → Tracing funding for: {org_name}")
        
        # Multi-angle funding search
        result = await strategies.funding_search(org_name)
        
        if result.get("results"):
            # Extract funder entities
            funders = extract_funding_entities(result["results"])
            
            if funders:
                funding_network[org_name] = funders
                entities[org_name]["funding_traced"] = True
                entities[org_name]["funders"] = funders
                total_funders_found += len(funders)
                
                print(f"  ✓ Found {len(funders)} funders for {org_name}")
                
                # Add funders as entities to investigate
                for funder in funders:
                    if funder not in entities and funder not in new_funders:
                        new_funders[funder] = create_entity_record(funder, "funder", importance=0.8)
                        
                        # Check for suspicious keywords
                        if any(keyword in funder.lower() for keyword in ["arms", "weapon", "defense"]):
                            new_funders[funder]["arms_dealer"] = True
                        
                        if any(keyword in funder.lower() for keyword in ["ned", "cia", "usaid"]):
                            new_funders[funder]["importance"] = 0.9  # High importance
    
    # Add new funders to entities
    for name, entity in new_funders.items():
        entities[name] = entity
    
    print(f"  ✓ Total funders found: {total_funders_found}")
    print(f"  ✓ New funder entities: {len(new_funders)}")
    
    return {
        "entities": entities,
        "funding_network": funding_network,
        "entity_queue": state.get("entity_queue", []) + list(new_funders.keys())
    }


