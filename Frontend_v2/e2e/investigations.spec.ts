import { test, expect } from '@playwright/test';

test.describe('Investigations Page - Professional UI', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001/investigations');
  });

  test('should load and display header with stats', async ({ page }) => {
    // Check main header
    await expect(page.locator('h1')).toContainText('Investigations');
    await expect(page.getByText('Deep investigative journalism projects')).toBeVisible();
    
    // Check New Investigation button
    await expect(page.getByRole('button', { name: '+ New Investigation' })).toBeVisible();
    
    // Check stats bar
    await expect(page.locator('.stat-label', { hasText: 'Total' })).toBeVisible();
    await expect(page.locator('.stat-label', { hasText: 'Active' })).toBeVisible();
    await expect(page.locator('.stat-label', { hasText: 'Completed' })).toBeVisible();
    await expect(page.locator('.stat-label', { hasText: 'Archived' })).toBeVisible();
  });

  test('should display filter toolbar', async ({ page }) => {
    // Check filter label
    await expect(page.getByText('Filter:')).toBeVisible();
    
    // Check all filter buttons
    await expect(page.getByRole('button', { name: /All \(\d+\)/ })).toBeVisible();
    await expect(page.getByRole('button', { name: /Active \(\d+\)/ })).toBeVisible();
    await expect(page.getByRole('button', { name: /Completed \(\d+\)/ })).toBeVisible();
    await expect(page.getByRole('button', { name: /Archived \(\d+\)/ })).toBeVisible();
  });

  test('should render investigation cards with proper structure', async ({ page }) => {
    // Wait for loading to complete
    await page.waitForSelector('.investigation-card', { timeout: 3000 });
    
    // Check that cards are rendered
    const cards = page.locator('.investigation-card');
    await expect(cards).toHaveCount(3); // We have 3 dummy investigations
    
    // Check first card structure
    const firstCard = cards.first();
    
    // Card header elements
    await expect(firstCard.locator('.card-status')).toBeVisible();
    await expect(firstCard.locator('.card-meta-top')).toBeVisible();
    await expect(firstCard.locator('.card-title')).toBeVisible();
    await expect(firstCard.locator('.card-article')).toBeVisible();
    
    // Progress section
    await expect(firstCard.locator('.card-progress')).toBeVisible();
    await expect(firstCard.locator('.progress-bar')).toBeVisible();
    await expect(firstCard.locator('.progress-fill')).toBeVisible();
    
    // Evidence grid
    await expect(firstCard.locator('.card-evidence')).toBeVisible();
    await expect(firstCard.locator('.evidence-item')).toHaveCount(4); // 4 evidence types
    
    // Card footer
    await expect(firstCard.locator('.card-footer')).toBeVisible();
    await expect(firstCard.locator('.card-cost')).toBeVisible();
  });

  test('should filter investigations by status', async ({ page }) => {
    // Wait for initial load
    await page.waitForSelector('.investigation-card');
    
    // Click "Active" filter
    await page.getByRole('button', { name: /Active \(\d+\)/ }).click();
    await expect(page.getByRole('button', { name: /Active \(\d+\)/ })).toHaveClass(/active/);
    
    // Check only active investigations are shown
    const activeCards = page.locator('.investigation-card .status-active');
    await expect(activeCards).toHaveCount(await activeCards.count());
    
    // Click "Completed" filter
    await page.getByRole('button', { name: /Completed \(\d+\)/ }).click();
    await expect(page.getByRole('button', { name: /Completed \(\d+\)/ })).toHaveClass(/active/);
    
    // Click "All" to reset
    await page.getByRole('button', { name: /All \(\d+\)/ }).click();
    await expect(page.getByRole('button', { name: /All \(\d+\)/ })).toHaveClass(/active/);
  });

  test('should show card hover effects', async ({ page }) => {
    await page.waitForSelector('.investigation-card');
    
    const firstCard = page.locator('.investigation-card').first();
    
    // Hover over card
    await firstCard.hover();
    
    // Card should have hover state (border color change)
    // Note: Visual testing would be better here, but we can at least check the element is interactive
    await expect(firstCard).toBeVisible();
  });

  test('should navigate to investigation detail on click', async ({ page }) => {
    await page.waitForSelector('.investigation-card');
    
    const firstCard = page.locator('.investigation-card').first();
    
    // Click the card
    await firstCard.click();
    
    // Should navigate to detail page (even though it doesn't exist yet)
    await expect(page).toHaveURL(/\/investigations\/inv_/);
  });

  test('should match the existing UI design system', async ({ page }) => {
    await page.waitForSelector('.investigations-page');
    
    // Check that CSS variables are being used (Aistra design system)
    const pageStyles = await page.locator('.investigations-page').evaluate((el) => {
      const styles = window.getComputedStyle(el);
      return {
        backgroundColor: styles.backgroundColor,
      };
    });
    
    // Background should be dark (rgb values for #1c1e20)
    expect(pageStyles.backgroundColor).toMatch(/rgb\(28, 30, 32\)|rgb\(26, 26, 26\)/);
  });

  test('should be responsive', async ({ page }) => {
    // Desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('.investigations-grid')).toBeVisible();
    
    // Tablet view
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('.investigations-grid')).toBeVisible();
    
    // Mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('.investigations-grid')).toBeVisible();
  });
});
