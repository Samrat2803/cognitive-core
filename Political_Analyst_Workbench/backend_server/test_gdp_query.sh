#!/bin/bash

echo "========================================"
echo "Testing India GDP Query via Backend API"
echo "========================================"
echo ""

curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create a trend chart of India'\''s GDP growth rate over the period 2020-2025"
  }' \
  -w "\n\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n"

