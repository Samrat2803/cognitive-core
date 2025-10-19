"""Pattern detection utilities for identifying suspicious connections"""

from typing import Dict, List, Any


def detect_suspicious_patterns(entities: Dict[str, Any], timeline: List[Dict]) -> List[Dict]:
    """Detect suspicious patterns across entities and timeline"""
    patterns = []
    
    # Pattern 1: Rapid mobilization
    patterns.extend(detect_rapid_mobilization(timeline))
    
    # Pattern 2: Questionable backers
    patterns.extend(detect_questionable_backers(entities))
    
    # Pattern 3: Shared funding sources
    patterns.extend(detect_shared_funding(entities))
    
    return patterns


def detect_rapid_mobilization(timeline: List[Dict]) -> List[Dict]:
    """Detect if mobilization happened too quickly"""
    patterns = []
    
    if len(timeline) < 2:
        return patterns
    
    # Look for call-to-action followed by protests
    for i in range(len(timeline) - 1):
        event_a = timeline[i]
        event_b = timeline[i + 1]
        
        if ("call" in event_a["description"].lower() and 
            "protest" in event_b["description"].lower()):
            patterns.append({
                "pattern": "rapid_mobilization",
                "description": "Rapid mobilization from call to action to mass protest",
                "entities": [],
                "implication": "Suggests pre-existing infrastructure or planning",
                "suspicion_level": "high"
            })
    
    return patterns


def detect_questionable_backers(entities: Dict[str, Any]) -> List[Dict]:
    """Detect if suspicious entities are funding organizations"""
    patterns = []
    
    for name, entity in entities.items():
        funders = entity.get("funders", [])
        
        for funder in funders:
            funder_entity = entities.get(funder, {})
            
            # Check if funder is suspicious
            if (funder_entity.get("corruption_charges") or 
                funder_entity.get("arms_dealer")):
                patterns.append({
                    "pattern": "questionable_backer",
                    "description": f"{funder} has corruption/arms dealing background but funds {name}",
                    "entities": [name, funder],
                    "implication": "Motivations unclear, needs investigation",
                    "suspicion_level": "critical"
                })
    
    return patterns


def detect_shared_funding(entities: Dict[str, Any]) -> List[Dict]:
    """Detect if multiple entities share same funders (possible coordination)"""
    patterns = []
    
    # Map funders to entities they fund
    funders_map = {}
    for name, entity in entities.items():
        for funder in entity.get("funders", []):
            if funder not in funders_map:
                funders_map[funder] = []
            funders_map[funder].append(name)
    
    # Check for shared funding
    for funder, funded_entities in funders_map.items():
        if len(funded_entities) > 1:
            patterns.append({
                "pattern": "shared_funding",
                "description": f"{funder} funds multiple entities: {', '.join(funded_entities)}",
                "entities": funded_entities,
                "implication": "Possible coordination or common agenda",
                "suspicion_level": "medium" if "NED" not in funder else "high"
            })
    
    return patterns


def find_contradictions(entities: Dict[str, Any]) -> List[Dict]:
    """Find contradictions between claims and facts"""
    contradictions = []
    
    for name, entity in entities.items():
        claims = entity.get("claims", [])
        facts = entity.get("facts", [])
        
        # Simple contradiction detection (can be enhanced with NLP)
        for claim in claims:
            claim_text = claim.get("text", "").lower()
            for fact in facts:
                fact_text = fact.get("fact", "").lower()
                
                # Check for negation patterns
                if any(neg in claim_text for neg in ["not", "never", "no"]):
                    # Remove negation and check if appears in fact
                    claim_core = claim_text.replace("not ", "").replace("never ", "").replace("no ", "")
                    if any(word in fact_text for word in claim_core.split() if len(word) > 4):
                        contradictions.append({
                            "entity": name,
                            "claim": claim_text,
                            "fact": fact_text,
                            "source_claim": claim.get("source", ""),
                            "source_fact": fact.get("source", "")
                        })
    
    return contradictions


def identify_clusters(entities: Dict[str, Any], min_cluster_size: int = 3) -> List[List[str]]:
    """Identify tightly connected clusters of entities (inner circles)"""
    # Build adjacency list
    graph = {name: set(entity.get("connections", [])) for name, entity in entities.items()}
    
    # Find clusters using simple connected components
    visited = set()
    clusters = []
    
    def dfs(node, cluster):
        visited.add(node)
        cluster.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited and neighbor in graph:
                dfs(neighbor, cluster)
    
    for node in graph:
        if node not in visited:
            cluster = []
            dfs(node, cluster)
            if len(cluster) >= min_cluster_size:
                clusters.append(cluster)
    
    return clusters


