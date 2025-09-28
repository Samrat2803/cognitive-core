# Development Guide

This guide covers local development setup, debugging, and development best practices for the Web Research Agent.

## 🚀 **Quick Start**

### **Prerequisites**
- **Python 3.9+** with pip
- **Node.js 16+** with npm
- **Git** for version control
- **MongoDB Atlas** account (free tier)
- **API Keys:** Tavily, OpenAI

### **Environment Setup**
```bash
# Clone the repository
git clone https://github.com/your-repo/web-research-agent.git
cd web-research-agent

# Set up backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Create environment file
cp env.example .env
# Edit .env with your API keys (see API Keys section below)

# Set up frontend
cd ../frontend
npm install

# Install development tools (optional but recommended)
cd ..
npm install -g @playwright/test  # For E2E testing
```

## 🔑 **API Keys Configuration**

### **Required API Keys**
Create `backend/.env` file with:
```bash
# Required for core functionality
TAVILY_API_KEY=your_tavily_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Required for database
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/

# Optional development settings
FLASK_ENV=development
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=DEBUG
```

### **Getting API Keys**

#### **Tavily API Key**
1. Go to https://tavily.com
2. Sign up for an account
3. Navigate to API Keys section
4. Copy your API key

#### **OpenAI API Key**
1. Go to https://platform.openai.com
2. Sign up or log in
3. Go to API Keys section
4. Create new API key
5. Copy the key (save it immediately - you can't see it again)

#### **MongoDB Connection String**
1. Go to https://cloud.mongodb.com
2. Create free cluster
3. Set up database user and network access
4. Get connection string from Connect → Connect your application

## 🏗 **Development Workflow**

### **Starting the Development Environment**
```bash
# Terminal 1 - Backend
cd backend
source .venv/bin/activate
python app.py
# Backend will run on http://localhost:8000

# Terminal 2 - Frontend  
cd frontend
npm start
# Frontend will run on http://localhost:3000

# Terminal 3 - Optional: MongoDB local instance
# Only if you prefer local MongoDB over Atlas
mongod --dbpath ./data/db
```

### **Development URLs**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (FastAPI auto-docs)
- **Health Check:** http://localhost:8000/health

## 🧪 **Testing**

### **Backend Testing**
```bash
cd backend

# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_research_agent.py

# Run with verbose output
python -m pytest -v -s

# Run only integration tests
python -m pytest -m integration
```

### **Frontend Testing**
```bash
cd frontend

# Run unit tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage --watchAll=false

# Update snapshots
npm test -- --updateSnapshot
```

### **End-to-End Testing**
```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run E2E tests
npx playwright test

# Run tests in headed mode (see browser)
npx playwright test --headed

# Run specific test file
npx playwright test tests/research-flow.spec.ts

# Generate test report
npx playwright show-report
```

## 🔧 **Debugging**

### **Backend Debugging**

#### **Using Python Debugger**
```python
# Add breakpoint in your code
import pdb; pdb.set_trace()

# Or use modern breakpoint() function (Python 3.7+)
breakpoint()
```

#### **Logging Configuration**
```python
# backend/config.py
import logging

# Development logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# In your code
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

#### **FastAPI Debug Mode**
```python
# backend/app.py
from fastapi import FastAPI

app = FastAPI(debug=True)  # Enable debug mode

# Or run with reload
# uvicorn app:app --reload --log-level debug
```

### **Frontend Debugging**

#### **Browser DevTools**
```javascript
// Add console logs
console.log('Debug info:', data);
console.error('Error occurred:', error);

// Use browser debugger
debugger;

// React DevTools
// Install React DevTools browser extension
// Inspect component state and props
```

#### **Network Debugging**
```javascript
// Check API calls in browser Network tab
// Monitor request/response headers and data
// Use fetch directly in browser console to test endpoints

fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log);
```

### **Common Issues and Solutions**

#### **Backend Issues**
```bash
# Issue: Module not found
# Solution: Ensure virtual environment is activated and dependencies installed
source .venv/bin/activate
uv pip install -r requirements.txt

# Issue: API key errors
# Solution: Check .env file exists and has correct keys
ls -la .env
cat .env  # (be careful not to expose keys publicly)

# Issue: Database connection fails
# Solution: Check MongoDB connection string and network access
# Test connection with MongoDB Compass or mongo shell

# Issue: Port already in use
# Solution: Kill process or use different port
lsof -ti:8000 | xargs kill -9
# Or change port in app.py
```

#### **Frontend Issues**
```bash
# Issue: npm install fails
# Solution: Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Issue: CORS errors
# Solution: Check backend CORS configuration
# Ensure CORS_ORIGINS includes http://localhost:3000

# Issue: API calls fail
# Solution: Check backend is running and URLs match
curl http://localhost:8000/health
```

## 📦 **Project Structure**

### **Backend Structure**
```
backend/
├── app.py                 # FastAPI application entry point
├── research_agent.py      # Multi-agent research system
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── .env.example         # Environment template
├── tests/               # Test files
│   ├── test_agents.py
│   ├── test_api.py
│   └── conftest.py
├── database/            # Database integration (Team B)
│   ├── models/
│   ├── services/
│   └── migrations/
└── utils/               # Utility functions
    ├── logging.py
    └── helpers.py
