# Political Analyst Workbench - Feature Implementation Plan

**Project:** Political Analyst Workbench MVP  
**Approach:** Incremental development with testing  
**Timeline:** 7 working days (56 hours)

---

## 🎯 **Core Principles**

1. ✅ Build one feature at a time
2. ✅ Test immediately after implementation
3. ✅ Frontend + Backend developed together
4. ✅ Each feature must be demonstrable
5. ✅ No feature is "done" until tested

---

## 📦 **Feature Breakdown (10 Features)**

### **Phase 1: Foundation (Day 1-2)**

---

#### **Feature 1: Project Setup + Basic UI Layout**
**Priority:** P0 - Blocker  
**Time:** 4 hours  
**Status:** ⬜ Not Started

**Description:**  
Set up both frontend and backend projects with basic layout structure.

**Frontend Tasks:**
- [ ] Create Vite + React + TypeScript project
- [ ] Copy bolt.diy's UI component library
- [ ] Set up UnoCSS styling
- [ ] Create split-pane layout (ResizablePanel)
- [ ] Add basic header with logo

**Backend Tasks:**
- [ ] Verify Political_Analyst_Workbench backend is running
- [ ] Ensure `/health` endpoint works
- [ ] Verify MongoDB connection
- [ ] Confirm S3 service is ready

**Test Criteria:**
```bash
# Frontend
✓ npm run dev starts on http://localhost:5173
✓ Split-pane layout renders (2 panels visible)
✓ Panels are resizable
✓ No console errors

# Backend
✓ curl http://localhost:8000/health returns 200
✓ MongoDB connected
✓ S3 service available
```

**Deliverable:**  
- Empty split-pane UI running
- Backend health check passing
- Screenshot of layout

---

#### **Feature 2: WebSocket Connection (No Messages Yet)**
**Priority:** P0 - Blocker  
**Time:** 3 hours  
**Status:** ⬜ Not Started

**Description:**  
Establish WebSocket connection between frontend and backend.

**Frontend Tasks:**
- [ ] Create `WebSocketService` class
- [ ] Implement connection logic
- [ ] Add connection status indicator (🟢 Connected / 🔴 Disconnected)
- [ ] Handle reconnection on failure
- [ ] Add connection logs to console

**Backend Tasks:**
- [ ] Update `/ws/analyze` endpoint
- [ ] Send `connected` message on connection
- [ ] Handle client disconnection
- [ ] Add logging for connections

**Test Criteria:**
```bash
# Frontend
✓ Status indicator shows 🟢 when connected
✓ Status indicator shows 🔴 when backend is down
✓ Automatic reconnection works (stop/start backend)
✓ Console shows: "WebSocket connected"

# Backend
✓ Server logs: "Client connected: conn_xyz"
✓ Server logs: "Client disconnected: conn_xyz"
✓ No crashes on connection/disconnection
```

**Deliverable:**
- Frontend shows connection status
- WebSocket handshake working
- Connection survives backend restart

---

#### **Feature 3: Message Input + Send**
**Priority:** P0 - Blocker  
**Time:** 3 hours  
**Status:** ⬜ Not Started

**Description:**  
User can type a message and send it (UI only, no processing yet).

**Frontend Tasks:**
- [ ] Create `MessageInput` component (textarea + send button)
- [ ] Add character counter (0/2000)
- [ ] Disable send button when empty or > 2000 chars
- [ ] Add "Press Enter to send" hint
- [ ] Send query message via WebSocket
- [ ] Clear input after sending

**Backend Tasks:**
- [ ] Receive `query` message from WebSocket
- [ ] Parse message JSON
- [ ] Validate query (length, format)
- [ ] Send back `session_start` message
- [ ] Log received query

**Test Criteria:**
```bash
# Frontend
✓ Input accepts text
✓ Character counter updates (e.g., "45/2000")
✓ Send button disabled when empty
✓ Send button disabled when > 2000 chars
✓ Pressing Enter sends message
✓ Input clears after sending

# Backend
✓ Receives query message
✓ Logs: "Received query: <text>"
✓ Sends back session_start with session_id
✓ Rejects queries > 2000 chars (error message)
```

