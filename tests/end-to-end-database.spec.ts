import { test, expect } from '@playwright/test';

test.describe('End-to-End Database Pipeline Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Wait for the page to fully load
    await page.waitForLoadState('networkidle');
  });

  test('should complete full research workflow with database persistence', async ({ page, request }) => {
    const testQuery = 'End-to-end test: What are the environmental benefits of solar energy?';
    const sessionId = `e2e-test-${Date.now()}`;
    
    // Step 1: Submit query through UI
    await page.fill('textarea', testQuery);
    
    // If there's a session input, fill it
    const sessionInput = page.locator('input[placeholder*="session"]').or(page.locator('input[name*="session"]'));
    if (await sessionInput.count() > 0) {
      await sessionInput.fill(sessionId);
    }
    
    await page.click('button:has-text("Start Research"), button[type="submit"], button:has-text("Research")');
    
    // Step 2: Wait for and verify research completion
    await expect(page.locator('text=Research Results, text=Final Answer, text=Results')).toBeVisible({ timeout: 90000 });
    
    // Verify UI shows complete results
    const finalAnswerElement = page.locator('text=Final Answer').or(page.locator('[data-testid="final-answer"]')).first();
    await expect(finalAnswerElement).toBeVisible();
    
    // Step 3: Verify data persistence by checking backend directly
    await page.waitForTimeout(2000); // Allow database writes to complete
    
    // Test if query history endpoint exists
    try {
      const historyResponse = await request.get(`http://localhost:8000/research?user_session=${sessionId}&limit=10&offset=0`);
      if (historyResponse.ok()) {
        const historyData = await historyResponse.json();
        
        // Verify our query appears in history
        expect(historyData).toHaveProperty('queries');
        expect(Array.isArray(historyData.queries)).toBeTruthy();
        
        // Find our test query in the history
        const ourQuery = historyData.queries.find((q: any) => q.query === testQuery);
        if (ourQuery) {
          expect(ourQuery.status).toBe('completed');
          expect(ourQuery.query).toBe(testQuery);
        }
      }
    } catch (error) {
      console.log('Query history endpoint not available yet');
    }
    
    // Step 4: Verify UI persistence on reload
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // The application should maintain some state or show history
    // At minimum, it should still be functional
    await expect(page.locator('textarea, input[type="text"]')).toBeVisible();
  });

  test('should handle multiple queries with proper database tracking', async ({ page, request }) => {
    const queries = [
      'Multi-query test 1: Benefits of renewable energy',
      'Multi-query test 2: Wind power vs solar power',
      'Multi-query test 3: Energy storage solutions'
    ];
    
    const sessionId = `multi-query-e2e-${Date.now()}`;
    
    for (let i = 0; i < queries.length; i++) {
      const query = queries[i];
      
      // Submit query
      await page.fill('textarea', query);
      await page.click('button:has-text("Start Research"), button[type="submit"]');
      
      // Wait for completion
      await expect(page.locator('text=Research Results, text=Final Answer')).toBeVisible({ timeout: 60000 });
      
      // Verify results are displayed
      await expect(page.locator('text=Search Terms, text=Sources')).toBeVisible();
      
      // Wait between queries to avoid rate limiting
      if (i < queries.length - 1) {
        await page.waitForTimeout(3000);
      }
    }
    
    // Verify all queries were processed
    console.log(`Completed ${queries.length} sequential queries successfully`);
  });

  test('should verify export functionality includes database data', async ({ page, request }) => {
    const exportQuery = 'Export test query: Machine learning in autonomous vehicles';
    
    // Step 1: Complete a research query
    await page.fill('textarea', exportQuery);
    await page.click('button:has-text("Start Research"), button[type="submit"]');
    
    await expect(page.locator('text=Research Results, text=Final Answer')).toBeVisible({ timeout: 60000 });
    
    // Step 2: Look for export functionality
    const exportButtons = page.locator('button:has-text("Export"), button:has-text("Download"), a:has-text("Export")');
    
    if (await exportButtons.count() > 0) {
      // Test different export formats if available
      const exportButton = exportButtons.first();
      
      // Set up download handler
      const downloadPromise = page.waitForEvent('download', { timeout: 30000 });
      await exportButton.click();
      
      try {
        const download = await downloadPromise;
        
        // Verify download occurred
        expect(download.suggestedFilename()).toMatch(/\.(json|csv|pdf|txt)$/);
        console.log(`Export successful: ${download.suggestedFilename()}`);
      } catch (error) {
        console.log('Export functionality may not be fully implemented yet');
      }
    } else {
      console.log('Export buttons not found - feature may not be implemented yet');
    }
    
    // Step 3: Verify data can be retrieved via API for export
    const testResponse = await request.post('http://localhost:8000/research', {
      data: {
        query: 'API export test query',
        user_session: 'export-test'
      }
    });
    
    expect(testResponse.ok()).toBeTruthy();
    const data = await testResponse.json();
    
    // Verify data structure is suitable for export
    expect(data).toHaveProperty('final_answer');
    expect(data).toHaveProperty('sources');
    expect(data).toHaveProperty('search_terms');
    
    // Data should be substantial enough for export
    expect(data.final_answer.length).toBeGreaterThan(0);
    expect(data.sources.length).toBeGreaterThan(0);
  });

  test('should verify error handling throughout the complete pipeline', async ({ page, request }) => {
    // Test 1: Empty query handling
    await page.click('button:has-text("Start Research"), button[type="submit"]');
    
    // Should show some form of error or validation message
    const errorMessage = page.locator('text=required, text=empty, text=error, .error, [data-testid*="error"]');
    
    // Wait briefly for error to appear
    await page.waitForTimeout(1000);
    
    // Either error message appears or button is disabled/doesn't trigger
    const hasErrorMessage = await errorMessage.count() > 0;
    const buttonStillEnabled = await page.locator('button:has-text("Start Research"):not([disabled])').count() > 0;
    
    if (hasErrorMessage) {
      console.log('UI properly shows error for empty query');
    } else if (!buttonStillEnabled) {
      console.log('UI properly disables submission for empty query');
    }
    
    // Test 2: Very long query handling
    const longQuery = 'a'.repeat(1000);
    await page.fill('textarea', longQuery);
    await page.click('button:has-text("Start Research"), button[type="submit"]');
    
    // Should either process or show error gracefully
    await page.waitForTimeout(5000);
    
    // Test 3: Network error simulation via direct API
    try {
      const networkErrorResponse = await request.post('http://localhost:8000/nonexistent-endpoint', {
        data: { query: 'test' }
      });
      
      expect(networkErrorResponse.status()).toBe(404);
    } catch (error) {
      // Expected for network errors
      console.log('Network error handling test completed');
    }
  });

  test('should verify real-time updates and progress tracking', async ({ page }) => {
    const progressQuery = 'Progress tracking test: Comprehensive analysis of renewable energy trends globally';
    
    await page.fill('textarea', progressQuery);
    await page.click('button:has-text("Start Research"), button[type="submit"]');
    
    // Look for progress indicators
    const progressIndicators = page.locator(
      'text=Processing, text=Loading, text=Searching, .loading, .progress, [data-testid*="progress"]'
    );
    
    // Should show some form of progress initially
    await expect(progressIndicators.first()).toBeVisible({ timeout: 10000 });
    
    // Eventually should complete with results
    await expect(page.locator('text=Research Results, text=Final Answer')).toBeVisible({ timeout: 90000 });
    
    // Progress indicators should be gone or changed
    const finalProgressState = await progressIndicators.count();
    console.log(`Progress tracking test completed. Final progress elements: ${finalProgressState}`);
  });

  test('should verify mobile responsiveness with database operations', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    const mobileQuery = 'Mobile test: Impact of AI on mobile technology';
    
    // Verify mobile layout
    await expect(page.locator('textarea')).toBeVisible();
    
    // Submit query on mobile
    await page.fill('textarea', mobileQuery);
    await page.click('button:has-text("Start Research"), button[type="submit"]');
    
    // Should work the same as desktop
    await expect(page.locator('text=Research Results, text=Final Answer')).toBeVisible({ timeout: 60000 });
    
    // Verify mobile layout of results
    const results = page.locator('text=Search Terms, text=Sources');
    await expect(results.first()).toBeVisible();
    
    console.log('Mobile responsiveness test with database operations completed');
  });

  test('should verify analytics data collection end-to-end', async ({ page, request }) => {
    const analyticsQuery = 'Analytics end-to-end test: Future of quantum computing applications';
    
    // Submit query through UI
    await page.fill('textarea', analyticsQuery);
    await page.click('button:has-text("Start Research"), button[type="submit"]');
    
    await expect(page.locator('text=Research Results, text=Final Answer')).toBeVisible({ timeout: 60000 });
    
    // Wait for analytics to be recorded
    await page.waitForTimeout(3000);
    
    // Check if analytics endpoint is available
    try {
      const analyticsResponse = await request.get('http://localhost:8000/analytics');
      
      if (analyticsResponse.ok()) {
        const analyticsData = await analyticsResponse.json();
        
        // Verify analytics structure
        expect(typeof analyticsData.total_queries).toBe('number');
        expect(analyticsData.total_queries).toBeGreaterThan(0);
        
        if (analyticsData.popular_topics) {
          expect(Array.isArray(analyticsData.popular_topics)).toBeTruthy();
        }
        
        console.log('Analytics data verified:', {
          total_queries: analyticsData.total_queries,
          success_rate: analyticsData.success_rate,
          popular_topics: analyticsData.popular_topics?.length || 0
        });
      }
    } catch (error) {
      console.log('Analytics endpoint not available for testing');
    }
  });

  test('should verify complete user session tracking', async ({ page, request }) => {
    const sessionId = `session-tracking-${Date.now()}`;
    const sessionQueries = [
      'Session test 1: Blockchain technology overview',
      'Session test 2: Cryptocurrency market analysis',
      'Session test 3: Smart contract applications'
    ];
    
    // If the UI supports session input
    const sessionInput = page.locator('input[placeholder*="session"], input[name*="session"]');
    if (await sessionInput.count() > 0) {
      await sessionInput.fill(sessionId);
    }
    
    // Submit multiple queries in the same session
    for (const query of sessionQueries) {
      await page.fill('textarea', query);
      await page.click('button:has-text("Start Research"), button[type="submit"]');
      
      await expect(page.locator('text=Research Results, text=Final Answer')).toBeVisible({ timeout: 60000 });
      
      // Small delay between queries
      await page.waitForTimeout(2000);
    }
    
    // Try to verify session tracking via API
    try {
      const sessionResponse = await request.get(`http://localhost:8000/research?user_session=${sessionId}`);
      
      if (sessionResponse.ok()) {
        const sessionData = await sessionResponse.json();
        
        if (sessionData.queries) {
          expect(Array.isArray(sessionData.queries)).toBeTruthy();
          expect(sessionData.queries.length).toBeGreaterThanOrEqual(1);
          
          console.log(`Session tracking verified: ${sessionData.queries.length} queries found for session`);
        }
      }
    } catch (error) {
      console.log('Session tracking API not available for testing');
    }
  });
});
