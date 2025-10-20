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


        {/* All Operational Sub-Agents Showcase */}
        <section className="info-section">
          <h2 className="info-section-title">🎯 Three Flagship Capabilities</h2>
          
          {/* Investigative Journalist */}
          <div className="info-card" style={{ marginBottom: 'var(--space-2xl)' }}>
            <h3>📰 Investigative Journalist: Hypothesis-Driven Research</h3>
            <p style={{ marginBottom: 'var(--space-lg)', fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
              Cost-optimized investigative agent with real journalist tools and hypothesis testing framework.
            </p>
            <div className="info-grid-2">
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Hypothesis Testing Approach</h4>
                <ul className="info-list">
                  <li>Competing hypotheses framework - tests multiple explanations</li>
                  <li>Evidence-based validation with scoring</li>
                  <li>Iterative refinement as new data emerges</li>
                </ul>
                <h4 style={{ color: 'var(--primary)', marginTop: 'var(--space-lg)', marginBottom: 'var(--space-md)' }}>Real Journalist Tools</h4>
                <ul className="info-list">
                  <li>Wayback Machine - historical archives</li>
                  <li>OCCRP Aleph - leaked docs & financial records</li>
                  <li>Free extraction - Jina AI + Trafilatura (83% success)</li>
                  <li>Entity tracking & anomaly detection</li>
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
                    <div className="info-stat-label">Free Extraction</div>
                  </div>
                  <div className="info-stat-card">
                    <div className="info-stat-value">$0.036</div>
                    <div className="info-stat-label">Per Iteration</div>
                  </div>
                </div>
                <h4 style={{ color: 'var(--primary)', marginTop: 'var(--space-lg)', marginBottom: 'var(--space-md)' }}>Outputs</h4>
                <ul className="info-list">
                  <li>Publication-ready articles with evidence chains</li>
                  <li>Interactive timelines (vis.js)</li>
                  <li>Entity network graphs</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Cognitive Crawler */}
          <div className="info-card" style={{ marginBottom: 'var(--space-2xl)' }}>
            <h3>🧠 Cognitive Crawler: Intelligent Crawling + RAG Chat</h3>
            <p style={{ marginBottom: 'var(--space-lg)', fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
              Three-layer intelligence system for smart crawling, with semantic search and chat capabilities.
            </p>
            <div className="info-grid-2">
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>3-Layer Intelligence</h4>
                <ul className="info-list">
                  <li>Intent detection - "crawl entire site" vs "specific pages"</li>
                  <li>Domain classification - Authority (.gov) = full, News = specific</li>
                  <li>Smart prioritization - 100-point scoring system</li>
                </ul>
                <h4 style={{ color: 'var(--primary)', marginTop: 'var(--space-lg)', marginBottom: 'var(--space-md)' }}>Chunking Philosophy</h4>
                <ul className="info-list">
                  <li>Recursive text splitter - 3000 chars/chunk</li>
                  <li>400-char overlap for context preservation</li>
                  <li>Natural boundaries (paragraphs → sentences)</li>
                  <li>Multiple embeddings per document</li>
                </ul>
              </div>
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>RAG Retrieval Logic</h4>
                <ul className="info-list">
                  <li>MongoDB Vector Search (OpenAI 1536-dim embeddings)</li>
                  <li>Local (session) + Global (all data) modes</li>
                  <li>Top-k retrieval with similarity scoring</li>
                  <li>Min score filtering (0.3) removes noise</li>
                  <li>LLM synthesis with source attribution</li>
                </ul>
                <div className="info-grid-3" style={{ marginTop: 'var(--space-lg)' }}>
                  <div className="info-stat-card">
                    <div className="info-stat-value">3</div>
                    <div className="info-stat-label">Intelligence Layers</div>
                  </div>
                  <div className="info-stat-card">
                    <div className="info-stat-value">100</div>
                    <div className="info-stat-label">Priority Score</div>
                  </div>
                  <div className="info-stat-card">
                    <div className="info-stat-value">1536</div>
                    <div className="info-stat-label">Embedding Dims</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Live Political Monitor */}
          <div className="info-card" style={{ marginBottom: 'var(--space-2xl)' }}>
            <h3>🔴 Live Political Monitor: Real-Time Event Tracking</h3>
            <p style={{ marginBottom: 'var(--space-lg)', fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
              Hybrid RSS + Tavily monitoring with explosiveness scoring for breaking stories.
            </p>
            <div className="info-grid-2">
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Hybrid Architecture</h4>
                <ul className="info-list">
                  <li>Primary: RSS feeds (major news sources)</li>
                  <li>Fallback: Tavily Search for comprehensive coverage</li>
                  <li>3-hour intelligent caching</li>
                  <li>Topic clustering and breaking story detection</li>
                </ul>
                <h4 style={{ color: 'var(--primary)', marginTop: 'var(--space-lg)', marginBottom: 'var(--space-md)' }}>Explosiveness Algorithm (0-100)</h4>
                <ul className="info-list">
                  <li>LLM Rating: 30 points</li>
                  <li>Frequency: 25 points</li>
                  <li>Source Diversity: 20 points</li>
                  <li>Urgency Keywords: 15 points</li>
                  <li>Recency: 10 points</li>
                </ul>
              </div>
              <div>
                <h4 style={{ color: 'var(--primary)', marginBottom: 'var(--space-md)' }}>Performance</h4>
                <div className="info-grid-3">
                  <div className="info-stat-card">
                    <div className="info-stat-value">99.4%</div>
                    <div className="info-stat-label">Cost Reduction</div>
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
                <h4 style={{ color: 'var(--primary)', marginTop: 'var(--space-lg)', marginBottom: 'var(--space-md)' }}>Auto SitRep Generation</h4>
                <ul className="info-list">
                  <li>PDF reports (professional formatting)</li>
                  <li>HTML dashboards (interactive)</li>
                  <li>TXT (email-ready) + JSON (API)</li>
                </ul>
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

