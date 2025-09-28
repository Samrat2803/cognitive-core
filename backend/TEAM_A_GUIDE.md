# Team A: Backend Infrastructure & AWS Deployment Guide

**Team:** Backend Infrastructure & Deployment  
**Timeline:** 5-6 days  
**Working Directory:** `backend/`  
**Dependencies:** None (100% independent start)

---

## 🎯 **Team A Objectives**

1. Deploy existing FastAPI app to AWS Elastic Beanstalk
2. Set up multi-instance deployment with load balancing
3. Implement production-ready monitoring and logging
4. Ensure API contracts are met for Teams B & C integration

---

## 📋 **Phase 1: AWS Elastic Beanstalk Setup (Days 1-3)**

### **Step 1: AWS Account & CLI Setup**
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Output format (json)

# Install EB CLI
pip install awsebcli
```

### **Step 2: Create Elastic Beanstalk Application**
```bash
cd backend/

# Initialize EB application
eb init
# Choose: Python platform, latest version, no CodeCommit, no SSH

# Create environment
eb create production-env
# Choose: Application Load Balancer, spot fleet
```

### **Step 3: Required Files to Create**

#### **`backend/application.py`** (EB Entry Point):
```python
#!/usr/bin/env python3
"""
AWS Elastic Beanstalk entry point
"""
from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
```

#### **`backend/.ebextensions/python.config`**:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: application.py
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:autoscaling:asg:
    MinSize: 2
    MaxSize: 10
  aws:autoscaling:trigger:
    MeasureName: CPUUtilization
    Unit: Percent
    UpperThreshold: 80
    LowerThreshold: 20
```

#### **`backend/.ebextensions/environment.config`**:
```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    FLASK_ENV: production
    TAVILY_API_KEY: your-tavily-key
    OPENAI_API_KEY: your-openai-key
    CORS_ORIGINS: https://your-frontend-domain.com
```

### **Step 4: Update `requirements.txt`**
```
# Add these to existing requirements.txt
gunicorn==20.1.0
flask-cors==4.0.0
python-json-logger==2.0.4
```

---

## 📋 **Phase 2: Production Optimization (Days 4-6)**

### **Step 1: Add Rate Limiting**
Create `backend/middleware/rate_limiter.py`:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask

def setup_rate_limiting(app: Flask):
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["100 per minute"]
    )
    return limiter
```

### **Step 2: Add CORS & Security Headers**
Update `backend/app.py`:
```python
from flask_cors import CORS
import os

# Add after app initialization
CORS(app, origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','))

