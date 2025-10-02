"""
Shared Observability Setup for LangFuse
"""

import os
from typing import Optional

try:
    from langfuse import Langfuse
    from langfuse.decorators import observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("⚠️  LangFuse not installed. Observability disabled.")
    
    # Dummy decorator
    def observe(name: Optional[str] = None):
        def decorator(func):
            return func
        return decorator


class ObservabilityManager:
    """Manages observability setup for all agents"""
    
    def __init__(self, host: str = "http://localhost:3761"):
        self.host = host
        self.enabled = LANGFUSE_AVAILABLE
        
        if self.enabled:
            print(f"✅ LangFuse observability enabled: {host}")
        else:
            print("⚠️  LangFuse observability disabled")
    
    @staticmethod
    def get_observe_decorator():
        """Get the observe decorator (works even if LangFuse not installed)"""
        return observe

