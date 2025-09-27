#!/bin/bash

# Web Research Agent - Restart and Test Script
echo "🔄 Restarting servers and running tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local service_name=$2
    
    print_status "Killing processes on port $port ($service_name)..."
    
    # Find and kill processes on the port
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -9 2>/dev/null
        print_success "Killed processes on port $port"
    else
        print_status "No processes found on port $port"
    fi
}

# Function to wait for port to be free
wait_for_port_free() {
    local port=$1
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if ! lsof -ti:$port >/dev/null 2>&1; then
            print_success "Port $port is now free"
            return 0
        fi
        
        print_status "Waiting for port $port to be free... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Port $port is still in use after $max_attempts attempts"
    return 1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready at $url"
            return 0
        fi
        
        print_status "Waiting for $service_name to be ready... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name is not ready after $max_attempts attempts"
    return 1
}

# Main execution
main() {
    print_status "Starting restart and test process..."
    
    # Kill existing processes
    kill_port 8000 "Backend"
    kill_port 3000 "Frontend"
    
    # Wait for ports to be free
    wait_for_port_free 8000
    wait_for_port_free 3000
    
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
    
    # Wait for services to be ready
    wait_for_service "http://localhost:8000/health" "Backend"
    wait_for_service "http://localhost:3000" "Frontend"
    
    # Run tests with single worker to avoid multiple browsers
    print_status "Running Playwright tests..."
    npx playwright test --headed --project=chromium --workers=1 --config=config/playwright-headed.config.ts
    
    # Capture test result
    TEST_RESULT=$?
    
    # Clean up
    print_status "Cleaning up..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    
    # Kill any remaining processes on ports
    kill_port 8000 "Backend"
    kill_port 3000 "Frontend"
    
    if [ $TEST_RESULT -eq 0 ]; then
        print_success "Tests completed successfully!"
    else
        print_error "Tests failed!"
    fi
    
    exit $TEST_RESULT
}

# Run main function
main "$@"
