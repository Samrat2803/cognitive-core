"""
Configuration for Live Political Monitor Agent
"""

import os

# LLM Configuration
MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
TEMPERATURE = 0  # Always 0 for consistency

# Default Keywords
DEFAULT_KEYWORDS = ["Bihar", "corruption", "India politics"]

# Cache Configuration
DEFAULT_CACHE_HOURS = 3
MIN_CACHE_HOURS = 1
MAX_CACHE_HOURS = 24

# Search Configuration
MAX_QUERIES_PER_REQUEST = 3  # Generate max 3 Tavily queries
TAVILY_MAX_RESULTS_PER_QUERY = 15
SEARCH_DEPTH = "basic"

# Relevance Filtering
MIN_RELEVANCE_SCORE = 30  # Minimum score to be considered relevant
KEYWORD_MATCH_WEIGHT = 20  # Points per keyword match
CRISIS_KEYWORD_WEIGHT = 10  # Points per crisis keyword match

# Crisis Keywords (boost urgency score)
CRISIS_KEYWORDS = [
    "breaking", "urgent", "just in", "developing", "alert",
    "war", "coup", "attack", "assassination", "bombing",
    "emergency", "crisis", "collapse", "resign", "resigns",
    "killed", "dies", "death", "strike", "strikes",
    "conflict", "violence", "protest", "riot", "raid",
    "arrest", "investigation", "scandal", "scam", "corruption"
]

# Explosiveness Scoring Weights (Total: 100 points)
SIGNAL_WEIGHTS = {
    "llm_explosiveness": 30,      # LLM rating (0-30)
    "frequency": 25,               # Article count (0-25)
    "source_diversity": 20,        # Unique sources (0-20)
    "urgency_keywords": 15,        # Crisis keywords (0-15)
    "recency_bonus": 10           # Fixed bonus (0-10)
}

# Classification Thresholds
CLASSIFICATION_THRESHOLDS = {
    "CRITICAL": 70,      # 70-100: Major crisis
    "EXPLOSIVE": 50,     # 50-69: Significant development
    "TRENDING": 35,      # 35-49: Notable event
    "EMERGING": 0        # 0-34: Minor story
}

# Output Configuration
MAX_TOPICS_RETURNED = 10
ARTIFACT_DIR = "artifacts"

# MongoDB Cache Collection
CACHE_COLLECTION = "explosive_topics_cache"

