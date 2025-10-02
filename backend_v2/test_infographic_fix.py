"""
Test script to verify infographic 404 fix
Tests that artifact_id matches the actual filename
"""
import requests
import time
import os
import sys

def test_infographic_fix():
    """Test that infographics are created and accessible"""
    
    print("=" * 70)
    print("🧪 TESTING INFOGRAPHIC 404 FIX")
    print("=" * 70)
    print()
    
    # 1. Check server health
    print("1️⃣ Checking server health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server healthy: {data['status']}")
            print(f"   Agent: {data['agent_status']}")
        else:
            print(f"   ❌ Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Server not accessible: {e}")
        return False
    
    print()
    
    # 2. Check if artifacts exist from previous run
    print("2️⃣ Checking for recent infographic artifacts...")
    artifacts_dir = "langgraph_master_agent/sub_agents/sentiment_analyzer/artifacts"
    
    if os.path.exists(artifacts_dir):
        # Find recent infographic files
        infographic_files = [f for f in os.listdir(artifacts_dir) 
                            if f.startswith('infographic_') and f.endswith('.html')]
        
        print(f"   Found {len(infographic_files)} infographic files")
        
        if infographic_files:
            print()
            print("3️⃣ Testing artifact accessibility...")
            
            # Test the most recent infographic
            infographic_files.sort(reverse=True)  # Most recent first
            test_file = infographic_files[0]
            artifact_id = test_file.replace('.html', '')
            
            print(f"   Testing file: {test_file}")
            print(f"   Artifact ID: {artifact_id}")
            print()
            
            # Verify filename format is correct
            print("   Checking filename format:")
            if '_' in artifact_id:
                parts = artifact_id.split('_')
                print(f"      Prefix: {parts[0]}")
                print(f"      Schema: {parts[1] if len(parts) > 1 else 'N/A'}")
                print(f"      Template: {parts[2] if len(parts) > 2 else 'N/A'}")
                print(f"      Timestamp: {parts[3] if len(parts) > 3 else 'N/A'}")
                print(f"   ✅ Filename format looks correct")
            else:
                print(f"   ⚠️  Old format detected (timestamp-only)")
            
            print()
            
            # Try to access the artifact via API
            print("   Testing API access:")
            url = f"http://localhost:8000/api/artifacts/{test_file}"
            print(f"   GET {url}")
            
            try:
                response = requests.get(url, timeout=5)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   Content-Type: {response.headers.get('content-type')}")
                    print(f"   Content-Length: {len(response.content)} bytes")
                    print(f"   ✅ Artifact accessible!")
                    
                    # Check if it's valid HTML
                    if b'<!DOCTYPE html>' in response.content or b'<html' in response.content:
                        print(f"   ✅ Valid HTML content")
                    else:
                        print(f"   ⚠️  May not be valid HTML")
                    
                    return True
                elif response.status_code == 404:
                    print(f"   ❌ 404 Not Found - FIX NOT WORKING!")
                    return False
                else:
                    print(f"   ⚠️  Unexpected status code")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Request failed: {e}")
                return False
        else:
            print("   ⚠️  No infographic files found")
            print("   Run a sentiment analysis query to generate infographics")
            return None
    else:
        print(f"   ❌ Artifacts directory not found: {artifacts_dir}")
        return None
    
    return True

def test_artifact_id_consistency():
    """Test that artifact_id generation is consistent"""
    print()
    print("=" * 70)
    print("🧪 TESTING ARTIFACT ID CONSISTENCY")
    print("=" * 70)
    print()
    
    # Import the renderer
    sys.path.insert(0, 'shared')
    try:
        from html_infographic_renderer import HTMLInfographicRenderer
        from infographic_schemas import KeyMetricsDashboard, MetricItem
        
        print("✅ Modules imported successfully")
        print()
        
        # Create test data
        test_data = KeyMetricsDashboard(
            title="Test Dashboard",
            subtitle="Testing artifact ID consistency",
            metrics=[
                MetricItem(value="42%", label="Test Metric"),
                MetricItem(value="99", label="Test Count")
            ],
            insight="This is a test",
            footer="Test Footer"
        )
        
        # Create temporary renderer
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            renderer = HTMLInfographicRenderer(
                templates_dir="shared/templates/html_samples",
                output_dir=temp_dir
            )
            
            print("Creating test infographic...")
            artifact = renderer.render(
                schema_data=test_data,
                visual_template="gradient_modern"
            )
            
            print(f"   Artifact ID: {artifact['artifact_id']}")
            print(f"   Path: {artifact['path']}")
            print()
            
            # Extract filename from path
            filename = os.path.basename(artifact['path'])
            expected_id = filename.replace('.html', '')
            
            print(f"   Expected ID: {expected_id}")
            print(f"   Actual ID: {artifact['artifact_id']}")
            print()
            
            if artifact['artifact_id'] == expected_id:
                print("   ✅ Artifact ID matches filename!")
                return True
            else:
                print("   ❌ Artifact ID DOES NOT match filename!")
                print(f"   This will cause 404 errors!")
                return False
                
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print()
    results = []
    
    # Test 1: Check existing artifacts
    result1 = test_infographic_fix()
    results.append(("Infographic Accessibility", result1))
    
    # Test 2: Check artifact ID consistency
    result2 = test_artifact_id_consistency()
    results.append(("Artifact ID Consistency", result2))
    
    # Summary
    print()
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print()
    
    for test_name, result in results:
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  SKIPPED"
        print(f"   {test_name}: {status}")
    
    print()
    
    if all(r is True for r in [result1, result2] if r is not None):
        print("🎉 ALL TESTS PASSED!")
        print()
        exit(0)
    elif any(r is False for r in [result1, result2]):
        print("❌ SOME TESTS FAILED")
        print()
        exit(1)
    else:
        print("⚠️  TESTS INCOMPLETE (no artifacts to test)")
        print("   Generate infographics by running a sentiment analysis query")
        print()
        exit(2)

