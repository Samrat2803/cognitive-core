"""
Demonstrate complete analysis flow with real-time progress tracking
"""

import asyncio
import time
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

async def demo_complete_analysis_flow():
    """Demonstrate a complete analysis from start to completion"""
    print("🚀 Demonstrating Complete Analysis Flow")
    print("=" * 50)
    
    # Step 1: Start an analysis
    print("1️⃣ Starting analysis...")
    response = client.post("/api/analysis/execute", json={
        "query_text": "US-Iran diplomatic relations sentiment analysis",
        "parameters": {
            "countries": ["United States", "Iran"],
            "days": 7,
            "results_per_country": 15
        },
        "session_id": "demo_session"
    })
    
    analysis_id = response.json()["analysis_id"]
    print(f"   ✅ Analysis started: {analysis_id}")
    
    # Step 2: Monitor progress
    print("\n2️⃣ Monitoring progress...")
    for i in range(10):  # Check for up to 10 seconds
        response = client.get(f"/api/analysis/{analysis_id}")
        data = response.json()
        status = data["status"]
        
        if status == "processing":
            progress = data["progress"]
            print(f"   ⏳ {progress['completion_percentage']}% - {progress['current_step']}")
            
        elif status == "completed":
            print(f"   ✅ Analysis completed!")
            results = data["results"]
            summary = results["summary"]
            print(f"   📊 Countries analyzed: {summary['countries_analyzed']}")
            print(f"   📄 Total articles: {summary['total_articles']}")
            print(f"   🎯 Overall sentiment: {summary['overall_sentiment']}")
            
            country_results = results["country_results"]
            for country in country_results:
                print(f"   🇺🇸 {country['country']}: {country['sentiment_score']} ({country['dominant_sentiment']})")
            
            break
            
        elif status == "failed":
            print(f"   ❌ Analysis failed: {data['error']}")
            break
        
        time.sleep(1)
    
    print("\n✅ Demo completed successfully!")

def demo_websocket_simulation():
    """Simulate WebSocket message flow"""
    print("\n🌐 WebSocket Message Flow Simulation")
    print("-" * 30)
    
    # This simulates what would happen in a real WebSocket connection
    from websocket_manager import websocket_manager
    from models.api_schemas import AnalysisProgress, ProgressMessage
    
    # Simulate progress updates
    progress_updates = [
        {"current_step": "analyzing_query", "completion_percentage": 10},
        {"current_step": "analyzing_united_states", "completion_percentage": 40},
        {"current_step": "analyzing_iran", "completion_percentage": 70},
        {"current_step": "synthesizing_results", "completion_percentage": 90},
    ]
    
    for i, progress_data in enumerate(progress_updates):
        print(f"   📡 WebSocket would broadcast: {progress_data['current_step']} - {progress_data['completion_percentage']}%")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_complete_analysis_flow())
    demo_websocket_simulation()
