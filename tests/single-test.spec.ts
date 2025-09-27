import { test, expect } from '@playwright/test';

test('Complete end-to-end research query', async ({ page }) => {
  console.log('🚀 Starting end-to-end test...');
  
  // Step 1: Navigate to the app
  console.log('📱 Navigating to the app...');
  await page.goto('/');
  
  // Step 2: Verify page loads
  console.log('✅ Checking page elements...');
  await expect(page.locator('.header')).toBeVisible();
  await expect(page.locator('.research-form')).toBeVisible();
  await expect(page.locator('textarea[id="query"]')).toBeVisible();
  await expect(page.locator('.submit-button')).toBeVisible();
  
  // Step 3: Enter a simple query
  const query = 'What is artificial intelligence?';
  console.log(`🔍 Entering query: "${query}"`);
  await page.fill('textarea[id="query"]', query);
  
  // Step 4: Submit the form
  console.log('📤 Submitting the form...');
  await page.click('.submit-button');
  
  // Step 5: Wait for loading state
  console.log('⏳ Waiting for loading state...');
  await expect(page.locator('.submit-button')).toContainText('Researching...');
  await expect(page.locator('.loading-spinner')).toBeVisible();
  
  // Step 6: Wait for results (with generous timeout)
  console.log('⏳ Waiting for research results...');
  try {
    await page.waitForSelector('.research-results', { timeout: 120000 }); // 2 minutes
    
    // Step 7: Verify results are displayed
    console.log('✅ Checking research results...');
    await expect(page.locator('.research-results')).toBeVisible();
    
    // Check that we have search terms
    const searchTerms = page.locator('.term-tag');
    await expect(searchTerms).toHaveCount({ min: 1 });
    console.log('✅ Search terms found');
    
    // Check that we have a final answer
    await expect(page.locator('.final-answer')).toBeVisible();
    await expect(page.locator('.answer-content')).toBeVisible();
    console.log('✅ Final answer displayed');
    
    // Check that we have sources
    await expect(page.locator('.sources')).toBeVisible();
    const sources = page.locator('.sources-list a');
    await expect(sources).toHaveCount({ min: 1 });
    console.log('✅ Sources found');
    
    // Get the actual answer text
    const answerText = await page.locator('.answer-content').textContent();
    console.log('📝 Answer preview:', answerText?.substring(0, 100) + '...');
    
    console.log('🎉 End-to-end test completed successfully!');
    
  } catch (error) {
    console.log('❌ Test failed or timed out');
    
    // Check for error messages
    const errorElement = page.locator('.error-message');
    if (await errorElement.isVisible()) {
      const errorText = await errorElement.textContent();
      console.log('🚨 Error message:', errorText);
    }
    
    // Take a screenshot for debugging
    await page.screenshot({ path: 'test-failure.png' });
    console.log('📸 Screenshot saved as test-failure.png');
    
    throw error;
  }
});
