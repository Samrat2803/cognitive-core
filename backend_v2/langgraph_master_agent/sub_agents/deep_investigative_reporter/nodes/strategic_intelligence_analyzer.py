"""
Strategic Intelligence Analyzer - The "Brain" of the investigative agent using GPT-5.

This node uses GPT-5 to:
1. Analyze current investigation state
2. Identify suspicious patterns and connections
3. Detect knowledge gaps
4. Generate new investigative questions
5. Form hypotheses to test
6. Prioritize next investigation targets
"""

from typing import Dict, Any, List
from ..state import InvestigativeState
from ..utils.pattern_detection import detect_suspicious_patterns, find_contradictions, identify_clusters
from shared.llm_factory import LLMFactory


# LLM instance for strategic analysis
_llm = None

def get_llm():
    """Get or create LLM instance"""
    global _llm
    if _llm is None:
        _llm = LLMFactory.create_llm(
            model="gpt-5",
            max_tokens=1500,
            reasoning_effort="low",
            verbosity="low"
        )
    return _llm


async def strategic_intelligence_analyzer(state: InvestigativeState) -> Dict[str, Any]:
    """
    The brain of the investigation.
    
    Continuously asks: "What don't we know?" and "What's suspicious here?"
    """
    print("\n🧠 STRATEGIC INTELLIGENCE ANALYZER: Analyzing investigation state...")
    
    # Analyze current knowledge
    analysis = analyze_current_state(state)
    
    # Generate new investigative questions
    new_questions = generate_investigative_questions(analysis, state)
    
    # Identify potential hidden connections
    potential_connections = identify_hidden_connections(analysis, state)
    
    # Form hypotheses
    hypotheses = form_hypotheses(analysis, state)
    
    # Prioritize entity queue based on questions and patterns
    prioritized_queue = prioritize_investigation_targets(
        state.get("entities", {}),
        new_questions,
        potential_connections
    )
    
    # Update state
    updates = {
        "generated_questions": state.get("generated_questions", []) + new_questions,
        "potential_connections": state.get("potential_connections", []) + potential_connections,
        "investigation_hypotheses": hypotheses,
        "knowledge_gaps": analysis["knowledge_gaps"],
        "suspicious_patterns": analysis["suspicious_patterns"],
        "entity_queue": prioritized_queue,
        "investigation_depth": state.get("investigation_depth", 0) + 1
    }
    
    # Log insights
    print(f"  ✓ Generated {len(new_questions)} new questions")
    print(f"  ✓ Found {len(potential_connections)} potential connections")
    print(f"  ✓ Formed {len(hypotheses)} hypotheses")
    print(f"  ✓ Detected {len(analysis['suspicious_patterns'])} suspicious patterns")
    
    return updates


def analyze_current_state(state: InvestigativeState) -> Dict[str, Any]:
    """Analyze what we know and what we don't know"""
    entities = state.get("entities", {})
    timeline = state.get("timeline", [])
    funding_network = state.get("funding_network", {})
    
    analysis = {
        "knowledge_gaps": [],
        "suspicious_patterns": [],
        "high_value_targets": []
    }
    
    # KNOWLEDGE GAP 1: Low confidence entities
    low_confidence = [
        name for name, info in entities.items()
        if info.get("confidence", 0) < 0.6
    ]
    if low_confidence:
        analysis["knowledge_gaps"].append({
            "type": "low_confidence_entities",
            "entities": low_confidence,
            "impact": "Cannot make strong claims about these actors"
        })
    
    # KNOWLEDGE GAP 2: Unfunded organizations
    orgs_without_funding = [
        name for name, info in entities.items()
        if info.get("type") == "organization" and not info.get("funders")
    ]
    if orgs_without_funding:
        analysis["knowledge_gaps"].append({
            "type": "unknown_funding",
            "entities": orgs_without_funding,
            "impact": "Cannot assess external influence"
        })
    
    # KNOWLEDGE GAP 3: Isolated entities
    isolated = [
        name for name, info in entities.items()
        if len(info.get("connections", [])) == 0 and info.get("importance", 0) > 0.5
    ]
    if isolated:
        analysis["knowledge_gaps"].append({
            "type": "isolated_entities",
            "entities": isolated,
            "impact": "Missing network connections"
        })
    
    # SUSPICIOUS PATTERNS
    patterns = detect_suspicious_patterns(entities, timeline)
    analysis["suspicious_patterns"] = patterns
    
    # HIGH VALUE TARGETS (entities that need investigation)
    for name, entity in entities.items():
        if (not entity.get("investigated") and 
            entity.get("importance", 0) > 0.6):
            analysis["high_value_targets"].append(name)
    
    return analysis


