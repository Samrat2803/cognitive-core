#!/usr/bin/env python3
"""
Test WebSocket connection to Political Analyst Workbench backend
"""

import asyncio
import websockets
import json
from datetime import datetime

WS_URL = "ws://localhost:8000/ws/analyze"

async def test_websocket():
    """Test WebSocket connection and basic message exchange"""
    
    print("🔌 Testing WebSocket connection...")
    print(f"URL: {WS_URL}")
    print("-" * 60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ WebSocket connected!")
            
            # Wait for initial 'connected' message
            message = await websocket.recv()
            data = json.loads(message)
            print(f"\n📥 Received: {data['type']}")
            if data['type'] == 'connected':
                print(f"   Message: {data['data'].get('message', 'N/A')}")
                print(f"   Server Version: {data['data'].get('server_version', 'N/A')}")
                print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            
            # Send a test query (using new API contract format)
            test_query = {
                "type": "query",
                "data": {
                    "query": "What is the current political situation in France?",
                    "use_citations": True
                },
                "message_id": f"test_{int(datetime.now().timestamp())}"
            }
            
            print(f"\n📤 Sending query: {test_query['data']['query']}")
            await websocket.send(json.dumps(test_query))
            
            # Listen for responses (max 30 seconds for full analysis)
            print("\n📥 Listening for responses...\n")
            
            timeout = 30
            start_time = asyncio.get_event_loop().time()
            content_buffer = []
            
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    msg_type = data.get('type', 'unknown')
                    
                    if msg_type == 'session_start':
                        print(f"   🎬 Session Start:")
                        print(f"      Session ID: {data['data'].get('session_id', 'N/A')}")
                        print(f"      Query: {data['data'].get('query', 'N/A')}")
                        
                    elif msg_type == 'status':
                        step = data['data'].get('step', 'N/A')
                        message_text = data['data'].get('message', 'N/A')
                        progress = data['data'].get('progress', 0) * 100
                        print(f"   📊 Status [{step}]: {message_text} ({progress:.0f}%)")
                        
                    elif msg_type == 'content':
                        content = data['data'].get('content', '')
                        content_buffer.append(content)
                        is_complete = data['data'].get('is_complete', False)
                        if is_complete:
                            full_content = ''.join(content_buffer)
                            print(f"\n   💬 Content:")
                            print(f"      {full_content[:200]}...")
                            content_buffer = []
                            
                    elif msg_type == 'citation':
                        print(f"   📚 Citation:")
                        print(f"      Title: {data['data'].get('title', 'N/A')}")
                        print(f"      URL: {data['data'].get('url', 'N/A')}")
                        
                    elif msg_type == 'artifact':
                        print(f"   🎨 Artifact:")
                        print(f"      ID: {data['data'].get('artifact_id', 'N/A')}")
                        print(f"      Type: {data['data'].get('type', 'N/A')}")
                        print(f"      Title: {data['data'].get('title', 'N/A')}")
                        print(f"      HTML URL: {data['data'].get('html_url', 'N/A')}")
                        
                    elif msg_type == 'complete':
                        print(f"\n   ✅ Complete!")
                        print(f"      Session ID: {data['data'].get('session_id', 'N/A')}")
                        print(f"      Confidence: {data['data'].get('confidence', 0):.2f}")
                        print(f"      Citations: {data['data'].get('total_citations', 0)}")
                        print(f"      Has Artifact: {data['data'].get('has_artifact', False)}")
                        break
                        
                    elif msg_type == 'error':
                        print(f"   ❌ Error: {data['data'].get('message', 'N/A')}")
                        break
                        
                    else:
                        print(f"   {msg_type}: {str(data['data'])[:100]}")
                
                except asyncio.TimeoutError:
                    continue
            
            print("\n✅ WebSocket test completed successfully!")
            
    except ConnectionRefusedError:
        print("❌ Connection refused. Is the backend running?")
        print("   Start it with: cd Political_Analyst_Workbench/backend_server && python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())

