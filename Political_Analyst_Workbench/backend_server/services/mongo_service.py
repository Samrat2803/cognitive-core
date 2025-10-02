"""
MongoDB Service for Political Analyst Backend
Handles all database operations including sessions, artifacts, and analytics
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
from pymongo.errors import DuplicateKeyError
from pymongo import ASCENDING, DESCENDING
import os
from dotenv import load_dotenv
import ssl
import certifi

load_dotenv()


class AnalysisSession:
    """Model for analysis session"""
    def __init__(self, **kwargs):
        self.session_id: str = kwargs.get('session_id', str(uuid.uuid4()))
        self.query: str = kwargs['query']
        self.user_session: Optional[str] = kwargs.get('user_session')
        self.status: str = kwargs.get('status', 'processing')  # processing, completed, failed
        self.created_at: datetime = kwargs.get('created_at', datetime.utcnow())
        self.completed_at: Optional[datetime] = kwargs.get('completed_at')
        self.processing_time_ms: Optional[int] = kwargs.get('processing_time_ms')
        
        # Results
        self.response: Optional[str] = kwargs.get('response')
        self.confidence: float = kwargs.get('confidence', 0.0)
        self.citations: List[Dict] = kwargs.get('citations', [])
        self.tools_used: List[str] = kwargs.get('tools_used', [])
        self.iterations: int = kwargs.get('iterations', 0)
        
        # Artifact reference
        self.artifact_id: Optional[str] = kwargs.get('artifact_id')
        
        # Error tracking
        self.error_message: Optional[str] = kwargs.get('error_message')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB"""
        return {
            'session_id': self.session_id,
            'query': self.query,
            'user_session': self.user_session,
            'status': self.status,
            'created_at': self.created_at,
            'completed_at': self.completed_at,
            'processing_time_ms': self.processing_time_ms,
            'response': self.response,
            'confidence': self.confidence,
            'citations': self.citations,
            'tools_used': self.tools_used,
            'iterations': self.iterations,
            'artifact_id': self.artifact_id,
            'error_message': self.error_message
        }


