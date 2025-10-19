"""
Configuration for Cognitive Crawler Agent
Generic web crawler with RAG chat capabilities
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ====== LLM Configuration ======
MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
TEMPERATURE = 0  # Always 0 per user rules

# ====== API Keys ======
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ====== MongoDB Configuration ======
MONGODB_URI = os.getenv("MONGODB_CONNECTION_STRING")
DATABASE_NAME = os.getenv("DATABASE_NAME", "political_analyst_db")  # Use same DB as main app

# MongoDB Collections (keeping old names for backwards compatibility)
PORTALS_COLLECTION = "tender_portals"
TENDERS_COLLECTION = "tenders"
VECTORS_COLLECTION = "tender_vectors"
CRAWLER_SESSIONS_COLLECTION = "crawler_sessions"
CRAWLED_PAGES_COLLECTION = "tenders"  # Alias

# ====== RAG Configuration ======
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
TOP_K_RESULTS = 10
MIN_SIMILARITY_SCORE = 0.5
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks

# ====== Tavily Configuration ======
TAVILY_SEARCH_DEPTH = "advanced"
MAX_SEARCH_RESULTS = 5

# ====== Crawl4AI Configuration ======
CRAWL_TIMEOUT = 30  # seconds
DEFAULT_MAX_PAGES = 20  # Default, user can override
DEFAULT_MAX_DEPTH = 2   # Default, user can override
ENABLE_JS = True  # For dynamic content (SPAs, etc.)

# ====== Discovery ======
MAX_PAGES_TO_MAP = 10  # Max URLs from Tavily map
MAX_PAGES_TO_CRAWL = 20  # Max pages to actually crawl in a session

# ====== Artifact Configuration ======
ARTIFACT_DIR = "artifacts"
EXAMPLES_DIR = "examples"

# ====== Content Processing ======
MIN_CONTENT_LENGTH = 500  # Minimum characters to consider valid content
SUPPORTED_FILE_TYPES = [".html", ".htm", ".txt", ".md", ".pdf", ".json"]