**Deliverable:**
- Working input box
- Messages sent to backend
- Backend acknowledges receipt
- Video demo of typing + sending

---

### **Phase 2: Core Streaming (Day 3-4)**

---

#### **Feature 4: Display Streaming Response (Text Only)**
**Priority:** P0 - Blocker  
**Time:** 4 hours  
**Status:** ⬜ Not Started

**Description:**  
Backend processes query and streams response text. Frontend displays it incrementally.

**Frontend Tasks:**
- [ ] Create `MessageList` component
- [ ] Create `Message` component (user vs AI)
- [ ] Display user message immediately after sending
- [ ] Display AI message with streaming text
- [ ] Add typing indicator animation
- [ ] Auto-scroll to bottom as text arrives

**Backend Tasks:**
- [ ] Integrate with existing MasterPoliticalAnalyst
- [ ] Stream `content` messages (chunks of text)
- [ ] Send `complete` message when done
- [ ] Handle cancellation requests
- [ ] Add streaming to existing workflow

**Test Criteria:**
```bash
# Frontend
✓ User message appears instantly
✓ AI message appears with typing indicator
✓ Text streams word-by-word (visible animation)
✓ Markdown rendering works (bold, links, etc.)
✓ Auto-scrolls to bottom
✓ Final message is complete and formatted

# Backend
✓ Sends content messages every ~100-200ms
✓ Each content message contains text chunk
✓ Final content message has is_complete: true
✓ Sends complete message with metadata
✓ Total time < 15 seconds for simple query
```

**Test Query:**
```
"Tell me about India's economy in 2024"
```

**Deliverable:**
- Full conversation UI with streaming
- Working chat history
- Video showing smooth text streaming

---

#### **Feature 5: Status Updates + Progress**
**Priority:** P1 - High  
**Time:** 2 hours  
**Status:** ⬜ Not Started

**Description:**  
Show what the AI is doing (searching, analyzing, generating).

**Frontend Tasks:**
- [ ] Create `StatusIndicator` component
- [ ] Show status below typing indicator
- [ ] Icons for each status: 🔍 📊 🎨 ✅
- [ ] Optional: Progress bar (0-100%)
- [ ] Animate status transitions

**Backend Tasks:**
- [ ] Send `status` message at each workflow step
- [ ] Update existing nodes to emit status
- [ ] Add status: "searching", "analyzing", "generating"
- [ ] Include progress percentage (optional)

**Test Criteria:**
```bash
# Frontend
✓ Shows "🔍 Searching..." when backend searches
✓ Shows "📊 Analyzing..." when processing
✓ Shows "✅ Complete" when done
✓ Status updates smoothly (no flickering)

# Backend
✓ Sends status before Tavily search
✓ Sends status before response generation
✓ Status messages include descriptive text
✓ Timing: status updates every 1-2 seconds
```

**Deliverable:**
- Status indicator visible during analysis
- Clear visual feedback of AI progress

---

#### **Feature 6: Citations Display**
**Priority:** P1 - High  
**Time:** 3 hours  
**Status:** ⬜ Not Started

**Description:**  
Show sources/citations for the AI response.

**Frontend Tasks:**
- [ ] Create `CitationList` component
- [ ] Show citations below AI message
- [ ] Display: title, URL, snippet
- [ ] Add "View Sources" collapse/expand
- [ ] Make URLs clickable (open in new tab)
- [ ] Add citation count badge

**Backend Tasks:**
- [ ] Extract citations from Tavily results
- [ ] Send `citation` message with sources
- [ ] Include: title, url, snippet, score
- [ ] Send citations after search completes

**Test Criteria:**
```bash
# Frontend
✓ Citations appear after AI response
✓ Shows count: "3 sources"
✓ Each citation shows title + URL
✓ Clicking URL opens in new tab
✓ "View Sources" toggle works
✓ Citations are readable and formatted

# Backend
✓ Sends citation message with 3-5 sources
✓ Each citation has title, url, snippet
✓ Citations are relevant to query
✓ No duplicate citations
```

**Test Query:**
```
"What are the latest developments in US-China trade relations?"
```

**Deliverable:**
- Working citations display
- Sources are clickable
- Clean, readable layout

