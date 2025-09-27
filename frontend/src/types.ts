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
