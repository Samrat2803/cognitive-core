"""
Direct MongoDB verification to show stored data
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def check_mongodb():
    # Connect to MongoDB
    client = MongoClient(os.getenv('MONGODB_CONNECTION_STRING'))
    db = client[os.getenv('DATABASE_NAME', 'web_research_agent')]

    print('🔍 DIRECT MONGODB VERIFICATION')
    print('=' * 50)

    # Check recent queries (last hour)
    recent_time = datetime.utcnow() - timedelta(hours=1)
    print(f'🕐 Checking records since: {recent_time}')

    # Queries collection
    queries = list(db.queries.find({
        'created_at': {'$gte': recent_time}
    }).sort('created_at', -1).limit(10))

    print(f'\n📋 RECENT QUERIES ({len(queries)} found):')
    for i, query in enumerate(queries, 1):
        print(f'   {i}. Query ID: {query.get("query_id", "N/A")}')
        print(f'      Text: {query.get("query_text", "N/A")}')
        print(f'      Session: {query.get("user_session", "N/A")}')
        print(f'      Status: {query.get("status", "N/A")}')
        print(f'      Created: {query.get("created_at", "N/A")}')
        if query.get("processing_time_ms"):
            print(f'      Processing Time: {query.get("processing_time_ms", "N/A")} ms')
        print()

    # Results collection  
    results = list(db.results.find({
        'created_at': {'$gte': recent_time}
    }).sort('created_at', -1).limit(5))

    print(f'📊 RECENT RESULTS ({len(results)} found):')
    for i, result in enumerate(results, 1):
        print(f'   {i}. Query ID: {result.get("query_id", "N/A")}')
        answer = result.get('final_answer', '')
        print(f'      Answer Length: {len(answer)} characters')
        print(f'      Search Terms: {result.get("search_terms", [])}')
        print(f'      Sources: {len(result.get("sources", []))}')
        print(f'      Created: {result.get("created_at", "N/A")}')
        if answer and len(answer) > 100:
            print(f'      Answer Preview: {answer[:200]}...')
        print()

    # Analytics
    analytics = list(db.analytics.find().sort('date', -1).limit(3))
    print(f'📈 ANALYTICS SUMMARY:')
    for analytics_doc in analytics:
        date = analytics_doc.get("date", "N/A")
        total = analytics_doc.get("total_queries", 0)
        completed = analytics_doc.get("completed_queries", 0)
        print(f'   Date: {date} | Total: {total}, Completed: {completed}')

    # Check all collections
    print(f'\n📚 DATABASE COLLECTIONS:')
    collections = db.list_collection_names()
    for collection_name in collections:
        count = db[collection_name].count_documents({})
        print(f'   {collection_name}: {count} documents')

    client.close()
    print('\n✅ Direct MongoDB verification completed')

if __name__ == "__main__":
    check_mongodb()
