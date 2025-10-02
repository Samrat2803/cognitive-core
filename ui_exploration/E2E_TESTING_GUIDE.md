# End-to-End Testing Guide - Political Analyst Workbench

This guide explains the E2E testing strategy for the Political Analyst Workbench using Playwright.

---

## 📋 Overview

We use **Playwright** for end-to-end testing that verifies:
- ✅ Frontend UI components
- ✅ Backend API integration
- ✅ WebSocket real-time communication
- ✅ Complete user journeys

### Test Philosophy
- **Incremental**: Tests grow with each feature we build
- **User-centric**: Tests follow actual user workflows
- **Comprehensive**: Tests both frontend and backend integration

---

## 🚀 Running Tests

### Prerequisites
1. **Backend must be running** on `http://localhost:8000`
2. **Frontend dev server** will auto-start (configured in playwright.config.ts)

### Commands

```bash
# Run all tests (headless)
npm run test:e2e

# Run with UI mode (interactive)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Debug mode (step through tests)
npm run test:e2e:debug

# Run specific test
npx playwright test -g "Feature 1"

# Run and show test report
npx playwright show-report
```

---

## 📁 Test Structure

```
e2e/
└── user-journey.spec.ts    # Main test file covering all features
```

### Current Tests (Features 1-4)

#### ✅ Feature 1: Project Setup + Basic UI Layout
- Verifies page loads with correct title
- Checks header, navigation buttons
- Validates split-pane layout (chat + artifacts panels)

#### ✅ Feature 2: WebSocket Connection
- Waits for connection status indicator
- Verifies "Connected" status appears (green indicator)
- Confirms WebSocket establishes successfully

#### ✅ Feature 3: Message Input + Send
- Tests textarea input functionality
- Verifies send button enables/disables correctly
- Tests sending messages via button and Enter key
- Tests suggestion card click functionality
- Verifies "thinking" indicator appears

#### ✅ Feature 4: Display Streaming Response
- Sends query and waits for AI response
- Verifies assistant message appears
- Checks markdown rendering (headers, lists, etc.)
- Validates thinking indicator disappears on completion

#### ✅ Complete User Journey
- End-to-end test covering all steps:
  1. Land on page
  2. WebSocket connects
  3. See welcome message
  4. Click suggestion
  5. User message appears
  6. Thinking indicator shows
  7. AI response streams in
  8. Response contains markdown
  9. Completion state

#### ✅ Backend Health Check
- Tests `/health` endpoint
- Verifies backend is ready

---

## 📝 Test Patterns

### Waiting for Connection
```typescript
await expect(page.locator('.connection-status'))
  .toContainText('Connected', { timeout: 10000 });
```

### Sending a Message
```typescript
await page.locator('textarea.message-textarea').fill('Test query');
await page.locator('button.send-button.send').click();
```

### Waiting for AI Response
```typescript
const assistantMessage = page.locator('.assistant-message').first();
await expect(assistantMessage).toBeVisible({ timeout: 30000 }); // 30s for AI
```

### Checking Markdown Rendering
```typescript
const markdownContent = assistantMessage.locator('.markdown-content');
await expect(markdownContent).toBeVisible();
```

---

## 🔮 Future Tests (Features 5-10)

### Feature 5: Status Updates + Progress
```typescript
test('Should display status updates and progress bar', async ({ page }) => {
  // Send query
  // Verify status messages: "Searching web...", "Analyzing data..."
  // Verify progress bar updates: 0% → 100%
  // Check smooth animations
});
```

### Feature 6: Citations Display
```typescript
test('Should display citations', async ({ page }) => {
  // Send query with citations enabled
  // Verify citation cards appear
  // Check citation links are clickable
  // Verify citation count matches response
});
```

### Feature 7: Artifact Display
```typescript
test('Should display artifacts (charts)', async ({ page }) => {
  // Send query that generates chart
  // Verify artifact appears in right panel
  // Check artifact is interactive (if applicable)
  // Verify artifact metadata
});
```

### Feature 8: Artifact Actions
```typescript
test('Should allow artifact downloads', async ({ page }) => {
  // Generate artifact
  // Click "Download PNG" button
  // Verify file download
  // Test HTML download
  // Test share functionality
});
```

