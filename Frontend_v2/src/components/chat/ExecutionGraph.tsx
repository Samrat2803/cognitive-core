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

        // Transform to React Flow format with enhanced display
        const flowNodes: Node[] = data.nodes.map((node, index) => {
          const executed = node.execution?.executed ?? false;
          const hasError = node.execution?.status === 'error';
          const durationMs = node.execution?.duration_ms || 0;
          const durationSec = durationMs > 0 ? (durationMs / 1000).toFixed(2) : null;
          
          return {
            id: node.id,
            type: node.type === 'decision' ? 'default' : 'default',
            data: {
              label: (
                <div className="node-content">
                  <div className="node-label">
                    {node.label}
                    {node.metadata.llm_used && (
                      <span className="node-badge llm-badge">🧠 LLM</span>
                    )}
                  </div>
                  {executed && durationSec && (
                    <div className="node-duration">{durationSec}s</div>
                  )}
                  {!executed && (
                    <div className="node-status-badge skipped">Skipped</div>
                  )}
                  {hasError && (
                    <div className="node-status-badge error">Error</div>
                  )}
                </div>
              ),
              nodeData: node, // Store full node data for details panel
            },
            position: calculatePosition(node, index, data.nodes.length),
            style: {
              background: getNodeColor(node, executed, hasError),
              border: getNodeBorderColor(node, executed, hasError),
              borderRadius: '10px',
              padding: '14px 18px',
              fontSize: '13px',
              fontWeight: executed ? '600' : '400',
              opacity: executed ? 1 : 0.35,
              minWidth: '180px',
              maxWidth: '220px',
              color: executed ? '#1f2937' : '#6b7280',
              cursor: executed ? 'pointer' : 'default',
              boxShadow: executed 
                ? hasError 
                  ? '0 2px 8px rgba(239, 68, 68, 0.15)'
                  : '0 2px 12px rgba(0, 0, 0, 0.08)'
                : 'none',
              transition: 'all 0.2s ease',
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

      {/* Enhanced Legend */}
      <div className="execution-legend">
        <div className="legend-section">
          <strong style={{ fontSize: '12px', color: '#6b7280', marginRight: '16px' }}>Node Types:</strong>
          <div className="legend-item">
            <div className="legend-indicator" style={{ background: '#dbeafe', borderColor: '#3b82f6' }} />
            <span>Conversation</span>
          </div>
          <div className="legend-item">
            <div className="legend-indicator" style={{ background: '#f3e8ff', borderColor: '#a855f7' }} />
            <span>🧠 AI Decision</span>
          </div>
          <div className="legend-item">
            <div className="legend-indicator" style={{ background: '#d1fae5', borderColor: '#10b981' }} />
            <span>Tool Execution</span>
          </div>
          <div className="legend-item">
            <div className="legend-indicator" style={{ background: '#fef3c7', borderColor: '#eab308' }} />
            <span>Gate/Check</span>
          </div>
        </div>
        <div className="legend-section">
          <strong style={{ fontSize: '12px', color: '#6b7280', marginRight: '16px' }}>Status:</strong>
          <div className="legend-item">
            <div className="legend-indicator edge-traversed" />
            <span>Executed Path</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Get color for node based on type and state
function getNodeColor(node: GraphNode, executed: boolean, hasError: boolean): string {
  if (hasError) return '#fef2f2'; // Red tint for errors
  if (!executed) return '#f9fafb'; // Light gray for not executed
  
  // Color by node type
  const nodeId = node.id.toLowerCase();
  if (nodeId.includes('conversation') || nodeId.includes('manager')) {
    return '#dbeafe'; // Blue for conversation
  } else if (nodeId.includes('planner') || nodeId.includes('decision') || nodeId.includes('artifact')) {
    return '#f3e8ff'; // Purple for AI/LLM decisions
  } else if (nodeId.includes('executor') || nodeId.includes('tool')) {
    return '#d1fae5'; // Green for execution
  } else if (nodeId.includes('synthesizer') || nodeId.includes('response')) {
    return '#fae8ff'; // Pink for response generation
  } else if (nodeId.includes('gate')) {
    return '#fef3c7'; // Yellow for gates/checks
  }
  
  return '#d1fae5'; // Default green
}

// Get border color for node
function getNodeBorderColor(node: GraphNode, executed: boolean, hasError: boolean): string {
  if (hasError) return '2px solid #ef4444';
  if (!executed) return '1.5px solid #e5e7eb';
  
  const nodeId = node.id.toLowerCase();
  if (nodeId.includes('conversation')) return '2px solid #3b82f6';
  if (nodeId.includes('planner') || node.metadata.llm_used) return '2px solid #a855f7';
  if (nodeId.includes('executor') || nodeId.includes('tool')) return '2px solid #10b981';
  if (nodeId.includes('gate')) return '2px solid #eab308';
  
  return '2px solid #10b981';
}

// Calculate node positions in a more horizontal layout
function calculatePosition(node: GraphNode, index: number, total: number) {
  const HORIZONTAL_SPACING = 240;
  const VERTICAL_SPACING = 140;
  
  // Horizontal-first layout for better space usage
  const layers: { [key: string]: { layer: number; position: number } } = {
    '__start__': { layer: 0, position: 1 },
    'conversation_manager': { layer: 1, position: 0 },
    'strategic_planner': { layer: 1, position: 1 },
    'tool_executor': { layer: 1, position: 2 },
    'decision_gate': { layer: 2, position: 0 },
    'response_synthesizer': { layer: 2, position: 1 },
    'artifact_decision': { layer: 2, position: 2 },
    'artifact_creator': { layer: 3, position: 2 },
    '__end__': { layer: 3, position: 0 },
  };

  const layout = layers[node.id] || { layer: Math.floor(index / 3), position: index % 3 };

  return {
    x: layout.position * HORIZONTAL_SPACING + 100,
    y: layout.layer * VERTICAL_SPACING + 50,
  };
}

