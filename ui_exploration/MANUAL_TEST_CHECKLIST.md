# Manual Test Checklist - Features 1-4

**Date:** 2025-10-01  
**Testing URL:** http://localhost:5174/

Since Playwright has some configuration issues, let's perform manual testing to verify Features 1-4 are working correctly.

---

## ✅ Pre-Test Setup

### 1. Verify Backend is Running
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status":"healthy","version":"1.0.0","agent_status":"ready"}`

### 2. Verify Frontend is Running
Open browser to: http://localhost:5174/

---

## 📋 Feature 1: Project Setup + Basic UI Layout

### Test Steps:
1. ✅ **Page loads successfully**
   - No errors in browser console (F12)
   - Page title visible

2. ✅ **Header is visible**
   - Logo/title: "Political Analyst Workbench" (lime green)
   - History button (icon)
   - Settings button (icon)

3. ✅ **Connection Status Indicator**
   - Visible in top-right of header
   - Shows connection state

4. ✅ **Split-pane Layout**
   - Left panel: Chat area
   - Right panel: Artifacts area
   - Resize handle between panels works (drag to resize)

### Expected Result:
✅ All UI elements visible and functional

---

## 📋 Feature 2: WebSocket Connection

### Test Steps:
1. ✅ **Connection Status Indicator**
   - Wait up to 10 seconds after page load
   - Status should show: 🟢 "Connected"
   - Text should be green/lime color

2. ✅ **Browser Console Check**
   - Open DevTools (F12) → Console tab
   - Should see: "✅ WebSocket connected" (or similar)
   - Should see: "📥 Received message: connected"
   - No WebSocket errors

### Expected Result:
✅ Green "Connected" indicator visible  
✅ No WebSocket errors in console

---

## 📋 Feature 3: Message Input + Send

### Test 3a: Send Message via Textarea
1. ✅ **Input Field Visible**
   - Textarea at bottom of chat panel
   - Placeholder text: "Ask about political events..."
   - Send button visible (paper plane icon)

2. ✅ **Type and Send**
   - Type: "What is the capital of France?"
   - Press Enter (or click Send button)

3. ✅ **User Message Appears**
   - Message appears immediately in chat
   - Shows "You" as sender
   - Shows timestamp
   - Message has lime green tint background

4. ✅ **Input Clears**
   - Textarea is empty after sending

### Test 3b: Send Message via Suggestion Card
1. ✅ **Welcome Message Visible** (if first load)
   - "Welcome to Political Analyst Workbench"
   - 3 suggestion cards visible

2. ✅ **Click Suggestion**
   - Click any suggestion card (e.g., "Middle East Politics")

3. ✅ **Message Sent Automatically**
   - User message appears in chat
   - Suggestion text becomes the message

### Test 3c: Thinking Indicator
1. ✅ **Send a message** (any message)

2. ✅ **Thinking Indicator Appears**
   - "Analyzing..." text visible
   - 3 animated dots (bouncing animation)
   - Appears while waiting for response

### Expected Results:
✅ Messages send successfully  
✅ User messages display correctly  
✅ Thinking indicator animates  
✅ Input clears after sending

---

## 📋 Feature 4: Display Streaming Response

### Test 4a: Receive Streaming Response
1. ✅ **Send a Query**
   - Type: "What is happening in France?"
   - Press Enter

2. ✅ **Assistant Response Streams In**
   - Wait up to 30 seconds
   - Response appears character-by-character (streaming)
   - "Political Analyst" as sender
   - Bot icon visible

3. ✅ **Thinking Indicator Disappears**
   - Once response starts, thinking dots disappear

4. ✅ **Response Completes**
   - Full response visible
   - No loading indicators

### Test 4b: Markdown Rendering
1. ✅ **Send Query that Generates Markdown**
   - Type: "Explain the US political system with examples"
   - Press Enter

2. ✅ **Wait for Response**
   - Response should stream in

3. ✅ **Check Markdown Elements:**
   - **Headers** (H1-H4): Lime green color, different sizes
   - **Bold text**: Heavier font weight
   - **Lists**: Bullet points or numbers with lime markers
   - **Paragraphs**: Proper spacing

4. ✅ **If Code Blocks Appear:**
   - Syntax highlighting (colors for different code elements)
   - Line numbers on left
   - Copy button in top-right
   - Dark background

5. ✅ **If Links Appear:**
   - Lime green color
   - Underline on hover
   - Click opens in new tab

### Expected Results:
✅ Response streams in smoothly  
✅ Markdown renders correctly  
✅ Headers, lists, code blocks styled properly  
✅ Links are clickable

---

## 📋 Complete User Journey (End-to-End)

### Full Flow Test:
1. ✅ **Load Page**
   - http://localhost:5174/
   - Wait for page to fully load

2. ✅ **WebSocket Connects**
   - See 🟢 "Connected" in header

3. ✅ **Welcome Message**
   - See welcome text and 3 suggestions

4. ✅ **Click Suggestion**
   - Click "Middle East Politics" (or any card)

5. ✅ **User Message Appears**
   - Immediately visible in chat

6. ✅ **Thinking Indicator**
   - "Analyzing..." with bouncing dots

7. ✅ **AI Response Streams**
   - Text appears gradually
   - Markdown renders

8. ✅ **Response Completes**
   - Full response visible
   - Thinking indicator gone

9. ✅ **Send Another Message**
   - Type new query in input
   - Verify it works again

### Expected Result:
✅ Entire flow works smoothly from start to finish

---

## 📋 Backend Health Check

### Test:
```bash
curl http://localhost:8000/health
```

### Expected Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agent_status": "ready",
  "timestamp": "2025-10-01T..."
}
```

✅ Status: healthy  
✅ Agent: ready

---

## 🐛 Common Issues

### Issue: "Disconnected" Status
**Solution:**
- Check backend is running: `curl http://localhost:8000/health`
- Check browser console for WebSocket errors
- Verify CORS settings allow localhost:5174

### Issue: No Response from AI
**Solution:**
- Check `.env` file has valid API keys:
  - `TAVILY_API_KEY=...`
  - `OPENAI_API_KEY=...`
- Check backend logs for errors
- Wait up to 30 seconds for response

### Issue: Markdown Not Rendering
**Solution:**
- Open browser DevTools → Console
- Check for React errors
- Verify `react-markdown` is installed: `npm list react-markdown`

---

## ✅ Test Results

**Date Tested:** _____________  
**Tester:** _____________

| Feature | Status | Notes |
|---------|--------|-------|
| Feature 1: UI Layout | ☐ Pass ☐ Fail | |
| Feature 2: WebSocket | ☐ Pass ☐ Fail | |
| Feature 3a: Send Message | ☐ Pass ☐ Fail | |
| Feature 3b: Suggestions | ☐ Pass ☐ Fail | |
| Feature 3c: Thinking | ☐ Pass ☐ Fail | |
| Feature 4a: Streaming | ☐ Pass ☐ Fail | |
| Feature 4b: Markdown | ☐ Pass ☐ Fail | |
| Complete Journey | ☐ Pass ☐ Fail | |
| Backend Health | ☐ Pass ☐ Fail | |

**Overall:** ☐ All Pass ☐ Some Fail

---

## 📸 Screenshots (Optional)

Take screenshots of:
1. Full page view
2. Connected status indicator
3. User message sent
4. AI response with markdown
5. Any errors encountered

---

**Next Steps:**
- If all tests pass → Proceed to Feature 5
- If any fail → Debug and fix before continuing

---

**Ready to test?** Open http://localhost:5174/ and follow this checklist! ✅

