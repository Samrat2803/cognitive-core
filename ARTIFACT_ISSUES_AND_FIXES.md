# Artifact Display Issues & Solutions

## 🐛 **Issues Identified:**

### 1. **Blank White Image in Artifact Panel**
**Root Cause:** The frontend is trying to load S3-hosted HTML files in an iframe using presigned URLs. However:
- S3 private objects loaded in iframes may have CORS issues
- Browsers block cross-origin iframe content for security
- The `text/html` content-type from S3 may not render properly in iframes

**Current Flow:**
```
Backend → Upload HTML to S3 (private) → Generate presigned URL → 
Frontend iframe loads URL → ❌ Blank/CORS error
```

### 2. **Slow Artifact Creation (90 seconds)**
**Root Cause:**
- GPT-4o takes 30-40 seconds to process query
- Data extraction from conversation history is LLM-heavy
- Agent runs through multiple nodes (strategic_planner, tool_executor, response_synthesizer, artifact_decision, artifact_creator)

**Current Timing:**
- Query 1 (TCS Revenue): ~10 seconds ✅
- Query 2 (Create Chart): ~90 seconds ❌

---

## ✅ **Solutions:**

### **Fix 1: Serve HTML Directly from Backend (Not S3)**

**Why:** Backend-served HTML doesn't have CORS issues.

**Changes Needed:**
1. **Keep S3 for PNG only** (for download)
2. **Serve HTML via backend endpoint:**
   ```python
   @app.get("/api/artifacts/{artifact_id}.html")
   async def get_artifact_html(artifact_id: str):
       file_path = f"artifacts/{artifact_id}.html"
       return FileResponse(file_path, media_type="text/html")
   ```
3. **Update frontend to use:**
   ```typescript
   html_url: `http://localhost:8000/api/artifacts/${artifact_id}.html`
   ```

**Impact:** ✅ No CORS issues, instant loading

---

### **Fix 2: Use PNG Instead of HTML for Display**

**Why:** PNG images are simpler, smaller, and always work in `<img>` tags.

**Changes Needed:**
1. **Frontend: Show PNG by default, HTML on request:**
   ```tsx
   {artifact.png_url && (
     <img src={artifact.png_url} alt={artifact.title} />
   )}
   <button onClick={() => window.open(artifact.html_url)}>
     View Interactive
   </button>
   ```

**Impact:** ✅ Instant rendering, smaller file size (PNG ~20KB vs HTML 4.4MB)

---

### **Fix 3: Reduce Chart Creation Time**

**Options:**

#### **Option A: Cache Data Extraction (Fast Fix)**
- After Query 1, store extracted data in agent state
- Query 2 just creates chart from cached data
- **Impact:** 90s → 15s

#### **Option B: Stream Artifact Creation**
- Start creating chart while LLM is still generating response
- Show "Generating visualization..." status
- **Impact:** Better UX, same actual time

#### **Option C: Switch to GPT-4o-mini for Artifact Decisions**
- Use GPT-4o for main query
- Use GPT-4o-mini for data extraction (faster, cheaper)
- **Impact:** 90s → 30-40s

---

## 🎯 **Recommended Immediate Fix:**

### **Combination: PNG Display + Backend HTML Serving**

1. **Frontend Change (ArtifactPanel.tsx):**
```tsx
{artifact.status === 'ready' && (
  artifact.png_url ? (
    <img 
      src={artifact.png_url} 
      alt={artifact.title} 
      className="artifact-image"
    />
  ) : artifact.html_url ? (
    <iframe 
      src={artifact.html_url} 
      className="artifact-iframe"
    />
  ) : null
)}
```

2. **Backend Change (app.py):**
```python
# In artifact message creation:
await websocket.send_json(create_message(
    "artifact",
    {
        "artifact_id": artifact_data.get("artifact_id"),
        "type": artifact_data.get("type", "chart"),
        "title": artifact_data.get("title", "Analysis Result"),
        # Serve HTML from backend, not S3
        "html_url": f"http://localhost:8000/api/artifacts/{artifact_data.get('artifact_id')}.html",
        # S3 PNG works fine for images
        "png_url": png_url,  # S3 presigned URL
        "storage": artifact_data.get("storage", "local"),
        "metadata": artifact_data.get("metadata", {})
    },
    current_message_id
))
```

---

## 📊 **Expected Results After Fix:**

- ✅ Artifacts display immediately (no blank screen)
- ✅ PNG images are smaller and faster (~20KB vs 4.4MB)
- ✅ Interactive HTML available via "View Interactive" button
- ✅ No CORS issues
- ⏱️  Creation time still ~90s (fix separately if needed)

---

## 🔧 **Next Steps:**

1. Implement PNG-first display
2. Add backend HTML endpoint
3. Test with S3 presigned PNG URLs
4. (Optional) Optimize chart creation speed