def generate_investigative_questions(analysis: Dict, state: InvestigativeState) -> List[Dict]:
    """Generate targeted questions based on knowledge gaps"""
    questions = []
    entities = state.get("entities", {})
    
    # QUESTION TYPE 1: Follow the money
    for gap in analysis["knowledge_gaps"]:
        if gap["type"] == "unknown_funding":
            for entity_name in gap["entities"]:
                questions.append({
                    "type": "funding",
                    "priority": "critical",
                    "question": f"Who funds {entity_name}?",
                    "search_strategy": "funding_search",
                    "entity": entity_name,
                    "answered": False
                })
    
    # QUESTION TYPE 2: Understand entities
    for gap in analysis["knowledge_gaps"]:
        if gap["type"] == "low_confidence_entities":
            for entity_name in gap["entities"]:
                entity = entities.get(entity_name, {})
                priority = "high" if entity.get("importance", 0) > 0.7 else "medium"
                questions.append({
                    "type": "understanding",
                    "priority": priority,
                    "question": f"Who is {entity_name} and what's their background?",
                    "search_strategy": "comprehensive_search",
                    "entity": entity_name,
                    "answered": False
                })
    
    # QUESTION TYPE 3: Map connections
    for gap in analysis["knowledge_gaps"]:
        if gap["type"] == "isolated_entities":
            for entity_name in gap["entities"]:
                questions.append({
                    "type": "isolation",
                    "priority": "medium",
                    "question": f"How is {entity_name} connected to other actors?",
                    "search_strategy": "association_search",
                    "entity": entity_name,
                    "answered": False
                })
    
    # QUESTION TYPE 4: Investigate suspicious patterns
    for pattern in analysis["suspicious_patterns"]:
        if pattern["suspicion_level"] in ["critical", "high"]:
            questions.append({
                "type": "motivation",
                "priority": "critical" if pattern["suspicion_level"] == "critical" else "high",
                "question": f"Why: {pattern['description']}?",
                "search_strategy": "network_search",
                "entities": pattern.get("entities", []),
                "answered": False
            })
    
    # Sort by priority
    priority_order = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    questions.sort(key=lambda q: priority_order[q["priority"]], reverse=True)
    
    return questions[:10]  # Top 10 questions


def identify_hidden_connections(analysis: Dict, state: InvestigativeState) -> List[Dict]:
    """Identify potential hidden connections between entities"""
    connections = []
    entities = state.get("entities", {})
    funding_network = state.get("funding_network", {})
    
    # CONNECTION TYPE 1: Shared funding sources
    funders_map = {}
    for org_name, funders in funding_network.items():
        for funder in funders:
            if funder not in funders_map:
                funders_map[funder] = []
            funders_map[funder].append(org_name)
    
    for funder, funded_orgs in funders_map.items():
        if len(funded_orgs) > 1:
            connections.append({
                "type": "shared_funding",
                "entities": funded_orgs,
                "connector": funder,
                "suspicion_level": "high" if any(x in funder for x in ["NED", "CIA", "State Department"]) else "medium",
                "question": f"Why is {funder} funding multiple entities: {', '.join(funded_orgs)}?"
            })
    
    # CONNECTION TYPE 2: Suspicious credentials
    for name, entity in entities.items():
        background = entity.get("background", "").lower()
        current_role = entity.get("current_role", "").lower()
        
        # Arms dealer funding peace movement?
        if entity.get("arms_dealer") and any(org in funding_network.get(name, []) 
                                              for org in entities.keys()):
            connections.append({
                "type": "suspicious_credentials",
                "entities": [name],
                "suspicion_level": "critical",
                "question": f"Why is arms dealer {name} involved in funding organizations?"
            })
        
        # Corruption charges but still active?
        if entity.get("corruption_charges"):
            connections.append({
                "type": "suspicious_credentials",
                "entities": [name],
                "suspicion_level": "high",
                "question": f"{name} has corruption charges - why are they still influential?"
            })
    
    # CONNECTION TYPE 3: Network clusters
    clusters = identify_clusters(entities, min_cluster_size=3)
    for cluster in clusters:
        connections.append({
            "type": "network_cluster",
            "entities": cluster,
            "suspicion_level": "medium",
            "question": f"What's the relationship between this group: {', '.join(cluster[:3])}{'...' if len(cluster) > 3 else ''}?"
        })
    
    return connections


