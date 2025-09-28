#!/usr/bin/env python3
"""
Test database integration by manually triggering startup events
"""

import sys
import os
import asyncio

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

async def test_database_with_startup():
    """Test database integration with proper startup"""
    print("🧪 Testing Database Integration with Manual Startup")
    print("=" * 60)
    
    try:
        # Import app and manually trigger startup
        from app import app, startup_event
        
        print("✅ App imported successfully")
        
        # Manually call startup event
        print("\n1️⃣ Triggering startup event...")
        await startup_event()
        
        # Now test with TestClient
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        print("✅ TestClient created after startup")
        
        # Test health check
        print("\n2️⃣ Testing health check...")
        response = client.get("/health")
        health_data = response.json()
        
        print(f"   Status: {response.status_code}")
        print(f"   Agent initialized: {health_data.get('agent_initialized')}")
        print(f"   Database connected: {health_data.get('database_connected')}")
        print(f"   Database available: {health_data.get('database_available')}")
        
        if not health_data.get('database_connected'):
            print("   ❌ Database still not connected after startup!")
            return False
            
        # Test research endpoint
        print("\n3️⃣ Testing research endpoint...")
        test_data = {
            "query": "Database integration test: What is AI?",
            "user_session": "startup-test"
        }
        
        response = client.post("/research", json=test_data)
        if response.status_code == 200:
            research_data = response.json()
            query_id = research_data.get('query_id')
            
            print(f"   ✅ Research successful!")
            print(f"   Query ID: {query_id}")
            print(f"   Success: {research_data.get('success')}")
            
            if query_id:
                print("   🎉 DATABASE WRITE SUCCESSFUL!")
                return query_id
            else:
                print("   ❌ No query_id - database write failed")
                return False
        else:
            print(f"   ❌ Research failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_direct_database():
    """Test database directly to verify connection"""
    print("\n4️⃣ Testing direct database connection...")
    
    try:
        from database.services.mongo_service import MongoService
        
        service = MongoService()
        await service.connect()
        
        # Create test query
        query_id = await service.create_query({
            "query_text": "Direct database test",
            "user_session": "direct-test"
        })
        
        print(f"   ✅ Direct database test successful!")
        print(f"   Created query ID: {query_id}")
        
        await service.disconnect()
        return True
        
    except Exception as e:
        print(f"   ❌ Direct database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🗄️  Complete Database Integration Test")
    print("Testing if Team B successfully integrated database with backend")
    print()
    
    # Test 1: Direct database
    direct_success = await test_direct_database()
    
    # Test 2: FastAPI integration
    api_success = await test_database_with_startup()
    
    print("\n" + "=" * 60)
    if direct_success and api_success:
        print("🎉 SUCCESS: TEAM B OBJECTIVE COMPLETE!")
        print("✅ Database connection working")
        print("✅ Backend successfully writes to MongoDB")
        print(f"✅ API returns query_id: {api_success}")
        print("✅ Full integration pipeline working")
        return True
    else:
        print("❌ FAILED: Database integration incomplete")
        if not direct_success:
            print("❌ Direct database connection failed")
        if not api_success:
            print("❌ API database integration failed")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
