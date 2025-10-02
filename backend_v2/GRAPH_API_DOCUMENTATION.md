# Graph Visualization API Documentation

## Overview

The backend provides **three endpoints** for visualizing the LangGraph execution flow:

1. **`GET /api/graph/structure`** - Static graph structure (nodes & edges)
2. **`GET /api/graph/execution/{session_id}`** - Graph with execution state for specific conversation
3. **`GET /api/graph/mermaid`** - Mermaid diagram text (for simple rendering)

The frontend receives **structured JSON data** (nodes and edges) and can render it using any visualization library.

---

## API Endpoints

### 1. GET `/api/graph/structure`

**Purpose:** Get the static graph structure of the Master Agent workflow.

**Use Case:** Display the agent architecture diagram on documentation pages, onboarding flows, or as a static reference.

**Request:**
```bash
curl http://localhost:8000/api/graph/structure
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "__start__",
      "label": "START",
      "type": "control",
      "description": "Entry point for the agent workflow",
      "category": "control",
      "metadata": {
        "color": "#4ade80",
        "icon": "play"
      }
    },
    {
      "id": "conversation_manager",
      "label": "Conversation Manager",
      "type": "processing",
      "description": "Manages conversation context and message history",
      "category": "processing",
      "metadata": {
        "color": "#60a5fa",
        "icon": "message-circle",
        "responsibilities": [
          "Initialize conversation history",
          "Track artifacts from previous turns",
          "Maintain session state"
        ]
      }
    },
    {
      "id": "strategic_planner",
      "label": "Strategic Planner",
      "type": "llm",
      "description": "Analyzes query and selects appropriate tools",
      "category": "decision",
      "metadata": {
        "color": "#a78bfa",
        "icon": "brain",
        "llm_used": true,
        "responsibilities": [
          "Understand user intent",
          "Select tools/sub-agents",
          "Plan execution strategy"
        ]
      }
    }
    // ... more nodes
  ],
  "edges": [
    {
      "id": "edge_0",
      "source": "__start__",
      "target": "conversation_manager",
      "type": "default",
      "label": ""
    },
    {
      "id": "edge_6",
      "source": "decision_gate",
      "target": "tool_executor",
      "type": "conditional",
      "label": "needs more tools",
      "condition": "tool_executor"
    }
    // ... more edges
  ],
  "metadata": {
    "node_count": 9,
    "edge_count": 10,
    "graph_type": "state_machine",
    "description": "Master Political Analyst Agent - LangGraph Workflow"
  }
}
```

---

### 2. GET `/api/graph/execution/{session_id}`

**Purpose:** Get graph with execution state overlaid for a specific conversation.

**Use Case:** Show users which nodes were executed, timing information, and decision paths taken for their specific query.

**Request:**
```bash
curl http://localhost:8000/api/graph/execution/session_1759381623
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "conversation_manager",
      "label": "Conversation Manager",
      "type": "processing",
      "description": "Manages conversation context...",
      "category": "processing",
      "metadata": { /* ... */ },
      "execution": {
        "executed": true,
        "timestamp": "2024-10-02T10:00:00",
        "status": "completed",
        "duration_ms": 125,
        "details": {
          "action": "Context initialized",
          "input": "User message: how has india been affected...",
          "output": "Session ID: session_1759381623..."
        }
      }
    },
    {
      "id": "artifact_creator",
      "label": "Artifact Creator",
      "type": "processing",
      "execution": {
        "executed": false
      }
    }
    // ... more nodes with execution state
  ],
  "edges": [
    {
      "id": "edge_0",
      "source": "__start__",
      "target": "conversation_manager",
      "type": "default",
      "label": "",
      "execution": {
        "traversed": true,
        "count": 1
      }
    },
    {
      "id": "edge_7",
      "source": "decision_gate",
      "target": "tool_executor",
      "type": "conditional",
      "label": "needs more tools",
      "execution": {
        "traversed": false,
        "count": 0
      }
    }
    // ... more edges with traversal info
  ],
  "execution_metadata": {
    "session_id": "session_1759381623",
    "total_steps": 8,
    "executed_nodes": 6,
    "start_time": "2024-10-02T10:00:00",
    "end_time": "2024-10-02T10:00:09",
    "total_duration_ms": 9000,
    "iterations": 1
  }
}
```

