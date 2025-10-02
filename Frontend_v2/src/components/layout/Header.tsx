import { Brain, History, Settings } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import ConnectionStatus from '../ui/ConnectionStatus';
import { AgentTooltip, EnhancedTooltip, FeatureBadge } from '../ui/EnhancedTooltip';
import './Header.css';

export function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const isHomePage = location.pathname === '/';

  return (
    <header className="header">
      <AgentTooltip
        title="Cognitive Core Platform"
        description="Advanced political analysis powered by LangGraph multi-agent system with real-time data gathering"
        features={[
          'Master orchestration agent with sub-agents',
          'Sentiment analysis across regions',
          'Live political monitoring',
          'Interactive data visualizations'
        ]}
        position="bottom"
      >
        <div 
          className="header-left"
          onClick={() => navigate('/')}
          style={{ cursor: 'pointer' }}
        >
          <Brain size={24} className="logo-icon" />
          <h1 className="header-title">
            Cognitive Core
            <FeatureBadge 
              label="AI" 
              tooltip="Powered by OpenAI GPT-4 & Tavily Search API"
              icon="agent"
              variant="primary"
            />
          </h1>
        </div>
      </AgentTooltip>
      <div className="header-right">
        <ConnectionStatus />
        <EnhancedTooltip
          content="View conversation history and past analyses"
          icon="feature"
          position="bottom"
        >
          <button className="header-button" aria-label="History">
            <History size={20} />
          </button>
        </EnhancedTooltip>
        <EnhancedTooltip
          content="Configure agent settings and preferences"
          icon="feature"
          position="bottom"
        >
          <button className="header-button" aria-label="Settings">
            <Settings size={20} />
          </button>
        </EnhancedTooltip>
      </div>
    </header>
  );
}

