"""MongoDB document models for queries, results, and analytics"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
from .base_model import BaseDocument


class QueryOptions(BaseModel):
    """Query execution options"""
    max_results: int = Field(default=10, ge=1, le=20)
    search_depth: Literal["basic", "advanced"] = "advanced"
    export_format: str = "json"


class QueryDocument(BaseDocument):
    """Document model for user queries"""
    query_id: str = Field(..., description="External UUID for API reference")
    query_text: str = Field(..., min_length=1, max_length=1000)
    user_session: Optional[str] = Field(None, description="Optional session tracking")
    status: Literal["processing", "completed", "failed"] = "processing"
    options: QueryOptions = Field(default_factory=QueryOptions)
    
    # Timing fields
    processing_started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    
    # Error tracking
    error_message: Optional[str] = None
    retry_count: int = 0

    @validator("processing_time_ms")
    def validate_processing_time(cls, v, values):
        if v is not None and v < 0:
            raise ValueError("Processing time cannot be negative")
        return v

    def mark_processing_started(self):
        """Mark query as processing started"""
        self.processing_started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_completed(self, processing_time_ms: int):
        """Mark query as completed"""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.processing_time_ms = processing_time_ms
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error_message: str):
        """Mark query as failed"""
        self.status = "failed"
        self.error_message = error_message
        self.updated_at = datetime.utcnow()


class SourceDocument(BaseModel):
    """Individual source information"""
    url: str
    title: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    content_snippet: Optional[str] = None


class AgentWorkflowStep(BaseModel):
    """Individual agent workflow step"""
    step_name: str
    duration_ms: int
    output_summary: str
    agent_type: str


class ResultDocument(BaseDocument):
    """Document model for research results"""
    query_id: str = Field(..., description="Links to QueryDocument")
    final_answer: str = Field(..., description="Formatted research response")
    search_terms: List[str] = Field(default_factory=list)
    sources: List[SourceDocument] = Field(default_factory=list)
    
    # Agent workflow tracking
    agent_workflow: List[AgentWorkflowStep] = Field(default_factory=list)
    
    # Result metadata
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    total_sources_found: int = 0
    unique_domains: int = 0

    @validator("sources")
    def validate_sources(cls, v):
        if len(v) > 50:  # Reasonable limit
            raise ValueError("Too many sources")
        return v


class AnalyticsDocument(BaseDocument):
    """Document model for daily analytics"""
    date: datetime = Field(..., description="Date for analytics (daily aggregation)")
    
    # Query statistics
    total_queries: int = 0
    completed_queries: int = 0
    failed_queries: int = 0
    
    # Performance metrics
    avg_processing_time_ms: float = 0.0
    min_processing_time_ms: int = 0
    max_processing_time_ms: int = 0
    
    # Content analysis
    popular_topics: List[str] = Field(default_factory=list)
    unique_sessions: int = 0
    
    # Error tracking
    common_errors: Dict[str, int] = Field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.total_queries == 0:
            return 0.0
        return (self.completed_queries / self.total_queries) * 100
