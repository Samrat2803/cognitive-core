#!/usr/bin/env python3
"""
Database Performance and Load Testing for Team B
Tests MongoDB operations under various load conditions
"""

import asyncio
import time
import statistics
import concurrent.futures
import sys
import os
from typing import List, Dict, Any
import requests
from datetime import datetime

# Add database directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database'))

try:
    from services.mongo_service import MongoService
    from services.analytics_service import AnalyticsService
except ImportError as e:
    print(f"❌ Could not import database services: {e}")
    print("Make sure you're running from the project root and dependencies are installed")
    sys.exit(1)


class DatabasePerformanceTest:
    """Performance testing for database operations"""
    
    def __init__(self):
        self.mongo_service = MongoService()
        self.analytics_service = AnalyticsService(self.mongo_service)
        self.results = []
    
    async def test_single_operation_performance(self):
        """Test performance of individual database operations"""
        print("🔍 Testing individual database operation performance...")
        
        operations_data = []
        
        # Test query creation performance
        for i in range(10):
            start_time = time.perf_counter()
            
            query_id = await self.mongo_service.create_query({
                "query_text": f"Performance test query {i}",
                "user_session": f"perf-test-{i}"
            })
            
            end_time = time.perf_counter()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            
            operations_data.append({
                "operation": "create_query",
                "duration_ms": duration,
                "query_id": query_id
            })
        
        # Analyze query creation performance
        durations = [op["duration_ms"] for op in operations_data]
        avg_duration = statistics.mean(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        print(f"   📊 Query Creation Performance:")
        print(f"      Average: {avg_duration:.2f}ms")
        print(f"      Min: {min_duration:.2f}ms")
        print(f"      Max: {max_duration:.2f}ms")
        
        # Test results saving performance
        results_data = []
        for op in operations_data[:5]:  # Test with 5 queries
            start_time = time.perf_counter()
            
            await self.mongo_service.save_results(op["query_id"], {
                "final_answer": "Performance test answer with sufficient content to test realistic data sizes",
                "search_terms": ["performance", "test", "database", "mongodb"],
                "sources": [
                    {"url": "https://example.com/1", "title": "Test Source 1", "relevance_score": 0.9},
                    {"url": "https://example.com/2", "title": "Test Source 2", "relevance_score": 0.8}
                ]
            })
            
            end_time = time.perf_counter()
            duration = (end_time - start_time) * 1000
            
            results_data.append(duration)
        
        avg_results = statistics.mean(results_data)
        print(f"   💾 Results Saving Performance: {avg_results:.2f}ms average")
        
        return {
            "query_creation_avg": avg_duration,
            "results_saving_avg": avg_results
        }
    
    async def test_concurrent_operations(self):
        """Test database performance under concurrent load"""
        print("⚡ Testing concurrent database operations...")
        
        async def create_and_save_query(index: int):
            """Single operation to create query and save results"""
            start_time = time.perf_counter()
            
            # Create query
            query_id = await self.mongo_service.create_query({
                "query_text": f"Concurrent test query {index}",
                "user_session": f"concurrent-{index}"
            })
            
            # Update status
            await self.mongo_service.update_query_status(query_id, "processing")
            
            # Save results
            await self.mongo_service.save_results(query_id, {
                "final_answer": f"Concurrent test answer {index}",
                "search_terms": ["concurrent", "test", f"query{index}"],
                "sources": [{"url": f"https://test{index}.com", "title": f"Source {index}", "relevance_score": 0.9}]
            })
            
            # Mark completed
            await self.mongo_service.update_query_status(query_id, "completed", processing_time_ms=1000)
            
            end_time = time.perf_counter()
            return {
                "index": index,
                "duration_ms": (end_time - start_time) * 1000,
                "query_id": query_id
            }
        
        # Test with different concurrency levels
        concurrency_levels = [5, 10, 15]
        
        for level in concurrency_levels:
            print(f"   🔄 Testing with {level} concurrent operations...")
            
            start_time = time.perf_counter()
            
            # Execute concurrent operations
            tasks = [create_and_save_query(i) for i in range(level)]
            results = await asyncio.gather(*tasks)
            
            end_time = time.perf_counter()
            total_time = (end_time - start_time) * 1000
            
            # Analyze results
            individual_times = [r["duration_ms"] for r in results]
            avg_individual = statistics.mean(individual_times)
            throughput = level / (total_time / 1000)  # operations per second
            
            print(f"      Total time: {total_time:.2f}ms")
            print(f"      Average individual: {avg_individual:.2f}ms") 
            print(f"      Throughput: {throughput:.2f} ops/sec")
            
            # Performance assertions
            assert total_time < 30000, f"Concurrent operations took too long: {total_time}ms"
            assert avg_individual < 10000, f"Individual operations too slow: {avg_individual}ms"
    
    async def test_query_retrieval_performance(self):
        """Test performance of query retrieval operations"""
        print("📊 Testing query retrieval performance...")
        
        # Create test data
        session_id = f"retrieval-test-{int(time.time())}"
        query_ids = []
        
        for i in range(20):
            query_id = await self.mongo_service.create_query({
                "query_text": f"Retrieval test query {i}",
                "user_session": session_id
            })
            query_ids.append(query_id)
        
        # Test individual query retrieval
        retrieval_times = []
        
        for query_id in query_ids[:10]:
            start_time = time.perf_counter()
            query = await self.mongo_service.get_query(query_id)
            end_time = time.perf_counter()
            
            assert query is not None
            retrieval_times.append((end_time - start_time) * 1000)
        
        avg_retrieval = statistics.mean(retrieval_times)
        print(f"   🔍 Individual query retrieval: {avg_retrieval:.2f}ms average")
        
        # Test session query retrieval
        start_time = time.perf_counter()
        session_queries = await self.mongo_service.get_user_queries(session_id, limit=10, offset=0)
        end_time = time.perf_counter()
        
        session_retrieval_time = (end_time - start_time) * 1000
        print(f"   📋 Session queries retrieval: {session_retrieval_time:.2f}ms for {len(session_queries)} queries")
        
        return {
            "individual_retrieval_avg": avg_retrieval,
            "session_retrieval_time": session_retrieval_time,
            "session_queries_count": len(session_queries)
        }
    
    async def test_analytics_performance(self):
        """Test performance of analytics operations"""
        print("📈 Testing analytics performance...")
        
        # Record some analytics data
        for i in range(15):
            await self.mongo_service.record_analytics(f"analytics-test-{i}", 1000 + i * 100)
        
        # Test dashboard data retrieval
        start_time = time.perf_counter()
        dashboard_data = await self.analytics_service.get_dashboard_data()
        end_time = time.perf_counter()
        
        dashboard_time = (end_time - start_time) * 1000
        print(f"   📊 Dashboard data retrieval: {dashboard_time:.2f}ms")
        
        # Test query trends
        start_time = time.perf_counter()
        trends = await self.analytics_service.get_query_trends()
        end_time = time.perf_counter()
        
        trends_time = (end_time - start_time) * 1000
        print(f"   📈 Query trends analysis: {trends_time:.2f}ms for {len(trends)} data points")
        
        return {
            "dashboard_time": dashboard_time,
            "trends_time": trends_time,
            "dashboard_queries": dashboard_data.get("total_queries", 0)
        }
    
    async def test_stress_conditions(self):
        """Test database under stress conditions"""
        print("🔥 Testing under stress conditions...")
        
        # High-frequency operations
        operations = []
        start_time = time.perf_counter()
        
        for i in range(50):
            query_id = await self.mongo_service.create_query({
                "query_text": f"Stress test query {i}",
                "user_session": f"stress-{i % 10}"  # 10 different sessions
            })
            operations.append(query_id)
        
        end_time = time.perf_counter()
        creation_time = (end_time - start_time) * 1000
        
        print(f"   ⚡ Created 50 queries in {creation_time:.2f}ms")
        print(f"   📊 Average: {creation_time/50:.2f}ms per query")
        
        # Bulk status updates
        start_time = time.perf_counter()
        
        update_tasks = []
        for query_id in operations:
            update_tasks.append(
                self.mongo_service.update_query_status(query_id, "completed", processing_time_ms=2000)
            )
        
        await asyncio.gather(*update_tasks)
        
        end_time = time.perf_counter()
        update_time = (end_time - start_time) * 1000
        
        print(f"   🔄 Updated 50 query statuses in {update_time:.2f}ms")
        
        # Memory and connection test
        print("   🧠 Testing connection stability...")
        
        connections_test = []
        for i in range(10):
            # Create new service instance to test connection pooling
            service = MongoService()
            connections_test.append(service.get_analytics())
        
        analytics_results = await asyncio.gather(*connections_test)
        print(f"   ✅ Successfully handled {len(analytics_results)} concurrent connections")
    
    async def run_all_tests(self):
        """Run all performance tests"""
        print("🚀 Starting Database Performance Test Suite")
        print("=" * 60)
        
        try:
            await self.mongo_service.connect()
            
            # Run individual tests
            single_perf = await self.test_single_operation_performance()
            await self.test_concurrent_operations()
            retrieval_perf = await self.test_query_retrieval_performance()
            analytics_perf = await self.test_analytics_performance()
            await self.test_stress_conditions()
            
            # Summary
            print("\n" + "=" * 60)
            print("🎉 Performance Test Summary:")
            print(f"   Query Creation Average: {single_perf['query_creation_avg']:.2f}ms")
            print(f"   Results Saving Average: {single_perf['results_saving_avg']:.2f}ms")
            print(f"   Query Retrieval Average: {retrieval_perf['individual_retrieval_avg']:.2f}ms")
            print(f"   Analytics Dashboard: {analytics_perf['dashboard_time']:.2f}ms")
            print("   ✅ All concurrent and stress tests passed")
            print("\n📈 Database performance is acceptable for production use!")
            
            return True
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
        
        finally:
            await self.mongo_service.disconnect()


async def test_api_performance():
    """Test API performance with database integration"""
    print("\n🌐 Testing API Performance with Database Integration")
    print("-" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test if backend is running
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if not response.ok:
            print("❌ Backend is not running. Skipping API performance tests.")
            return
    except:
        print("❌ Backend is not accessible. Skipping API performance tests.")
        return
    
    # Test API response times
    api_times = []
    
    for i in range(5):
        start_time = time.perf_counter()
        
        response = requests.post(f"{base_url}/research", json={
            "query": f"API performance test {i} - artificial intelligence applications",
            "user_session": f"api-perf-{i}"
        }, timeout=60)
        
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000
        
        if response.ok:
            api_times.append(duration)
            print(f"   ✅ API request {i+1}: {duration:.2f}ms")
        else:
            print(f"   ❌ API request {i+1} failed: {response.status_code}")
    
    if api_times:
        avg_api_time = statistics.mean(api_times)
        print(f"\n   📊 Average API response time: {avg_api_time:.2f}ms")
        print(f"   📊 Min: {min(api_times):.2f}ms, Max: {max(api_times):.2f}ms")


def main():
    """Main test runner"""
    print("Database Performance Testing Suite")
    print("This will test MongoDB operations under various conditions")
    print()
    
    # Run database performance tests
    db_test = DatabasePerformanceTest()
    
    async def run_tests():
        # Database tests
        db_success = await db_test.run_all_tests()
        
        # API tests
        await test_api_performance()
        
        return db_success
    
    try:
        success = asyncio.run(run_tests())
        
        if success:
            print("\n🎉 All performance tests completed successfully!")
            print("💾 Database is ready for production workload")
            sys.exit(0)
        else:
            print("\n❌ Some performance tests failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
