import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { config } from '../config';
import './InvestigationsPage.css';

// Investigation type definition
export interface Investigation {
  id: string;
  title: string;
  query: string;
  status: 'active' | 'completed' | 'archived';
  article: string;
  cost: number;
  phase: string;
  progress: {
    current: number;
    max: number;
  };
  currentIteration: number;
  maxIterations: number;
  createdAt: string;
  updatedAt: string;
  completedAt: string | null;
  entities: Array<{
    type: string;
    name: string;
    description?: string;
  }>;
  facts: Array<{
    id: string;
    content: string;
    sources: string[];
  }>;
  connections: Array<{
    from: string;
    to: string;
    type: string;
  }>;
  anomalies: any[];
}

export function InvestigationsPage() {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed' | 'archived'>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    query: '',
    title: '',
    max_iterations: 20
  });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    const fetchInvestigations = async () => {
      try {
        const response = await fetch(`${config.apiUrl}/api/investigations`);
        
        if (!response.ok) {
          console.error('Failed to fetch investigations:', response.status);
          setInvestigations([]);
          setLoading(false);
          return;
        }
        
        const result = await response.json();
        
        // Transform backend format to frontend format
        if (result.investigations) {
          const transformed = result.investigations.map((inv: any) => ({
            id: inv.investigation_id,
            title: inv.title,
            query: inv.query,
            status: inv.status,
            article: inv.article || '',
            cost: inv.cost_usd || 0,
            phase: inv.phase || 'initial',
            progress: {
              current: inv.current_iteration || 0,
              max: inv.max_iterations || 20
            },
            currentIteration: inv.current_iteration || 0,
            maxIterations: inv.max_iterations || 20,
            createdAt: inv.created_at,
            updatedAt: inv.updated_at,
            completedAt: inv.completed_at,
            entities: inv.entities || [],
            facts: inv.facts || [],
            connections: inv.connections || [],
            anomalies: inv.anomalies || []
          }));
          
          setInvestigations(transformed);
        } else {
          setInvestigations([]);
        }
      } catch (error) {
        console.error('Error fetching investigations:', error);
        setInvestigations([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchInvestigations();
  }, []);

  const handleCreateInvestigation = async () => {
    if (!createForm.query.trim()) {
      alert('Please enter a query');
      return;
    }

    setCreating(true);
    
    try {
      // Call the backend API
      const response = await fetch(`${config.apiUrl}/api/investigations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: createForm.query,
          title: createForm.title || createForm.query.slice(0, 100),
          max_iterations: createForm.max_iterations
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create investigation');
      }

      const data = await response.json();
      const investigationId = data.investigation_id;

      // Close modal and navigate to investigation detail page
      setShowCreateModal(false);
      setCreateForm({ query: '', title: '', max_iterations: 20 });
      
      // Navigate to the new investigation
      navigate(`/investigations/${investigationId}`);
      
    } catch (error) {
      console.error('Error creating investigation:', error);
      alert('Failed to create investigation. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const filteredInvestigations = investigations.filter(inv => {
    if (filter === 'all') return true;
    return inv.status === filter;
  });

  // Calculate stats
  const stats = {
    total: investigations.length,
    active: investigations.filter(inv => inv.status === 'active').length,
    completed: investigations.filter(inv => inv.status === 'completed').length,
    archived: investigations.filter(inv => inv.status === 'archived').length,
  };

  return (
    <div className="investigations-page">
      {/* Header Section */}
      <header className="investigations-header">
        <div className="investigations-header-top">
          <div className="investigations-header-left">
            <h1>Investigations</h1>
            <p className="investigations-header-subtitle">
              Deep investigative journalism projects with evidence tracking
            </p>
          </div>
          <button 
            className="investigations-header-action"
            onClick={() => setShowCreateModal(true)}
          >
            + New Investigation
          </button>
        </div>

        {/* Stats Bar */}
        <div className="investigations-stats">
          <div className="stat-item">
            <span className="stat-label">Total</span>
            <span className="stat-value">{stats.total}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Active</span>
            <span className="stat-value">{stats.active}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Completed</span>
            <span className="stat-value">{stats.completed}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Archived</span>
            <span className="stat-value">{stats.archived}</span>
          </div>
        </div>
      </header>

      {/* Toolbar with Filters */}
      <div className="investigations-toolbar">
        <span className="toolbar-label">Filter:</span>
        <div className="toolbar-filters">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All ({stats.total})
          </button>
          <button
            className={`filter-btn ${filter === 'active' ? 'active' : ''}`}
            onClick={() => setFilter('active')}
          >
            Active ({stats.active})
          </button>
          <button
            className={`filter-btn ${filter === 'completed' ? 'active' : ''}`}
            onClick={() => setFilter('completed')}
          >
            Completed ({stats.completed})
          </button>
          <button
            className={`filter-btn ${filter === 'archived' ? 'active' : ''}`}
            onClick={() => setFilter('archived')}
          >
            Archived ({stats.archived})
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="investigations-content">
        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <div className="loading-text">Loading investigations...</div>
          </div>
        ) : filteredInvestigations.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <h3>No investigations found</h3>
            <p>
              {filter === 'all'
                ? 'Create your first investigation to get started.'
                : `No ${filter} investigations at the moment.`}
            </p>
          </div>
        ) : (
          <div className="investigations-grid">
            {filteredInvestigations.map((inv) => (
              <Link
                key={inv.id}
                to={`/investigations/${inv.id}`}
                className="investigation-card"
              >
                {/* Card Header */}
                <div className="card-header">
                  <div className="card-header-top">
                    <span
                      className={`card-status status-${inv.status}`}
                    >
                      {inv.status}
                    </span>
                    <span className="card-meta-top">
                      {new Date(inv.updatedAt).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="card-title">{inv.title}</h3>
                  <p className="card-article">{inv.article}</p>
                </div>

                {/* Card Body */}
                <div className="card-body">
                  {/* Progress */}
                  <div className="card-progress">
                    <div className="progress-label">
                      <span className="progress-text">Progress</span>
                      <span className="progress-value">
                        {inv.progress.current}/{inv.progress.max} iterations
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${(inv.progress.current / inv.progress.max) * 100}%`,
                        }}
                      ></div>
                    </div>
                  </div>

                  {/* Evidence Grid */}
                  <div className="card-evidence">
                    <div className="evidence-item">
                      <span className="evidence-value">{inv.entities.length}</span>
                      <span className="evidence-label">Entities</span>
                    </div>
                    <div className="evidence-item">
                      <span className="evidence-value">{inv.facts.length}</span>
                      <span className="evidence-label">Facts</span>
                    </div>
                    <div className="evidence-item">
                      <span className="evidence-value">{inv.connections.length}</span>
                      <span className="evidence-label">Connections</span>
                    </div>
                    <div className="evidence-item">
                      <span className="evidence-value">{inv.anomalies?.length || 0}</span>
                      <span className="evidence-label">Anomalies</span>
                    </div>
                  </div>
                </div>

                {/* Card Footer */}
                <div className="card-footer">
                  <span className="card-meta">
                    Created {new Date(inv.createdAt).toLocaleDateString()}
                  </span>
                  <span className="card-cost">${inv.cost.toFixed(3)}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Create Investigation Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Investigation</h2>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>
                ×
              </button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="query">Investigation Query *</label>
                <textarea
                  id="query"
                  rows={3}
                  placeholder="e.g., India cough syrup deaths government response"
                  value={createForm.query}
                  onChange={(e) => setCreateForm({ ...createForm, query: e.target.value })}
                  className="form-input"
                />
                <span className="form-hint">What would you like to investigate?</span>
              </div>

              <div className="form-group">
                <label htmlFor="title">Title (optional)</label>
                <input
                  id="title"
                  type="text"
                  placeholder="Leave empty to auto-generate from query"
                  value={createForm.title}
                  onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="max_iterations">Max Iterations</label>
                <input
                  id="max_iterations"
                  type="number"
                  min="1"
                  max="100"
                  value={createForm.max_iterations}
                  onChange={(e) => setCreateForm({ ...createForm, max_iterations: parseInt(e.target.value) || 20 })}
                  className="form-input"
                />
                <span className="form-hint">
                  More iterations = deeper investigation (Cost: ~$0.036 per iteration)
                </span>
              </div>
            </div>

            <div className="modal-footer">
              <button 
                className="btn-secondary" 
                onClick={() => setShowCreateModal(false)}
                disabled={creating}
              >
                Cancel
              </button>
              <button 
                className="btn-primary" 
                onClick={handleCreateInvestigation}
                disabled={creating || !createForm.query.trim()}
              >
                {creating ? 'Creating...' : 'Create Investigation'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