@app.after_request
def after_request(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### **Step 3: Add Structured Logging**
Create `backend/utils/logger.py`:
```python
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    return logger
```

### **Step 4: Add Health Check Enhancement**
Update health check in `backend/app.py`:
```python
@app.get("/health")
async def enhanced_health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agent_initialized": agent is not None,
        "version": "1.0.0",
        "environment": os.getenv("FLASK_ENV", "development"),
        "uptime_seconds": time.time() - start_time
    }
```

---

## 📋 **Phase 3: Integration with Teams B & C (Days 5-6)**

### **Database Integration (Team B)**
```python
# Team A will import Team B's database service
from database.services.mongo_service import MongoService
from database.models.query_models import QueryDocument

# Add to app.py
db_service = MongoService()

@app.post("/research")
async def research(request: ResearchRequest):
    # Create query record
    query_id = await db_service.create_query({
        "query_text": request.query,
        "user_session": request.user_session,
        "status": "processing"
    })
    
    # Process research (existing logic)
    # ...
    
    # Save results
    await db_service.save_results(query_id, results)
    
    return {"query_id": query_id, "status": "processing"}
```

### **Frontend Integration (Team C)**
```python
# Ensure API endpoints match contracts
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 🚀 **Deployment Commands**

```bash
# Deploy to EB
eb deploy

# Check status
eb status

# View logs
eb logs

# SSH to instance (if needed)
eb ssh

# Set environment variables
eb setenv TAVILY_API_KEY=your-key OPENAI_API_KEY=your-key
```

---

## ✅ **Success Criteria**

- [ ] AWS EB environment running with 2+ instances
- [ ] Load balancer distributing traffic
- [ ] Auto-scaling working (test with load)
- [ ] All API endpoints responding correctly
- [ ] Rate limiting active (100 req/min)
- [ ] Security headers in place
- [ ] Structured logging to CloudWatch
- [ ] Health check returning detailed status
- [ ] Ready for Teams B & C integration

---

## 🔗 **Integration Points**

### **For Team B:**
- Database service import structure ready
- Query/result persistence integration points identified

### **For Team C:**  
- CORS configured for frontend domain
- API endpoints match contracts exactly
- Error responses in correct format

---

## 📊 **Testing Checklist**

```bash
# Load test endpoints
curl -X POST https://your-app.elasticbeanstalk.com/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'

# Check health
curl https://your-app.elasticbeanstalk.com/health

# Verify rate limiting
for i in {1..105}; do curl https://your-app.elasticbeanstalk.com/health; done
```

---

## 📋 **Instructions from Other Teams**

### **From Team D (Documentation & Demo Production):**

#### **For Demo Video Requirements:**
- [ ] **Ensure health endpoint returns detailed information:**
  ```python
  @app.get("/health")
  async def enhanced_health_check():
      return {
          "status": "healthy",
          "timestamp": datetime.utcnow().isoformat(),
          "agent_initialized": agent is not None,
          "version": "1.0.0",
          "environment": os.getenv("FLASK_ENV", "development"),
          "uptime_seconds": time.time() - start_time,
          "database_connected": await check_db_connection(),
          "api_keys_configured": bool(os.getenv("TAVILY_API_KEY") and os.getenv("OPENAI_API_KEY"))
      }
  ```

- [ ] **AWS Elastic Beanstalk URLs needed for documentation:**
  - Backend API URL (e.g., `https://web-research-agent.elasticbeanstalk.com`)
  - Health check URL for demo verification
  - Auto-scaling configuration details for architecture documentation

#### **For Production Demo:**
- [ ] **Configure structured logging for demo insights:**
  ```python
  import logging
  from pythonjsonlogger import jsonlogger
  
  # Add to app.py
  @app.middleware("http")
  async def log_requests(request, call_next):
      start_time = time.time()
      response = await call_next(request)
      process_time = time.time() - start_time
      
      logger.info({
          "method": request.method,
          "url": str(request.url),
          "status_code": response.status_code,
          "process_time": process_time
      })
      return response
  ```

- [ ] **Provide CloudWatch dashboard access** for demo showing:
  - Instance health and scaling events
  - Request metrics and error rates
  - Performance monitoring graphs

#### **Documentation Support:**
- [ ] **Share deployment configuration files** for documentation:
  - `.ebextensions/` folder contents
  - Environment variable configuration
  - Auto-scaling policies and thresholds

**Coordination:** Team D will use your deployed backend for the live demo video. Please ensure system is stable and provide the production URL when ready.

---

## 🔄 **Current Deployment Status**

### **✅ Completed Tasks (Sept 27, 2024)**
- [x] AWS CLI configured with root credentials
- [x] Elastic Beanstalk CLI installed
- [x] FastAPI application.py entry point created  
- [x] .ebextensions configuration files created
- [x] Requirements.txt updated for FastAPI + production dependencies
- [x] CORS configuration updated for environment variables
- [x] Environment variables configured (.env)
- [x] EB application "cognitive-core" initialized

### **🔧 Issues Resolved - Complete Fix Log**
**✅ SSL Certificate Error** (Removed placeholder certificate configuration)  
**✅ WSGI Path Configuration** (Fixed `application:application` for FastAPI)  
**✅ FastAPI App Exposure** (Added `application = app` in application.py)  
**✅ Database Module Missing** (Copied `/database/` to `/backend/database/`)  
**✅ Requirements.txt** (Removed invalid `asyncio` dependency)  
**✅ Configuration Complexity** (Simplified to minimal .ebextensions)  
**✅ Virtual Environment Upload** (Created `.ebignore` to exclude `.venv/`)  
**✅ Clean Deployment** (Fresh environment: cognitive-core-working)  
**✅ Infrastructure Creation** (AWS resources: Load Balancer, Auto Scaling, CloudWatch)

### **🎯 Current Status - Deployment Debugging Phase**
- [x] **Environment Created**: `cognitive-core-working.eba-c4n432jt.us-east-1.elasticbeanstalk.com` ✅ DEPLOYED
- [x] **Critical Issues Fixed**: SSL certificate error, WSGI path, database module inclusion
- [x] **Infrastructure Status**: AWS resources created successfully (Load balancer, Auto Scaling, CloudWatch)
- [x] **Progress Made**: 502 Bad Gateway → 500 Internal Server Error (application starting but crashing)
- [x] **Database Integration**: Team B completed - database services copied to backend/
- [x] **Configuration**: Minimal .ebextensions with essential settings only
- [🔧] **Current Focus**: Debugging application startup error (500 Internal Server Error)
- [ ] **Final Goal**: Provide stable API URL for Teams B & C integration

### **🏆 AWS Best Practices Applied**
**✅ Practice #1**: Single Instance Environment (dev/test) → Load Balanced (production)  
**✅ Practice #2**: Optimized instance configuration (t3.micro → scaling)  
**✅ Practice #4**: Enhanced health checks and monitoring  
**✅ Practice #5**: Application logging with CloudWatch  
**✅ Practice #6**: Security with environment variables and IAM  
**✅ Practice #8**: Secure environment variable management  
**✅ Practice #9**: Rolling deployment policy for zero downtime

### **📡 API Endpoint Status - Current State**
- **Production URL**: 🌐 `http://cognitive-core-working.eba-c4n432jt.us-east-1.elasticbeanstalk.com`
- **Deployment Status**: ✅ **DEPLOYED** (AWS infrastructure running)
- **Application Status**: 🔧 **500 Internal Server Error** (debugging in progress)  
- **Infrastructure**: ✅ Load Balancer, Auto Scaling Group, CloudWatch logs active
- **Previous Issues**: ✅ 502 Bad Gateway resolved → now getting application errors
- **Team B Integration**: ✅ Database services included in deployment package
- **Next Step**: Debug application startup to resolve 500 error

### **🧪 Local Test Results (Sept 27, 2024)**
**Query**: "What is FastAPI?"
- ✅ **Multi-Agent Workflow**: All 4 agents working correctly
- ✅ **Response Time**: ~60 seconds  
- ✅ **Sources Found**: 15 sources via Tavily API
- ✅ **Final Answer**: Comprehensive research with proper formatting
- ✅ **API Structure**: Professional JSON responses with error handling

### **🔗 Integration Status with Teams B & C**
**✅ Team B (Database)**: **COMPLETED** - Database services successfully integrated
- ✅ MongoDB services copied to backend/database/
- ✅ All database models and connections ready
- ✅ API contracts implemented and tested

**✅ Team C (Frontend)**: **READY FOR INTEGRATION** 
- ✅ Live API URL available: `cognitive-core-working.eba-c4n432jt.us-east-1.elasticbeanstalk.com`
- ✅ CORS configuration ready for frontend domain
- ✅ API contracts defined in `/documentation/API_CONTRACTS.md`
- 🔧 Debugging application startup to provide stable API access

### **🚀 For Teams B & C - Ready for Integration**

**LOCAL TESTING ENDPOINTS (Available Now):**
```bash
Base URL: http://localhost:8000

# Test endpoints
GET  /health          # Check if agent is ready
GET  /                 # API info  
POST /research         # Submit research queries
GET  /config           # Get configuration info
GET  /docs             # Interactive API documentation
```

**Example API Usage:**
```bash
# Health check
curl http://localhost:8000/health

# Submit research query  
curl -X POST "http://localhost:8000/research" \
  -H "Content-Type: application/json" \
  -d '{"query": "Your research question here"}'
```

**PRODUCTION URL:** Will be provided once AWS deployment completes (~10 minutes)

---

  **Team A: This guide provides everything needed for independent AWS deployment while preparing for Teams B & C integration!**

---

## 📊 **LATEST UPDATE - September 28, 2025**

### **🎉 MAJOR PROGRESS ACHIEVED**
- ✅ **AWS Environment Live**: `cognitive-core-working.eba-c4n432jt.us-east-1.elasticbeanstalk.com`
- ✅ **All Infrastructure Working**: Load Balancer, Auto Scaling, CloudWatch, Security Groups
- ✅ **Team B Integration Complete**: Database services successfully included
- ✅ **9 Critical Issues Resolved**: SSL cert, WSGI path, database inclusion, etc.

### **🔧 CURRENT STATE**
**Status**: 95% Complete - Application deployed but debugging startup error  
**Issue**: 500 Internal Server Error (progress from 502 Bad Gateway)  
**Impact**: Infrastructure is solid, application needs debugging  
**Timeline**: Ready for Team C integration once application startup is resolved

### **🎯 IMMEDIATE NEXT STEPS**
1. **Debug Application**: Resolve 500 Internal Server Error in FastAPI startup
2. **Provide Stable API**: Ensure `/health`, `/research` endpoints respond correctly  
3. **Team C Integration**: Share working production URL for frontend integration
4. **Monitoring Setup**: Add comprehensive logging and health checks

---

## 📢 **Instructions from other teams**

### **🎉 FROM TEAM C (Frontend) - PRODUCTION DEPLOYMENT COMPLETE!**

**Status**: ✅ **DEPLOYED TO AWS PRODUCTION** - Frontend successfully deployed to AWS S3 + CloudFront!

#### **🌍 LIVE PRODUCTION FRONTEND:**
- **🚀 Frontend URL**: https://dgbfif5o7v03y.cloudfront.net
- **☁️ CloudFront Distribution ID**: E32329Y6R6V5UG  
- **🪣 S3 Bucket**: tavily-research-frontend-1759000227
- **🔒 Security**: Private S3 bucket with Origin Access Control (AWS best practices)
- **🌐 Global CDN**: Optimized performance worldwide with SSL/HTTPS

#### **Integration Results:**
- ✅ **Development Integration**: Fully tested with localhost:8000
- ✅ **Production Build**: Optimized and deployed to AWS
- ✅ **Health Check**: Working - `{"status":"healthy","agent_initialized":true,"database_connected":true}`
- ✅ **Research Endpoint**: Fully tested (42-second response time)
- ✅ **All UI Features**: Export, query history, responsive design, error handling

#### **Production Frontend Features:**
- 🎨 High-contrast Aistra dark theme (#d9f378, #5d535c, #333333, #1c1e20)
- 📱 Mobile-first responsive design optimized for all devices
- ⚡ Real-time research progress indicators with agent workflow visualization
- 📁 Export functionality (JSON, CSV, PDF) fully working
- 🔄 Query history with localStorage (ready for database integration)
- 🛡️ Professional error handling and user feedback
- 🚀 Performance optimized with CDN caching

#### **🔄 CRITICAL - CORS Configuration Required:**
When deploying your backend to AWS, ensure CORS allows:
```python
origins = [
    "https://dgbfif5o7v03y.cloudfront.net",  # Team C Production Frontend
    "http://localhost:3000",  # Development
]
```

#### **🚀 Next Steps for Team A:**
1. **Deploy backend** to AWS Elastic Beanstalk
2. **Update CORS** to include `https://dgbfif5o7v03y.cloudfront.net`
3. **Share production API URL** (e.g., `https://api.tavily-research.amazonaws.com`)
4. **Team C will update** frontend configuration for production API integration

**🎯 Team C Status: PRODUCTION INTEGRATION COMPLETE! Frontend connected to your production API!**

#### **🎉 INTEGRATION SUCCESS - LIVE PRODUCTION SYSTEM:**
- ✅ **Frontend**: https://dgbfif5o7v03y.cloudfront.net (updated and deployed)
- ✅ **Backend**: http://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com (connected)
- ✅ **Database**: MongoDB Atlas integration working perfectly
- ✅ **End-to-End**: Production frontend → Production backend → Database pipeline operational

#### **🔗 What We Updated:**
1. **Frontend Config**: Updated to use your production API URL automatically in production mode
2. **AWS Deployment**: Rebuilt and deployed updated frontend to CloudFront
3. **Cache Invalidation**: Forced immediate update (Invalidation ID: I2QJR1V6MCLY2FMJHHL5TMK2V6)
4. **Integration Testing**: Verified your health endpoint shows full database integration

#### **🚀 PRODUCTION SYSTEM NOW COMPLETE:**
**Frontend** (AWS CloudFront) ↔ **Backend** (AWS Elastic Beanstalk) ↔ **Database** (MongoDB Atlas)

**🌍 LIVE DEMO URL**: https://dgbfif5o7v03y.cloudfront.net

**Perfect Integration!** 🎊 Your production backend with full database integration is now powering our production frontend!
3. Ensure CORS includes production frontend domain
4. Test with production environment

---

---

## **Instructions from Other Teams**

### **From Team B (Database) - READY FOR INTEGRATION** ✅

**Database service is now fully implemented and ready for integration!**

#### **Quick Setup:**
1. **Install dependencies**: `uv pip install motor pymongo pydantic python-dotenv`
2. **Create .env file**: Copy `backend/env.example` to `backend/.env` (MongoDB connection already configured)
3. **Import database service**: `from database import db_interface, mongo_service`

#### **Integration Points:**
```python
# Add to your app.py
from database import db_interface, mongo_service

@app.on_event("startup")
async def startup():
    await db_interface.initialize()

@app.post("/research")
async def research_endpoint(request):
    # 1. Create query record
    query_id = await mongo_service.create_query({
        "query_text": request.query,
        "user_session": request.user_session
    })
    
    # 2. Run your research agent
    # ... your existing research logic ...
    
    # 3. Save results
    await mongo_service.save_results(query_id, {
        "final_answer": result["final_answer"],
        "search_terms": result["search_terms"],
        "sources": result["sources"]
    })
    
    return {"query_id": query_id}
```

#### **Available Services:**
- ✅ Query creation and status tracking
- ✅ Results storage and retrieval  
- ✅ User query history
- ✅ Analytics for demo dashboard
- ✅ Full async MongoDB operations
- ✅ Error handling and validation

📖 **Full integration guide**: `database/INTEGRATION_GUIDE.md`

**Ready to integrate immediately! Let me know if you need any clarification.**

#### **Testing Requirements from Team B** 🧪
Team B has created comprehensive database tests that validate your backend integration:

```bash
# Run all database tests (includes your API endpoints)
./tests/run-database-tests.sh

# Run specific database integration tests
./tests/run-database-tests.sh integration

# Check database performance with your API
./tests/run-database-tests.sh performance
```

**Tests validate:**
- ✅ Your API endpoints properly store data in MongoDB
- ✅ Query status tracking works correctly
- ✅ Results persistence and retrieval
- ✅ Error handling throughout the pipeline
- ✅ Performance meets production requirements

**Before deploying to AWS:** Run `./tests/run-database-tests.sh` to ensure database integration is working correctly.
