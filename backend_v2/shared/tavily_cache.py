"""
Unified Tavily Caching Layer with Vector Storage
Caches all Tavily searches and extractions in MongoDB to avoid repeat costs
Also stores all extracted content as vectors for RAG queries

Architecture:
1. Search Cache (24h TTL) - Cache search results
2. Extract Cache (7d TTL) - Cache article extractions  
3. Vector Store (permanent) - All content as embeddings for RAG
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pymongo import MongoClient, ASCENDING
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


class TavilyCache:
    """
    MongoDB-based caching for Tavily API calls + Vector Storage for RAG
    
    Collections:
    - tavily_search_cache: Cache search results (24h TTL)
    - tavily_extract_cache: Cache article extractions (7d TTL)
    - tavily_vector_store: Permanent vector storage for RAG (no TTL)
    
    Cache TTL:
    - Search results: 24 hours (news changes frequently)
    - Extractions: 7 days (article content doesn't change)
    - Vectors: Permanent (knowledge base grows over time)
    """
    
    # Cache expiry times
    SEARCH_CACHE_HOURS = 24  # Search results expire after 24 hours
    EXTRACT_CACHE_DAYS = 7   # Extractions expire after 7 days
    
    # Vector storage settings
    VECTOR_DIMENSIONS = 1536  # OpenAI text-embedding-3-small dimensions
    
    def __init__(self):
        """Initialize cache with MongoDB connection"""
        self.mongo_uri = os.getenv('MONGODB_CONNECTION_STRING')
        self.db_name = os.getenv('DATABASE_NAME', 'political_analyst_db')
        
        self.client: Optional[MongoClient] = None
        self.db = None
        
        # OpenAI client for embeddings
        self.openai = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Collection names
        self.search_collection = 'tavily_search_cache'
        self.extract_collection = 'tavily_extract_cache'
        self.vector_collection = 'tavily_vector_store'  # NEW: Vector storage
        
        # Statistics
        self.stats = {
            'search_hits': 0,
            'search_misses': 0,
            'extract_hits': 0,
            'extract_misses': 0,
            'vectors_created': 0,
            'total_saved': 0.0,  # Dollars saved
            'embedding_cost': 0.0  # Embedding generation cost
        }
    
    def connect(self):
        """Connect to MongoDB and create indexes"""
        if self.client is None and self.mongo_uri:
            try:
                self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
                self.db = self.client[self.db_name]
                
                # Create indexes for performance
                # Search cache index
                self.db[self.search_collection].create_index([
                    ('query_hash', ASCENDING),
                    ('cached_at', ASCENDING)
                ])
                
                # Extract cache index
                self.db[self.extract_collection].create_index([
                    ('url_hash', ASCENDING),
                    ('cached_at', ASCENDING)
                ])
                
                # Vector store indexes
                self.db[self.vector_collection].create_index([
                    ('url_hash', ASCENDING)
                ], unique=True)  # One vector per URL
                
                self.db[self.vector_collection].create_index([
                    ('cached_at', ASCENDING)
                ])
                
                # TTL indexes for automatic expiry
                self.db[self.search_collection].create_index(
                    'cached_at',
                    expireAfterSeconds=self.SEARCH_CACHE_HOURS * 3600
                )
                
                self.db[self.extract_collection].create_index(
                    'cached_at',
                    expireAfterSeconds=self.EXTRACT_CACHE_DAYS * 86400
                )
                
                # NO TTL for vector store - it's permanent!
                
                print("✅ Tavily cache connected to MongoDB (with vector storage)")
                return True
            except Exception as e:
                print(f"⚠️  Tavily cache MongoDB connection failed: {e}")
                self.client = None
                self.db = None
                return False
        return self.db is not None
    
    def _generate_query_hash(self, query: str, search_depth: str = "advanced", 
                            max_results: int = 10) -> str:
        """Generate hash for search query (includes params for cache key)"""
        # Normalize query
        normalized = f"{query.lower().strip()}|{search_depth}|{max_results}"
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _generate_url_hash(self, url: str) -> str:
        """Generate hash for URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    async def get_cached_search(self, query: str, search_depth: str = "advanced",
                                max_results: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get cached search results
        
        Returns:
            Cached search results or None if not found/expired
        """
        if not self.connect():
            return None
        
        query_hash = self._generate_query_hash(query, search_depth, max_results)
        
        try:
            cached = self.db[self.search_collection].find_one({
                'query_hash': query_hash
            })
            
            if cached:
                # Check if expired (double-check even though TTL index exists)
                cached_at = cached.get('cached_at')
                if isinstance(cached_at, str):
                    cached_at = datetime.fromisoformat(cached_at)
                
                expiry = cached_at + timedelta(hours=self.SEARCH_CACHE_HOURS)
                
                if datetime.utcnow() > expiry:
                    # Expired, delete it
                    self.db[self.search_collection].delete_one({'query_hash': query_hash})
                    self.stats['search_misses'] += 1
                    return None
                
                # Cache hit!
                self.stats['search_hits'] += 1
                self.stats['total_saved'] += 0.01  # $0.01 per search
                
                # Update hit count
                self.db[self.search_collection].update_one(
                    {'query_hash': query_hash},
                    {
                        '$inc': {'hit_count': 1},
                        '$set': {'last_accessed': datetime.utcnow()}
                    }
                )
                
                print(f"💰 CACHE HIT - Search: '{query[:50]}...' (Saved $0.01)")
                return cached.get('results')
            
            self.stats['search_misses'] += 1
            return None
            
        except Exception as e:
            print(f"⚠️  Cache retrieval error: {e}")
            return None
    
    async def cache_search(self, query: str, results: Dict[str, Any], 
                          search_depth: str = "advanced", max_results: int = 10):
        """
        Cache search results in MongoDB
        
        Args:
            query: Search query
            results: Tavily search results
            search_depth: Search depth used
            max_results: Max results requested
        """
        if not self.connect():
            return
        
        query_hash = self._generate_query_hash(query, search_depth, max_results)
        
        try:
            self.db[self.search_collection].update_one(
                {'query_hash': query_hash},
                {
                    '$set': {
                        'query': query,
                        'query_hash': query_hash,
                        'search_depth': search_depth,
                        'max_results': max_results,
                        'results': results,
                        'cached_at': datetime.utcnow(),
                        'last_accessed': datetime.utcnow(),
                        'hit_count': 0
                    }
                },
                upsert=True
            )
            print(f"💾 CACHED - Search: '{query[:50]}...'")
            
        except Exception as e:
            print(f"⚠️  Cache storage error: {e}")
    
    async def get_cached_extract(self, url: str) -> Optional[str]:
        """
        Get cached article extraction
        
        Returns:
            Cached article content or None if not found/expired
        """
        if not self.connect():
            return None
        
        url_hash = self._generate_url_hash(url)
        
        try:
            cached = self.db[self.extract_collection].find_one({
                'url_hash': url_hash
            })
            
            if cached:
                # Check if expired
                cached_at = cached.get('cached_at')
                if isinstance(cached_at, str):
                    cached_at = datetime.fromisoformat(cached_at)
                
                expiry = cached_at + timedelta(days=self.EXTRACT_CACHE_DAYS)
                
                if datetime.utcnow() > expiry:
                    # Expired, delete it
                    self.db[self.extract_collection].delete_one({'url_hash': url_hash})
                    self.stats['extract_misses'] += 1
                    return None
                
                # Cache hit!
                self.stats['extract_hits'] += 1
                self.stats['total_saved'] += 0.05  # $0.05 per extract
                
                # Update hit count
                self.db[self.extract_collection].update_one(
                    {'url_hash': url_hash},
                    {
                        '$inc': {'hit_count': 1},
                        '$set': {'last_accessed': datetime.utcnow()}
                    }
                )
                
                print(f"💰 CACHE HIT - Extract: {url[:60]}... (Saved $0.05)")
                return cached.get('content')
            
            self.stats['extract_misses'] += 1
            return None
            
        except Exception as e:
            print(f"⚠️  Cache retrieval error: {e}")
            return None
    
    async def cache_extract(self, url: str, content: str, method: str = "unknown", 
                           metadata: Optional[Dict] = None, store_vector: bool = True):
        """
        Cache article extraction in MongoDB
        
        Args:
            url: Article URL
            content: Extracted article content
            method: Extraction method (free/tavily/crawl4ai)
            metadata: Optional metadata (title, source, date, etc.)
            store_vector: Whether to also store as vector for RAG (default: True)
        """
        if not self.connect():
            return
        
        if not content or len(content) < 100:
            # Don't cache empty or very short content
            return
        
        url_hash = self._generate_url_hash(url)
        
        try:
            # 1. Store in extract cache (7 days TTL)
            self.db[self.extract_collection].update_one(
                {'url_hash': url_hash},
                {
                    '$set': {
                        'url': url,
                        'url_hash': url_hash,
                        'content': content,
                        'content_length': len(content),
                        'extraction_method': method,
                        'metadata': metadata or {},
                        'cached_at': datetime.utcnow(),
                        'last_accessed': datetime.utcnow(),
                        'hit_count': 0
                    }
                },
                upsert=True
            )
            print(f"💾 CACHED - Extract: {url[:60]}... ({len(content)} chars, {method})")
            
            # 2. Also store as vector for RAG (permanent)
            if store_vector:
                await self.store_vector(url, content, metadata)
            
        except Exception as e:
            print(f"⚠️  Cache storage error: {e}")
    
    async def get_multiple_cached_extracts(self, urls: List[str]) -> Dict[str, str]:
        """
        Get multiple cached extracts at once (batch operation)
        
        Returns:
            Dict of {url: content} for URLs that have cached content
        """
        if not self.connect():
            return {}
        
        url_hashes = {self._generate_url_hash(url): url for url in urls}
        
        try:
            cached_docs = self.db[self.extract_collection].find({
                'url_hash': {'$in': list(url_hashes.keys())}
            })
            
            results = {}
            for doc in cached_docs:
                url = url_hashes[doc['url_hash']]
                results[url] = doc.get('content', '')
                
                # Update stats
                self.stats['extract_hits'] += 1
                self.stats['total_saved'] += 0.05
                
                # Update hit count
                self.db[self.extract_collection].update_one(
                    {'url_hash': doc['url_hash']},
                    {
                        '$inc': {'hit_count': 1},
                        '$set': {'last_accessed': datetime.utcnow()}
                    }
                )
            
            if results:
                print(f"💰 CACHE HIT - Batch: {len(results)}/{len(urls)} URLs (Saved ${len(results) * 0.05:.2f})")
            
            return results
            
        except Exception as e:
            print(f"⚠️  Batch cache retrieval error: {e}")
            return {}
    
    async def store_vector(self, url: str, content: str, metadata: Optional[Dict] = None):
        """
        Store article as vector embedding for RAG queries (PERMANENT storage)
        
        Args:
            url: Article URL
            content: Article content
            metadata: Optional metadata (title, source, published_date, etc.)
        """
        if not self.connect():
            return
        
        url_hash = self._generate_url_hash(url)
        
        try:
            # Check if already exists
            existing = self.db[self.vector_collection].find_one({'url_hash': url_hash})
            if existing:
                print(f"🔗 Vector already exists: {url[:60]}...")
                return
            
            # Generate embedding using OpenAI
            # Truncate content to ~8000 chars to stay within token limits
            truncated_content = content[:8000] if len(content) > 8000 else content
            
            response = await self.openai.embeddings.create(
                model="text-embedding-3-small",
                input=truncated_content
            )
            
            embedding = response.data[0].embedding
            
            # Cost tracking: $0.02 per 1M tokens, ~1000 chars = ~250 tokens
            tokens_used = len(truncated_content) // 4  # Rough estimate
            embedding_cost = (tokens_used / 1_000_000) * 0.02
            self.stats['embedding_cost'] += embedding_cost
            self.stats['vectors_created'] += 1
            
            # Store in MongoDB
            self.db[self.vector_collection].insert_one({
                'url': url,
                'url_hash': url_hash,
                'content': content,
                'content_length': len(content),
                'embedding': embedding,
                'metadata': metadata or {},
                'cached_at': datetime.utcnow(),
                'query_count': 0  # Track how often this is retrieved via RAG
            })
            
            print(f"🧬 VECTOR STORED: {url[:60]}... (${embedding_cost:.5f})")
            
        except Exception as e:
            print(f"⚠️  Vector storage error: {e}")
    
    async def rag_search(self, query: str, top_k: int = 5, 
                         min_similarity: float = 0.7) -> List[Dict[str, Any]]:
        """
        RAG search: Find most similar documents using vector similarity
        
        Args:
            query: Search query
            top_k: Number of results to return
            min_similarity: Minimum cosine similarity score (0-1)
        
        Returns:
            List of documents with similarity scores
        """
        if not self.connect():
            return []
        
        try:
            # Generate query embedding
            response = await self.openai.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            
            query_embedding = response.data[0].embedding
            
            # MongoDB Atlas Vector Search
            # Note: Requires MongoDB Atlas with vector search index configured
            pipeline = [
                {
                    '$vectorSearch': {
                        'index': 'tavily_vector_index',  # Create this in Atlas
                        'path': 'embedding',
                        'queryVector': query_embedding,
                        'numCandidates': top_k * 10,
                        'limit': top_k
                    }
                },
                {
                    '$project': {
                        'url': 1,
                        'content': 1,
                        'metadata': 1,
                        'cached_at': 1,
                        'score': {'$meta': 'vectorSearchScore'}
                    }
                },
                {
                    '$match': {
                        'score': {'$gte': min_similarity}
                    }
                }
            ]
            
            results = list(self.db[self.vector_collection].aggregate(pipeline))
            
            # Update query counts
            for result in results:
                self.db[self.vector_collection].update_one(
                    {'_id': result['_id']},
                    {'$inc': {'query_count': 1}}
                )
            
            print(f"🔍 RAG SEARCH: Found {len(results)} documents (similarity >= {min_similarity})")
            return results
            
        except Exception as e:
            print(f"⚠️  RAG search error: {e}")
            print("   Note: Requires MongoDB Atlas with vector search index 'tavily_vector_index'")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.connect():
            return self.stats
        
        try:
            # Get collection stats
            search_count = self.db[self.search_collection].count_documents({})
            extract_count = self.db[self.extract_collection].count_documents({})
            vector_count = self.db[self.vector_collection].count_documents({})
            
            # Get total hits from database
            search_pipeline = [
                {'$group': {'_id': None, 'total_hits': {'$sum': '$hit_count'}}}
            ]
            extract_pipeline = [
                {'$group': {'_id': None, 'total_hits': {'$sum': '$hit_count'}}}
            ]
            vector_pipeline = [
                {'$group': {'_id': None, 'total_queries': {'$sum': '$query_count'}}}
            ]
            
            search_hits_db = list(self.db[self.search_collection].aggregate(search_pipeline))
            extract_hits_db = list(self.db[self.extract_collection].aggregate(extract_pipeline))
            vector_queries_db = list(self.db[self.vector_collection].aggregate(vector_pipeline))
            
            total_search_hits = search_hits_db[0]['total_hits'] if search_hits_db else 0
            total_extract_hits = extract_hits_db[0]['total_hits'] if extract_hits_db else 0
            total_rag_queries = vector_queries_db[0]['total_queries'] if vector_queries_db else 0
            
            return {
                **self.stats,
                'cached_searches': search_count,
                'cached_extracts': extract_count,
                'stored_vectors': vector_count,
                'total_search_hits_db': total_search_hits,
                'total_extract_hits_db': total_extract_hits,
                'total_rag_queries': total_rag_queries,
                'estimated_total_saved': (total_search_hits * 0.01) + (total_extract_hits * 0.05)
            }
        except Exception as e:
            print(f"⚠️  Error getting stats: {e}")
            return self.stats
    
    def clear_cache(self, collection: Optional[str] = None):
        """
        Clear cache (use with caution!)
        
        Args:
            collection: 'searches', 'extracts', or None (both)
        """
        if not self.connect():
            return
        
        try:
            if collection == 'searches' or collection is None:
                result = self.db[self.search_collection].delete_many({})
                print(f"🗑️  Cleared {result.deleted_count} search cache entries")
            
            if collection == 'extracts' or collection is None:
                result = self.db[self.extract_collection].delete_many({})
                print(f"🗑️  Cleared {result.deleted_count} extract cache entries")
                
        except Exception as e:
            print(f"⚠️  Error clearing cache: {e}")


# Global cache instance
_cache_instance: Optional[TavilyCache] = None


def get_tavily_cache() -> TavilyCache:
    """Get global cache instance (singleton pattern)"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = TavilyCache()
    return _cache_instance

