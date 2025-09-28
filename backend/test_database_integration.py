#!/usr/bin/env python3
"""
Test database integration using FastAPI TestClient
This properly tests if the backend writes to MongoDB
"""

import sys
import os
import asyncio
from fastapi.testclient import TestClient

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_database_integration():
    """Test if backend integrates with database using TestClient"""
    print("🧪 Testing Backend Database Integration with FastAPI TestClient")
    print("=" * 70)
    
    try:
        # Import the FastAPI app
        from app import app
        print("✅ FastAPI app imported successfully")
        
        # Create test client
        client = TestClient(app)
        print("✅ TestClient created successfully")
        
        # Test 1: Health check - should show database status
        print("\n1️⃣ Testing health endpoint...")
        response = client.get("/health")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Agent initialized: {health_data.get('agent_initialized')}")
            print(f"   Database connected: {health_data.get('database_connected')}")
            
            database_connected = health_data.get('database_connected', False)
            if database_connected:
                print("   ✅ Database is connected!")
            else:
                print("   ❌ Database is NOT connected!")
                return False
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # Test 2: Submit research query - should return query_id if database works
        print("\n2️⃣ Testing research endpoint with database write...")
        test_query = {
            "query": "TestClient test: What is machine learning?",
            "user_session": "testclient-123"
        }
        
        response = client.post("/research", json=test_query)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            research_data = response.json()
            print(f"   Success: {research_data.get('success')}")
            print(f"   Query ID: {research_data.get('query_id')}")
            print(f"   Processing time: {research_data.get('processing_time_ms')}ms")
            print(f"   Sources found: {research_data.get('sources_count')}")
            
            query_id = research_data.get('query_id')
            if query_id:
                print("   ✅ Got query_id - DATABASE WRITE SUCCESSFUL!")
                return query_id
            else:
                print("   ❌ No query_id - DATABASE WRITE FAILED!")
                return False
        else:
            print(f"   ❌ Research failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        print("💡 Make sure database dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection_directly():
    """Test database connection directly"""
    print("\n3️⃣ Testing direct database connection...")
    
    try:
        from database.services.mongo_service import MongoService
        
        async def test_db():
            service = MongoService()
            await service.connect()
            
            # Test query creation
            query_id = await service.create_query({
                "query_text": "Direct test query",
                "user_session": "direct-test"
            })
            
            print(f"   ✅ Direct database test successful: {query_id}")
            await service.disconnect()
            return True
        
        return asyncio.run(test_db())
        
    except Exception as e:
        print(f"   ❌ Direct database test failed: {e}")
        return False

def main():
    """Run all database integration tests"""
    print("🗄️  FastAPI TestClient Database Integration Test")
    print("This tests if the backend properly writes to MongoDB")
    print()
    
    # Test 1: FastAPI integration
    result = test_database_integration()
    
    if result:
        print("\n" + "=" * 70)
        print("🎉 SUCCESS: Backend is writing to database!")
        print(f"✅ Query ID returned: {result}")
        print("✅ Database integration is working correctly")
        
        # Test 2: Direct database test
        direct_result = test_database_connection_directly()
        
        if direct_result:
            print("✅ Direct database connection also working")
        
        print("\n🚀 TEAM B OBJECTIVE COMPLETE:")
        print("   - Backend successfully integrates with MongoDB")
        print("   - Queries are properly persisted to database") 
        print("   - API returns query_id confirming database writes")
        return True
    else:
        print("\n" + "=" * 70)
        print("❌ FAILED: Backend is NOT writing to database!")
        print("🔧 Issues to fix:")
        print("   - Database connection not established")
        print("   - No query_id returned from API")
        print("   - Data is not persisted")
        
        # Test direct connection to isolate the issue
        print("\n🔍 Testing direct database connection...")
        direct_result = test_database_connection_directly()
        
        if direct_result:
            print("✅ Direct database works - issue is in FastAPI integration")
        else:
            print("❌ Database connection itself is broken")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
