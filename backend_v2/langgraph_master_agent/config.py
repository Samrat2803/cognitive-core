"""
Configuration for Master Agent
"""

import os
from dotenv import load_dotenv

load_dotenv()


class MasterAgentConfig:
    """Configuration settings for master agent"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # LLM Settings
    MODEL_NAME = "gpt-4o"
    TEMPERATURE = 0  # Always 0 as per user rules
    MAX_TOKENS = 4000
    
    # Agent Behavior
    MAX_TOOL_ITERATIONS = 3  # Maximum loops before forcing response
    MAX_CONVERSATION_HISTORY = 10  # Keep last N messages
    
    # Tavily Settings
    TAVILY_SEARCH_DEPTH = "basic"  # or "advanced"
    TAVILY_MAX_RESULTS = 8
    TAVILY_INCLUDE_ANSWER = True
    
    # LangFuse Observability
    LANGFUSE_HOST = "http://localhost:3761"
    LANGFUSE_ENABLED = True
    
    # Tool/Sub-agent Registry
    AVAILABLE_TOOLS = {
        "tavily_search": {
            "description": "Real-time web search for current political information",
            "use_for": ["news", "current events", "factual lookups", "recent updates"]
        },
        "tavily_extract": {
            "description": "Extract full content from specific URLs in markdown format",
            "use_for": ["article content", "deep reading", "detailed analysis"]
        },
        "tavily_crawl": {
            "description": "Deep crawl of websites for comprehensive data collection",
            "use_for": ["website analysis", "multi-page content", "systematic collection"]
        },
        "sentiment_analysis_agent": {
            "description": """
            Comprehensive geopolitical sentiment analysis across multiple countries.
            Features:
            - Multi-country sentiment scoring (-1 to +1)
            - Bias detection (7 types: selection, framing, language, source, citation, temporal, geographic)
            - Source credibility assessment
            - Multi-iteration refinement with bias correction
            - Detailed reasoning and citations
            
            Use for:
            - "Analyze sentiment on [topic]"
            - "How does [country] view [issue]"
            - "Compare international perspectives on [topic]"
            - "Give me unbiased analysis of [political event]"
            """,
            "use_for": ["sentiment analysis", "bias detection", "multi-country analysis", "credibility assessment"]
        },
        "media_bias_detector_agent": {
            "description": """
            Multi-source media bias analysis comparing how different news outlets cover the same topic.
            Features:
            - Political lean classification (-1.0 far left to +1.0 far right)
            - Loaded language detection (8 categories: emotionally_charged, sensationalist, fear_based, etc.)
            - Framing analysis (conflict, human interest, economic, morality, responsibility, etc.)
            - Bias technique identification (spin, selective quoting, labeling, omission, etc.)
            - Comparison matrix across sources
            - Consensus vs divergence analysis
            - Interactive visualizations (bias spectrum, heatmap, framing chart)
            
            Use for:
            - "Compare media bias on [topic]"
            - "How do different news sources cover [event]"
            - "Analyze CNN vs Fox News coverage of [issue]"
            - "Show me bias spectrum for [topic]"
            - "What's the media framing of [event]"
            - "Detect loaded language in [topic] reporting"
            """,
            "use_for": ["media bias", "source comparison", "framing analysis", "loaded language", "political lean", "news coverage"]
        }
    }
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment")
        if not cls.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY not found in environment")
        
        return True


# Validate on import
MasterAgentConfig.validate_config()

