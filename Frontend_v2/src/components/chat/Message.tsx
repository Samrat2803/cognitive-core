import { useState, memo } from 'react';
import { User, Bot, ChevronDown, ChevronRight } from 'lucide-react';
import { Markdown } from '../ui/Markdown';
import { Citations, type Citation } from './Citations';
import { ExecutionGraph } from './ExecutionGraph';
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

  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-icon">
        {isUser ? (
          <User size={20} className="icon" />
        ) : (
          <Bot size={20} className="icon" />
        )}
      </div>
      
      <div className="message-content">
        <div className="message-header">
          <span className="message-role">{isUser ? 'You' : 'Political Analyst'}</span>
          <span className="message-time">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
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

