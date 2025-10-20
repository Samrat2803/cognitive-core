"""
On-Demand Embedding Creator for RSS Articles

NOW USES UNIFIED VECTOR STORE (tender_vectors) with OpenAI embeddings
for compatibility with Cognitive Crawler and Investigative Journalist.

Usage:
    from shared.rss_embedder import RSSEmbedder
    
    embedder = RSSEmbedder()
    
    # Store RSS articles in unified vector store
    await embedder.store_articles(article_urls)
    
    # Semantic search across ALL sources (RSS + Crawler + Journalist)
    results = await embedder.semantic_search(query, top_k=10)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../langgraph_master_agent/sub_agents/cognitive_crawler/tools'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../langgraph_master_agent/sub_agents/cognitive_crawler'))

from pymongo import MongoClient
from typing import List, Dict, Optional
from datetime import datetime, timezone
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RSSEmbedder:
    """
    Creates and stores RSS article embeddings in UNIFIED vector store
    
    Philosophy: All sources (RSS, Crawler, Journalist) → ONE vector store
    
    Benefits:
    - Cross-source RAG (chat with all data)
    - Consistent embedding model (OpenAI)
    - Single source of truth
    """
    
    def __init__(self):
        """Initialize with unified vector store (TenderMongoDBHandler)"""
        try:
            from mongodb_handler import TenderMongoDBHandler
            self.db_handler = TenderMongoDBHandler()
            print(f"✓ RSS Embedder initialized with UNIFIED vector store")
            print(f"   Database: {self.db_handler.db.name}")
            print(f"   Collection: tender_vectors (shared with Crawler + Journalist)")
        except ImportError as e:
            print(f"⚠️  Could not import TenderMongoDBHandler: {e}")
            print(f"   RSS embeddings will not work")
            raise
        
        # Also connect to rss_articles for fetching content
        mongo_uri = os.getenv("MONGODB_URI") or os.getenv("MONGODB_CONNECTION_STRING")
        database_name = os.getenv("DATABASE_NAME", "political_analyst_db")
        
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database_name]
        self.articles_collection = self.db["rss_articles"]
    
    async def store_articles(self, article_urls: List[str]) -> Dict[str, any]:
        """
        Store RSS articles in unified vector store
        
        Args:
            article_urls: List of article URLs to embed and store
            
        Returns:
            {
                "stored": int,
                "skipped": int (already existed),
                "failed": int
            }
        """
        print(f"\n{'─'*80}")
        print(f"📰 RSS → UNIFIED VECTOR STORE")
        print(f"{'─'*80}")
        print(f"   Processing {len(article_urls)} articles...")
        
        # Fetch articles from rss_articles collection
        articles = list(self.articles_collection.find({"url": {"$in": article_urls}}))
        
        if not articles:
            print(f"   ⚠️  No articles found in rss_articles collection")
            return {"stored": 0, "skipped": 0, "failed": 0}
        
        print(f"   ✅ Found {len(articles)} articles in rss_articles")
        
        # Prepare documents for unified vector store
        documents = []
        for article in articles:
            url = article.get("url", "")
            title = article.get("title", "Untitled")
            content = article.get("content") or article.get("description", "")
            
            if not content or len(content) < 100:
                print(f"   ⚠️  Skipping {url[:50]}... (no content)")
                continue
            
            # Generate unique doc_id
            doc_id = hashlib.md5(f"rss_{url}".encode()).hexdigest()
            
            doc = {
                "doc_id": doc_id,
                "content": f"{title}\n\n{content}",  # Include title for better context
                "metadata": {
                    "url": url,
                    "source": "rss",  # Tag as RSS source
                    "source_name": article.get("source", "Unknown"),
                    "category": article.get("source_category", "general"),
                    "region": article.get("source_region", "global"),
                    "published_dt": article.get("published_dt", datetime.now(timezone.utc)).isoformat() if isinstance(article.get("published_dt"), datetime) else str(article.get("published_dt")),
                    "stored_at": datetime.now(timezone.utc).isoformat()
                }
            }
            documents.append(doc)
        
        if not documents:
            print(f"   ⚠️  No valid documents to store")
            return {"stored": 0, "skipped": 0, "failed": 0}
        
        print(f"   📦 Storing {len(documents)} COMPLETE articles (NO CHUNKING)...")
        print(f"   💡 RSS strategy: 1 article = 1 embedding (cost-efficient)")
        
        # Store using TenderMongoDBHandler (same as Crawler + Journalist)
        try:
            await self.db_handler.store_vectors(
                documents=documents,
                thread_id="rss_global"  # Use consistent thread_id for RSS
            )
            
            print(f"   ✅ Stored {len(documents)} RSS articles in tender_vectors")
            print(f"   🔍 Now queryable via Chat with Data + Knowledge Base!")
            print(f"{'─'*80}\n")
            
            return {"stored": len(documents), "skipped": 0, "failed": 0}
            
        except Exception as e:
            print(f"   ❌ Storage failed: {e}")
            import traceback
            traceback.print_exc()
            return {"stored": 0, "skipped": 0, "failed": len(documents)}
    
    async def semantic_search(self, query: str, top_k: int = 10, rss_only: bool = False) -> List[Dict]:
        """
        Search unified vector store (includes RSS + Crawler + Journalist)
        
        Args:
            query: Search query
            top_k: Number of results
            rss_only: If True, only return RSS articles
            
        Returns:
            List of matching articles with scores
        """
        print(f"\n🔍 Semantic Search: {query}")
        print(f"   Target: {'RSS only' if rss_only else 'ALL sources (RSS + Crawler + Journalist)'}")
        
        # Use TenderMongoDBHandler's search (Atlas Vector Search)
        results = await self.db_handler.search_vectors(
            query=query,
            thread_id=None,  # Search globally (all sources)
            top_k=top_k
        )
        
        # Filter to RSS only if requested
        if rss_only:
            results = [r for r in results if r.get('metadata', {}).get('source') == 'rss']
            print(f"   ✅ Found {len(results)} RSS results")
        else:
            print(f"   ✅ Found {len(results)} results across ALL sources")
            
            # Show source breakdown
            sources = {}
            for r in results:
                src = r.get('metadata', {}).get('source', 'unknown')
                sources[src] = sources.get(src, 0) + 1
            print(f"   📊 Sources: {sources}")
        
        return results
    
    def close(self):
        """Close connections"""
        self.db_handler.close()
        self.client.close()
