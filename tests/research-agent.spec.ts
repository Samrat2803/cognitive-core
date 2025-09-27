import { test, expect, Page } from '@playwright/test';

// Test data
const TEST_QUERIES = [
  'What are the latest developments in artificial intelligence?',
  'How is machine learning being used in healthcare?',
  'What are the current trends in renewable energy?'
];

const INVALID_QUERIES = [
  '', // Empty query
  'a'.repeat(501), // Too long query
];

// Helper function to wait for research to complete
async function waitForResearchComplete(page: Page) {
  // Wait for loading spinner to disappear
  await page.waitForSelector('.loading-spinner', { state: 'hidden', timeout: 60000 });
  
  // Wait for results to appear
  await page.waitForSelector('.research-results', { timeout: 10000 });
}

// Helper function to check if results are valid
async function validateResearchResults(page: Page) {
  // Check that results container exists
  await expect(page.locator('.research-results')).toBeVisible();
  
  // Check that we have search terms
  await expect(page.locator('.search-terms')).toBeVisible();
  await expect(page.locator('.term-tag')).toHaveCount({ min: 1 });
  
  // Check that we have a final answer
  await expect(page.locator('.final-answer')).toBeVisible();
  await expect(page.locator('.answer-content')).toBeVisible();
  
  // Check that we have sources
  await expect(page.locator('.sources')).toBeVisible();
  await expect(page.locator('.sources-list a')).toHaveCount({ min: 1 });
  
  // Check metadata
  await expect(page.locator('.results-meta')).toBeVisible();
  await expect(page.locator('.meta-item')).toHaveCount({ min: 2 });
}

