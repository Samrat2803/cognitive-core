import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for local MVP UI testing
 * Tests the frontend at localhost:3000 with backend at localhost:8000
 */
export default defineConfig({
  testDir: '../tests',
  testMatch: ['**/mvp-ui-integration.spec.ts'],
  
  /* Run tests in files in parallel */
  fullyParallel: false, // Sequential for integration tests
  
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 1,
  
  /* Opt out of parallel tests for integration */
  workers: 1,
  
  /* Reporter to use */
  reporter: [
    ['html', { outputFolder: '../playwright-report' }],
    ['json', { outputFile: '../test-results/mvp-integration-results.json' }],
    ['list']
  ],
  
  /* Shared settings for all projects */
  use: {
    /* Base URL for local development */
    baseURL: 'http://localhost:3000',
    
    /* Collect trace when retrying failed tests */
    trace: 'on-first-retry',
    
    /* Take screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Record video on failure */
    video: 'retain-on-failure',
    
    /* Global timeout for actions */
    actionTimeout: 30000,
    
    /* Global timeout for navigation */
    navigationTimeout: 30000,
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium-local',
      use: { 
        ...devices['Desktop Chrome'],
        // Additional Chrome flags for local testing
        launchOptions: {
          args: ['--disable-web-security', '--disable-features=VizDisplayCompositor']
        }
      },
    },
    
    // Uncomment for cross-browser testing
    // {
    //   name: 'firefox-local',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    
    // {
    //   name: 'webkit-local',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  /* Global timeout for entire test suite */
  globalTimeout: 600000, // 10 minutes for full integration suite
  
  /* Timeout per test */
  timeout: 180000, // 3 minutes per test
  
  /* Expect timeout for assertions */
  expect: {
    timeout: 10000, // 10 seconds for expect assertions
  },
});
