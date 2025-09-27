"""
Minimal FastAPI app for quick testing
"""

import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from minimal_agent import get_minimal_agent

# Initialize FastAPI app
app = FastAPI(
    title="Minimal Web Research Agent",
    description="A fast, minimal web research agent for testing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    """Request model for research queries"""
    query: str

class ResearchResponse(BaseModel):
    """Response model for research results"""
    success: bool
    query: str
    search_terms: list[str]
    sources_count: int
    final_answer: str
    sources: list[str]
    error: str = ""

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Minimal Web Research Agent API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_type": "minimal"
    }

@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Perform quick web research on a given query
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    if len(request.query) > 500:
        raise HTTPException(
            status_code=400, 
            detail="Query too long. Maximum length is 500 characters"
        )
    
    try:
        # Get the minimal agent
        agent = get_minimal_agent()
        
        # Perform research
        result = await agent.search_and_answer(request.query)
        
        return ResearchResponse(
            success=result["success"],
            query=result["query"],
            search_terms=result["search_terms"],
            sources_count=result["sources_count"],
            final_answer=result["final_answer"],
            sources=result["sources"],
            error=result.get("error", "")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "minimal_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
