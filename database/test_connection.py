#!/usr/bin/env python3
"""
Quick test script to verify MongoDB database connection and basic operations
Run this to verify Team B database service is working correctly
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

try:
    from services.mongo_service import MongoService
    from services.analytics_service import AnalyticsService
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure to install dependencies: uv pip install motor pymongo pydantic python-dotenv")
    sys.exit(1)


async def test_database_connection():
    """Test database connection and basic operations"""
    print("🧪 Testing Team B Database Service...")
    print("=" * 50)
    
    # Initialize service
    mongo_service = MongoService()
    analytics_service = AnalyticsService(mongo_service)
    
    try:
        # Test 1: Connection
        print("1️⃣ Testing MongoDB connection...")
        await mongo_service.connect()
        print("   ✅ Connection successful!")
        
        # Test 2: Query creation
        print("\n2️⃣ Testing query creation...")
        query_id = await mongo_service.create_query({
            "query_text": "Test query for database verification",
            "user_session": "test-session-123"
        })
        print(f"   ✅ Query created with ID: {query_id}")
        
        # Test 3: Status update
        print("\n3️⃣ Testing status updates...")
        success = await mongo_service.update_query_status(query_id, "processing")
        assert success, "Status update failed"
        print("   ✅ Status updated to processing")
        
        # Test 4: Query retrieval
        print("\n4️⃣ Testing query retrieval...")
        query_doc = await mongo_service.get_query(query_id)
        assert query_doc is not None, "Query retrieval failed"
        assert query_doc.query_text == "Test query for database verification"
        print(f"   ✅ Query retrieved: {query_doc.status}")
        
        # Test 5: Results saving
        print("\n5️⃣ Testing results saving...")
        test_results = {
            "final_answer": "This is a test answer from Team B database service",
            "search_terms": ["test", "database", "verification"],
            "sources": [
                {
                    "url": "https://example.com/test",
                    "title": "Test Source",
                    "relevance_score": 0.95,
                    "content_snippet": "This is a test source for verification"
                }
            ],
            "agent_workflow": [
                {
                    "step_name": "Test Analysis",
                    "duration_ms": 1000,
                    "output_summary": "Analyzed test query successfully",
                    "agent_type": "test_agent"
                }
            ]
        }
        
        await mongo_service.save_results(query_id, test_results)
        print("   ✅ Results saved successfully")
        
        # Test 6: Results retrieval
        print("\n6️⃣ Testing results retrieval...")
        result_doc = await mongo_service.get_results(query_id)
        assert result_doc is not None, "Results retrieval failed"
        assert "test answer" in result_doc.final_answer.lower()
        print(f"   ✅ Results retrieved: {len(result_doc.sources)} sources")
        
        # Test 7: Analytics
        print("\n7️⃣ Testing analytics...")
        await mongo_service.record_analytics(query_id, 5000)
        dashboard_data = await analytics_service.get_dashboard_data()
        print(f"   ✅ Analytics recorded: {dashboard_data['total_queries']} total queries")
        
        # Test 8: Query completion
        print("\n8️⃣ Testing query completion...")
        await mongo_service.update_query_status(query_id, "completed", processing_time_ms=5000)
        final_query = await mongo_service.get_query(query_id)
        assert final_query.status == "completed"
        print(f"   ✅ Query marked completed: {final_query.processing_time_ms}ms")
        
        # Summary
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Team B Database Service is ready for Team A integration")
        print("✅ MongoDB Atlas connection working")
        print("✅ All CRUD operations functional")
        print("✅ Analytics service operational")
        print("\n📋 Integration ready!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("🔧 Check:")
        print("   - MongoDB connection string in backend/.env")
        print("   - Network connectivity to MongoDB Atlas")
        print("   - Required dependencies installed")
        return False
        
    finally:
        await mongo_service.disconnect()
        
    return True


def main():
    """Run the test"""
    print("Starting Team B Database Service Test...")
    print("This will verify MongoDB connection and all operations\n")
    
    # Check if running in the right environment
    if not os.path.exists("services") or not os.path.exists("models"):
        print("❌ Please run this script from the database/ directory")
        print("   cd database/")
        print("   python test_connection.py")
        sys.exit(1)
    
    # Run the async test
    result = asyncio.run(test_database_connection())
    
    if result:
        print("\n🚀 Team A can now integrate the database service!")
        print("📖 See database/INTEGRATION_GUIDE.md for full integration details")
    else:
        print("\n⚠️  Fix the issues above and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()
