"""Database package for Team A integration"""
from .services.mongo_service import mongo_service
from .services.analytics_service import analytics_service
from .models.query_models import QueryDocument, ResultDocument, AnalyticsDocument

# Main service interface for Team A
class DatabaseInterface:
    """Main interface for database operations"""
    
    def __init__(self):
        self.mongo = mongo_service
        self.analytics = analytics_service
    
    async def initialize(self):
        """Initialize database connection"""
        await self.mongo.connect()
    
    async def cleanup(self):
        """Cleanup database connection"""
        await self.mongo.disconnect()

# Export main interface
db_interface = DatabaseInterface()

__all__ = [
    'db_interface', 
    'mongo_service', 
    'analytics_service',
    'QueryDocument', 
    'ResultDocument', 
    'AnalyticsDocument'
]
