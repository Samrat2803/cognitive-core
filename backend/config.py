"""
Configuration settings for the Web Research Agent
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for the research agent"""
    
    # API Keys
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # LLM Settings
    DEFAULT_LLM_PROVIDER = "openai"  # or "anthropic"
    DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
    DEFAULT_ANTHROPIC_MODEL = "claude-3-haiku-20240307"
    TEMPERATURE = 0  # Always use 0 for research tasks
    
    # Search Settings
    MAX_SEARCH_RESULTS_PER_TERM = 5
    MAX_TOTAL_RESULTS = 15
    SEARCH_DEPTH = "advanced"  # "basic" or "advanced"
    
    # Analysis Settings
    MAX_CONTENT_LENGTH = 500  # Characters per result for analysis
    MAX_SOURCES_DISPLAY = 10
    
    # UI Settings
    MAX_QUERY_LENGTH = 500
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Get LLM configuration based on available API keys"""
        if cls.OPENAI_API_KEY:
            return {
                "provider": "openai",
                "model": cls.DEFAULT_OPENAI_MODEL,
                "api_key": cls.OPENAI_API_KEY
            }
        elif cls.ANTHROPIC_API_KEY:
            return {
                "provider": "anthropic", 
                "model": cls.DEFAULT_ANTHROPIC_MODEL,
                "api_key": cls.ANTHROPIC_API_KEY
            }
        else:
            raise ValueError("No LLM API key found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        if not cls.TAVILY_API_KEY:
            print("❌ TAVILY_API_KEY is required")
            return False
        
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            print("❌ At least one LLM API key is required (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
            return False
        
        return True
