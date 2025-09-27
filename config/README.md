# Configuration Directory

This directory contains configuration files for testing and build tools:

- `playwright.config.ts` - Main Playwright configuration
- `playwright-headed.config.ts` - Playwright config for headed browser tests
- `playwright-sequential.config.ts` - Playwright config for sequential tests

## Usage

These config files are referenced by test scripts and package.json scripts:
```bash
npx playwright test --config=config/playwright.config.ts
```
