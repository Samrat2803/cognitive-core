#!/bin/bash

# Start backend with database integration on port 8001 for testing
# This version includes full MongoDB integration to test database writes

echo "🗄️  Starting Backend with Database Integration"
echo "============================================="
echo "Port: 8001 (for testing database writes)"
echo

# Check if we're in the backend directory
if [ ! -f "app_with_database.py" ]; then
    echo "❌ Please run this script from the backend/ directory"
    echo "   cd backend && ./start_database_backend.sh"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ .env file created from env.example"
        echo "🔧 Please edit .env file with your API keys before continuing"
        echo "   Required: TAVILY_API_KEY, OPENAI_API_KEY"
        echo "   MongoDB connection string is already configured"
        read -p "Press Enter after editing .env file..."
    else
        echo "❌ env.example file not found!"
        exit 1
    fi
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not detected"
    if [ -d ".venv" ]; then
        echo "🔄 Activating virtual environment..."
        source .venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ No .venv directory found"
        echo "   Please create virtual environment: python -m venv .venv"
        echo "   Then activate it: source .venv/bin/activate"
        exit 1
    fi
fi

# Check if database dependencies are installed
echo "🔍 Checking database dependencies..."
python -c "import motor, pymongo, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Database dependencies not installed"
    echo "📦 Installing database dependencies..."
    uv pip install motor pymongo pydantic python-dotenv
    echo "✅ Database dependencies installed"
fi

# Test database connection
echo "🗄️  Testing MongoDB connection..."
python -c "
import asyncio
import sys
import os
sys.path.append('../database')
try:
    from services.mongo_service import MongoService
    async def test():
        service = MongoService()
        await service.connect()
        print('✅ MongoDB connection successful')
        await service.disconnect()
    asyncio.run(test())
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
    print('🔧 Please check:')
    print('   - MONGODB_CONNECTION_STRING in .env file')
    print('   - MongoDB Atlas cluster is running')
    print('   - Network connectivity')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection test failed!"
    echo "🔧 Please fix database connection before continuing"
    exit 1
fi

echo "✅ Database connection verified"
echo

# Start the backend server
echo "🚀 Starting backend server with database integration..."
echo "🔗 URL: http://localhost:8001"
echo "🗄️  Database: MongoDB Atlas (integrated)"
echo "📊 API Docs: http://localhost:8001/docs"
echo
echo "Press Ctrl+C to stop the server"
echo

python app_with_database.py
