import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '../../App';

// Mock all API functions
vi.mock('../../api/client', () => ({
  apiResearch: vi.fn(),
  apiChatMessage: vi.fn(),
  apiConfirmAnalysis: vi.fn(),
  apiAnalysisExecute: vi.fn(),
  apiGetAnalysis: vi.fn(),
  apiAnalysisHistory: vi.fn(),
  apiExportCreate: vi.fn(),
  apiGetExport: vi.fn()
}));

// Mock WebSocket service
vi.mock('../../services/websocket', () => ({
  wsService: {
    connect: vi.fn(),
    disconnect: vi.fn(),
    on: vi.fn().mockReturnValue(() => {}),
  }
}));

// Mock config
vi.mock('../../config', () => ({
  getSessionId: vi.fn().mockReturnValue('test-session-123'),
  API_CONFIG: {
    baseURL: 'http://localhost:8000',
    wsBaseURL: 'ws://localhost:8000/ws',
    timeout: 120000,
    environment: 'development',
    endpoints: {
      root: '/',
      health: '/health',
      research: '/research',
      chatMessage: '/api/chat/message',
      chatConfirm: '/api/chat/confirm-analysis',
      analysisExecute: '/api/analysis/execute',
      analysisById: (id: string) => `/api/analysis/${id}`,
      analysisHistory: '/api/analysis/history',
      exportCreate: '/api/export/create',
      exportById: (id: string) => `/api/export/${id}`,
      exportDownload: (id: string) => `/api/export/download/${id}`,
    }
  },
  UI_CONFIG: {
    colors: {
      primary: '#d9f378',
      secondary: '#5d535c',
      dark: '#333333',
      darkest: '#1c1e20',
      white: '#ffffff',
      error: '#ef4444',
      success: '#10b981',
      warning: '#f59e0b'
    },
    fonts: {
      main: 'Roboto Flex, sans-serif'
    },
    maxQueryLength: 1000,
    pollingInterval: 2000,
    exportFormats: ['json', 'csv', 'pdf']
  }
}));

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false }
  }
});

const renderApp = () => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  );
};

