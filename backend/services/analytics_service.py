"""Analytics service for demo insights"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
try:
    from .mongo_service import MongoService
except ImportError:
    from mongo_service import MongoService


class AnalyticsService:
    """Service for generating analytics insights"""
    
    def __init__(self, mongo_service: MongoService):
        self.mongo_service = mongo_service
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for demo"""
        await self.mongo_service.connect()
        
        # Get recent queries (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        # Query statistics
        total_queries = await self.mongo_service.db.queries.count_documents({
            "created_at": {"$gte": seven_days_ago}
        })
        
        completed_queries = await self.mongo_service.db.queries.count_documents({
            "status": "completed",
            "created_at": {"$gte": seven_days_ago}
        })
        
        # Average processing time
        pipeline = [
            {
                "$match": {
                    "status": "completed",
                    "processing_time_ms": {"$exists": True},
                    "created_at": {"$gte": seven_days_ago}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_time": {"$avg": "$processing_time_ms"},
                    "min_time": {"$min": "$processing_time_ms"},
                    "max_time": {"$max": "$processing_time_ms"}
                }
            }
        ]
        
        time_stats = await self.mongo_service.db.queries.aggregate(pipeline).to_list(1)
        
        # Popular topics (from search terms)
        topics_pipeline = [
            {"$match": {"created_at": {"$gte": seven_days_ago}}},
            {"$unwind": "$search_terms"},
            {"$group": {"_id": "$search_terms", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        popular_topics = await self.mongo_service.db.results.aggregate(
            topics_pipeline
        ).to_list(10)
        
        return {
            "total_queries": total_queries,
            "completed_queries": completed_queries,
            "success_rate": (completed_queries / total_queries * 100) if total_queries > 0 else 0,
            "avg_processing_time_ms": time_stats[0]["avg_time"] if time_stats else 0,
            "min_processing_time_ms": time_stats[0]["min_time"] if time_stats else 0,
            "max_processing_time_ms": time_stats[0]["max_time"] if time_stats else 0,
            "popular_topics": [topic["_id"] for topic in popular_topics],
            "daily_query_count": total_queries // 7
        }
    
    async def get_query_trends(self) -> List[Dict[str, Any]]:
        """Get daily query trends for the last 30 days"""
        await self.mongo_service.connect()
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        pipeline = [
            {
                "$match": {"created_at": {"$gte": thirty_days_ago}}
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        trends = await self.mongo_service.db.queries.aggregate(pipeline).to_list(30)
        return [{"date": trend["_id"], "count": trend["count"]} for trend in trends]
    
    async def get_source_analysis(self) -> Dict[str, Any]:
        """Analyze source domains and reliability"""
        await self.mongo_service.connect()
        
        # Get top domains
        domain_pipeline = [
            {"$unwind": "$sources"},
            {
                "$group": {
                    "_id": {
                        "$arrayElemAt": [
                            {"$split": [
                                {"$arrayElemAt": [
                                    {"$split": ["$sources.url", "//"]}, 1
                                ]}, "/"
                            ]}, 0
                        ]
                    },
                    "count": {"$sum": 1},
                    "avg_relevance": {"$avg": "$sources.relevance_score"}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        domains = await self.mongo_service.db.results.aggregate(domain_pipeline).to_list(10)
        
        return {
            "top_domains": [
                {
                    "domain": domain["_id"],
                    "usage_count": domain["count"],
                    "avg_relevance_score": round(domain["avg_relevance"], 3)
                }
                for domain in domains if domain["_id"]
            ]
        }


# Create service instance
from .mongo_service import mongo_service
analytics_service = AnalyticsService(mongo_service)
