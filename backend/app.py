"""
FastAPI backend server for the Web Research Agent
"""

import asyncio
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from research_agent import WebResearchAgent
from config import Config

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Web Research Agent API",
    description="A sophisticated web research agent using LangGraph and Tavily",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[WebResearchAgent] = None

class ResearchRequest(BaseModel):
    """Request model for research queries"""
    query: str
    llm_provider: Optional[str] = "openai"
    model: Optional[str] = None

class ResearchResponse(BaseModel):
    """Response model for research results"""
    success: bool
    query: str
    search_terms: list[str]
    sources_count: int
    final_answer: str
    sources: list[str]
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the research agent on startup"""
    global agent
    
    if not Config.validate_config():
        raise RuntimeError("Invalid configuration. Please check your API keys.")
    
    llm_config = Config.get_llm_config()
    agent = WebResearchAgent(
        llm_provider=llm_config["provider"],
        model=llm_config["model"]
    )
    print("🚀 Web Research Agent initialized successfully!")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Web Research Agent API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None
    }

@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Perform web research on a given query
    
    Args:
        request: Research request containing query and optional parameters
        
    Returns:
        ResearchResponse: Comprehensive research results
    """
    if not agent:
        raise HTTPException(status_code=500, detail="Research agent not initialized")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    if len(request.query) > Config.MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"Query too long. Maximum length is {Config.MAX_QUERY_LENGTH} characters"
        )
    
    try:
        # Use custom agent if different provider/model specified
        if request.llm_provider != Config.DEFAULT_LLM_PROVIDER or request.model:
            custom_agent = WebResearchAgent(
                llm_provider=request.llm_provider,
                model=request.model or Config.get_llm_config()["model"]
            )
            result = await custom_agent.research(request.query)
        else:
            result = await agent.research(request.query)
        
        if result.get("error"):
            return ResearchResponse(
                success=False,
                query=request.query,
                search_terms=result.get("search_terms", []),
                sources_count=len(result.get("sources", [])),
                final_answer="",
                sources=result.get("sources", []),
                error=result["error"]
            )
        
        return ResearchResponse(
            success=True,
            query=request.query,
            search_terms=result.get("search_terms", []),
            sources_count=len(result.get("sources", [])),
            final_answer=result.get("final_answer", ""),
            sources=result.get("sources", [])[:Config.MAX_SOURCES_DISPLAY],
            error=None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

@app.get("/config")
async def get_config():
    """Get current configuration (without sensitive data)"""
    return {
        "llm_provider": Config.DEFAULT_LLM_PROVIDER,
        "max_query_length": Config.MAX_QUERY_LENGTH,
        "max_sources_display": Config.MAX_SOURCES_DISPLAY,
        "search_depth": Config.SEARCH_DEPTH
    }

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
