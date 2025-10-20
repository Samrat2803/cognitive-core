import React from 'react';
import './InvestigativeJournalistStateViewer.css';

interface InvestigativeJournalistStateViewerProps {
  state: any;
}

export function InvestigativeJournalistStateViewer({ state }: InvestigativeJournalistStateViewerProps) {
  if (!state) {
    return (
      <div className="state-empty">
        <div className="empty-icon">🔍</div>
        <p>Investigation state will appear here once the investigation starts</p>
      </div>
    );
  }

  // Helper to safely render any value
  const safeRender = (value: any): string => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
      return String(value);
    }
    if (Array.isArray(value)) return `${value.length} items`;
    if (typeof value === 'object') return '[Object]';
    return 'N/A';
  };

  return (
    <div className="state-viewer">
      {/* Meta Section */}
      <div className="state-section">
        <h4>📊 Meta</h4>
        <div className="state-item">
          <span className="state-label">Iteration:</span>
          <span className="state-value">
            {state.meta?.iteration || 0} / {state.meta?.max_iterations || 0}
          </span>
        </div>
        <div className="state-item">
          <span className="state-label">Phase:</span>
          <span className="state-value">{safeRender(state.meta?.phase)}</span>
        </div>
        <div className="state-item">
          <span className="state-label">Confidence:</span>
          <span className="state-value">
            {((state.meta?.overall_confidence || 0) * 100).toFixed(0)}%
          </span>
        </div>
        <div className="state-item">
          <span className="state-label">Investigation ID:</span>
          <span className="state-value state-id">{safeRender(state.meta?.investigation_id)}</span>
        </div>
      </div>

      {/* Hypotheses Section */}
      <div className="state-section">
        <h4>💡 Hypotheses ({(state.hypotheses || []).length})</h4>
        {(state.hypotheses || []).length === 0 ? (
          <div className="state-empty-section">No hypotheses yet</div>
        ) : (
          (state.hypotheses || []).map((hyp: any, idx: number) => (
            <details key={idx} className="state-collapsible" open={hyp.status === 'exploring'}>
              <summary className="state-summary">
                <span className={`status-badge status-${hyp.status || 'pending'}`}>{safeRender(hyp.status)}</span>
                <span className="state-text">{safeRender(hyp.id)}: {safeRender(hyp.statement)}</span>
              </summary>
              <div className="state-detail">
                <div className="state-item">
                  <span className="state-label">Confidence:</span>
                  <span className="state-value">{(hyp.confidence * 100).toFixed(0)}%</span>
                </div>
                <div className="state-item">
                  <span className="state-label">Priority:</span>
                  <span className="state-value">
                    {hyp.priority === 0 ? '🚨 HIGHEST (User-Driven)' : hyp.priority || 10}
                  </span>
                </div>
                <div className="state-item">
                  <span className="state-label">Questions:</span>
                  <span className="state-value">
                    {(hyp.questions || []).length} total, {' '}
                    {(hyp.questions || []).filter((q: any) => q.answer || q.a).length} answered
                  </span>
                </div>
                {(hyp.questions || []).length > 0 && (
                  <div className="state-questions">
                    {(hyp.questions || []).map((q: any, qIdx: number) => {
                      const answer = q.answer || q.a;
                      const question = q.question || q.q;
                      return (
                        <div key={qIdx} className={`state-question ${answer ? 'answered' : 'unanswered'}`}>
                          <div className="question-text">
                            {answer ? '✅' : '❓'} <strong>Q{qIdx + 1}:</strong> {safeRender(question)}
                          </div>
                          {answer && (
                            <div className="answer-text">
                              <strong>Answer:</strong> {safeRender(answer)}
                              {q.source && typeof q.source === 'string' && (
                                <a href={q.source} target="_blank" rel="noopener noreferrer" className="source-link"> [source]</a>
                              )}
                            </div>
                          )}
                          <div className="question-meta">
                            <span className="question-status">{q.status || 'exploring'}</span>
                            {q.iteration && <span className="question-iteration">Iteration {q.iteration}</span>}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </details>
          ))
        )}
      </div>

      {/* Entities Section */}
      <div className="state-section">
        <h4>👥 Entities ({(state.entities || []).length})</h4>
        {(state.entities || []).length === 0 ? (
          <div className="state-empty-section">No entities discovered yet</div>
        ) : (
          (state.entities || []).slice(0, 15).map((entity: any, idx: number) => (
            <details key={idx} className="state-collapsible">
              <summary className="state-summary">
                <span className="entity-type">{safeRender(entity.type)}</span>
                <span className="state-text">{safeRender(entity.name)}</span>
                <span className="importance-badge">{((entity.importance || 0) * 100).toFixed(0)}%</span>
              </summary>
              <div className="state-detail">
                <div className="state-item">
                  <span className="state-label">Role:</span>
                  <span className="state-value">{safeRender(entity.role)}</span>
                </div>
                <div className="state-item">
                  <span className="state-label">Investigated:</span>
                  <span className="state-value">{entity.investigated ? '✅ Yes' : '⏸️ Pending'}</span>
                </div>
                {(entity.questions_about || []).length > 0 && (
                  <div className="state-item">
                    <span className="state-label">Questions:</span>
                    <span className="state-value">{String((entity.questions_about || []).length)} pending</span>
                  </div>
                )}
                {(entity.sources || []).length > 0 && (
                  <div className="state-item">
                    <span className="state-label">Sources:</span>
                    <span className="state-value">{String((entity.sources || []).length)} URLs</span>
                  </div>
                )}
              </div>
            </details>
          ))
        )}
        {(state.entities || []).length > 15 && (
          <div className="state-more">...and {(state.entities || []).length - 15} more entities</div>
        )}
      </div>

      {/* Facts Section */}
      <div className="state-section">
        <h4>📌 Facts ({(state.facts || []).length})</h4>
        {(state.facts || []).length === 0 ? (
          <div className="state-empty-section">No facts collected yet</div>
        ) : (
          <div className="facts-list">
            {(state.facts || []).slice(0, 10).map((fact: string, idx: number) => (
              <div key={idx} className="fact-item">
                <span className="fact-bullet">•</span>
                <span className="fact-text">{safeRender(fact)}</span>
              </div>
            ))}
            {(state.facts || []).length > 10 && (
              <div className="state-more">...and {(state.facts || []).length - 10} more facts</div>
            )}
          </div>
        )}
      </div>

      {/* Anomalies Section */}
      {(state.anomalies || []).length > 0 && (
        <div className="state-section">
          <h4>⚠️ Anomalies ({(state.anomalies || []).length})</h4>
          <div className="anomalies-list">
            {(state.anomalies || []).map((anomaly: string, idx: number) => (
              <div key={idx} className="anomaly-item">
                <span className="anomaly-icon">⚠️</span>
                <span className="anomaly-text">{safeRender(anomaly)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Narrative Section */}
      {state.narrative?.story && typeof state.narrative.story === 'string' && (
        <div className="state-section">
          <h4>📖 Narrative</h4>
          <div className="narrative-content">
            <p>{state.narrative.story}</p>
            {(state.narrative.key_findings || []).length > 0 && (
              <div className="key-findings">
                <strong>Key Findings:</strong>
                <ul>
                  {state.narrative.key_findings.map((finding: string, idx: number) => (
                    <li key={idx}>{safeRender(finding)}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Timeline Section */}
      {(state.timeline || []).length > 0 && (
        <div className="state-section">
          <h4>⏱️ Timeline ({(state.timeline || []).length})</h4>
          <div className="timeline-list">
            {(state.timeline || []).map((event: any, idx: number) => (
              <div key={idx} className="timeline-item">
                <span className="timeline-date">{safeRender(event.date)}</span>
                <span className="timeline-event">{safeRender(event.event)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Costs Section */}
      <div className="state-section">
        <h4>💰 Costs</h4>
        <div className="state-item">
          <span className="state-label">Tavily Searches:</span>
          <span className="state-value">{state.costs?.tavily_searches || 0}</span>
        </div>
        <div className="state-item">
          <span className="state-label">Free Extractions:</span>
          <span className="state-value">{state.costs?.free_extractions || 0}</span>
        </div>
        <div className="state-item">
          <span className="state-label">Tavily Extractions:</span>
          <span className="state-value">{state.costs?.tavily_extractions || 0}</span>
        </div>
        <div className="state-item">
          <span className="state-label">LLM Calls:</span>
          <span className="state-value">{state.costs?.llm_calls || 0}</span>
        </div>
        <div className="state-item">
          <span className="state-label">Total Cost:</span>
          <span className="state-value state-cost">${(state.costs?.total_cost || 0).toFixed(3)}</span>
        </div>
      </div>

      {/* Cache Stats */}
      <div className="state-section">
        <h4>📦 Cache</h4>
        <div className="state-item">
          <span className="state-label">Seen URLs:</span>
          <span className="state-value">{(state.cache?.seen_urls || []).length}</span>
        </div>
        <div className="state-item">
          <span className="state-label">Previous Queries:</span>
          <span className="state-value">{(state.cache?.previous_queries || []).length}</span>
        </div>
        <div className="state-item">
          <span className="state-label">Documents in RAG:</span>
          <span className="state-value">{state.cache?.documents_in_rag || 0}</span>
        </div>
      </div>

      {/* Raw JSON Toggle */}
      <details className="state-collapsible state-raw-json">
        <summary className="state-summary">
          <span className="state-text">📋 Raw JSON</span>
        </summary>
        <pre className="json-viewer">
          {JSON.stringify(state, null, 2)}
        </pre>
      </details>
    </div>
  );
}