### Feature 9: Conversation History
```typescript
test('Should display conversation history', async ({ page }) => {
  // Send multiple messages
  // Open history panel
  // Verify all conversations listed
  // Test loading previous conversation
  // Test delete functionality
});
```

### Feature 10: Error Handling
```typescript
test('Should handle errors gracefully', async ({ page }) => {
  // Stop backend
  // Send message
  // Verify friendly error message
  // Check reconnect functionality
});
```

---

## 🎯 Adding Tests for New Features

When implementing a new feature:

1. **Write the feature code** (frontend + backend)
2. **Update `user-journey.spec.ts`**:
   ```typescript
   test('Feature X: Description', async ({ page }) => {
     // Test steps
   });
   ```
3. **Run tests** to verify
4. **Update this guide** with new test patterns

### Template for New Test
```typescript
test('Feature X: Should do something', async ({ page }) => {
  // Step 1: Setup (wait for connection, navigate, etc.)
  await expect(page.locator('.connection-status'))
    .toContainText('Connected', { timeout: 10000 });
  
  // Step 2: User action
  await page.locator('.some-button').click();
  
  // Step 3: Verify result
  await expect(page.locator('.expected-result')).toBeVisible();
  
  console.log('✅ Feature X: Test passed');
});
```

---

## 🐛 Debugging

### Common Issues

**1. Backend not running**
```
Error: connect ECONNREFUSED 127.0.0.1:8000
```
**Solution**: Start backend first
```bash
cd Political_Analyst_Workbench/backend_server
source ../../.venv/bin/activate
python app.py
```

**2. WebSocket timeout**
```
TimeoutError: page.locator('.connection-status')
```
**Solution**: 
- Check backend WebSocket endpoint is running
- Check CORS settings allow frontend origin
- Increase timeout if network is slow

**3. AI response timeout**
```
TimeoutError: Waiting for assistant message (30000ms)
```
**Solution**:
- Check Tavily API key is valid
- Check OpenAI API key is valid
- Increase `WEBSOCKET_TIMEOUT` in test file

### Debug Tips

1. **Run in headed mode** to see browser
   ```bash
   npm run test:e2e:headed
   ```

2. **Use debug mode** to step through
   ```bash
   npm run test:e2e:debug
   ```

3. **Check screenshots** in `test-results/` folder after failures

4. **Use console.log** statements in tests
   ```typescript
   console.log('✅ Step completed');
   ```

5. **Inspect HTML** during test
   ```typescript
   await page.pause(); // Pauses test for manual inspection
   ```

---

## 📊 Test Reports

After running tests, view the HTML report:
```bash
npx playwright show-report
```

The report shows:
- ✅ Passed tests (green)
- ❌ Failed tests (red)
- ⏱️ Test duration
- 📸 Screenshots on failure
- 🎥 Videos on failure
- 📋 Detailed logs

---

## 🎯 CI/CD Integration (Future)

When ready for CI/CD, update `.github/workflows/test.yml`:

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          npm ci
          pip install -r requirements.txt
      
      - name: Start backend
        run: |
          cd Political_Analyst_Workbench/backend_server
          python app.py &
          sleep 10
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

---

## 📚 Resources

- [Playwright Documentation](https://playwright.dev)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [API Reference](https://playwright.dev/docs/api/class-playwright)
- [Selectors Guide](https://playwright.dev/docs/selectors)

---

## ✅ Current Status

**Tests Implemented:** 8/10 feature areas

- ✅ Feature 1: UI Layout (3 tests)
- ✅ Feature 2: WebSocket Connection (1 test)
- ✅ Feature 3: Message Input (3 tests)
- ✅ Feature 4: Streaming Response (2 tests)
- ⏳ Feature 5: Status & Progress (pending)
- ⏳ Feature 6: Citations (pending)
- ⏳ Feature 7: Artifacts (pending)
- ⏳ Feature 8: Artifact Actions (pending)
- ⏳ Feature 9: History (pending)
- ⏳ Feature 10: Error Handling (pending)
- ✅ Complete User Journey (1 test)
- ✅ Backend Health (1 test)

**Total Tests:** 11 tests (growing with each feature!)

