"""Investigate entities using multiple strategies"""

from typing import Dict, Any
from ..state import InvestigativeState
from ..strategies import InvestigationStrategies
from ..utils.entity_extraction import extract_entities_from_text, extract_facts_from_results, create_entity_record


async def entity_investigator(state: InvestigativeState) -> Dict[str, Any]:
    """
    Investigate current entity using multiple strategies until confidence threshold reached.
    
    Tries up to 8 different investigation methods.
    """
    print("\n🔬 ENTITY INVESTIGATOR: Investigating entities...")
    
    strategies = InvestigationStrategies()
    entities = state.get("entities", {})
    entity_queue = state.get("entity_queue", [])
    
    if not entity_queue:
        print("  ⚠️  No entities in queue")
        return {}
    
    # Get next entity to investigate
    current_entity_name = entity_queue[0]
    entity = entities.get(current_entity_name, {})
    
    print(f"  → Investigating: {current_entity_name} (type: {entity.get('type')})")
    
    # Don't re-investigate if already confident
    if entity.get("confidence", 0) >= 0.8:
        print(f"  ✓ Already confident about {current_entity_name}")
        # Remove from queue
        return {"entity_queue": entity_queue[1:]}
    
    # Try different strategies
    strategy_methods = [
        ("direct", lambda: strategies.direct_search(current_entity_name, "background role")),
        ("association", lambda: strategies.association_search(current_entity_name, entity.get("type", "unknown"))),
        ("controversy", lambda: strategies.controversy_search(current_entity_name)),
    ]
    
    new_entities = {}
    total_facts = 0
    
    for strategy_name, strategy_func in strategy_methods:
        # Skip if already tried
        if strategy_name in entity.get("blocked_methods", []):
            continue
        
        try:
            result = await strategy_func()
            
            if result.get("results"):
                # Extract facts
                facts = extract_facts_from_results(result["results"])
                entity["facts"] = entity.get("facts", []) + facts
                total_facts += len(facts)
                
                # Extract new entities
                for res in result["results"]:
                    found_entities = extract_entities_from_text(res.get("content", ""))
                    for ent in found_entities:
                        ent_name = ent["name"]
                        if ent_name not in entities and ent_name not in new_entities:
                            new_entities[ent_name] = create_entity_record(ent_name, ent["type"], importance=0.5)
                        
                        # Add connection
                        if ent_name not in entity.get("connections", []):
                            entity["connections"] = entity.get("connections", []) + [ent_name]
                
                # Increase confidence
                entity["confidence"] = min(entity.get("confidence", 0) + 0.2, 1.0)
                entity["investigation_attempts"] = entity.get("investigation_attempts", 0) + 1
                
                # If we found good info, break
                if len(facts) >= 3:
                    break
            else:
                entity["blocked_methods"] = entity.get("blocked_methods", []) + [strategy_name]
        
        except Exception as e:
            print(f"  ⚠️  Strategy {strategy_name} failed: {e}")
            entity["blocked_methods"] = entity.get("blocked_methods", []) + [strategy_name]
    
    # Mark as investigated
    entity["investigated"] = True
    entities[current_entity_name] = entity
    
    # Add new entities to collection and queue
    for new_name, new_entity in new_entities.items():
        entities[new_name] = new_entity
    
    new_queue = entity_queue[1:] + list(new_entities.keys())
    
    print(f"  ✓ Found {total_facts} facts, {len(new_entities)} new entities")
    print(f"  ✓ Confidence: {entity['confidence']:.2f}")
    
    return {
        "entities": entities,
        "entity_queue": new_queue,
        "current_entity": current_entity_name
    }


