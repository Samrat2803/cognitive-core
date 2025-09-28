# Team B: Database Testing Guide

**Comprehensive testing suite for MongoDB integration and data architecture**

## 🎯 **Team B Testing Responsibilities**

According to the comprehensive deployment plan, Team B is responsible for:
- ✅ **Data logging verification** *(Teams A,B)*
- ✅ **End-to-end Frontend ↔ Backend ↔ MongoDB integration** *(All Teams)*
- ✅ **Database performance validation**
- ✅ **Error handling in database operations**

---

## 📋 **Test Suite Overview**

### **1. Database Unit Tests** (`database/tests/`)
- MongoDB connection and basic operations
- CRUD functionality testing
- Data model validation
- Error handling scenarios

### **2. Database Integration Tests** (`database-integration.spec.ts`)
- Complete Frontend → Backend → MongoDB pipeline
- Query creation and status tracking
- Database error handling and resilience
- Analytics and metadata collection
- Performance with multiple operations
- Data consistency across operations

### **3. Data Logging Verification Tests** (`data-logging-verification.spec.ts`) 
- Query data properly logged and stored
- Error cases properly logged
- Session and user data logging
- Research metadata comprehensively logged
- Performance metrics logging
- Analytics data accumulation
- Concurrent logging integrity

### **4. End-to-End Database Tests** (`end-to-end-database.spec.ts`)
- Full research workflow with database persistence
- Multiple queries with database tracking
- Export functionality includes database data
- Error handling throughout complete pipeline
- Real-time updates and progress tracking
- Mobile responsiveness with database operations
- Analytics data collection end-to-end
- Complete user session tracking

### **5. Database Performance Tests** (`database-performance.py`)
- Individual operation performance
- Concurrent operations under load
- Query retrieval performance
- Analytics operations performance
- Stress testing conditions
- API performance with database integration

---

## 🚀 **Running the Tests**

### **Quick Start**
```bash
# Run all database tests
./tests/run-database-tests.sh

# Run specific test types
./tests/run-database-tests.sh db            # Database unit tests only
./tests/run-database-tests.sh integration   # Integration tests only  
./tests/run-database-tests.sh performance   # Performance tests only
./tests/run-database-tests.sh e2e          # End-to-end tests only
```

### **Prerequisites**
1. **MongoDB Connection**: Connection string configured in `backend/.env`
2. **Backend Running**: `cd backend && python app.py`
3. **Frontend Running**: `cd frontend && npm start`
4. **Dependencies Installed**: `uv pip install motor pymongo pydantic python-dotenv`

### **Individual Test Commands**

#### **Database Unit Tests**
```bash
# Basic connection test
cd database && python test_connection.py

# Comprehensive unit tests
cd database && python -m pytest tests/ -v

# Manual verification
cd database && python tests/test_mongo_service.py
```

#### **Integration Tests (Playwright)**
```bash
# Database integration
npx playwright test tests/database-integration.spec.ts

# Data logging verification
npx playwright test tests/data-logging-verification.spec.ts

# End-to-end database pipeline
npx playwright test tests/end-to-end-database.spec.ts

# With visible browser
npx playwright test tests/database-integration.spec.ts --headed

# With UI mode for debugging
npx playwright test tests/data-logging-verification.spec.ts --ui
```

#### **Performance Tests**
```bash
# Full performance suite
python3 tests/database-performance.py

# API performance only
curl -X POST http://localhost:8000/research -H "Content-Type: application/json" -d '{"query":"performance test"}'
```

---

## 🔍 **Test Coverage**

### **✅ Functional Testing**
- [x] Query creation and retrieval
- [x] Results storage and retrieval  
- [x] Status tracking and updates
- [x] User session management
- [x] Analytics data collection
- [x] Error handling and validation

### **✅ Integration Testing**
- [x] Frontend → Backend → Database pipeline
- [x] API → Database persistence
- [x] Real-time status updates
- [x] Export functionality data layer
- [x] Multi-user session handling

### **✅ Performance Testing**
- [x] Individual operation benchmarks
- [x] Concurrent operation handling
- [x] Load testing with multiple users
- [x] Database query optimization
- [x] Memory and connection management

