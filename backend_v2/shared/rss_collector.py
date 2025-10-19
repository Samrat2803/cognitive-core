"""
RSS Article Collector with MongoDB Storage

Polls RSS feeds, stores articles in MongoDB with automatic deduplication.
Features 48-hour TTL for automatic cleanup.

Usage:
    from shared.rss_collector import RSSCollector
    
    collector = RSSCollector()
    
    # Poll a source
    stats = await collector.poll_and_store(source_dict)
    
    # Get articles
    articles = await collector.get_articles(max_age_hours=24)
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import feedparser
import httpx
import asyncio
import os
from dotenv import load_dotenv
from email.utils import parsedate_to_datetime

# Load environment variables
load_dotenv()


class RSSCollector:
    """
    Polls RSS feeds and stores in MongoDB
    
    Features:
    - Automatic deduplication (by URL)
    - 48-hour TTL for auto-cleanup
    - Prevents duplicate articles
    - Tracks source metrics
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
        self.db = self.client["political_analyst"]
        self.articles_collection = self.db["rss_articles"]
        self.sources_collection = self.db["rss_sources"]
        
        # Create indexes
        self._create_indexes()
        
        print(f"✓ RSS Collector initialized (DB: {self.db.name})")
    
    def _create_indexes(self):
        """Create indexes with TTL for auto-deletion"""
        # Unique URL index (prevents duplicates)
        self.articles_collection.create_index([("url", ASCENDING)], unique=True)
        
        # Query optimization indexes
        self.articles_collection.create_index([("published_dt", DESCENDING)])
        self.articles_collection.create_index([("source", ASCENDING)])
        self.articles_collection.create_index([("source_category", ASCENDING)])
        self.articles_collection.create_index([("source_region", ASCENDING)])
        
        # TTL index (auto-delete after 48 hours from expires_at)
        self.articles_collection.create_index(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0
        )
        
        print(f"✓ Created indexes on rss_articles collection (with 48h TTL)")
    
    async def poll_and_store(self, source: Dict) -> Dict:
        """
        Poll single RSS feed and store articles in MongoDB
        
        Args:
            source: Source document from rss_sources collection
        
        Returns:
            {
                "new_articles": int,      # Successfully added
                "duplicates": int,        # Already exists
                "errors": int,            # Parse/insert errors
                "source_name": str
            }
        """
        
        stats = {
            "new_articles": 0,
            "duplicates": 0,
            "errors": 0,
            "source_name": source["name"]
        }
        
        try:
            # Fetch RSS feed
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(source["url"])
                response.raise_for_status()
                feed = feedparser.parse(response.text)
            
            if not feed.entries:
                print(f"  ⚠️  No entries found for {source['name']}")
                return stats
            
            # Process each entry
            for entry in feed.entries:
                try:
                    article_doc = self._parse_entry(entry, source)
                    
                    if not article_doc.get("url"):
                        stats["errors"] += 1
                        continue
                    
                    # Try to insert (will fail if duplicate URL)
                    try:
                        self.articles_collection.insert_one(article_doc)
                        stats["new_articles"] += 1
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "duplicate" in error_msg or "E11000" in str(e):
                            stats["duplicates"] += 1
                        else:
                            stats["errors"] += 1
                            print(f"  ✗ Insert error: {e}")
                
                except Exception as e:
                    stats["errors"] += 1
                    print(f"  ✗ Parse error: {e}")
            
            # Update source last_polled
            from bson.objectid import ObjectId
            self.sources_collection.update_one(
                {"_id": ObjectId(source["_id"])},
                {
                    "$set": {
                        "last_polled": datetime.now(timezone.utc),
                        "last_article_count": stats["new_articles"]
                    },
                    "$inc": {"articles_scraped_total": stats["new_articles"]}
                }
            )
        
        except Exception as e:
            stats["errors"] += 1
            print(f"  ✗ Feed fetch error for {source['name']}: {e}")
            
            # Update error count
            from bson.objectid import ObjectId
            self.sources_collection.update_one(
                {"_id": ObjectId(source["_id"])},
                {"$inc": {"scrape_error_count": 1}}
            )
        
        return stats
    
    def _parse_entry(self, entry: Dict, source: Dict) -> Dict:
        """
        Parse RSS entry into article document
        
        Args:
            entry: feedparser entry
            source: Source document
        
        Returns:
            Article document ready for MongoDB
        """
        
        # Parse publish date
        published_dt = self._parse_date(entry.get("published"))
        scraped_at = datetime.now(timezone.utc)
        
        # Calculate age
        age_hours = (scraped_at - published_dt).total_seconds() / 3600
        
        # Extract content
        summary = entry.get("summary", "")
        content = ""
        if hasattr(entry, "content") and entry.content:
            content = entry.content[0].get("value", "")
        
        return {
            "url": entry.get("link", ""),
            "title": entry.get("title", ""),
            "summary": summary,
            "content": content,
            
            # Source metadata
            "source": source["name"],
            "source_url": source["url"],
            "source_category": source["category"],
            "source_region": source["region"],
            "source_priority": source["priority"],
            
            # Temporal data
            "published_dt": published_dt,
            "scraped_at": scraped_at,
            "age_hours": age_hours,
            
            # Embedding status
            "has_embedding": False,
            "user_requested_source": source.get("user_requested", False),
            
            # TTL: expires 48 hours after scraping
            "expires_at": scraped_at + timedelta(hours=48)
        }
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse various date formats to datetime
        
        Args:
            date_str: Date string from RSS feed
        
        Returns:
            datetime object (UTC)
        """
        if not date_str:
            return datetime.now(timezone.utc)
        
        try:
            # Try email format (RFC 2822)
            dt = parsedate_to_datetime(date_str)
            # Convert to UTC if not already
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except:
            pass
        
        try:
            # Try ISO format
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except:
            pass
        
        # Fallback to now
        return datetime.now(timezone.utc)
    
    async def get_articles(
        self,
        max_age_hours: int = 48,
        category: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Get articles from MongoDB
        
        Args:
            max_age_hours: Maximum age in hours (default: 48)
            category: Filter by category (optional)
            region: Filter by region (optional)
            limit: Maximum number of articles (default: 1000)
        
        Returns:
            List of article documents (sorted by publish date, newest first)
        """
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        
        query = {"published_dt": {"$gte": cutoff_time}}
        
        if category:
            query["source_category"] = category
        if region:
            query["source_region"] = region
        
        articles = list(
            self.articles_collection
            .find(query)
            .sort("published_dt", DESCENDING)
            .limit(limit)
        )
        
        # Remove MongoDB _id and convert to serializable
        for article in articles:
            article.pop("_id", None)
            # Convert datetime to ISO string for JSON serialization
            if isinstance(article.get("published_dt"), datetime):
                article["published_dt"] = article["published_dt"].isoformat()
            if isinstance(article.get("scraped_at"), datetime):
                article["scraped_at"] = article["scraped_at"].isoformat()
            if isinstance(article.get("expires_at"), datetime):
                article["expires_at"] = article["expires_at"].isoformat()
        
        return articles
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        total = self.articles_collection.count_documents({})
        
        # Age distribution
        now = datetime.now(timezone.utc)
        last_6h = self.articles_collection.count_documents({
            "published_dt": {"$gte": now - timedelta(hours=6)}
        })
        last_24h = self.articles_collection.count_documents({
            "published_dt": {"$gte": now - timedelta(hours=24)}
        })
        
        return {
            "total_articles": total,
            "last_6h": last_6h,
            "last_24h": last_24h,
            "categories": self._get_category_counts(),
            "sources": self._get_source_counts()
        }
    
    def _get_category_counts(self) -> Dict[str, int]:
        """Count articles by category"""
        pipeline = [
            {"$group": {"_id": "$source_category", "count": {"$sum": 1}}}
        ]
        results = list(self.articles_collection.aggregate(pipeline))
        return {r["_id"]: r["count"] for r in results}
    
    def _get_source_counts(self) -> Dict[str, int]:
        """Count articles by source"""
        pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        results = list(self.articles_collection.aggregate(pipeline))
        return {r["_id"]: r["count"] for r in results}