test.describe('Web Research Agent UI Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
    
    // Wait for the page to load
    await expect(page.locator('.header')).toBeVisible();
    await expect(page.locator('.research-form')).toBeVisible();
  });

  test('should display the main page elements', async ({ page }) => {
    // Check header
    await expect(page.locator('.header h1')).toContainText('Web Research Agent');
    await expect(page.locator('.header p')).toContainText('Powered by LangGraph & Tavily');
    
    // Check form elements
    await expect(page.locator('textarea[id="query"]')).toBeVisible();
    await expect(page.locator('.submit-button')).toBeVisible();
    await expect(page.locator('.submit-button')).toContainText('Start Research');
  });

  test('should handle valid research queries', async ({ page }) => {
    for (const query of TEST_QUERIES) {
      // Clear any previous results
      await page.reload();
      await expect(page.locator('.research-form')).toBeVisible();
      
      // Enter query
      await page.fill('textarea[id="query"]', query);
      
      // Check character count
      await expect(page.locator('small')).toContainText(`${query.length}/500 characters`);
      
      // Submit form
      await page.click('.submit-button');
      
      // Wait for loading state
      await expect(page.locator('.submit-button')).toContainText('Researching...');
      await expect(page.locator('.loading-spinner')).toBeVisible();
      
      // Wait for research to complete
      await waitForResearchComplete(page);
      
      // Validate results
      await validateResearchResults(page);
      
      // Check that the query is displayed in results
      await expect(page.locator('.results-title')).toContainText('Research Results');
      
      // Check that sources are clickable
      const firstSource = page.locator('.sources-list a').first();
      await expect(firstSource).toBeVisible();
      await expect(firstSource).toHaveAttribute('href');
      await expect(firstSource).toHaveAttribute('target', '_blank');
    }
  });

  test('should handle empty query submission', async ({ page }) => {
    // Try to submit empty form
    await page.click('.submit-button');
    
    // Button should be disabled
    await expect(page.locator('.submit-button')).toBeDisabled();
  });

  test('should handle query that is too long', async ({ page }) => {
    const longQuery = 'a'.repeat(501);
    
    // Enter long query
    await page.fill('textarea[id="query"]', longQuery);
    
    // Check character count shows limit exceeded
    await expect(page.locator('small')).toContainText('501/500 characters');
    
    // Try to submit - should be disabled or show error
    await page.click('.submit-button');
    
    // Should show error or be disabled
    const submitButton = page.locator('.submit-button');
    const isDisabled = await submitButton.isDisabled();
    
    if (!isDisabled) {
      // If not disabled, should show error
      await expect(page.locator('.error-message')).toBeVisible();
    }
  });

  test('should display loading state correctly', async ({ page }) => {
    const query = TEST_QUERIES[0];
    
    // Enter query
    await page.fill('textarea[id="query"]', query);
    
    // Submit form
    await page.click('.submit-button');
    
    // Check loading state
    await expect(page.locator('.submit-button')).toContainText('Researching...');
    await expect(page.locator('.loading-spinner')).toBeVisible();
    await expect(page.locator('.submit-button')).toBeDisabled();
    
    // Form should be disabled during loading
    await expect(page.locator('textarea[id="query"]')).toBeDisabled();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error by intercepting the request
    await page.route('**/research', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      });
    });
    
    const query = TEST_QUERIES[0];
    
    // Enter query and submit
    await page.fill('textarea[id="query"]', query);
    await page.click('.submit-button');
    
    // Wait for error to appear
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toContainText('Internal server error');
    
    // Form should be re-enabled after error
    await expect(page.locator('.submit-button')).not.toBeDisabled();
    await expect(page.locator('textarea[id="query"]')).not.toBeDisabled();
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that header is still visible
    await expect(page.locator('.header h1')).toBeVisible();
    
    // Check that form is still usable
    await expect(page.locator('textarea[id="query"]')).toBeVisible();
    await expect(page.locator('.submit-button')).toBeVisible();
    
    // Test a simple query on mobile
    const query = 'What is artificial intelligence?';
    await page.fill('textarea[id="query"]', query);
    await page.click('.submit-button');
    
    // Wait for results
    await waitForResearchComplete(page);
    
    // Check that results are displayed properly on mobile
    await expect(page.locator('.research-results')).toBeVisible();
    await expect(page.locator('.final-answer')).toBeVisible();
  });

  test('should allow multiple research queries in sequence', async ({ page }) => {
    for (let i = 0; i < 2; i++) {
      const query = TEST_QUERIES[i];
      
      // Enter query
      await page.fill('textarea[id="query"]', query);
      
      // Submit form
      await page.click('.submit-button');
      
      // Wait for research to complete
      await waitForResearchComplete(page);
      
      // Validate results
      await validateResearchResults(page);
      
      // Clear form for next iteration
      await page.fill('textarea[id="query"]', '');
    }
  });

  test('should display proper styling and colors', async ({ page }) => {
    // Check that Aistra color palette is applied
    const header = page.locator('.header');
    const submitButton = page.locator('.submit-button');
    
    // Check header background gradient
    await expect(header).toHaveCSS('background', /linear-gradient/);
    
    // Check submit button styling
    await expect(submitButton).toHaveCSS('background', /linear-gradient/);
    
    // Check that Roboto Flex font is loaded
    const body = page.locator('body');
    await expect(body).toHaveCSS('font-family', /Roboto Flex/);
  });

  test('should handle network timeout gracefully', async ({ page }) => {
    // Mock slow API response
    await page.route('**/research', route => {
      // Delay response to simulate timeout
      setTimeout(() => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            query: 'test',
            search_terms: ['test'],
            sources_count: 1,
            final_answer: 'Test answer',
            sources: ['https://example.com']
          })
        });
      }, 10000); // 10 second delay
    });
    
    const query = TEST_QUERIES[0];
    
    // Enter query and submit
    await page.fill('textarea[id="query"]', query);
    await page.click('.submit-button');
    
    // Should show loading state
    await expect(page.locator('.loading-spinner')).toBeVisible();
    
    // Wait for response (this will timeout in real scenario)
    // In a real test, you might want to set a shorter timeout
    await page.waitForTimeout(5000);
  });
});
