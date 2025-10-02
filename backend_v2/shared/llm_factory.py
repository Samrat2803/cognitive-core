"""
LLM Factory for consistent LLM initialization across agents
"""

import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMFactory:
    """Factory for creating LLM instances with consistent settings"""
    
    @staticmethod
    def create_llm(
        model: str = "gpt-4o",
        temperature: float = 0,
        max_tokens: int = 4000
    ) -> ChatOpenAI:
        """
        Create LLM instance
        
        Args:
            model: OpenAI model name
            temperature: Always 0 (per user rules)
            max_tokens: Max response tokens
        
        Returns:
            Configured ChatOpenAI instance
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        return ChatOpenAI(
            openai_api_key=api_key,
            model=model,
            temperature=temperature,  # Always 0
            max_tokens=max_tokens
        )

