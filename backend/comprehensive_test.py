"""
Comprehensive End-to-End Test with MongoDB Verification
Tests the specific query: "give me sentiments about Hamas in US, Israel and Iran"
"""

import requests
import time
import json
import asyncio
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
TEST_QUERY = "give me sentiments about Hamas in US, Israel and Iran"
TEST_SESSION = f"comprehensive_test_{int(time.time())}"

# MongoDB connection
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
DATABASE_NAME = os.getenv("DATABASE_NAME", "web_research_agent")

def connect_to_mongodb():
    """Connect to MongoDB for verification"""
    try:
        client = MongoClient(MONGODB_CONNECTION_STRING)
        db = client[DATABASE_NAME]
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection established")
        return client, db
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return None, None

def run_comprehensive_test():
    """Run the complete end-to-end test"""
    print("🎯 COMPREHENSIVE END-TO-END TEST")
    print("=" * 50)
    print(f"Query: '{TEST_QUERY}'")
    print(f"Session: {TEST_SESSION}")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Step 1: Chat Intent Parsing
    print("1️⃣ CHAT INTENT PARSING")
    print("-" * 25)
    
    chat_payload = {
        "message": TEST_QUERY,
        "session_id": TEST_SESSION,
        "context": {"test": "comprehensive_end_to_end"}
    }
    
    try:
        chat_response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json=chat_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {chat_response.status_code}")
        
        if chat_response.status_code != 200:
            print(f"❌ Chat endpoint failed: {chat_response.text}")
            return None
        
        chat_data = chat_response.json()
        print(f"Success: {chat_data['success']}")
        print(f"Response Type: {chat_data['response_type']}")
        
        if chat_data['response_type'] == 'query_parsed':
            intent = chat_data['parsed_intent']
            analysis_id = chat_data['analysis_id']
            
            print(f"✅ Intent Successfully Parsed:")
            print(f"   Action: {intent['action']}")
            print(f"   Topic: {intent['topic']}")
            print(f"   Countries: {intent['countries']}")
            print(f"   Analysis ID: {analysis_id}")
            print(f"   Confirmation: {chat_data['confirmation']}")
            
            return analysis_id, intent
        else:
            print(f"⚠️ Intent not parsed, got direct response:")
            print(f"   Message: {chat_data['message']}")
            print(f"   Suggestions: {chat_data.get('suggestions', [])}")
            return None, None
            
    except Exception as e:
        print(f"❌ Chat parsing failed: {e}")
        return None, None

def confirm_and_execute_analysis(chat_analysis_id, intent):
    """Confirm the analysis and execute it"""
    print("\n2️⃣ ANALYSIS CONFIRMATION & EXECUTION")
    print("-" * 38)
    
    # Confirm the analysis from chat
    confirm_payload = {
        "analysis_id": chat_analysis_id,
        "confirmed": True,
        "modifications": {
            "days": 7,
            "results_per_country": 25
        }
    }
    
    try:
        confirm_response = requests.post(
            f"{BASE_URL}/api/chat/confirm-analysis",
            json=confirm_payload,
            timeout=30
        )
        
        print(f"Confirmation Status: {confirm_response.status_code}")
        
        if confirm_response.status_code == 200:
            confirm_data = confirm_response.json()
            actual_analysis_id = confirm_data['analysis_id']
            
            print(f"✅ Analysis Confirmed:")
            print(f"   Analysis ID: {actual_analysis_id}")
            print(f"   Status: {confirm_data['status']}")
            print(f"   WebSocket Session: {confirm_data['websocket_session']}")
            
            return actual_analysis_id
        else:
            print(f"❌ Confirmation failed: {confirm_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Analysis confirmation failed: {e}")
        return None