### **✅ Data Integrity Testing**
- [x] Data validation on input
- [x] Consistent data storage
- [x] Proper error logging
- [x] Transaction handling
- [x] Data consistency across operations

---

## 📊 **Test Results Interpretation**

### **Expected Performance Benchmarks**
- **Query Creation**: < 100ms average
- **Results Saving**: < 200ms average  
- **Query Retrieval**: < 50ms average
- **Analytics Generation**: < 500ms average
- **Concurrent Operations**: > 5 ops/sec throughput

### **Success Criteria**
- ✅ All database operations complete successfully
- ✅ Data is properly persisted and retrievable
- ✅ Error handling works gracefully
- ✅ Performance meets benchmarks
- ✅ Concurrent operations don't interfere
- ✅ Analytics data accumulates correctly

### **Common Issues and Solutions**

#### **Connection Errors**
```
❌ MongoDB connection failed
✅ Check MONGODB_CONNECTION_STRING in backend/.env
✅ Verify MongoDB Atlas cluster is running
✅ Check network connectivity
```

#### **Performance Issues**
```
❌ Operations taking too long
✅ Check database indexes are created
✅ Verify connection pooling is working
✅ Monitor MongoDB Atlas performance metrics
```

#### **Data Inconsistency**
```
❌ Data not persisting correctly
✅ Check error logs for validation failures
✅ Verify all required fields are provided
✅ Test with smaller datasets first
```

---

## 🔧 **Debugging Tests**

### **Playwright Test Debugging**
```bash
# Run with visible browser to see UI interactions
npx playwright test tests/database-integration.spec.ts --headed

# Use UI mode for step-by-step debugging
npx playwright test tests/end-to-end-database.spec.ts --ui

# Debug mode with breakpoints
npx playwright test tests/data-logging-verification.spec.ts --debug
```

### **Database Test Debugging**
```bash
# Increase logging verbosity
cd database && python test_connection.py --verbose

# Test individual components
cd database && python -c "
from services.mongo_service import MongoService
import asyncio
async def test():
    service = MongoService()
    await service.connect()
    print('Connected successfully')
asyncio.run(test())
"
```

### **Performance Test Analysis**
```bash
# Run with detailed output
python3 tests/database-performance.py --verbose

# Test specific operations
python3 -c "
import asyncio
from database.services.mongo_service import MongoService
# ... test specific operations
"
```

---

## 📈 **Continuous Integration**

### **CI/CD Pipeline Integration**
```bash
# Install dependencies
uv pip install motor pymongo pydantic python-dotenv pytest

# Install Playwright
npx playwright install --with-deps

# Run tests
./tests/run-database-tests.sh --ci

# Generate reports
npx playwright show-report
```

### **Test Reports**
- **Playwright HTML Report**: `playwright-report/index.html`
- **Database Performance Logs**: Console output with timing metrics
- **Unit Test Results**: PyTest standard output
- **Coverage Reports**: Generated with `pytest --cov`

---

## 🎯 **Integration with Other Teams**

### **Team A (Backend) Integration**
- Database services ready for integration
- Connection string configured
- Error handling patterns established
- Performance benchmarks validated

### **Team C (Frontend) Integration**
- Query history API tested and ready
- Real-time status updates validated
- Export functionality data layer complete
- Mobile responsiveness with database operations

### **Team D (Documentation) Integration**
- Analytics data ready for demo insights
- Database schema fully documented
- Performance metrics available for reporting
- Complete test coverage for documentation

---

## ✅ **Completion Checklist**

### **Database Implementation**
- [x] MongoDB Atlas cluster operational
- [x] All CRUD operations implemented and tested
- [x] Analytics service functional
- [x] Error handling comprehensive
- [x] Performance optimized

### **Testing Coverage**
- [x] Unit tests for all database operations
- [x] Integration tests for full pipeline
- [x] Data logging verification complete
- [x] End-to-end workflow testing
- [x] Performance and load testing
- [x] Error scenarios covered

### **Team Integration**
- [x] Database service ready for Team A
- [x] API endpoints tested and documented
- [x] Frontend integration points validated
- [x] Analytics ready for Team D demo

**🎉 Team B Database testing is comprehensive and production-ready!**

---

*Team B Database Testing Guide - Complete Coverage for Production Deployment*
