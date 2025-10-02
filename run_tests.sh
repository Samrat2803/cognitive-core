#!/bin/bash

# V2 App - Test Runner Script
# Purpose: Run all backend tests sequentially

echo ""
echo "=========================================="
echo "🧪 V2 App - Backend Test Suite"
echo "=========================================="
echo ""

# Check if backend server is running
echo "⏸️  Checking if backend server is running..."
curl -s http://localhost:8000/health > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Backend server is not running!"
    echo ""
    echo "Please start the backend server first:"
    echo "   cd backend_v2"
    echo "   source .venv/bin/activate"
    echo "   python app.py"
    echo ""
    exit 1
fi

echo "✅ Backend server is running"
echo ""

# Navigate to backend directory
cd backend_v2 || exit 1

# Activate virtual environment
source .venv/bin/activate

# Run tests
echo "=========================================="
echo "Running Test Suite 1: API Health"
echo "=========================================="
python tests/test_01_api_health.py
if [ $? -ne 0 ]; then
    echo "❌ Test Suite 1 Failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "Running Test Suite 2: Master Agent"
echo "=========================================="
python tests/test_02_master_agent.py
if [ $? -ne 0 ]; then
    echo "❌ Test Suite 2 Failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "Running Test Suite 3: Sub-Agents"
echo "=========================================="
python tests/test_03_sub_agents.py
if [ $? -ne 0 ]; then
    echo "❌ Test Suite 3 Failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ ALL BACKEND TESTS PASSED!"
echo "=========================================="
echo ""
echo "📊 Test Summary:"
echo "   ✅ API Health & Connectivity"
echo "   ✅ Master Agent Query Processing"
echo "   ✅ Sub-Agents Functionality"
echo ""
echo "📝 Next Steps:"
echo "   1. Review test output above"
echo "   2. Test frontend (see TESTING_PLAN_V2.md)"
echo "   3. Run performance tests if needed"
echo ""

