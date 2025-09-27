import { defineConfig, devices } from '@playwright/test';

/**
 * Sequential testing configuration - one browser, one test at a time
 */
export default defineConfig({
  testDir: './tests',
  testMatch: ['**/*@(spec|test).ts'],
  testIgnore: ['**/node_modules/**', '**/frontend/**'],
  /* Run tests sequentially */
  fullyParallel: false,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* No retries for sequential testing */
  retries: 0,
  /* Single worker - one browser only */
  workers: 1,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['list'], // Simple list reporter
    ['html'],
  ],
  /* Shared settings for all the projects below. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:3000',

    /* Collect trace when retrying the failed test. */
    trace: 'on-first-retry',
    
    /* Take screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Record video on failure */
    video: 'retain-on-failure',
    
    /* Slower actions for better visibility */
    actionTimeout: 30000,
    navigationTimeout: 30000,
  },

  /* Only Chromium for sequential testing */
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Keep browser open between tests for better visibility
        launchOptions: {
          headless: false,
          slowMo: 1000, // Slow down actions by 1 second
        }
      },
    },
  ],

  /* No webServer - servers should be running manually */
  /* Global timeout for the entire test run */
  timeout: 300000, // 5 minutes per test
});