def form_hypotheses(analysis: Dict, state: InvestigativeState) -> List[Dict]:
    """Form hypotheses to test"""
    hypotheses = []
    entities = state.get("entities", {})
    
    # Count foreign funders
    foreign_funders = [
        name for name, entity in entities.items()
        if entity.get("type") == "funder" and 
        any(x in name for x in ["US", "NED", "USAID", "Embassy", "International"])
    ]
    
    # Count suspicious backers
    suspicious_backers = [
        name for name, entity in entities.items()
        if entity.get("corruption_charges") or entity.get("arms_dealer")
    ]
    
    # HYPOTHESIS 1: Foreign orchestration
    if len(foreign_funders) >= 2:
        hypotheses.append({
            "hypothesis": "foreign_orchestrated_movement",
            "evidence_for": [
                f"Multiple foreign funders: {', '.join(foreign_funders)}",
                "Professional organizing detected" if "rapid_mobilization" in [p["pattern"] for p in analysis["suspicious_patterns"]] else ""
            ],
            "evidence_against": [],
            "to_verify": [
                "Are there training programs?",
                "What's the timeline of funding vs. events?",
                "Are grievances genuine?"
            ],
            "confidence": 0.4
        })
    
    # HYPOTHESIS 2: Organic grassroots
    timeline_str = str(state.get("timeline", [])).lower()
    if "corruption" in timeline_str:
        hypotheses.append({
            "hypothesis": "organic_grassroots_anger",
            "evidence_for": [
                "Real corruption scandals documented",
                "Economic grievances visible"
            ],
            "evidence_against": [
                "Professional organizing infrastructure exists"
            ],
            "to_verify": [
                "Did protests start spontaneously?",
                "Is there genuine popular support?"
            ],
            "confidence": 0.6
        })
    
    # HYPOTHESIS 3: Hybrid (organic anger + professional channeling)
    if len(foreign_funders) > 0 and len(suspicious_backers) > 0:
        hypotheses.append({
            "hypothesis": "hybrid_organic_anger_professional_mobilization",
            "evidence_for": [
                "Genuine grievances exist (corruption, inequality)",
                "Professional infrastructure pre-built",
                f"Questionable backers: {', '.join(suspicious_backers)}"
            ],
            "evidence_against": [],
            "to_verify": [
                "When was infrastructure built vs when anger emerged?",
                "Who benefits from outcome?"
            ],
            "confidence": 0.7
        })
    
    return hypotheses


def prioritize_investigation_targets(entities: Dict, questions: List[Dict], 
                                     connections: List[Dict]) -> List[str]:
    """Prioritize which entities to investigate next"""
    priority_scores = {}
    
    for name, entity in entities.items():
        if entity.get("investigated"):
            continue
        
        score = entity.get("importance", 0.5) * 100
        
        # Boost if mentioned in critical questions
        critical_questions = [q for q in questions if q["priority"] == "critical"]
        if any(name in str(q) for q in critical_questions):
            score += 50
        
        # Boost if part of suspicious connections
        high_suspicion_connections = [c for c in connections if c["suspicion_level"] in ["critical", "high"]]
        if any(name in c.get("entities", []) for c in high_suspicion_connections):
            score += 40
        
        # Boost if organization without funding info
        if entity.get("type") == "organization" and not entity.get("funders"):
            score += 30
        
        priority_scores[name] = score
    
    # Sort by score
    sorted_entities = sorted(priority_scores.items(), key=lambda x: x[1], reverse=True)
    
    return [name for name, score in sorted_entities]

