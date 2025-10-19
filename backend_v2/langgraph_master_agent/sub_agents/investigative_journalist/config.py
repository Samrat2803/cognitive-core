"""
Configuration for Investigative Journalist Agent
"""

import os

# LLM Configuration
MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o")
TEMPERATURE = 0  # Always 0 for consistency

# Investigation Configuration
DEFAULT_MAX_ITERATIONS = 20
MAX_ITERATIONS_LIMIT = 100

# Search Configuration
SEARCH_DEPTH = "basic"  # Use basic for cost optimization
MAX_RESULTS_PER_SEARCH = 5
ARTICLES_TO_EXTRACT_PER_SEARCH = 2  # Extract top 2 articles

# Cost Constants (approximate)
COST_TAVILY_SEARCH = 0.01   # $0.01 per search
COST_TAVILY_EXTRACT = 0.05  # $0.05 per extract (fallback)
COST_GPT4O_INPUT = 0.0025   # $2.50 per 1M tokens (~1000 tokens per call)
COST_GPT4O_OUTPUT = 0.01    # $10 per 1M tokens (~500 tokens per call)

# Extraction Configuration
EXTRACTION_METHODS = ["jina_ai", "trafilatura", "beautifulsoup"]  # Try in order
MIN_CONTENT_LENGTH = 500  # Minimum characters for valid extraction
CACHE_EXTRACTIONS = True  # Cache extracted content

# Completion Criteria
MIN_ENTITIES_FOR_COMPLETION = 5
MIN_FACTS_FOR_COMPLETION = 10
FORCE_INITIAL_SEARCH = True  # Always perform at least 1 search

# Query Validation
QUERY_SIMILARITY_THRESHOLD = 0.7  # 70% similar = too similar

# Search Frequency (by iteration phase)
PHASE_1_END = 20   # Iterations 1-20: Search every iteration
PHASE_2_END = 60   # Iterations 21-60: Search every 2 iterations
PHASE_3_END = 100  # Iterations 61-100: Search every 5 iterations

# Artifact Configuration
ARTIFACT_DIR = "artifacts"
REPORT_FORMAT = "markdown"  # Output format for final report

# Evidence Repository
SAVE_TO_MONGODB = True  # Save evidence repository to MongoDB
AUTO_SAVE_FREQUENCY = 5  # Save every N iterations


