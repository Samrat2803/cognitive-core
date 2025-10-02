"""
API Schemas for MVP endpoints matching the API contracts
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field


# Chat endpoints schemas
class ChatMessageRequest(BaseModel):
    """Request schema for /api/chat/message"""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None


class ParsedIntent(BaseModel):
    """Parsed intent structure"""
    action: str = Field(..., description="Type of analysis requested")
    topic: str = Field(..., description="Main subject of analysis")
    countries: List[str] = Field(default_factory=list, description="Countries to analyze")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Analysis parameters")


class ChatMessageResponse(BaseModel):
    """Response schema for /api/chat/message"""
    success: bool
    response_type: Literal["query_parsed", "direct_response"]
    # For query_parsed responses
    parsed_intent: Optional[ParsedIntent] = None
    confirmation: Optional[str] = None
    analysis_id: Optional[str] = None
    # For direct_response responses
    message: Optional[str] = None
    suggestions: Optional[List[str]] = None


class ChatConfirmAnalysisRequest(BaseModel):
    """Request schema for /api/chat/confirm-analysis"""
    analysis_id: str = Field(..., min_length=1)
    confirmed: bool
    modifications: Optional[Dict[str, Any]] = None


class ChatConfirmAnalysisResponse(BaseModel):
    """Response schema for /api/chat/confirm-analysis"""
    success: bool
    analysis_id: str
    status: str
    estimated_completion: Optional[datetime] = None
    websocket_session: str


# Analysis endpoints schemas
class AnalysisExecuteRequest(BaseModel):
    """Request schema for /api/analysis/execute"""
    query_text: str = Field(..., min_length=1, max_length=1000)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    session_id: str = Field(..., min_length=1)


class AnalysisExecuteResponse(BaseModel):
    """Response schema for /api/analysis/execute"""
    success: bool
    analysis_id: str
    status: str
    estimated_completion: Optional[datetime] = None
    websocket_session: str
    created_at: datetime


class AnalysisProgress(BaseModel):
    """Progress information for analysis"""
    current_step: str
    completion_percentage: int = Field(ge=0, le=100)
    processed_countries: List[str] = Field(default_factory=list)
    remaining_countries: List[str] = Field(default_factory=list)
    articles_processed: int = Field(default=0, ge=0)
    total_articles: int = Field(default=0, ge=0)


class CountryResult(BaseModel):
    """Results for a specific country"""
    country: str
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    articles_count: int = Field(ge=0)
    dominant_sentiment: str
    key_themes: List[str] = Field(default_factory=list)
    bias_analysis: Dict[str, Any] = Field(default_factory=dict)


class AnalysisSummary(BaseModel):
    """Summary of analysis results"""
    overall_sentiment: float = Field(ge=-1.0, le=1.0)
    countries_analyzed: int = Field(ge=0)
    total_articles: int = Field(ge=0)
    analysis_confidence: float = Field(ge=0.0, le=1.0)
    bias_detected: bool
    completion_time_ms: int = Field(ge=0)


class AnalysisResults(BaseModel):
    """Complete analysis results"""
    summary: AnalysisSummary
    country_results: List[CountryResult] = Field(default_factory=list)


class AnalysisGetResponse(BaseModel):
    """Response schema for /api/analysis/{analysis_id}"""
    success: bool
    analysis_id: str
    status: Literal["processing", "completed", "failed"]
    # For processing status
    progress: Optional[AnalysisProgress] = None
    estimated_completion: Optional[datetime] = None
    # For completed status
    query: Optional[Dict[str, Any]] = None
    results: Optional[AnalysisResults] = None
    # For error cases
    error: Optional[Dict[str, Any]] = None


# WebSocket message schemas
class WebSocketMessage(BaseModel):
    """Base WebSocket message"""
    type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PingMessage(WebSocketMessage):
    """Server ping message"""
    type: Literal["ping"] = "ping"


class PongMessage(WebSocketMessage):
    """Client pong response"""
    type: Literal["pong"] = "pong"


class ProgressMessage(WebSocketMessage):
    """Progress update message"""
    type: Literal["analysis_progress"] = "analysis_progress"
    analysis_id: str
    progress: AnalysisProgress


class CompletedMessage(WebSocketMessage):
    """Analysis completed message"""
    type: Literal["analysis_completed"] = "analysis_completed"
    analysis_id: str
    results: AnalysisResults


class ErrorMessage(WebSocketMessage):
    """Error message"""
    type: Literal["analysis_error"] = "analysis_error"
    analysis_id: Optional[str] = None
    error: Dict[str, Any]


# Error response schemas
class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    code: str


if __name__ == "__main__":
    # Test schema creation
    print("✅ Testing API schemas...")
    
    # Test chat message request
    chat_req = ChatMessageRequest(
        message="Analyze Hamas sentiment in US, Iran, and Israel",
        session_id="test_session"
    )
    print(f"Chat request: {chat_req.dict()}")
    
    # Test analysis execute request
    analysis_req = AnalysisExecuteRequest(
        query_text="Hamas sentiment analysis",
        parameters={"countries": ["United States", "Iran"], "days": 7},
        session_id="test_session"
    )
    print(f"Analysis request: {analysis_req.dict()}")
    
    # Test WebSocket messages
    ping = PingMessage()
    progress = ProgressMessage(
        analysis_id="test_123",
        progress=AnalysisProgress(
            current_step="analyzing_articles",
            completion_percentage=45
        )
    )
    print(f"WebSocket ping: {ping.dict()}")
    print(f"WebSocket progress: {progress.dict()}")
    
    print("✅ All schemas created successfully!")
