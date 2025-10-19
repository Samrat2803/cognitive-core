"""
RSS Source Registry with MongoDB Deduplication

Manages RSS feed URLs and prevents duplicate sources.
Tracks user-requested sources and polling metrics.

Usage:
    from shared.rss_sources import RSSSourceManager
    
    manager = RSSSourceManager()
    
    # Add source with deduplication
    result = await manager.add_source(
        url="https://reuters.com/rss/technology",
        name="Reuters Technology",
        category="technology",
        region="United States"
    )
    
    # Get active sources
    sources = await manager.get_active_sources(category="technology")
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from typing import List, Dict, Optional
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RSSSourceManager:
    """
    Manages RSS feed sources with MongoDB-backed deduplication
    
    Key Features:
    - Prevents duplicate RSS feeds (by URL - unique index)
    - Tracks user-requested sources (agent-initiated)
    - Manages polling priority and metrics
    """
    
    def __init__(self, mongo_uri: str = None):
        """
        Initialize MongoDB connection
        
        Args:
            mongo_uri: MongoDB connection string (defaults to MONGODB_URI env var)
        """
        if mongo_uri is None:
            mongo_uri = os.getenv("MONGODB_URI") or os.getenv("MONGODB_CONNECTION_STRING")
            if not mongo_uri:
                raise ValueError("MONGODB_URI or MONGODB_CONNECTION_STRING environment variable not set")
        
        self.client = MongoClient(mongo_uri)
        self.db = self.client["political_analyst"]  # Same DB as Cognitive Core
        self.collection = self.db["rss_sources"]
        
        # Create indexes
        self._create_indexes()
        
        print(f"✓ RSS Source Manager initialized (DB: {self.db.name})")
    
    def _create_indexes(self):
        """Create indexes for efficient querying"""
        # Unique index on URL (prevents duplicates)
        self.collection.create_index([("url", ASCENDING)], unique=True)
        
        # Query optimization indexes
        self.collection.create_index([("active", ASCENDING), ("priority", ASCENDING)])
        self.collection.create_index([("category", ASCENDING)])
        self.collection.create_index([("region", ASCENDING)])
        
        print(f"✓ Created indexes on rss_sources collection")
    
    def add_source(
        self,
        url: str,
        name: str,
        category: str,
        region: str,
        priority: str = "medium",
        user_requested: bool = False,
        requested_for_query: str = None
    ) -> Dict:
        """
        Add RSS source with automatic deduplication
        
        Args:
            url: RSS feed URL (must be unique)
            name: Display name (e.g., "Reuters Technology")
            category: Category (technology, business, general, science)
            region: Geographic region
            priority: Polling priority (high, medium, low)
            user_requested: True if agent-initiated on-demand
            requested_for_query: Original query that triggered this (if user_requested)
        
        Returns:
            {
                "added": bool,           # True if new, False if duplicate
                "source": dict,          # Source document
                "message": str,          # Human-readable message
                "duplicate": bool        # True if already exists
            }
        """
        
        # CHECK FOR DUPLICATES (URL-based)
        existing = self.collection.find_one({"url": url})
        
        if existing:
            return {
                "added": False,
                "source": self._clean_document(existing),
                "message": f"Source already exists: {existing['name']}",
                "duplicate": True
            }
        
        # Add new source
        source_doc = {
            "url": url,
            "name": name,
            "category": category,
            "region": region,
            "priority": priority,
            "active": True,
            
            # Polling status
            "last_polled": None,
            "last_article_count": 0,
            "poll_interval_minutes": 5 if priority == "high" else 10,
            
            # Origin tracking
            "user_requested": user_requested,
            "requested_by_user_id": None,
            "requested_at": datetime.now(timezone.utc) if user_requested else None,
            "requested_for_query": requested_for_query,
            
            # Quality metrics
            "articles_scraped_total": 0,
            "scrape_error_count": 0,
            "avg_articles_per_poll": 0.0,
            
            "created_at": datetime.now(timezone.utc)
        }
        
        try:
            result = self.collection.insert_one(source_doc)
            source_doc["_id"] = result.inserted_id
            
            return {
                "added": True,
                "source": self._clean_document(source_doc),
                "message": f"Added new source: {name}",
                "duplicate": False
            }
        except Exception as e:
            # Handle duplicate key error (race condition)
            if "duplicate" in str(e).lower():
                existing = self.collection.find_one({"url": url})
                return {
                    "added": False,
                    "source": self._clean_document(existing),
                    "message": f"Source already exists: {existing['name']}",
                    "duplicate": True
                }
            raise
    
    def get_active_sources(
        self,
        category: Optional[str] = None,
        region: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all active RSS sources
        
        Args:
            category: Filter by category (optional)
            region: Filter by region (optional)
            priority: Filter by priority (optional)
        
        Returns:
            List of source documents
        """
        query = {"active": True}
        
        if category:
            query["category"] = category
        if region:
            query["region"] = region
        if priority:
            query["priority"] = priority
        
        sources = list(
            self.collection.find(query).sort("priority", DESCENDING)
        )
        
        return [self._clean_document(s) for s in sources]
    
    def check_if_exists(self, url: str) -> bool:
        """
        Check if RSS feed already exists
        
        Args:
            url: RSS feed URL
        
        Returns:
            True if exists, False otherwise
        """
        return self.collection.find_one({"url": url}) is not None
    
    def agent_request_new_source(
        self,
        url: str,
        name: str,
        category: str,
        region: str,
        query: str
    ) -> Dict:
        """
        Agent-initiated RSS source addition (on-demand)
        
        This is called when the agent determines a new RSS feed
        should be added based on user's query.
        
        Args:
            url: RSS feed URL
            name: Source name
            category: Category
            region: Region
            query: Original user query that triggered this
        
        Returns:
            Same as add_source()
        """
        
        return self.add_source(
            url=url,
            name=name,
            category=category,
            region=region,
            priority="medium",  # User-requested gets medium priority
            user_requested=True,
            requested_for_query=query
        )
    
    def update_poll_stats(
        self,
        source_id: str,
        article_count: int,
        error: bool = False
    ):
        """
        Update source polling statistics
        
        Args:
            source_id: Source _id (as string)
            article_count: Number of new articles fetched
            error: True if polling failed
        """
        from bson.objectid import ObjectId
        
        update = {
            "$set": {
                "last_polled": datetime.now(timezone.utc),
                "last_article_count": article_count
            },
            "$inc": {
                "articles_scraped_total": article_count
            }
        }
        
        if error:
            update["$inc"]["scrape_error_count"] = 1
        
        self.collection.update_one(
            {"_id": ObjectId(source_id)},
            update
        )
    
    def get_source_by_url(self, url: str) -> Optional[Dict]:
        """Get source by URL"""
        source = self.collection.find_one({"url": url})
        return self._clean_document(source) if source else None
    
    def _clean_document(self, doc: Dict) -> Dict:
        """Remove MongoDB-specific fields and convert ObjectId to string"""
        if doc is None:
            return None
        
        cleaned = dict(doc)
        if "_id" in cleaned:
            cleaned["_id"] = str(cleaned["_id"])
        
        return cleaned
    
    def get_stats(self) -> Dict:
        """Get overall statistics"""
        total = self.collection.count_documents({})
        active = self.collection.count_documents({"active": True})
        user_requested = self.collection.count_documents({"user_requested": True})
        
        return {
            "total_sources": total,
            "active_sources": active,
            "user_requested": user_requested,
            "categories": self._get_category_counts(),
            "regions": self._get_region_counts()
        }
    
    def _get_category_counts(self) -> Dict[str, int]:
        """Count sources by category"""
        pipeline = [
            {"$match": {"active": True}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        results = list(self.collection.aggregate(pipeline))
        return {r["_id"]: r["count"] for r in results}
    
    def _get_region_counts(self) -> Dict[str, int]:
        """Count sources by region"""
        pipeline = [
            {"$match": {"active": True}},
            {"$group": {"_id": "$region", "count": {"$sum": 1}}}
        ]
        results = list(self.collection.aggregate(pipeline))
        return {r["_id"]: r["count"] for r in results}


# Standalone test
if __name__ == "__main__":
    print("=" * 80)
    print("RSS SOURCE MANAGER - Standalone Test")
    print("=" * 80)
    
    manager = RSSSourceManager()
    
    # Test 1: Add source
    print("\n[TEST 1] Adding new source...")
    result = manager.add_source(
        url="https://feeds.reuters.com/reuters/technologyNews",
        name="Reuters Technology",
        category="technology",
        region="United States",
        priority="high"
    )
    print(f"  Result: {result['message']}")
    print(f"  Added: {result['added']}")
    
    # Test 2: Try duplicate
    print("\n[TEST 2] Trying to add duplicate...")
    result = manager.add_source(
        url="https://feeds.reuters.com/reuters/technologyNews",
        name="Reuters Technology",
        category="technology",
        region="United States"
    )
    print(f"  Result: {result['message']}")
    print(f"  Duplicate: {result['duplicate']}")
    
    # Test 3: Get active sources
    print("\n[TEST 3] Getting active sources...")
    sources = manager.get_active_sources()
    print(f"  Found {len(sources)} active sources")
    for source in sources[:3]:
        print(f"    - {source['name']} ({source['category']})")
    
    # Test 4: Agent-requested source
    print("\n[TEST 4] Agent requesting new source...")
    result = manager.agent_request_new_source(
        url="https://techcrunch.com/feed/",
        name="TechCrunch",
        category="technology",
        region="United States",
        query="Show me news about AI startups"
    )
    print(f"  Result: {result['message']}")
    print(f"  User requested: {result['source']['user_requested']}")
    
    # Test 5: Stats
    print("\n[TEST 5] Getting statistics...")
    stats = manager.get_stats()
    print(f"  Total sources: {stats['total_sources']}")
    print(f"  Active sources: {stats['active_sources']}")
    print(f"  User requested: {stats['user_requested']}")
    print(f"  Categories: {stats['categories']}")
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)

