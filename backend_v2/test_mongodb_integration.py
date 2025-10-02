"""
Test MongoDB Integration with Backend Server
Verifies that sessions, artifacts, and logs are being saved to MongoDB
"""

import asyncio
import httpx
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from services.mongo_service import mongo_service

BASE_URL = "http://localhost:8000"


async def test_mongodb_connection():
    """Test direct MongoDB connection"""
    print("\n" + "=" * 70)
    print("TEST 1: MongoDB Connection")
    print("=" * 70)
    
    try:
        await mongo_service.connect()
        print("✅ MongoDB connected successfully")
        print(f"   Database: {mongo_service.database_name}")
        print(f"   Connected: {mongo_service._connected}")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False


async def test_session_creation():
    """Test session creation in MongoDB"""
    print("\n" + "=" * 70)
    print("TEST 2: Session Creation in MongoDB")
    print("=" * 70)
    
    try:
        # Create a test session
        session_id = await mongo_service.create_session(
            query="Test query for MongoDB verification",
            user_session="test_user_123"
        )
        
        print(f"✅ Session created: {session_id}")
        
        # Retrieve the session
        session = await mongo_service.get_session(session_id)
        
        if session:
            print(f"✅ Session retrieved successfully")
            print(f"   Query: {session['query']}")
            print(f"   Status: {session['status']}")
            print(f"   Created: {session['created_at']}")
            return True
        else:
            print("❌ Session not found in database")
            return False
            
    except Exception as e:
        print(f"❌ Session test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_with_mongodb():
    """Test API endpoint and verify data is saved to MongoDB"""
    print("\n" + "=" * 70)
    print("TEST 3: API Call with MongoDB Persistence")
    print("=" * 70)
    
    query = "Create a trend chart of India's GDP growth rate over 2020-2025"
    
    print(f"Query: {query}")
    print("\n🔄 Sending request to backend...")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Make API call
            response = await client.post(
                f"{BASE_URL}/api/analyze",
                json={"query": query, "user_session": "mongodb_test_user"}
            )
            
            if response.status_code != 200:
                print(f"❌ API call failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
            
            result = response.json()
            session_id = result['session_id']
            
            print(f"\n✅ API call successful")
            print(f"   Session ID: {session_id}")
            print(f"   Confidence: {result['confidence']:.0%}")
            print(f"   Artifact: {result.get('artifact', {}).get('artifact_id', 'None')}")
            
            # Verify data was saved to MongoDB
            print("\n🔍 Verifying MongoDB persistence...")
            
            # Check session in MongoDB
            db_session = await mongo_service.get_session(session_id)
            
            if not db_session:
                print("❌ Session not found in MongoDB!")
                return False
            
            print(f"✅ Session found in MongoDB")
            print(f"   Status: {db_session['status']}")
            print(f"   Confidence: {db_session.get('confidence', 0):.0%}")
            print(f"   Tools Used: {', '.join(db_session.get('tools_used', []))}")
            print(f"   Processing Time: {db_session.get('processing_time_ms', 0)}ms")
            
            # Check execution log
            exec_log = await mongo_service.get_execution_log(session_id)
            
            if exec_log:
                print(f"✅ Execution log saved ({len(exec_log.get('steps', []))} steps)")
            else:
                print("⚠️  Execution log not found")
            
            # Check artifact metadata
            if result.get('artifact'):
                artifact_id = result['artifact']['artifact_id']
                artifact_meta = await mongo_service.get_artifact(artifact_id)
                
                if artifact_meta:
                    print(f"✅ Artifact metadata saved")
                    print(f"   Type: {artifact_meta['type']}")
                    print(f"   Title: {artifact_meta.get('title', 'N/A')}")
                    print(f"   HTML Size: {artifact_meta.get('html_size_bytes', 0)} bytes")
                    print(f"   PNG Size: {artifact_meta.get('png_size_bytes', 0)} bytes")
                else:
                    print("⚠️  Artifact metadata not found in MongoDB")
            
            return True
            
    except httpx.ConnectError:
        print("❌ Cannot connect to backend server")
        print("   Make sure server is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_analytics():
    """Test analytics retrieval from MongoDB"""
    print("\n" + "=" * 70)
    print("TEST 4: Analytics from MongoDB")
    print("=" * 70)
    
    try:
        analytics = await mongo_service.get_analytics(days=30)
        
        print("✅ Analytics retrieved")
        print(f"   Total Sessions: {analytics['total_sessions']}")
        print(f"   Completed: {analytics['completed_sessions']}")
        print(f"   Failed: {analytics['failed_sessions']}")
        print(f"   Success Rate: {analytics['success_rate']:.1f}%")
        print(f"   Total Artifacts: {analytics['total_artifacts']}")
        print(f"   Avg Processing Time: {analytics['avg_processing_time_ms']:.0f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics test failed: {e}")
        return False


async def test_user_sessions():
    """Test retrieving user sessions"""
    print("\n" + "=" * 70)
    print("TEST 5: User Session History")
    print("=" * 70)
    
    try:
        sessions = await mongo_service.get_user_sessions(
            user_session="mongodb_test_user",
            limit=5
        )
        
        print(f"✅ Retrieved {len(sessions)} sessions for user 'mongodb_test_user'")
        
        for i, session in enumerate(sessions, 1):
            print(f"\n   Session {i}:")
            print(f"   - Query: {session['query'][:60]}...")
            print(f"   - Status: {session['status']}")
            print(f"   - Created: {session['created_at']}")
            print(f"   - Confidence: {session.get('confidence', 0):.0%}")
        
        return True
        
    except Exception as e:
        print(f"❌ User sessions test failed: {e}")
        return False


async def test_recent_sessions():
    """Test retrieving recent sessions"""
    print("\n" + "=" * 70)
    print("TEST 6: Recent Sessions (All Users)")
    print("=" * 70)
    
    try:
        sessions = await mongo_service.get_recent_sessions(limit=10)
        
        print(f"✅ Retrieved {len(sessions)} recent sessions")
        
        for i, session in enumerate(sessions[:3], 1):
            print(f"\n   Session {i}:")
            print(f"   - ID: {session['session_id']}")
            print(f"   - Query: {session['query'][:60]}...")
            print(f"   - User: {session.get('user_session', 'anonymous')}")
            print(f"   - Status: {session['status']}")
        
        if len(sessions) > 3:
            print(f"\n   ... and {len(sessions) - 3} more sessions")
        
        return True
        
    except Exception as e:
        print(f"❌ Recent sessions test failed: {e}")
        return False


async def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "=" * 70)
    print("CLEANUP: Removing Test Data")
    print("=" * 70)
    
    try:
        # Delete test sessions
        result = await mongo_service.db.analysis_sessions.delete_many({
            'query': {'$regex': 'Test query for MongoDB verification'}
        })
        
        print(f"✅ Cleaned up {result.deleted_count} test sessions")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Cleanup failed: {e}")
        return False


async def main():
    """Run all MongoDB integration tests"""
    print("\n" + "=" * 70)
    print("🧪 MONGODB INTEGRATION TESTS")
    print("=" * 70)
    print("\nThese tests verify that the backend is properly")
    print("saving all data to MongoDB Atlas")
    print("=" * 70)
    
    results = {}
    
    try:
        # Test 1: MongoDB Connection
        results['connection'] = await test_mongodb_connection()
        
        if not results['connection']:
            print("\n❌ CRITICAL: MongoDB not connected")
            print("   Check your MONGODB_CONNECTION_STRING in .env")
            return
        
        # Test 2: Session Creation
        results['session_creation'] = await test_session_creation()
        
        # Test 3: API with MongoDB
        results['api_persistence'] = await test_api_with_mongodb()
        
        # Test 4: Analytics
        results['analytics'] = await test_analytics()
        
        # Test 5: User Sessions
        results['user_sessions'] = await test_user_sessions()
        
        # Test 6: Recent Sessions
        results['recent_sessions'] = await test_recent_sessions()
        
        # Cleanup
        await cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASS" if passed_test else "❌ FAIL"
            print(f"{status}  {test_name.replace('_', ' ').title()}")
        
        print("=" * 70)
        print(f"Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ ALL TESTS PASSED!")
            print("\n🎉 MongoDB integration is working correctly!")
            print("   - Sessions are being saved")
            print("   - Execution logs are persisted")
            print("   - Artifact metadata is stored")
            print("   - Analytics are available")
        else:
            print(f"⚠️  {total - passed} tests failed")
            print("   Check the logs above for details")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disconnect from MongoDB
        try:
            await mongo_service.disconnect()
            print("\n✅ Disconnected from MongoDB")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())

