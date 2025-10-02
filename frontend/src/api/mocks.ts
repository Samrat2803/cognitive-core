// Minimal in-app mocks aligned to API contracts (MVP)
import { ResearchResponse } from '../types';

const delay = (ms: number) => new Promise((res) => setTimeout(res, ms));

export const USE_MOCKS = (process.env.REACT_APP_USE_MOCKS || 'false') === 'true';

// Mock data store
const mockAnalyses = new Map<string, any>();
const mockExports = new Map<string, any>();

export async function mockResearch(query: string): Promise<ResearchResponse> {
  await delay(800);
  return {
    success: true,
    query,
    search_terms: ['example', 'mock', 'query'],
    sources_count: 3,
    final_answer: 'This is a mocked research answer for your query.',
    sources: [
      'https://example.com/a',
      'https://example.com/b',
      'https://example.com/c'
    ],
  };
}

export async function mockChatMessage(message: string, sessionId: string) {
  await delay(600);
  const analysisId = `analysis_${Date.now()}`;
  
  return {
    success: true,
    response_type: 'query_parsed' as const,
    parsed_intent: {
      action: 'sentiment_analysis',
      topic: 'Hamas',
      countries: ['United States', 'Iran', 'Israel'],
      parameters: {
        days: 7,
        results_per_country: 20
      }
    },
    confirmation: `I'll analyze sentiment for "${message}" across multiple countries. Proceed?`,
    analysis_id: analysisId
  };
}

export async function mockConfirmAnalysis(analysisId: string, confirmed: boolean) {
  await delay(300);
  if (!confirmed) {
    return { success: false, error: 'Analysis cancelled' };
  }
  
  // Store mock analysis
  mockAnalyses.set(analysisId, {
    analysis_id: analysisId,
    status: 'processing',
    progress: { completion_percentage: 0, current_step: 'initializing' },
    created_at: new Date().toISOString()
  });
  
  return {
    success: true,
    analysis_id: analysisId,
    status: 'queued' as const,
    estimated_completion: new Date(Date.now() + 30000).toISOString(),
    websocket_session: `ws_${analysisId}_${Date.now()}`
  };
}

export async function mockAnalysisExecute(queryText: string, parameters: any, sessionId: string) {
  await delay(500);
  const analysisId = `analysis_${Date.now()}`;
  
  mockAnalyses.set(analysisId, {
    analysis_id: analysisId,
    status: 'processing',
    progress: { completion_percentage: 0, current_step: 'initializing' },
    created_at: new Date().toISOString()
  });
  
  return {
    success: true,
    analysis_id: analysisId,
    status: 'processing' as const,
    estimated_completion: new Date(Date.now() + 45000).toISOString(),
    websocket_session: `ws_${sessionId}_${Date.now()}`,
    created_at: new Date().toISOString()
  };
}

export async function mockGetAnalysis(analysisId: string) {
  await delay(200);
  const analysis = mockAnalyses.get(analysisId);
  
  if (!analysis) {
    throw new Error('Analysis not found');
  }
  
  // Simulate progression
  const elapsed = Date.now() - new Date(analysis.created_at).getTime();
  if (elapsed > 20000) {
    // Complete after 20 seconds
    return {
      success: true,
      analysis_id: analysisId,
      status: 'completed' as const,
      query: {
        text: 'Hamas sentiment analysis',
        parameters: {
          countries: ['United States', 'Iran', 'Israel'],
          days: 7,
          results_per_country: 20
        }
      },
      results: {
        summary: {
          overall_sentiment: -0.23,
          countries_analyzed: 3,
          total_articles: 57,
          analysis_confidence: 0.89,
          bias_detected: true,
          completion_time_ms: elapsed
        },
        country_results: [
          {
            country: 'United States',
            sentiment_score: -0.45,
            confidence: 0.87,
            articles_count: 19,
            dominant_sentiment: 'negative',
            key_themes: ['conflict', 'terrorism', 'security'],
            bias_analysis: {
              bias_types: ['selection', 'framing'],
              bias_severity: 0.34,
              notes: 'Predominantly western media sources'
            }
          },
          {
            country: 'Iran',
            sentiment_score: 0.67,
            confidence: 0.82,
            articles_count: 18,
            dominant_sentiment: 'positive',
            key_themes: ['resistance', 'liberation', 'solidarity'],
            bias_analysis: {
              bias_types: ['source', 'language'],
              bias_severity: 0.52,
              notes: 'Limited English language sources'
            }
          }
        ]
      },
      created_at: analysis.created_at,
      completed_at: new Date().toISOString()
    };
  } else {
    // Still processing
    const progress = Math.min(90, Math.floor((elapsed / 20000) * 100));
    return {
      success: true,
      analysis_id: analysisId,
      status: 'processing' as const,
      progress: {
        current_step: progress < 30 ? 'searching_articles' : progress < 70 ? 'analyzing_sentiment' : 'finalizing_results',
        completion_percentage: progress,
        processed_countries: progress > 30 ? ['United States'] : [],
        remaining_countries: progress > 30 ? ['Iran', 'Israel'] : ['United States', 'Iran', 'Israel'],
        articles_processed: Math.floor(progress * 0.6),
        total_articles: 60
      },
      estimated_completion: new Date(Date.now() + (20000 - elapsed)).toISOString(),
      created_at: analysis.created_at
    };
  }
}

// mockAnalysisHistory removed - not implemented in backend

export async function mockExportCreate(analysisId: string, format: string, options: any) {
  await delay(400);
  const exportId = `export_${Date.now()}`;
  
  mockExports.set(exportId, {
    export_id: exportId,
    analysis_id: analysisId,
    status: 'generating',
    format,
    created_at: new Date().toISOString()
  });
  
  return {
    success: true,
    export_id: exportId,
    status: 'generating' as const,
    estimated_completion: new Date(Date.now() + 10000).toISOString(),
    format
  };
}

export async function mockGetExport(exportId: string) {
  await delay(200);
  const exportData = mockExports.get(exportId);
  
  if (!exportData) {
    throw new Error('Export not found');
  }
  
  const elapsed = Date.now() - new Date(exportData.created_at).getTime();
  if (elapsed > 8000) {
    return {
      success: true,
      export_id: exportId,
      status: 'completed' as const,
      download_url: `https://mock-s3.amazonaws.com/exports/${exportId}.${exportData.format}`,
      expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      file_size: 2048576,
      format: exportData.format
    };
  } else {
    return {
      success: true,
      export_id: exportId,
      status: 'generating' as const,
      progress: Math.floor((elapsed / 8000) * 100),
      estimated_completion: new Date(Date.now() + (8000 - elapsed)).toISOString(),
      format: exportData.format
    };
  }
}


