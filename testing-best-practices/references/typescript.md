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

it('returns a valid result or structured error for arbitrary input', () => {
  fc.assert(
    fc.property(fc.string(), (input) => {
      expect(() => parse(input)).not.toThrow();
      const result = parse(input);

      if (result.ok) {
        expect(result.ast).toMatchObject({ type: expect.any(String) });
      } else {
        expect(result.error).toMatchObject({ message: expect.any(String) });
      }
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

```

**Key arbitraries**: `fc.string()`, `fc.integer()`, `fc.float()`,
`fc.array()`, `fc.record()`, `fc.uuid()`, `fc.webUrl()`,
`fc.constantFrom(...)`, `fc.option()`. Use `fc.record()` and `fc.letrec()` for specification-valid structures; keep hostile arbitrary input in a separate totality property.

### Collection, Replay, and Command Models

When Vitest projects, filters, or workspaces make reachability uncertain, inspect collection with the same CI configuration. `--filesOnly` proves file-level discovery, not collection of a particular test; add a persistent guard only where that configuration has a real drift risk.

Preserve fast-check's `seed` and `path` for `fc.assert`. Model-based failures also report a `replayPath`; pass it to `fc.commands`, not `fc.assert`. Ensure the configuration that runs the property receives those values; logging them is not replay.

```typescript
// Values parsed from a saved model-based failure. Omit them for normal discovery.
const { seed, path, replayPath } = savedFailure;
const commands = fc.commands(commandArbs, { maxCommands, replayPath });

await fc.assert(
  fc.asyncProperty(commands, async (cmds) => {
    await fc.asyncModelRun(setup, cmds);
  }),
  { numRuns, seed, path },
);
```

For model-based tests, make `Command.check` target-specific and resolve the same logical handle that `run` uses. `fc.commands` generates candidates before preconditions are applied, so a command cap is not evidence of useful depth; observe accepted transitions when that matters. Do not hide an inapplicable target as a silent no-op in `run`.

If a function receives `fc` or a narrowed adapter, use that binding and the installed API rather than importing a second engine or guessing a convenience constructor.

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

## Choosing values and matchers

- Include distinct, non-default test values so at least one case exposes a
  dropped, defaulted, or swapped argument. Still cover `0`, `''`, and
  equal-value cases when they are boundaries or part of the contract.
- When order is not part of the contract, use
  `expect(arr).toEqual(expect.arrayContaining([...]))` plus a length check,
  or sort both sides, instead of pinning incidental order.
- Derive expected results independently of the SUT. Literals are clearest for
  simple examples; properties and independent reference models are valid for
  broader cases. Do not reuse the SUT's logic or constants in the oracle.
