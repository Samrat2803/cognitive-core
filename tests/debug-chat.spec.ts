import { test, expect } from '@playwright/test';

test('Debug Chat Page Loading', async ({ page }) => {
  console.log('🔍 Debugging chat page loading...');
  
  // Navigate directly to chat
  await page.goto('http://localhost:3000/chat');
  
  // Take a screenshot for debugging
  await page.screenshot({ path: 'debug-chat-page.png', fullPage: true });
  
  // Log all text content on the page
  const bodyText = await page.locator('body').textContent();
  console.log('📄 Page content:', bodyText);
  
  // Check if there are any error messages
  const errorElements = await page.locator('[class*="error"], [class*="Error"]').all();
  for (const error of errorElements) {
    const errorText = await error.textContent();
    console.log('❌ Error found:', errorText);
  }
  
  // Check what's actually rendered
  const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
  console.log('📋 Headings found:');
  for (const heading of headings) {
    const text = await heading.textContent();
    console.log(`  - ${text}`);
  }
  
  // Check if React app is loaded
  const reactRoot = await page.locator('#root').textContent();
  console.log('⚛️ React root content length:', reactRoot?.length || 0);
});
