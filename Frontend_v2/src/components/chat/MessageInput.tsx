import { useState, useRef, type KeyboardEvent, type ChangeEvent } from 'react';
import { Send, Square } from 'lucide-react';
import { useWebSocketSend } from '../../hooks/useWebSocket';
import './MessageInput.css';

interface MessageInputProps {
  onSendMessage?: (query: string) => void;
  disabled?: boolean;
  isStreaming?: boolean;
  onStop?: () => void;
}

export function MessageInput({ onSendMessage, disabled, isStreaming, onStop }: MessageInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const sendMessage = useWebSocketSend();

  const handleSend = () => {
    const trimmedInput = input.trim();
    
    if (!trimmedInput || disabled) {
      return;
    }

    // Send via WebSocket
    sendMessage('query', {
      query: trimmedInput,
      use_citations: true,
    });

    // Call optional callback
    onSendMessage?.(trimmedInput);

    // Clear input
    setInput('');
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleStop = () => {
    if (onStop) {
      onStop();
    }
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter') {
      // Shift+Enter = new line, Enter = send
      if (event.shiftKey) {
        return;
      }

      event.preventDefault();

      if (isStreaming) {
        handleStop();
        return;
      }

      handleSend();
    }
  };

  const handleChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value);

    // Auto-resize textarea
    const textarea = event.target;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
  };

  return (
    <div className="message-input-container">
      <div className="message-input-wrapper">
        <textarea
          ref={textareaRef}
          className="message-textarea"
          placeholder="Ask about political events, policies, trends..."
          value={input}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
        />
        
        <button
          className={`send-button ${isStreaming ? 'stop' : 'send'}`}
          onClick={isStreaming ? handleStop : handleSend}
          disabled={disabled || (!isStreaming && !input.trim())}
          title={isStreaming ? 'Stop generating' : 'Send message'}
          aria-label={isStreaming ? 'Stop generating' : 'Send message'}
        >
          {isStreaming ? (
            <Square size={20} className="icon" />
          ) : (
            <Send size={20} className="icon" />
          )}
        </button>
      </div>
      
      <div className="message-input-hint">
        Press <kbd>Enter</kbd> to send, <kbd>Shift + Enter</kbd> for new line
      </div>
    </div>
  );
}

