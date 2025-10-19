import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { ArrowLeft, Play, Download, Archive, ExternalLink, ChevronRight, ChevronDown, Square } from 'lucide-react';
import { Markdown } from '../components/ui/Markdown';
import type { Investigation } from './InvestigationsPage';
import './InvestigationDetailPage.css';

// Log Entry Interface
interface LogEntry {
  timestamp: string;
  type: string;
  message: string;
}

// Investigation Graph Data Structure
interface QuestionNode {
  id: string;
  question: string;
  status: 'answered' | 'exploring' | 'pending';
  answer?: string;
  children?: QuestionNode[];
}

// Hypothesis Data Structure
interface Hypothesis {
  id: string;
  statement: string;
  status: 'confirmed' | 'exploring' | 'rejected' | 'pending';
  confidence: number;
  evidence: string[];
}

// Extract URLs from sources (with error handling)
const extractUrls = (investigation: Investigation) => {
  const urls = new Set<string>();
  investigation.facts.forEach(fact => {
    fact.sources.forEach(source => {
      try {
        new URL(source);
        urls.add(source);
      } catch (e) {
        console.warn(`Invalid URL skipped: ${source}`);
      }
    });
  });
  return Array.from(urls);
};

// Build question tree from flat array of questions (for initial load from REST API)
const buildQuestionTreeFromArray = (questions: any[]): QuestionNode | null => {
  if (!questions || questions.length === 0) return null;
  
  // Group questions by hypothesis_id
  const generalQuestions = questions.filter(q => q.hypothesis_id === 'general');
  const hypothesisGroups: Record<string, any[]> = {};
  
  questions.forEach(q => {
    if (q.hypothesis_id !== 'general') {
      if (!hypothesisGroups[q.hypothesis_id]) {
        hypothesisGroups[q.hypothesis_id] = [];
      }
      hypothesisGroups[q.hypothesis_id].push(q);
    }
  });
  
  // Build tree structure
  const children: QuestionNode[] = [];
  
  // Add general questions
  generalQuestions.forEach(q => {
    children.push({
      id: q.id || Math.random().toString(36),
      question: q.question,
      status: q.status === 'answered' ? 'answered' : 
              q.status === 'exploring' ? 'exploring' : 'pending',
      answer: q.answer,
      children: []
    });
  });
  
  // Add hypothesis branches
  Object.entries(hypothesisGroups).forEach(([hypId, questions]) => {
    children.push({
      id: hypId,
      question: `Hypothesis ${hypId} Questions`,
      status: 'exploring' as const,
      children: questions.map(q => ({
        id: q.id || Math.random().toString(36),
        question: q.question,
        status: q.status === 'answered' ? 'answered' : 
                q.status === 'exploring' ? 'exploring' : 'pending',
        answer: q.answer,
        children: []
      }))
    });
  });
  
  return {
    id: 'root',
    question: 'Investigation Questions',
    status: 'exploring' as const,
    children
  };
};

