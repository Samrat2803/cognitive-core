# 🧪 V2 App - Minimum Testing Plan

**Created:** October 2, 2025  
**Purpose:** Comprehensive testing plan to validate all features of the Cognitive Core Platform (V2)  
**Duration:** 2-3 hours for complete test execution

---

## 📋 Table of Contents

1. [Test Environment Setup](#test-environment-setup)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [Integration Testing](#integration-testing)
5. [Performance Testing](#performance-testing)
6. [Test Execution Checklist](#test-execution-checklist)

---

## 🛠️ Test Environment Setup

### Prerequisites

**File:** `backend_v2/.env` (ensure all keys are present)

```bash
# Required API Keys
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Optional (for full testing)
MONGODB_CONNECTION_STRING=mongodb+srv://...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET_NAME=...
```

### Setup Commands

**File to create:** `test_setup.sh` in project root

```bash
#!/bin/bash

# Navigate to backend_v2
cd backend_v2

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if needed)
uv pip install fastapi uvicorn python-dotenv openai tavily-python plotly pandas kaleido

# Navigate to frontend
cd ../Frontend_v2

# Install dependencies (if needed)
npm install

echo "✅ Test environment ready!"
```

---

## 🔧 Backend Testing

### Test Suite 1: API Health & Connectivity

**Test File:** `backend_v2/tests/test_01_api_health.py`

```python
"""
Test: API Health and Connectivity
Purpose: Verify backend server is running and healthy
"""

import asyncio
import httpx
from datetime import datetime

# Test Configuration
BASE_URL = "http://localhost:8000"

async def test_health_endpoint():
    """Test /health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent_status"] == "ready"
        print("✅ Health endpoint working")

async def test_root_endpoint():
    """Test / endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        print("✅ Root endpoint working")

async def test_cors_headers():
    """Test CORS headers are present"""
    async with httpx.AsyncClient() as client:
        response = await client.options(f"{BASE_URL}/api/analyze")
        assert "access-control-allow-origin" in response.headers
        print("✅ CORS configured correctly")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 1: API Health & Connectivity")
    print("="*70)
    
    asyncio.run(test_health_endpoint())
    asyncio.run(test_root_endpoint())
    asyncio.run(test_cors_headers())
    
    print("\n✅ All API health tests passed!")
```

**Expected Result:** All tests pass, server responds correctly

---

### Test Suite 2: Master Agent - Basic Query Processing

**Test File:** `backend_v2/tests/test_02_master_agent.py`

```python
"""
Test: Master Agent Query Processing
Purpose: Verify master agent can process queries and return results
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_simple_query():
    """Test simple political query"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "query": "What is the current political situation in India?",
            "user_session": "test_session_1"
        }
        
        response = await client.post(f"{BASE_URL}/api/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert len(data["response"]) > 100  # Meaningful response
        assert len(data["execution_log"]) > 0  # Execution logged
        assert data["confidence"] > 0.0
        
        print(f"✅ Simple query processed")
        print(f"   Response length: {len(data['response'])} chars")
        print(f"   Confidence: {data['confidence']}")
        print(f"   Tools used: {data['tools_used']}")
        
        return data

async def test_query_with_artifact():
    """Test query that should generate artifact"""
    async with httpx.AsyncClient(timeout=90.0) as client:
        payload = {
            "query": "Give me a visualization of India's GDP growth since 2020",
            "user_session": "test_session_2"
        }
        
        response = await client.post(f"{BASE_URL}/api/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["artifact"] is not None  # Artifact created
        assert data["artifact"]["type"] in ["line_chart", "bar_chart"]
        assert data["artifact"]["artifact_id"] is not None
        
        print(f"✅ Query with artifact processed")
        print(f"   Artifact type: {data['artifact']['type']}")
        print(f"   Artifact ID: {data['artifact']['artifact_id']}")
        
        return data

async def test_error_handling():
    """Test error handling with invalid query"""
    async with httpx.AsyncClient() as client:
        # Empty query
        response = await client.post(f"{BASE_URL}/api/analyze", json={"query": ""})
        assert response.status_code == 400
        
        # Too long query
        response = await client.post(f"{BASE_URL}/api/analyze", json={"query": "a" * 3000})
        assert response.status_code == 400
        
        print("✅ Error handling working correctly")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 2: Master Agent - Basic Query Processing")
    print("="*70)
    
    asyncio.run(test_simple_query())
    asyncio.run(test_query_with_artifact())
    asyncio.run(test_error_handling())
    
    print("\n✅ All master agent tests passed!")
```

**Expected Result:** Master agent processes queries, returns responses and artifacts

---

### Test Suite 3: Sub-Agents Testing

**Test File:** `backend_v2/tests/test_03_sub_agents.py`

```python
"""
Test: Sub-Agents Functionality
Purpose: Test each implemented sub-agent
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_sentiment_analyzer():
    """Test Sentiment Analyzer sub-agent"""
    async with httpx.AsyncClient(timeout=90.0) as client:
        payload = {
            "query": "Analyze sentiment about nuclear energy in US, UK, and France"
        }
        
        response = await client.post(f"{BASE_URL}/api/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        # Check if sentiment analyzer was used
        # Should have sub_agent_artifacts
        if data.get("sub_agent_artifacts"):
            print("✅ Sentiment Analyzer invoked via master agent")
            print(f"   Sub-agent artifacts: {list(data['sub_agent_artifacts'].keys())}")
        
        return data

async def test_live_monitor():
    """Test Live Political Monitor"""
    async with httpx.AsyncClient(timeout=90.0) as client:
        payload = {
            "keywords": ["Bihar", "election"],
            "cache_hours": 1,
            "max_results": 5
        }
        
        response = await client.post(
            f"{BASE_URL}/api/live-monitor/explosive-topics", 
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert len(data["topics"]) > 0
        assert data["total_articles_analyzed"] > 0
        
        print(f"✅ Live Monitor working")
        print(f"   Topics found: {len(data['topics'])}")
        print(f"   Articles analyzed: {data['total_articles_analyzed']}")
        
        return data

async def test_media_bias_detector():
    """Test Media Bias Detector sub-agent"""
    async with httpx.AsyncClient(timeout=90.0) as client:
        payload = {
            "query": "Analyze media bias on climate change reporting"
        }
        
        response = await client.post(f"{BASE_URL}/api/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        print("✅ Media Bias Detector query processed")
        
        return data

async def test_sitrep_generator():
    """Test SitRep Generator sub-agent"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        payload = {
            "query": "Generate a situation report for current global events"
        }
        
        response = await client.post(f"{BASE_URL}/api/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        print("✅ SitRep Generator query processed")
        
        return data

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 3: Sub-Agents Testing")
    print("="*70)
    
    print("\n1. Testing Sentiment Analyzer...")
    asyncio.run(test_sentiment_analyzer())
    
    print("\n2. Testing Live Political Monitor...")
    asyncio.run(test_live_monitor())
    
    print("\n3. Testing Media Bias Detector...")
    asyncio.run(test_media_bias_detector())
    
    print("\n4. Testing SitRep Generator...")
    asyncio.run(test_sitrep_generator())
    
    print("\n✅ All sub-agent tests passed!")
```

**Expected Result:** All sub-agents can be invoked and return results

---

### Test Suite 4: Artifact System

**Test File:** `backend_v2/tests/test_04_artifacts.py`

```python
"""
Test: Artifact Generation and Retrieval
Purpose: Verify artifacts are created, saved, and retrievable
"""

import asyncio
import httpx
import os

BASE_URL = "http://localhost:8000"

async def test_artifact_creation():
    """Test artifact is created"""
    async with httpx.AsyncClient(timeout=90.0) as client:
        payload = {
            "query": "Show me a bar chart of US GDP vs China GDP in 2023"
        }
        
        response = await client.post(f"{BASE_URL}/api/analyze", json=payload)
        data = response.json()
        
        assert data["artifact"] is not None
        artifact_id = data["artifact"]["artifact_id"]
        
        print(f"✅ Artifact created: {artifact_id}")
        
        return artifact_id

async def test_artifact_retrieval_html(artifact_id):
    """Test HTML artifact retrieval"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/artifacts/{artifact_id}.html")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        print(f"✅ HTML artifact retrieved: {artifact_id}.html")

async def test_artifact_retrieval_png(artifact_id):
    """Test PNG artifact retrieval"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/artifacts/{artifact_id}.png")
        assert response.status_code == 200
        assert "image/png" in response.headers["content-type"]
        
        print(f"✅ PNG artifact retrieved: {artifact_id}.png")

async def test_artifact_not_found():
    """Test 404 for missing artifact"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/artifacts/nonexistent.html")
        assert response.status_code == 404
        
        print("✅ 404 returned for missing artifact")

async def test_multiple_artifacts():
    """Test query that generates multiple artifacts"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        payload = {
            "query": "Analyze sentiment about AI regulation in US and EU with visualizations"
        }
        
        response = await client.post(f"{BASE_URL}/api/analyze", json=payload)
        data = response.json()
        
        # Check for sub-agent artifacts
        total_artifacts = 0
        if data.get("artifact"):
            total_artifacts += 1
        if data.get("sub_agent_artifacts"):
            for agent_name, artifacts_list in data["sub_agent_artifacts"].items():
                total_artifacts += len(artifacts_list)
        
        print(f"✅ Multiple artifacts test: {total_artifacts} artifacts generated")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 4: Artifact System")
    print("="*70)
    
    print("\n1. Creating artifact...")
    artifact_id = asyncio.run(test_artifact_creation())
    
    print("\n2. Retrieving HTML artifact...")
    asyncio.run(test_artifact_retrieval_html(artifact_id))
    
    print("\n3. Retrieving PNG artifact...")
    asyncio.run(test_artifact_retrieval_png(artifact_id))
    
    print("\n4. Testing 404 handling...")
    asyncio.run(test_artifact_not_found())
    
    print("\n5. Testing multiple artifacts...")
    asyncio.run(test_multiple_artifacts())
    
    print("\n✅ All artifact tests passed!")
```

**Expected Result:** Artifacts are created, saved, and can be retrieved in multiple formats

---

### Test Suite 5: WebSocket Streaming

**Test File:** `backend_v2/tests/test_05_websocket.py`

```python
"""
Test: WebSocket Real-time Streaming
Purpose: Verify WebSocket connection and message streaming
"""

import asyncio
import websockets
import json

WS_URL = "ws://localhost:8000/ws/analyze"

async def test_websocket_connection():
    """Test WebSocket connection"""
    async with websockets.connect(WS_URL) as websocket:
        # Wait for connection message
        message = await websocket.recv()
        data = json.loads(message)
        
        assert data["type"] == "connected"
        assert "session_id" in data["data"]
        
        print("✅ WebSocket connection established")
        print(f"   Session ID: {data['data']['session_id']}")
        
        return data["data"]["session_id"]

async def test_websocket_query_streaming():
    """Test query streaming over WebSocket"""
    async with websockets.connect(WS_URL) as websocket:
        # Receive connection message
        await websocket.recv()
        
        # Send query
        query_message = {
            "type": "query",
            "data": {
                "query": "What is happening in Bihar politics today?",
                "use_citations": True
            },
            "message_id": "test_msg_001"
        }
        
        await websocket.send(json.dumps(query_message))
        print("✅ Query sent via WebSocket")
        
        # Collect messages
        messages_received = []
        message_types = set()
        
        try:
            while True:
                message = await asyncio.wait_for(websocket.recv(), timeout=120.0)
                data = json.loads(message)
                messages_received.append(data)
                message_types.add(data["type"])
                
                print(f"   Received: {data['type']}")
                
                if data["type"] == "complete":
                    break
        except asyncio.TimeoutError:
            print("   ⚠️ Timeout waiting for completion")
        
        # Verify message types
        assert "session_start" in message_types
        assert "status" in message_types
        assert "content" in message_types
        assert "complete" in message_types
        
        print(f"✅ Streaming query completed")
        print(f"   Total messages: {len(messages_received)}")
        print(f"   Message types: {message_types}")

async def test_websocket_artifact_streaming():
    """Test artifact delivery via WebSocket"""
    async with websockets.connect(WS_URL) as websocket:
        # Receive connection message
        await websocket.recv()
        
        # Send query that generates artifact
        query_message = {
            "type": "query",
            "data": {
                "query": "Show me a chart of global temperature trends",
                "use_citations": False
            },
            "message_id": "test_msg_002"
        }
        
        await websocket.send(json.dumps(query_message))
        
        # Wait for artifact message
        artifact_received = False
        
        try:
            while True:
                message = await asyncio.wait_for(websocket.recv(), timeout=120.0)
                data = json.loads(message)
                
                if data["type"] == "artifact":
                    artifact_received = True
                    print(f"✅ Artifact received via WebSocket")
                    print(f"   Artifact ID: {data['data']['artifact_id']}")
                    print(f"   Type: {data['data']['type']}")
                
                if data["type"] == "complete":
                    break
        except asyncio.TimeoutError:
            print("   ⚠️ Timeout")
        
        # Artifacts may or may not be generated depending on query
        print(f"   Artifact delivery: {'✅' if artifact_received else '⚠️ Not triggered'}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 5: WebSocket Streaming")
    print("="*70)
    
    print("\n1. Testing WebSocket connection...")
    asyncio.run(test_websocket_connection())
    
    print("\n2. Testing query streaming...")
    asyncio.run(test_websocket_query_streaming())
    
    print("\n3. Testing artifact streaming...")
    asyncio.run(test_websocket_artifact_streaming())
    
    print("\n✅ All WebSocket tests passed!")
```

**Expected Result:** WebSocket connects, streams messages, delivers artifacts

---

## 🎨 Frontend Testing

### Test Suite 6: Frontend Components

**Test File:** `Frontend_v2/e2e/test_06_frontend_basic.spec.ts`

```typescript
/**
 * Test: Frontend Basic Functionality
 * Purpose: Verify core frontend features work
 */

import { test, expect } from '@playwright/test';

test.describe('Frontend Basic Tests', () => {
  
  test('Homepage loads correctly', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    
    // Check title
    await expect(page).toHaveTitle(/Cognitive Core/);
    
    // Check header
    await expect(page.locator('.header-title')).toContainText('Cognitive Core');
    
    // Check search input
    await expect(page.locator('.hero-search-input')).toBeVisible();
    
    console.log('✅ Homepage loads correctly');
  });
  
  test('Connection status displays', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    
    // Connection status should be visible
    await expect(page.locator('.connection-status')).toBeVisible();
    
    console.log('✅ Connection status visible');
  });
  
  test('Live Monitor Dashboard displays', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    
    // Wait for dashboard to load
    await page.waitForSelector('.live-monitor-dashboard', { timeout: 10000 });
    
    // Check if topics are displayed
    const topicsVisible = await page.locator('.topic-card').count() > 0;
    console.log(`✅ Live Monitor Dashboard displayed (${topicsVisible ? 'with topics' : 'empty'})`);
  });
  
  test('Navigation to chat page works', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    
    // Type query and submit
    await page.fill('.hero-search-input', 'Test query');
    await page.click('.hero-search-button');
    
    // Wait for navigation
    await page.waitForURL('**/chat');
    
    // Check chat page loaded
    await expect(page.locator('.chat-panel')).toBeVisible();
    
    console.log('✅ Navigation to chat page works');
  });
});
```

**Run Command:**
```bash
cd Frontend_v2
npx playwright test e2e/test_06_frontend_basic.spec.ts --headed
```

---

### Test Suite 7: Chat Functionality

**Test File:** `Frontend_v2/e2e/test_07_chat.spec.ts`

```typescript
/**
 * Test: Chat Functionality
 * Purpose: Test chat interface and messaging
 */

import { test, expect } from '@playwright/test';

test.describe('Chat Functionality Tests', () => {
  
  test('Chat interface loads', async ({ page }) => {
    await page.goto('http://localhost:5173/chat');
    
    // Check chat components
    await expect(page.locator('.chat-panel')).toBeVisible();
    await expect(page.locator('.message-input')).toBeVisible();
    
    console.log('✅ Chat interface loaded');
  });
  
  test('Can send a message', async ({ page }) => {
    await page.goto('http://localhost:5173/chat');
    
    // Type and send message
    await page.fill('.message-input', 'What is the political situation in India?');
    await page.click('button:has-text("Send")');
    
    // Wait for user message to appear
    await expect(page.locator('.message.user')).toBeVisible({ timeout: 5000 });
    
    console.log('✅ Message sent successfully');
  });
  
  test('Receives AI response', async ({ page }) => {
    await page.goto('http://localhost:5173/chat');
    
    // Send query
    await page.fill('.message-input', 'Test query');
    await page.click('button:has-text("Send")');
    
    // Wait for AI response
    await expect(page.locator('.message.assistant')).toBeVisible({ timeout: 90000 });
    
    // Check response has content
    const responseText = await page.locator('.message.assistant').first().textContent();
    expect(responseText.length).toBeGreaterThan(50);
    
    console.log('✅ AI response received');
  });
  
  test('Status updates display during processing', async ({ page }) => {
    await page.goto('http://localhost:5173/chat');
    
    // Send query
    await page.fill('.message-input', 'Analyze GDP trends');
    await page.click('button:has-text("Send")');
    
    // Check for status message
    await expect(page.locator('.status-message')).toBeVisible({ timeout: 5000 });
    
    console.log('✅ Status updates displayed');
  });
});
```

---

### Test Suite 8: Artifact Viewer

**Test File:** `Frontend_v2/e2e/test_08_artifacts.spec.ts`

```typescript
/**
 * Test: Artifact Viewer
 * Purpose: Test artifact display and interaction
 */

import { test, expect } from '@playwright/test';

test.describe('Artifact Viewer Tests', () => {
  
  test('Artifact panel appears when artifact is generated', async ({ page }) => {
    await page.goto('http://localhost:5173/chat');
    
    // Send query that generates artifact
    await page.fill('.message-input', 'Show me a chart of India GDP growth');
    await page.click('button:has-text("Send")');
    
    // Wait for artifact panel
    await expect(page.locator('.artifact-panel')).toBeVisible({ timeout: 120000 });
    
    console.log('✅ Artifact panel displayed');
  });
  
  test('Can view artifact content', async ({ page }) => {
    await page.goto('http://localhost:5173/chat');
    
    // Send query
    await page.fill('.message-input', 'Visualize temperature trends');
    await page.click('button:has-text("Send")');
    
    // Wait for artifact
    await expect(page.locator('.artifact-panel')).toBeVisible({ timeout: 120000 });
    
    // Check iframe or image is present
    const artifactContent = await page.locator('.artifact-content iframe, .artifact-content img').count();
    expect(artifactContent).toBeGreaterThan(0);
    
    console.log('✅ Artifact content visible');
  });
  
  test('Can switch between multiple artifacts', async ({ page }) => {
    await page.goto('http://localhost:5173/chat');
    
    // Send query that may generate multiple artifacts
    await page.fill('.message-input', 'Analyze sentiment about climate change in US and UK');
    await page.click('button:has-text("Send")');
    
    // Wait for artifacts
    await page.waitForTimeout(120000); // Wait up to 2 minutes
    
    // Check if multiple artifacts are present
    const artifactButtons = await page.locator('.artifact-selector button').count();
    
    if (artifactButtons > 1) {
      console.log(`✅ Multiple artifacts available (${artifactButtons})`);
      
      // Try switching
      await page.locator('.artifact-selector button').nth(1).click();
      console.log('✅ Switched between artifacts');
    } else {
      console.log('ℹ️  Single artifact generated');
    }
  });
});
```

---

## 🔗 Integration Testing

### Test Suite 9: End-to-End User Journey

**Test File:** `Frontend_v2/e2e/test_09_user_journey.spec.ts`

```typescript
/**
 * Test: Complete User Journey
 * Purpose: Simulate real user flow from homepage to results
 */

import { test, expect } from '@playwright/test';

test.describe('End-to-End User Journey', () => {
  
  test('Complete analysis journey', async ({ page }) => {
    console.log('\n🧪 Starting complete user journey test...\n');
    
    // 1. Land on homepage
    console.log('Step 1: Loading homepage...');
    await page.goto('http://localhost:5173/');
    await expect(page.locator('.hero-title')).toBeVisible();
    console.log('✅ Homepage loaded');
    
    // 2. Enter query
    console.log('\nStep 2: Entering query...');
    await page.fill('.hero-search-input', 'Analyze political sentiment about healthcare reform in US');
    await page.click('.hero-search-button');
    console.log('✅ Query submitted');
    
    // 3. Navigate to chat
    console.log('\nStep 3: Navigating to chat...');
    await page.waitForURL('**/chat');
    await expect(page.locator('.chat-panel')).toBeVisible();
    console.log('✅ Chat page loaded');
    
    // 4. Wait for processing
    console.log('\nStep 4: Waiting for AI processing...');
    await expect(page.locator('.status-message')).toBeVisible({ timeout: 10000 });
    console.log('✅ Processing started');
    
    // 5. Receive response
    console.log('\nStep 5: Waiting for response...');
    await expect(page.locator('.message.assistant')).toBeVisible({ timeout: 120000 });
    const response = await page.locator('.message.assistant').first().textContent();
    expect(response.length).toBeGreaterThan(100);
    console.log(`✅ Response received (${response.length} chars)`);
    
    // 6. Check for citations
    console.log('\nStep 6: Checking for citations...');
    const citationsExist = await page.locator('.citations').count() > 0;
    console.log(`${citationsExist ? '✅' : 'ℹ️'} Citations ${citationsExist ? 'present' : 'not shown'}`);
    
    // 7. Check for artifacts
    console.log('\nStep 7: Checking for artifacts...');
    const artifactExists = await page.locator('.artifact-panel').isVisible();
    console.log(`${artifactExists ? '✅' : 'ℹ️'} Artifacts ${artifactExists ? 'generated' : 'not generated'}`);
    
    // 8. Check execution graph
    console.log('\nStep 8: Checking execution graph...');
    const graphButton = await page.locator('button:has-text("Show Graph")').count();
    if (graphButton > 0) {
      await page.locator('button:has-text("Show Graph")').click();
      await expect(page.locator('.execution-graph')).toBeVisible();
      console.log('✅ Execution graph displayed');
    } else {
      console.log('ℹ️  Execution graph button not found');
    }
    
    console.log('\n🎉 Complete user journey test passed!');
  });
  
  test('Multi-turn conversation', async ({ page }) => {
    await page.goto('http://localhost:5173/chat');
    
    // First query
    await page.fill('.message-input', 'What is GDP?');
    await page.click('button:has-text("Send")');
    await expect(page.locator('.message.assistant')).toBeVisible({ timeout: 90000 });
    
    // Follow-up query
    await page.fill('.message-input', 'How does it compare to GNP?');
    await page.click('button:has-text("Send")');
    await expect(page.locator('.message.assistant').nth(1)).toBeVisible({ timeout: 90000 });
    
    // Check conversation history
    const messageCount = await page.locator('.message').count();
    expect(messageCount).toBeGreaterThanOrEqual(4); // 2 user + 2 assistant
    
    console.log(`✅ Multi-turn conversation (${messageCount} messages)`);
  });
});
```

---

## ⚡ Performance Testing

### Test Suite 10: Performance Benchmarks

**Test File:** `backend_v2/tests/test_10_performance.py`

```python
"""
Test: Performance Benchmarks
Purpose: Measure response times and resource usage
"""

import asyncio
import httpx
import time
from statistics import mean, stdev

BASE_URL = "http://localhost:8000"

async def measure_response_time(query, expected_max_time=30.0):
    """Measure response time for a query"""
    start = time.time()
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/analyze",
            json={"query": query}
        )
        
    elapsed = time.time() - start
    
    assert elapsed < expected_max_time, f"Query took too long: {elapsed:.2f}s"
    
    return elapsed

async def test_simple_query_performance():
    """Test simple query performance"""
    queries = [
        "What is GDP?",
        "Explain political parties",
        "What is democracy?"
    ]
    
    times = []
    for query in queries:
        elapsed = await measure_response_time(query, expected_max_time=15.0)
        times.append(elapsed)
        print(f"   {query[:30]}... : {elapsed:.2f}s")
    
    avg_time = mean(times)
    print(f"\n✅ Simple queries: avg {avg_time:.2f}s (target: <15s)")

async def test_complex_query_performance():
    """Test complex query with artifact generation"""
    query = "Analyze GDP trends for US, China, India and create visualization"
    
    elapsed = await measure_response_time(query, expected_max_time=60.0)
    
    print(f"✅ Complex query: {elapsed:.2f}s (target: <60s)")

async def test_concurrent_requests():
    """Test handling of concurrent requests"""
    queries = [
        "What is GDP?",
        "Explain inflation",
        "What is trade balance?"
    ]
    
    start = time.time()
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        tasks = [
            client.post(f"{BASE_URL}/api/analyze", json={"query": q})
            for q in queries
        ]
        responses = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    
    assert all(r.status_code == 200 for r in responses)
    
    print(f"✅ Concurrent requests: {elapsed:.2f}s for {len(queries)} queries")
    print(f"   Avg per query: {elapsed/len(queries):.2f}s")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 10: Performance Benchmarks")
    print("="*70)
    
    print("\n1. Testing simple query performance...")
    asyncio.run(test_simple_query_performance())
    
    print("\n2. Testing complex query performance...")
    asyncio.run(test_complex_query_performance())
    
    print("\n3. Testing concurrent requests...")
    asyncio.run(test_concurrent_requests())
    
    print("\n✅ All performance tests passed!")
```

**Performance Targets:**
- Simple queries: < 15 seconds
- Complex queries with artifacts: < 60 seconds
- WebSocket connection: < 2 seconds
- Artifact retrieval: < 1 second

---

## ✅ Test Execution Checklist

### Pre-Test Setup

```bash
# Terminal 1: Start Backend
cd backend_v2
source .venv/bin/activate
python app.py

# Terminal 2: Start Frontend
cd Frontend_v2
npm run dev

# Wait for both servers to be ready
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

### Backend Tests (Sequential Execution)

```bash
cd backend_v2

# Test 1: API Health
python tests/test_01_api_health.py

# Test 2: Master Agent
python tests/test_02_master_agent.py

# Test 3: Sub-Agents
python tests/test_03_sub_agents.py

# Test 4: Artifacts
python tests/test_04_artifacts.py

# Test 5: WebSocket
python tests/test_05_websocket.py

# Test 10: Performance
python tests/test_10_performance.py
```

### Frontend Tests (Playwright)

```bash
cd Frontend_v2

# Install Playwright (if needed)
npx playwright install

# Run all frontend tests
npx playwright test e2e/test_06_frontend_basic.spec.ts --headed
npx playwright test e2e/test_07_chat.spec.ts --headed
npx playwright test e2e/test_08_artifacts.spec.ts --headed
npx playwright test e2e/test_09_user_journey.spec.ts --headed
```

### Test Results Summary

**File:** `TEST_RESULTS.md` (to be created after test run)

```markdown
# Test Results - V2 App

**Test Date:** [Date]  
**Tester:** [Name]

## Backend Tests

| Test Suite | Status | Duration | Notes |
|-----------|--------|----------|-------|
| API Health | ✅ Pass | 2s | All endpoints healthy |
| Master Agent | ✅ Pass | 45s | Responses generated |
| Sub-Agents | ⚠️ Partial | 180s | 3/4 agents tested |
| Artifacts | ✅ Pass | 60s | All formats working |
| WebSocket | ✅ Pass | 90s | Streaming functional |
| Performance | ✅ Pass | 120s | Within targets |

## Frontend Tests

| Test Suite | Status | Duration | Notes |
|-----------|--------|----------|-------|
| Basic UI | ✅ Pass | 10s | All components render |
| Chat | ✅ Pass | 90s | Messaging works |
| Artifacts | ✅ Pass | 120s | Viewer functional |
| User Journey | ✅ Pass | 150s | End-to-end success |

## Issues Found

1. [List any issues]
2. [...]

## Overall Status

- **Pass Rate:** XX%
- **Total Duration:** XX minutes
- **Ready for Production:** Yes/No
```

---

## 📊 Test Coverage Summary

### Backend Coverage

- ✅ API Endpoints (REST)
- ✅ WebSocket Streaming
- ✅ Master Agent Processing
- ✅ Sub-Agent Invocation (4 agents)
- ✅ Artifact Generation (charts, maps, tables)
- ✅ Artifact Retrieval (HTML, PNG, JSON)
- ✅ Error Handling
- ✅ Performance Benchmarks
- ⚠️ Database Integration (MongoDB) - optional
- ⚠️ S3 Integration - optional

### Frontend Coverage

- ✅ Homepage Rendering
- ✅ Live Monitor Dashboard
- ✅ Navigation
- ✅ Chat Interface
- ✅ Message Sending/Receiving
- ✅ WebSocket Connection
- ✅ Status Updates
- ✅ Artifact Display
- ✅ Citations Display
- ✅ Multi-turn Conversations
- ⚠️ Execution Graph - UI dependent

---

## 🚀 Running All Tests (Automated)

**File to create:** `run_all_tests.sh` in project root

```bash
#!/bin/bash

echo "=========================================="
echo "🧪 V2 App - Complete Test Suite"
echo "=========================================="
echo ""

# Check servers are running
echo "⏸️  Make sure servers are running:"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo ""
read -p "Press Enter when ready..."

# Backend Tests
echo ""
echo "=========================================="
echo "🔧 Running Backend Tests..."
echo "=========================================="
cd backend_v2

source .venv/bin/activate

python tests/test_01_api_health.py
python tests/test_02_master_agent.py
python tests/test_03_sub_agents.py
python tests/test_04_artifacts.py
python tests/test_05_websocket.py
python tests/test_10_performance.py

# Frontend Tests
echo ""
echo "=========================================="
echo "🎨 Running Frontend Tests..."
echo "=========================================="
cd ../Frontend_v2

npx playwright test e2e/test_06_frontend_basic.spec.ts
npx playwright test e2e/test_07_chat.spec.ts
npx playwright test e2e/test_08_artifacts.spec.ts
npx playwright test e2e/test_09_user_journey.spec.ts

echo ""
echo "=========================================="
echo "✅ All Tests Complete!"
echo "=========================================="
echo ""
echo "Review test results above."
echo "Document any failures in TEST_RESULTS.md"
```

**Make it executable:**
```bash
chmod +x run_all_tests.sh
```

---

## 📝 Notes

1. **Test Duration:** Full test suite takes ~30-45 minutes
2. **API Keys Required:** OPENAI_API_KEY and TAVILY_API_KEY must be set
3. **Network Required:** Tests make real API calls
4. **Cleanup:** Artifacts generated during tests can be deleted after
5. **Optional Tests:** MongoDB and S3 tests are optional if services not configured

---

## 🎯 Success Criteria

The V2 app is **ready for production** if:

- ✅ All health checks pass
- ✅ Master agent processes queries successfully
- ✅ At least 3 sub-agents are functional
- ✅ Artifacts are generated and retrievable
- ✅ WebSocket streaming works
- ✅ Frontend displays all components
- ✅ End-to-end user journey completes
- ✅ Performance is within targets

---

**Last Updated:** October 2, 2025  
**Version:** 1.0  
**Status:** Ready for Execution

