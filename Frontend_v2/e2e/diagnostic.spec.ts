import { test, expect } from '@playwright/test';

/**
 * Diagnostic Test - Check if UI is actually rendering
 */

test.describe('Diagnostic - UI Health Check', () => {
  
  test('Check if page loads and app renders', async ({ page }) => {
    console.log('\n🔍 Starting diagnostic test...\n');
    
    // Listen for console errors
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
        console.log('❌ Console Error:', msg.text());
      }
    });
    
    // Listen for page errors
    const pageErrors: Error[] = [];
    page.on('pageerror', error => {
      pageErrors.push(error);
      console.log('❌ Page Error:', error.message);
    });
    
    // Go to page
    console.log('📍 Navigating to http://localhost:5175/');
    await page.goto('http://localhost:5175/', { waitUntil: 'networkidle' });
    
    // Wait a bit for React to render
    await page.waitForTimeout(3000);
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/diagnostic-screenshot.png', fullPage: true });
    console.log('📸 Screenshot saved to test-results/diagnostic-screenshot.png');
    
    // Check HTML content
    const htmlContent = await page.content();
    console.log('\n📄 Page HTML length:', htmlContent.length);
    
    // Check if root div has content
    const rootElement = await page.locator('#root').innerHTML();
    console.log('📦 Root element HTML length:', rootElement.length);
    console.log('📦 Root element preview:', rootElement.substring(0, 200));
    
    // Check if specific elements exist
    const checks = [
      { selector: '#root', name: 'Root div' },
      { selector: 'header', name: 'Header' },
      { selector: '.header', name: 'Header with class' },
      { selector: '.main-layout', name: 'Main layout' },
      { selector: 'h1', name: 'Any H1' },
      { selector: '*', name: 'Any element' },
    ];
    
    console.log('\n🔍 Element checks:');
    for (const check of checks) {
      const count = await page.locator(check.selector).count();
      const exists = count > 0;
      console.log(`  ${exists ? '✅' : '❌'} ${check.name} (${check.selector}): ${count} found`);
    }
    
    // Check for specific text
    const textChecks = [
      'Political Analyst Workbench',
      'Welcome',
      'Chat',
      'Connected',
      'Disconnected',
    ];
    
    console.log('\n📝 Text content checks:');
    for (const text of textChecks) {
      const exists = await page.getByText(text, { exact: false }).count() > 0;
      console.log(`  ${exists ? '✅' : '❌'} "${text}"`);
    }
    
    // Report errors
    console.log('\n🐛 Error Summary:');
    console.log(`  Console Errors: ${consoleErrors.length}`);
    console.log(`  Page Errors: ${pageErrors.length}`);
    
    if (consoleErrors.length > 0) {
      console.log('\n❌ Console Errors:');
      consoleErrors.forEach(err => console.log(`  - ${err}`));
    }
    
    if (pageErrors.length > 0) {
      console.log('\n❌ Page Errors:');
      pageErrors.forEach(err => console.log(`  - ${err.message}\n    ${err.stack}`));
    }
    
    // Final verdict
    const hasContent = rootElement.length > 100;
    const hasNoErrors = consoleErrors.length === 0 && pageErrors.length === 0;
    
    console.log('\n📊 Final Verdict:');
    console.log(`  Root has content: ${hasContent ? '✅' : '❌'}`);
    console.log(`  No errors: ${hasNoErrors ? '✅' : '❌'}`);
    
    if (!hasContent) {
      console.log('\n❌ PROBLEM: App is not rendering!');
      console.log('   Root div is empty or very small');
    }
    
    if (!hasNoErrors) {
      console.log('\n❌ PROBLEM: Errors detected!');
      console.log('   Check console/page errors above');
    }
    
    // Assert conditions
    expect(hasContent, 'Root element should have content').toBeTruthy();
    
    console.log('\n✅ Diagnostic test complete!\n');
  });
});