class ArtifactMetadata:
    """Model for artifact metadata"""
    def __init__(self, **kwargs):
        self.artifact_id: str = kwargs['artifact_id']
        self.session_id: str = kwargs['session_id']
        self.type: str = kwargs['type']  # bar_chart, line_chart, mind_map
        self.title: str = kwargs.get('title', '')
        self.created_at: datetime = kwargs.get('created_at', datetime.utcnow())
        
        # File references
        self.html_file_id: Optional[str] = kwargs.get('html_file_id')  # GridFS file ID
        self.png_file_id: Optional[str] = kwargs.get('png_file_id')    # GridFS file ID
        self.html_url: Optional[str] = kwargs.get('html_url')          # External URL (deprecated)
        self.png_url: Optional[str] = kwargs.get('png_url')            # External URL (deprecated)
        
        # S3 storage
        self.s3_html_key: Optional[str] = kwargs.get('s3_html_key')    # S3 key for HTML
        self.s3_png_key: Optional[str] = kwargs.get('s3_png_key')      # S3 key for PNG
        self.s3_html_url: Optional[str] = kwargs.get('s3_html_url')    # Presigned URL (temp)
        self.s3_png_url: Optional[str] = kwargs.get('s3_png_url')      # Presigned URL (temp)
        self.storage: str = kwargs.get('storage', 'local')              # 'local' or 's3'
        
        # Local paths (for backward compatibility)
        self.html_path: Optional[str] = kwargs.get('html_path')
        self.png_path: Optional[str] = kwargs.get('png_path')
        
        # Data used to create artifact
        self.data: Dict[str, Any] = kwargs.get('data', {})
        self.query: str = kwargs.get('query', '')
        
        # Size tracking
        self.html_size_bytes: int = kwargs.get('html_size_bytes', 0)
        self.png_size_bytes: int = kwargs.get('png_size_bytes', 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB"""
        return {
            'artifact_id': self.artifact_id,
            'session_id': self.session_id,
            'type': self.type,
            'title': self.title,
            'created_at': self.created_at,
            's3_html_key': self.s3_html_key,      # Store S3 keys (permanent)
            's3_png_key': self.s3_png_key,        # Store S3 keys (permanent)
            's3_html_url': self.s3_html_url,      # Presigned URL (optional, for backward compat)
            's3_png_url': self.s3_png_url,        # Presigned URL (optional, for backward compat)
            'storage': self.storage,
            'html_path': self.html_path,
            'png_path': self.png_path,
            'html_file_id': self.html_file_id,
            'png_file_id': self.png_file_id,
            'html_url': self.html_url,
            'png_url': self.png_url,
            'data': self.data,
            'query': self.query,
            'html_size_bytes': self.html_size_bytes,
            'png_size_bytes': self.png_size_bytes
        }


class MongoService:
    """MongoDB service for Political Analyst backend"""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv("MONGODB_CONNECTION_STRING")
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.gridfs: Optional[AsyncIOMotorGridFSBucket] = None
        self.database_name = os.getenv("DATABASE_NAME", "political_analyst_db")
        self._connected = False
    
    async def connect(self):
        """Connect to MongoDB Atlas"""
        if self._connected:
            return
        
        if not self.connection_string:
            raise RuntimeError("Missing MONGODB_CONNECTION_STRING environment variable")
        
        try:
            print("🔗 Connecting to MongoDB Atlas...")
            self.client = AsyncIOMotorClient(
                self.connection_string,
                tls=True,
                tlsCAFile=certifi.where(),
                tlsDisableOCSPEndpointCheck=True,
                serverSelectionTimeoutMS=30000
            )
            
            # Verify connection
            await self.client.admin.command("ping")
            print("✅ MongoDB connection verified")
            
            self.db = self.client[self.database_name]
            self.gridfs = AsyncIOMotorGridFSBucket(self.db)
            
            await self._create_indexes()
            self._connected = True
            print(f"✅ Database initialized: {self.database_name}")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            self.gridfs = None
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.gridfs = None
            self._connected = False
    
    async def _create_indexes(self):
        """Create database indexes for performance"""
        if self.db is None:
            return
        
        try:
            # Analysis sessions indexes
            await self.db.analysis_sessions.create_index("session_id", unique=True)
            await self.db.analysis_sessions.create_index("user_session")
            await self.db.analysis_sessions.create_index("status")
            await self.db.analysis_sessions.create_index([("created_at", DESCENDING)])
            
            # Artifacts indexes
            await self.db.artifacts.create_index("artifact_id", unique=True)
            await self.db.artifacts.create_index("session_id")
            await self.db.artifacts.create_index("type")
            await self.db.artifacts.create_index([("created_at", DESCENDING)])
            
            # Execution logs indexes
            await self.db.execution_logs.create_index("session_id")
            await self.db.execution_logs.create_index([("timestamp", DESCENDING)])
            
            print("✅ Database indexes created")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not create indexes: {e}")
    
    # ========================================================================
    # Analysis Session Management
    # ========================================================================
    
    async def create_session(self, query: str, user_session: Optional[str] = None) -> str:
        """Create a new analysis session"""
        await self.connect()
        
        session = AnalysisSession(
            query=query,
            user_session=user_session
        )
        
        await self.db.analysis_sessions.insert_one(session.to_dict())
        return session.session_id
    
    async def update_session(
        self, 
        session_id: str, 
        status: str = None,
        response: str = None,
        confidence: float = None,
        citations: List[Dict] = None,
        tools_used: List[str] = None,
        iterations: int = None,
        artifact_id: str = None,
        processing_time_ms: int = None,
        error_message: str = None
    ) -> bool:
        """Update analysis session"""
        await self.connect()
        
        update_data = {}
        
        if status:
            update_data['status'] = status
            if status == 'completed':
                update_data['completed_at'] = datetime.utcnow()
        
        if response is not None:
            update_data['response'] = response
        if confidence is not None:
            update_data['confidence'] = confidence
        if citations is not None:
            update_data['citations'] = citations
        if tools_used is not None:
            update_data['tools_used'] = tools_used
        if iterations is not None:
            update_data['iterations'] = iterations
        if artifact_id:
            update_data['artifact_id'] = artifact_id
        if processing_time_ms is not None:
            update_data['processing_time_ms'] = processing_time_ms
        if error_message:
            update_data['error_message'] = error_message
        
        result = await self.db.analysis_sessions.update_one(
            {'session_id': session_id},
            {'$set': update_data}
        )
        
        return result.modified_count > 0
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis session by ID"""
        await self.connect()
        return await self.db.analysis_sessions.find_one({'session_id': session_id})
    
    async def get_user_sessions(
        self, 
        user_session: str, 
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get sessions for a user"""
        await self.connect()
        
        cursor = self.db.analysis_sessions.find(
            {'user_session': user_session}
        ).sort('created_at', DESCENDING).skip(offset).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent sessions"""
        await self.connect()
        
        cursor = self.db.analysis_sessions.find().sort('created_at', DESCENDING).limit(limit)
        return await cursor.to_list(length=limit)
    
    # ========================================================================
    # Artifact Management
    # ========================================================================
    
    async def save_artifact_metadata(self, artifact: ArtifactMetadata) -> bool:
        """Save artifact metadata"""
        await self.connect()
        
        await self.db.artifacts.insert_one(artifact.to_dict())
        return True
    
    async def upload_artifact_file(
        self, 
        artifact_id: str,
        file_content: bytes,
        filename: str,
        content_type: str
    ) -> str:
        """Upload artifact file to GridFS"""
        await self.connect()
        
        file_id = await self.gridfs.upload_from_stream(
            filename,
            file_content,
            metadata={
                'artifact_id': artifact_id,
                'content_type': content_type,
                'uploaded_at': datetime.utcnow()
            }
        )
        
        return str(file_id)
    
    async def download_artifact_file(self, file_id: str) -> bytes:
        """Download artifact file from GridFS"""
        await self.connect()
        
        from bson import ObjectId
        grid_out = await self.gridfs.open_download_stream(ObjectId(file_id))
        return await grid_out.read()
    
    async def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Get artifact metadata"""
        await self.connect()
        return await self.db.artifacts.find_one({'artifact_id': artifact_id})
    
    async def get_session_artifacts(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all artifacts for a session"""
        await self.connect()
        
        cursor = self.db.artifacts.find({'session_id': session_id})
        return await cursor.to_list(length=None)
    
    async def delete_artifact(self, artifact_id: str) -> bool:
        """Delete artifact and its files"""
        await self.connect()
        
        # Get artifact to find file IDs
        artifact = await self.get_artifact(artifact_id)
        if not artifact:
            return False
        
        # Delete files from GridFS
        from bson import ObjectId
        if artifact.get('html_file_id'):
            await self.gridfs.delete(ObjectId(artifact['html_file_id']))
        if artifact.get('png_file_id'):
            await self.gridfs.delete(ObjectId(artifact['png_file_id']))
        
        # Delete metadata
        result = await self.db.artifacts.delete_one({'artifact_id': artifact_id})
        return result.deleted_count > 0
    
    # ========================================================================
    # Execution Logs
    # ========================================================================
    
    async def save_execution_log(
        self, 
        session_id: str, 
        execution_log: List[Dict[str, Any]]
    ) -> bool:
        """Save execution log for a session"""
        await self.connect()
        
        log_doc = {
            'session_id': session_id,
            'steps': execution_log,
            'created_at': datetime.utcnow()
        }
        
        await self.db.execution_logs.insert_one(log_doc)
        return True
    
    async def get_execution_log(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get execution log for a session"""
        await self.connect()
        return await self.db.execution_logs.find_one({'session_id': session_id})
    
    # ========================================================================
    # Analytics
    # ========================================================================
    
    async def get_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics for the last N days"""
        await self.connect()
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Total sessions
        total_sessions = await self.db.analysis_sessions.count_documents(
            {'created_at': {'$gte': cutoff_date}}
        )
        
        # Completed sessions
        completed_sessions = await self.db.analysis_sessions.count_documents(
            {'status': 'completed', 'created_at': {'$gte': cutoff_date}}
        )
        
        # Failed sessions
        failed_sessions = await self.db.analysis_sessions.count_documents(
            {'status': 'failed', 'created_at': {'$gte': cutoff_date}}
        )
        
        # Total artifacts
        total_artifacts = await self.db.artifacts.count_documents(
            {'created_at': {'$gte': cutoff_date}}
        )
        
        # Average processing time
        pipeline = [
            {'$match': {
                'status': 'completed',
                'processing_time_ms': {'$exists': True},
                'created_at': {'$gte': cutoff_date}
            }},
            {'$group': {
                '_id': None,
                'avg_time': {'$avg': '$processing_time_ms'},
                'min_time': {'$min': '$processing_time_ms'},
                'max_time': {'$max': '$processing_time_ms'}
            }}
        ]
        
        timing_result = await self.db.analysis_sessions.aggregate(pipeline).to_list(length=1)
        timing_stats = timing_result[0] if timing_result else {
            'avg_time': 0, 
            'min_time': 0, 
            'max_time': 0
        }
        
        return {
            'period_days': days,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'failed_sessions': failed_sessions,
            'success_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'total_artifacts': total_artifacts,
            'avg_processing_time_ms': timing_stats['avg_time'],
            'min_processing_time_ms': timing_stats['min_time'],
            'max_processing_time_ms': timing_stats['max_time']
        }


# Singleton instance
mongo_service = MongoService()


if __name__ == "__main__":
    async def _smoke_test():
        """Test MongoDB connection"""
        try:
            service = MongoService()
            await service.connect()
            print(f"✅ Connected to database: {service.database_name}")
            
            # Test session creation
            session_id = await service.create_session("Test query", "test_user")
            print(f"✅ Created test session: {session_id}")
            
            # Test session retrieval
            session = await service.get_session(session_id)
            print(f"✅ Retrieved session: {session['query']}")
            
            # Get analytics
            analytics = await service.get_analytics(30)
            print(f"✅ Analytics: {analytics}")
            
            await service.disconnect()
            print("✅ Disconnected cleanly")
            
        except Exception as e:
            print(f"❌ Smoke test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(_smoke_test())

