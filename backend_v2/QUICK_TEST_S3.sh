#!/bin/bash

echo "🧪 Quick S3 Test"
echo "================"
echo ""

# Kill and restart server
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2

source ../.venv_studio/bin/activate
python app.py > server.log 2>&1 &
sleep 8

# Test API call
curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Create a bar chart of top 3 programming languages", "user_session": "test"}' | \
  python -c "
import sys, json
d = json.load(sys.stdin)
storage = d.get('artifact', {}).get('storage', 'N/A')
print(f'Storage: {storage}')
if storage == 's3':
    print('✅ SUCCESS! Uploading to S3!')
    print(f'HTML: {d[\"artifact\"].get(\"s3_html_url\", \"N/A\")[:60]}...')
else:
    print('⚠️  Still local storage. Check AWS Console permissions.')
"

echo ""
echo "Check logs: tail -50 server.log | grep S3"
