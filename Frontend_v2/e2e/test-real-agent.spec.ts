import { test, expect } from '@playwright/test';

test('Real Agent Execution Test - Dual Panel UI', async ({ page }) => {
  console.log('\n' + '='.repeat(80));
  console.log('🧪 TESTING DUAL-PANEL UI WITH REAL AGENT');
  console.log('='.repeat(80));
  
  // Create investigation
  console.log('\n📝 Creating investigation...');
  await page.goto('http://localhost:3002/investigations');
  await page.waitForLoadState('networkidle');
  
  await page.click('button:has-text("New Investigation")');
  await page.waitForSelector('.modal-overlay');
  
  await page.fill('textarea#query', 'Latest AI developments');
  await page.fill('input#title', 'AI News Investigation');
  await page.fill('input#max_iterations', '3');
  
  await page.click('button:has-text("Create Investigation")');
  await page.waitForURL('**/investigations/inv_**');
  
  const invId = page.url().split('/').pop();
  console.log(`✅ Created: ${invId}`);
  
  // Verify dual-panel layout exists
  console.log('\n🔍 Verifying UI layout...');
  await page.waitForSelector('.investigation-graph-panel', { timeout: 5000 });
  await page.waitForSelector('.investigation-evidence-panel', { timeout: 5000 });
  console.log('✅ Both panels rendered');
  
  // Start investigation
  console.log('\n🚀 Starting investigation...');
  const startBtn = page.locator('button:has-text("Start Investigation")');
  await startBtn.click();
  
  // Wait for logs to start streaming
  await page.waitForTimeout(8000);
  
  const logCount = await page.locator('.log-entry').count();
  console.log(`📊 Logs streaming: ${logCount} entries`);
  
  // Verify left panel has question tree area
  const questionTree = await page.locator('.question-tree').count();
  console.log(`🗺️ Question tree area: ${questionTree > 0 ? 'Present' : 'Missing'}`);
  
  // Verify right panel tabs
  const logTab = await page.locator('button.evidence-tab:has-text("Logs")').count();
  const articleTab = await page.locator('button.evidence-tab:has-text("Article")').count();
  const evidenceTab = await page.locator('button.evidence-tab:has-text("Evidence")').count();
  
  console.log(`📋 Tabs: Logs=${logTab > 0}, Article=${articleTab > 0}, Evidence=${evidenceTab > 0}`);
  
  console.log('\n' + '='.repeat(80));
  console.log('✅ TEST COMPLETE - UI STRUCTURE VERIFIED');
  console.log('📝 Note: Question tree will populate once backend sends graph updates');
  console.log('='.repeat(80));
  
  // Assertions
  expect(logCount).toBeGreaterThan(5);
  expect(questionTree).toBeGreaterThan(0);
  expect(logTab + articleTab + evidenceTab).toBe(3);
});
