"""
Configuration for Sentiment Analyzer Agent
"""

import os

# LLM Configuration
MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
TEMPERATURE = 0  # Always 0 for consistency

# Search Configuration
DEFAULT_COUNTRIES = ["US", "UK", "China", "India", "Russia"]  # More diverse geopolitical coverage
MAX_COUNTRIES = 10
DEFAULT_TIME_RANGE_DAYS = 7
SEARCH_DEPTH = "basic"
MAX_RESULTS_PER_COUNTRY = 5

# Sentiment Scoring
SENTIMENT_THRESHOLD_POSITIVE = 0.3
SENTIMENT_THRESHOLD_NEGATIVE = -0.3

# Bias Types to Detect
BIAS_TYPES = [
    "political_lean",      # Left/right political bias
    "source_bias",         # Government vs independent
    "temporal_bias",       # Recency bias
    "selection_bias",      # Cherry-picking facts
    "framing_bias",        # How story is presented
    "confirmation_bias",   # Supporting pre-existing views
    "cultural_bias"        # Cultural perspective
]

# Visualization
ARTIFACT_DIR = "artifacts"
MAP_COLOR_SCALE = "RdYlGn"  # Red-Yellow-Green for sentiment

