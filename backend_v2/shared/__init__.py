"""
Shared RSS Tools

Reusable tools for RSS data collection, storage, and embedding.
"""

from shared.rss_sources import RSSSourceManager
from shared.rss_collector import RSSCollector

# Optional: RSS Embedder (requires sentence-transformers)
try:
    from shared.rss_embedder import RSSEmbedder
    __all__ = ["RSSSourceManager", "RSSCollector", "RSSEmbedder"]
except ImportError:
    # sentence-transformers not installed, skip embedder
    __all__ = ["RSSSourceManager", "RSSCollector"]
    print("⚠️  RSSEmbedder not available (sentence-transformers not installed)")

