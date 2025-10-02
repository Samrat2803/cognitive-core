#!/bin/bash

echo "🧪 Testing S3 Access After Permission Grant"
echo "==========================================="
echo ""

# Kill existing server
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2

# Start server
cd "$(dirname "$0")"
source ../.venv_studio/bin/activate

echo "🚀 Starting server..."
python app.py > server.log 2>&1 &
SERVER_PID=$!

echo "⏳ Waiting for server to start..."
sleep 8

echo ""
echo "📊 Testing artifact creation with S3 upload..."
curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Create a bar chart comparing tech giants revenue in 2023", "user_session": "s3_permission_test"}' \
  | python -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f\"✅ Request successful!\")
    print(f\"   Session: {d['session_id']}\")
    print(f\"   Artifact: {d.get('artifact', {}).get('artifact_id', 'None')}\")
    print(f\"   Storage: {d.get('artifact', {}).get('storage', 'N/A')}\")
    
    if d.get('artifact', {}).get('storage') == 's3':
        print(\"\n🎉 SUCCESS! Artifact uploaded to S3\")
        print(f\"   S3 HTML URL: {d['artifact'].get('s3_html_url', 'N/A')[:80]}...\")
        print(f\"   S3 PNG URL: {d['artifact'].get('s3_png_url', 'N/A')[:80]}...\")
    else:
        print(\"\n⚠️  Still using local storage - check IAM permissions\")
except Exception as e:
    print(f\"❌ Error: {e}\")
"

echo ""
echo "📋 Check server logs for S3 upload details:"
echo "   tail -50 server.log | grep -E 'S3|upload|storage'"
echo ""
echo "🛑 To stop server: kill $SERVER_PID"

