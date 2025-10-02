# Simple Artifact Persistence Architecture

## Overview

Lightweight artifact system - agent creates artifacts (charts, docs, PPTs) and saves them. No complex memory/session management.

## Core Concept

```
User Query → Agent Analyzes → Creates Artifact → Saves to DB → Returns Download Link
```

## Architecture

### 1. Simplified State

```python
class ArtifactAgentState(TypedDict):
    # Standard fields (existing)
    conversation_history: List[Dict]
    current_message: str
    tool_results: Dict
    final_response: str
    
    # Artifact fields (NEW - simple!)
    should_create_artifact: bool
    artifact_type: Optional[str]  # "viz", "ppt", "doc", "data"
    artifact: Optional[Dict]  # The generated artifact
    artifact_id: Optional[str]  # MongoDB ID after save
```

### 2. Artifact Schema (Simple)

```python
{
    "_id": ObjectId("..."),
    "artifact_id": "art_1234567890",
    "type": "visualization",  # viz, ppt, doc, reel, data
    "title": "Climate Policy Sentiment Analysis",
    "query": "Analyze global sentiment on climate policy",
    "content": {
        # Type-specific content
        "chart_type": "bar",
        "data": [...],
        "config": {...}
    },
    "file_path": "artifacts/art_1234567890.html",  # or .pptx, .pdf
    "sources": [...],  # Citations from analysis
    "created_at": "2025-10-01T12:00:00Z",
    "metadata": {
        "format": "html",
        "size_bytes": 12345
    }
}
```

### 3. Updated Graph (Add 2 Nodes)

```
START
  ↓
Conversation Manager
  ↓
Strategic Planner
  ↓
Tool Executor
  ↓
Decision Gate
  ↓
Response Synthesizer
  ↓
[Artifact Decision]  ← NEW: Should create artifact?
  ├─ YES → [Artifact Creator] ← NEW: Create & Save
  └─ NO  → END
  ↓
END
```

### 4. Artifact Decision Node

```python
async def artifact_decision(state: dict) -> dict:
    """
    Decide if artifact should be created
    
    Rules:
    - User explicitly asks: "create chart", "make presentation"
    - Analysis has data suitable for visualization
    - Multiple sources that need documentation
    """
    
    message = state["current_message"].lower()
    
    # Check for explicit requests
    if any(word in message for word in ["chart", "graph", "visualization", "visualize"]):
        state["should_create_artifact"] = True
        state["artifact_type"] = "viz"
    
    elif any(word in message for word in ["presentation", "ppt", "slides"]):
        state["should_create_artifact"] = True
        state["artifact_type"] = "ppt"
    
    elif any(word in message for word in ["document", "report", "pdf"]):
        state["should_create_artifact"] = True
        state["artifact_type"] = "doc"
    
    elif any(word in message for word in ["export", "download", "csv", "excel"]):
        state["should_create_artifact"] = True
        state["artifact_type"] = "data"
    
    else:
        # Auto-detect: if we have structured data, offer visualization
        tool_results = state.get("tool_results", {})
        if tool_results and len(tool_results.get("results", [])) > 3:
            state["should_create_artifact"] = True
            state["artifact_type"] = "viz"
        else:
            state["should_create_artifact"] = False
    
    return state
```

### 5. Artifact Creator Node

```python
async def artifact_creator(state: dict) -> dict:
    """
    Create and save artifact based on type
    """
    artifact_type = state.get("artifact_type")
    
    if artifact_type == "viz":
        artifact = await create_visualization(state)
    elif artifact_type == "ppt":
        artifact = await create_presentation(state)
    elif artifact_type == "doc":
        artifact = await create_document(state)
    elif artifact_type == "data":
        artifact = await create_data_export(state)
    
    # Save to MongoDB
    artifact_id = await save_artifact_to_db(artifact)
    
    state["artifact"] = artifact
    state["artifact_id"] = artifact_id
    
    return state
```

### 6. MongoDB Setup (Simple)

