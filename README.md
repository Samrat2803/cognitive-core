# Political Analyst Workbench

<div align="center">

[![Deploy Status](https://img.shields.io/badge/deploy-success-brightgreen)]()
[![Backend Status](https://img.shields.io/badge/backend-healthy-green)](http://political-analyst-backend-prod.eba-tf2vrc23.us-east-1.elasticbeanstalk.com/health)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue)]()
[![React](https://img.shields.io/badge/react-19-61dafb)]()
[![LangGraph](https://img.shields.io/badge/LangGraph-0.6-purple)]()

**An AI-powered political analysis platform with real-time web search, intelligent agents, and automatic visualization generation**

[🚀 Live Demo](#-live-deployment) · [📚 Documentation](#-documentation) · [🛠️ Tech Stack](#️-technology-stack) · [⚡ Quick Start](#-quick-start)

</div>

---

## 🎯 Overview

The Political Analyst Workbench is a sophisticated AI-powered research platform that combines **LangGraph's Master Agent architecture** with **Tavily's real-time web search** to deliver comprehensive political analysis with automatic chart and graph generation.

### ✨ Key Features

- 🤖 **7-Node LangGraph Master Agent** - Intelligent multi-step reasoning and planning
- 🌐 **Real-Time Web Search** - Powered by Tavily API for current, accurate data
- 📊 **Auto-Visualization** - Automatic generation of charts, graphs, and infographics
- ⚡ **WebSocket Streaming** - Real-time response updates as analysis progresses
- 💬 **Advanced Chat Interface** - Modern UI with citations and source linking
- 🎨 **Dynamic Artifacts** - Interactive visualizations with Plotly
- 🌓 **Theme Support** - Dark/light mode with smooth transitions
- 📱 **Responsive Design** - Works seamlessly across devices

---

## 🚀 Live Deployment

### Production URLs

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | [https://d2dk8wkh2d0mmy.cloudfront.net](https://d2dk8wkh2d0mmy.cloudfront.net) | ✅ Live |
| **Backend API** | [http://political-analyst-backend-prod.eba-tf2vrc23.us-east-1.elasticbeanstalk.com](http://political-analyst-backend-prod.eba-tf2vrc23.us-east-1.elasticbeanstalk.com) | ✅ Live |
| **API Health** | [/health](http://political-analyst-backend-prod.eba-tf2vrc23.us-east-1.elasticbeanstalk.com/health) | ✅ Healthy |
| **API Docs** | [/docs](http://political-analyst-backend-prod.eba-tf2vrc23.us-east-1.elasticbeanstalk.com/docs) | 📖 Available |

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
└─────────────────────────────────────────────────────────────┘
          ↓                    ↓                    ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Tavily API  │    │  MongoDB     │    │  AWS S3      │
│  (Search)    │    │  (Storage)   │    │  (Artifacts) │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Agent Workflow

The Master Agent follows an intelligent multi-step process:
1. **Analyzes** user query for intent and requirements
2. **Plans** optimal tool usage and data gathering
3. **Executes** real-time web searches via Tavily
4. **Evaluates** if additional data is needed (up to 3 iterations)
5. **Synthesizes** comprehensive responses with citations
6. **Generates** visualizations when data allows (charts, graphs)

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

#### Backend V2 Setup
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

#### Frontend V2 Setup
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

- **[Deployment Guide](documentation/deployment/DEPLOYMENT_GUIDE_V2.md)** - Complete AWS deployment walkthrough
- **[Quick Deploy](documentation/deployment/QUICK_DEPLOY_V2.md)** - Fast deployment reference
- **[Setup Guide](documentation/setup/SETUP_V2_GUIDE.md)** - Local development setup
- **[Troubleshooting](documentation/troubleshooting/)** - Common issues and solutions
- **[API Documentation](http://political-analyst-backend-prod.eba-tf2vrc23.us-east-1.elasticbeanstalk.com/docs)** - Interactive API docs

---

## 📋 Project Structure

```
political-analyst-workbench/
├── backend_v2/                 # V2 Backend (LangGraph Master Agent)
│   ├── langgraph_master_agent/ # Agent implementation
│   ├── shared/                 # Shared utilities
│   ├── services/               # MongoDB, S3 services
│   ├── artifacts/              # Generated charts (local)
│   ├── app.py                  # FastAPI application
│   └── requirements.txt        # Python dependencies
│
├── Frontend_v2/                # V2 Frontend (Vite + React)
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
└── config/                     # Configuration files
```

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

- **Response Time**: 3-8 seconds for analysis
- **Concurrent Users**: Supports multiple simultaneous connections
- **Artifact Generation**: +1-2 seconds for visualizations
- **Caching**: Intelligent query caching for faster responses
- **Scalability**: Horizontal scaling via AWS Auto Scaling

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
- 🐛 [Report a Bug](https://github.com/your-repo/issues)
- 💡 [Request a Feature](https://github.com/your-repo/issues)
- 📧 Contact: your-email@example.com

---

<div align="center">

**Built with ❤️ using LangGraph, Tavily, and Modern Web Technologies**

[⬆ Back to Top](#political-analyst-workbench)

</div>