# Standalone test
if __name__ == "__main__":
    import asyncio
    from rss_sources import RSSSourceManager
    
    async def test():
        print("=" * 80)
        print("RSS COLLECTOR - Standalone Test")
        print("=" * 80)
        
        # Initialize
        source_manager = RSSSourceManager()
        collector = RSSCollector()
        
        # Add test sources if not exist
        print("\n[SETUP] Adding test sources...")
        test_sources = [
            {
                "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
                "name": "BBC Technology",
                "category": "technology",
                "region": "United Kingdom"
            },
            {
                "url": "https://www.aljazeera.com/xml/rss/all.xml",
                "name": "Al Jazeera",
                "category": "general",
                "region": "Qatar"
            },
            {
                "url": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
                "name": "NY Times Technology",
                "category": "technology",
                "region": "United States"
            }
        ]
        
        for src in test_sources:
            result = source_manager.add_source(**src, priority="high")
            print(f"  {result['message']}")
        
        # Get active sources
        print("\n[TEST 1] Getting active sources...")
        sources = source_manager.get_active_sources()
        print(f"  Found {len(sources)} active sources")
        
        # Poll each source
        print("\n[TEST 2] Polling RSS feeds...")
        total_new = 0
        total_duplicates = 0
        
        for source in sources[:3]:  # Test first 3
            print(f"\n  Polling: {source['name']}")
            stats = await collector.poll_and_store(source)
            print(f"    ✓ New: {stats['new_articles']}, Duplicates: {stats['duplicates']}, Errors: {stats['errors']}")
            total_new += stats['new_articles']
            total_duplicates += stats['duplicates']
        
        print(f"\n  Summary: {total_new} new articles, {total_duplicates} duplicates")
        
        # Get articles
        print("\n[TEST 3] Retrieving articles from MongoDB...")
        articles = await collector.get_articles(max_age_hours=24, limit=10)
        print(f"  Retrieved {len(articles)} articles")
        
        if articles:
            print("\n  Sample articles:")
            for article in articles[:3]:
                age = article.get('age_hours', 0)
                print(f"    - {article['title'][:70]}...")
                print(f"      Source: {article['source']}, Age: {age:.1f}h")
        
        # Stats
        print("\n[TEST 4] Collection statistics...")
        stats = collector.get_stats()
        print(f"  Total articles: {stats['total_articles']}")
        print(f"  Last 6h: {stats['last_6h']}")
        print(f"  Last 24h: {stats['last_24h']}")
        print(f"  Categories: {stats['categories']}")
        
        print("\n" + "=" * 80)
        print("✅ All tests completed!")
        print("=" * 80)
    
    asyncio.run(test())