**Key Features:**
- ✅ Each node has `execution.executed` flag
- ✅ Executed nodes include timing, status, and details
- ✅ Edges show if they were traversed
- ✅ Loop detection (iteration count)
- ✅ Total execution metadata

---

### 3. GET `/api/graph/mermaid`

**Purpose:** Get Mermaid diagram text for simple rendering.

**Use Case:** Quick preview without heavy JavaScript libraries. Can be rendered with Mermaid.js (lightweight).

**Request:**
```bash
curl http://localhost:8000/api/graph/mermaid
```

**Response:**
```json
{
  "format": "mermaid",
  "diagram": "graph TD;\n\t__start__([<p>__start__</p>]):::first\n\tconversation_manager(conversation_manager)\n...",
  "viewer_url": "https://mermaid.live"
}
```

---

## Frontend Implementation Guide

### Option 1: React Flow (Recommended for Interactive UI)

**Installation:**
```bash
npm install reactflow
```

**Component Example:**
```typescript
import React, { useEffect, useState } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap,
  Node,
  Edge 
} from 'reactflow';
import 'reactflow/dist/style.css';

interface GraphVisualizerProps {
  sessionId?: string;  // Optional: for execution state
}

export const GraphVisualizer: React.FC<GraphVisualizerProps> = ({ sessionId }) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        // Fetch execution-specific graph or static structure
        const url = sessionId 
          ? `/api/graph/execution/${sessionId}`
          : '/api/graph/structure';
        
        const response = await fetch(url);
        const data = await response.json();
        
        // Transform to React Flow format
        const flowNodes: Node[] = data.nodes.map((node: any, index: number) => ({
          id: node.id,
          type: getNodeType(node.type),
          data: {
            label: node.label,
            description: node.description,
            executed: node.execution?.executed,
            status: node.execution?.status,
            duration: node.execution?.duration_ms
          },
          position: calculatePosition(node, index, data.nodes.length),
          style: {
            background: node.execution?.executed ? '#10b981' : node.metadata.color,
            opacity: node.execution?.executed === false ? 0.3 : 1,
            border: node.execution?.status === 'error' ? '2px solid #ef4444' : undefined
          }
        }));

        const flowEdges: Edge[] = data.edges.map((edge: any) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.label,
          type: edge.type === 'conditional' ? 'smoothstep' : 'default',
          animated: edge.execution?.traversed,
          style: {
            stroke: edge.execution?.traversed ? '#10b981' : '#999',
            strokeWidth: edge.execution?.traversed ? 2 : 1,
            opacity: edge.execution?.traversed === false ? 0.2 : 1
          }
        }));

        setNodes(flowNodes);
        setEdges(flowEdges);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch graph:', error);
        setLoading(false);
      }
    };

    fetchGraph();
  }, [sessionId]);

  if (loading) return <div>Loading graph...</div>;

  return (
    <div style={{ height: '600px', width: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        attributionPosition="bottom-left"
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
};

function getNodeType(type: string): string {
  switch (type) {
    case 'control': return 'input';
    case 'decision': return 'default';
    case 'llm': return 'default';
    default: return 'default';
  }
}

function calculatePosition(node: any, index: number, total: number) {
  // Simple vertical layout (can be improved with dagre or elkjs)
  return {
    x: (index % 3) * 250,
    y: Math.floor(index / 3) * 150
  };
}
```

**Usage:**
```tsx
// Static graph
<GraphVisualizer />

// Execution-specific graph
<GraphVisualizer sessionId="session_1759381623" />
```

---

### Option 2: D3.js (For Custom Visualizations)

**Installation:**
```bash
npm install d3
```

