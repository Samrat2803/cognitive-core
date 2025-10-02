import { test, expect } from '@playwright/test';

test.use({ 
  baseURL: 'http://localhost:3000'
});

test('Simple Chat Page Test', async ({ page }) => {
  console.log('🧪 Testing direct navigation to chat page...');
  
  // Listen for console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('🚨 Console error:', msg.text());
    }
  });
  
  // Listen for page errors
  page.on('pageerror', error => {
    console.log('💥 Page error:', error.message);
  });
  
  // Navigate directly to chat
  await page.goto('/chat');
  
  // Wait for page to load
  await page.waitForLoadState('networkidle');
  
  // Take screenshot for debugging
  await page.screenshot({ path: 'simple-chat-test.png', fullPage: true });
  
  // Check if we can find any text that should be on the chat page
  const pageContent = await page.textContent('body');
  console.log('📄 Page content preview:', pageContent?.substring(0, 200));
  
  // Try to find the chat interface elements with more flexible selectors
  const chatElements = [
    'Cognitive Core',
    'Chat', 
    'geopolitical',
    'sentiment',
    'analysis'
  ];
  
  for (const element of chatElements) {
    const found = await page.getByText(element, { timeout: 1000 }).isVisible().catch(() => false);
    console.log(`🔍 "${element}": ${found ? '✅ Found' : '❌ Not found'}`);
  }
  
  // Check if React is working
  const reactRoot = await page.locator('#root').innerHTML();
  console.log('⚛️ React root has content:', reactRoot.length > 100);
  
  // Try alternative selectors
  const h4Elements = await page.locator('h4').all();
  console.log('📋 H4 elements found:', h4Elements.length);
  for (const h4 of h4Elements) {
    const text = await h4.textContent();
    console.log(`  - H4: "${text}"`);
  }
});
