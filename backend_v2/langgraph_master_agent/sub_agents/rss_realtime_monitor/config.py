"""
Configuration for RSS Realtime Monitor Agent

Following agent development guidelines:
- Temperature = 0 always
- Simple constants only
- No complex logic
"""

# ═══════════════════════════════════════════════════════════
# LLM SETTINGS (Following agent guidelines)
# ═══════════════════════════════════════════════════════════
MODEL = "gpt-4o-mini"
TEMPERATURE = 0  # Always 0 for deterministic results

# ═══════════════════════════════════════════════════════════
# RSS DATA SETTINGS (Fixed, not user-controlled)
# ═══════════════════════════════════════════════════════════
CACHE_WINDOW_HOURS = 48  # Fixed 48h window (NOT user-configurable)
MIN_ARTICLE_AGE_HOURS = 0
MAX_ARTICLE_AGE_HOURS = 48

# ═══════════════════════════════════════════════════════════
# KEYWORD FILTERING
# ═══════════════════════════════════════════════════════════
SEMANTIC_SEARCH_TOP_K = 200  # Max articles after semantic search
SEMANTIC_MIN_SIMILARITY = 0.25  # Minimum cosine similarity threshold
EXACT_MATCH_BOOST = 0.1  # Boost score for exact keyword matches

# ═══════════════════════════════════════════════════════════
# CLUSTERING SETTINGS
# ═══════════════════════════════════════════════════════════
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Sentence transformers
DBSCAN_EPS = 0.5  # Distance threshold for clustering
DBSCAN_MIN_SAMPLES = 2  # Min articles per cluster

# ═══════════════════════════════════════════════════════════
# SCORING SETTINGS (Velocity used for SORTING, not filtering!)
# ═══════════════════════════════════════════════════════════
VELOCITY_WEIGHT = 40  # Out of 100
RECENCY_WEIGHT = 20
DIVERSITY_WEIGHT = 20
GEOGRAPHIC_WEIGHT = 10
RELEVANCE_WEIGHT = 10

# Threshold for "ready for Tavily" flag (NOT a filter!)
TAVILY_READINESS_THRESHOLD = 70  # Score > 70 → ready_for_tavily: true

# ═══════════════════════════════════════════════════════════
# OUTPUT SETTINGS
# ═══════════════════════════════════════════════════════════
DEFAULT_MAX_TOPICS = 10
MAX_HEADLINES_PER_TOPIC = 5
MAX_ENTITIES_PER_TYPE = 10  # Max entities to extract per type

# ═══════════════════════════════════════════════════════════
# ENTITY EXTRACTION
# ═══════════════════════════════════════════════════════════
ENTITY_TYPES = ["people", "organizations", "locations", "companies"]

