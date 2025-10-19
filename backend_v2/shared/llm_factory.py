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
        model: str = "gpt-5",
        temperature: float = None,
        max_tokens: int = 4000,
        reasoning_effort: str = "high",
        verbosity: str = "medium"
    ) -> ChatOpenAI:
        """
        Create LLM instance (supports GPT-5 with enhanced reasoning)
        
        Args:
            model: OpenAI model name (gpt-5, gpt-5-mini, gpt-5-nano, or gpt-4o)
            temperature: Temperature (ignored for GPT-5, only for GPT-4)
            max_tokens: Max response tokens (max_completion_tokens for GPT-5)
            reasoning_effort: GPT-5 reasoning level (minimal/low/medium/high)
            verbosity: GPT-5 response verbosity (low/medium/high)
        
        Returns:
            Configured ChatOpenAI instance
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        # Base configuration
        config = {
            "openai_api_key": api_key,
            "model": model
        }
        
        # GPT-5 specific configuration
        if model.startswith("gpt-5"):
            # GPT-5 uses different endpoint (/v1/responses) and nested parameters
            config["max_completion_tokens"] = max_tokens
            # Parameters must be nested for GPT-5 Responses API
            config["model_kwargs"] = {
                "reasoning": {
                    "effort": reasoning_effort
                },
                "text": {
                    "verbosity": verbosity
                }
            }
            # GPT-5 does NOT support temperature parameter (only default 1.0)
        else:
            # GPT-4 and earlier models
            config["max_tokens"] = max_tokens
            if temperature is not None:
                config["temperature"] = temperature
        
        return ChatOpenAI(**config)

