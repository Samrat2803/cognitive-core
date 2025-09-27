import { test, expect } from '@playwright/test';

test.describe('API Integration Tests', () => {
  test('should test backend API endpoints directly', async ({ request }) => {
    // Test root endpoint
    const rootResponse = await request.get('http://localhost:8000/');
    expect(rootResponse.ok()).toBeTruthy();
    
    const rootData = await rootResponse.json();
    expect(rootData).toHaveProperty('message', 'Web Research Agent API');
    expect(rootData).toHaveProperty('status', 'running');
  });

  test('should test health check endpoint', async ({ request }) => {
    const healthResponse = await request.get('http://localhost:8000/health');
    expect(healthResponse.ok()).toBeTruthy();
    
    const healthData = await healthResponse.json();
    expect(healthData).toHaveProperty('status', 'healthy');
    expect(healthData).toHaveProperty('agent_initialized', true);
  });

  test('should test config endpoint', async ({ request }) => {
    const configResponse = await request.get('http://localhost:8000/config');
    expect(configResponse.ok()).toBeTruthy();
    
    const configData = await configResponse.json();
    expect(configData).toHaveProperty('llm_provider');
    expect(configData).toHaveProperty('max_query_length');
    expect(configData).toHaveProperty('max_sources_display');
    expect(configData).toHaveProperty('search_depth');
  });

  test('should test research endpoint with valid query', async ({ request }) => {
    const researchResponse = await request.post('http://localhost:8000/research', {
      data: {
        query: 'What is artificial intelligence?'
      }
    });
    
    expect(researchResponse.ok()).toBeTruthy();
    
    const researchData = await researchResponse.json();
    expect(researchData).toHaveProperty('success', true);
    expect(researchData).toHaveProperty('query', 'What is artificial intelligence?');
    expect(researchData).toHaveProperty('search_terms');
    expect(researchData).toHaveProperty('sources_count');
    expect(researchData).toHaveProperty('final_answer');
    expect(researchData).toHaveProperty('sources');
    expect(Array.isArray(researchData.search_terms)).toBeTruthy();
    expect(Array.isArray(researchData.sources)).toBeTruthy();
    expect(typeof researchData.final_answer).toBe('string');
    expect(researchData.final_answer.length).toBeGreaterThan(0);
  });

  test('should handle empty query in API', async ({ request }) => {
    const response = await request.post('http://localhost:8000/research', {
      data: {
        query: ''
      }
    });
    
    expect(response.status()).toBe(400);
    
    const errorData = await response.json();
    expect(errorData).toHaveProperty('detail', 'Query cannot be empty');
  });

  test('should handle query that is too long in API', async ({ request }) => {
    const longQuery = 'a'.repeat(501);
    
    const response = await request.post('http://localhost:8000/research', {
      data: {
        query: longQuery
      }
    });
    
    expect(response.status()).toBe(400);
    
    const errorData = await response.json();
    expect(errorData.detail).toContain('Query too long');
  });

  test('should test CORS headers', async ({ request }) => {
    const response = await request.get('http://localhost:8000/health', {
      headers: {
        'Origin': 'http://localhost:3000'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    
    // Check CORS headers
    const headers = response.headers();
    expect(headers['access-control-allow-origin']).toBe('http://localhost:3000');
  });

  test('should test research with different LLM providers', async ({ request }) => {
    // Test with default provider
    const defaultResponse = await request.post('http://localhost:8000/research', {
      data: {
        query: 'What is machine learning?'
      }
    });
    
    expect(defaultResponse.ok()).toBeTruthy();
    
    // Test with explicit provider
    const explicitResponse = await request.post('http://localhost:8000/research', {
      data: {
        query: 'What is deep learning?',
        llm_provider: 'openai'
      }
    });
    
    expect(explicitResponse.ok()).toBeTruthy();
    
    const defaultData = await defaultResponse.json();
    const explicitData = await explicitResponse.json();
    
    expect(defaultData.success).toBeTruthy();
    expect(explicitData.success).toBeTruthy();
  });

  test('should handle concurrent research requests', async ({ request }) => {
    const queries = [
      'What is artificial intelligence?',
      'What is machine learning?',
      'What is deep learning?'
    ];
    
    // Send multiple requests concurrently
    const promises = queries.map(query => 
      request.post('http://localhost:8000/research', {
        data: { query }
      })
    );
    
    const responses = await Promise.all(promises);
    
    // All requests should succeed
    responses.forEach(response => {
      expect(response.ok()).toBeTruthy();
    });
    
    // All should return valid data
    const dataPromises = responses.map(response => response.json());
    const allData = await Promise.all(dataPromises);
    
    allData.forEach(data => {
      expect(data.success).toBeTruthy();
      expect(data.final_answer.length).toBeGreaterThan(0);
    });
  });

  test('should validate response structure', async ({ request }) => {
    const response = await request.post('http://localhost:8000/research', {
      data: {
        query: 'What are the benefits of renewable energy?'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    
    // Validate all required fields
    expect(data).toHaveProperty('success', true);
    expect(data).toHaveProperty('query');
    expect(data).toHaveProperty('search_terms');
    expect(data).toHaveProperty('sources_count');
    expect(data).toHaveProperty('final_answer');
    expect(data).toHaveProperty('sources');
    
    // Validate data types
    expect(typeof data.success).toBe('boolean');
    expect(typeof data.query).toBe('string');
    expect(Array.isArray(data.search_terms)).toBeTruthy();
    expect(typeof data.sources_count).toBe('number');
    expect(typeof data.final_answer).toBe('string');
    expect(Array.isArray(data.sources)).toBeTruthy();
    
    // Validate data content
    expect(data.query.length).toBeGreaterThan(0);
    expect(data.search_terms.length).toBeGreaterThan(0);
    expect(data.sources_count).toBeGreaterThan(0);
    expect(data.final_answer.length).toBeGreaterThan(0);
    expect(data.sources.length).toBeGreaterThan(0);
    
    // Validate sources are URLs
    data.sources.forEach((source: string) => {
      expect(source).toMatch(/^https?:\/\//);
    });
  });
});
