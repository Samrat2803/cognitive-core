# Team B Database Integration Guide

## 🚀 **Setup Instructions for Team A**

### **Step 1: Install Dependencies**
```bash
cd backend/
uv pip install motor pymongo pydantic python-dotenv
```

### **Step 2: Create .env File**
Copy `backend/env.example` to `backend/.env` and update with your API keys:
```bash
cp env.example .env
# Edit .env with your Tavily and OpenAI API keys
```

The MongoDB connection string is already configured in the env.example file.

### **Step 3: Import Database Service**
```python
# In your backend/app.py
from database import db_interface, mongo_service

# Initialize on startup
@app.on_event("startup")
async def startup():
    await db_interface.initialize()
    print("✅ Database connected successfully")

@app.on_event("shutdown") 
async def shutdown():
    await db_interface.cleanup()
    print("🔌 Database connection closed")
```

## 📋 **Usage Examples**

### **Create and Process Query**
```python
@app.post("/research")
async def research_endpoint(request: ResearchRequest):
    # 1. Create query record
    query_id = await mongo_service.create_query({
        "query_text": request.query,
        "user_session": request.user_session or "anonymous",
        "options": {
            "max_results": request.max_results or 10,
            "search_depth": "advanced"
        }
    })
    
    # 2. Update status to processing
    await mongo_service.update_query_status(query_id, "processing")
    
    # 3. Run your research agent (existing code)
    # ... your research logic here ...
    
    # 4. Save results
    await mongo_service.save_results(query_id, {
        "final_answer": result["final_answer"],
        "search_terms": result["search_terms"],
        "sources": [
            {
                "url": source["url"],
                "title": source["title"], 
                "relevance_score": source["score"],
                "content_snippet": source["content"][:200]
            }
            for source in result["sources"]
        ],
        "agent_workflow": [
            {
                "step_name": "Query Analysis",
                "duration_ms": 1500,
                "output_summary": "Extracted key search terms",
                "agent_type": "analyzer"
            },
            # Add more workflow steps...
        ]
    })
    
    # 5. Mark as completed
    processing_time = 45000  # Calculate actual time
    await mongo_service.update_query_status(
        query_id, "completed", processing_time_ms=processing_time
    )
    
    # 6. Record analytics
    await mongo_service.record_analytics(query_id, processing_time)
    
    return {"query_id": query_id, "status": "completed"}
```

### **Get Query Results**
```python
@app.get("/research/{query_id}")
async def get_results(query_id: str):
    # Get query status
    query = await mongo_service.get_query(query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    if query.status == "completed":
        # Get results
        results = await mongo_service.get_results(query_id)
        return {
            "query_id": query_id,
            "status": "completed",
            "query": query.query_text,
            "final_answer": results.final_answer,
            "sources": results.sources,
            "search_terms": results.search_terms,
            "processing_time_ms": query.processing_time_ms,
            "created_at": query.created_at,
            "completed_at": query.completed_at
        }
    else:
        return {
            "query_id": query_id,
            "status": query.status,
            "progress": 65,  # You can calculate this
            "current_step": "Analyzing search results"
        }
```

### **Get Query History**
```python
@app.get("/research")
async def get_query_history(
    user_session: str = Query(...),
    limit: int = 10,
    offset: int = 0
):
    queries = await mongo_service.get_user_queries(user_session, limit, offset)
    return {
        "queries": [
            {
                "query_id": q.query_id,
                "query": q.query_text,
                "status": q.status,
                "created_at": q.created_at,
                "processing_time_ms": q.processing_time_ms
            }
            for q in queries
        ],
        "total": len(queries),
        "limit": limit,
        "offset": offset
    }
```

### **Analytics Endpoint**
```python
@app.get("/analytics")
async def get_analytics():
    dashboard_data = await analytics_service.get_dashboard_data()
    return {
        "total_queries": dashboard_data["total_queries"],
        "success_rate": dashboard_data["success_rate"],
        "avg_processing_time_ms": dashboard_data["avg_processing_time_ms"],
        "popular_topics": dashboard_data["popular_topics"],
        "daily_query_count": dashboard_data["daily_query_count"]
    }
```

## 🧪 **Testing Your Integration**

```python
# Test script to verify database integration
import asyncio
from database import db_interface, mongo_service

async def test_integration():
    await db_interface.initialize()
    
    # Test query creation
    query_id = await mongo_service.create_query({
        "query_text": "Test integration query",
        "user_session": "test-session"
    })
    print(f"✅ Created query: {query_id}")
    
    # Test results saving
    await mongo_service.save_results(query_id, {
        "final_answer": "Integration test successful!",
        "search_terms": ["test", "integration"],
        "sources": []
    })
    print("✅ Saved results")
    
    # Test retrieval
    results = await mongo_service.get_results(query_id)
    print(f"✅ Retrieved results: {results.final_answer}")
    
    await db_interface.cleanup()
    print("✅ Integration test completed")

# Run: asyncio.run(test_integration())
```

## 🔧 **Database Collections Schema**

### **Queries Collection**
- `query_id` (string, unique): External UUID
- `query_text` (string): User's research query
- `user_session` (string, optional): Session tracking
- `status` (enum): "processing" | "completed" | "failed" 
- `options` (object): Query execution options
- `created_at`, `updated_at` (datetime): Timestamps
- `processing_time_ms` (int): Total processing time

### **Results Collection** 
- `query_id` (string, unique): Links to query
- `final_answer` (string): Formatted research response
- `search_terms` (array): Terms used for search
- `sources` (array): Source URLs with metadata
- `agent_workflow` (array): Agent execution steps
- `confidence_score` (float): Result confidence

### **Analytics Collection**
- `date` (datetime): Daily aggregation date
- `total_queries`, `completed_queries`, `failed_queries` (int)
- `avg_processing_time_ms` (float): Performance metrics
- `popular_topics` (array): Trending search terms

## 🚨 **Error Handling**

```python
try:
    query_id = await mongo_service.create_query(query_data)
except Exception as e:
    # Handle database errors
    await mongo_service.update_query_status(
        query_id, "failed", error_message=str(e)
    )
    raise HTTPException(status_code=500, detail="Database error")
```

**Team A: The database service is ready for integration! 🎉**
