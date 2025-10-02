import { User, Bot } from 'lucide-react';
import { Markdown } from '../ui/Markdown';
import { Citations, type Citation } from './Citations';
import './Message.css';

export interface MessageData {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
}

interface MessageProps {
  message: MessageData;
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';

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
                </>
              )}
            </div>
          </div>
        </div>
      );
    }