// Question Tree Node Component
function QuestionTreeNode({ node, level = 0 }: { node: QuestionNode; level?: number }) {
  const [expanded, setExpanded] = useState(true);
  const hasChildren = node.children && node.children.length > 0;
  const isRoot = level === 0;

  return (
    <div className="question-node" style={{ marginLeft: isRoot ? '0px' : `${(level - 1) * 20 + 20}px` }}>
      <div className="question-content">
        {!isRoot && hasChildren && (
          <button 
            className="expand-button" 
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          </button>
        )}
        <div className="question-text">
          <div className="question-title">{node.question}</div>
          {node.answer && <div className="question-answer">{node.answer}</div>}
        </div>
      </div>
      {hasChildren && expanded && (
        <div className="question-children">
          {node.children!.map(child => (
            <QuestionTreeNode key={child.id} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

// Hypothesis Board Component
function HypothesisBoard({ hypotheses }: { hypotheses: Hypothesis[] }) {
  const statusIcons = {
    confirmed: '✅',
    exploring: '🔍',
    rejected: '❌',
    pending: '⏳'
  };

  const statusLabels = {
    confirmed: 'Confirmed',
    exploring: 'Exploring',
    rejected: 'Rejected',
    pending: 'Pending'
  };

  return (
    <div className="hypothesis-board">
      <h3 className="board-title">Hypotheses Being Tested</h3>
      <div className="hypotheses-list">
        {hypotheses.map(hyp => (
          <div key={hyp.id} className={`hypothesis-card hypothesis-${hyp.status}`}>
            <div className="hypothesis-main">
              <div className="hypothesis-statement">{hyp.statement}</div>
              <div className="hypothesis-status-group">
                <span className="hypothesis-icon">{statusIcons[hyp.status]}</span>
                <span className="hypothesis-status">{statusLabels[hyp.status]}</span>
              </div>
            </div>
            {hyp.evidence.length > 0 && (
              <div className="hypothesis-evidence">
                {hyp.evidence.map((ev, idx) => (
                  <div key={idx} className="evidence-item">• {ev}</div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Left Panel - Investigation Graph + Chat
function InvestigationGraphPanel({ 
  investigation,
  questionGraph,
  hypotheses,
  onSendMessage
}: { 
  investigation: Investigation;
  questionGraph: QuestionNode | null;
  hypotheses: Hypothesis[];
  onSendMessage: (message: string) => void;
}) {
  const [activeView, setActiveView] = useState<'graph' | 'hypotheses'>('graph');
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    onSendMessage(input);
    setInput('');
  };

  return (
    <div className="investigation-graph-panel">
      {/* Tabs for Graph vs Hypotheses */}
      <div className="graph-tabs">
        <button
          className={`graph-tab ${activeView === 'graph' ? 'active' : ''}`}
          onClick={() => setActiveView('graph')}
        >
          🗺️ Question Flow
        </button>
        <button
          className={`graph-tab ${activeView === 'hypotheses' ? 'active' : ''}`}
          onClick={() => setActiveView('hypotheses')}
        >
          💡 Hypotheses ({hypotheses.length})
        </button>
      </div>

      {/* Content Area - Scrollable */}
      <div className="graph-content-scrollable">
        {activeView === 'graph' ? (
          <div className="question-tree">
            {questionGraph ? (
              <QuestionTreeNode node={questionGraph} />
            ) : (
              <div className="empty-graph">
                <p>Question flow tree will appear here as the investigation progresses...</p>
              </div>
            )}
          </div>
        ) : (
          hypotheses.length > 0 ? (
            <HypothesisBoard hypotheses={hypotheses} />
          ) : (
            <div className="empty-hypotheses">
              <p>Hypotheses will appear here as they are developed...</p>
            </div>
          )
        )}
      </div>

      {/* Chat Input at Bottom - Sticky */}
      <div className="graph-chat-input-sticky">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Continue investigation, ask follow-up questions..."
          className="chat-input"
        />
        <button onClick={handleSend} className="chat-send-button">
          Send
        </button>
      </div>
    </div>
  );
}

// Evidence Panel Component (right side) - Article, Logs, Evidence tabs
function InvestigationEvidencePanel({ 
  investigation,
  logs
}: { 
  investigation: Investigation;
  logs: LogEntry[];
}) {
  const [activeTab, setActiveTab] = useState<'logs' | 'article' | 'evidence'>('logs');
  const urls = extractUrls(investigation);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logs to bottom
  useEffect(() => {
    if (activeTab === 'logs') {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, activeTab]);

  return (
    <div className="investigation-evidence-panel">
      {/* Tabs - Article, Logs, Evidence */}
      <div className="evidence-tabs">
        <button
          className={`evidence-tab ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          <span className="tab-icon">📋</span>
          <span className="tab-label">Logs</span>
          <span className="tab-count">{logs.length}</span>
        </button>
        <button
          className={`evidence-tab ${activeTab === 'article' ? 'active' : ''}`}
          onClick={() => setActiveTab('article')}
        >
          <span className="tab-icon">📄</span>
          <span className="tab-label">Article</span>
        </button>
        <button
          className={`evidence-tab ${activeTab === 'evidence' ? 'active' : ''}`}
          onClick={() => setActiveTab('evidence')}
        >
          <span className="tab-icon">🔍</span>
          <span className="tab-label">Evidence</span>
          <span className="tab-count">
            {investigation.entities.length + investigation.facts.length + investigation.connections.length}
          </span>
        </button>
      </div>

      {/* Content */}
      <div className="evidence-content">
        {activeTab === 'logs' && (
          <div className="logs-view">
            {logs.length === 0 ? (
              <div className="empty-logs">
                <p>No logs yet. Click "Start Investigation" to begin.</p>
              </div>
            ) : (
              <>
                {logs.map((log, idx) => (
                  <div key={idx} className={`log-entry log-${log.type}`}>
                    <span className="log-timestamp">{log.timestamp}</span>
                    <span className="log-type">{log.type}</span>
                    <span className="log-message">{log.message}</span>
                  </div>
                ))}
                <div ref={logsEndRef} />
              </>
            )}
          </div>
        )}

        {activeTab === 'article' && (
          <div className="article-view">
            {investigation.article ? (
              <Markdown>{investigation.article}</Markdown>
            ) : (
              <div className="empty-article">
                <p>Article will be generated as the investigation progresses...</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'evidence' && (
          <div className="evidence-view">
            {/* URLs Section */}
            {urls.length > 0 && (
              <div className="evidence-section">
                <h3 className="section-title">
                  <span className="section-icon">🔗</span>
                  Sources & URLs
                  <span className="section-count">{urls.length}</span>
                </h3>
                <div className="urls-grid">
                  {urls.map((url, idx) => {
                    let hostname = url;
                    try {
                      hostname = new URL(url).hostname;
                    } catch (e) {
                      // Use full URL if parsing fails
                    }
                    return (
                      <a
                        key={idx}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="url-card"
                      >
                        <span className="url-icon">
                          <ExternalLink size={14} />
                        </span>
                        <span className="url-text">{hostname}</span>
                      </a>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Key Findings (from facts) */}
            {investigation.facts.length > 0 && (
              <div className="evidence-section">
                <h3 className="section-title">
                  <span className="section-icon">📊</span>
                  Key Findings
                  <span className="section-count">{investigation.facts.length}</span>
                </h3>
                <div className="findings-list">
                  {investigation.facts.map((fact) => (
                    <div key={fact.id} className="finding-item">
                      <div className="finding-header">
                        <span className="finding-id">#{fact.id}</span>
                      </div>
                      <p className="finding-content">{fact.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Entities */}
            {investigation.entities.length > 0 && (
              <div className="evidence-section">
                <h3 className="section-title">
                  <span className="section-icon">👥</span>
                  Entities Discovered
                  <span className="section-count">{investigation.entities.length}</span>
                </h3>
                <div className="entities-compact">
                  {investigation.entities.map((entity, idx) => (
                    <div key={idx} className="entity-chip">
                      <span className={`entity-badge type-${entity.type}`}>
                        {entity.type}
                      </span>
                      <span className="entity-name-compact">{entity.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Connections */}
            {investigation.connections.length > 0 && (
              <div className="evidence-section">
                <h3 className="section-title">
                  <span className="section-icon">🔗</span>
                  Connections Mapped
                  <span className="section-count">{investigation.connections.length}</span>
                </h3>
                <div className="connections-compact">
                  {investigation.connections.map((conn, idx) => (
                    <div key={idx} className="connection-row">
                      <span className="connection-node-compact">{conn.from}</span>
                      <span className="connection-type-compact">{conn.type}</span>
                      <span className="connection-node-compact">{conn.to}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {urls.length === 0 && investigation.facts.length === 0 && 
             investigation.entities.length === 0 && investigation.connections.length === 0 && (
              <div className="empty-evidence">
                <p>Evidence will appear here as it is discovered during the investigation...</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export function InvestigationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [questionGraph, setQuestionGraph] = useState<QuestionNode | null>(null);
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([]);
  const [showContinueModal, setShowContinueModal] = useState(false);
  const [continueForm, setContinueForm] = useState({
    additionalIterations: 5,
    customInstructions: '',
    newHypothesis: '',
    newQuestion: ''
  });
  const wsRef = useRef<WebSocket | null>(null);

  // Fetch investigation data
  useEffect(() => {
    const fetchInvestigation = async () => {
      if (!id) {
        setLoading(false);
        return;
      }
      
      try {
        const response = await fetch(`http://localhost:8000/api/investigations/${id}`);
        
        if (!response.ok) {
          console.error('Failed to fetch investigation:', response.status);
          setInvestigation(null);
          setLoading(false);
          return;
        }
        
        const result = await response.json();
        
        if (result.success && result.data) {
          const backendData = result.data;
          
          const transformed: Investigation = {
            id: backendData.investigation_id,
            title: backendData.title,
            query: backendData.query,
            status: backendData.status,
            article: backendData.article || '',
            cost: backendData.cost_usd || 0,
            phase: backendData.phase || 'initial',
            progress: {
              current: backendData.current_iteration || 0,
              max: backendData.max_iterations || 20
            },
            currentIteration: backendData.current_iteration || 0,
            maxIterations: backendData.max_iterations || 20,
            createdAt: backendData.created_at,
            updatedAt: backendData.updated_at,
            completedAt: backendData.completed_at,
            entities: (backendData.entities || []).map((e: any) => ({
              type: e.type || 'unknown',
              name: e.name || '',
              description: e.description || ''
            })),
            facts: (backendData.facts || []).map((f: any) => ({
              id: f.id || Math.random().toString(36),
              content: f.content || f.fact || '',
              sources: f.sources || []
            })),
            connections: (backendData.connections || []).map((c: any) => ({
              from: c.from || c.source || '',
              to: c.to || c.target || '',
              type: c.type || c.relationship || 'related'
            })),
            anomalies: backendData.anomalies || []
          };
          
          setInvestigation(transformed);
          setIsRunning(backendData.status === 'running');
          
          // Load questions from REST API (for revisiting investigations)
          if (backendData.questions && backendData.questions.length > 0) {
            console.log('📊 Loading', backendData.questions.length, 'questions from REST API');
            const tree = buildQuestionTreeFromArray(backendData.questions);
            setQuestionGraph(tree);
          }
          
          // Load hypotheses from REST API (for revisiting investigations)
          if (backendData.hypotheses && backendData.hypotheses.length > 0) {
            console.log('💡 Loading', backendData.hypotheses.length, 'hypotheses from REST API');
            setHypotheses(backendData.hypotheses.map((h: any) => ({
              id: h.id || Math.random().toString(36),
              statement: h.statement || '',
              status: h.status || 'pending',
              confidence: h.confidence || 0.0,
              evidence: h.evidence || []
            })));
          }
        } else {
          setInvestigation(null);
        }
      } catch (error) {
        console.error('Error fetching investigation:', error);
        setInvestigation(null);
      } finally {
        setLoading(false);
      }
    };
    
    fetchInvestigation();
  }, [id]);

  // Shared WebSocket message handler (used by both start and continue)
  const handleWebSocketMessage = (message: any) => {
    console.log('WebSocket message:', message);
    
    const msgType = message.type;
    const data = message.data || {};
    
    // Handle different message types from backend
    switch (msgType) {
      case 'log':
        // Real-time log streaming from backend stdout
        setLogs(prev => [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          type: 'info',
          message: data.message
        }]);
        break;
        
      case 'hypothesis_updated':
        // New hypothesis discovered
        console.log('🎯 HYPOTHESIS RECEIVED:', data);
        setHypotheses(prev => [...prev, {
          id: data.id || Math.random().toString(36),
          statement: data.statement || '',
          status: data.status || 'pending',
          confidence: data.confidence || 0.0,
          evidence: []
        }]);
        setLogs(prev => [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          type: 'hypothesis',
          message: `💡 Hypothesis: ${data.statement?.substring(0, 80)}...`
        }]);
        break;
        
      case 'question_discovered':
        // New question discovered - build question tree
        console.log('❓ QUESTION RECEIVED:', data);
        console.log('   Question ID:', data.id);
        console.log('   Hypothesis ID:', data.hypothesis_id);
        console.log('   Question text:', data.question);
        
        setLogs(prev => [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          type: 'info',
          message: `❓ Question: ${data.question?.substring(0, 80)}...`
        }]);
        
        // Build question tree structure
        const newQuestion: QuestionNode = {
          id: data.id || Math.random().toString(36),
          question: data.question || '',
          status: data.status === 'answered' ? 'answered' : 
                  data.status === 'exploring' ? 'exploring' : 'pending',
          answer: data.answer,
          children: []
        };
        
        console.log('   Adding question to tree:', newQuestion.id);
        
        // If this is a root question (hypothesis_id === 'general'), add to tree
        // Otherwise, find parent hypothesis and add under it
        if (data.hypothesis_id === 'general') {
          setQuestionGraph(prev => {
            console.log('   Adding to general questions. Current tree:', prev);
            if (!prev) {
              // First question becomes root
              const newTree = {
                id: 'root',
                question: 'Investigation Questions',
                status: 'exploring' as const,
                children: [newQuestion]
              };
              console.log('   Created new tree:', newTree);
              return newTree;
            } else {
              // Add to existing root
              const updatedTree = {
                ...prev,
                children: [...(prev.children || []), newQuestion]
              };
              console.log('   Updated tree:', updatedTree);
              return updatedTree;
            }
          });
        } else {
          setQuestionGraph(prev => {
            console.log(`   Adding to hypothesis ${data.hypothesis_id}. Current tree:`, prev);
            if (!prev) {
              return {
                id: 'root',
                question: 'Investigation Questions',
                status: 'exploring' as const,
                children: [{
                  id: data.hypothesis_id,
                  question: `Hypothesis ${data.hypothesis_id} Questions`,
                  status: 'exploring' as const,
                  children: [newQuestion]
                }]
              };
            }
            
            // Find or create hypothesis branch
            const children = prev.children || [];
            const hypBranch = children.find(c => c.id === data.hypothesis_id);
            
            if (hypBranch) {
              // Add to existing hypothesis branch
              console.log(`   Found existing branch for ${data.hypothesis_id}`);
              return {
                ...prev,
                children: children.map(c => 
                  c.id === data.hypothesis_id 
                    ? { ...c, children: [...(c.children || []), newQuestion] }
                    : c
                )
              };
            } else {
              // Create new hypothesis branch
              console.log(`   Creating new branch for ${data.hypothesis_id}`);
              return {
                ...prev,
                children: [...children, {
                  id: data.hypothesis_id,
                  question: `Hypothesis ${data.hypothesis_id} Questions`,
                  status: 'exploring' as const,
                  children: [newQuestion]
                }]
              };
            }
          });
        }
        console.log('   Question tree update complete');
        break;
        
      case 'connected':
        setLogs(prev => [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          type: 'success',
          message: `📡 Connected to investigation: ${data.title}`
        }]);
        break;
        
      case 'investigation_started':
        setLogs(prev => [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          type: 'info',
          message: `🚀 Investigation started: "${data.query}"`
        }]);
        break;
        
      case 'entity_discovered':
        if (investigation) {
          setInvestigation({
            ...investigation,
            entities: [...investigation.entities, {
              type: data.type || 'unknown',
              name: data.name || '',
              description: data.description || ''
            }]
          });
        }
        break;
        
      case 'fact_recorded':
        if (investigation) {
          setInvestigation({
            ...investigation,
            facts: [...investigation.facts, {
              id: Math.random().toString(36),
              content: data.content || '',
              sources: data.sources || []
            }]
          });
        }
        break;
        
      case 'article_updated':
        if (investigation) {
          setInvestigation({
            ...investigation,
            article: data.article || ''
          });
        }
        break;
        
      case 'investigation_complete':
        setIsRunning(false);
        setLogs(prev => [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          type: 'success',
          message: `✅ Investigation complete! Total cost: $${data.total_cost?.toFixed(3) || '0.000'}`
        }]);
        if (investigation) {
          setInvestigation({
            ...investigation,
            status: 'completed',
            article: data.article || investigation.article,
            cost: data.total_cost || investigation.cost
          });
        }
        break;
        
      case 'error':
        setIsRunning(false);
        setLogs(prev => [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          type: 'error',
          message: `❌ Error: ${data.message || 'Unknown error'}`
        }]);
        break;
        
      default:
        // For any other message types, just log them
        if (data.message) {
          setLogs(prev => [...prev, {
            timestamp: new Date().toLocaleTimeString(),
            type: 'info',
            message: data.message
          }]);
        }
    }
  };

  // WebSocket connection for real-time updates
  const startInvestigation = () => {
    if (!id || isRunning) return;
    
    setIsRunning(true);
    setLogs([{ timestamp: new Date().toLocaleTimeString(), type: 'info', message: '🚀 Starting investigation...' }]);
    
    const ws = new WebSocket(`ws://localhost:8000/ws/investigations/${id}`);
    wsRef.current = ws;
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setLogs(prev => [...prev, { 
        timestamp: new Date().toLocaleTimeString(), 
        type: 'success', 
        message: '✅ Connected to server' 
      }]);
      
      // Send start message to trigger investigation
      ws.send(JSON.stringify({ type: 'start' }));
      console.log('Sent start message to server');
    };
    
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('WebSocket message:', message);
        
        const msgType = message.type;
        const data = message.data || {};
        
        // Handle different message types from backend
        switch (msgType) {
          case 'log':
            // Real-time log streaming from backend stdout
            setLogs(prev => [...prev, {
              timestamp: new Date().toLocaleTimeString(),
              type: 'info',
              message: data.message
            }]);
            break;
            
          case 'hypothesis_updated':
            // New hypothesis discovered
            console.log('🎯 HYPOTHESIS RECEIVED:', data);
            setHypotheses(prev => [...prev, {
              id: data.id || Math.random().toString(36),
              statement: data.statement || '',
              status: data.status || 'pending',
              confidence: data.confidence || 0.0,
              evidence: []
            }]);
            setLogs(prev => [...prev, {
              timestamp: new Date().toLocaleTimeString(),
              type: 'hypothesis',
              message: `💡 Hypothesis: ${data.statement?.substring(0, 80)}...`
            }]);
            break;
            
          case 'question_discovered':
            // New question discovered - build question tree
            console.log('❓ QUESTION RECEIVED:', data);
            console.log('   Question ID:', data.id);
            console.log('   Hypothesis ID:', data.hypothesis_id);
            console.log('   Question text:', data.question);
            
            setLogs(prev => [...prev, {
              timestamp: new Date().toLocaleTimeString(),
              type: 'info',
              message: `❓ Question: ${data.question?.substring(0, 80)}...`
            }]);
            
            // Build question tree structure
            const newQuestion: QuestionNode = {
              id: data.id || Math.random().toString(36),
              question: data.question || '',
              status: data.status === 'answered' ? 'answered' : 
                      data.status === 'exploring' ? 'exploring' : 'pending',
              answer: data.answer,
              children: []
            };
            
            console.log('   Adding question to tree:', newQuestion.id);
            
            // If this is a root question (hypothesis_id === 'general'), add to tree
            // Otherwise, find parent hypothesis and add under it
            if (data.hypothesis_id === 'general') {
              setQuestionGraph(prev => {
                console.log('   Adding to general questions. Current tree:', prev);
                if (!prev) {
                  // First question becomes root
                  const newTree = {
                    id: 'root',
                    question: 'Investigation Questions',
                    status: 'exploring' as const,
                    children: [newQuestion]
                  };
                  console.log('   Created new tree:', newTree);
                  return newTree;
                } else {
                  // Add to existing root
                  const updatedTree = {
                    ...prev,
                    children: [...(prev.children || []), newQuestion]
                  };
                  console.log('   Updated tree:', updatedTree);
                  return updatedTree;
                }
              });
            } else {
              setQuestionGraph(prev => {
                console.log(`   Adding to hypothesis ${data.hypothesis_id}. Current tree:`, prev);
                if (!prev) {
                  return {
                    id: 'root',
                    question: 'Investigation Questions',
                    status: 'exploring' as const,
                    children: [{
                      id: data.hypothesis_id,
                      question: `Hypothesis ${data.hypothesis_id} Questions`,
                      status: 'exploring' as const,
                      children: [newQuestion]
                    }]
                  };
                }
                
                // Find or create hypothesis branch
                const children = prev.children || [];
                const hypBranch = children.find(c => c.id === data.hypothesis_id);
                
                if (hypBranch) {
                  // Add to existing hypothesis branch
                  console.log(`   Found existing branch for ${data.hypothesis_id}`);
                  return {
                    ...prev,
                    children: children.map(c => 
                      c.id === data.hypothesis_id 
                        ? { ...c, children: [...(c.children || []), newQuestion] }
                        : c
                    )
                  };
                } else {
                  // Create new hypothesis branch
                  console.log(`   Creating new branch for ${data.hypothesis_id}`);
                  return {
                    ...prev,
                    children: [...children, {
                      id: data.hypothesis_id,
                      question: `Hypothesis ${data.hypothesis_id} Questions`,
                      status: 'exploring' as const,
                      children: [newQuestion]
                    }]
                  };
                }
              });
            }
            console.log('   Question tree update complete');
            break;
            
          case 'connected':
            setLogs(prev => [...prev, {
              timestamp: new Date().toLocaleTimeString(),
              type: 'success',
              message: `📡 Connected to investigation: ${data.title}`
            }]);
            break;
            
          case 'investigation_started':
            setLogs(prev => [...prev, {
              timestamp: new Date().toLocaleTimeString(),
              type: 'info',
              message: `🚀 Investigation started: "${data.query}"`
            }]);
            break;
            
          case 'entity_discovered':
            if (investigation) {
              setInvestigation({
                ...investigation,
                entities: [...investigation.entities, {
                  type: data.type || 'unknown',
                  name: data.name || '',
                  description: data.description || ''
                }]
              });
            }
            break;
            
          case 'fact_recorded':
            if (investigation) {
              setInvestigation({
                ...investigation,
                facts: [...investigation.facts, {
                  id: Math.random().toString(36),
                  content: data.content || '',
                  sources: data.sources || []
                }]
              });
            }
            break;
            
          case 'article_updated':
            if (investigation) {
              setInvestigation({
                ...investigation,
                article: data.article || ''
              });
            }
            break;
            
          case 'investigation_complete':
            setIsRunning(false);
            setLogs(prev => [...prev, {
              timestamp: new Date().toLocaleTimeString(),
              type: 'success',
              message: `✅ Investigation complete! Total cost: $${data.total_cost?.toFixed(3) || '0.000'}`
            }]);
            if (investigation) {
              setInvestigation({
                ...investigation,
                status: 'completed',
                article: data.article || investigation.article,
                cost: data.total_cost || investigation.cost
              });
            }
            break;
            
          case 'error':
            setIsRunning(false);
            setLogs(prev => [...prev, {
              timestamp: new Date().toLocaleTimeString(),
              type: 'error',
              message: `❌ Error: ${data.message || 'Unknown error'}`
            }]);
            break;
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setLogs(prev => [...prev, {
        timestamp: new Date().toLocaleTimeString(),
        type: 'error',
        message: '❌ Connection error'
      }]);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsRunning(false);
      setLogs(prev => [...prev, {
        timestamp: new Date().toLocaleTimeString(),
        type: 'info',
        message: '🔌 Disconnected from server'
      }]);
    };
  };

  const stopInvestigation = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsRunning(false);
  };

  const continueInvestigation = async () => {
    if (!id) return;
    
    try {
      // Update max_iterations via REST API
      const response = await fetch(`http://localhost:8000/api/investigations/${id}/continue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ additional_iterations: continueForm.additionalIterations })
      });
      
      if (!response.ok) {
        throw new Error('Failed to continue investigation');
      }
      
      setShowContinueModal(false);
      
      // Now start the investigation via WebSocket
      setIsRunning(true);
      setLogs([{ timestamp: new Date().toLocaleTimeString(), type: 'info', message: '🔄 Continuing investigation...' }]);
      
      const ws = new WebSocket(`ws://localhost:8000/ws/investigations/${id}`);
      wsRef.current = ws;
      
      ws.onopen = () => {
        console.log('WebSocket connected for continuation');
        setLogs(prev => [...prev, { 
          timestamp: new Date().toLocaleTimeString(), 
          type: 'success', 
          message: '✅ Connected to server' 
        }]);
        
        // Send start message WITH additional context (instructions, hypothesis, question)
        const startMessage: any = { type: 'start' };
        
        // Add user guidance if provided
        if (continueForm.customInstructions) {
          startMessage.instructions = continueForm.customInstructions;
          setLogs(prev => [...prev, {
            timestamp: new Date().toLocaleTimeString(),
            type: 'info',
            message: `📝 Custom instructions: ${continueForm.customInstructions}`
          }]);
        }
        
        if (continueForm.newHypothesis) {
          startMessage.suggested_hypothesis = continueForm.newHypothesis;
          setLogs(prev => [...prev, {
            timestamp: new Date().toLocaleTimeString(),
            type: 'info',
            message: `💡 Suggested hypothesis: ${continueForm.newHypothesis}`
          }]);
        }
        
        if (continueForm.newQuestion) {
          startMessage.suggested_question = continueForm.newQuestion;
          setLogs(prev => [...prev, {
            timestamp: new Date().toLocaleTimeString(),
            type: 'info',
            message: `❓ Suggested question: ${continueForm.newQuestion}`
          }]);
        }
        
        ws.send(JSON.stringify(startMessage));
        console.log('Sent continue message with context:', startMessage);
      };
      
      // Reuse the same message handlers from startInvestigation
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsRunning(false);
        setLogs(prev => [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          type: 'error',
          message: '❌ Connection error'
        }]);
      };
      
      ws.onclose = () => {
        console.log('WebSocket closed');
        setIsRunning(false);
        setLogs(prev => [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          type: 'info',
          message: '🔌 Disconnected from server'
        }]);
      };
      
      // Reset form
      setContinueForm({
        additionalIterations: 5,
        customInstructions: '',
        newHypothesis: '',
        newQuestion: ''
      });
      
    } catch (error) {
      console.error('Error continuing investigation:', error);
      alert('Failed to continue investigation. Please try again.');
    }
  };

  const handleSendMessage = (message: string) => {
    // In the future, this will send messages to continue the investigation
    console.log('User message:', message);
    setLogs(prev => [...prev, {
      timestamp: new Date().toLocaleTimeString(),
      type: 'user',
      message: `💬 You: ${message}`
    }]);
  };

  if (loading) {
    return (
      <div className="investigation-detail-page">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading investigation...</div>
        </div>
      </div>
    );
  }

  if (!investigation) {
    return (
      <div className="investigation-detail-page">
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h3>Investigation Not Found</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="investigation-detail-page">
      {/* Header */}
      <header className="investigation-header">
        <div className="header-left">
          <button className="back-button" onClick={() => navigate('/investigations')}>
            <ArrowLeft size={18} />
          </button>
          <div className="header-info">
            <h1 className="header-title">{investigation.title}</h1>
            <div className="header-meta">
              {/* Show meaningful status based on actual state */}
              <span className={`status-badge ${
                isRunning ? 'status-running' : 
                investigation.currentIteration >= investigation.maxIterations ? 'status-complete' :
                investigation.currentIteration > 0 ? 'status-in-progress' :
                'status-new'
              }`}>
                {isRunning ? 'Running' : 
                 investigation.currentIteration >= investigation.maxIterations ? 'Complete' :
                 investigation.currentIteration > 0 ? `In Progress (${investigation.currentIteration}/${investigation.maxIterations})` :
                 'New'}
              </span>
              <span className="meta-divider">•</span>
              <span className="meta-text">{investigation.entities.length} entities</span>
              <span className="meta-divider">•</span>
              <span className="meta-text">{investigation.facts.length} facts</span>
              <span className="meta-divider">•</span>
              <span className="meta-cost">${investigation.cost.toFixed(3)}</span>
            </div>
          </div>
        </div>
        <div className="header-actions">
          <button className="action-btn action-secondary" title="Archive">
            <Archive size={16} />
          </button>
          <button className="action-btn action-secondary" title="Export">
            <Download size={16} />
          </button>
          {isRunning ? (
            <button className="action-btn action-danger" onClick={stopInvestigation}>
              <Square size={16} />
              <span>Stop</span>
            </button>
          ) : investigation.currentIteration > 0 ? (
            // Investigation has run before - can continue or restart
            <>
              <button className="action-btn action-primary" onClick={() => setShowContinueModal(true)}>
                <Play size={16} />
                <span>Continue Investigation</span>
              </button>
              <button className="action-btn action-secondary" onClick={startInvestigation}>
                <Play size={16} />
                <span>Restart from Beginning</span>
              </button>
            </>
          ) : (
            // Investigation never run - only show start
            <button className="action-btn action-primary" onClick={startInvestigation}>
              <Play size={16} />
              <span>Start Investigation</span>
            </button>
          )}
        </div>
      </header>

      {/* Split Panel Layout */}
      <div className="investigation-content">
        <PanelGroup direction="horizontal">
          {/* Left Panel - Investigation Graph + Hypotheses */}
          <Panel 
            defaultSize={40} 
            minSize={30}
          >
            <InvestigationGraphPanel 
              investigation={investigation}
              questionGraph={questionGraph}
              hypotheses={hypotheses}
              onSendMessage={handleSendMessage}
            />
          </Panel>

          <PanelResizeHandle className="resize-handle">
            <div className="resize-handle-line" />
          </PanelResizeHandle>

          {/* Right Panel - Article + Logs + Evidence */}
          <Panel 
            defaultSize={60} 
            minSize={30}
          >
            <InvestigationEvidencePanel 
              investigation={investigation}
              logs={logs}
            />
          </Panel>
        </PanelGroup>
      </div>

      {/* Continue Investigation Modal */}
      {showContinueModal && (
        <div className="modal-overlay" onClick={() => setShowContinueModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Continue Investigation</h2>
              <button className="modal-close" onClick={() => setShowContinueModal(false)}>×</button>
            </div>
            
            <div className="modal-body">
              <p className="modal-description">
                Resume this investigation with additional iterations and optional guidance for the AI agent.
              </p>
              
              {/* Iteration Count Slider */}
              <div className="form-group">
                <label className="form-label">
                  Additional Iterations: <strong>{continueForm.additionalIterations}</strong>
                </label>
                <input
                  type="range"
                  min="1"
                  max="20"
                  value={continueForm.additionalIterations}
                  onChange={(e) => setContinueForm({
                    ...continueForm,
                    additionalIterations: parseInt(e.target.value)
                  })}
                  className="form-range"
                />
                <div className="range-labels">
                  <span>1</span>
                  <span>10</span>
                  <span>20</span>
                </div>
              </div>

              {/* Custom Instructions */}
              <div className="form-group">
                <label className="form-label">
                  Custom Instructions (Optional)
                  <span className="form-hint">Guide the investigation direction</span>
                </label>
                <textarea
                  value={continueForm.customInstructions}
                  onChange={(e) => setContinueForm({
                    ...continueForm,
                    customInstructions: e.target.value
                  })}
                  placeholder="e.g., Focus on financial connections, Look into regulatory violations..."
                  className="form-textarea"
                  rows={3}
                />
              </div>

              {/* Suggested Hypothesis */}
              <div className="form-group">
                <label className="form-label">
                  Suggest New Hypothesis (Optional)
                  <span className="form-hint">Propose a new angle to explore</span>
                </label>
                <input
                  type="text"
                  value={continueForm.newHypothesis}
                  onChange={(e) => setContinueForm({
                    ...continueForm,
                    newHypothesis: e.target.value
                  })}
                  placeholder="e.g., The CEO had undisclosed conflicts of interest..."
                  className="form-input"
                />
              </div>

              {/* Suggested Question */}
              <div className="form-group">
                <label className="form-label">
                  Suggest Question to Investigate (Optional)
                  <span className="form-hint">Ask a specific question</span>
                </label>
                <input
                  type="text"
                  value={continueForm.newQuestion}
                  onChange={(e) => setContinueForm({
                    ...continueForm,
                    newQuestion: e.target.value
                  })}
                  placeholder="e.g., Who were the largest donors to the campaign?"
                  className="form-input"
                />
              </div>

              {/* Cost Estimate */}
              <div className="cost-estimate">
                <span className="cost-icon">💰</span>
                <span className="cost-text">
                  Estimated additional cost: ~${(continueForm.additionalIterations * 0.06).toFixed(2)}
                </span>
              </div>
            </div>

            <div className="modal-footer">
              <button 
                className="btn btn-secondary" 
                onClick={() => setShowContinueModal(false)}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                onClick={continueInvestigation}
              >
                <Play size={16} />
                Continue Investigation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