---

### **Phase 3: Artifacts (Day 5-6)**

---

#### **Feature 7: Artifact Display (Right Panel)**
**Priority:** P0 - Blocker  
**Time:** 4 hours  
**Status:** ⬜ Not Started

**Description:**  
Display generated charts in the right panel.

**Frontend Tasks:**
- [ ] Create `ArtifactPanel` component
- [ ] Show "No artifact yet" placeholder
- [ ] Display iframe when artifact arrives
- [ ] Add loading spinner during generation
- [ ] Handle artifact errors gracefully
- [ ] Resize iframe to fill panel

**Backend Tasks:**
- [ ] Send `artifact` message with status: "generating"
- [ ] Generate chart using existing artifact_creator
- [ ] Upload to S3 / save locally
- [ ] Send `artifact` message with status: "ready"
- [ ] Include html_url and png_url

**Test Criteria:**
```bash
# Frontend
✓ Right panel shows placeholder initially
✓ Shows spinner when artifact is generating
✓ Displays chart in iframe when ready
✓ Chart is interactive (Plotly controls work)
✓ No scrollbars in iframe (perfect fit)
✓ Chart updates when new artifact arrives

# Backend
✓ Detects when query needs visualization
✓ Sends "generating" status
✓ Creates Plotly chart
✓ Sends "ready" status with URLs
✓ HTML file is accessible
✓ PNG file is accessible
```

**Test Query:**
```
"Create a line chart of US GDP growth 2020-2025"
```

**Deliverable:**
- Chart displays in right panel
- Smooth loading experience
- Interactive Plotly chart works

---

#### **Feature 8: Artifact Actions (Download, Share)**
**Priority:** P2 - Medium  
**Time:** 2 hours  
**Status:** ⬜ Not Started

**Description:**  
User can download or share artifacts.

**Frontend Tasks:**
- [ ] Create `ArtifactActions` component
- [ ] Add Download PNG button
- [ ] Add Download HTML button
- [ ] Add Copy Link button
- [ ] Show toast notification on action
- [ ] Implement download logic

**Backend Tasks:**
- [ ] Ensure artifact URLs are publicly accessible
- [ ] Add CORS headers for downloads
- [ ] Generate shareable links (optional)
- [ ] Track download count (optional)

**Test Criteria:**
```bash
# Frontend
✓ Download PNG button downloads file
✓ Downloaded PNG filename: "india-gdp-growth.png"
✓ Download HTML button downloads file
✓ Downloaded HTML opens in browser
✓ Copy Link copies URL to clipboard
✓ Toast shows "Link copied!" message

# Backend
✓ PNG download returns image/png
✓ HTML download returns text/html
✓ CORS headers allow downloads
✓ Files are accessible without auth
```

**Deliverable:**
- Working download buttons
- Shareable artifact links
- User-friendly filenames

---

### **Phase 4: History & Polish (Day 7)**

---

#### **Feature 9: Conversation History (Sidebar)**
**Priority:** P2 - Medium  
**Time:** 3 hours  
**Status:** ⬜ Not Started

**Description:**  
Show list of recent conversations, click to load.

**Frontend Tasks:**
- [ ] Create `HistoryPanel` sidebar (collapsible)
- [ ] Fetch history on mount
- [ ] Display list of sessions (title, date, thumbnail)
- [ ] Click to load conversation
- [ ] Add "New Chat" button
- [ ] Show active conversation highlight

**Backend Tasks:**
- [ ] Create `GET /api/sessions` endpoint
- [ ] Return list of recent sessions
- [ ] Include: session_id, query, date, artifact_id
- [ ] Create `GET /api/sessions/{id}` endpoint
- [ ] Return full conversation with messages

**Test Criteria:**
```bash
# Frontend
✓ History sidebar opens on button click
✓ Shows last 10 conversations
✓ Each item shows query snippet + date
✓ Clicking item loads full conversation
✓ "New Chat" clears current chat
✓ Active conversation is highlighted

# Backend
✓ GET /api/sessions returns sessions
✓ Sessions sorted by date (newest first)
✓ Each session includes query + artifact
✓ GET /api/sessions/{id} returns full data
✓ Response includes all messages + artifact
```

