"""
Chat Router for conversational endpoints
Handles query parsing and analysis confirmation
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from langchain_core.messages import HumanMessage, SystemMessage
from research_agent import WebResearchAgent
from config import Config
from models.api_schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatConfirmAnalysisRequest,
    ChatConfirmAnalysisResponse,
    ParsedIntent,
    ErrorResponse
)

# Router setup
router = APIRouter(prefix="/api/chat", tags=["chat"])

# Global agent instance (will be initialized on first use)
_chat_agent: Optional[WebResearchAgent] = None

def get_chat_agent() -> WebResearchAgent:
    """Get or initialize the chat agent"""
    global _chat_agent
    if _chat_agent is None:
        try:
            llm_config = Config.get_llm_config()
            _chat_agent = WebResearchAgent(
                llm_provider=llm_config["provider"],
                model=llm_config["model"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize chat agent: {str(e)}")
    return _chat_agent


@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(request: ChatMessageRequest):
    """
    Process chat message and parse intent for geopolitical analysis
    
    Returns either:
    - Parsed intent with analysis_id for confirmation
    - Direct response with suggestions if parsing fails
    """
    try:
        agent = get_chat_agent()
        
        # Use LLM to parse the intent (temperature = 0 for consistency)
        intent_result = await _parse_query_intent(agent, request.message)
        
        if intent_result["success"]:
            # Successfully parsed - return structured intent
            analysis_id = str(uuid.uuid4())
            
            return ChatMessageResponse(
                success=True,
                response_type="query_parsed",
                parsed_intent=ParsedIntent(**intent_result["parsed_intent"]),
                confirmation=intent_result["confirmation"],
                analysis_id=analysis_id
            )
        else:
            # Failed to parse - return suggestions
            return ChatMessageResponse(
                success=True,
                response_type="direct_response",
                message=intent_result["message"],
                suggestions=intent_result.get("suggestions", _get_default_suggestions())
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.post("/confirm-analysis", response_model=ChatConfirmAnalysisResponse)
async def confirm_analysis(request: ChatConfirmAnalysisRequest):
    """
    Confirm analysis execution with optional modifications
    Queues the analysis for background processing
    """
    try:
        if not request.confirmed:
            raise HTTPException(
                status_code=400,
                detail="Analysis was not confirmed"
            )
        
        # Import here to avoid circular imports
        from services.analysis_service import analysis_service
        from websocket_manager import websocket_manager
        
        # Create default parameters (these would come from the original parsed intent in a full implementation)
        parameters = {
            "countries": ["United States", "Iran", "Israel"],  # Default countries
            "days": 7,
            "results_per_country": 20,
            "include_bias_analysis": True
        }
        
        # Apply any modifications
        if request.modifications:
            if "countries" in request.modifications:
                parameters["countries"] = request.modifications["countries"]
            if "days" in request.modifications:
                parameters["days"] = request.modifications["days"]
        
        # Create analysis task
        # For MVP, we'll use a generic query since we don't have the original parsed intent stored
        query_text = f"Geopolitical sentiment analysis for {', '.join(parameters['countries'])}"
        
        analysis_id = await analysis_service.create_analysis(
            query_text=query_text,
            parameters=parameters,
            session_id=f"chat_session_{uuid.uuid4().hex[:8]}"
        )
        
        # Start background processing
        await analysis_service.start_analysis(analysis_id, websocket_manager)
        
        # Register for WebSocket updates
        websocket_session = f"ws_{analysis_id}"
        websocket_manager.register_analysis(websocket_session, analysis_id)
        
        return ChatConfirmAnalysisResponse(
            success=True,
            analysis_id=analysis_id,
            status="queued",
            estimated_completion=datetime.utcnow() + timedelta(minutes=5),
            websocket_session=websocket_session
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to confirm analysis: {str(e)}"
        )


async def _parse_query_intent(agent: WebResearchAgent, message: str) -> Dict[str, Any]:
    """
    Parse user query to extract geopolitical analysis intent
    Uses the research agent's LLM with temperature=0 for consistent parsing
    """
    
    # Intent parsing prompt
    parsing_prompt = f"""
    Analyze the following user message to determine if it's requesting a geopolitical sentiment analysis.
    
    User message: "{message}"
    
    If this is a request for geopolitical sentiment analysis:
    1. Extract the main topic/subject
    2. Identify any countries mentioned
    3. Determine analysis parameters (timeframe, etc.)
    4. Return structured data
    
    If this is NOT a clear geopolitical analysis request:
    1. Return a helpful response with suggestions
    
    Respond in JSON format:
    {{
        "is_analysis_request": true/false,
        "topic": "extracted topic" (if applicable),
        "countries": ["Country1", "Country2"] (if applicable),
        "timeframe_days": 7 (default),
        "confidence": 0.0-1.0
    }}
    """
    
    try:
        messages = [
            SystemMessage(content="You are a geopolitical analysis assistant that parses user queries for sentiment analysis requests."),
            HumanMessage(content=parsing_prompt)
        ]
        
        response = agent.llm.invoke(messages)
        response_text = response.content.strip()
        
        # Try to parse JSON response
        import json
        try:
            parsed_response = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback parsing
            parsed_response = _fallback_intent_parsing(message)
        
        if parsed_response.get("is_analysis_request", False) and parsed_response.get("confidence", 0) > 0.6:
            # High confidence parsing
            countries = parsed_response.get("countries", [])
            topic = parsed_response.get("topic", "geopolitical sentiment")
            timeframe = parsed_response.get("timeframe_days", 7)
            
            # Ensure we have at least one country
            if not countries:
                countries = ["United States"]  # Default fallback
            
            return {
                "success": True,
                "parsed_intent": {
                    "action": "sentiment_analysis",
                    "topic": topic,
                    "countries": countries,
                    "parameters": {
                        "days": timeframe,
                        "results_per_country": 20,
                        "include_bias_analysis": True
                    }
                },
                "confirmation": f"I'll analyze {topic} sentiment across {', '.join(countries)} using the last {timeframe} days of data. Proceed?"
            }
        else:
            # Low confidence or not analysis request
            return {
                "success": False,
                "message": "I can help with geopolitical sentiment analysis. Try asking about specific topics and countries.",
                "suggestions": _get_contextual_suggestions(message)
            }
            
    except Exception as e:
        print(f"❌ Intent parsing error: {e}")
        return {
            "success": False,
            "message": "I can help with geopolitical sentiment analysis. Try asking about specific topics and countries.",
            "suggestions": _get_default_suggestions()
        }


def _fallback_intent_parsing(message: str) -> Dict[str, Any]:
    """
    Fallback intent parsing using simple keyword matching
    """
    message_lower = message.lower()
    
    # Check for analysis keywords
    analysis_keywords = ["sentiment", "analyze", "analysis", "opinion", "view", "position"]
    has_analysis_keyword = any(keyword in message_lower for keyword in analysis_keywords)
    
    # Check for common countries
    country_keywords = {
        "us": "United States", "usa": "United States", "america": "United States",
        "iran": "Iran", "israel": "Israel", "china": "China", "russia": "Russia",
        "uk": "United Kingdom", "france": "France", "germany": "Germany"
    }
    
    found_countries = []
    for keyword, country in country_keywords.items():
        if keyword in message_lower:
            found_countries.append(country)
    
    # Check for common topics
    topics = ["hamas", "ukraine", "gaza", "syria", "taiwan", "trade", "nuclear"]
    found_topic = None
    for topic in topics:
        if topic in message_lower:
            found_topic = topic
            break
    
    confidence = 0.0
    if has_analysis_keyword and (found_countries or found_topic):
        confidence = 0.8
    elif has_analysis_keyword or found_countries:
        confidence = 0.4
    
    return {
        "is_analysis_request": confidence > 0.6,
        "topic": found_topic or "geopolitical sentiment",
        "countries": found_countries or ["United States"],
        "timeframe_days": 7,
        "confidence": confidence
    }


def _get_contextual_suggestions(message: str) -> list[str]:
    """Generate contextual suggestions based on the message"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["ukraine", "russia", "war"]):
        return [
            "Analyze Ukraine conflict sentiment",
            "Compare US and European views on Ukraine",
            "Russia-Ukraine sentiment in NATO countries"
        ]
    elif any(word in message_lower for word in ["israel", "palestine", "gaza", "hamas"]):
        return [
            "Analyze Hamas sentiment across US, Iran, and Israel",
            "Israeli-Palestinian conflict sentiment analysis",
            "Compare Middle East views on Gaza situation"
        ]
    elif any(word in message_lower for word in ["china", "taiwan", "trade"]):
        return [
            "Analyze China-Taiwan sentiment",
            "US-China trade war sentiment",
            "Asian countries' views on China"
        ]
    else:
        return _get_default_suggestions()


def _get_default_suggestions() -> list[str]:
    """Get default suggestions for geopolitical analysis"""
    return [
        "Analyze Hamas sentiment across US, Iran, and Israel",
        "Compare European countries' views on Ukraine",
        "US-China trade relationship sentiment analysis",
        "Middle East conflict sentiment in Arab countries"
    ]


if __name__ == "__main__":
    # Test chat router functionality
    import asyncio
    
    async def test_chat_router():
        print("🧪 Testing Chat Router...")
        
        # Test intent parsing
        agent = WebResearchAgent(llm_provider="openai", model="gpt-4o-mini")
        
        test_messages = [
            "Analyze Hamas sentiment in US, Iran, and Israel",
            "What's the weather like?",
            "Compare views on Ukraine conflict",
            "Hello, how are you?"
        ]
        
        for msg in test_messages:
            result = await _parse_query_intent(agent, msg)
            print(f"Message: {msg}")
            print(f"Result: {result['success']}")
            print("---")
        
        print("✅ Chat router test completed!")
    
    # asyncio.run(test_chat_router())
