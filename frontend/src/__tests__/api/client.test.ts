import { describe, it, expect, beforeEach, vi } from 'vitest';
import { 
  apiResearch, 
  apiChatMessage, 
  apiAnalysisExecute, 
  apiGetAnalysis,
  apiAnalysisHistory,
  apiExportCreate,
  apiGetExport
} from '../../api/client';

// Mock the mocks module
vi.mock('../../api/mocks', () => ({
  USE_MOCKS: true,
  mockResearch: vi.fn().mockResolvedValue({
    success: true,
    query: 'test query',
    search_terms: ['test'],
    sources_count: 1,
    final_answer: 'test answer',
    sources: ['http://test.com']
  }),
  mockChatMessage: vi.fn().mockResolvedValue({
    success: true,
    response_type: 'query_parsed',
    parsed_intent: {
      action: 'sentiment_analysis',
      topic: 'test',
      countries: ['US'],
      parameters: { days: 7 }
    },
    confirmation: 'Test confirmation',
    analysis_id: 'test_analysis_123'
  }),
  mockAnalysisExecute: vi.fn().mockResolvedValue({
    success: true,
    analysis_id: 'test_analysis_123',
    status: 'processing',
    created_at: new Date().toISOString()
  }),
  mockGetAnalysis: vi.fn().mockResolvedValue({
    success: true,
    analysis_id: 'test_analysis_123',
    status: 'completed',
    created_at: new Date().toISOString(),
    results: {
      summary: {
        overall_sentiment: -0.5,
        countries_analyzed: 2,
        total_articles: 50,
        analysis_confidence: 0.85,
        bias_detected: false,
        completion_time_ms: 30000
      },
      country_results: []
    }
  }),
  mockAnalysisHistory: vi.fn().mockResolvedValue({
    success: true,
    analyses: [],
    total_count: 0,
    has_more: false
  }),
  mockExportCreate: vi.fn().mockResolvedValue({
    success: true,
    export_id: 'test_export_123',
    status: 'generating',
    format: 'pdf'
  }),
  mockGetExport: vi.fn().mockResolvedValue({
    success: true,
    export_id: 'test_export_123',
    status: 'completed',
    download_url: 'http://test.com/export.pdf',
    format: 'pdf'
  })
}));

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('apiResearch', () => {
    it('should call research API with query', async () => {
      const result = await apiResearch('test query');
      
      expect(result).toEqual({
        success: true,
        query: 'test query',
        search_terms: ['test'],
        sources_count: 1,
        final_answer: 'test answer',
        sources: ['http://test.com']
      });
    });
  });

  describe('apiChatMessage', () => {
    it('should send chat message and return parsed intent', async () => {
      const request = {
        message: 'Analyze sentiment',
        session_id: 'test_session'
      };
      
      const result = await apiChatMessage(request);
      
      expect(result.success).toBe(true);
      expect(result.response_type).toBe('query_parsed');
      expect(result.analysis_id).toBe('test_analysis_123');
    });
  });

  describe('apiAnalysisExecute', () => {
    it('should start analysis execution', async () => {
      const request = {
        query_text: 'Test analysis',
        parameters: {
          countries: ['US', 'UK'],
          days: 7,
          results_per_country: 20
        },
        session_id: 'test_session'
      };
      
      const result = await apiAnalysisExecute(request);
      
      expect(result.success).toBe(true);
      expect(result.status).toBe('processing');
      expect(result.analysis_id).toBe('test_analysis_123');
    });
  });

  describe('apiGetAnalysis', () => {
    it('should fetch analysis results', async () => {
      const result = await apiGetAnalysis('test_analysis_123');
      
      expect(result.success).toBe(true);
      expect(result.status).toBe('completed');
      expect(result.results).toBeDefined();
      expect(result.results?.summary.overall_sentiment).toBe(-0.5);
    });
  });

  describe('apiAnalysisHistory', () => {
    it('should fetch analysis history with pagination', async () => {
      const result = await apiAnalysisHistory(10, 0);
      
      expect(result.success).toBe(true);
      expect(result.analyses).toEqual([]);
      expect(result.total_count).toBe(0);
      expect(result.has_more).toBe(false);
    });
  });

  describe('apiExportCreate', () => {
    it('should create export request', async () => {
      const request = {
        analysis_id: 'test_analysis_123',
        format: 'pdf' as const,
        options: {
          include_bias_details: true
        }
      };
      
      const result = await apiExportCreate(request);
      
      expect(result.success).toBe(true);
      expect(result.status).toBe('generating');
      expect(result.format).toBe('pdf');
    });
  });

  describe('apiGetExport', () => {
    it('should fetch export status and download URL', async () => {
      const result = await apiGetExport('test_export_123');
      
      expect(result.success).toBe(true);
      expect(result.status).toBe('completed');
      expect(result.download_url).toBe('http://test.com/export.pdf');
    });
  });
});
