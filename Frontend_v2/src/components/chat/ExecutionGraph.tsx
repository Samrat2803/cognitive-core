import { useEffect, useState, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  type Node,
  type Edge,
} from 'reactflow';
import 'reactflow/dist/style.css';
import './ExecutionGraph.css';
import { config } from '../../config';

interface ExecutionGraphProps {
  sessionId: string;
}

interface GraphNode {
  id: string;
  label: string;
  type: string;
  description: string;
  metadata: {
    color: string;
    icon?: string;
    llm_used?: boolean;
  };
  execution?: {
    executed: boolean;
    timestamp?: string;
    status?: string;
    duration_ms?: number;
    details?: {
      action: string;
      input: string;
      output: string;
    };
  };
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  label?: string;
  execution?: {
    traversed: boolean;
    count?: number;
  };
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  execution_metadata?: {
    session_id: string;
    total_steps: number;
    executed_nodes: number;
    total_duration_ms: number;
    iterations: number;
  };
}

export function ExecutionGraph({ sessionId }: ExecutionGraphProps) {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  // Memoize options to prevent React Flow warnings about recreating objects
  const defaultEdgeOptions = useMemo(() => ({ animated: false }), []);
  const nodeTypes = useMemo(() => ({}), []);
  const edgeTypes = useMemo(() => ({}), []);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${config.apiUrl}/api/graph/execution/${sessionId}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch graph: ${response.statusText}`);
        }

        const data: GraphData = await response.json();
        setGraphData(data);

        // Transform to React Flow format
        const flowNodes: Node[] = data.nodes.map((node, index) => {
          const executed = node.execution?.executed ?? false;
          const hasError = node.execution?.status === 'error';
          
          return {
            id: node.id,
            type: node.type === 'decision' ? 'default' : 'default',
            data: {
              label: (
                <div className="node-content">
                  <div className="node-label">{node.label}</div>
                  {node.metadata.llm_used && (
                    <div className="node-badge">LLM</div>
                  )}
                  {executed && node.execution?.duration_ms && (
                    <div className="node-duration">{node.execution.duration_ms}ms</div>
                  )}
                </div>
              ),
              nodeData: node, // Store full node data for details panel
            },
            position: calculatePosition(node, index, data.nodes.length),
            style: {
              background: executed
                ? hasError
                  ? '#fee2e2'
                  : '#d1fae5'
                : node.metadata.color,
              border: hasError ? '2px solid #ef4444' : executed ? '2px solid #10b981' : '1px solid #ddd',
              borderRadius: '8px',
              padding: '12px 16px',
              fontSize: '13px',
              fontWeight: executed ? '600' : '400',
              opacity: executed ? 1 : 0.4,
              minWidth: '150px',
              color: executed ? '#1f2937' : '#6b7280',
              cursor: executed ? 'pointer' : 'default',
            },
          };
        });

        const flowEdges: Edge[] = data.edges.map((edge) => {
          const traversed = edge.execution?.traversed ?? false;
          
          return {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            label: edge.label,
            type: edge.type === 'conditional' ? 'smoothstep' : 'default',
            animated: traversed,
            style: {
              stroke: traversed ? '#10b981' : '#d1d5db',
              strokeWidth: traversed ? 2.5 : 1.5,
              opacity: traversed ? 1 : 0.3,
            },
            labelStyle: {
              fontSize: '11px',
              fill: traversed ? '#047857' : '#6b7280',
              fontWeight: traversed ? '600' : '400',
            },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: traversed ? '#10b981' : '#d1d5db',
            },
          };
        });

        setNodes(flowNodes);
        setEdges(flowEdges);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching execution graph:', err);
        setError(err instanceof Error ? err.message : 'Failed to load execution graph');
        setLoading(false);
      }
    };

    fetchGraph();
  }, [sessionId, setNodes, setEdges]);

  if (loading) {
    return (
      <div className="execution-graph-loading">
        <div className="loading-spinner" />
        <p>Loading execution graph...</p>
      </div>
    );
  }

  if (error) {
    const isNotFound = error.includes('Not Found') || error.includes('not found');
    return (
      <div className="execution-graph-error">
        {isNotFound ? (
          <>
            <p>⚠️ Execution data not available for this session.</p>
            <p style={{ fontSize: '12px', marginTop: '8px', opacity: 0.7 }}>
              Execution tracking is only available for new queries. Send a new message to see the execution graph!
            </p>
          </>
        ) : (
          <p>⚠️ {error}</p>
        )}
      </div>
    );
  }

  if (!graphData) {
    return <div className="execution-graph-error">No graph data available</div>;
  }

  return (
    <div className="execution-graph-container">
      {/* Metadata Header */}
      {graphData.execution_metadata && (
        <div className="execution-metadata">
          <div className="metadata-item">
            <span className="metadata-label">Nodes Executed:</span>
            <span className="metadata-value">
              {graphData.execution_metadata.executed_nodes}/{graphData.nodes.length}
            </span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Duration:</span>
            <span className="metadata-value">
              {(graphData.execution_metadata.total_duration_ms / 1000).toFixed(1)}s
            </span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Iterations:</span>
            <span className="metadata-value">
              {graphData.execution_metadata.iterations}
            </span>
          </div>
        </div>
      )}

      {/* Graph Visualization */}
      <div className="execution-graph">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={(event, node) => {
            const nodeData = (node.data as any).nodeData as GraphNode;
            if (nodeData?.execution?.executed) {
              setSelectedNode(nodeData);
            }
          }}
          fitView
          attributionPosition="bottom-right"
          minZoom={0.5}
          maxZoom={1.5}
          defaultEdgeOptions={defaultEdgeOptions}
        >
          <Background color="#f3f4f6" gap={16} />
          <Controls />
          <MiniMap
            nodeColor={(node) => {
              const style = node.style as any;
              return style?.background || '#e5e7eb';
            }}
            maskColor="rgba(0, 0, 0, 0.1)"
            style={{
              background: '#fff',
              border: '1px solid #e5e7eb',
            }}
          />
        </ReactFlow>
      </div>

      {/* Node Details Panel */}
      {selectedNode && selectedNode.execution && (
        <div className="node-details-panel">
          <div className="node-details-header">
            <h3>{selectedNode.label}</h3>
            <button 
              className="close-details-btn" 
              onClick={() => setSelectedNode(null)}
              aria-label="Close details"
            >
              ✕
            </button>
          </div>
          <div className="node-details-content">
            {selectedNode.execution.details && (
              <>
                {selectedNode.execution.details.input && (
                  <div className="detail-section">
                    <h4>Input:</h4>
                    <pre className="detail-text">{selectedNode.execution.details.input}</pre>
                  </div>
                )}
                {selectedNode.execution.details.action && (
                  <div className="detail-section">
                    <h4>Decision/Action:</h4>
                    <pre className="detail-text">{selectedNode.execution.details.action}</pre>
                  </div>
                )}
                {selectedNode.execution.details.output && (
                  <div className="detail-section">
                    <h4>Output:</h4>
                    <pre className="detail-text">{selectedNode.execution.details.output}</pre>
                  </div>
                )}
              </>
            )}
            {selectedNode.execution.timestamp && (
              <div className="detail-section">
                <h4>Timestamp:</h4>
                <p className="detail-text">{new Date(selectedNode.execution.timestamp).toLocaleString()}</p>
              </div>
            )}
            {selectedNode.execution.duration_ms && (
              <div className="detail-section">
                <h4>Duration:</h4>
                <p className="detail-text">{selectedNode.execution.duration_ms}ms</p>
              </div>
            )}
            {!selectedNode.execution.details && (
              <p className="no-details">No detailed execution information available for this node.</p>
            )}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="execution-legend">
        <div className="legend-item">
          <div className="legend-indicator executed" />
          <span>Executed</span>
        </div>
        <div className="legend-item">
          <div className="legend-indicator not-executed" />
          <span>Not Executed</span>
        </div>
        <div className="legend-item">
          <div className="legend-indicator edge-traversed" />
          <span>Path Taken</span>
        </div>
      </div>
    </div>
  );
}

// Calculate node positions in a hierarchical layout
function calculatePosition(node: GraphNode, index: number, total: number) {
  const HORIZONTAL_SPACING = 220;
  const VERTICAL_SPACING = 120;
  
  // Define layers for the master agent workflow
  const layers: { [key: string]: { layer: number; position: number } } = {
    '__start__': { layer: 0, position: 0 },
    'conversation_manager': { layer: 1, position: 0 },
    'strategic_planner': { layer: 2, position: 0 },
    'tool_executor': { layer: 3, position: 0 },
    'decision_gate': { layer: 4, position: 0 },
    'response_synthesizer': { layer: 5, position: 0 },
    'artifact_decision': { layer: 6, position: 0 },
    'artifact_creator': { layer: 7, position: 1 },
    '__end__': { layer: 7, position: -1 },
  };

  const layout = layers[node.id] || { layer: Math.floor(index / 2), position: index % 2 };

  return {
    x: layout.position * HORIZONTAL_SPACING + 100,
    y: layout.layer * VERTICAL_SPACING + 50,
  };
}

