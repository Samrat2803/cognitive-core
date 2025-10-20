import { useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import './InfoPage.css';

export function InfoPage() {
  const navigate = useNavigate();

  return (
    <div className="info-page">
      <Header />
      
      <div className="info-container">
        {/* Hero Section */}
        <section className="info-hero">
          <div className="info-hero-content">
            <h1 className="info-hero-title">Political Analyst Workbench</h1>
            <p className="info-hero-subtitle">
              Multi-Agent System with LangGraph, Tavily API, and Real-Time Intelligence
            </p>
          <div className="info-hero-badges">
            <span className="info-badge">LangGraph</span>
            <span className="info-badge">Tavily API</span>
            <span className="info-badge">AWS</span>
            <span className="info-badge">MongoDB Atlas</span>
          </div>
          <div style={{ marginTop: 'var(--space-lg)' }}>
            <a 
              href="https://github.com/Samrat2803/cognitive-core" 
              target="_blank" 
              rel="noopener noreferrer"
              className="github-link"
            >
              ⭐ View on GitHub
            </a>
          </div>
          </div>
        </section>

        {/* Project Overview */}
        <section className="info-section">
          <h2 className="info-section-title">Project Overview</h2>
          <div className="info-card">
            <div className="info-grid-2">
              <div className="info-content">
                <h3>What We Built</h3>
                <p>
                  A sophisticated AI-powered political intelligence platform that combines 
                  <strong> LangGraph's multi-agent architecture</strong> with <strong>Tavily's real-time web search</strong> 
                  to deliver comprehensive analysis with automatic visualization generation, deep investigative reporting, 
                  and intelligent web crawling capabilities.
                </p>
                <ul className="info-list">
                  <li>7-Node Master Agent orchestrating complex workflows</li>
                  <li>10+ Specialized Sub-Agents for diverse analysis types</li>
                  <li>Real-time web data integration via Tavily & RSS feeds</li>
                  <li>Intelligent web crawling with domain classification</li>
                  <li>Deep investigative journalism with evidence tracking</li>
                  <li>Knowledge base with RAG (Retrieval Augmented Generation)</li>
                  <li>Automatic chart, graph, and infographic generation</li>
                  <li>WebSocket streaming for live updates</li>
                </ul>
              </div>
              <div className="info-stats">
                <div className="info-stat-card">
                  <div className="info-stat-value">7</div>
                  <div className="info-stat-label">Master Agent Nodes</div>
                </div>
                <div className="info-stat-card">
                  <div className="info-stat-value">8</div>
                  <div className="info-stat-label">Specialized Sub-Agents</div>
                </div>
                <div className="info-stat-card">
                  <div className="info-stat-value">50+</div>
                  <div className="info-stat-label">Artifact Types</div>
                </div>
                <div className="info-stat-card">
                  <div className="info-stat-value">20+</div>
                  <div className="info-stat-label">Integrated Tools</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Architecture */}
        <section className="info-section">
          <h2 className="info-section-title">Multi-Agent Architecture</h2>
          <div className="info-card">
            <div className="arch-legend">
              <span className="legend-item">
                <span className="legend-box legend-live"></span>
                <span>Live & Operational ✓</span>
              </span>
              <span className="legend-item">
                <span className="legend-box legend-pending"></span>
                <span>Under Implementation</span>
              </span>
            </div>
            <div className="architecture-diagram">
              <div className="arch-layer">
                <h4>Frontend Layer</h4>
                <div className="arch-boxes">
                  <div className="arch-box">React 19 + TypeScript</div>
                  <div className="arch-box">REST API + WebSocket</div>
                  <div className="arch-box">Real-time UI</div>
                </div>
              </div>
              
              <div className="arch-arrow">↓</div>
              
              <div className="arch-layer">
                <h4>Master Agent (LangGraph - 7 Nodes)</h4>
                <div className="arch-flow">
                  <div className="arch-node">1. Conversation Manager</div>
                  <div className="arch-connector">→</div>
                  <div className="arch-node">2. Strategic Planner</div>
                  <div className="arch-connector">→</div>
                  <div className="arch-node">3. Tool Executor</div>
                  <div className="arch-connector">→</div>
                  <div className="arch-node">4. Decision Gate</div>
                  <div className="arch-connector">↻</div>
                  <div className="arch-node">5. Response Synthesizer</div>
                  <div className="arch-connector">→</div>
                  <div className="arch-node">6. Artifact Decision</div>
                  <div className="arch-connector">→</div>
                  <div className="arch-node">7. Artifact Creator</div>
                </div>
              </div>
              
              <div className="arch-arrow">↓</div>
              
              <div className="arch-layer">
                <h4>Sub-Agents (8 Specialized Agents) - All Operational ✓</h4>
                <div className="arch-grid">
                  <div className="arch-subagent arch-live">Cognitive Crawler ✓</div>
                  <div className="arch-subagent arch-live">Investigative Journalist ✓</div>
                  <div className="arch-subagent arch-live">Media Bias Detector ✓</div>
                  <div className="arch-subagent arch-live">Sentiment Analyzer ✓</div>
                  <div className="arch-subagent arch-live">Live Political Monitor ✓</div>
                  <div className="arch-subagent arch-live">RSS Realtime Monitor ✓</div>
                  <div className="arch-subagent arch-live">SitRep Generator ✓</div>
                  <div className="arch-subagent arch-live">Deep Investigative Reporter ✓</div>
                </div>
              </div>
              
              <div className="arch-arrow">↓</div>
              
              <div className="arch-layer">
                <h4>Integrated Tools & Data Sources</h4>
                <div className="arch-grid">
                  <div className="arch-subagent arch-live">Tavily Search API ✓</div>
                  <div className="arch-subagent arch-live">Tavily Extract API ✓</div>
                  <div className="arch-subagent arch-live">RSS Feed Collector ✓</div>
                  <div className="arch-subagent arch-live">Jina AI Reader ✓</div>
                  <div className="arch-subagent arch-live">Aleph Data ✓</div>
                  <div className="arch-subagent arch-live">Wayback Machine ✓</div>
                  <div className="arch-subagent arch-live">Chart Generator ✓</div>
                  <div className="arch-subagent arch-live">Infographic Maker ✓</div>
                  <div className="arch-subagent arch-live">Timeline Builder ✓</div>
                  <div className="arch-subagent arch-live">Network Graphs ✓</div>
                  <div className="arch-subagent arch-live">Evidence Repository ✓</div>
                  <div className="arch-subagent arch-live">Knowledge Base (RAG) ✓</div>
                </div>
              </div>
              
              <div className="arch-arrow">↓</div>
              
              <div className="arch-layer">
                <h4>Data & Services Layer</h4>
                <div className="arch-boxes">
                  <div className="arch-box arch-live">Tavily API ✓</div>
                  <div className="arch-box arch-live">MongoDB Atlas ✓</div>
                  <div className="arch-box arch-live">AWS S3 ✓</div>
                  <div className="arch-box arch-live">OpenAI ✓</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* How Agents Work */}
        <section className="info-section">
          <h2 className="info-section-title">How the Agents Work</h2>
          <div className="workflow-container">
            <div className="workflow-card">
              <div className="workflow-number">1</div>
              <div className="workflow-content">
                <h3>Query Analysis</h3>
                <p>
                  The <strong>Conversation Manager</strong> receives your query and analyzes intent, 
                  extracting key entities, topics, and required analysis type.
                </p>
                <div className="workflow-example">
                  <strong>Example:</strong> "Analyze sentiment on Gaza conflict"<br/>
                  → Identifies: sentiment analysis, geopolitical topic, region-specific
                </div>
              </div>
            </div>

            <div className="workflow-card">
              <div className="workflow-number">2</div>
              <div className="workflow-content">
                <h3>Strategic Planning</h3>
                <p>
                  The <strong>Strategic Planner</strong> creates an execution plan, selecting appropriate 
                  tools and sub-agents based on query requirements.
                </p>
                <div className="workflow-example">
                  <strong>Plan:</strong><br/>
                  1. Use Tavily Search for recent articles<br/>
                  2. Delegate to Sentiment Analyzer sub-agent<br/>
                  3. Generate sentiment map visualization
                </div>
              </div>
            </div>

            <div className="workflow-card">
              <div className="workflow-number">3</div>
              <div className="workflow-content">
                <h3>Tool Execution</h3>
                <p>
                  The <strong>Tool Executor</strong> calls Tavily APIs (Search, Extract, Crawl) to gather 
                  real-time web data with citations and credibility scores.
                </p>
                <div className="workflow-example">
                  <strong>Output:</strong> 8-20 articles with content, URLs, scores, and publish dates
                </div>
              </div>
            </div>

            <div className="workflow-card">
              <div className="workflow-number">4</div>
              <div className="workflow-content">
                <h3>Sub-Agent Delegation</h3>
                <p>
                  Master Agent delegates to specialized <strong>Sub-Agents</strong> (Sentiment Analyzer, 
                  Live Monitor, SitRep Generator) which run their own LangGraph workflows.
                </p>
                <div className="workflow-example">
                  <strong>Sub-Agent Flow:</strong><br/>
                  Search → Analyze → Synthesize → Visualize
                </div>
              </div>
            </div>

            <div className="workflow-card">
              <div className="workflow-number">5</div>
              <div className="workflow-content">
                <h3>Decision Gate</h3>
                <p>
                  The <strong>Decision Gate</strong> evaluates if gathered information is sufficient. 
                  If not, loops back to gather more data (max 3 iterations).
                </p>
                <div className="workflow-example">
                  <strong>Logic:</strong> Check completeness → Loop or Continue
                </div>
              </div>
            </div>

            <div className="workflow-card">
              <div className="workflow-number">6</div>
              <div className="workflow-content">
                <h3>Response Synthesis</h3>
                <p>
                  The <strong>Response Synthesizer</strong> combines all data into a comprehensive answer 
                  with proper citations, structured formatting, and key insights.
                </p>
                <div className="workflow-example">
                  <strong>Includes:</strong> Analysis, citations, confidence scores, sources
                </div>
              </div>
            </div>

            <div className="workflow-card">
              <div className="workflow-number">7</div>
              <div className="workflow-content">
                <h3>Artifact Decision</h3>
                <p>
                  The <strong>Artifact Decision</strong> node determines if data supports visualization. 
                  Checks for numerical data, geographic info, or relationships.
                </p>
                <div className="workflow-example">
                  <strong>Triggers:</strong> Sentiment scores → Bar chart<br/>
                  Geographic data → Map visualization
                </div>
              </div>
            </div>

            <div className="workflow-card">
              <div className="workflow-number">8</div>
              <div className="workflow-content">
                <h3>Artifact Creation</h3>
                <p>
                  The <strong>Artifact Creator</strong> generates interactive visualizations using Plotly, 
                  exports to HTML/PNG, and stores in AWS S3 or MongoDB.
                </p>
                <div className="workflow-example">
                  <strong>Output:</strong> Interactive charts, maps, infographics, reports
                </div>
              </div>
            </div>
          </div>

          {/* Real-time Streaming */}
          <div className="info-card" style={{ marginTop: 'var(--space-3xl)' }}>
            <h3>Real-Time WebSocket Streaming</h3>
            <p style={{ marginBottom: 'var(--space-lg)' }}>
              Throughout this entire process, the Master Agent streams updates to the frontend via WebSocket:
            </p>
            <div className="streaming-flow">
              <div className="stream-item">
                <strong>Step Updates</strong>
                <p>Current node being executed</p>
              </div>
              <div className="stream-arrow">→</div>
              <div className="stream-item">
                <strong>Tool Calls</strong>
                <p>Which tools are being invoked</p>
              </div>
              <div className="stream-arrow">→</div>
              <div className="stream-item">
                <strong>Intermediate Results</strong>
                <p>Partial data as it arrives</p>
              </div>
              <div className="stream-arrow">→</div>
              <div className="stream-item">
                <strong>Final Response</strong>
                <p>Complete analysis with artifacts</p>
              </div>
            </div>
          </div>
        </section>

        {/* Sentiment Analyzer Deep Dive */}
        <section className="info-section">
          <h2 className="info-section-title">All Operational Sub-Agents Showcase</h2>
          
          {/* Cognitive Crawler */}
          <div className="info-card" style={{ marginBottom: 'var(--space-2xl)' }}>
            <h3>🧠 Cognitive Crawler: Intelligent Web Crawling</h3>
            <p style={{ marginBottom: 'var(--space-lg)', fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
              Three-layer intelligence system for smart, efficient web crawling with domain classification and URL prioritization.
            </p>
            <div className="info-grid-2">
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Core Capabilities</h4>
                <ul className="info-list">
                  <li>Intent detection (crawl entire site vs. specific pages)</li>
                  <li>Domain classification (Authority, News, Research, Unknown)</li>
                  <li>Smart URL prioritization (100-point scoring system)</li>
                  <li>Portal discovery via Tavily integration</li>
                  <li>Knowledge base storage with MongoDB + embeddings</li>
                  <li>RAG query support for stored content</li>
                </ul>
              </div>
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Technical Highlights</h4>
                <div className="info-grid-3">
                  <div className="info-stat-card">
                    <div className="info-stat-value">3</div>
                    <div className="info-stat-label">Intelligence Layers</div>
                  </div>
                  <div className="info-stat-card">
                    <div className="info-stat-value">100</div>
                    <div className="info-stat-label">Max Priority Score</div>
                  </div>
                  <div className="info-stat-card">
                    <div className="info-stat-value">4</div>
                    <div className="info-stat-label">Domain Types</div>
                  </div>
                </div>
                <p style={{ marginTop: 'var(--space-md)', fontSize: '0.9rem', color: 'var(--text-tertiary)' }}>
                  <strong>Use Case:</strong> "Find and crawl all drug regulation portals in India" 
                  → Discovers government sites → Maps entire domains → Stores with embeddings → Enables semantic search
                </p>
              </div>
            </div>
          </div>

          {/* Investigative Journalist */}
          <div className="info-card" style={{ marginBottom: 'var(--space-2xl)' }}>
            <h3>📰 Investigative Journalist: Deep Research & Reporting</h3>
            <p style={{ marginBottom: 'var(--space-lg)', fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
              Cost-optimized investigative agent (91% cheaper) with evidence tracking, hypothesis testing, and publication-ready outputs.
            </p>
            <div className="info-grid-2">
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Key Features</h4>
                <ul className="info-list">
                  <li>Hypothesis-driven investigation methodology</li>
                  <li>Free extraction (Jina AI + Trafilatura: 83% success)</li>
                  <li>Evidence repository with full source attribution</li>
                  <li>Resume capability across multiple sessions</li>
                  <li>Query diversity validation (prevents repetition)</li>
                  <li>Publication-ready article generation</li>
                  <li>Timeline, network graph, and evidence chain artifacts</li>
                </ul>
              </div>
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Performance Metrics</h4>
                <div className="info-grid-3">
                  <div className="info-stat-card">
                    <div className="info-stat-value">91%</div>
                    <div className="info-stat-label">Cost Reduction</div>
                  </div>
                  <div className="info-stat-card">
                    <div className="info-stat-value">83%</div>
                    <div className="info-stat-label">Free Extraction Success</div>
                  </div>
                  <div className="info-stat-card">
                    <div className="info-stat-value">$0.036</div>
                    <div className="info-stat-label">Per Iteration</div>
                  </div>
                </div>
                <p style={{ marginTop: 'var(--space-md)', fontSize: '0.9rem', color: 'var(--text-tertiary)' }}>
                  <strong>Outputs:</strong> Professional investigative articles with executive summary, key findings, 
                  evidence chains, timeline visualizations, and entity network graphs
                </p>
              </div>
            </div>
          </div>

          {/* Media Bias Detector */}
          <div className="info-card" style={{ marginBottom: 'var(--space-2xl)' }}>
            <h3>📊 Media Bias Detector: Multi-Source Analysis</h3>
            <p style={{ marginBottom: 'var(--space-lg)', fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
              Compares how different media outlets cover the same event, detecting framing bias, political lean, and loaded language.
            </p>
            <div className="info-grid-2">
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Analysis Capabilities</h4>
                <ul className="info-list">
                  <li>Multi-source comparison (left-center-right spectrum)</li>
                  <li>Political lean classification with confidence scores</li>
                  <li>Loaded language detection and word cloud generation</li>
                  <li>Framing analysis (how stories are presented)</li>
                  <li>Consensus vs. divergence point identification</li>
                  <li>Omission analysis (what each source leaves out)</li>
                </ul>
              </div>
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Artifact Types</h4>
                <ul className="info-list">
                  <li>Bias spectrum chart (political positioning)</li>
                  <li>Source comparison matrix</li>
                  <li>Loaded language word clouds</li>
                  <li>Framing analysis reports</li>
                </ul>
                <p style={{ marginTop: 'var(--space-lg)', fontSize: '0.9rem', color: 'var(--text-tertiary)' }}>
                  <strong>Example Query:</strong> "Compare how CNN, Fox News, and BBC covered the climate summit"
                  → Analyzes bias, framing, language → Visual comparison report
                </p>
              </div>
            </div>
          </div>

          {/* Sentiment Analyzer */}
          <div className="info-card" style={{ marginBottom: 'var(--space-2xl)' }}>
            <h3>😊 Sentiment Analyzer: Multi-Country Analysis</h3>
            <p style={{ marginBottom: 'var(--space-lg)', fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
              Advanced sentiment analysis with iterative quality-checking loop to combat language bias and ensure geopolitical accuracy.
            </p>
            <div className="info-grid-2">
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Sophisticated Features</h4>
                <ul className="info-list">
                  <li>7-node LangGraph workflow with iteration loop</li>
                  <li>Language bias detection (English vs. local content)</li>
                  <li>Country-specific domain filtering (e.g., .ir for Iran)</li>
                  <li>Source diversity scoring and validation</li>
                  <li>Sentiment scoring (-1.0 to +1.0) with justification</li>
                  <li>Bias analysis (7 types: selection, framing, language, etc.)</li>
                  <li>Max 3 iterations for quality improvement</li>
                </ul>
              </div>
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Technical Specs</h4>
                <div className="info-grid-3">
                  <div className="info-stat-card">
                    <div className="info-stat-value">7</div>
                    <div className="info-stat-label">Workflow Nodes</div>
                  </div>
                  <div className="info-stat-card">
                    <div className="info-stat-value">3</div>
                    <div className="info-stat-label">Max Iterations</div>
                  </div>
                  <div className="info-stat-card">
                    <div className="info-stat-value">8-20</div>
                    <div className="info-stat-label">Articles/Country</div>
                  </div>
                </div>
                <p style={{ marginTop: 'var(--space-md)', fontSize: '0.9rem', color: 'var(--text-tertiary)' }}>
                  <strong>Innovation:</strong> Quality checker detects language bias (&gt;70% English for non-English countries) 
                  → Triggers iteration with domain filtering → Ensures balanced analysis
                </p>
              </div>
            </div>
          </div>

          {/* Live Political Monitor */}
          <div className="info-card" style={{ marginBottom: 'var(--space-2xl)' }}>
            <h3>🔴 Live Political Monitor: Real-Time Event Tracking</h3>
            <p style={{ marginBottom: 'var(--space-lg)', fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
              Hybrid RSS + Tavily real-time monitoring with "explosiveness" scoring to identify breaking stories and trending topics. 
              Defaults to cost-efficient RSS, with Tavily backup available for broader coverage.
            </p>
            <div className="info-grid-2">
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Monitoring Capabilities</h4>
                <ul className="info-list">
                  <li>Primary: RSS feed collection from major news sources</li>
                  <li>Fallback: Tavily search for comprehensive coverage</li>
                  <li>Explosiveness scoring (0-100 scale)</li>
                  <li>Weighted algorithm (LLM rating, frequency, diversity, urgency)</li>
                  <li>Topic clustering and identification</li>
                  <li>Breaking story detection</li>
                  <li>3-hour caching for cost efficiency</li>
                </ul>
              </div>
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Cost Optimization</h4>
                <div className="info-grid-3">
                  <div className="info-stat-card">
                    <div className="info-stat-value">99.4%</div>
                    <div className="info-stat-label">Cheaper (RSS mode)</div>
                  </div>
                  <div className="info-stat-card">
                    <div className="info-stat-value">2-5s</div>
                    <div className="info-stat-label">Response Time</div>
                  </div>
                  <div className="info-stat-card">
                    <div className="info-stat-value">$0.00003</div>
                    <div className="info-stat-label">Per Query (RSS)</div>
                  </div>
                </div>
                <p style={{ marginTop: 'var(--space-md)', fontSize: '0.9rem', color: 'var(--text-tertiary)' }}>
                  <strong>Dual Mode:</strong> RSS-based endpoint (default, 99.4% cheaper) + Tavily-based endpoint (fallback, comprehensive). 
                  Explosiveness Formula: LLM Rating (30pts) + Frequency (25pts) + Source Diversity (20pts) + Urgency Keywords (15pts) + Recency (10pts)
                </p>
              </div>
            </div>
          </div>

          {/* SitRep Generator */}
          <div className="info-card" style={{ marginBottom: 'var(--space-2xl)' }}>
            <h3>📋 SitRep Generator: Professional Situation Reports</h3>
            <p style={{ marginBottom: 'var(--space-lg)', fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
              Generates comprehensive situation reports (daily/weekly) with professional formatting and multiple export options.
            </p>
            <div className="info-grid-2">
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Report Features</h4>
                <ul className="info-list">
                  <li>Scope definition (daily, weekly, custom time ranges)</li>
                  <li>Data aggregation from multiple sources</li>
                  <li>Priority ranking of events and topics</li>
                  <li>Professional report composition</li>
                  <li>Multi-format export (PDF, HTML, TXT, JSON)</li>
                  <li>Uses Live Monitor's explosive topics data</li>
                </ul>
              </div>
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Output Formats</h4>
                <ul className="info-list">
                  <li>📄 PDF reports (professional formatting)</li>
                  <li>🌐 HTML dashboards (interactive)</li>
                  <li>📧 Email-ready text (plain text)</li>
                  <li>💾 JSON data (programmatic access)</li>
                </ul>
                <p style={{ marginTop: 'var(--space-lg)', fontSize: '0.9rem', color: 'var(--text-tertiary)' }}>
                  <strong>Execution Time:</strong> 35-45 seconds for comprehensive reports with 
                  executive summary, key developments, priority events, and source citations
                </p>
              </div>
            </div>
          </div>

          {/* RSS Realtime Monitor */}
          <div className="info-card" style={{ marginBottom: 'var(--space-2xl)' }}>
            <h3>📡 RSS Realtime Monitor: Continuous Feed Monitoring</h3>
            <p style={{ marginBottom: 'var(--space-lg)', fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
              Background RSS feed monitoring with automatic article collection, parsing, and knowledge base storage.
            </p>
            <div className="info-grid-2">
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Monitoring System</h4>
                <ul className="info-list">
                  <li>Continuous background polling (configurable interval)</li>
                  <li>Multiple RSS source management</li>
                  <li>Automatic article extraction and parsing</li>
                  <li>Duplicate detection and filtering</li>
                  <li>MongoDB storage with metadata</li>
                  <li>Integration with Live Political Monitor</li>
                </ul>
              </div>
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Data Processing</h4>
                <ul className="info-list">
                  <li>Title, description, link extraction</li>
                  <li>Publication date parsing</li>
                  <li>Source tracking and attribution</li>
                  <li>Category and topic tagging</li>
                  <li>Automatic embedding generation (optional)</li>
                </ul>
                <p style={{ marginTop: 'var(--space-lg)', fontSize: '0.9rem', color: 'var(--text-tertiary)' }}>
                  <strong>Use Case:</strong> Powers Live Political Monitor with real-time data, 
                  enables fast query responses without repeated API calls
                </p>
              </div>
            </div>
          </div>

          {/* Deep Investigative Reporter */}
          <div className="info-card" style={{ marginBottom: 'var(--space-2xl)' }}>
            <h3>🔍 Deep Investigative Reporter: Strategic Intelligence Analysis</h3>
            <p style={{ marginBottom: 'var(--space-lg)', fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
              Advanced investigative capabilities with specialized strategies for entity investigation, funding tracing, and pattern detection.
            </p>
            <div className="info-grid-2">
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Investigation Strategies</h4>
                <ul className="info-list">
                  <li>Entity investigation (track individuals, organizations)</li>
                  <li>Event mapping (timeline reconstruction)</li>
                  <li>Funding tracer (follow the money)</li>
                  <li>Strategic intelligence analysis</li>
                  <li>Causal extraction (cause-effect relationships)</li>
                  <li>Network building (relationship mapping)</li>
                  <li>Pattern detection (anomalies and trends)</li>
                </ul>
              </div>
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Advanced Features</h4>
                <ul className="info-list">
                  <li>Multiple investigation strategies</li>
                  <li>Cross-reference validation</li>
                  <li>Source credibility assessment</li>
                  <li>Hypothesis generation and testing</li>
                  <li>Interactive network visualizations</li>
                  <li>Comprehensive reporting</li>
                </ul>
                <p style={{ marginTop: 'var(--space-lg)', fontSize: '0.9rem', color: 'var(--text-tertiary)' }}>
                  <strong>Example:</strong> "Investigate funding sources for political campaign X" 
                  → Traces donations → Maps relationships → Identifies patterns → Generates network graph
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Sentiment Analyzer Deep Dive */}
        <section className="info-section" style={{ display: 'none' }}>
          <h2 className="info-section-title">Sentiment Analyzer: Advanced Multi-Node Architecture</h2>
          <div className="info-card">
            <p style={{ marginBottom: 'var(--space-xl)', fontSize: '1.1rem', color: 'var(--text-secondary)' }}>
              Our most sophisticated sub-agent featuring an <strong>iterative quality-checking loop</strong> to combat 
              language bias and ensure geopolitically accurate sentiment analysis.
            </p>

            <div className="workflow-container">
              <div className="workflow-card" style={{ border: '2px solid var(--primary)' }}>
                <div className="workflow-number">1</div>
                <div className="workflow-content">
                  <h3>Query Analyzer</h3>
                  <p>
                    Parses the sentiment query and extracts target countries, topics, and analysis parameters.
                  </p>
                  <div className="workflow-example">
                    <strong>Input:</strong> "Analyze sentiment on Hamas in US and Iran"<br/>
                    <strong>Output:</strong> Countries: [US, Iran], Topic: Hamas, Mode: Comparative
                  </div>
                </div>
              </div>

              <div className="workflow-card">
                <div className="workflow-number">2</div>
                <div className="workflow-content">
                  <h3>Search Executor</h3>
                  <p>
                    Executes <strong>country-specific Tavily searches</strong> using dynamic search parameters. 
                    In iteration 0, uses standard queries. In iterations 1+, applies domain filtering and 
                    country-specific queries to combat language bias.
                  </p>
                  <div className="workflow-example">
                    <strong>Iteration 0:</strong> "Hamas public opinion United States"<br/>
                    <strong>Iteration 1:</strong> Targets local domains (e.g., .ir for Iran) with translated queries
                  </div>
                </div>
              </div>

              <div className="workflow-card">
                <div className="workflow-number">3</div>
                <div className="workflow-content">
                  <h3>Sentiment Scorer</h3>
                  <p>
                    Uses LLM (temperature=0) to analyze article content and assign sentiment scores (-1.0 to +1.0) 
                    with justification for each country.
                  </p>
                  <div className="workflow-example">
                    <strong>Output:</strong> US: -0.75 (negative), Iran: +0.45 (positive)
                  </div>
                </div>
              </div>

              <div className="workflow-card">
                <div className="workflow-number">4</div>
                <div className="workflow-content">
                  <h3>Bias Detector</h3>
                  <p>
                    Analyzes sources for media bias, geographic diversity, and source credibility. 
                    Identifies potential biases in the data collection.
                  </p>
                  <div className="workflow-example">
                    <strong>Checks:</strong> Western vs local media, domain diversity, publication dates
                  </div>
                </div>
              </div>

              <div className="workflow-card" style={{ border: '2px solid #d9f378' }}>
                <div className="workflow-number">5</div>
                <div className="workflow-content">
                  <h3>Quality Checker (Iteration Control) ⭐</h3>
                  <p>
                    <strong>The key innovation:</strong> Analyzes search result quality and decides whether to iterate. 
                    Detects language bias (too much English for non-English countries), source homogeneity, 
                    and insufficient data.
                  </p>
                  <div className="workflow-example">
                    <strong>Language Bias Detection:</strong><br/>
                    • Calculates English content ratio (with heuristics for non-English domains)<br/>
                    • Analyzes source diversity score<br/>
                    • If bias detected → Generate new search params → Loop back to Search Executor<br/>
                    <br/>
                    <strong>Dynamic Search Params:</strong><br/>
                    • Country-specific domain lists (e.g., tehrantimes.com, presstv.ir for Iran)<br/>
                    • Translated/localized queries<br/>
                    • Max 3 iterations to prevent infinite loops
                  </div>
                </div>
              </div>

              <div className="workflow-card">
                <div className="workflow-number">6</div>
                <div className="workflow-content">
                  <h3>Synthesizer</h3>
                  <p>
                    Combines sentiment scores, bias analysis, and source data into a comprehensive report 
                    with geographic breakdown and key insights.
                  </p>
                  <div className="workflow-example">
                    <strong>Output:</strong> Structured sentiment data + Bias report + Source citations
                  </div>
                </div>
              </div>

              <div className="workflow-card">
                <div className="workflow-number">7</div>
                <div className="workflow-content">
                  <h3>Visualizer</h3>
                  <p>
                    Generates visualizations (by default: bar chart + table). User can request infographics 
                    on-demand for rich dashboard displays.
                  </p>
                  <div className="workflow-example">
                    <strong>Default:</strong> Sentiment bar chart + HTML table<br/>
                    <strong>On-demand:</strong> Key metrics dashboard, comparison infographic
                  </div>
                </div>
              </div>
            </div>

            {/* Iteration Loop Diagram */}
            <div style={{ marginTop: 'var(--space-3xl)' }}>
              <h3 style={{ marginBottom: 'var(--space-lg)' }}>Iteration Loop: Combating Language Bias</h3>
              <div className="streaming-flow">
                <div className="stream-item" style={{ background: 'rgba(217, 243, 120, 0.1)' }}>
                  <strong>Iteration 0</strong>
                  <p>Standard search</p>
                </div>
                <div className="stream-arrow">→</div>
                <div className="stream-item" style={{ background: 'rgba(217, 243, 120, 0.2)' }}>
                  <strong>Quality Check</strong>
                  <p>Detect bias?</p>
                </div>
                <div className="stream-arrow">→</div>
                <div className="stream-item" style={{ background: 'rgba(217, 243, 120, 0.3)' }}>
                  <strong>Iteration 1+</strong>
                  <p>Domain filtering</p>
                </div>
                <div className="stream-arrow">→</div>
                <div className="stream-item" style={{ background: 'rgba(217, 243, 120, 0.4)' }}>
                  <strong>Quality Check</strong>
                  <p>Improved?</p>
                </div>
                <div className="stream-arrow">→</div>
                <div className="stream-item" style={{ background: 'var(--primary)' }}>
                  <strong>Stop</strong>
                  <p>Quality acceptable</p>
                </div>
              </div>
            </div>

            {/* Key Metrics */}
            <div style={{ marginTop: 'var(--space-3xl)' }}>
              <h3 style={{ marginBottom: 'var(--space-lg)' }}>Technical Specifications</h3>
              <div className="info-grid-3">
                <div className="info-stat-card">
                  <div className="info-stat-value">7</div>
                  <div className="info-stat-label">Node Workflow</div>
                </div>
                <div className="info-stat-card">
                  <div className="info-stat-value">3</div>
                  <div className="info-stat-label">Max Iterations</div>
                </div>
                <div className="info-stat-card">
                  <div className="info-stat-value">70%</div>
                  <div className="info-stat-label">English Threshold</div>
                </div>
                <div className="info-stat-card">
                  <div className="info-stat-value">8-20</div>
                  <div className="info-stat-label">Articles/Country</div>
                </div>
                <div className="info-stat-card">
                  <div className="info-stat-value">Advanced</div>
                  <div className="info-stat-label">Tavily Search Depth</div>
                </div>
                <div className="info-stat-card">
                  <div className="info-stat-value">2-7</div>
                  <div className="info-stat-label">Default Artifacts</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Tavily Integration */}
        <section className="info-section">
          <h2 className="info-section-title">Tavily API Integration</h2>
          <div className="info-grid-3">
            <div className="info-feature-card">
              <div className="info-feature-icon">🔍</div>
              <h3>Search API</h3>
              <p>Real-time web search with AI-powered relevance ranking</p>
              <ul className="info-feature-list">
                <li>Basic & Advanced search modes</li>
                <li>Country-specific results</li>
                <li>Domain filtering</li>
                <li>Citation extraction</li>
              </ul>
            </div>
            
            <div className="info-feature-card">
              <div className="info-feature-icon">📄</div>
              <h3>Extract API</h3>
              <p>Deep content extraction from multiple URLs</p>
              <ul className="info-feature-list">
                <li>Markdown format output</li>
                <li>Batch URL processing</li>
                <li>Clean text extraction</li>
                <li>Metadata parsing</li>
              </ul>
            </div>
            
            <div className="info-feature-card">
              <div className="info-feature-icon">🕷️</div>
              <h3>Crawl API</h3>
              <p>Website crawling for comprehensive data gathering</p>
              <ul className="info-feature-list">
                <li>Multi-level crawling</li>
                <li>Smart link following</li>
                <li>Content aggregation</li>
                <li>Structured output</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Technology Stack */}
        <section className="info-section">
          <h2 className="info-section-title">Technology Stack</h2>
          <div className="info-grid-2">
            <div className="info-card">
              <h3>Backend</h3>
              <div className="tech-list">
                <div className="tech-item">
                  <span className="tech-name">Python 3.11</span>
                  <span className="tech-desc">Core Language</span>
                </div>
                <div className="tech-item">
                  <span className="tech-name">FastAPI</span>
                  <span className="tech-desc">Async Web Framework</span>
                </div>
                <div className="tech-item">
                  <span className="tech-name">LangGraph 0.6</span>
                  <span className="tech-desc">Agent Orchestration</span>
                </div>
                <div className="tech-item">
                  <span className="tech-name">Tavily API</span>
                  <span className="tech-desc">Real-time Web Search</span>
                </div>
                <div className="tech-item">
                  <span className="tech-name">MongoDB Atlas</span>
                  <span className="tech-desc">Database</span>
                </div>
                <div className="tech-item">
                  <span className="tech-name">Plotly</span>
                  <span className="tech-desc">Visualization</span>
                </div>
              </div>
            </div>
            
            <div className="info-card">
              <h3>Frontend</h3>
              <div className="tech-list">
                <div className="tech-item">
                  <span className="tech-name">React 19</span>
                  <span className="tech-desc">UI Library</span>
                </div>
                <div className="tech-item">
                  <span className="tech-name">TypeScript</span>
                  <span className="tech-desc">Type Safety</span>
                </div>
                <div className="tech-item">
                  <span className="tech-name">Vite</span>
                  <span className="tech-desc">Build Tool</span>
                </div>
                <div className="tech-item">
                  <span className="tech-name">Framer Motion</span>
                  <span className="tech-desc">Animations</span>
                </div>
                <div className="tech-item">
                  <span className="tech-name">REST API + WebSocket</span>
                  <span className="tech-desc">Dual Communication</span>
                </div>
                <div className="tech-item">
                  <span className="tech-name">Radix UI</span>
                  <span className="tech-desc">Accessible Components</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Showcase */}
        <section className="info-section">
          <h2 className="info-section-title">Key Features</h2>
          <div className="info-grid-2">
            <div className="info-feature-showcase">
              <div className="feature-number">01</div>
              <h3>Multi-Agent Collaboration</h3>
              <p>
                7-node master agent coordinates 8 specialized sub-agents, each with distinct 
                responsibilities. Agents communicate through a shared state graph, ensuring 
                seamless information flow and intelligent decision-making.
              </p>
            </div>
            
            <div className="info-feature-showcase">
              <div className="feature-number">02</div>
              <h3>Intelligent Web Crawling</h3>
              <p>
                Cognitive Crawler with 3-layer intelligence system: intent detection, domain 
                classification, and URL prioritization. Smart crawling with knowledge base storage 
                and RAG query support for semantic search.
              </p>
            </div>
            
            <div className="info-feature-showcase">
              <div className="feature-number">03</div>
              <h3>Investigative Journalism</h3>
              <p>
                Cost-optimized (91% cheaper) deep research agent with hypothesis testing, evidence 
                tracking, and publication-ready outputs. Generates timelines, network graphs, and 
                comprehensive investigative reports.
              </p>
            </div>
            
            <div className="info-feature-showcase">
              <div className="feature-number">04</div>
              <h3>Media Bias Analysis</h3>
              <p>
                Multi-source comparison detecting political lean, framing bias, and loaded language. 
                Identifies consensus points, divergences, and omissions across different media outlets 
                with visual spectrum charts.
              </p>
            </div>
            
            <div className="info-feature-showcase">
              <div className="feature-number">05</div>
              <h3>Sentiment Analysis</h3>
              <p>
                Advanced multi-country sentiment analysis with iterative quality-checking loop to 
                combat language bias. Includes domain filtering, source diversity validation, and 
                automatic artifact generation.
              </p>
            </div>
            
            <div className="info-feature-showcase">
              <div className="feature-number">06</div>
              <h3>Real-Time Monitoring</h3>
              <p>
                Hybrid RSS + Tavily monitoring with explosiveness scoring (0-100). Identifies breaking 
                stories, trending topics, and generates situation reports. 99.4% cost reduction in RSS mode.
              </p>
            </div>
            
            <div className="info-feature-showcase">
              <div className="feature-number">07</div>
              <h3>Strategic Intelligence</h3>
              <p>
                Deep Investigative Reporter with specialized strategies for entity investigation, 
                funding tracing, event mapping, and pattern detection. Comprehensive network 
                visualizations and cross-reference validation.
              </p>
            </div>
            
            <div className="info-feature-showcase">
              <div className="feature-number">08</div>
              <h3>Knowledge Base & RAG</h3>
              <p>
                Retrieval Augmented Generation with MongoDB vector search and embeddings. Query stored 
                content semantically, integrate with Aleph data, Wayback Machine, and multiple extraction 
                methods (Jina AI, Trafilatura).
              </p>
            </div>
          </div>
        </section>

        {/* Deployment */}
        <section className="info-section">
          <h2 className="info-section-title">AWS Deployment</h2>
          <div className="info-card">
            <div className="deployment-diagram">
              <div className="deploy-box deploy-cloudfront">
                <h4>🌐 CloudFront CDN</h4>
                <p>Global distribution with SSL</p>
                <div className="deploy-url">d2dk8wkh2d0mmy.cloudfront.net</div>
              </div>
              
              <div className="deploy-split">
                <div className="deploy-box deploy-s3">
                  <h4>📦 S3 Bucket</h4>
                  <p>Frontend hosting (private)</p>
                  <ul>
                    <li>Origin Access Control</li>
                    <li>Static assets</li>
                    <li>Artifact storage</li>
                  </ul>
                </div>
                
                <div className="deploy-box deploy-eb">
                  <h4>⚙️ Elastic Beanstalk</h4>
                  <p>Backend hosting (t3.medium)</p>
                  <ul>
                    <li>Auto-scaling enabled</li>
                    <li>Health monitoring</li>
                    <li>Environment variables</li>
                  </ul>
                </div>
              </div>
              
              <div className="deploy-box deploy-mongo">
                <h4>🗄️ MongoDB Atlas</h4>
                <p>Database cluster (M0 Free Tier)</p>
                <ul>
                  <li>User sessions</li>
                  <li>Agent outputs</li>
                  <li>Execution logs</li>
                  <li>Analytics data</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Try It Out CTA */}
        <section className="info-section">
          <div className="info-cta">
            <h2>Experience It Yourself</h2>
            <p>Ready to see the Political Analyst Workbench in action?</p>
            <button 
              className="info-cta-button"
              onClick={() => navigate('/chat')}
            >
              Launch Chat Interface →
            </button>
          </div>
        </section>

        {/* Footer */}
        <footer className="info-footer">
          <p>Built with ❤️ using LangGraph, Tavily, and Modern Web Technologies</p>
          <p className="info-footer-links">
            <a href="https://github.com/Samrat2803/cognitive-core" target="_blank" rel="noopener noreferrer">GitHub</a>
            <span>•</span>
            <a href="http://political-analyst-backend-prod.eba-tf2vrc23.us-east-1.elasticbeanstalk.com/docs" target="_blank" rel="noopener noreferrer">API Docs</a>
            <span>•</span>
            <a href="/" onClick={(e) => { e.preventDefault(); navigate('/'); }}>Home</a>
          </p>
        </footer>
      </div>
    </div>
  );
}

