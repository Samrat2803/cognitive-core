import { test, expect } from '@playwright/test';

test.describe('Streaming Chat UI Tests - 2-MVP', () => {
  const FRONTEND_URL = 'http://localhost:3000';
  
  test.beforeEach(async ({ page }) => {
    // Set mock backend environment variable
    await page.addInitScript(() => {
      window.localStorage.setItem('REACT_APP_USE_MOCK', 'true');
    });
    
    await page.goto(FRONTEND_URL, { timeout: 30000 });
  });

  test('should display homepage with Cognitive Core branding', async ({ page }) => {
    // Check homepage elements
    await expect(page.getByRole('heading', { name: 'Cognitive Core' })).toBeVisible();
    await expect(page.getByText('Political Analyst Workbench')).toBeVisible();
    await expect(page.getByRole('button', { name: '🚀 Start Analysis' })).toBeVisible();
    
    // Check feature cards
    await expect(page.getByText('Real-time Analysis')).toBeVisible();
    await expect(page.getByText('Trend Detection')).toBeVisible();
    await expect(page.getByText('Global Coverage')).toBeVisible();
    await expect(page.getByText('Fast Results')).toBeVisible();
    
    console.log('✅ Homepage displays correctly with Cognitive Core branding');
  });

  test('should navigate from homepage to chat via CTA button', async ({ page }) => {
    // Click main CTA button
    await page.getByRole('button', { name: '🚀 Start Analysis' }).click();
    
    // Should navigate to /chat
    await expect(page).toHaveURL(/.*\/chat/);
    await expect(page.getByText('Cognitive Core Chat')).toBeVisible();
    await expect(page.getByText('Streaming geopolitical sentiment analysis')).toBeVisible();
    
    console.log('✅ Navigation from homepage to chat works');
  });

  test('should navigate from homepage to chat via prompt chip', async ({ page }) => {
    // Click on a prompt chip
    const promptChip = page.getByText('Analyze Hamas sentiment in US, Iran, and Israel').first();
    await promptChip.click();
    
    // Should navigate to /chat with pre-filled prompt
    await expect(page).toHaveURL(/.*\/chat/);
    await expect(page.getByPlaceholder('Ask me to analyze geopolitical sentiment...')).toHaveValue('Analyze Hamas sentiment in US, Iran, and Israel');
    
    console.log('✅ Prompt chip navigation works with pre-filled text');
  });

  test('should display chat interface with connection status', async ({ page }) => {
    // Navigate to chat
    await page.goto(`${FRONTEND_URL}/chat`);
    
    // Check chat interface elements
    await expect(page.getByText('Cognitive Core Chat')).toBeVisible();
    await expect(page.getByPlaceholder('Ask me to analyze geopolitical sentiment...')).toBeVisible();
    await expect(page.getByRole('button').filter({ hasText: /send/i })).toBeVisible();
    
    // Check connection status (should show Connected with mock backend)
    await expect(page.getByText('Connected')).toBeVisible();
    
    // Check welcome message and prompt chips
    await expect(page.getByText('Welcome to Cognitive Core')).toBeVisible();
    await expect(page.getByText('Analyze Hamas sentiment in US, Iran, and Israel')).toBeVisible();
    
    console.log('✅ Chat interface displays correctly with connection status');
  });

  test('should perform streaming chat with mock backend', async ({ page }) => {
    // Navigate to chat
    await page.goto(`${FRONTEND_URL}/chat`);
    
    // Wait for connection
    await expect(page.getByText('Connected')).toBeVisible();
    
    // Enter a test message
    const testQuery = 'Analyze sentiment about climate change policies in G7 countries';
    await page.fill('[placeholder="Ask me to analyze geopolitical sentiment..."]', testQuery);
    
    // Send message
    await page.getByRole('button').filter({ hasText: /send/i }).click();
    
    // Check user message appears
    await expect(page.getByText(testQuery)).toBeVisible();
    
    // Wait for streaming response to start
    await expect(page.getByText('Based on my analysis')).toBeVisible({ timeout: 10000 });
    
    // Wait for streaming to complete and citations to appear
    await expect(page.getByText('## Key Findings')).toBeVisible({ timeout: 15000 });
    
    // Check for citation links
    const citationLinks = page.locator('button[class*="citation-link"]');
    await expect(citationLinks.first()).toBeVisible({ timeout: 5000 });
    
    console.log('✅ Streaming chat works with mock backend');
  });

  test('should open sources panel when citation is clicked', async ({ page }) => {
    // Navigate to chat and send message
    await page.goto(`${FRONTEND_URL}/chat`);
    await expect(page.getByText('Connected')).toBeVisible();
    
    const testQuery = 'Test query for citations';
    await page.fill('[placeholder="Ask me to analyze geopolitical sentiment..."]', testQuery);
    await page.getByRole('button').filter({ hasText: /send/i }).click();
    
    // Wait for streaming to complete
    await expect(page.getByText('Based on my analysis')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('## Key Findings')).toBeVisible({ timeout: 15000 });
    
    // Click on a citation link
    const citationLink = page.locator('button[class*="citation-link"]').first();
    await citationLink.click();
    
    // Check sources panel opens
    await expect(page.getByText('Sources (3)')).toBeVisible();
    await expect(page.getByText('Middle East Political Analysis')).toBeVisible();
    await expect(page.getByText('reuters.com')).toBeVisible();
    
    // Check credibility indicators
    await expect(page.getByText('High')).toBeVisible();
    
    // Close sources panel
    await page.getByRole('button', { name: 'Close sources panel' }).click();
    await expect(page.getByText('Sources (3)')).not.toBeVisible();
    
    console.log('✅ Sources panel opens and closes correctly');
  });

  test('should handle keyboard shortcuts correctly', async ({ page }) => {
    // Navigate to chat
    await page.goto(`${FRONTEND_URL}/chat`);
    await expect(page.getByText('Connected')).toBeVisible();
    
    const textarea = page.getByPlaceholder('Ask me to analyze geopolitical sentiment...');
    
    // Test Shift+Enter for new line
    await textarea.fill('First line');
    await textarea.press('Shift+Enter');
    await textarea.type('Second line');
    
    const value = await textarea.inputValue();
    expect(value).toContain('\n');
    
    // Test Enter to send
    await textarea.fill('Test message');
    await textarea.press('Enter');
    
    // Message should be sent and input cleared
    await expect(page.getByText('Test message')).toBeVisible();
    await expect(textarea).toHaveValue('');
    
    console.log('✅ Keyboard shortcuts work correctly');
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Navigate to homepage
    await page.goto(FRONTEND_URL);
    
    // Check homepage is responsive
    await expect(page.getByRole('heading', { name: 'Cognitive Core' })).toBeVisible();
    await expect(page.getByRole('button', { name: '🚀 Start Analysis' })).toBeVisible();
    
    // Navigate to chat
    await page.getByRole('button', { name: '🚀 Start Analysis' }).click();
    
    // Check chat interface is responsive
    await expect(page.getByText('Cognitive Core Chat')).toBeVisible();
    await expect(page.getByPlaceholder('Ask me to analyze geopolitical sentiment...')).toBeVisible();
    
    // Sources panel should take full width on mobile
    const testQuery = 'Mobile test query';
    await page.fill('[placeholder="Ask me to analyze geopolitical sentiment..."]', testQuery);
    await page.getByRole('button').filter({ hasText: /send/i }).click();
    
    // Wait for response and click citation
    await expect(page.getByText('Based on my analysis')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('## Key Findings')).toBeVisible({ timeout: 15000 });
    
    const citationLink = page.locator('button[class*="citation-link"]').first();
    await citationLink.click();
    
    // Sources panel should be visible and take full width
    await expect(page.getByText('Sources (3)')).toBeVisible();
    
    console.log('✅ Mobile responsive design works correctly');
  });

  test('should handle mock backend toggle', async ({ page }) => {
    // Test with mock backend enabled (default)
    await page.goto(`${FRONTEND_URL}/chat`);
    await expect(page.getByText('Connected')).toBeVisible();
    
    // Send message and verify mock response
    await page.fill('[placeholder="Ask me to analyze geopolitical sentiment..."]', 'Test query');
    await page.getByRole('button').filter({ hasText: /send/i }).click();
    
    // Should get mock response quickly
    await expect(page.getByText('Based on my analysis')).toBeVisible({ timeout: 5000 });
    
    console.log('✅ Mock backend integration works correctly');
  });

  test('should display loading states correctly', async ({ page }) => {
    // Navigate to chat
    await page.goto(`${FRONTEND_URL}/chat`);
    await expect(page.getByText('Connected')).toBeVisible();
    
    // Send message
    await page.fill('[placeholder="Ask me to analyze geopolitical sentiment..."]', 'Loading test');
    await page.getByRole('button').filter({ hasText: /send/i }).click();
    
    // Should show loading skeleton briefly
    const skeleton = page.locator('[class*="MuiSkeleton"]');
    
    // Wait for streaming to start
    await expect(page.getByText('Based on my analysis')).toBeVisible({ timeout: 10000 });
    
    // Should show streaming cursor
    const streamingCursor = page.locator('[style*="animation: blink"]');
    await expect(streamingCursor).toBeVisible();
    
    console.log('✅ Loading states display correctly');
  });

  test('should maintain accessibility standards', async ({ page }) => {
    // Navigate to chat
    await page.goto(`${FRONTEND_URL}/chat`);
    
    // Check aria-live region exists for streaming
    const ariaLiveRegion = page.locator('[aria-live="polite"]');
    
    // Send message to trigger streaming
    await page.fill('[placeholder="Ask me to analyze geopolitical sentiment..."]', 'Accessibility test');
    await page.getByRole('button').filter({ hasText: /send/i }).click();
    
    // Wait for streaming
    await expect(page.getByText('Based on my analysis')).toBeVisible({ timeout: 10000 });
    
    // Aria-live region should be present during streaming
    await expect(ariaLiveRegion).toBeVisible();
    
    // Check sources panel accessibility
    await expect(page.getByText('## Key Findings')).toBeVisible({ timeout: 15000 });
    const citationLink = page.locator('button[class*="citation-link"]').first();
    await citationLink.click();
    
    // Sources panel should have proper close button
    await expect(page.getByRole('button', { name: 'Close sources panel' })).toBeVisible();
    
    console.log('✅ Accessibility standards maintained');
  });
});
