#!/bin/bash

# Single Test Runner - One test, one query, end-to-end
echo "🧪 Single End-to-End Test Runner"
echo "================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Kill existing processes
print_status "Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start backend
print_status "Starting backend server..."
cd backend
source .venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Start frontend  
print_status "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait for servers
print_status "Waiting 15 seconds for servers to start..."
sleep 15

# Quick health check
print_status "Checking servers..."
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    print_success "Backend is running"
else
    print_error "Backend not responding - check API keys in backend/.env"
fi

if curl -s http://localhost:3000 >/dev/null 2>&1; then
    print_success "Frontend is running"
else
    print_error "Frontend not responding"
fi

# Run the single test
print_status "Running single end-to-end test..."
echo "This will open a browser window - watch it perform the test!"
echo ""

npx playwright test tests/single-test.spec.ts --config=config/playwright-sequential.config.ts --project=chromium

TEST_RESULT=$?

# Clean up
print_status "Cleaning up..."
kill $BACKEND_PID 2>/dev/null || true
kill $FRONTEND_PID 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

if [ $TEST_RESULT -eq 0 ]; then
    print_success "🎉 Test passed! End-to-end functionality is working!"
else
    print_error "❌ Test failed. Check the logs above and test-failure.png if created."
fi

exit $TEST_RESULT
