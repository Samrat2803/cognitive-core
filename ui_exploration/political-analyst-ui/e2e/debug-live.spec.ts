import { test, expect } from '@playwright/test';

test('Debug: Watch live interaction', async ({ page }) => {
  console.log('\n🔍 Starting live debug test...\n');
  
  // Go to page
  await page.goto('http://localhost:5175/');
  console.log('✅ Page loaded');
  
  // Wait for connected
  await page.waitForSelector('text=Connected', { timeout: 10000 });
  console.log('✅ WebSocket connected');
  
  // Click first suggestion
  const suggestion = page.locator('.suggestion-card').first();
  await suggestion.click();
  console.log('✅ Clicked suggestion');
  
  // Wait for user message
  await page.waitForSelector('.user-message', { timeout: 5000 });
  console.log('✅ User message appeared');
  
  // Wait for thinking indicator
  const thinking = page.locator('.thinking-indicator');
  if (await thinking.isVisible()) {
    console.log('✅ Thinking indicator visible');
  }
  
  // Listen for console messages
  page.on('console', msg => {
    if (msg.text().includes('WebSocket') || msg.text().includes('message')) {
      console.log('🌐 Browser console:', msg.text());
    }
  });
  
  // Wait up to 60 seconds for response
  console.log('⏳ Waiting for AI response (up to 60s)...');
  
  try {
    await page.waitForSelector('.assistant-message', { timeout: 60000 });
    console.log('✅ Assistant message appeared!');
    
    const content = await page.locator('.assistant-message .message-text').first().textContent();
    console.log('📝 Response preview:', content?.substring(0, 100));
    
  } catch (error) {
    console.log('❌ No assistant message after 60s');
    
    // Check if thinking indicator still visible
    if (await thinking.isVisible()) {
      console.log('⚠️ Thinking indicator still showing - backend might be stuck');
    }
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/debug-timeout.png' });
    console.log('📸 Screenshot saved');
    
    throw error;
  }
  
  // Keep browser open for 5 seconds so you can see
  console.log('\n⏸️ Pausing 5 seconds so you can see the result...\n');
  await page.waitForTimeout(5000);
});

