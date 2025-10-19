"""
On-Demand Embedding Creator for RSS Articles

Creates and caches embeddings in MongoDB only when needed (lazy loading).
Prevents duplicate embedding creation.

Usage:
    from shared.rss_embedder import RSSEmbedder
    
    embedder = RSSEmbedder()
    
    # Get or create embeddings for articles
    embeddings = await embedder.get_or_create_embeddings(article_urls)
    
    # Semantic search
    results = await embedder.semantic_search(query, top_k=10)
"""

from pymongo import MongoClient, ASCENDING
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RSSEmbedder:
    """
    Creates and caches embeddings for RSS articles
    
    Strategy:
    - Create embeddings on-demand (not for all articles upfront)
    - Cache in MongoDB to avoid re-computation
    - Support semantic search using cosine similarity
    """
    
    def __init__(self, mongo_uri: str = None, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedder with MongoDB and sentence transformer
        
        Args:
            mongo_uri: MongoDB connection string
            model_name: SentenceTransformer model name
        """
        if mongo_uri is None:
            mongo_uri = os.getenv("MONGODB_URI") or os.getenv("MONGODB_CONNECTION_STRING")
            if not mongo_uri:
                raise ValueError("MONGODB_URI or MONGODB_CONNECTION_STRING environment variable not set")
        
        self.client = MongoClient(mongo_uri)
        self.db = self.client["political_analyst"]
        self.embeddings_collection = self.db["rss_article_embeddings"]
        self.articles_collection = self.db["rss_articles"]
        
        # Load embedding model
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Create indexes
        self._create_indexes()
        
        print(f"✓ RSS Embedder initialized ({model_name}, {self.embedding_dim}D)")
    
    def _create_indexes(self):
        """Create indexes for efficient querying"""
        # Unique index on article_url (prevents duplicate embeddings)
        self.embeddings_collection.create_index([("article_url", ASCENDING)], unique=True)
        self.embeddings_collection.create_index([("embedding_model", ASCENDING)])
        
        print(f"✓ Created indexes on rss_article_embeddings collection")
    
    async def get_or_create_embeddings(
        self,
        article_urls: List[str],
        show_progress: bool = False
    ) -> Dict[str, np.ndarray]:
        """
        Get embeddings for articles (create if not exists)
        
        Args:
            article_urls: List of article URLs
            show_progress: Show progress during creation
        
        Returns:
            {article_url: embedding_vector, ...}
        """
        
        result = {}
        to_embed = []
        
        # OPTIMIZED: Bulk query instead of N individual queries
        # Single query fetches all embeddings at once (100x faster for Atlas)
        cached_embeddings = list(self.embeddings_collection.find({
            "article_url": {"$in": article_urls},
            "embedding_model": self.model_name
        }))
        
        # Create lookup dict
        cached_lookup = {doc["article_url"]: np.array(doc["embedding"]) for doc in cached_embeddings}
        
        # Check which ones we have vs need
        for url in article_urls:
            if url in cached_lookup:
                result[url] = cached_lookup[url]
            else:
                to_embed.append(url)
        
        if show_progress:
            print(f"  Cached: {len(result)}, To embed: {len(to_embed)}")
        
        # Create missing embeddings
        if to_embed:
            new_embeddings = await self._create_embeddings(to_embed, show_progress)
            result.update(new_embeddings)
        
        return result
    
    async def _create_embeddings(
        self,
        article_urls: List[str],
        show_progress: bool = False
    ) -> Dict[str, np.ndarray]:
        """
        Create embeddings for articles
        
        Args:
            article_urls: List of article URLs
            show_progress: Show progress bar
        
        Returns:
            {article_url: embedding_vector, ...}
        """
        
        result = {}
        
        # Fetch articles from MongoDB
        articles = list(self.articles_collection.find({"url": {"$in": article_urls}}))
        
        if not articles:
            return result
        
        # Create text for embedding (title + summary)
        texts = []
        url_map = {}
        
        for article in articles:
            title = article.get("title", "")
            summary = article.get("summary", "")
            text = f"{title} {summary[:200]}"
            texts.append(text)
            url_map[text] = article['url']
        
        # Create embeddings (batch processing)
        if show_progress:
            print(f"  Creating {len(texts)} embeddings...")
        
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=show_progress
        )
        
        # Store in MongoDB and result dict
        for text, embedding in zip(texts, embeddings):
            url = url_map[text]
            
            embedding_doc = {
                "article_url": url,
                "embedding": embedding.tolist(),
                "embedding_model": self.model_name,
                "embedding_dim": len(embedding),
                "created_at": datetime.now(timezone.utc),
                "text_used": text[:500]  # Store first 500 chars for debugging
            }
            
            # Store in MongoDB (upsert to handle race conditions)
            try:
                self.embeddings_collection.update_one(
                    {"article_url": url, "embedding_model": self.model_name},
                    {"$set": embedding_doc},
                    upsert=True
                )
            except Exception as e:
                if "duplicate" not in str(e).lower():
                    print(f"  ✗ Error storing embedding for {url}: {e}")
            
            # Mark article as having embedding
            self.articles_collection.update_one(
                {"url": url},
                {"$set": {"has_embedding": True}}
            )
            
            result[url] = embedding
        
        return result
    
    async def semantic_search(
        self,
        query: str,
        article_urls: List[str],
        top_k: int = 50,
        min_similarity: float = 0.3
    ) -> List[Tuple[str, float]]:
        """
        Semantic search using cosine similarity
        
        Args:
            query: Search query text
            article_urls: List of article URLs to search within
            top_k: Number of top results to return
            min_similarity: Minimum cosine similarity threshold
        
        Returns:
            List of (article_url, similarity_score) tuples, sorted by score
        """
        
        # Create query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)[0]
        
        # Get or create article embeddings
        article_embeddings = await self.get_or_create_embeddings(article_urls)
        
        # Calculate cosine similarities
        similarities = []
        
        for url, embedding in article_embeddings.items():
            # Cosine similarity
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            
            if similarity >= min_similarity:
                similarities.append((url, float(similarity)))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    async def find_similar_articles(
        self,
        article_url: str,
        candidate_urls: List[str],
        top_k: int = 10,
        min_similarity: float = 0.5
    ) -> List[Tuple[str, float]]:
        """
        Find articles similar to a given article
        
        Args:
            article_url: Reference article URL
            candidate_urls: List of candidate article URLs
            top_k: Number of results
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of (article_url, similarity_score) tuples
        """
        
        # Get embeddings
        all_urls = [article_url] + candidate_urls
        embeddings = await self.get_or_create_embeddings(all_urls)
        
        if article_url not in embeddings:
            return []
        
        reference_embedding = embeddings[article_url]
        similarities = []
        
        for url in candidate_urls:
            if url == article_url or url not in embeddings:
                continue
            
            embedding = embeddings[url]
            similarity = np.dot(reference_embedding, embedding) / (
                np.linalg.norm(reference_embedding) * np.linalg.norm(embedding)
            )
            
            if similarity >= min_similarity:
                similarities.append((url, float(similarity)))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def get_stats(self) -> Dict:
        """Get embedding collection statistics"""
        total = self.embeddings_collection.count_documents({})
        by_model = {}
        
        pipeline = [
            {"$group": {"_id": "$embedding_model", "count": {"$sum": 1}}}
        ]
        results = list(self.embeddings_collection.aggregate(pipeline))
        by_model = {r["_id"]: r["count"] for r in results}
        
        return {
            "total_embeddings": total,
            "by_model": by_model,
            "current_model": self.model_name,
            "embedding_dim": self.embedding_dim
        }


# Standalone test
if __name__ == "__main__":
    import asyncio
    from rss_collector import RSSCollector
    
    async def test():
        print("=" * 80)
        print("RSS EMBEDDER - Standalone Test")
        print("=" * 80)
        
        # Initialize
        collector = RSSCollector()
        embedder = RSSEmbedder()
        
        # Get some articles
        print("\n[TEST 1] Getting articles from MongoDB...")
        articles = await collector.get_articles(max_age_hours=24, limit=20)
        print(f"  Retrieved {len(articles)} articles")
        
        if not articles:
            print("  ⚠️  No articles found. Run rss_collector.py first!")
            return
        
        article_urls = [a["url"] for a in articles]
        
        # Create embeddings
        print("\n[TEST 2] Creating embeddings (on-demand)...")
        embeddings = await embedder.get_or_create_embeddings(article_urls[:10], show_progress=True)
        print(f"  ✓ Created/retrieved {len(embeddings)} embeddings")
        print(f"  Embedding shape: {list(embeddings.values())[0].shape}")
        
        # Test semantic search
        print("\n[TEST 3] Semantic search...")
        queries = [
            "artificial intelligence regulation",
            "climate change policy",
            "technology companies"
        ]
        
        for query in queries:
            print(f"\n  Query: '{query}'")
            results = await embedder.semantic_search(query, article_urls, top_k=3)
            print(f"  Found {len(results)} results")
            
            for i, (url, score) in enumerate(results, 1):
                # Get article title
                article = next((a for a in articles if a["url"] == url), None)
                if article:
                    print(f"    {i}. {article['title'][:60]}...")
                    print(f"       Similarity: {score:.3f}")
        
        # Test similar articles
        print("\n[TEST 4] Finding similar articles...")
        if len(article_urls) >= 5:
            reference_url = article_urls[0]
            reference_article = articles[0]
            print(f"  Reference: {reference_article['title'][:60]}...")
            
            similar = await embedder.find_similar_articles(
                reference_url,
                article_urls[1:],
                top_k=3
            )
            
            print(f"  Found {len(similar)} similar articles:")
            for i, (url, score) in enumerate(similar, 1):
                article = next((a for a in articles if a["url"] == url), None)
                if article:
                    print(f"    {i}. {article['title'][:60]}...")
                    print(f"       Similarity: {score:.3f}")
        
        # Stats
        print("\n[TEST 5] Embedding statistics...")
        stats = embedder.get_stats()
        print(f"  Total embeddings: {stats['total_embeddings']}")
        print(f"  Current model: {stats['current_model']}")
        print(f"  Embedding dimension: {stats['embedding_dim']}")
        print(f"  By model: {stats['by_model']}")
        
        print("\n" + "=" * 80)
        print("✅ All tests completed!")
        print("=" * 80)
    
    asyncio.run(test())

