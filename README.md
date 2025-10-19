# Political Analyst Workbench

<div align="center">

[![Deploy Status](https://img.shields.io/badge/deploy-success-brightgreen)]()
[![Backend Status](https://img.shields.io/badge/backend-healthy-green)](http://political-analyst-backend-prod.eba-tf2vrc23.us-east-1.elasticbeanstalk.com/health)
[![Agent Progress](https://img.shields.io/badge/agents-3/9%20operational-orange)]()
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue)]()
[![React](https://img.shields.io/badge/react-19-61dafb)]()
[![LangGraph](https://img.shields.io/badge/LangGraph-0.6-purple)]()

**An AI-powered political analysis platform with real-time web search, intelligent agents, and automatic visualization generation**

[🚀 Live Demo](#-live-deployment) · [📚 Documentation](#-documentation) · [🛠️ Tech Stack](#️-technology-stack) · [⚡ Quick Start](#-quick-start)

</div>

---

## 🎯 For New Teams - DEPLOYMENT

**Deploying this application? Start here:**

1. **📖 Read First:** [`START_HERE_DEPLOYMENT.md`](START_HERE_DEPLOYMENT.md) (5 min overview)
2. **📘 Detailed Guide:** [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) (complete step-by-step)
3. **⏱ Time Required:** 45-60 minutes (first time), 15-20 minutes (updates)
4. **💰 Cost:** ~$38-50/month

**All issues solved:**
- ✅ WebSocket SSL configuration (wss://)
- ✅ Load balancer setup for auto-scaling
- ✅ CloudFront with free SSL
- ✅ Package size optimization (109MB → 22MB)
- ✅ CORS configuration
- ✅ Secrets management

**Don't start deployment without reading the guides above!**

---

## 🎯 Overview

The Political Analyst Workbench is a sophisticated AI-powered research platform that combines **LangGraph's Master Agent architecture** with **Tavily's real-time web search** to deliver comprehensive political analysis with automatic chart and graph generation.

### 🚀 Recent Updates (October 2025)

- ✅ **Repository Cleanup:** Removed V1 codebase, 144 files deleted (53K lines)
- ✅ **Agent Expansion Project:** 3/9 specialized sub-agents completed (33%)
- ✅ **Sentiment Analyzer:** Multi-country sentiment analysis with bias detection
- ✅ **Live Political Monitor:** Real-time event tracking with explosiveness scoring
- ✅ **SitRep Generator:** Automated situation reports (daily/weekly)
- ✅ **3 Shared Tools:** Infographic, Reel, and Deck generators
- 🎯 **Status:** Ahead of schedule, 6 more agents in development

### ✨ Key Features

- 🤖 **7-Node LangGraph Master Agent** - Intelligent multi-step reasoning and planning
- 🔬 **9 Specialized Sub-Agents** - Domain-specific analysis capabilities (3 operational)
- 🌐 **Real-Time Web Search** - Powered by Tavily API for current, accurate data
- 📊 **Auto-Visualization** - Automatic generation of charts, graphs, and infographics
- 🎨 **Professional Artifacts** - Infographics, reels, and presentation decks
- ⚡ **WebSocket Streaming** - Real-time response updates as analysis progresses
- 💬 **Advanced Chat Interface** - Modern UI with citations and source linking
- 🌓 **Theme Support** - Dark/light mode with smooth transitions
- 📱 **Responsive Design** - Works seamlessly across devices

---

## 🚀 Live Deployment

### Production URLs

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | [https://d2dk8wkh2d0mmy.cloudfront.net](https://d2dk8wkh2d0mmy.cloudfront.net) | ✅ Live |
| **Info Page** | [/info](https://d2dk8wkh2d0mmy.cloudfront.net/info) | 🎬 Demo Ready |
| **Backend API** | [https://d1h4cjcbl77aah.cloudfront.net](https://d1h4cjcbl77aah.cloudfront.net) | ✅ Live |
| **API Health** | [/health](https://d1h4cjcbl77aah.cloudfront.net/health) | ✅ Healthy |
| **API Docs** | [/docs](https://d1h4cjcbl77aah.cloudfront.net/docs) | 📖 Available |
| **WebSocket** | `wss://d1h4cjcbl77aah.cloudfront.net/ws/analyze` | ✅ Connected |

> **Note**: Frontend may take 15-20 minutes to propagate globally via CloudFront

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (Vite + React)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chat Panel   │  │ Artifact     │  │ Citations    │      │
│  │              │  │ Viewer       │  │ Panel        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓ WebSocket/HTTP
┌─────────────────────────────────────────────────────────────┐
│              Backend (FastAPI + LangGraph)                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         LangGraph Master Agent (7 Nodes)            │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ 1. Conversation Manager  →  Initialize context      │    │
│  │ 2. Strategic Planner     →  Plan execution          │    │
│  │ 3. Tool Executor         →  Execute Tavily search   │    │
│  │ 4. Decision Gate         →  Evaluate completeness   │    │
│  │ 5. Response Synthesizer  →  Generate response       │    │
│  │ 6. Artifact Decision     →  Determine if viz needed │    │
│  │ 7. Artifact Creator      →  Generate charts/graphs  │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Specialized Sub-Agents (9 Planned)          │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ ✅ Sentiment Analyzer     →  Multi-country sentiment│    │
│  │ ✅ Live Political Monitor →  Real-time events       │    │
│  │ ✅ SitRep Generator       →  Daily/weekly reports   │    │
│  │ 🔄 Media Bias Detector    →  Bias analysis          │    │
│  │ 🔄 Fact Checker           →  Truth verification     │    │
│  │ 🔄 Entity Extractor       →  Relationship mapping   │    │
│  │ 🔄 Crisis Tracker         →  Event monitoring       │    │
│  │ 🔄 Comparative Analysis   →  Cross-entity compare   │    │
│  │ 🔄 Policy Brief Generator →  Policy analysis        │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Shared Tools (3 Completed)                  │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ ✅ Infographic Generator  →  Visual summaries       │    │
│  │ ✅ Reel Generator         →  Video animations       │    │
│  │ ✅ Deck Generator         →  PowerPoint decks       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
          ↓                    ↓                    ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Tavily API  │    │  MongoDB     │    │  AWS S3      │
│  (Search)    │    │  (Storage)   │    │  (Artifacts) │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Master Agent Workflow

The Master Agent follows an intelligent multi-step process:
1. **Analyzes** user query for intent and requirements
2. **Plans** optimal tool usage and data gathering
3. **Executes** real-time web searches via Tavily
4. **Evaluates** if additional data is needed (up to 3 iterations)
5. **Delegates** to specialized sub-agents when domain expertise needed
6. **Synthesizes** comprehensive responses with citations
7. **Generates** visualizations when data allows (charts, graphs, artifacts)

### Specialized Sub-Agents

Each sub-agent operates independently with its own LangGraph workflow:

#### ✅ **Operational (3/9)**
- **Sentiment Analyzer** - Analyzes sentiment across countries with bias detection
- **Live Political Monitor** - Tracks breaking events with explosiveness scoring  
- **SitRep Generator** - Creates professional situation reports

#### 🔄 **In Development (6/9)**
- **Media Bias Detector** - Identifies bias in sources
- **Fact Checker** - Verifies claims with evidence chains
- **Entity Extractor** - Maps relationships between entities
- **Crisis Tracker** - Monitors and tracks crisis events
- **Comparative Analysis** - Compares policies, positions, entities
- **Policy Brief Generator** - Generates comprehensive policy briefs

---

## 🛠️ Technology Stack

### Backend
- **Python 3.11** - Core language
- **FastAPI** - High-performance async web framework
- **LangGraph 0.6** - Agent orchestration and workflow
- **LangChain** - LLM integration and tooling
- **Tavily API** - Real-time web search
- **MongoDB Atlas** - Data persistence
- **Plotly** - Dynamic chart generation
- **AWS S3** - Artifact storage

### Frontend
- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Lightning-fast build tool
- **Radix UI** - Accessible component primitives
- **Framer Motion** - Smooth animations
- **React Markdown** - Rich text rendering
- **WebSocket** - Real-time communication

### Infrastructure
- **AWS Elastic Beanstalk** - Backend hosting (t3.medium)
- **AWS S3** - Static frontend hosting (private bucket)
- **AWS CloudFront** - Global CDN with SSL
- **MongoDB Atlas** - Managed database
- **Origin Access Control** - Secure CloudFront→S3

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (optional)
- AWS account (for deployment)
- API Keys: [Tavily](https://tavily.com), [OpenAI](https://openai.com)

### Local Development

#### Backend Setup
```bash
cd backend_v2

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run development server
python app.py
```

Backend will be available at: `http://localhost:8000`

#### Frontend Setup
```bash
cd Frontend_v2

# Install dependencies
npm install

# Configure API endpoint (optional)
# Edit src/services/WebSocketService.ts if needed

# Run development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## 🚀 Deployment

### Deploy to AWS

#### Backend Deployment
```bash
cd backend_v2
./aws-deploy-backend.sh
```

#### Frontend Deployment
```bash
cd Frontend_v2
./aws-deploy-secure.sh  # Recommended: Private S3 with OAC
# OR
./aws-deploy.sh         # Alternative: Public S3
```

For detailed deployment instructions, see [documentation/deployment/](documentation/deployment/)

---

## 📚 Documentation

### User Guides
- **[Deployment Guide](documentation/deployment/DEPLOYMENT_GUIDE_V2.md)** - Complete AWS deployment walkthrough
- **[Quick Deploy](documentation/deployment/QUICK_DEPLOY_V2.md)** - Fast deployment reference
- **[Setup Guide](documentation/setup/SETUP_V2_GUIDE.md)** - Local development setup
- **[Troubleshooting](documentation/troubleshooting/)** - Common issues and solutions
- **[API Documentation](http://political-analyst-backend-prod.eba-tf2vrc23.us-east-1.elasticbeanstalk.com/docs)** - Interactive API docs

### Developer Guides (Agent Development)
- **[START HERE (Agents)](backend_v2/START_HERE.md)** - Agent development quick start
- **[Agent Development Guide](backend_v2/AGENT_DEVELOPMENT_GUIDE.md)** - Complete development process
- **[Integration Protocol](backend_v2/INTEGRATION_PROTOCOL.md)** - Testing and integration workflow
- **[Complete Agent Roadmap](backend_v2/COMPLETE_AGENT_ROADMAP.md)** - All 9 agents overview
- **[Implementation Status](backend_v2/IMPLEMENTATION_STATUS.md)** - Current progress tracking

---

## 📋 Project Structure

```
political-analyst-workbench/
├── backend_v2/                 # Backend (LangGraph Master Agent + FastAPI)
│   ├── langgraph_master_agent/ # Master Agent implementation
│   │   ├── nodes/              # 7 core master agent nodes
│   │   ├── sub_agents/         # 9 specialized sub-agents
│   │   │   ├── sentiment_analyzer/        ✅ COMPLETE
│   │   │   ├── live_political_monitor/    ✅ COMPLETE
│   │   │   ├── sitrep_generator/          ✅ COMPLETE
│   │   │   ├── media_bias_detector/       🔄 In Dev
│   │   │   ├── fact_checker/              🔄 In Dev
│   │   │   ├── entity_relationship_extractor/ 🔄 In Dev
│   │   │   ├── crisis_event_tracker/      🔄 In Dev
│   │   │   ├── comparative_analysis/      🔄 In Dev
│   │   │   └── policy_brief_generator/    🔄 In Dev
│   │   ├── tools/              # Master agent tools
│   │   └── graph.py            # Main LangGraph workflow
│   ├── shared/                 # Shared utilities
│   │   ├── infographic_generator.py  ✅ (780 lines)
│   │   ├── reel_generator.py         ✅ (375 lines)
│   │   ├── deck_generator.py         ✅ (425 lines)
│   │   └── visualization_factory.py  (805 lines)
│   ├── services/               # MongoDB, S3 services
│   ├── artifacts/              # Generated charts (local)
│   ├── app.py                  # FastAPI application
│   └── requirements.txt        # Python dependencies
│
├── Frontend_v2/                # Frontend (Vite + React + TypeScript)
│   ├── src/
│   │   ├── components/         # UI components (80+)
│   │   ├── services/           # API and WebSocket
│   │   └── hooks/              # Custom React hooks
│   ├── e2e/                    # Playwright tests
│   └── package.json            # Node dependencies
│
├── documentation/              # Organized documentation
│   ├── deployment/             # Deployment guides
│   ├── setup/                  # Setup instructions
│   ├── development/            # Dev guidelines
│   └── troubleshooting/        # Issue resolution
│
├── scripts/                    # Utility scripts
├── config/                     # Playwright configurations
├── README.md                   # This file
├── START_HERE_DEPLOYMENT.md    # Quick deployment guide
└── DEPLOYMENT_GUIDE.md         # Detailed deployment guide
```

---

## 🔬 Agent Expansion Project

### Overview

We're expanding the platform with **9 specialized sub-agents** that provide domain-specific analysis capabilities. Each agent operates independently with its own LangGraph workflow and can be delegated tasks by the Master Agent.

### Progress Tracker

```
Phase 0 (Foundation):      ▓▓▓▓▓▓▓░░░ 67% (2/3)
Phase 1 (Quick Wins):      ▓▓▓▓░░░░░░ 33% (1/3)
Phase 2 (Premium Features): ░░░░░░░░░░  0% (0/3)

Overall Completion:        ▓▓▓░░░░░░░ 33% (3/9 agents)
Shared Tools:              ▓▓▓▓▓▓▓▓▓▓ 100% (3/3 tools) ✅
```

### Completed Agents

#### 1. Sentiment Analyzer 😊😐😠
- **Status:** ✅ Fully Operational
- **Capabilities:** Multi-country sentiment analysis, bias detection (7 types)
- **Artifacts:** Bar charts, radar charts, sentiment maps
- **Performance:** 31s execution, 0.70-0.80 sentiment scores

#### 2. Live Political Monitor 🔴
- **Status:** ✅ Fully Operational  
- **Implementation:** RSS-based (default since Oct 19, 2025)
- **Capabilities:** Real-time event tracking, explosiveness scoring (0-100)
- **Cost:** $0.00003 per query (99.4% cheaper than Tavily-only)
- **Performance:** 2-5 seconds response time (60% faster)
- **Artifacts:** JSON reports, explosive topic identification
- **Fallback:** Tavily-based backup available at `/api/live-monitor/explosive-topics-tavily`

#### 3. SitRep Generator 📋
- **Status:** ✅ Fully Operational
- **Capabilities:** Daily/weekly situation reports, professional formatting
- **Artifacts:** PDF reports, HTML dashboards, email-ready text
- **Performance:** Comprehensive reports with multiple sections

### In Development (6 Agents)

- 🔄 **Media Bias Detector** - Bias spectrum analysis
- 🔄 **Fact Checker** - Claim verification with evidence chains
- 🔄 **Entity Extractor** - Relationship mapping and network graphs
- 🔄 **Crisis Tracker** - Crisis event monitoring and tracking
- 🔄 **Comparative Analysis** - Cross-entity comparisons
- 🔄 **Policy Brief Generator** - Comprehensive policy analysis

### Shared Tools (All Complete)

- ✅ **Infographic Generator** - Visual summaries (780 lines, 9 templates)
- ✅ **Reel Generator** - Video animations (375 lines, MP4 exports)
- ✅ **Deck Generator** - PowerPoint decks (425 lines, PPTX exports)

### Development Approach

Each agent follows a **modular, isolated development approach**:
1. Built independently in `sub_agents/{agent_name}/` folder
2. Tested standalone before integration
3. Zero impact on existing code
4. Clean LangGraph workflow with 3-5 nodes
5. Documented with README and validation reports

For developers: See `backend_v2/START_HERE.md` for complete development guide.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📊 Performance & Scalability

### Master Agent
- **Response Time**: 3-8 seconds for analysis
- **Concurrent Users**: Supports multiple simultaneous connections
- **Artifact Generation**: +1-2 seconds for visualizations
- **Caching**: Intelligent query caching for faster responses
- **Scalability**: Horizontal scaling via AWS Auto Scaling

### Sub-Agents (Operational)
- **Sentiment Analyzer**: ~31s execution, 10+ sources analyzed
- **Live Political Monitor**: ~27s execution, 27+ articles processed
- **SitRep Generator**: Variable (depends on report complexity)

### Infrastructure
- **Backend Instance**: AWS t3.medium (2 vCPU, 4GB RAM)
- **Database**: MongoDB Atlas M0 (Free Tier)
- **CDN**: CloudFront (Global distribution)
- **Storage**: S3 (Artifacts and static assets)

---

## 🔒 Security

- ✅ Private S3 buckets with Origin Access Control
- ✅ CORS properly configured for production
- ✅ Environment variables for sensitive data
- ✅ HTTPS enforced via CloudFront
- ✅ API keys never exposed to client
- ✅ MongoDB Atlas with security best practices

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangGraph** by LangChain for agent orchestration
- **Tavily** for real-time web search API
- **OpenAI** for language model capabilities
- **AWS** for scalable cloud infrastructure
- **Plotly** for interactive visualizations

---

## 📞 Support

For issues, questions, or feedback:
- 📖 Check the [Documentation](documentation/)
- 🐛 [Report a Bug](https://github.com/Samrat2803/cognitive-core/issues)
- 💡 [Request a Feature](https://github.com/Samrat2803/cognitive-core/issues)
- 📧 GitHub: [Samrat2803/cognitive-core](https://github.com/Samrat2803/cognitive-core)

---

<div align="center">

**Built with ❤️ using LangGraph, Tavily, and Modern Web Technologies**

---

**Last Updated:** October 2, 2025  
**Version:** 2.0.0 (Agent Expansion in Progress)  
**Status:** 🟢 Operational | 🔨 Actively Developing

[⬆ Back to Top](#political-analyst-workbench)

</div>
