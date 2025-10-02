"""
Cache Manager - MongoDB caching for explosive topics

Uses MD5 hash of keywords as cache key
Supports configurable cache duration (default: 3 hours)
"""

import os
import sys
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Add backend_v2 services to path
backend_v2_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
sys.path.insert(0, backend_v2_path)

from backend_v2.services.mongo_service import MongoService
from config import CACHE_COLLECTION, DEFAULT_CACHE_HOURS


class CacheManager:
    """Manages caching of explosive topics results"""
    
    def __init__(self, mongo_service=None):
        """
        Initialize cache manager
        
        Args:
            mongo_service: Optional MongoService instance (if None, creates new one)
        """
        self.mongo = mongo_service if mongo_service else MongoService()
        self.collection_name = CACHE_COLLECTION
        self._connected = False
    
    async def ensure_connected(self):
        """Ensure MongoDB is connected before use"""
        if not self._connected and self.mongo is not None and not self.mongo._connected:
            try:
                await self.mongo.connect()
                self._connected = True
                print("✅ CacheManager: MongoDB connected")
            except Exception as e:
                print(f"⚠️  CacheManager: MongoDB connection failed: {e}")
                self.mongo = None
                self._connected = False
    
    def _generate_cache_key(self, keywords: List[str]) -> str:
        """
        Generate cache key from keywords
        
        Strategy: MD5 hash of sorted, comma-separated keywords
        This ensures same keywords in different order get same cache
        """
        normalized = ",".join(sorted([k.lower().strip() for k in keywords]))
        return hashlib.md5(normalized.encode()).hexdigest()
    
    async def get_cached_topics(
        self, 
        keywords: List[str], 
        cache_hours: int = DEFAULT_CACHE_HOURS
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached results if still valid
        
        Returns:
            Cached data if valid, None if expired or not found
        """
        
        # Ensure MongoDB is connected
        await self.ensure_connected()
        
        # Check if MongoDB is available
        if self.mongo is None or self.mongo.db is None:
            return None
        
        cache_key = self._generate_cache_key(keywords)
        
        # Get from MongoDB
        try:
            cached = await self.mongo.db[self.collection_name].find_one({"_id": cache_key})
        except Exception as e:
            print(f"Cache retrieval error: {e}")
            return None
        
        if not cached:
            return None
        
        # Check if expired
        cached_at = cached.get('cached_at')
        if not cached_at:
            return None
        
        # Parse datetime
        if isinstance(cached_at, str):
            cached_at = datetime.fromisoformat(cached_at)
        
        expiry_time = cached_at + timedelta(hours=cache_hours)
        
        if datetime.now() > expiry_time:
            # Cache expired
            return None
        
        # Update cache hit counter
        await self.mongo.db[self.collection_name].update_one(
            {"_id": cache_key},
            {"$inc": {"cache_hits": 1}}
        )
        
        # Calculate expiry info
        time_remaining = expiry_time - datetime.now()
        minutes_remaining = int(time_remaining.total_seconds() / 60)
        
        return {
            "topics": cached.get('topics', []),
            "cached_at": cached_at.isoformat() if isinstance(cached_at, datetime) else cached_at,
            "cache_expires_in_minutes": minutes_remaining,
            "total_articles_analyzed": cached.get('total_articles_analyzed', 0),
            "processing_time_seconds": cached.get('processing_time_seconds', 0),
            "cache_hits": cached.get('cache_hits', 0) + 1
        }
    
    async def cache_topics(
        self, 
        keywords: List[str], 
        topics: List[Dict], 
        cache_hours: int = DEFAULT_CACHE_HOURS,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Store results in cache
        
        Args:
            keywords: List of keywords used
            topics: Explosive topics results
            cache_hours: Cache duration
            metadata: Additional metadata (articles count, processing time, etc.)
        
        Returns:
            True if cached successfully
        """
        
        # Ensure MongoDB is connected
        await self.ensure_connected()
        
        # Check if MongoDB is available
        if self.mongo is None or self.mongo.db is None:
            print("Cache storage skipped: MongoDB not available")
            return False
        
        cache_key = self._generate_cache_key(keywords)
        now = datetime.now()
        
        cache_data = {
            "_id": cache_key,
            "keywords": keywords,
            "topics": topics,
            "cached_at": now,
            "expires_at": now + timedelta(hours=cache_hours),
            "cache_hours": cache_hours,
            "cache_hits": 0
        }
        
        # Add optional metadata
        if metadata:
            cache_data.update(metadata)
        
        try:
            await self.mongo.db[self.collection_name].update_one(
                {"_id": cache_key},
                {"$set": cache_data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Cache storage error: {e}")
            return False
    
    async def invalidate_cache(self, keywords: List[str]) -> bool:
        """
        Manually invalidate cache for specific keywords
        
        Returns:
            True if deleted successfully
        """
        cache_key = self._generate_cache_key(keywords)
        
        try:
            result = await self.mongo.db[self.collection_name].delete_one({"_id": cache_key})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Cache invalidation error: {e}")
            return False
    
    async def clear_expired_caches(self) -> int:
        """
        Clean up expired cache entries
        
        Returns:
            Number of expired entries deleted
        """
        try:
            result = await self.mongo.db[self.collection_name].delete_many({
                "expires_at": {"$lt": datetime.now()}
            })
            return result.deleted_count
        except Exception as e:
            print(f"Cache cleanup error: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Stats about cache usage
        """
        try:
            total_cached = await self.mongo.db[self.collection_name].count_documents({})
            
            # Count expired
            expired = await self.mongo.db[self.collection_name].count_documents({
                "expires_at": {"$lt": datetime.now()}
            })
            
            # Get top hit caches
            top_caches = await self.mongo.db[self.collection_name].find(
                {},
                {"keywords": 1, "cache_hits": 1, "cached_at": 1}
            ).sort("cache_hits", -1).limit(5).to_list(length=5)
            
            return {
                "total_cached_entries": total_cached,
                "active_entries": total_cached - expired,
                "expired_entries": expired,
                "top_caches": [
                    {
                        "keywords": c.get("keywords"),
                        "hits": c.get("cache_hits", 0),
                        "cached_at": c.get("cached_at")
                    }
                    for c in top_caches
                ]
            }
        except Exception as e:
            print(f"Cache stats error: {e}")
            return {"error": str(e)}


# Test cache manager independently
if __name__ == "__main__":
    import asyncio
    
    async def test_cache_manager():
        print("Testing Cache Manager...")
        
        manager = CacheManager()
        
        # Test data
        keywords = ["Bihar", "corruption", "India"]
        sample_topics = [
            {
                "topic": "Test Topic 1",
                "explosiveness_score": 75,
                "classification": "CRITICAL"
            }
        ]
        
        # Test caching
        print("\n1. Caching data...")
        success = await manager.cache_topics(
            keywords=keywords,
            topics=sample_topics,
            cache_hours=3,
            metadata={"total_articles_analyzed": 20, "processing_time_seconds": 15.5}
        )
        print(f"   Cache success: {success}")
        
        # Test retrieval
        print("\n2. Retrieving cached data...")
        cached = await manager.get_cached_topics(keywords, cache_hours=3)
        if cached:
            print(f"   ✓ Found cached data")
            print(f"   ✓ Expires in: {cached['cache_expires_in_minutes']} minutes")
            print(f"   ✓ Topics: {len(cached['topics'])}")
        else:
            print(f"   ✗ No cached data found")
        
        # Test stats
        print("\n3. Cache statistics...")
        stats = await manager.get_cache_stats()
        print(f"   Total entries: {stats.get('total_cached_entries')}")
        print(f"   Active entries: {stats.get('active_entries')}")
        
        print("\n✓ Cache Manager test complete")
    
    asyncio.run(test_cache_manager())

