import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  Box, 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  List, 
  ListItem,
  Chip,
  IconButton,
  Skeleton
} from '@mui/material';
import { Send as SendIcon, Article as SourcesIcon } from '@mui/icons-material';
import { useStreamingChat } from '../hooks/useWebSocket';
import { getSessionId } from '../config';
import { Citation } from '../types';
import SourcesPanel from '../components/results/SourcesPanel';

const Chat: React.FC = () => {
  const location = useLocation();
  const [inputValue, setInputValue] = useState('');
  const [sourcesPanelOpen, setSourcesPanelOpen] = useState(false);
  const [selectedCitationId, setSelectedCitationId] = useState<string | undefined>();
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    currentStreamingMessage,
    isStreaming,
    citations,
    addUserMessage,
    connect,
    disconnect,
    sendMessage,
    isConnected,
    isConnecting,
    error
  } = useStreamingChat();

  // Initialize with prompt from Home page if provided
  useEffect(() => {
    const initialPrompt = location.state?.initialPrompt;
    if (initialPrompt) {
      setInputValue(initialPrompt);
      // Clear the state to prevent re-setting on re-renders
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  // Connect to WebSocket on mount
  useEffect(() => {
    connect(getSessionId());
    return () => disconnect();
  }, [connect, disconnect]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentStreamingMessage]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && isConnected) {
      const query = inputValue.trim();
      addUserMessage(query);
      
      // Send analysis request (works with both mock and real backend)
      sendMessage({
        type: 'start_analysis',
        query: query,
        session_id: getSessionId()
      });
      
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const handleCitationClick = (citationId: string) => {
    setSelectedCitationId(citationId);
    setSourcesPanelOpen(true);
  };

  const renderMessageContent = (content: string, messageCitations?: Citation[]) => {
    // Process content to add citation links
    const processedContent = content.replace(
      /\[(\d+)\]/g,
      (match, num) => {
        const citationIndex = parseInt(num) - 1;
        const citation = messageCitations?.[citationIndex];
        if (citation) {
          return `<sup><button class="citation-link" data-citation-id="${citation.id}" style="background: var(--aistra-primary); color: var(--aistra-darker); border: none; border-radius: 3px; padding: 2px 6px; font-size: 0.8rem; font-weight: 600; cursor: pointer; margin: 0 2px;">[${num}]</button></sup>`;
        }
        return match;
      }
    );

    return (
      <Box
        dangerouslySetInnerHTML={{ __html: processedContent }}
        onClick={(e) => {
          const target = e.target as HTMLElement;
          if (target.classList.contains('citation-link')) {
            const citationId = target.getAttribute('data-citation-id');
            if (citationId) {
              handleCitationClick(citationId);
            }
          }
        }}
        sx={{
          '& p': { margin: 0 },
          '& .citation-link:hover': {
            opacity: 0.8,
            transform: 'translateY(-1px)'
          }
        }}
      />
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 3, height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ mb: 3, textAlign: 'center' }}>
        <Typography variant="h4" sx={{ color: 'var(--aistra-primary)', fontWeight: 600, mb: 1 }}>
          Cognitive Core Chat
        </Typography>
        <Typography variant="body1" sx={{ color: 'var(--aistra-white)', opacity: 0.8 }}>
          Streaming geopolitical sentiment analysis
        </Typography>
        
        {/* Connection Status */}
        <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: isConnected ? '#10b981' : isConnecting ? '#f59e0b' : '#ef4444'
            }}
          />
          <Typography variant="caption" sx={{ color: 'var(--aistra-white)', opacity: 0.7 }}>
            {isConnected ? 'Connected' : isConnecting ? 'Connecting...' : 'Disconnected'}
          </Typography>
          {citations.length > 0 && (
            <IconButton
              onClick={() => setSourcesPanelOpen(true)}
              sx={{ ml: 2, color: 'var(--aistra-primary)' }}
              size="small"
            >
              <SourcesIcon />
              <Typography variant="caption" sx={{ ml: 0.5 }}>
                {citations.length}
              </Typography>
            </IconButton>
          )}
        </Box>
      </Box>

      {/* Messages Area */}
      <Paper
        sx={{
          flex: 1,
          backgroundColor: 'var(--aistra-dark)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 2,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
      >
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {messages.length === 0 && !currentStreamingMessage && (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" sx={{ color: 'var(--aistra-primary)', mb: 2 }}>
                Welcome to Cognitive Core
              </Typography>
              <Typography variant="body2" sx={{ color: 'var(--aistra-white)', opacity: 0.7, mb: 3 }}>
                Start a conversation to analyze geopolitical sentiment across countries
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
                {[
                  "Analyze Hamas sentiment in US, Iran, and Israel",
                  "Compare Ukraine war coverage in Europe",
                  "Climate policy sentiment in G7 nations"
                ].map((prompt, index) => (
                  <Chip
                    key={index}
                    label={prompt}
                    onClick={() => setInputValue(prompt)}
                    sx={{
                      backgroundColor: 'var(--aistra-darker)',
                      color: 'var(--aistra-white)',
                      border: '1px solid var(--aistra-secondary)',
                        cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'var(--aistra-primary)',
                        color: 'var(--aistra-darker)'
                      }
                    }}
                  />
                ))}
              </Box>
            </Box>
          )}

          <List sx={{ p: 0 }}>
            {messages.map((message) => (
              <ListItem
                key={message.id}
                sx={{
                  flexDirection: 'column',
                  alignItems: message.role === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2,
                  p: 0
                }}
              >
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '80%',
                    backgroundColor: message.role === 'user' 
                      ? 'var(--aistra-primary)' 
                      : 'var(--aistra-darker)',
                    color: message.role === 'user' 
                      ? 'var(--aistra-darker)' 
                      : 'var(--aistra-white)',
                    borderRadius: 2,
                    border: message.role === 'assistant' ? '1px solid rgba(255,255,255,0.1)' : 'none'
                  }}
                >
                  {message.role === 'user' ? (
                    <Typography variant="body1">{message.content}</Typography>
                  ) : (
                    <Box>
                      {renderMessageContent(message.content, message.citations)}
                      {message.citations && message.citations.length > 0 && (
                        <Box sx={{ mt: 1, pt: 1, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                          <Typography variant="caption" sx={{ opacity: 0.7 }}>
                            {message.citations.length} source{message.citations.length !== 1 ? 's' : ''}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  )}
                </Paper>
                <Typography variant="caption" sx={{ mt: 0.5, opacity: 0.6 }}>
                  {message.timestamp.toLocaleTimeString()}
                </Typography>
              </ListItem>
            ))}

            {/* Streaming Message */}
            {isStreaming && currentStreamingMessage && (
              <ListItem sx={{ flexDirection: 'column', alignItems: 'flex-start', mb: 2, p: 0 }}>
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '80%',
                    backgroundColor: 'var(--aistra-darker)',
                    color: 'var(--aistra-white)',
                    borderRadius: 2,
                          border: '1px solid rgba(255,255,255,0.1)'
                  }}
                >
                  <Box
                    aria-live="polite"
                    aria-label="Streaming response"
                    sx={{ position: 'relative' }}
                  >
                    {renderMessageContent(currentStreamingMessage)}
                    <Box
                      sx={{
                                    display: 'inline-block',
                        width: '8px',
                        height: '16px',
                        backgroundColor: 'var(--aistra-primary)',
                        ml: 0.5,
                        animation: 'blink 1s infinite'
                      }}
                    />
                  </Box>
                </Paper>
              </ListItem>
            )}

            {/* Loading Skeleton */}
            {isStreaming && !currentStreamingMessage && (
              <ListItem sx={{ flexDirection: 'column', alignItems: 'flex-start', mb: 2, p: 0 }}>
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '80%',
                    backgroundColor: 'var(--aistra-darker)',
                    borderRadius: 2,
                    border: '1px solid rgba(255,255,255,0.1)'
                  }}
                >
                  <Skeleton variant="text" width="60%" sx={{ bgcolor: 'rgba(255,255,255,0.1)' }} />
                  <Skeleton variant="text" width="80%" sx={{ bgcolor: 'rgba(255,255,255,0.1)' }} />
                  <Skeleton variant="text" width="40%" sx={{ bgcolor: 'rgba(255,255,255,0.1)' }} />
                </Paper>
              </ListItem>
            )}
          </List>
          <div ref={messagesEndRef} />
        </Box>

        {/* Input Area */}
        <Box sx={{ p: 2, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
          {error && (
            <Typography variant="body2" sx={{ color: '#ef4444', mb: 1 }}>
              ❌ {error}
            </Typography>
          )}
          
          <Box component="form" onSubmit={handleSendMessage} sx={{ display: 'flex', gap: 1 }}>
            <TextField
              multiline
              maxRows={4}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me to analyze geopolitical sentiment..."
              disabled={!isConnected || isStreaming}
              sx={{
                flex: 1,
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'var(--aistra-darker)',
                  color: 'var(--aistra-white)',
                  '& fieldset': {
                    borderColor: 'rgba(255,255,255,0.2)'
                  },
                  '&:hover fieldset': {
                    borderColor: 'var(--aistra-primary)'
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: 'var(--aistra-primary)'
                  }
                },
                '& .MuiInputBase-input': {
                  color: 'var(--aistra-white)'
                },
                '& .MuiInputBase-input::placeholder': {
                  color: 'rgba(255,255,255,0.5)',
                  opacity: 1
                }
              }}
            />
            <Button
              type="submit"
              variant="contained"
              disabled={!inputValue.trim() || !isConnected || isStreaming}
              sx={{
                backgroundColor: 'var(--aistra-primary)',
                color: 'var(--aistra-darker)',
                minWidth: 'auto',
                px: 2,
                '&:hover': {
                  backgroundColor: 'var(--aistra-primary)',
                  opacity: 0.9
                },
                '&:disabled': {
                  backgroundColor: 'var(--aistra-secondary)',
                  color: 'rgba(255,255,255,0.5)'
                }
              }}
            >
              <SendIcon />
            </Button>
          </Box>
          
          <Typography variant="caption" sx={{ color: 'var(--aistra-white)', opacity: 0.6, mt: 1, display: 'block' }}>
            Press Enter to send, Shift+Enter for new line
          </Typography>
        </Box>
      </Paper>

      {/* Sources Panel */}
      <SourcesPanel
        open={sourcesPanelOpen}
        onClose={() => setSourcesPanelOpen(false)}
        citations={citations}
        selectedCitationId={selectedCitationId}
      />

      {/* CSS for animations */}
      <style>
        {`
          @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
          }
        `}
      </style>
    </Container>
  );
};

export default Chat;
