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
                  A sophisticated AI-powered political analysis platform that combines 
                  <strong> LangGraph's multi-agent architecture</strong> with <strong>Tavily's real-time web search</strong> 
                  to deliver comprehensive political insights with automatic visualization generation.
                </p>
                <ul className="info-list">
                  <li>7-Node Master Agent orchestrating complex workflows</li>
                  <li>9+ Specialized Sub-Agents for diverse analysis types</li>
                  <li>Real-time web data integration via Tavily API</li>
                  <li>Automatic chart and graph generation</li>
                  <li>WebSocket streaming for live updates</li>
                </ul>
              </div>
              <div className="info-stats">
                <div className="info-stat-card">
                  <div className="info-stat-value">7</div>
                  <div className="info-stat-label">Master Agent Nodes</div>
                </div>
                <div className="info-stat-card">
                  <div className="info-stat-value">9+</div>
                  <div className="info-stat-label">Specialized Sub-Agents</div>
                </div>
                <div className="info-stat-card">
                  <div className="info-stat-value">35+</div>
                  <div className="info-stat-label">Artifact Types</div>
                </div>
                <div className="info-stat-card">
                  <div className="info-stat-value">15+</div>
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
                <h4>Sub-Agents (9 Specialized Agents)</h4>
                <div className="arch-grid">
                  <div className="arch-subagent arch-live">Sentiment Analyzer ✓</div>
                  <div className="arch-subagent arch-pending">Media Bias Detector</div>
                  <div className="arch-subagent arch-pending">Fact Checker</div>
                  <div className="arch-subagent arch-pending">Entity Extractor</div>
                  <div className="arch-subagent arch-pending">Crisis Tracker</div>
                  <div className="arch-subagent arch-live">Live Monitor ✓</div>
                  <div className="arch-subagent arch-live">SitRep Generator ✓</div>
                  <div className="arch-subagent arch-pending">Policy Brief</div>
                  <div className="arch-subagent arch-pending">Comparative Analysis</div>
                </div>
              </div>
              
              <div className="arch-arrow">↓</div>
              
              <div className="arch-layer">
                <h4>Integrated Tools (15+)</h4>
                <div className="arch-grid">
                  <div className="arch-subagent arch-live">Tavily Search ✓</div>
                  <div className="arch-subagent arch-live">Tavily Extract ✓</div>
                  <div className="arch-subagent arch-live">Tavily Crawl ✓</div>
                  <div className="arch-subagent arch-live">Chart Generator ✓</div>
                  <div className="arch-subagent arch-live">Map Visualizer ✓</div>
                  <div className="arch-subagent arch-live">Infographic Maker ✓</div>
                  <div className="arch-subagent arch-live">Reel Generator ✓</div>
                  <div className="arch-subagent arch-live">Deck Creator ✓</div>
                  <div className="arch-subagent arch-live">Mind Map Builder ✓</div>
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
                7-node master agent coordinates 9+ specialized sub-agents, each with distinct 
                responsibilities. Agents communicate through a shared state graph, ensuring 
                seamless information flow and intelligent decision-making.
              </p>
            </div>
            
            <div className="info-feature-showcase">
              <div className="feature-number">02</div>
              <h3>Real-Time Web Intelligence</h3>
              <p>
                Tavily API integration provides access to current, accurate web data. Every analysis 
                is backed by live sources with automatic citation extraction and credibility scoring.
              </p>
            </div>
            
            <div className="info-feature-showcase">
              <div className="feature-number">03</div>
              <h3>Auto-Visualization</h3>
              <p>
                Intelligent artifact generation system automatically creates charts, graphs, maps, 
                and infographics when data supports visualization. 35+ artifact types available.
              </p>
            </div>
            
            <div className="info-feature-showcase">
              <div className="feature-number">04</div>
              <h3>Dual API Architecture</h3>
              <p>
                REST APIs for standard operations (health checks, metadata) and WebSocket streaming 
                for real-time updates. See agent decisions, tool calls, and intermediate results as they happen.
              </p>
            </div>
            
            <div className="info-feature-showcase">
              <div className="feature-number">05</div>
              <h3>Sentiment Analysis</h3>
              <p>
                Deep sentiment analysis across multiple sources and regions. Generates sentiment 
                maps, radar charts, trend lines, and bias reports automatically.
              </p>
            </div>
            
            <div className="info-feature-showcase">
              <div className="feature-number">06</div>
              <h3>Live Political Monitor</h3>
              <p>
                Continuous monitoring of political events with "explosiveness" scoring. Identifies 
                breaking stories, tracks trending topics, and generates situation reports.
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