```

### **Frontend Structure**
```
frontend/
├── public/              # Static files
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/      # React components
│   │   ├── Header.tsx
│   │   ├── ResearchForm.tsx
│   │   ├── ResearchResults.tsx
│   │   ├── QueryHistory.tsx
│   │   └── ExportButton.tsx
│   ├── hooks/           # Custom React hooks
│   │   └── useResearchQuery.ts
│   ├── types.ts         # TypeScript type definitions
│   ├── App.tsx         # Main application component
│   ├── index.tsx       # Application entry point
│   └── config.ts       # Configuration settings
├── package.json        # Dependencies and scripts
└── tsconfig.json       # TypeScript configuration
```

## 🔄 **Development Best Practices**

### **Code Quality**
```bash
# Backend code formatting
cd backend
black .                  # Format Python code
flake8 .                # Lint Python code
mypy .                  # Type checking

# Frontend code formatting  
cd frontend
npm run lint            # ESLint
npm run format          # Prettier
npm run type-check      # TypeScript checking
```

### **Git Workflow**
```bash
# Create feature branch
git checkout -b feature/new-agent-capability

# Make changes and commit
git add .
git commit -m "feat(agents): add query caching functionality"

# Push and create pull request
git push origin feature/new-agent-capability
# Then create PR on GitHub
```

### **Environment Management**
```bash
# Backend dependencies
cd backend
uv pip freeze > requirements.txt  # Update requirements

# Frontend dependencies
cd frontend
npm audit                         # Check for vulnerabilities
npm update                        # Update dependencies
```

## 🐛 **Common Development Scenarios**

### **Adding a New Agent**
```python
# 1. Create agent class in research_agent.py
class NewAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def process(self, state):
        # Agent logic here
        return {"new_data": "processed"}

# 2. Add to LangGraph workflow
builder.add_node("new_agent", new_agent_instance)
builder.add_edge("previous_agent", "new_agent")
builder.add_edge("new_agent", "next_agent")

# 3. Update state schema
class ResearchState(TypedDict):
    # ... existing fields
    new_data: str  # Add new field

# 4. Add tests
def test_new_agent():
    agent = NewAgent(mock_llm)
    result = agent.process(test_state)
    assert result["new_data"] == "expected"
```

### **Adding a New API Endpoint**
```python
# 1. Add endpoint to app.py
@app.post("/new-endpoint")
async def new_endpoint(request: NewRequest):
    # Endpoint logic
    return {"result": "success"}

# 2. Define request/response models
class NewRequest(BaseModel):
    field: str

class NewResponse(BaseModel):
    result: str

# 3. Add tests
def test_new_endpoint():
    response = client.post("/new-endpoint", json={"field": "value"})
    assert response.status_code == 200
```

### **Adding a New Frontend Component**
```typescript
// 1. Create component file
// src/components/NewComponent.tsx
import React from 'react';

interface NewComponentProps {
  data: string;
  onAction: () => void;
}

export const NewComponent: React.FC<NewComponentProps> = ({ data, onAction }) => {
  return (
    <div>
      <p>{data}</p>
      <button onClick={onAction}>Action</button>
    </div>
  );
};

// 2. Add to main component
// src/App.tsx
import { NewComponent } from './components/NewComponent';

// 3. Add tests
// src/components/NewComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { NewComponent } from './NewComponent';

test('renders and handles click', () => {
  const handleAction = jest.fn();
  render(<NewComponent data="test" onAction={handleAction} />);
  
  fireEvent.click(screen.getByText('Action'));
  expect(handleAction).toHaveBeenCalled();
});
```

## 📊 **Performance Monitoring**

### **Backend Monitoring**
```python
# Add timing decorators
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

@timing_decorator
def slow_function():
    # Function implementation
    pass
```

### **Database Query Optimization**
```python
# Add database query timing
import time
from database import mongo_service

async def timed_query():
    start = time.time()
    result = await mongo_service.find_queries()
    duration = time.time() - start
    logger.info(f"Query took {duration:.2f} seconds")
    return result
```

### **Frontend Performance**
```typescript
// Use React DevTools Profiler
// Monitor bundle size with webpack-bundle-analyzer
npm install --save-dev webpack-bundle-analyzer

// Add to package.json scripts
"analyze": "npm run build && npx webpack-bundle-analyzer build/static/js/*.js"

// Run analysis
npm run analyze
```

## 🚀 **Production Preparation**

### **Environment Variables**
```bash
# Development (.env)
FLASK_ENV=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000

# Production (.env.production)
FLASK_ENV=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-frontend-domain.com
```

### **Build Optimization**
```bash
# Backend: Install production dependencies only
uv pip install --no-dev

# Frontend: Build for production
npm run build
npm run build:analyze  # Check bundle size
```

---

This development guide provides everything needed for productive local development of the Web Research Agent multi-agent system. For deployment instructions, see the [Deployment Guide](./deployment-guide.md).
