"""
Investigative Journalist V2 - State Schema

Minimal, clean state design for hypothesis-driven investigation.
"""

from typing import TypedDict, List, Dict, Optional, Literal


class EntityQuestion(TypedDict, total=False):
    """Question about an entity"""
    q: str                          # Question text
    a: Optional[str]                # Answer (null = unanswered)


class Entity(TypedDict, total=False):
    """Entity in the investigation"""
    name: str                       # Entity name
    type: Literal["person", "organization", "location", "substance", "event"]
    importance: float               # 0-1: investigation_relevance × knowledge_gap
    investigated: bool              # Have we searched about this entity?
    role: str                       # One-sentence description
    questions_about: List[EntityQuestion]
    sources: List[str]              # URLs where entity mentioned


class HypothesisQuestion(TypedDict, total=False):
    """Question testing a hypothesis"""
    q: str                          # Question text
    a: Optional[str]                # Answer (null = unanswered)
    src: Optional[str]              # Source URL if answered


class Hypothesis(TypedDict, total=False):
    """Hypothesis being tested or proven"""
    id: str                         # h1, h2, h3...
    statement: str                  # Clear claim to test
    status: Literal["exploring", "proven", "disproven", "pending"]
    confidence: float               # 0-1
    importance: float               # 0-1
    questions: List[HypothesisQuestion]  # Questions to prove/disprove


class HypothesisSummary(TypedDict, total=False):
    """Compressed form of proven hypothesis"""
    id: str
    statement: str
    status: Literal["proven", "disproven"]
    confidence: float
    key_evidence: List[str]         # Bullet points


class Narrative(TypedDict, total=False):
    """Current investigation narrative"""
    last_updated: int               # Iteration when last updated
    updated_when: str               # What triggered update (e.g., "h1_proven")
    story: str                      # 3-4 sentence current story
    based_on_hypotheses: List[str]  # Which hypothesis IDs inform this
    key_findings: List[str]         # Bullet points


class Connection(TypedDict, total=False):
    """Relationship between entities (for graph viz)"""
    from_entity: str                # Entity name (renamed from 'from')
    to: str                         # Entity name
    type: str                       # Type of relationship


class TimelineEvent(TypedDict, total=False):
    """Event on timeline"""
    date: str                       # YYYY-MM or YYYY-MM-DD
    event: str                      # What happened
    source: str                     # URL


class Cache(TypedDict, total=False):
    """Investigation cache"""
    seen_urls: List[str]            # Already processed URLs
    previous_queries: List[str]     # Already executed search queries
    documents_in_rag: int           # Count of docs in vector DB


class Costs(TypedDict, total=False):
    """Cost tracking"""
    tavily_searches: int
    free_extractions: int
    tavily_extractions: int
    llm_calls: int
    total_cost: float


class Meta(TypedDict, total=False):
    """Investigation metadata"""
    investigation_id: str
    query: str                      # Original investigation question
    iteration: int
    max_iterations: int
    overall_confidence: float       # 0-1
    phase: Literal["exploratory", "hypothesis_testing", "synthesis"]


class InvestigativeJournalistStateV2(TypedDict, total=False):
    """Complete investigation state V2"""
    meta: Meta
    facts: List[str]                # Flat list of verified facts
    entities: List[Entity]
    hypotheses: List[Hypothesis]    # Active and pending hypotheses
    narrative: Narrative
    anomalies: List[str]            # Flat list of suspicious patterns
    connections: List[Connection]   # For graph visualization
    timeline: List[TimelineEvent]
    cache: Cache
    costs: Costs
    
    # Working variables (transient, not persisted)
    search_results: Optional[List[Dict]]      # Current search results
    extracted_content: Optional[List[Dict]]   # Current extracted articles
    next_action: Optional[str]                # Next action to take
    search_query: Optional[str]               # Current search query


class CompressedState(InvestigativeJournalistStateV2):
    """State after compression"""
    entities_archived: List[Dict[str, str]]  # {"name": "...", "reason": "..."}
    _compressed: bool
    _compressed_at_iteration: int


def create_initial_state_v2(
    query: str,
    max_iterations: int,
    investigation_id: str
) -> InvestigativeJournalistStateV2:
    """Create fresh V2 investigation state"""
    return {
        "meta": {
            "investigation_id": investigation_id,
            "query": query,
            "iteration": 0,
            "max_iterations": max_iterations,
            "overall_confidence": 0.0,
            "phase": "exploratory"
        },
        "facts": [],
        "entities": [],
        "hypotheses": [],
        "narrative": {
            "last_updated": 0,
            "updated_when": "",
            "story": "",
            "based_on_hypotheses": [],
            "key_findings": []
        },
        "anomalies": [],
        "connections": [],
        "timeline": [],
        "cache": {
            "seen_urls": [],
            "previous_queries": [],
            "documents_in_rag": 0
        },
        "costs": {
            "tavily_searches": 0,
            "free_extractions": 0,
            "tavily_extractions": 0,
            "llm_calls": 0,
            "total_cost": 0.0
        },
        "search_results": [],
        "extracted_content": [],
        "next_action": None,
        "search_query": None
    }