**Example:**
```typescript
import * as d3 from 'd3';

async function renderGraph(containerId: string, sessionId?: string) {
  const url = sessionId 
    ? `/api/graph/execution/${sessionId}`
    : '/api/graph/structure';
  
  const data = await fetch(url).then(res => res.json());
  
  const width = 800;
  const height = 600;
  
  const svg = d3.select(`#${containerId}`)
    .append('svg')
    .attr('width', width)
    .attr('height', height);
  
  // Create force simulation
  const simulation = d3.forceSimulation(data.nodes)
    .force('link', d3.forceLink(data.edges).id((d: any) => d.id))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2));
  
  // Draw edges
  const links = svg.append('g')
    .selectAll('line')
    .data(data.edges)
    .join('line')
    .attr('stroke', (d: any) => d.execution?.traversed ? '#10b981' : '#999')
    .attr('stroke-width', (d: any) => d.execution?.traversed ? 2 : 1);
  
  // Draw nodes
  const nodes = svg.append('g')
    .selectAll('circle')
    .data(data.nodes)
    .join('circle')
    .attr('r', 20)
    .attr('fill', (d: any) => d.execution?.executed ? '#10b981' : d.metadata.color)
    .attr('opacity', (d: any) => d.execution?.executed === false ? 0.3 : 1);
  
  // Add labels
  const labels = svg.append('g')
    .selectAll('text')
    .data(data.nodes)
    .join('text')
    .text((d: any) => d.label)
    .attr('font-size', 12)
    .attr('dx', 25);
  
  // Update positions on simulation tick
  simulation.on('tick', () => {
    links
      .attr('x1', (d: any) => d.source.x)
      .attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x)
      .attr('y2', (d: any) => d.target.y);
    
    nodes
      .attr('cx', (d: any) => d.x)
      .attr('cy', (d: any) => d.y);
    
    labels
      .attr('x', (d: any) => d.x)
      .attr('y', (d: any) => d.y);
  });
}

// Usage
renderGraph('graph-container', 'session_1759381623');
```

---

### Option 3: Cytoscape.js (For Complex Layouts)

**Installation:**
```bash
npm install cytoscape
```

**Example:**
```typescript
import cytoscape from 'cytoscape';

async function renderGraph(containerId: string, sessionId?: string) {
  const url = sessionId 
    ? `/api/graph/execution/${sessionId}`
    : '/api/graph/structure';
  
  const data = await fetch(url).then(res => res.json());
  
  const cy = cytoscape({
    container: document.getElementById(containerId),
    
    elements: {
      nodes: data.nodes.map((node: any) => ({
        data: {
          id: node.id,
          label: node.label,
          executed: node.execution?.executed,
          color: node.metadata.color
        }
      })),
      
      edges: data.edges.map((edge: any) => ({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.label,
          traversed: edge.execution?.traversed
        }
      }))
    },
    
    style: [
      {
        selector: 'node',
        style: {
          'background-color': 'data(color)',
          'label': 'data(label)',
          'opacity': (ele: any) => ele.data('executed') === false ? 0.3 : 1
        }
      },
      {
        selector: 'edge',
        style: {
          'width': (ele: any) => ele.data('traversed') ? 3 : 1,
          'line-color': (ele: any) => ele.data('traversed') ? '#10b981' : '#999',
          'target-arrow-color': '#999',
          'target-arrow-shape': 'triangle',
          'label': 'data(label)',
          'curve-style': 'bezier'
        }
      }
    ],
    
    layout: {
      name: 'dagre',  // Hierarchical layout
      rankDir: 'TB'    // Top to bottom
    }
  });
}
```

---

### Option 4: Mermaid.js (Lightweight)

**Installation:**
```bash
npm install mermaid
```

**Example:**
```typescript
import mermaid from 'mermaid';

mermaid.initialize({ startOnLoad: true });