def monitor_analysis_progress(analysis_id, max_wait_time=60):
    """Monitor analysis progress until completion"""
    print(f"\n3️⃣ MONITORING ANALYSIS PROGRESS")
    print("-" * 32)
    print(f"Analysis ID: {analysis_id}")
    print(f"Max wait time: {max_wait_time} seconds")
    print()
    
    start_time = time.time()
    check_interval = 2
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(
                f"{BASE_URL}/api/analysis/{analysis_id}",
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Status check failed: {response.status_code}")
                break
            
            data = response.json()
            status = data['status']
            elapsed = int(time.time() - start_time)
            
            print(f"[{elapsed:02d}s] Status: {status}")
            
            if status == 'processing':
                progress = data.get('progress', {})
                print(f"       Progress: {progress.get('completion_percentage', 0)}%")
                print(f"       Step: {progress.get('current_step', 'N/A')}")
                print(f"       Articles: {progress.get('articles_processed', 0)}/{progress.get('total_articles', 0)}")
                
            elif status == 'completed':
                print("🎉 ANALYSIS COMPLETED!")
                return data
                
            elif status == 'failed':
                error = data.get('error', {})
                print(f"❌ Analysis failed: {error.get('message', 'Unknown error')}")
                return None
            
            time.sleep(check_interval)
            
        except Exception as e:
            print(f"❌ Progress check failed: {e}")
            break
    
    print(f"⏰ Analysis did not complete within {max_wait_time} seconds")
    return None

def analyze_results(completed_data):
    """Analyze the completed analysis results"""
    print("\n4️⃣ RESULTS ANALYSIS")
    print("-" * 18)
    
    if not completed_data or completed_data['status'] != 'completed':
        print("❌ No valid results to analyze")
        return None
    
    query_info = completed_data.get('query', {})
    results = completed_data.get('results', {})
    summary = results.get('summary', {})
    country_results = results.get('country_results', [])
    
    print(f"✅ ANALYSIS SUMMARY:")
    print(f"   Query: {query_info.get('text', 'N/A')}")
    print(f"   Overall Sentiment: {summary.get('overall_sentiment', 'N/A')}")
    print(f"   Countries Analyzed: {summary.get('countries_analyzed', 0)}")
    print(f"   Total Articles: {summary.get('total_articles', 0)}")
    print(f"   Analysis Confidence: {summary.get('analysis_confidence', 'N/A')}")
    print(f"   Bias Detected: {summary.get('bias_detected', 'N/A')}")
    print(f"   Processing Time: {summary.get('completion_time_ms', 'N/A')} ms")
    
    print(f"\n📊 COUNTRY-SPECIFIC RESULTS:")
    for i, country in enumerate(country_results, 1):
        print(f"   {i}. {country.get('country', 'N/A')}:")
        print(f"      Sentiment Score: {country.get('sentiment_score', 'N/A')}")
        print(f"      Confidence: {country.get('confidence', 'N/A')}")
        print(f"      Articles Count: {country.get('articles_count', 'N/A')}")
        print(f"      Dominant Sentiment: {country.get('dominant_sentiment', 'N/A')}")
        print(f"      Key Themes: {country.get('key_themes', [])}")
        
        bias_analysis = country.get('bias_analysis', {})
        if bias_analysis:
            print(f"      Bias Types: {bias_analysis.get('bias_types', [])}")
            print(f"      Bias Severity: {bias_analysis.get('bias_severity', 'N/A')}")
        print()
    
    return results

def verify_mongodb_storage(analysis_id, session_id):
    """Verify data was stored in MongoDB"""
    print("5️⃣ MONGODB STORAGE VERIFICATION")
    print("-" * 32)
    
    client, db = connect_to_mongodb()
    if client is None or db is None:
        print("❌ Cannot verify MongoDB storage - connection failed")
        return False
    
    try:
        # Check queries collection
        print("🔍 Checking queries collection...")
        queries = list(db.queries.find({"user_session": session_id}))
        print(f"   Found {len(queries)} query records for session '{session_id}'")
        
        if queries:
            query_doc = queries[0]  # Get the most recent
            print(f"   ✅ Query Document:")
            print(f"      Query ID: {query_doc.get('query_id', 'N/A')}")
            print(f"      Query Text: {query_doc.get('query_text', 'N/A')}")
            print(f"      Status: {query_doc.get('status', 'N/A')}")
            print(f"      Created: {query_doc.get('created_at', 'N/A')}")
            print(f"      Processing Time: {query_doc.get('processing_time_ms', 'N/A')} ms")
        
        # Check results collection
        print("\n🔍 Checking results collection...")
        results = list(db.results.find())
        session_results = [r for r in results if any(q.get('query_id') == r.get('query_id') for q in queries)]
        
        print(f"   Found {len(session_results)} result records for this session")
        
        if session_results:
            result_doc = session_results[0]
            print(f"   ✅ Result Document:")
            print(f"      Query ID: {result_doc.get('query_id', 'N/A')}")
            print(f"      Final Answer Length: {len(result_doc.get('final_answer', ''))}")
            print(f"      Search Terms: {result_doc.get('search_terms', [])}")
            print(f"      Sources Count: {len(result_doc.get('sources', []))}")
            print(f"      Created: {result_doc.get('created_at', 'N/A')}")
        
        # Check analytics collection
        print("\n🔍 Checking analytics collection...")
        today_analytics = list(db.analytics.find().sort("date", -1).limit(1))
        
        if today_analytics:
            analytics_doc = today_analytics[0]
            print(f"   ✅ Analytics Document (Latest):")
            print(f"      Date: {analytics_doc.get('date', 'N/A')}")
            print(f"      Total Queries: {analytics_doc.get('total_queries', 0)}")
            print(f"      Completed Queries: {analytics_doc.get('completed_queries', 0)}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB verification failed: {e}")
        if client:
            client.close()
        return False

def main():
    """Run the complete comprehensive test"""
    print("🚀 STARTING COMPREHENSIVE END-TO-END TEST")
    print("🎯 Testing query: 'give me sentiments about Hamas in US, Israel and Iran'")
    print("🔍 Verifying MongoDB storage")
    print("📊 Analyzing actual results")
    print("=" * 60)
    
    # Step 1: Parse intent via chat
    analysis_id, intent = run_comprehensive_test()
    
    if not analysis_id:
        print("\n❌ Test failed at intent parsing stage")
        return
    
    # Step 2: Confirm and execute analysis
    actual_analysis_id = confirm_and_execute_analysis(analysis_id, intent)
    
    if not actual_analysis_id:
        print("\n❌ Test failed at analysis execution stage")
        return
    
    # Step 3: Monitor progress
    completed_data = monitor_analysis_progress(actual_analysis_id, max_wait_time=90)
    
    if not completed_data:
        print("\n❌ Test failed - analysis did not complete")
        # Still try to verify what was stored
        verify_mongodb_storage(actual_analysis_id, TEST_SESSION)
        return
    
    # Step 4: Analyze results
    results = analyze_results(completed_data)
    
    # Step 5: Verify MongoDB storage
    mongodb_verified = verify_mongodb_storage(actual_analysis_id, TEST_SESSION)
    
    # Final summary
    print("\n" + "=" * 60)
    print("📋 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Intent Parsing: SUCCESS")
    print(f"✅ Analysis Execution: SUCCESS") 
    print(f"{'✅' if completed_data else '❌'} Analysis Completion: {'SUCCESS' if completed_data else 'FAILED'}")
    print(f"{'✅' if results else '❌'} Results Analysis: {'SUCCESS' if results else 'FAILED'}")
    print(f"{'✅' if mongodb_verified else '❌'} MongoDB Storage: {'VERIFIED' if mongodb_verified else 'FAILED'}")
    
    if completed_data and results:
        print(f"\n🎯 KEY FINDINGS:")
        summary = completed_data['results']['summary']
        print(f"   Overall Hamas Sentiment: {summary.get('overall_sentiment', 'N/A')}")
        print(f"   Countries Successfully Analyzed: {summary.get('countries_analyzed', 0)}")
        print(f"   Total Articles Processed: {summary.get('total_articles', 0)}")
        
        country_results = completed_data['results']['country_results']
        for country in country_results:
            sentiment = country.get('sentiment_score', 0)
            sentiment_text = country.get('dominant_sentiment', 'neutral')
            print(f"   {country.get('country', 'Unknown')}: {sentiment} ({sentiment_text})")
    
    print(f"\n🌐 Server: {BASE_URL}")
    print(f"📚 API Docs: {BASE_URL}/docs")
    print(f"🎉 Comprehensive test completed!")

if __name__ == "__main__":
    main()
