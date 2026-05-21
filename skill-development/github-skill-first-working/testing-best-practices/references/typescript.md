# TypeScript / JavaScript Testing Reference

## Framework: Vitest (preferred) or Jest

### Project setup (Vitest)

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    include: ['tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.ts'],
      exclude: ['src/types/**', 'src/**/*.d.ts'],
    },
  },
});
```

For Cloudflare Workers:
```typescript
import { defineWorkersConfig } from '@cloudflare/vitest-pool-workers/config';

export default defineWorkersConfig({
  test: {
    poolOptions: {
      workers: { wrangler: { configPath: './wrangler.toml' } },
    },
  },
});
```

### Directory structure

```
tests/
  unit/           # Pure logic, no network
  integration/    # Multiple components, some real deps
  api/            # HTTP tests against real/dev server
    setup/
      api-client.ts       # Typed HTTP client
      test-factories.ts   # User/post/data builders
      assertions.ts       # Domain assertion helpers
      global-setup.ts     # Server startup/teardown
  e2e/            # Playwright browser tests
  visual/         # Screenshot regression tests
```

## Property-Based Testing: fast-check

```typescript
import fc from 'fast-check';

it('never throws on arbitrary input', () => {
  fc.assert(
    fc.property(fc.string(), (input) => {
      const result = parse(input);
      expect(result).toBeDefined();
    }),
    { numRuns: 500 }
  );
});

it('roundtrip: decode(encode(x)) === x', () => {
  fc.assert(
    fc.property(fc.string(), (text) => {
      expect(decode(encode(text))).toBe(text);
    }),
    { numRuns: 200 }
  );
});

it('results sorted by descending score', () => {
  fc.assert(
    fc.property(fc.integer({ min: 1, max: 10 }), (n) => {
      const results = rankResults(generateItems(n));
      for (let i = 1; i < results.length; i++) {
        expect(results[i - 1].score).toBeGreaterThanOrEqual(results[i].score);
      }
    }),
    { numRuns: 100 }
  );
});
```

**Key arbitraries**: `fc.string()`, `fc.integer()`, `fc.float()`,
`fc.array()`, `fc.record()`, `fc.uuid()`, `fc.webUrl()`,
`fc.constantFrom(...)`, `fc.option()`.

## E2E Testing: Playwright

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: 'http://localhost:8787',
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { viewport: { width: 375, height: 812 } } },
  ],
});
```

### Visual regression

```typescript
test('component layout', async ({ page }) => {
  await page.goto('/');
  const component = page.locator('.my-component');
  await expect(component).toHaveScreenshot('component.png', {
    maxDiffPixelRatio: 0.01,
    animations: 'disabled',
    mask: [page.locator('.timestamp')],
  });
});

// Skip in CI (font rendering differs)
test.skip(!!process.env.CI, 'Visual tests skipped in CI');
```

### Mock contract tests (validate mocks against real browser)

```typescript
test('canvas measureText returns positive width', async ({ page }) => {
  await page.goto('/');
  const width = await page.evaluate(() => {
    const ctx = document.createElement('canvas').getContext('2d')!;
    ctx.font = '16px system-ui';
    return ctx.measureText('Hello').width;
  });
  expect(width).toBeGreaterThan(0);
});
```

## Test Infrastructure Patterns

### Typed API client

```typescript
export class ApiClient {
  private token: string | null = null;
  setToken(token: string): void { this.token = token; }
  async get<T>(path: string): Promise<ApiResponse<T>> { ... }
  async post<T>(path: string, body?: unknown): Promise<ApiResponse<T>> { ... }
}
```

### Domain assertion helpers

```typescript
export function assertSuccess<T>(response: ApiResponse<T>, status = 200): T {
  expect(response.status).toBe(status);
  expect(response.body.success).toBe(true);
  return response.body.data!;
}

export function assertPost(post: unknown): void {
  expect(post).toMatchObject({
    id: expect.any(String),
    content: expect.any(String),
    createdAt: expect.any(Number),
  });
}
```

### Test factories with invalid input collections

```typescript
export const INVALID_EMAILS = ['', 'notanemail', 'user@', '@domain.com'];
export const CONTENT_LENGTHS = {
  MAX: 'a'.repeat(280),
  OVERFLOW: 'a'.repeat(281),
};

export function createUser(client: ApiClient, overrides?: Partial<SignupData>) {
  return client.post('/api/auth/signup', createUserData(overrides));
}
```

## CLI testing with Click-equivalent

```typescript
import { CliRunner } from './test-helpers';

test('help text', () => {
  const result = runner.invoke(['--help']);
  expect(result.exitCode).toBe(0);
  expect(result.output).toContain('Usage:');
});
```

## Global test setup (API tests against real server)

```typescript
// tests/api/setup/global-setup.ts
export async function setup() {
  const server = spawn('npx', ['wrangler', 'dev', '--port', '8787']);
  await waitForServer('http://localhost:8787');
  await resetDatabase('http://localhost:8787');
  return async () => { server.kill('SIGTERM'); };
}
```
