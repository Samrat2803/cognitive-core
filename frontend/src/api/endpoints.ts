import { API_CONFIG } from '../config';

export const ENDPOINTS = {
  health: () => `${API_CONFIG.baseURL}${API_CONFIG.endpoints.health}`,
  research: () => `${API_CONFIG.baseURL}${API_CONFIG.endpoints.research}`,
  chatMessage: () => `${API_CONFIG.baseURL}${API_CONFIG.endpoints.chatMessage}`,
  chatConfirm: () => `${API_CONFIG.baseURL}${API_CONFIG.endpoints.chatConfirm}`,
  analysisExecute: () => `${API_CONFIG.baseURL}${API_CONFIG.endpoints.analysisExecute}`,
  analysisById: (id: string) => `${API_CONFIG.baseURL}${API_CONFIG.endpoints.analysisById(id)}`,
  exportCreate: () => `${API_CONFIG.baseURL}${API_CONFIG.endpoints.exportCreate}`,
  exportById: (id: string) => `${API_CONFIG.baseURL}${API_CONFIG.endpoints.exportById(id)}`,
  exportDownload: (id: string) => `${API_CONFIG.baseURL}${API_CONFIG.endpoints.exportDownload(id)}`,
};

export const WS = {
  session: (sessionId: string) => `${API_CONFIG.wsBaseURL}/${sessionId}`,
};


