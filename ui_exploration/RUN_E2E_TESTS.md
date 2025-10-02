# Running E2E Tests - Quick Start

## 🚀 Prerequisites

**Both servers MUST be running before tests:**

### 1. Start Backend (Terminal 1)
```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2
source .venv/bin/activate
cd Political_Analyst_Workbench/backend_server
python app.py
```

**Wait for:** `✅ S3 service initialized` and `INFO: Uvicorn running on http://0.0.0.0:8000`

### 2. Start Frontend (Terminal 2)
```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2/ui_exploration/political-analyst-ui
npm run dev
```

**Wait for:** `➜  Local:   http://localhost:5174/`

### 3. Verify Both Are Running (Terminal 3)
```bash
# Check backend
curl http://localhost:8000/health

# Check frontend  
curl http://localhost:5174
```

Both should respond successfully.

---

## 🧪 Run Tests (Terminal 3)

```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2/ui_exploration/political-analyst-ui

# Run all tests
npm run test:e2e

# Run with UI (interactive)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Run specific feature
npx playwright test --grep="Feature 1"
```

---

## ✅ Expected Results

**11 Tests Should Pass:**

1. ✅ Feature 1: UI Layout with header and panels
2. ✅ Feature 2: WebSocket connection
3. ✅ Feature 3: Send message via textarea
4. ✅ Feature 3: Send message via suggestion card  
5. ✅ Feature 3: Thinking indicator
6. ✅ Feature 4: Receive streaming response
7. ✅ Feature 4: Markdown rendering
8. ✅ Complete User Journey (E2E)
9. ✅ Backend health check

**6 Tests Skipped** (Features 5-10 not yet implemented)

---

## 📊 View Results

```bash
# Open HTML report
npx playwright show-report
```

Shows:
- Pass/fail status
- Screenshots on failure
- Videos of test runs
- Detailed logs

---

## 🐛 Troubleshooting

**Test fails immediately:**
- Check both servers are running
- Verify http://localhost:5174 loads in browser
- Verify http://localhost:8000/health returns `{"status": "healthy"}`

**WebSocket connection fails:**
- Check backend logs for errors
- Verify CORS settings allow localhost:5174
- Check `.env` file has valid API keys

**AI response times out:**
- Check Tavily API key is valid
- Check OpenAI API key is valid
- Increase `WEBSOCKET_TIMEOUT` in test file (currently 30s)

---

## 📝 Adding New Tests

When you implement Feature 5-10, uncomment the corresponding test in `e2e/user-journey.spec.ts`:

```typescript
// Change from:
test.skip('Feature 5: Should display status updates', ...)

// To:
test('Feature 5: Should display status updates', ...)
```

Then run tests to verify!