describe('End-to-End Flow Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Navigation', () => {
    it('should navigate between different sections', async () => {
      renderApp();
      
      // Should start on Chat page
      expect(screen.getAllByText('Political Analyst Workbench')).toHaveLength(2); // One in nav, one in content
      expect(screen.getByText(/ask me to analyze geopolitical sentiment/i)).toBeInTheDocument();
      
      // Navigate to Analysis Results
      fireEvent.click(screen.getByRole('button', { name: /analysis/i }));
      expect(screen.getByText('Analysis Results')).toBeInTheDocument();
      expect(screen.getByText('Start Direct Analysis')).toBeInTheDocument();
      
      // Navigate to History
      fireEvent.click(screen.getByRole('button', { name: /history/i }));
      expect(screen.getByText('Analysis History')).toBeInTheDocument();
      
      // Navigate to Legacy Research
      fireEvent.click(screen.getByRole('button', { name: /legacy research/i }));
      expect(screen.getByText('Legacy Research Interface')).toBeInTheDocument();
    });
  });

  describe('Complete Chat to Analysis Flow', () => {
    it('should complete full chat → confirmation → analysis flow', async () => {
      const { 
        apiChatMessage, 
        apiConfirmAnalysis, 
        apiGetAnalysis 
      } = await import('../../api/client');
      
      // Mock chat message response
      (apiChatMessage as any).mockResolvedValue({
        success: true,
        response_type: 'query_parsed',
        parsed_intent: {
          action: 'sentiment_analysis',
          topic: 'Hamas',
          countries: ['United States', 'Iran', 'Israel'],
          parameters: { days: 7, results_per_country: 20 }
        },
        confirmation: 'I will analyze Hamas sentiment across US, Iran, and Israel. Proceed?',
        analysis_id: 'analysis_123'
      });
      
      // Mock confirmation response
      (apiConfirmAnalysis as any).mockResolvedValue({
        success: true,
        analysis_id: 'analysis_123',
        status: 'queued',
        websocket_session: 'ws_session_456'
      });
      
      // Mock analysis status (processing)
      (apiGetAnalysis as any).mockResolvedValue({
        success: true,
        analysis_id: 'analysis_123',
        status: 'processing',
        progress: {
          current_step: 'analyzing_sentiment',
          completion_percentage: 60,
          processed_countries: ['United States'],
          remaining_countries: ['Iran', 'Israel']
        },
        created_at: new Date().toISOString()
      });

      renderApp();
      
      // Step 1: Send chat message
      const textarea = screen.getByLabelText('Your Analysis Request');
      fireEvent.change(textarea, { target: { value: 'Analyze Hamas sentiment in US, Iran, Israel' } });
      fireEvent.click(screen.getByRole('button', { name: /send request/i }));
      
      // Step 2: Verify parsed intent is shown
      await waitFor(() => {
        expect(screen.getByText('Analysis Plan')).toBeInTheDocument();
        expect(screen.getByText('sentiment_analysis')).toBeInTheDocument();
        expect(screen.getByText('Hamas')).toBeInTheDocument();
        expect(screen.getByText('United States, Iran, Israel')).toBeInTheDocument();
      });
      
      // Step 3: Confirm analysis
      fireEvent.click(screen.getByRole('button', { name: /proceed with analysis/i }));
      
      // Step 4: Verify analysis started
      await waitFor(() => {
        expect(screen.getByText('✅ Analysis Started!')).toBeInTheDocument();
      });
      
      // Verify API calls were made correctly
      expect(apiChatMessage).toHaveBeenCalledWith({
        message: 'Analyze Hamas sentiment in US, Iran, Israel',
        session_id: 'test-session-123'
      });
      
      expect(apiConfirmAnalysis).toHaveBeenCalledWith({
        analysis_id: 'analysis_123',
        confirmed: true
      });
    });
  });

  describe('Direct Analysis Flow', () => {
    it('should execute direct analysis and show results', async () => {
      const { apiAnalysisExecute, apiGetAnalysis } = await import('../../api/client');
      
      // Mock analysis execution
      (apiAnalysisExecute as any).mockResolvedValue({
        success: true,
        analysis_id: 'direct_analysis_456',
        status: 'processing',
        created_at: new Date().toISOString()
      });
      
      // Mock completed analysis
      (apiGetAnalysis as any).mockResolvedValue({
        success: true,
        analysis_id: 'direct_analysis_456',
        status: 'completed',
        created_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
        results: {
          summary: {
            overall_sentiment: -0.15,
            countries_analyzed: 3,
            total_articles: 45,
            analysis_confidence: 0.92,
            bias_detected: false,
            completion_time_ms: 35000
          },
          country_results: [
            {
              country: 'United States',
              sentiment_score: -0.3,
              confidence: 0.88,
              articles_count: 15,
              dominant_sentiment: 'negative',
              key_themes: ['politics', 'economy'],
              bias_analysis: {
                bias_types: ['selection'],
                bias_severity: 0.2,
                notes: 'Minimal bias detected'
              }
            }
          ]
        }
      });

      renderApp();
      
      // Navigate to Analysis Results
      fireEvent.click(screen.getByRole('button', { name: /analysis/i }));
      
      // Start direct analysis
      const queryInput = screen.getByLabelText('Query Text');
      fireEvent.change(queryInput, { target: { value: 'Direct sentiment analysis' } });
      fireEvent.click(screen.getByRole('button', { name: /start analysis/i }));
      
      // Verify analysis was started
      await waitFor(() => {
        expect(apiAnalysisExecute).toHaveBeenCalledWith({
          query_text: 'Direct sentiment analysis',
          parameters: {
            countries: ['United States', 'Iran', 'Israel'],
            days: 7,
            results_per_country: 20,
            include_bias_analysis: true
          },
          session_id: 'test-session-123'
        });
      });
      
      // Should show analysis info and results
      await waitFor(() => {
        expect(screen.getByText('Analysis Info')).toBeInTheDocument();
        expect(screen.getByText('direct_analysis_456')).toBeInTheDocument();
        expect(screen.getByText('completed')).toBeInTheDocument();
      });
    });
  });

  describe('History Integration', () => {
    it('should display analysis history', async () => {
      const { apiAnalysisHistory } = await import('../../api/client');
      
      (apiAnalysisHistory as any).mockResolvedValue({
        success: true,
        analyses: [
          {
            analysis_id: 'history_analysis_1',
            query_text: 'Previous analysis query',
            status: 'completed',
            countries: ['United States', 'Canada'],
            created_at: new Date().toISOString(),
            completed_at: new Date().toISOString(),
            summary: {
              overall_sentiment: 0.25,
              articles_analyzed: 30
            }
          },
          {
            analysis_id: 'history_analysis_2',
            query_text: 'Another analysis',
            status: 'processing',
            countries: ['Germany', 'France'],
            created_at: new Date().toISOString()
          }
        ],
        total_count: 2,
        has_more: false
      });

      renderApp();
      
      // Navigate to History
      fireEvent.click(screen.getByRole('button', { name: /history/i }));
      
      // Verify history is loaded and displayed
      await waitFor(() => {
        expect(screen.getByText('Previous analysis query')).toBeInTheDocument();
        expect(screen.getByText('Another analysis')).toBeInTheDocument();
        expect(screen.getByText('United States, Canada')).toBeInTheDocument();
        expect(screen.getByText('Germany, France')).toBeInTheDocument();
        expect(screen.getByText('0.25')).toBeInTheDocument(); // sentiment score
        expect(screen.getByText('30')).toBeInTheDocument(); // articles count
      });
      
      expect(apiAnalysisHistory).toHaveBeenCalledWith(10, 0);
    });
  });

  describe('Legacy Research Integration', () => {
    it('should work with legacy research endpoint', async () => {
      const { apiResearch } = await import('../../api/client');
      
      (apiResearch as any).mockResolvedValue({
        success: true,
        query: 'Legacy research query',
        search_terms: ['legacy', 'research'],
        sources_count: 5,
        final_answer: 'This is the legacy research answer.',
        sources: [
          'https://example1.com',
          'https://example2.com'
        ]
      });

      renderApp();
      
      // Navigate to Legacy Research
      fireEvent.click(screen.getByRole('button', { name: /legacy research/i }));
      
      // Use legacy research form
      const textarea = screen.getByLabelText(/research query/i);
      fireEvent.change(textarea, { target: { value: 'Legacy research query' } });
      fireEvent.click(screen.getByRole('button', { name: /start research/i }));
      
      // Verify results are displayed
      await waitFor(() => {
        expect(screen.getAllByText('Research Results')).toHaveLength(2); // One in nav, one in results
        expect(screen.getByText('This is the legacy research answer.')).toBeInTheDocument();
        expect(screen.getByText('5 sources')).toBeInTheDocument();
        expect(screen.getByText('https://example1.com')).toBeInTheDocument();
      });
      
      expect(apiResearch).toHaveBeenCalledWith('Legacy research query');
    });
  });

  describe('Error Handling Integration', () => {
    it('should handle API errors gracefully across all sections', async () => {
      const { apiChatMessage, apiAnalysisHistory } = await import('../../api/client');
      
      // Mock API errors
      (apiChatMessage as any).mockRejectedValue(new Error('Chat API unavailable'));
      (apiAnalysisHistory as any).mockRejectedValue(new Error('History service down'));

      renderApp();
      
      // Test chat error handling
      const textarea = screen.getByLabelText('Your Analysis Request');
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      fireEvent.click(screen.getByRole('button', { name: /send request/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/Chat API unavailable/)).toBeInTheDocument();
      });
      
      // Test history error handling
      fireEvent.click(screen.getByRole('button', { name: /history/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/History service down/)).toBeInTheDocument();
      });
    });
  });
});
