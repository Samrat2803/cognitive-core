import { API_CONFIG, getSessionId } from '../config';
import { ENDPOINTS } from './endpoints';
import { 
  USE_MOCKS, 
  mockResearch, 
  mockChatMessage, 
  mockConfirmAnalysis, 
  mockAnalysisExecute, 
  mockGetAnalysis, 
  mockExportCreate, 
  mockGetExport 
} from './mocks';
import {
  ResearchResponse,
  ChatMessageRequest,
  ChatMessageResponse,
  ConfirmAnalysisRequest,
  AnalysisExecuteRequest,
  AnalysisResponse,
  ExportCreateRequest,
  ExportResponse
} from '../types';

type HttpMethod = 'GET' | 'POST';

interface RequestOptions<TBody> {
  path: string;
  method?: HttpMethod;
  body?: TBody;
  signal?: AbortSignal;
}

interface ErrorEnvelope {
  success?: boolean;
  error?: string;
  code?: string;
  details?: Record<string, unknown>;
}

export async function httpRequest<TResponse, TBody = unknown>(options: RequestOptions<TBody>): Promise<TResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_CONFIG.timeout);

  try {
    const response = await fetch(options.path, {
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
      signal: options.signal || controller.signal,
    });

    const text = await response.text();
    const json = text ? JSON.parse(text) : {};

    if (!response.ok) {
      const err = json as ErrorEnvelope;
      const message = err?.error || `HTTP ${response.status}: ${response.statusText}`;
      throw new Error(message);
    }

    return json as TResponse;
  } finally {
    clearTimeout(timeout);
  }
}

// API Service Functions
export async function apiResearch(query: string): Promise<ResearchResponse> {
  if (USE_MOCKS) {
    return mockResearch(query);
  }
  
  return httpRequest<ResearchResponse>({
    path: ENDPOINTS.research(),
    method: 'POST',
    body: { query, user_session: getSessionId() }
  });
}

export async function apiChatMessage(request: ChatMessageRequest): Promise<ChatMessageResponse> {
  if (USE_MOCKS) {
    return mockChatMessage(request.message, request.session_id);
  }
  
  return httpRequest<ChatMessageResponse>({
    path: ENDPOINTS.chatMessage(),
    method: 'POST',
    body: request
  });
}

export async function apiConfirmAnalysis(request: ConfirmAnalysisRequest): Promise<any> {
  if (USE_MOCKS) {
    return mockConfirmAnalysis(request.analysis_id, request.confirmed);
  }
  
  return httpRequest({
    path: ENDPOINTS.chatConfirm(),
    method: 'POST',
    body: request
  });
}

export async function apiAnalysisExecute(request: AnalysisExecuteRequest): Promise<AnalysisResponse> {
  if (USE_MOCKS) {
    return mockAnalysisExecute(request.query_text, request.parameters, request.session_id);
  }
  
  return httpRequest<AnalysisResponse>({
    path: ENDPOINTS.analysisExecute(),
    method: 'POST',
    body: request
  });
}

export async function apiGetAnalysis(analysisId: string): Promise<AnalysisResponse> {
  if (USE_MOCKS) {
    return mockGetAnalysis(analysisId);
  }
  
  return httpRequest<AnalysisResponse>({
    path: ENDPOINTS.analysisById(analysisId),
    method: 'GET'
  });
}

// History endpoint removed - not implemented in backend

export async function apiExportCreate(request: ExportCreateRequest): Promise<ExportResponse> {
  if (USE_MOCKS) {
    return mockExportCreate(request.analysis_id, request.format, request.options);
  }
  
  return httpRequest<ExportResponse>({
    path: ENDPOINTS.exportCreate(),
    method: 'POST',
    body: request
  });
}

export async function apiGetExport(exportId: string): Promise<ExportResponse> {
  if (USE_MOCKS) {
    return mockGetExport(exportId);
  }
  
  return httpRequest<ExportResponse>({
    path: ENDPOINTS.exportById(exportId),
    method: 'GET'
  });
}

export async function apiDownloadExport(exportId: string): Promise<Blob> {
  // For mocks, just return a dummy blob
  if (USE_MOCKS) {
    return new Blob(['Mock export content'], { type: 'application/octet-stream' });
  }
  
  const response = await fetch(ENDPOINTS.exportDownload(exportId));
  if (!response.ok) {
    throw new Error(`Download failed: ${response.statusText}`);
  }
  return response.blob();
}


