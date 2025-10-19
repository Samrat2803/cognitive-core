"""
State schema for Deep Investigative Reporter sub-agent.

This state maintains all investigation data including entities, relationships,
funding networks, causal chains, and strategic intelligence.
"""

from typing import TypedDict, List, Dict, Optional, Annotated, Literal
from datetime import datetime
from langgraph.graph import add_messages


class InvestigationEntity(TypedDict, total=False):
    """Schema for an entity being investigated"""
    name: str
    type: Literal["person", "organization", "event", "claim", "funder"]
    importance: float  # 0-1 priority score
    investigated: bool
    confidence: float  # 0-1 how well we understand this entity
    facts: List[Dict[str, str]]  # verified facts about entity
    claims: List[Dict[str, str]]  # unverified claims
    connections: List[str]  # other entity names connected to this
    sources: List[str]  # URLs where info was found
    investigation_attempts: int
    blocked_methods: List[str]  # methods that didn't work
    background: str
    current_role: str
    funders: List[str]  # for organizations
    funding_traced: bool
    corruption_charges: bool
    arms_dealer: bool


class CausalLink(TypedDict):
    """A cause-effect relationship"""
    cause: str
    effect: str
    evidence: List[str]
    confidence: float


class InvestigativeQuestion(TypedDict):
    """A question the agent needs to answer"""
    type: Literal["funding", "motivation", "understanding", "isolation", 
                  "causation", "verification", "root_cause", "cui_bono"]
    priority: Literal["critical", "high", "medium", "low"]
    question: str
    search_strategy: str
    entity: Optional[str]
    entities: Optional[List[str]]
    answered: bool
    answer: Optional[str]


class SuspiciousPattern(TypedDict):
    """A pattern that suggests something worth investigating"""
    pattern: str
    description: str
    entities: List[str]
    implication: str
    suspicion_level: Literal["critical", "high", "medium", "low"]


class PotentialConnection(TypedDict):
    """A potential hidden connection between entities"""
    type: Literal["shared_funding", "temporal_coincidence", "contradiction",
                  "suspicious_credentials", "network_cluster"]
    entities: List[str]
    connector: Optional[str]
    question: str
    suspicion_level: Literal["high", "medium", "low"]


class Hypothesis(TypedDict):
    """A hypothesis to test"""
    hypothesis: str
    evidence_for: List[str]
    evidence_against: List[str]
    to_verify: List[str]
    confidence: float


class TimelineEvent(TypedDict):
    """An event on the timeline"""
    date: str
    description: str
    sources: List[str]
    major_event: bool
    cause_identified: bool


class InvestigativeState(TypedDict):
    """Complete state for deep investigative analysis"""
    
    # User input
    query: str
    investigation_goal: str  # "why did X happen?", "who funds Y?", etc.
    cutoff_date: Optional[str]  # Only use info before this date
    
    # Discovery
    timeline: List[TimelineEvent]
    first_article_url: Optional[str]
    trigger_events: List[str]
    
    # Entities
    entities: Dict[str, InvestigationEntity]  # name -> entity
    entity_queue: List[str]  # entities to investigate next
    
    # Investigation tracking
    current_entity: Optional[str]
    attempted_strategies: List[str]
    
    # Strategic Intelligence (THE BRAIN)
    generated_questions: List[InvestigativeQuestion]
    potential_connections: List[PotentialConnection]
    investigation_hypotheses: List[Hypothesis]
    knowledge_gaps: List[Dict[str, any]]
    suspicious_patterns: List[SuspiciousPattern]
    current_questions: List[str]
    answered_questions: List[Dict[str, str]]
    
    # Findings
    causal_chains: List[CausalLink]
    funding_network: Dict[str, List[str]]  # entity -> funders
    relationships: Dict[str, List[str]]  # entity -> connected entities
    
    # Confidence tracking
    overall_confidence: float  # 0-1
    investigation_depth: int  # current iteration count
    max_depth: int  # stop at this depth (default: 5)
    
    # Output
    artifacts: List[Dict[str, any]]
    messages: Annotated[list, add_messages]
    
    # Control flow
    should_continue: bool