**Deliverable:**
- Working history sidebar
- Click to load previous chats
- "New Chat" functionality

---

#### **Feature 10: Error Handling + Loading States**
**Priority:** P1 - High  
**Time:** 2 hours  
**Status:** ⬜ Not Started

**Description:**  
Gracefully handle errors and show loading states.

**Frontend Tasks:**
- [ ] Add error boundary component
- [ ] Show error messages in chat
- [ ] Add retry button for failed requests
- [ ] Show loading skeleton for history
- [ ] Handle WebSocket disconnection gracefully
- [ ] Show offline indicator

**Backend Tasks:**
- [ ] Send `error` messages on failure
- [ ] Include error code, message, recoverable flag
- [ ] Handle Tavily rate limits
- [ ] Handle MongoDB connection errors
- [ ] Log all errors to console

**Test Criteria:**
```bash
# Frontend
✓ Shows error message if backend crashes
✓ "Retry" button re-sends query
✓ Offline indicator when WebSocket disconnects
✓ Loading skeletons during data fetch
✓ Error messages are user-friendly

# Backend
✓ Sends error message on Tavily failure
✓ Error includes: code, message, recoverable
✓ Rate limit errors show retry_after
✓ Server doesn't crash on errors
✓ All errors are logged
```

**Test Scenarios:**
1. Stop backend → Frontend shows offline
2. Invalid query → Backend sends error
3. Rate limit → Shows "Please wait 60s"

**Deliverable:**
- Robust error handling
- User-friendly error messages
- Graceful degradation

---

## 🧪 **Testing Strategy**

### **Unit Tests (Optional for MVP)**
- WebSocket service
- Message parsing
- UI components

### **Integration Tests (Required)**
Each feature must pass these:
1. **Manual testing** - Developer clicks through
2. **Acceptance criteria** - All checkboxes ✓
3. **Demo video** - Screen recording of feature

### **End-to-End Test (Final)**
Complete user journey:
```
1. Open app → See empty chat
2. Type query → See streaming response
3. View citation → Opens in new tab
4. See chart → Displays in right panel
5. Download PNG → File downloads
6. View history → Shows past chats
7. Load old chat → Full conversation appears
```

---

## 📊 **Progress Tracking**

| Feature | Frontend | Backend | Testing | Status | Time |
|---------|----------|---------|---------|--------|------|
| F1: Project Setup | ⬜ | ⬜ | ⬜ | Not Started | 4h |
| F2: WebSocket | ⬜ | ⬜ | ⬜ | Not Started | 3h |
| F3: Message Input | ⬜ | ⬜ | ⬜ | Not Started | 3h |
| F4: Streaming | ⬜ | ⬜ | ⬜ | Not Started | 4h |
| F5: Status | ⬜ | ⬜ | ⬜ | Not Started | 2h |
| F6: Citations | ⬜ | ⬜ | ⬜ | Not Started | 3h |
| F7: Artifacts | ⬜ | ⬜ | ⬜ | Not Started | 4h |
| F8: Actions | ⬜ | ⬜ | ⬜ | Not Started | 2h |
| F9: History | ⬜ | ⬜ | ⬜ | Not Started | 3h |
| F10: Errors | ⬜ | ⬜ | ⬜ | Not Started | 2h |
| **TOTAL** | | | | | **30h** |

---

## 🚀 **Getting Started**

### **Prerequisites**
- [ ] Node.js installed
- [ ] Python + FastAPI backend running
- [ ] MongoDB connected
- [ ] S3 service configured

### **Start Feature 1**
```bash
# 1. Create frontend project
cd ui_exploration
npm create vite@latest political-analyst-ui -- --template react-ts

# 2. Verify backend
cd ../Political_Analyst_Workbench/backend_server
python app.py

# 3. Copy UI components from bolt.diy
# (Instructions in Feature 1)
```

---

## 💡 **Notes**

- Each feature is **independently testable**
- Features **build on previous work**
- Can **skip optional features** if time is tight
- **Demo after each feature** to stakeholders
- Keep **both frontend and backend in sync**

---

**Ready to start Feature 1?** Let me know! 🚀

