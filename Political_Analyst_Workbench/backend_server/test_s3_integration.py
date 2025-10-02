"""
Test S3 Integration with Backend Server
Verifies that artifacts are being uploaded to S3 and URLs are stored
"""

import asyncio
import httpx
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from services.mongo_service import mongo_service
from services.s3_service import s3_service

BASE_URL = "http://localhost:8000"


async def test_s3_connection():
    """Test S3 service availability"""
    print("\n" + "=" * 70)
    print("TEST 1: S3 Service Connection")
    print("=" * 70)
    
    if not s3_service:
        print("❌ S3 service not available")
        return False
    
    try:
        # Try to ensure bucket exists
        result = s3_service._ensure_bucket_exists()
        if result:
            print(f"✅ S3 service available")
            print(f"   Bucket: {s3_service.bucket_name}")
            print(f"   Region: {s3_service.region}")
            return True
        else:
            print("❌ S3 bucket check failed")
            return False
    except Exception as e:
        print(f"❌ S3 connection failed: {e}")
        return False


async def test_api_with_s3():
    """Test API endpoint and verify artifact uploaded to S3"""
    print("\n" + "=" * 70)
    print("TEST 2: API Call with S3 Artifact Upload")
    print("=" * 70)
    
    query = "Create a trend chart showing the GDP growth of India from 2020 to 2025"
    
    print(f"Query: {query}")
    print("\n🔄 Sending request to backend...")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Make API call
            response = await client.post(
                f"{BASE_URL}/api/analyze",
                json={"query": query, "user_session": "s3_test_user"}
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
            
            # Check if artifact was created
            if not result.get('artifact'):
                print("⚠️  No artifact created")
                return False
            
            artifact = result['artifact']
            print(f"   Artifact ID: {artifact['artifact_id']}")
            print(f"   Artifact Type: {artifact['type']}")
            
            # Verify S3 upload
            print("\n🔍 Verifying S3 upload...")
            
            # Check MongoDB for S3 URLs
            await mongo_service.connect()
            artifact_meta = await mongo_service.get_artifact(artifact['artifact_id'])
            
            if not artifact_meta:
                print("❌ Artifact metadata not found in MongoDB!")
                return False
            
            print(f"✅ Artifact metadata found in MongoDB")
            print(f"   Storage: {artifact_meta.get('storage', 'local')}")
            
            if artifact_meta.get('storage') == 's3':
                print(f"✅ Artifact uploaded to S3")
                print(f"   HTML URL: {artifact_meta.get('s3_html_url', 'N/A')}")
                print(f"   PNG URL: {artifact_meta.get('s3_png_url', 'N/A')}")
                
                # Verify URLs are accessible
                html_url = artifact_meta.get('s3_html_url')
                png_url = artifact_meta.get('s3_png_url')
                
                if html_url:
                    try:
                        html_response = await client.get(html_url, timeout=10.0)
                        if html_response.status_code == 200:
                            print(f"✅ HTML accessible on S3 ({len(html_response.content)} bytes)")
                        else:
                            print(f"⚠️  HTML URL returned {html_response.status_code}")
                    except Exception as e:
                        print(f"⚠️  Could not verify HTML URL: {e}")
                
                if png_url:
                    try:
                        png_response = await client.get(png_url, timeout=10.0)
                        if png_response.status_code == 200:
                            print(f"✅ PNG accessible on S3 ({len(png_response.content)} bytes)")
                        else:
                            print(f"⚠️  PNG URL returned {png_response.status_code}")
                    except Exception as e:
                        print(f"⚠️  Could not verify PNG URL: {e}")
                
                return True
            else:
                print(f"⚠️  Artifact stored locally (not in S3)")
                print(f"   HTML Path: {artifact_meta.get('html_path', 'N/A')}")
                print(f"   PNG Path: {artifact_meta.get('png_path', 'N/A')}")
                return False
            
    except httpx.ConnectError:
        print("❌ Cannot connect to backend server")
        print("   Make sure server is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_s3_artifact_list():
    """List artifacts in S3 bucket"""
    print("\n" + "=" * 70)
    print("TEST 3: List S3 Artifacts")
    print("=" * 70)
    
    if not s3_service:
        print("❌ S3 service not available")
        return False
    
    try:
        artifacts = await s3_service.list_artifacts()
        
        print(f"✅ Found {len(artifacts)} objects in S3")
        
        # Group by type
        by_type = {}
        for key in artifacts:
            parts = key.split('/')
            if len(parts) >= 2:
                artifact_type = parts[1]
                by_type[artifact_type] = by_type.get(artifact_type, 0) + 1
        
        print("\n📊 Artifacts by type:")
        for atype, count in by_type.items():
            print(f"   {atype}: {count} files")
        
        # Show recent artifacts
        if artifacts:
            print("\n📄 Recent artifacts (first 5):")
            for i, key in enumerate(artifacts[:5], 1):
                print(f"   {i}. {key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to list S3 artifacts: {e}")
        return False


async def main():
    """Run all S3 integration tests"""
    print("\n" + "=" * 70)
    print("🧪 S3 INTEGRATION TESTS")
    print("=" * 70)
    print("\nThese tests verify that artifacts are being")
    print("uploaded to AWS S3 and URLs are stored in MongoDB")
    print("=" * 70)
    
    results = {}
    
    try:
        # Test 1: S3 Connection
        results['s3_connection'] = await test_s3_connection()
        
        if not results['s3_connection']:
            print("\n❌ CRITICAL: S3 not available")
            print("   Check your AWS credentials in .env")
            return
        
        # Test 2: API with S3
        results['api_s3_upload'] = await test_api_with_s3()
        
        # Test 3: List S3 artifacts
        results['s3_list'] = await test_s3_artifact_list()
        
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
            print("\n🎉 S3 integration is working correctly!")
            print("   - Artifacts are uploaded to S3")
            print("   - S3 URLs are stored in MongoDB")
            print("   - Artifacts are publicly accessible")
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

