#!/bin/bash

# Web Research Agent - Test Runner Script
echo "🧪 Web Research Agent Test Suite"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if servers are running
check_servers() {
    print_status "Checking if servers are running..."
    
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend server is running on http://localhost:8000"
    else
        print_error "Backend server is not running on http://localhost:8000"
        print_status "Please start the backend server first:"
        print_status "  ./start_backend.sh"
        exit 1
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend server is running on http://localhost:3000"
    else
        print_error "Frontend server is not running on http://localhost:3000"
        print_status "Please start the frontend server first:"
        print_status "  ./start_frontend.sh"
        exit 1
    fi
}

# Function to run specific test suite
run_tests() {
    local test_type=$1
    local test_name=$2
    
    print_status "Running $test_name tests..."
    
    case $test_type in
        "all")
            npx playwright test
            ;;
        "ui")
            npx playwright test tests/research-agent.spec.ts
            ;;
        "api")
            npx playwright test tests/api-integration.spec.ts
            ;;
        "headed")
            npx playwright test --headed
            ;;
        "ui-mode")
            npx playwright test --ui
            ;;
        "debug")
            npx playwright test --debug
            ;;
        *)
            print_error "Unknown test type: $test_type"
            show_help
            exit 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        print_success "$test_name tests completed successfully!"
    else
        print_error "$test_name tests failed!"
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  all         Run all tests (default)"
    echo "  ui          Run UI tests only"
    echo "  api         Run API integration tests only"
    echo "  headed      Run tests in headed mode (visible browser)"
    echo "  ui-mode     Run tests with Playwright UI mode"
    echo "  debug       Run tests in debug mode"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0          # Run all tests"
    echo "  $0 ui       # Run UI tests only"
    echo "  $0 api      # Run API tests only"
    echo "  $0 headed   # Run tests with visible browser"
    echo "  $0 ui-mode  # Run tests with Playwright UI"
}

# Function to show test report
show_report() {
    print_status "Opening test report..."
    npx playwright show-report
}

# Main script logic
main() {
    local test_type=${1:-"all"}
    
    case $test_type in
        "help"|"-h"|"--help")
            show_help
            exit 0
            ;;
        "report")
            show_report
            exit 0
            ;;
        *)
            check_servers
            run_tests "$test_type" "$test_type"
            ;;
    esac
}

# Run main function with all arguments
main "$@"