async function renderMermaid(containerId: string) {
  const response = await fetch('/api/graph/mermaid');
  const data = await response.json();
  
  const element = document.getElementById(containerId);
  if (element) {
    element.innerHTML = `<div class="mermaid">${data.diagram}</div>`;
    mermaid.init(undefined, element.querySelector('.mermaid'));
  }
}
```

---

## Visual Styling Guide

### Node Colors (from metadata)

| Node Type | Color | Use Case |
|-----------|-------|----------|
| Control (__start__, __end__) | `#4ade80` / `#ef4444` | Entry/exit points |
| Conversation Manager | `#60a5fa` | Context management |
| Strategic Planner | `#a78bfa` | LLM decision making |
| Tool Executor | `#f59e0b` | Tool execution |
| Decision Gate | `#ec4899` | Routing decisions |
| Response Synthesizer | `#10b981` | LLM synthesis |
| Artifact Decision | `#8b5cf6` | Visualization logic |
| Artifact Creator | `#06b6d4` | Chart generation |

### Execution State Indicators

```typescript
// Node styling based on execution state
const getNodeStyle = (node: any) => {
  if (!node.execution) {
    return { opacity: 1, background: node.metadata.color };
  }
  
  if (node.execution.executed) {
    return {
      opacity: 1,
      background: '#10b981',  // Green for executed
      border: node.execution.status === 'error' ? '2px solid #ef4444' : undefined
    };
  } else {
    return {
      opacity: 0.3,  // Faded for not executed
      background: node.metadata.color
    };
  }
};

// Edge styling based on traversal
const getEdgeStyle = (edge: any) => {
  if (edge.execution?.traversed) {
    return {
      stroke: '#10b981',
      strokeWidth: 2,
      animated: true  // For React Flow
    };
  } else {
    return {
      stroke: '#999',
      strokeWidth: 1,
      opacity: 0.2
    };
  }
};
```

---

## Use Cases & Examples

### 1. Documentation Page - Static Graph

```tsx
<div className="agent-architecture">
  <h2>How the Agent Works</h2>
  <GraphVisualizer />
</div>
```

### 2. Conversation Page - Execution Graph

```tsx
<div className="conversation-debug">
  <h3>Execution Path for This Query</h3>
  <GraphVisualizer sessionId={currentSessionId} />
  <ExecutionTimeline sessionId={currentSessionId} />
</div>
```

### 3. Admin Dashboard - Multiple Sessions

```tsx
<div className="admin-dashboard">
  {sessions.map(session => (
    <div key={session.id}>
      <h4>{session.query}</h4>
      <GraphVisualizer sessionId={session.id} />
    </div>
  ))}
</div>
```

---

## Performance Considerations

1. **Caching**: Cache static graph structure (doesn't change)
2. **Lazy Loading**: Load execution graphs on-demand
3. **Virtualization**: For admin views with many sessions
4. **Debouncing**: Debounce session ID changes

```typescript
import { useEffect, useState, useCallback } from 'react';
import debounce from 'lodash/debounce';

function useGraphData(sessionId?: string) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchGraph = useCallback(
    debounce(async (sid?: string) => {
      setLoading(true);
      const url = sid ? `/api/graph/execution/${sid}` : '/api/graph/structure';
      const response = await fetch(url);
      const graphData = await response.json();
      setData(graphData);
      setLoading(false);
    }, 300),
    []
  );

  useEffect(() => {
    fetchGraph(sessionId);
  }, [sessionId, fetchGraph]);

  return { data, loading };
}
```

---

## Testing the API

```bash
# 1. Get static graph
curl http://localhost:8000/api/graph/structure | jq

# 2. Get execution graph (replace with actual session_id)
curl http://localhost:8000/api/graph/execution/session_1759381623 | jq

# 3. Get Mermaid diagram
curl http://localhost:8000/api/graph/mermaid | jq -r '.diagram'
```

---

## Summary

✅ **Backend returns structured JSON** (nodes & edges)  
✅ **Frontend has full control** over rendering  
✅ **Multiple visualization options** (React Flow, D3, Cytoscape, Mermaid)  
✅ **Execution state overlaid** for specific sessions  
✅ **Rich metadata** for styling and interaction  
✅ **Performance optimized** with caching and lazy loading  

The frontend can now:
- Display static agent architecture
- Show execution paths for specific conversations
- Highlight which nodes were executed
- Show timing and performance data
- Create interactive, zoomable, pannable graphs
- Style nodes and edges based on execution state

