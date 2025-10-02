"""
Quick script to verify data in MongoDB
Shows what's actually in the database
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from services.mongo_service import mongo_service


async def main():
    """Check what's in MongoDB"""
    print("=" * 70)
    print("🔍 MongoDB Data Verification")
    print("=" * 70)
    
    await mongo_service.connect()
    
    print(f"\n📊 Database: {mongo_service.database_name}")
    print(f"   Connected: {mongo_service._connected}")
    
    # Count documents in each collection
    print("\n📈 Collection Counts:")
    
    sessions_count = await mongo_service.db.analysis_sessions.count_documents({})
    print(f"   Analysis Sessions: {sessions_count}")
    
    artifacts_count = await mongo_service.db.artifacts.count_documents({})
    print(f"   Artifacts: {artifacts_count}")
    
    logs_count = await mongo_service.db.execution_logs.count_documents({})
    print(f"   Execution Logs: {logs_count}")
    
    # Show recent sessions
    print("\n📋 Recent Sessions:")
    sessions = await mongo_service.get_recent_sessions(limit=5)
    
    for i, session in enumerate(sessions, 1):
        print(f"\n   {i}. Session ID: {session['session_id']}")
        print(f"      Query: {session['query'][:60]}...")
        print(f"      Status: {session['status']}")
        print(f"      User: {session.get('user_session', 'anonymous')}")
        print(f"      Created: {session['created_at']}")
        if session.get('confidence'):
            print(f"      Confidence: {session['confidence']:.0%}")
        if session.get('artifact_id'):
            print(f"      Artifact: {session['artifact_id']}")
    
    # Show recent artifacts
    if artifacts_count > 0:
        print("\n🎨 Recent Artifacts:")
        cursor = mongo_service.db.artifacts.find().sort('created_at', -1).limit(3)
        artifacts = await cursor.to_list(length=3)
        
        for i, artifact in enumerate(artifacts, 1):
            print(f"\n   {i}. Artifact ID: {artifact['artifact_id']}")
            print(f"      Type: {artifact['type']}")
            print(f"      Session: {artifact.get('session_id', 'N/A')}")
            print(f"      Query: {artifact.get('query', 'N/A')[:50]}...")
            print(f"      Created: {artifact['created_at']}")
    
    print("\n" + "=" * 70)
    
    await mongo_service.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

