import { test, expect } from '@playwright/test';

test.describe('Complete User Journey - Streaming Chat UI', () => {
  const FRONTEND_URL = 'http://localhost:3000';
  
  test.use({ 
    baseURL: 'http://localhost:3000',
    ignoreHTTPSErrors: true 
  });
  
  test('should complete full user journey: Homepage → Chat → Streaming Analysis → Citations', async ({ page }) => {
    console.log('🚀 Starting complete user journey test...');
    
    // Step 1: Load Homepage
    console.log('📍 Step 1: Loading homepage...');
    await page.goto(FRONTEND_URL, { timeout: 30000 });
    
    // Verify homepage elements
    await expect(page.getByRole('heading', { name: 'Cognitive Core' })).toBeVisible();
    await expect(page.getByText('Political Analyst Workbench')).toBeVisible();
    await expect(page.getByRole('button', { name: '🚀 Start Analysis' })).toBeVisible();
    console.log('✅ Homepage loaded with Cognitive Core branding');
    
    // Step 2: Navigate to Chat via Prompt Chip
    console.log('📍 Step 2: Clicking prompt chip to navigate to chat...');
    const promptChip = page.getByText('Analyze Hamas sentiment in US, Iran, and Israel').first();
    await promptChip.click();
    
    // Wait for navigation and verify URL
    await page.waitForURL(/.*\/chat/, { timeout: 10000 });
    console.log('✅ URL changed to /chat');
    
    // Wait for chat page to load and verify elements
    await expect(page.getByText('Cognitive Core Chat')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Streaming geopolitical sentiment analysis')).toBeVisible();
    console.log('✅ Navigated to chat page with pre-filled prompt');
    
    // Step 3: Verify Chat Interface Setup
    console.log('📍 Step 3: Verifying chat interface...');
    
    // Check connection status (mock backend should connect quickly)
    await expect(page.getByText('Connected')).toBeVisible({ timeout: 10000 });
    console.log('✅ WebSocket connected (mock backend)');
    
    // Verify input is pre-filled from prompt chip
    const textarea = page.getByPlaceholder('Ask me to analyze geopolitical sentiment...');
    await expect(textarea).toHaveValue('Analyze Hamas sentiment in US, Iran, and Israel');
    console.log('✅ Input pre-filled from homepage prompt chip');
    
    // Step 4: Send Message and Start Streaming
    console.log('📍 Step 4: Sending message to start streaming analysis...');
    
    // Send the message
    await page.getByRole('button').filter({ hasText: /send/i }).click();
    
    // Verify user message appears
    await expect(page.getByText('Analyze Hamas sentiment in US, Iran, and Israel')).toBeVisible();
    console.log('✅ User message displayed in chat');
    
    // Step 5: Verify Streaming Response
    console.log('📍 Step 5: Waiting for streaming response...');
    
    // Wait for streaming to start (mock backend begins streaming)
    await expect(page.getByText('Based on my analysis')).toBeVisible({ timeout: 15000 });
    console.log('✅ Streaming response started');
    
    // Verify streaming cursor is visible during streaming
    const streamingCursor = page.locator('[style*="animation: blink"]');
    await expect(streamingCursor).toBeVisible({ timeout: 5000 });
    console.log('✅ Streaming cursor animation visible');
    
    // Wait for more content to stream in
    await expect(page.getByText('## Key Findings')).toBeVisible({ timeout: 20000 });
    console.log('✅ Streaming content appearing progressively');
    
    // Step 6: Verify Citations Appear
    console.log('📍 Step 6: Waiting for citations to appear...');
    
    // Wait for streaming to complete and citations to be rendered
    await expect(page.getByText('### United States')).toBeVisible({ timeout: 25000 });
    
    // Check for citation links (should be clickable buttons with [1], [2], etc.)
    const citationLinks = page.locator('button[class*="citation-link"]');
    await expect(citationLinks.first()).toBeVisible({ timeout: 10000 });
    console.log('✅ Citation links rendered in streaming text');
    
    // Step 7: Open Sources Panel
    console.log('📍 Step 7: Opening sources panel via citation click...');
    
    // Click on the first citation
    await citationLinks.first().click();
    
    // Verify sources panel opens
    await expect(page.getByText('Sources (3)')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText('Middle East Political Analysis')).toBeVisible();
    await expect(page.getByText('reuters.com')).toBeVisible();
    console.log('✅ Sources panel opened with citation details');
    
    // Step 8: Verify Citation Details
    console.log('📍 Step 8: Verifying citation details and credibility...');
    
    // Check credibility indicators
    await expect(page.getByText('High')).toBeVisible();
    
    // Check external links
    const externalLink = page.getByRole('link').filter({ hasText: 'Middle East Political Analysis' });
    await expect(externalLink).toHaveAttribute('target', '_blank');
    console.log('✅ Citation credibility and external links working');
    
    // Step 9: Test Sources Panel Interaction
    console.log('📍 Step 9: Testing sources panel interactions...');
    
    // Close sources panel
    await page.getByRole('button', { name: 'Close sources panel' }).click();
    await expect(page.getByText('Sources (3)')).not.toBeVisible();
    console.log('✅ Sources panel closes correctly');
    
    // Reopen via sources button in header
    const sourcesButton = page.getByRole('button').filter({ hasText: /3/ });
    if (await sourcesButton.isVisible()) {
      await sourcesButton.click();
      await expect(page.getByText('Sources (3)')).toBeVisible();
      console.log('✅ Sources panel reopens via header button');
    }
    
    // Step 10: Verify Complete Analysis
    console.log('📍 Step 10: Verifying complete analysis content...');
    
    // Check that all sections are present
    await expect(page.getByText('### Iran')).toBeVisible();
    await expect(page.getByText('### Israel')).toBeVisible();
    await expect(page.getByText('## Methodology')).toBeVisible();
    console.log('✅ Complete analysis with all sections rendered');
    
    // Step 11: Test Keyboard Shortcuts
    console.log('📍 Step 11: Testing keyboard shortcuts...');
    
    // Close sources panel if open
    const closeButton = page.getByRole('button', { name: 'Close sources panel' });
    if (await closeButton.isVisible()) {
      await closeButton.click();
    }
    
    // Test new message input
    await textarea.fill('Test Shift+Enter for newline');
    await textarea.press('Shift+Enter');
    await textarea.type('Second line');
    
    const value = await textarea.inputValue();
    expect(value).toContain('\n');
    console.log('✅ Shift+Enter creates newline');
    
    // Clear and test Enter to send
    await textarea.fill('Quick follow-up question');
    await textarea.press('Enter');
    
    // Should send message and clear input
    await expect(page.getByText('Quick follow-up question')).toBeVisible();
    await expect(textarea).toHaveValue('');
    console.log('✅ Enter sends message and clears input');
    
    // Step 12: Verify Mobile Responsiveness
    console.log('📍 Step 12: Testing mobile responsiveness...');
    
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Interface should still be usable
    await expect(page.getByText('Cognitive Core Chat')).toBeVisible();
    await expect(textarea).toBeVisible();
    
    // Sources panel should take full width on mobile
    await citationLinks.first().click();
    await expect(page.getByText('Sources (3)')).toBeVisible();
    console.log('✅ Mobile responsive design working');
    
    // Final Step: Journey Complete
    console.log('📍 ✅ COMPLETE: Full user journey successful!');
    console.log('🎉 User successfully:');
    console.log('   • Loaded homepage with Cognitive Core branding');
    console.log('   • Navigated to chat via prompt chip');
    console.log('   • Sent message and received streaming response');
    console.log('   • Interacted with citations and sources panel');
    console.log('   • Used keyboard shortcuts effectively');
    console.log('   • Experienced responsive mobile design');
    
    // Reset viewport for cleanup
    await page.setViewportSize({ width: 1200, height: 800 });
  });
});
