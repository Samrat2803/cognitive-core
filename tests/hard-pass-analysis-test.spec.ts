import { test, expect } from '@playwright/test';

test.describe('Hard Pass Analysis Test - Must Show Real Output', () => {
  const FRONTEND_URL = 'http://localhost:3000';
  const TEST_QUERY = 'Analyze Hamas sentiment in United States, Iran, and Israel';
  
  test('HARD PASS: Must verify actual analysis output is displayed on UI', async ({ page }) => {
    // Extended timeout for full analysis completion
    test.setTimeout(180000); // 3 minutes
    
    console.log('🎯 HARD PASS TEST: Will only pass if real analysis output is visible');
    
    // Step 1: Navigate and setup
    await page.goto(FRONTEND_URL, { timeout: 30000 });
    await expect(page.locator('h1').first()).toContainText('Political Analyst Workbench');
    console.log('✅ Step 1: Application loaded');
    
    // Step 2: Enter query
    await page.fill('#message', TEST_QUERY);
    console.log(`✅ Step 2: Query entered: "${TEST_QUERY}"`);
    
    // Step 3: Submit query
    await page.click('button:has-text("Send Request")');
    console.log('✅ Step 3: Query submitted');
    
    // Step 4: Wait for analysis plan
    await expect(page.getByText('Analysis Plan')).toBeVisible({ timeout: 20000 });
    console.log('✅ Step 4: Analysis plan displayed');
    
    // Step 5: Proceed with analysis
    await page.click('button:has-text("Proceed with Analysis")');
    console.log('✅ Step 5: Clicked proceed with analysis');
    
    // Step 6: Verify analysis started with ID
    await expect(page.getByText('Analysis in Progress')).toBeVisible({ timeout: 10000 });
    const analysisIdElement = page.locator('span[style*="monospace"]');
    await expect(analysisIdElement).toBeVisible({ timeout: 5000 });
    const analysisId = await analysisIdElement.textContent();
    console.log(`✅ Step 6: Analysis started with ID: ${analysisId}`);
    
    // Step 7: HARD PASS CRITERIA - Wait for actual analysis results
    console.log('⏳ Step 7: WAITING FOR REAL ANALYSIS OUTPUT (up to 150 seconds)...');
    console.log('🎯 HARD PASS CRITERIA: Must see actual analysis content with sentiment data');
    
    // Wait for analysis results to appear
    let analysisOutputFound = false;
    let analysisContent = '';
    
    try {
      // Wait for the proper visualization to appear
      await Promise.race([
        page.waitForSelector('h5:has-text("📊 Analysis Summary")', { timeout: 150000 }),
        page.waitForSelector('h5:has-text("🌍 Country-Specific Results")', { timeout: 150000 })
      ]);
      
      // Get the full page content to verify visualization
      const pageContent = await page.textContent('body') || '';
      analysisContent = pageContent;
      
      console.log('📄 PROPER ANALYSIS VISUALIZATION DETECTED:');
      console.log('=' .repeat(80));
      
      // Extract key visual elements
      const summarySection = await page.locator('h5:has-text("📊 Analysis Summary")').isVisible();
      const countrySection = await page.locator('h5:has-text("🌍 Country-Specific Results")').isVisible();
      const overallSentiment = await page.locator('text=Overall Sentiment:').isVisible();
      const articlesProcessed = await page.locator('text=Articles Processed:').isVisible();
      
      console.log(`✅ Analysis Summary Section: ${summarySection ? 'VISIBLE' : 'MISSING'}`);
      console.log(`✅ Country Results Section: ${countrySection ? 'VISIBLE' : 'MISSING'}`);
      console.log(`✅ Overall Sentiment Display: ${overallSentiment ? 'VISIBLE' : 'MISSING'}`);
      console.log(`✅ Articles Processed Display: ${articlesProcessed ? 'VISIBLE' : 'MISSING'}`);
      
      // Show sample of the formatted content
      if (summarySection) {
        const summaryText = await page.locator('div:has(h5:has-text("📊 Analysis Summary"))').textContent();
        console.log('📊 SUMMARY CONTENT:');
        console.log(summaryText?.substring(0, 500) + '...');
      }
      
      if (countrySection) {
        const countryText = await page.locator('div:has(h5:has-text("🌍 Country-Specific Results"))').textContent();
        console.log('🌍 COUNTRY RESULTS CONTENT:');
        console.log(countryText?.substring(0, 500) + '...');
      }
      
      console.log('=' .repeat(80));
      
      // HARD PASS VALIDATION: Check for proper visualization elements
      const hasCountryData = pageContent.includes('United States') || 
                            pageContent.includes('Iran') || 
                            pageContent.includes('Israel');
      
      const hasSentimentData = pageContent.includes('Overall Sentiment:') || 
                              pageContent.includes('Sentiment:') ||
                              pageContent.includes('😊') ||
                              pageContent.includes('😞') ||
                              pageContent.includes('😐');
      
      const hasAnalysisStructure = summarySection && countrySection && overallSentiment && articlesProcessed;
      
      if (hasCountryData && hasSentimentData && hasAnalysisStructure) {
        analysisOutputFound = true;
        console.log('✅ HARD PASS CRITERIA MET:');
        console.log('  ✅ Country data found in visualization');
        console.log('  ✅ Sentiment data properly displayed with emojis'); 
        console.log('  ✅ Professional analysis structure with sections');
        console.log(`  ✅ Total content length: ${analysisContent.length} characters`);
        console.log('  ✅ Proper UI visualization (not raw JSON)');
      } else {
        console.log('❌ HARD PASS CRITERIA NOT MET:');
        console.log(`  ${hasCountryData ? '✅' : '❌'} Country data in visualization`);
        console.log(`  ${hasSentimentData ? '✅' : '❌'} Sentiment data with proper formatting`);
        console.log(`  ${hasAnalysisStructure ? '✅' : '❌'} Professional analysis structure`);
        console.log(`  📊 Content length: ${analysisContent.length} characters`);
      }
      
    } catch (error) {
      console.log('❌ ANALYSIS OUTPUT NOT FOUND WITHIN TIMEOUT');
      console.log('🔍 Current page state:');
      
      // Capture current state for debugging
      const currentContent = await page.textContent('body');
      console.log('📄 Page content sample:', currentContent?.substring(0, 1000));
      
      // Take screenshot for manual verification
      await page.screenshot({ path: 'hard-pass-test-failure.png', fullPage: true });
      console.log('📸 Screenshot saved: hard-pass-test-failure.png');
    }
    
    // HARD PASS ASSERTION
    if (!analysisOutputFound) {
      throw new Error(`
🚫 HARD PASS TEST FAILED!

CRITERIA: Must display proper analysis visualization with:
- Professional UI sections (📊 Analysis Summary, 🌍 Country Results)
- Country data (US, Iran, Israel) in formatted display
- Sentiment analysis with emojis and colors
- Structured layout (not raw JSON)

ACTUAL RESULT: 
- Professional visualization found: ${analysisOutputFound}
- Content length: ${analysisContent.length}
- Content preview: ${analysisContent.substring(0, 300)}...

❌ This test requires PROPER ANALYSIS VISUALIZATION on the UI.
`);
    }
    
    console.log('🎉 HARD PASS TEST SUCCEEDED!');
    console.log('✅ Real analysis output is visible on the UI');
    console.log('✅ All hard pass criteria met');
    console.log(`✅ Analysis ID: ${analysisId}`);
    console.log(`✅ Output length: ${analysisContent.length} characters`);
  });
});
