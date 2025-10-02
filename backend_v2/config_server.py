"""
Configuration settings for the Political Analyst Backend Server
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for the backend server"""
    
    # API Keys
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    
    # LLM Settings
    DEFAULT_MODEL = "gpt-4o"
    TEMPERATURE = 0  # Always use 0 for consistency
    
    # Server Settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8501")
    MAX_QUERY_LENGTH = 2000
    
    # Artifact Settings
    ARTIFACT_DIR = "../artifacts"
    MAX_ARTIFACT_SIZE_MB = 10
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required API keys are present"""
        if not cls.TAVILY_API_KEY:
            print("❌ TAVILY_API_KEY is required")
            return False
        
        if not cls.OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY is required")
            return False
        
        return True
    
    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """Get configuration summary for debugging"""
        return {
            "tavily_configured": bool(cls.TAVILY_API_KEY),
            "openai_configured": bool(cls.OPENAI_API_KEY),
            "langsmith_configured": bool(cls.LANGSMITH_API_KEY),
            "langfuse_configured": bool(cls.LANGFUSE_PUBLIC_KEY and cls.LANGFUSE_SECRET_KEY),
            "default_model": cls.DEFAULT_MODEL,
            "temperature": cls.TEMPERATURE,
            "cors_origins": cls.CORS_ORIGINS.split(","),
            "artifact_dir": cls.ARTIFACT_DIR
        }