```python
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Connect to MongoDB
mongo_client = AsyncIOMotorClient(
    os.getenv("MONGODB_CONNECTION_STRING")
)
db = mongo_client["political_analyst_db"]
artifacts_collection = db["artifacts"]

async def save_artifact_to_db(artifact: dict) -> str:
    """Save artifact and return ID"""
    result = await artifacts_collection.insert_one(artifact)
    return str(result.inserted_id)

async def get_artifact(artifact_id: str) -> dict:
    """Retrieve artifact by ID"""
    return await artifacts_collection.find_one(
        {"artifact_id": artifact_id}
    )

async def list_recent_artifacts(limit: int = 10) -> list:
    """Get recent artifacts"""
    cursor = artifacts_collection.find().sort(
        "created_at", -1
    ).limit(limit)
    return await cursor.to_list(length=limit)
```

### 7. Artifact Types Implementation

#### Visualization (Plotly)

```python
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import uuid

async def create_visualization(state: dict) -> dict:
    """Create interactive chart from analysis results"""
    
    # Extract data from tool results
    tool_results = state.get("tool_results", {})
    
    # Example: Create bar chart from sentiment data
    # (This is simplified - real implementation extracts from your results)
    
    fig = go.Figure(data=[
        go.Bar(
            x=["US", "EU", "China"],
            y=[0.7, 0.5, -0.2],  # Sentiment scores
            marker_color=['green', 'yellow', 'red']
        )
    ])
    
    fig.update_layout(
        title=state["current_message"],
        xaxis_title="Country",
        yaxis_title="Sentiment Score"
    )
    
    # Save as HTML
    artifact_id = f"art_{uuid.uuid4().hex[:12]}"
    file_path = f"artifacts/{artifact_id}.html"
    
    os.makedirs("artifacts", exist_ok=True)
    fig.write_html(file_path)
    
    return {
        "artifact_id": artifact_id,
        "type": "visualization",
        "title": f"Analysis: {state['current_message'][:50]}",
        "query": state["current_message"],
        "content": {
            "chart_type": "bar",
            "data": fig.to_dict()
        },
        "file_path": file_path,
        "sources": state.get("citations", []),
        "created_at": datetime.utcnow().isoformat(),
        "metadata": {
            "format": "html",
            "library": "plotly"
        }
    }
```

#### Document (PDF)

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

