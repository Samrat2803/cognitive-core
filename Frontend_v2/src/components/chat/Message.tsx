import { useState, memo } from 'react';
import { User, Bot, ChevronDown, ChevronRight, Copy, Check } from 'lucide-react';
import { Markdown } from '../ui/Markdown';
import { Citations, type Citation } from './Citations';
import { ExecutionGraph } from './ExecutionGraph';
import { EnhancedTooltip, AgentTooltip } from '../ui/EnhancedTooltip';
import './Message.css';

export interface MessageData {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
  sessionId?: string; // For fetching execution graph
}

interface MessageProps {
  message: MessageData;
}

// Memoize to prevent unnecessary re-renders during streaming
export const Message = memo(function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';
  const [showExecutionGraph, setShowExecutionGraph] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-icon">
        {isUser ? (
          <EnhancedTooltip
            content="Your query sent to the Political Analyst AI"
            icon="info"
            position="right"
          >
            <User size={20} className="icon" />
          </EnhancedTooltip>
        ) : (
          <AgentTooltip
            title="Political Analyst Agent"
            description="AI-powered analysis using LangGraph orchestration with multiple specialized sub-agents"
            features={[
              'Real-time web search via Tavily API',
              'Sentiment analysis across regions',
              'Citation-backed responses',
              'Interactive visualizations'
            ]}
            position="right"
          >
            <Bot size={20} className="icon" />
          </AgentTooltip>
        )}
      </div>
      
      <div className="message-content">
        <div className="message-header">
          <span className="message-role">{isUser ? 'You' : 'Political Analyst'}</span>
          <div className="message-header-actions">
            <EnhancedTooltip
              content={copied ? "Copied to clipboard!" : "Copy message to clipboard"}
              icon="feature"
              position="top"
            >
              <button
                className="message-copy-button"
                onClick={handleCopy}
                aria-label="Copy message"
              >
                {copied ? <Check size={14} /> : <Copy size={14} />}
              </button>
            </EnhancedTooltip>
            <span className="message-time">
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </div>
        
        <div className="message-text">
          {isUser ? (
            // User messages: plain text with preserved whitespace
            <div className="user-text">{message.content}</div>
          ) : (
            // Assistant messages: rendered as Markdown with citations
            <>
              <Markdown>{message.content}</Markdown>
              {message.citations && message.citations.length > 0 && (
                <Citations citations={message.citations} />
              )}
              
              {/* Execution Graph - Only for assistant messages with sessionId */}
              {message.sessionId && (
                <div className="execution-details">
                  <AgentTooltip
                    title="Execution Graph"
                    description="Visual representation of the agent's decision-making process and tool usage"
                    features={[
                      'Step-by-step workflow visualization',
                      'Tool execution timeline',
                      'Node transitions and decisions',
                      'Performance metrics'
                    ]}
                    position="top"
                  >
                    <button
                      className="execution-toggle"
                      onClick={() => setShowExecutionGraph(!showExecutionGraph)}
                      aria-expanded={showExecutionGraph}
                    >
                      {showExecutionGraph ? (
                        <ChevronDown size={16} />
                      ) : (
                        <ChevronRight size={16} />
                      )}
                      <span>Execution Details</span>
                      <span className="execution-badge">
                        View execution graph
                      </span>
                    </button>
                  </AgentTooltip>
                  
                  {showExecutionGraph && (
                    <div className="execution-graph-wrapper">
                      <ExecutionGraph sessionId={message.sessionId} />
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
});

