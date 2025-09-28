#!/bin/bash

# Database Test Runner Script for Team B
# Tests all database integration and performance aspects

set -e

echo "🗄️  Database Test Suite Runner"
echo "=============================="
echo

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

# Check if we're in the right directory
if [ ! -d "tests" ] || [ ! -d "database" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if backend is running
print_status "Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "Backend is running"
else
    print_warning "Backend is not running. Some tests may fail."
    echo "  To start backend: cd backend && python app.py"
fi

# Check if frontend is running
print_status "Checking if frontend is running..."
if curl -s http://localhost:3000 > /dev/null; then
    print_success "Frontend is running"
else
    print_warning "Frontend is not running. End-to-end tests may fail."
    echo "  To start frontend: cd frontend && npm start"
fi

echo

# Parse command line arguments
TEST_TYPE="all"
HEADED="false"
UI_MODE="false"
DEBUG="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --database-only|db)
            TEST_TYPE="database"
            shift
            ;;
        --integration-only|integration)
            TEST_TYPE="integration"
            shift
            ;;
        --performance-only|performance|perf)
            TEST_TYPE="performance"
            shift
            ;;
        --e2e-only|e2e)
            TEST_TYPE="e2e"
            shift
            ;;
        --headed)
            HEADED="true"
            shift
            ;;
        --ui)
            UI_MODE="true"
            shift
            ;;
        --debug)
            DEBUG="true"
            shift
            ;;
        --help|-h)
            echo "Database Test Runner"
            echo
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "Options:"
            echo "  --database-only, db     Run only database unit tests"
            echo "  --integration-only      Run only database integration tests"
            echo "  --performance-only      Run only performance tests"
            echo "  --e2e-only             Run only end-to-end tests"
            echo "  --headed               Run Playwright tests with visible browser"
            echo "  --ui                   Run Playwright tests in UI mode"
            echo "  --debug                Run tests in debug mode"
            echo "  --help, -h             Show this help message"
            echo
            echo "Examples:"
            echo "  $0                     Run all database tests"
            echo "  $0 db                  Run only database unit tests"
            echo "  $0 performance         Run only performance tests"
            echo "  $0 --headed            Run all tests with visible browser"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Prepare Playwright arguments
PLAYWRIGHT_ARGS=""
if [ "$HEADED" = "true" ]; then
    PLAYWRIGHT_ARGS="$PLAYWRIGHT_ARGS --headed"
fi
if [ "$UI_MODE" = "true" ]; then
    PLAYWRIGHT_ARGS="$PLAYWRIGHT_ARGS --ui"
fi
if [ "$DEBUG" = "true" ]; then
    PLAYWRIGHT_ARGS="$PLAYWRIGHT_ARGS --debug"
fi

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=""

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    print_status "Running $test_name..."
    
    if eval "$test_command"; then
        print_success "$test_name passed"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        print_error "$test_name failed"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        FAILED_TESTS="$FAILED_TESTS\n  - $test_name"
    fi
    echo
}

# Run Database Unit Tests
if [ "$TEST_TYPE" = "all" ] || [ "$TEST_TYPE" = "database" ]; then
    print_status "🧪 Running Database Unit Tests"
    echo "----------------------------------------"
    
    # Check if database dependencies are installed
    if ! python3 -c "import motor, pymongo, pydantic" 2>/dev/null; then
        print_error "Database dependencies not installed"
        echo "Please install: uv pip install motor pymongo pydantic python-dotenv"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    else
        # Run database connection test
        run_test "Database Connection Test" "cd database && python test_connection.py"
        
        # Run database unit tests
        if [ -f "database/tests/test_mongo_service.py" ]; then
            run_test "Database Unit Tests" "cd database && python -m pytest tests/ -v"
        fi
    fi
fi

# Run Database Integration Tests (Playwright)
if [ "$TEST_TYPE" = "all" ] || [ "$TEST_TYPE" = "integration" ]; then
    print_status "🔗 Running Database Integration Tests"
    echo "----------------------------------------"
    
    run_test "Database Integration Tests" "npx playwright test tests/database-integration.spec.ts $PLAYWRIGHT_ARGS"
    run_test "Data Logging Verification Tests" "npx playwright test tests/data-logging-verification.spec.ts $PLAYWRIGHT_ARGS"
fi

# Run End-to-End Database Tests
if [ "$TEST_TYPE" = "all" ] || [ "$TEST_TYPE" = "e2e" ]; then
    print_status "🌐 Running End-to-End Database Tests"
    echo "----------------------------------------"
    
    run_test "End-to-End Database Pipeline Tests" "npx playwright test tests/end-to-end-database.spec.ts $PLAYWRIGHT_ARGS"
fi

# Run Performance Tests
if [ "$TEST_TYPE" = "all" ] || [ "$TEST_TYPE" = "performance" ]; then
    print_status "⚡ Running Database Performance Tests"
    echo "----------------------------------------"
    
    run_test "Database Performance Tests" "python3 tests/database-performance.py"
fi

# Summary
echo "=============================="
print_status "Test Summary"
echo "=============================="
echo

if [ $TESTS_FAILED -eq 0 ]; then
    print_success "All tests passed! ($TESTS_PASSED/$((TESTS_PASSED + TESTS_FAILED)))"
    echo "✅ Database implementation is ready for production!"
else
    print_error "Some tests failed ($TESTS_FAILED/$((TESTS_PASSED + TESTS_FAILED)))"
    echo -e "Failed tests:$FAILED_TESTS"
    echo
    echo "❌ Please fix the failing tests before proceeding"
fi

echo
print_status "Database Testing Complete"

exit $TESTS_FAILED
