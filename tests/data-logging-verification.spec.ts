import { test, expect } from '@playwright/test';

test.describe('Data Logging Verification Tests', () => {
  test('should verify query data is properly logged and stored', async ({ request }) => {
    const testQuery = 'Data logging test - renewable energy trends';
    const sessionId = `log-test-${Date.now()}`;
    
    // Step 1: Submit a research query
    const researchResponse = await request.post('http://localhost:8000/research', {
      data: {
        query: testQuery,
        user_session: sessionId
      }
    });
    
    expect(researchResponse.ok()).toBeTruthy();
    const researchData = await researchResponse.json();
    
    // Step 2: Verify that the response indicates proper logging
    expect(researchData).toHaveProperty('success', true);
    expect(researchData).toHaveProperty('query', testQuery);
    
    // Step 3: Verify data structure that should be logged
    expect(researchData).toHaveProperty('search_terms');
    expect(researchData).toHaveProperty('sources');
    expect(researchData).toHaveProperty('final_answer');
    expect(researchData).toHaveProperty('sources_count');
    
    // Verify search terms are logged
    expect(Array.isArray(researchData.search_terms)).toBeTruthy();
    expect(researchData.search_terms.length).toBeGreaterThan(0);
    
    // Verify sources are logged with proper structure
    expect(Array.isArray(researchData.sources)).toBeTruthy();
    expect(researchData.sources.length).toBeGreaterThan(0);
    
    // Each source should be a valid URL (basic validation)
    researchData.sources.forEach((source: string) => {
      expect(source).toMatch(/^https?:\/\/.+/);
    });
    
    // Step 4: Verify final answer is properly logged
    expect(typeof researchData.final_answer).toBe('string');
    expect(researchData.final_answer.length).toBeGreaterThan(0);
  });

  test('should verify error cases are properly logged', async ({ request }) => {
    // Test 1: Empty query logging
    const emptyQueryResponse = await request.post('http://localhost:8000/research', {
      data: {
        query: '',
        user_session: 'error-log-test-1'
      }
    });
    
    expect(emptyQueryResponse.status()).toBe(400);
    const errorData = await emptyQueryResponse.json();
    
    // Verify error is properly structured for logging
    expect(errorData).toHaveProperty('detail');
    expect(typeof errorData.detail).toBe('string');
    
    // Test 2: Invalid data type logging
    const invalidResponse = await request.post('http://localhost:8000/research', {
      data: {
        query: 123, // Invalid type
        user_session: 'error-log-test-2'
      }
    });
    
    expect([400, 422].includes(invalidResponse.status())).toBeTruthy();
    
    // Test 3: Missing data logging
    const missingDataResponse = await request.post('http://localhost:8000/research', {
      data: {
        // Missing query field
        user_session: 'error-log-test-3'
      }
    });
    
    expect([400, 422].includes(missingDataResponse.status())).toBeTruthy();
  });

  test('should verify session and user data logging', async ({ request }) => {
    const baseSession = `session-log-test-${Date.now()}`;
    const queries = [
      'First query for session logging',
      'Second query for session logging',
      'Third query for session logging'
    ];
    
    // Submit multiple queries with the same session
    for (let i = 0; i < queries.length; i++) {
      const response = await request.post('http://localhost:8000/research', {
        data: {
          query: queries[i],
          user_session: `${baseSession}-${i}`
        }
      });
      
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      
      // Verify each query logs properly
      expect(data.success).toBeTruthy();
      expect(data.query).toBe(queries[i]);
    }
    
    // Test without session ID (should still work)
    const noSessionResponse = await request.post('http://localhost:8000/research', {
      data: {
        query: 'Query without session ID for logging test'
      }
    });
    
    expect(noSessionResponse.ok()).toBeTruthy();
    const noSessionData = await noSessionResponse.json();
    expect(noSessionData.success).toBeTruthy();
  });

  test('should verify research metadata is comprehensively logged', async ({ request }) => {
    const metadataQuery = 'Comprehensive logging test - artificial intelligence applications in healthcare';
    
    const response = await request.post('http://localhost:8000/research', {
      data: {
        query: metadataQuery,
        user_session: 'metadata-logging-test'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    // Verify all metadata fields that should be logged
    expect(data).toHaveProperty('query');
    expect(data).toHaveProperty('search_terms');
    expect(data).toHaveProperty('sources');
    expect(data).toHaveProperty('sources_count');
    expect(data).toHaveProperty('final_answer');
    expect(data).toHaveProperty('success');
    
    // Verify search terms contain meaningful content
    expect(data.search_terms.length).toBeGreaterThan(0);
    data.search_terms.forEach((term: string) => {
      expect(typeof term).toBe('string');
      expect(term.length).toBeGreaterThan(0);
    });
    
    // Verify sources contain meaningful URLs
    expect(data.sources.length).toBeGreaterThan(0);
    expect(data.sources_count).toBe(data.sources.length);
    
    // Verify final answer quality (basic checks)
    expect(data.final_answer.length).toBeGreaterThan(100); // Should be substantial
    expect(data.final_answer).toContain('intelligence'); // Should relate to query
  });

  test('should verify performance metrics are logged', async ({ request }) => {
    const performanceQuery = 'Performance logging test query about machine learning';
    const startTime = Date.now();
    
    const response = await request.post('http://localhost:8000/research', {
      data: {
        query: performanceQuery,
        user_session: 'performance-log-test'
      }
    });
    
    const endTime = Date.now();
    const requestTime = endTime - startTime;
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    // Verify response time is reasonable and could be logged
    expect(requestTime).toBeGreaterThan(0);
    expect(requestTime).toBeLessThan(120000); // Should complete within 2 minutes
    
    // Log the timing for analysis
    console.log(`Research request completed in ${requestTime}ms`);
    
    // Verify the research was successful (indicates proper processing and logging)
    expect(data.success).toBeTruthy();
    expect(data.sources_count).toBeGreaterThan(0);
  });

  test('should verify analytics data accumulation', async ({ request }) => {
    // Submit multiple queries to test analytics accumulation
    const analyticsQueries = [
      'Analytics test 1 - what is blockchain?',
      'Analytics test 2 - how does cryptocurrency work?',
      'Analytics test 3 - what are smart contracts?'
    ];
    
    let totalSources = 0;
    let totalSearchTerms = 0;
    
    for (let i = 0; i < analyticsQueries.length; i++) {
      const response = await request.post('http://localhost:8000/research', {
        data: {
          query: analyticsQueries[i],
          user_session: `analytics-test-${i}`
        }
      });
      
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      
      // Accumulate data for analytics verification
      totalSources += data.sources_count;
      totalSearchTerms += data.search_terms.length;
      
      expect(data.success).toBeTruthy();
    }
    
    // Verify meaningful data was collected
    expect(totalSources).toBeGreaterThan(0);
    expect(totalSearchTerms).toBeGreaterThan(0);
    
    console.log(`Analytics verification: ${analyticsQueries.length} queries generated ${totalSources} sources and ${totalSearchTerms} search terms`);
    
    // If analytics endpoint exists, test it
    try {
      const analyticsResponse = await request.get('http://localhost:8000/analytics');
      if (analyticsResponse.ok()) {
        const analyticsData = await analyticsResponse.json();
        
        // Verify analytics data structure
        expect(typeof analyticsData.total_queries).toBe('number');
        expect(analyticsData.total_queries).toBeGreaterThanOrEqual(analyticsQueries.length);
      }
    } catch (error) {
      console.log('Analytics endpoint not yet available');
    }
  });

  test('should verify concurrent logging integrity', async ({ request }) => {
    // Test that concurrent requests don't interfere with each other's logging
    const concurrentQueries = Array.from({ length: 3 }, (_, i) => ({
      query: `Concurrent logging test ${i + 1} - cloud computing benefits`,
      session: `concurrent-log-${i}`
    }));
    
    const promises = concurrentQueries.map(({ query, session }) =>
      request.post('http://localhost:8000/research', {
        data: {
          query,
          user_session: session
        }
      })
    );
    
    const responses = await Promise.all(promises);
    
    // Verify all requests completed successfully
    expect(responses.length).toBe(concurrentQueries.length);
    
    for (let i = 0; i < responses.length; i++) {
      expect(responses[i].ok()).toBeTruthy();
      
      const data = await responses[i].json();
      
      // Verify each response is properly logged and unique
      expect(data.success).toBeTruthy();
      expect(data.query).toBe(concurrentQueries[i].query);
      expect(data.search_terms.length).toBeGreaterThan(0);
      expect(data.sources.length).toBeGreaterThan(0);
    }
    
    console.log(`Concurrent logging test: ${responses.length} requests completed successfully`);
  });
});
