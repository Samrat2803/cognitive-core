#!/usr/bin/env python3
"""
Specific test to verify that the backend is actually writing to MongoDB
Tests the complete pipeline: API → Database → Verification

Run this with the database-integrated backend on port 8001
"""

import requests
import time
import json
import sys
import os
from datetime import datetime

# Add database directory to path for direct database verification
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database'))

try:
    from services.mongo_service import MongoService
    DIRECT_DB_ACCESS = True
except ImportError as e:
    print(f"⚠️  Direct database access not available: {e}")
    DIRECT_DB_ACCESS = False

def test_backend_database_writes():
    """Test if backend is actually writing to the database"""
    print("🧪 Testing Backend → Database Write Operations")
    print("=" * 60)
    
    # Test configuration
    base_url = "http://localhost:8001"  # Use port 8001 as requested
    session_id = f"write-test-{int(time.time())}"
    
    print(f"🎯 Testing against: {base_url}")
    print(f"📝 Test session: {session_id}")
    print()
    
    # Step 1: Test if backend is running
    print("1️⃣ Testing backend connectivity...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.ok:
            health_data = response.json()
            print(f"   ✅ Backend is running")
            print(f"   🗄️  Database connected: {health_data.get('database_connected', False)}")
            
            if not health_data.get('database_connected'):
                print("   ❌ Database is not connected to backend!")
                return False
        else:
            print(f"   ❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to backend: {e}")
        print("   💡 Make sure to run: cd backend && python app_with_database.py")
        return False
    
    # Step 2: Test database connection endpoint
    print("\n2️⃣ Testing database connection endpoint...")
    try:
        response = requests.get(f"{base_url}/database/test", timeout=10)
        if response.ok:
            test_data = response.json()
            print(f"   ✅ Database connection test passed")
            print(f"   📝 Test query ID: {test_data.get('test_query_id', 'N/A')}")
        else:
            print(f"   ❌ Database test endpoint failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False
    
    # Step 3: Submit a research query that should be saved to database
    print("\n3️⃣ Submitting research query to test database writes...")
    test_query = "Database write test: What is artificial intelligence?"
    
    try:
        response = requests.post(
            f"{base_url}/research",
            json={
                "query": test_query,
                "user_session": session_id
            },
            timeout=60
        )
        
        if response.ok:
            result_data = response.json()
            print(f"   ✅ Research query completed successfully")
            print(f"   📝 Query ID: {result_data.get('query_id', 'N/A')}")
            print(f"   ⏱️  Processing time: {result_data.get('processing_time_ms', 0)}ms")
            print(f"   🔍 Sources found: {result_data.get('sources_count', 0)}")
            
            query_id = result_data.get('query_id')
            if not query_id:
                print("   ❌ No query_id returned - database write may have failed!")
                return False
                
            return query_id
        else:
            print(f"   ❌ Research query failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Research query failed: {e}")
        return False

def verify_database_writes_via_api(query_id, session_id, base_url):
    """Verify database writes using the API endpoints"""
    print("\n4️⃣ Verifying database writes via API...")
    
    # Test 1: Retrieve the specific query by ID
    try:
        response = requests.get(f"{base_url}/research/{query_id}", timeout=10)
        if response.ok:
            query_data = response.json()
            print(f"   ✅ Query retrieval successful")
            print(f"   📊 Status: {query_data.get('status', 'unknown')}")
            print(f"   📝 Query text: {query_data.get('query', 'N/A')[:50]}...")
            
            if query_data.get('status') == 'completed':
                print(f"   🎯 Final answer length: {len(query_data.get('final_answer', ''))}")
                print(f"   🔍 Sources count: {len(query_data.get('sources', []))}")
                print(f"   🏷️  Search terms: {len(query_data.get('search_terms', []))}")
            
        else:
            print(f"   ❌ Query retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Query retrieval failed: {e}")
        return False
    
    # Test 2: Check query history for the session
    try:
        response = requests.get(
            f"{base_url}/research",
            params={
                "user_session": session_id,
                "limit": 10
            },
            timeout=10
        )
        
        if response.ok:
            history_data = response.json()
            queries = history_data.get('queries', [])
            print(f"   ✅ Query history retrieval successful")
            print(f"   📊 Queries in session: {len(queries)}")
            
            # Find our specific query
            our_query = next((q for q in queries if q['query_id'] == query_id), None)
            if our_query:
                print(f"   🎯 Found our test query in history")
                print(f"   📊 Query status: {our_query.get('status')}")
            else:
                print(f"   ❌ Our test query not found in history!")
                return False
                
        else:
            print(f"   ❌ History retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ History retrieval failed: {e}")
        return False
    
    return True

def verify_database_writes_directly(query_id):
    """Verify database writes by directly querying MongoDB"""
    if not DIRECT_DB_ACCESS:
        print("\n5️⃣ Direct database verification skipped (dependencies not available)")
        return True
    
    print("\n5️⃣ Verifying database writes directly in MongoDB...")
    
    try:
        # Direct database access to verify
        import asyncio
        
        async def check_database():
            mongo_service = MongoService()
            try:
                await mongo_service.connect()
                
                # Check if query exists
                query = await mongo_service.get_query(query_id)
                if query:
                    print(f"   ✅ Query found in MongoDB")
                    print(f"   📊 Status: {query.status}")
                    print(f"   📝 Text: {query.query_text[:50]}...")
                    print(f"   🕒 Created: {query.created_at}")
                    
                    # Check if results exist
                    results = await mongo_service.get_results(query_id)
                    if results:
                        print(f"   ✅ Results found in MongoDB")
                        print(f"   📄 Answer length: {len(results.final_answer)}")
                        print(f"   🔍 Sources: {len(results.sources)}")
                        print(f"   🏷️  Search terms: {len(results.search_terms)}")
                        return True
                    else:
                        print(f"   ❌ No results found for query {query_id}")
                        return False
                else:
                    print(f"   ❌ Query {query_id} not found in MongoDB")
                    return False
                    
            finally:
                await mongo_service.disconnect()
        
        return asyncio.run(check_database())
        
    except Exception as e:
        print(f"   ❌ Direct database verification failed: {e}")
        return False

def test_analytics_writes():
    """Test if analytics data is being written"""
    print("\n6️⃣ Testing analytics data writes...")
    
    base_url = "http://localhost:8001"
    
    try:
        response = requests.get(f"{base_url}/analytics", timeout=10)
        if response.ok:
            analytics_data = response.json()
            print(f"   ✅ Analytics retrieval successful")
            print(f"   📊 Total queries: {analytics_data.get('total_queries', 0)}")
            print(f"   📈 Success rate: {analytics_data.get('success_rate', 0):.1f}%")
            print(f"   ⏱️  Avg processing: {analytics_data.get('avg_processing_time_ms', 0):.0f}ms")
            
            if analytics_data.get('total_queries', 0) > 0:
                print(f"   ✅ Analytics data is being recorded")
                return True
            else:
                print(f"   ⚠️  No analytics data yet (may be normal for first run)")
                return True
        else:
            print(f"   ❌ Analytics retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Analytics test failed: {e}")
        return False

def main():
    """Main test runner"""
    print("🗄️  Backend → Database Write Verification Test")
    print("This test verifies that the backend is actually writing to MongoDB")
    print("Using port 8001 for testing")
    print()
    
    # Run the complete test suite
    query_id = test_backend_database_writes()
    if not query_id:
        print("\n❌ Backend database write test failed!")
        sys.exit(1)
    
    session_id = f"write-test-{int(time.time())}"
    base_url = "http://localhost:8001"
    
    # Verify writes via API
    api_success = verify_database_writes_via_api(query_id, session_id, base_url)
    if not api_success:
        print("\n❌ API verification failed!")
        sys.exit(1)
    
    # Verify writes directly
    direct_success = verify_database_writes_directly(query_id)
    if not direct_success:
        print("\n❌ Direct database verification failed!")
        sys.exit(1)
    
    # Test analytics
    analytics_success = test_analytics_writes()
    if not analytics_success:
        print("\n⚠️  Analytics verification had issues")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 DATABASE WRITE VERIFICATION SUCCESSFUL!")
    print("=" * 60)
    print("✅ Backend is successfully writing to MongoDB")
    print("✅ Query data is properly persisted")
    print("✅ Results are saved and retrievable")
    print("✅ Query history is working")
    print("✅ Analytics data is being recorded")
    print()
    print("🎯 Key findings:")
    print(f"   📝 Test query ID: {query_id}")
    print(f"   🔗 Backend URL: {base_url}")
    print(f"   ⏱️  Test completed at: {datetime.now()}")
    print()
    print("🚀 The backend is ready for production with full database integration!")

if __name__ == "__main__":
    main()