async def create_document(state: dict) -> dict:
    """Create PDF document from analysis"""
    
    artifact_id = f"art_{uuid.uuid4().hex[:12]}"
    file_path = f"artifacts/{artifact_id}.pdf"
    
    # Create PDF
    c = canvas.Canvas(file_path, pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Political Analysis Report")
    
    # Query
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Query: {state['current_message']}")
    
    # Response
    c.setFont("Helvetica", 10)
    y = 680
    response = state.get("final_response", "")
    for line in response.split('\n')[:20]:  # First 20 lines
        c.drawString(50, y, line[:80])
        y -= 15
    
    c.save()
    
    return {
        "artifact_id": artifact_id,
        "type": "document",
        "title": f"Report: {state['current_message'][:50]}",
        "query": state["current_message"],
        "file_path": file_path,
        "created_at": datetime.utcnow().isoformat(),
        "metadata": {"format": "pdf"}
    }
```

#### Data Export (CSV)

```python
import pandas as pd

async def create_data_export(state: dict) -> dict:
    """Export analysis data to CSV"""
    
    # Extract data from results
    tool_results = state.get("tool_results", {})
    results = tool_results.get("results", [])
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    artifact_id = f"art_{uuid.uuid4().hex[:12]}"
    file_path = f"artifacts/{artifact_id}.csv"
    
    df.to_csv(file_path, index=False)
    
    return {
        "artifact_id": artifact_id,
        "type": "data",
        "title": f"Data Export: {state['current_message'][:50]}",
        "query": state["current_message"],
        "file_path": file_path,
        "created_at": datetime.utcnow().isoformat(),
        "metadata": {
            "format": "csv",
            "rows": len(df)
        }
    }
```

### 8. API Endpoints (Simple)

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

@app.post("/api/query")
async def process_query(query: str):
    """
    Process query and create artifact if needed
    Returns: response + artifact_id (if created)
    """
    result = await agent.process_query(query)
    
    return {
        "response": result["response"],
        "artifact_id": result.get("artifact_id"),
        "artifact_type": result.get("artifact_type")
    }

@app.get("/api/artifacts/{artifact_id}")
async def get_artifact_metadata(artifact_id: str):
    """Get artifact metadata"""
    artifact = await get_artifact(artifact_id)
    if not artifact:
        raise HTTPException(404, "Artifact not found")
    return artifact

@app.get("/api/artifacts/{artifact_id}/download")
async def download_artifact(artifact_id: str):
    """Download artifact file"""
    artifact = await get_artifact(artifact_id)
    if not artifact:
        raise HTTPException(404, "Artifact not found")
    
    return FileResponse(
        artifact["file_path"],
        filename=f"{artifact['artifact_id']}.{artifact['metadata']['format']}"
    )

@app.get("/api/artifacts/recent")
async def list_artifacts(limit: int = 10):
    """List recent artifacts"""
    return await list_recent_artifacts(limit)
```

### 9. UI Updates (Streamlit)

```python
# In chat_ui.py, after response:

if result.get("artifact_id"):
    st.success("🎨 Artifact Created!")
    
    artifact_type = result.get("artifact_type")
    artifact_id = result["artifact_id"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label=f"📥 Download {artifact_type.upper()}",
            data=open(f"artifacts/{artifact_id}.html", "rb").read(),
            file_name=f"analysis_{artifact_id}.html",
            mime="text/html"
        )
    
    with col2:
        # Preview (if HTML visualization)
        if artifact_type == "viz":
            st.components.v1.html(
                open(f"artifacts/{artifact_id}.html").read(),
                height=400
            )
```

### 10. File Structure

```
Political_Analyst_Workbench/
├── langgraph_master_agent/
│   ├── nodes/
│   │   ├── artifact_decision.py  ← NEW
│   │   └── artifact_creator.py   ← NEW
│   └── tools/
│       └── artifact_tools.py     ← NEW
│           ├── create_visualization()
│           ├── create_document()
│           ├── create_presentation()
│           └── create_data_export()
│
├── artifacts/                     ← NEW (storage)
│   ├── art_123abc.html
│   ├── art_456def.pdf
│   └── art_789ghi.csv
│
├── artifact_api.py                ← NEW (FastAPI)
└── chat_ui.py                     (updated)
```

### 11. Implementation Steps

**Step 1: Add MongoDB**
```bash
pip install motor pymongo
```

**Step 2: Create Artifact Tools**
```bash
pip install plotly reportlab python-pptx pandas
```

**Step 3: Add 2 New Nodes**
- artifact_decision.py
- artifact_creator.py

**Step 4: Update Graph**
```python
workflow.add_node("artifact_decision", artifact_decision)
workflow.add_node("artifact_creator", artifact_creator)

workflow.add_edge("response_synthesizer", "artifact_decision")

workflow.add_conditional_edges(
    "artifact_decision",
    lambda state: "create" if state["should_create_artifact"] else "end",
    {
        "create": "artifact_creator",
        "end": END
    }
)

workflow.add_edge("artifact_creator", END)
```

**Step 5: Update UI**
- Show artifact preview
- Add download button
- List recent artifacts in sidebar

## Benefits of Simple Approach

✅ **No Complex Setup**
- Just MongoDB for storage
- No user management
- No session complexity

✅ **Easy to Use**
- Agent auto-detects when to create artifacts
- Or user explicitly requests
- Download immediately

✅ **Scalable**
- Can add user/session later
- Start simple, grow as needed

✅ **Clear Flow**
- Query → Analysis → Artifact → Download
- One-to-one mapping

## Example Usage

```python
# User: "Analyze climate sentiment and create a chart"
result = agent.process_query(
    "Analyze climate sentiment and create a chart"
)

# Returns:
{
    "response": "Here's the analysis...",
    "artifact_id": "art_abc123",
    "artifact_type": "viz"
}

# User downloads: artifacts/art_abc123.html
```

---

**Simple. No memory. Just artifacts.** 🎨

Next: Implement artifact_decision.py and artifact_creator.py nodes?

