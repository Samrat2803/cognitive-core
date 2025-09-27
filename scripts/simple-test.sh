#!/bin/bash

# Simple Test Runner - Just try twice and show logs
echo "🧪 Simple Playwright Test Runner"
echo "================================"

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
print_status "Killing existing processes..."
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

# Wait a bit for servers to start
print_status "Waiting 10 seconds for servers to start..."
sleep 10

# Check if servers are running
print_status "Checking server status..."

# Check backend
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    print_success "Backend is running"
else
    print_error "Backend is not responding"
    echo "Backend logs:"
    ps aux | grep "python app.py" | grep -v grep
fi

# Check frontend
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    print_success "Frontend is running"
else
    print_error "Frontend is not responding"
    echo "Frontend logs:"
    ps aux | grep "react-scripts" | grep -v grep
fi

# Run just one simple test
print_status "Running basic UI test..."
npx playwright test tests/basic-ui.spec.ts --config=config/playwright-sequential.config.ts --project=chromium

# Clean up
print_status "Cleaning up..."
kill $BACKEND_PID 2>/dev/null || true
kill $FRONTEND_PID 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

print_status "Done!"
