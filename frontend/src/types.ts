export interface ResearchResponse {
  success: boolean;
  query: string;
  search_terms: string[];
  sources_count: number;
  final_answer: string;
  sources: string[];
  error?: string;
}

export interface ResearchRequest {
  query: string;
  llm_provider?: string;
  model?: string;
}

// Chat API types
export interface ChatMessageRequest {
  message: string;
  session_id: string;
  context?: {
    previous_queries?: string[];
    current_analysis_id?: string;
  };
}

export interface ChatMessageResponse {
  success: boolean;
  response_type: 'query_parsed' | 'direct_response';
  parsed_intent?: {
    action: string;
    topic: string;
    countries: string[];
    parameters: Record<string, any>;
  };
  confirmation?: string;
  analysis_id?: string;
  message?: string;
  suggestions?: string[];
  error?: string;
}

export interface ConfirmAnalysisRequest {
  analysis_id: string;
  confirmed: boolean;
  modifications?: {
    countries?: string[];
    days?: number;
  };
}

// Analysis API types
export interface AnalysisExecuteRequest {
  query_text: string;
  parameters: {
    countries: string[];
    days: number;
    results_per_country: number;
    include_bias_analysis?: boolean;
  };
  session_id: string;
}

export interface AnalysisResponse {
  success: boolean;
  analysis_id: string;
  status: 'processing' | 'completed' | 'failed' | 'queued';
  progress?: {
    current_step: string;
    completion_percentage: number;
    processed_countries?: string[];
    remaining_countries?: string[];
    articles_processed?: number;
    total_articles?: number;
  };
  estimated_completion?: string;
  websocket_session?: string;
  created_at: string;
  completed_at?: string;
  query?: {
    text: string;
    parameters: Record<string, any>;
  };
  results?: {
    summary: {
      overall_sentiment: number;
      countries_analyzed: number;
      total_articles: number;
      analysis_confidence: number;
      bias_detected: boolean;
      completion_time_ms: number;
    };
    country_results: Array<{
      country: string;
      sentiment_score: number;
      confidence: number;
      articles_count: number;
      dominant_sentiment: string;
      key_themes: string[];
      bias_analysis: {
        bias_types: string[];
        bias_severity: number;
        notes: string;
      };
    }>;
  };
}

// AnalysisHistoryResponse removed - not implemented in backend

// Export API types
export interface ExportCreateRequest {
  analysis_id: string;
  format: 'pdf' | 'csv' | 'json' | 'excel';
  options?: {
    include_full_articles?: boolean;
    include_bias_details?: boolean;
    template?: 'executive_summary' | 'detailed' | 'technical';
  };
}

export interface ExportResponse {
  success: boolean;
  export_id: string;
  status: 'generating' | 'completed' | 'failed';
  progress?: number;
  estimated_completion?: string;
  download_url?: string;
  expires_at?: string;
  file_size?: number;
  format: string;
}

// 2-MVP Streaming & Citations types
export interface Citation {
  id: string;
  url: string;
  title: string;
  domain: string;
  credibility: number;
  published_at?: string;
}

export interface StreamingMessage {
  type: 'token' | 'ping' | 'pong' | 'complete' | 'analysis_error';
  content?: string;
  index?: number;
  timestamp?: string;
  analysis_id?: string;
  citations?: Citation[];
  usage?: {
    tokens: number;
  };
  error?: {
    code: string;
    message: string;
    recoverable: boolean;
  };
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
  isStreaming?: boolean;
}
