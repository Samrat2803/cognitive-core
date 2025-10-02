import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Chat from '../../pages/Chat';

// Mock API client
vi.mock('../../api/client', () => ({
  apiChatMessage: vi.fn(),
  apiConfirmAnalysis: vi.fn()
}));

// Mock config
vi.mock('../../config', () => ({
  getSessionId: vi.fn().mockReturnValue('test-session-123')
}));

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false }
  }
});

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('Chat Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('initial state', () => {
    it('should render chat form', () => {
      renderWithQueryClient(<Chat />);
      
      expect(screen.getByText('Political Analyst Workbench')).toBeInTheDocument();
      expect(screen.getByLabelText('Your Analysis Request')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /send request/i })).toBeInTheDocument();
    });

    it('should have disabled submit button when no message', () => {
      renderWithQueryClient(<Chat />);
      
      const submitButton = screen.getByRole('button', { name: /send request/i });
      expect(submitButton).toBeDisabled();
    });
  });

  describe('message sending', () => {
    it('should enable submit button when message is entered', async () => {
      renderWithQueryClient(<Chat />);
      
      const textarea = screen.getByLabelText('Your Analysis Request');
      const submitButton = screen.getByRole('button', { name: /send request/i });
      
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      
      expect(submitButton).not.toBeDisabled();
    });

    it('should call API when form is submitted', async () => {
      const { apiChatMessage } = await import('../../api/client');
      (apiChatMessage as any).mockResolvedValue({
        success: true,
        response_type: 'query_parsed',
        parsed_intent: {
          action: 'sentiment_analysis',
          topic: 'Test',
          countries: ['US'],
          parameters: { days: 7 }
        },
        confirmation: 'Test confirmation',
        analysis_id: 'test_123'
      });

      renderWithQueryClient(<Chat />);
      
      const textarea = screen.getByLabelText('Your Analysis Request');
      const submitButton = screen.getByRole('button', { name: /send request/i });
      
      fireEvent.change(textarea, { target: { value: 'Analyze sentiment' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(apiChatMessage).toHaveBeenCalledWith({
          message: 'Analyze sentiment',
          session_id: 'test-session-123'
        });
      });
    });
  });

  describe('query parsed response', () => {
    it('should show analysis plan when query is parsed', async () => {
      const { apiChatMessage } = await import('../../api/client');
      (apiChatMessage as any).mockResolvedValue({
        success: true,
        response_type: 'query_parsed',
        parsed_intent: {
          action: 'sentiment_analysis',
          topic: 'Hamas',
          countries: ['United States', 'Iran'],
          parameters: { days: 7, results_per_country: 20 }
        },
        confirmation: 'I will analyze Hamas sentiment. Proceed?',
        analysis_id: 'test_123'
      });

      renderWithQueryClient(<Chat />);
      
      const textarea = screen.getByLabelText('Your Analysis Request');
      fireEvent.change(textarea, { target: { value: 'Analyze Hamas sentiment' } });
      fireEvent.click(screen.getByRole('button', { name: /send request/i }));
      
      await waitFor(() => {
        expect(screen.getByText('Analysis Plan')).toBeInTheDocument();
        expect(screen.getByText('sentiment_analysis')).toBeInTheDocument();
        expect(screen.getByText('Hamas')).toBeInTheDocument();
        expect(screen.getByText('United States, Iran')).toBeInTheDocument();
        expect(screen.getByText('I will analyze Hamas sentiment. Proceed?')).toBeInTheDocument();
      });
    });

    it('should show proceed and cancel buttons', async () => {
      const { apiChatMessage } = await import('../../api/client');
      (apiChatMessage as any).mockResolvedValue({
        success: true,
        response_type: 'query_parsed',
        parsed_intent: {
          action: 'sentiment_analysis',
          topic: 'Test',
          countries: ['US'],
          parameters: {}
        },
        confirmation: 'Proceed?',
        analysis_id: 'test_123'
      });

      renderWithQueryClient(<Chat />);
      
      const textarea = screen.getByLabelText('Your Analysis Request');
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      fireEvent.click(screen.getByRole('button', { name: /send request/i }));
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /proceed with analysis/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
      });
    });
  });

  describe('analysis confirmation', () => {
    it('should call confirm API when proceed is clicked', async () => {
      const { apiChatMessage, apiConfirmAnalysis } = await import('../../api/client');
      
      (apiChatMessage as any).mockResolvedValue({
        success: true,
        response_type: 'query_parsed',
        analysis_id: 'test_123',
        confirmation: 'Proceed?'
      });
      
      (apiConfirmAnalysis as any).mockResolvedValue({
        success: true,
        analysis_id: 'test_123',
        status: 'queued'
      });

      renderWithQueryClient(<Chat />);
      
      // Send message first
      const textarea = screen.getByLabelText('Your Analysis Request');
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      fireEvent.click(screen.getByRole('button', { name: /send request/i }));
      
      // Wait for response and click proceed
      await waitFor(() => {
        const proceedButton = screen.getByRole('button', { name: /proceed with analysis/i });
        fireEvent.click(proceedButton);
      });
      
      await waitFor(() => {
        expect(apiConfirmAnalysis).toHaveBeenCalledWith({
          analysis_id: 'test_123',
          confirmed: true
        });
      });
    });

    it('should show success message when analysis starts', async () => {
      const { apiChatMessage, apiConfirmAnalysis } = await import('../../api/client');
      
      (apiChatMessage as any).mockResolvedValue({
        success: true,
        response_type: 'query_parsed',
        analysis_id: 'test_123',
        confirmation: 'Proceed?'
      });
      
      (apiConfirmAnalysis as any).mockResolvedValue({
        success: true,
        analysis_id: 'test_123',
        status: 'queued'
      });

      renderWithQueryClient(<Chat />);
      
      // Send message and proceed
      const textarea = screen.getByLabelText('Your Analysis Request');
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      fireEvent.click(screen.getByRole('button', { name: /send request/i }));
      
      await waitFor(() => {
        fireEvent.click(screen.getByRole('button', { name: /proceed with analysis/i }));
      });
      
      await waitFor(() => {
        expect(screen.getByText('✅ Analysis Started!')).toBeInTheDocument();
        expect(screen.getByText(/queued and will begin processing/)).toBeInTheDocument();
      });
    });
  });

  describe('direct response', () => {
    it('should show suggestions when direct response received', async () => {
      const { apiChatMessage } = await import('../../api/client');
      (apiChatMessage as any).mockResolvedValue({
        success: true,
        response_type: 'direct_response',
        message: 'I can help with analysis.',
        suggestions: ['Analyze sentiment', 'Compare countries']
      });

      renderWithQueryClient(<Chat />);
      
      const textarea = screen.getByLabelText('Your Analysis Request');
      fireEvent.change(textarea, { target: { value: 'Help me' } });
      fireEvent.click(screen.getByRole('button', { name: /send request/i }));
      
      await waitFor(() => {
        expect(screen.getByText('I can help with analysis.')).toBeInTheDocument();
        expect(screen.getByText('Suggestions:')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Analyze sentiment' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Compare countries' })).toBeInTheDocument();
      });
    });

    it('should populate textarea when suggestion is clicked', async () => {
      const { apiChatMessage } = await import('../../api/client');
      (apiChatMessage as any).mockResolvedValue({
        success: true,
        response_type: 'direct_response',
        message: 'I can help with analysis.',
        suggestions: ['Analyze sentiment']
      });

      renderWithQueryClient(<Chat />);
      
      const textarea = screen.getByLabelText('Your Analysis Request');
      fireEvent.change(textarea, { target: { value: 'Help me' } });
      fireEvent.click(screen.getByRole('button', { name: /send request/i }));
      
      await waitFor(() => {
        fireEvent.click(screen.getByRole('button', { name: 'Analyze sentiment' }));
      });
      
      // Should show new chat button to reset
      expect(screen.getByRole('button', { name: /new chat/i })).toBeInTheDocument();
    });
  });

  describe('error handling', () => {
    it('should show error message when API fails', async () => {
      const { apiChatMessage } = await import('../../api/client');
      (apiChatMessage as any).mockRejectedValue(new Error('API Error'));

      renderWithQueryClient(<Chat />);
      
      const textarea = screen.getByLabelText('Your Analysis Request');
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      fireEvent.click(screen.getByRole('button', { name: /send request/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/Error: API Error/)).toBeInTheDocument();
      });
    });
  });

  describe('new chat', () => {
    it('should reset form when new chat is clicked', async () => {
      const { apiChatMessage } = await import('../../api/client');
      (apiChatMessage as any).mockResolvedValue({
        success: true,
        response_type: 'direct_response',
        message: 'Test response'
      });

      renderWithQueryClient(<Chat />);
      
      // Send a message first
      const textarea = screen.getByLabelText('Your Analysis Request');
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      fireEvent.click(screen.getByRole('button', { name: /send request/i }));
      
      await waitFor(() => {
        fireEvent.click(screen.getByRole('button', { name: /new chat/i }));
      });
      
      // Form should be reset
      expect(screen.getByLabelText('Your Analysis Request')).toHaveValue('');
      expect(screen.queryByText('Test response')).not.toBeInTheDocument();
    });
  });
});
