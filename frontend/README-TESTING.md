# Frontend Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the Political Analyst Workbench frontend application.

## Testing Stack

- **Test Runner**: Vitest (faster than Jest, better Vite integration)
- **Testing Library**: React Testing Library (component testing)
- **Mocking**: Vitest built-in mocking
- **Coverage**: V8 coverage provider
- **Environment**: jsdom (browser simulation)

## Test Structure

```
src/
├── __tests__/
│   ├── api/
│   │   ├── client.test.ts          # API client unit tests
│   │   └── mocks.test.ts           # Mock service tests
│   ├── services/
│   │   └── websocket.test.ts       # WebSocket service tests
│   ├── pages/
│   │   ├── Chat.test.tsx           # Chat page component tests
│   │   ├── AnalysisResults.test.tsx # Analysis results tests
│   │   └── History.test.tsx        # History page tests
│   ├── components/
│   │   ├── ResearchForm.test.tsx   # Form component tests
│   │   └── ExportButton.test.tsx   # Export functionality tests
│   └── integration/
│       └── e2e-flow.test.tsx       # End-to-end flow tests
├── setupTests.ts                   # Test environment setup
└── vitest.config.ts               # Vitest configuration
```

## Test Categories

### 1. Unit Tests

**API Client Tests** (`__tests__/api/client.test.ts`)
- Test all API service functions
- Mock API responses and error handling
- Verify correct request parameters
- Test mock/real API switching

**WebSocket Service Tests** (`__tests__/services/websocket.test.ts`)
- Connection management and reconnection logic
- Message sending and receiving
- Ping/pong heartbeat functionality
- Event listener management
- Error handling and cleanup

**Mock Service Tests** (`__tests__/api/mocks.test.ts`)
- Verify mock responses match API contracts
- Test progression simulation (analysis completion)
- Validate data consistency across mock calls

### 2. Component Tests

**Chat Page Tests** (`__tests__/pages/Chat.test.tsx`)
- Message input and validation
- Chat flow: message → parsed intent → confirmation
- Analysis confirmation and cancellation
- Error states and recovery
- Suggestion handling

**Analysis Results Tests** (`__tests__/pages/AnalysisResults.test.tsx`)
- Direct analysis execution
- Progress display and WebSocket integration
- Results rendering (summary, country details, bias analysis)
- Polling behavior and status updates
- Error handling

**History Page Tests** (`__tests__/pages/History.test.tsx`)
- Analysis list rendering and pagination
- Status badges and formatting
- Navigation and filtering
- Empty states

**Form Components Tests**
- Input validation and submission
- Loading states and disabled states
- Error display and recovery

### 3. Integration Tests

**End-to-End Flow Tests** (`__tests__/integration/e2e-flow.test.tsx`)
- Complete chat → confirmation → analysis flow
- Navigation between different sections
- Direct analysis execution and monitoring
- History integration and data consistency
- Error handling across the entire application
- Legacy research compatibility

## Running Tests

### Basic Commands

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with UI (browser interface)
npm run test:ui

# Generate coverage report
npm run test:coverage

# Run specific test file
npm test Chat.test.tsx

# Run tests matching pattern
npm test -- --grep "WebSocket"
```

### Test Configuration

**Environment Variables for Testing:**
```bash
# Use mocks in tests
REACT_APP_USE_MOCKS=true

# Test API URLs
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

## Test Patterns and Best Practices

### 1. Component Testing Pattern

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false }
  }
});

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};
```

### 2. API Mocking Pattern

```typescript
vi.mock('../../api/client', () => ({
  apiChatMessage: vi.fn(),
  apiConfirmAnalysis: vi.fn(),
  // ... other API functions
}));

// In test
const { apiChatMessage } = await import('../../api/client');
(apiChatMessage as any).mockResolvedValue({
  success: true,
  response_type: 'query_parsed',
  // ... response data
});
```

### 3. WebSocket Testing Pattern

```typescript
// Mock WebSocket globally
global.WebSocket = MockWebSocket as any;

// Test WebSocket interactions
wsService.connect('test-session');
await vi.advanceTimersByTimeAsync(20); // Fast-forward timers
```

### 4. Async Testing Pattern

```typescript
// Wait for API calls and state updates
await waitFor(() => {
  expect(screen.getByText('Expected Result')).toBeInTheDocument();
});

// Test loading states
expect(screen.getByText(/loading/i)).toBeInTheDocument();
```

## Coverage Goals

- **Statements**: > 90%
- **Branches**: > 85%
- **Functions**: > 90%
- **Lines**: > 90%

### Coverage Exclusions

- Configuration files
- Test setup files
- Type definitions
- Build artifacts
- Mock files (except for their own tests)

## Continuous Integration

### GitHub Actions Example

```yaml
name: Frontend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:coverage
      - uses: codecov/codecov-action@v3
```

## Testing Checklist

### Before Committing
- [ ] All tests pass
- [ ] Coverage meets minimum thresholds
- [ ] No console errors in test output
- [ ] New features have corresponding tests
- [ ] Edge cases are covered

### Test Quality Checks
- [ ] Tests are isolated (no shared state)
- [ ] Mocks are properly cleaned up
- [ ] Async operations are properly awaited
- [ ] Error scenarios are tested
- [ ] User interactions are realistic

## Debugging Tests

### Common Issues

1. **Timer-related tests failing**
   ```typescript
   // Use fake timers
   vi.useFakeTimers();
   await vi.advanceTimersByTimeAsync(1000);
   vi.useRealTimers();
   ```

2. **WebSocket tests not working**
   ```typescript
   // Ensure WebSocket mock is properly set up
   global.WebSocket = MockWebSocket as any;
   ```

3. **React Query tests failing**
   ```typescript
   // Disable retries in test client
   const queryClient = new QueryClient({
     defaultOptions: { queries: { retry: false } }
   });
   ```

### Debug Commands

```bash
# Run tests with debug output
npm test -- --reporter=verbose

# Run single test with full output
npm test Chat.test.tsx -- --reporter=verbose

# Debug specific test case
npm test -- --grep "should send chat message"
```

## Performance Testing

### Load Testing Components
- Test with large datasets (100+ history items)
- Simulate slow API responses
- Test WebSocket message flooding
- Memory leak detection in long-running tests

### Example Performance Test
```typescript
it('should handle large analysis history efficiently', async () => {
  const largeHistory = Array.from({ length: 1000 }, (_, i) => ({
    analysis_id: `analysis_${i}`,
    // ... other properties
  }));
  
  (apiAnalysisHistory as any).mockResolvedValue({
    success: true,
    analyses: largeHistory.slice(0, 10),
    total_count: 1000,
    has_more: true
  });
  
  const startTime = performance.now();
  renderWithQueryClient(<History />);
  
  await waitFor(() => {
    expect(screen.getByText('analysis_0')).toBeInTheDocument();
  });
  
  const renderTime = performance.now() - startTime;
  expect(renderTime).toBeLessThan(1000); // Should render in < 1s
});
```

## Future Testing Enhancements

1. **Visual Regression Testing**: Add screenshot testing for UI components
2. **Accessibility Testing**: Integrate @testing-library/jest-dom accessibility matchers
3. **Performance Monitoring**: Add performance budgets and monitoring
4. **Cross-browser Testing**: Integrate Playwright for real browser testing
5. **API Contract Testing**: Add contract testing with backend team

This comprehensive testing strategy ensures the frontend application is robust, maintainable, and reliable across all user scenarios.
