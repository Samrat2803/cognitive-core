import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import { API_CONFIG, getSessionId } from '../config';
import { ResearchResponse } from '../types';

interface ResearchState {
  status: 'idle' | 'loading' | 'completed' | 'error';
  results: ResearchResponse | null;
  error: string | null;
  progress: number;
  currentStep: string;
}

interface UseResearchQueryReturn extends ResearchState {
  submitQuery: (query: string) => Promise<void>;
  reset: () => void;
  exportResults: (format: 'json' | 'csv' | 'pdf') => void;
}

export const useResearchQuery = (): UseResearchQueryReturn => {
  const [state, setState] = useState<ResearchState>({
    status: 'idle',
    results: null,
    error: null,
    progress: 0,
    currentStep: ''
  });

  const submitQuery = useCallback(async (query: string) => {
    setState(prev => ({ 
      ...prev, 
      status: 'loading', 
      error: null, 
      progress: 10,
      currentStep: 'Initializing research...'
    }));
    
    try {
      // Simulate progress updates during loading
      const progressUpdates = [
        { progress: 25, step: 'Analyzing query...' },
        { progress: 50, step: 'Searching web sources...' },
        { progress: 75, step: 'Processing results...' },
        { progress: 90, step: 'Generating final answer...' }
      ];

      let currentProgressIndex = 0;
      
      const progressInterval = setInterval(() => {
        if (currentProgressIndex < progressUpdates.length) {
          setState(prev => ({
            ...prev,
            progress: progressUpdates[currentProgressIndex].progress,
            currentStep: progressUpdates[currentProgressIndex].step
          }));
          currentProgressIndex++;
        }
      }, 2000); // Update progress every 2 seconds

      // Make API call to current backend
      const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.research}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query,
          // Add user session for future database integration
          user_session: getSessionId()
        }),
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const results: ResearchResponse = await response.json();
      
      // Save to local storage for query history
      const queryHistory = JSON.parse(localStorage.getItem('research_history') || '[]');
      queryHistory.unshift({
        id: Date.now().toString(),
        query,
        timestamp: new Date().toISOString(),
        success: results.success,
        results: results.success ? results : null
      });
      
      // Keep only last 10 queries
      localStorage.setItem('research_history', JSON.stringify(queryHistory.slice(0, 10)));

      setState(prev => ({
        ...prev,
        status: 'completed',
        results,
        progress: 100,
        currentStep: 'Research completed!'
      }));

      toast.success('Research completed successfully!', {
        duration: 3000
      });
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred';
      setState(prev => ({
        ...prev,
        status: 'error',
        error: errorMessage,
        progress: 0,
        currentStep: ''
      }));

      toast.error(`Research failed: ${errorMessage}`, {
        duration: 5000
      });
    }
  }, []);

  const reset = useCallback(() => {
    setState({
      status: 'idle',
      results: null,
      error: null,
      progress: 0,
      currentStep: ''
    });
  }, []);

  const exportResults = useCallback((format: 'json' | 'csv' | 'pdf') => {
    if (!state.results) return;

    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `research-results-${timestamp}`;

    if (format === 'json') {
      const blob = new Blob([JSON.stringify(state.results, null, 2)], {
        type: 'application/json'
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${filename}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } else if (format === 'csv') {
      const csvData = convertToCSV(state.results);
      const blob = new Blob([csvData], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${filename}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } else if (format === 'pdf') {
      // PDF export will be implemented with jsPDF in ExportButton component
      console.log('PDF export will be handled by ExportButton component');
    }
  }, [state.results]);

  return {
    ...state,
    submitQuery,
    reset,
    exportResults
  };
};

// Helper function to convert results to CSV format
const convertToCSV = (results: ResearchResponse): string => {
  const headers = ['Query', 'Success', 'Answer', 'Sources Count', 'Search Terms', 'Sources'];
  const row = [
    `"${results.query.replace(/"/g, '""')}"`,
    results.success.toString(),
    `"${(results.final_answer || '').replace(/"/g, '""')}"`,
    results.sources_count.toString(),
    `"${results.search_terms.join(', ')}"`,
    `"${results.sources.join('; ')}"`
  ];
  
  return [headers, row].map(r => r.join(',')).join('\n');
};
