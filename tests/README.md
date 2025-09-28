# Web Research Agent - Test Suite

This directory contains comprehensive Playwright tests for the Web Research Agent application.

## Test Files

### **Frontend & UI Tests**

#### `research-agent.spec.ts`
UI tests for the React frontend application:
- Page load and element visibility
- Form validation and submission
- Research workflow testing
- Loading states and error handling
- Responsive design testing
- Multiple query handling
- Styling and color palette validation

#### `basic-ui.spec.ts`
Basic UI functionality tests:
- Component rendering
- Navigation and interactions
- Responsive design validation

### **API Integration Tests**

#### `api-integration.spec.ts`
API integration tests for the FastAPI backend:
- Endpoint availability and responses
- Request/response validation
- Error handling
- CORS configuration
- Concurrent request handling
- Data structure validation

### **Database Tests (Team B)** ✨

#### `database-integration.spec.ts`
Complete database integration testing:
- Frontend → Backend → MongoDB pipeline
- Query creation and status tracking
- Database error handling and resilience
- Analytics and metadata collection
- Performance with multiple operations
- Data consistency across operations

#### `data-logging-verification.spec.ts`
Data logging and persistence verification:
- Query data properly logged and stored
- Error cases properly logged
- Session and user data logging
- Research metadata comprehensively logged
- Performance metrics logging
- Analytics data accumulation
- Concurrent logging integrity

#### `end-to-end-database.spec.ts`
End-to-end database workflow testing:
- Full research workflow with database persistence
- Multiple queries with database tracking
- Export functionality includes database data
- Error handling throughout complete pipeline
- Real-time updates and progress tracking
- Mobile responsiveness with database operations
- Analytics data collection end-to-end
- Complete user session tracking

#### `database-performance.py`
Database performance and load testing:
- Individual operation performance benchmarks
- Concurrent operations under load
- Query retrieval performance optimization
- Analytics operations performance
- Stress testing conditions
- API performance with database integration

### **Backend Tests**

#### `test-backend.py`
Simple backend connectivity and functionality tests:
- Server connectivity
- Health check endpoint
- Config endpoint
- Basic research endpoint
- CORS headers validation

## Running Tests

### Prerequisites
1. **Backend server must be running** on `http://localhost:8000`
2. **Frontend server must be running** on `http://localhost:3000`
3. **API keys must be configured** in `backend/.env`

### Quick Start
```bash
# Start both servers first
./start_backend.sh    # Terminal 1
./start_frontend.sh   # Terminal 2

# Then run tests
./run-tests.sh        # Run all tests
```

### Test Commands

#### Using the main test runner script:
```bash
./run-tests.sh all         # Run all tests
./run-tests.sh ui          # Run UI tests only
./run-tests.sh api         # Run API tests only
./run-tests.sh headed      # Run with visible browser
./run-tests.sh ui-mode     # Run with Playwright UI
./run-tests.sh debug       # Run in debug mode
./run-tests.sh report      # Show test report
```

#### Using the database test runner (Team B):
```bash
./run-database-tests.sh                # Run all database tests
./run-database-tests.sh db             # Database unit tests only
./run-database-tests.sh integration    # Database integration tests
./run-database-tests.sh performance    # Performance tests only
./run-database-tests.sh e2e           # End-to-end database tests
./run-database-tests.sh --headed      # Run with visible browser
./run-database-tests.sh --ui          # Run with Playwright UI mode
```

#### Using npm scripts:
```bash
npm test                   # Run all tests
npm run test:ui           # Run with Playwright UI
npm run test:headed       # Run with visible browser
npm run test:debug        # Run in debug mode
npm run test:api          # Run API tests only
npm run test:ui-only      # Run UI tests only
npm run test:report       # Show test report
```

#### Using Playwright directly:
```bash
npx playwright test                    # Run all tests
npx playwright test --ui              # Run with UI mode
npx playwright test --headed          # Run with visible browser
npx playwright test --debug           # Run in debug mode
npx playwright test tests/ui.spec.ts  # Run specific test file
```

## Test Configuration

The tests are configured in `playwright.config.ts`:
- **Base URL**: `http://localhost:3000` (frontend)
- **API URL**: `http://localhost:8000` (backend)
- **Browsers**: Chromium, Firefox, WebKit, Mobile Chrome, Mobile Safari
- **Auto-start servers**: Tests will automatically start servers if not running
- **Screenshots**: Taken on failure
- **Videos**: Recorded on failure
- **Traces**: Collected on retry

## Test Data

### Valid Test Queries
- "What are the latest developments in artificial intelligence?"
- "How is machine learning being used in healthcare?"
- "What are the current trends in renewable energy?"

### Invalid Test Cases
- Empty queries
- Queries exceeding 500 characters
- Network timeouts
- API errors

## Test Reports

After running tests, you can view detailed reports:
```bash
npx playwright show-report
```

Reports include:
- Test results and timing
- Screenshots of failures
- Video recordings
- Trace files for debugging
- HTML report with detailed information

## Debugging Tests

### Debug Mode
```bash
npx playwright test --debug
```
This opens the Playwright Inspector where you can:
- Step through tests
- Inspect elements
- View network requests
- Take screenshots

### UI Mode
```bash
npx playwright test --ui
```
This opens the Playwright UI where you can:
- Run individual tests
- View test results
- Debug specific test cases
- Generate code from interactions

### Headed Mode
```bash
npx playwright test --headed
```
This runs tests with visible browser windows so you can see what's happening.

## Troubleshooting

### Common Issues

1. **Servers not running**
   - Ensure both backend and frontend servers are started
   - Check that ports 3000 and 8000 are available

2. **API key errors**
   - Verify `.env` file exists in `backend/` directory
   - Check that API keys are valid and have sufficient credits

3. **Test timeouts**
   - Research queries can take 30-60 seconds
   - Increase timeout in test configuration if needed

4. **CORS errors**
   - Ensure backend CORS is configured for `http://localhost:3000`

### Environment Setup
```bash
# Install Playwright browsers
npx playwright install

# Install dependencies
npm install

# Set up environment
cp backend/env.example backend/.env
# Edit backend/.env with your API keys
```

## Continuous Integration

For CI/CD pipelines, use:
```bash
npx playwright install --with-deps
npx playwright test --reporter=github
```

This will install browser dependencies and use GitHub-compatible reporting.
