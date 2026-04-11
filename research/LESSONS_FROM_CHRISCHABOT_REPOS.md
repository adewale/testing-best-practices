# Lessons from github.com/chrischabot Repositories

> Extracted from scanning ~60 repositories across TypeScript, Rust, Go, Swift, Shell, and Java.
> Date: 2026-04-11

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Testing Ecosystem Overview](#testing-ecosystem-overview)
3. [Five-Tier Test Architecture](#five-tier-test-architecture)
4. [API Scenario Testing](#api-scenario-testing)
5. [Test Infrastructure Patterns](#test-infrastructure-patterns)
6. [Visual Regression Testing](#visual-regression-testing)
7. [Scale and Load Testing](#scale-and-load-testing)
8. [Shell Script Testing](#shell-script-testing)
9. [Rust Testing Patterns](#rust-testing-patterns)
10. [Acceptance Battery Pattern](#acceptance-battery-pattern)
11. [Coverage Thresholds](#coverage-thresholds)
12. [Swift Testing with Real APIs](#swift-testing-with-real-apis)
13. [Coding Agent Testing](#coding-agent-testing)
14. [Anti-Patterns and Lessons](#anti-patterns-and-lessons)

---

## Executive Summary

Chris Chabot's repos demonstrate a practitioner who builds and ships across many languages and platforms. Key testing themes:

- **Five-tier test architecture** in the-wire: unit → integration → API → E2E → visual, each with its own vitest/playwright config
- **API scenario testing** models complex multi-user workflows (social graphs, blocking, feed composition) against a real wrangler dev server
- **Comprehensive test infrastructure**: typed API clients, assertion helpers, test factories, database reset between suites
- **High coverage thresholds** for API tests: 95% line/function, 90% branch — enforced in vitest config
- **Acceptance battery repos** — a pattern of generating hello-world repos across languages to test tooling/CI pipelines
- **Shell script test suites** with safety-critical validation (file deletion protection, path validation)
- **Real API integration tests in Swift** — tests that hit real Claude API, with graceful bailout on credit exhaustion

---

## Testing Ecosystem Overview

| Repo | Language | Test Framework | Test Tiers | Coverage Config |
|------|----------|---------------|-----------|-----------------|
| the-wire | TypeScript | Vitest (Workers pool) + Playwright | 5 tiers (unit/integration/api/e2e/visual) | 95%/95%/90%/95% thresholds (API) |
| foundry | TypeScript | bun:test | Unit + E2E | -- |
| code-search | Rust | cargo test | Integration (CLI binary tests) | -- |
| zerobrew-1 | Rust | cargo test | Unit (workspace) | -- |
| cleanmymac | Shell | Custom bash test runner | Unit (3 test suites) | -- |
| anthropic-swift-sdk | Swift | Swift Testing (@Test) | Unit + Integration (live API) | -- |
| helloworld | Multi-lang | -- | Acceptance battery | -- |

---

## Five-Tier Test Architecture

the-wire has the most elaborate test architecture of any repo examined across all three GitHub accounts.

### Tier 1: Unit Tests (`tests/unit/`)

Pure logic tests against utilities, crypto, validation, search indexing:

```typescript
// vitest.config.ts — Cloudflare Workers pool
include: ['tests/unit/**/*.test.ts', 'tests/integration/**/*.test.ts'],
exclude: ['tests/scale/**', 'tests/e2e/**'],
```

Tests are fast, deterministic, no network:
- `crypto.test.ts` — salt generation, password hashing, timing-safe comparison
- `snowflake.test.ts` — ID uniqueness, time-ordering, parse/roundtrip
- `search-index.test.ts` — tokenization, stopword filtering, prefix indexing
- `validation.test.ts` — input validation rules
- `response.test.ts` — response helper formatting

### Tier 2: Integration Tests (`tests/integration/`)

Tests that exercise multiple components via the Workers pool:
- `auth.test.ts` — authentication flow
- `feed.test.ts` — feed composition
- `follow-counts.test.ts` — social graph count consistency

### Tier 3: API Tests (`tests/api/`)

Full HTTP tests against a real wrangler dev server:

```typescript
// vitest.config.api.ts — separate config
globalSetup: ['tests/api/setup/global-setup.ts'],
testTimeout: 30000,
hookTimeout: 60000,
pool: 'forks',
poolOptions: { forks: { singleFork: true } }, // Sequential for state-dependent scenarios
coverage: {
  thresholds: {
    lines: 95,
    functions: 95,
    branches: 90,
    statements: 95,
  },
},
```

Organized by domain: `auth/`, `users/`, `posts/`, `feed/`, `search/`, `media/`, `notifications/`, `admin/`, `scenarios/`.

### Tier 4: E2E Tests (`tests/e2e/`)

Three approaches coexist:
- **Playwright** (`tests/e2e/playwright/`) — browser-based UI tests
- **Browser scripts** (`tests/e2e/browser/`) — comprehensive manual test scripts
- **Curl scripts** (`tests/e2e/curl/`) — shell-based API smoke tests (`auth.sh`, `posts.sh`, `social.sh`)

### Tier 5: Visual Regression (`tests/visual/`)

Playwright screenshot comparisons across all 6 themes:

```typescript
// Masks volatile content to prevent false positives
mask: [
  page.locator('.timestamp'),
  page.locator('.post-timestamp'),
  page.locator('.notification-badge'),
  page.locator('.unread-count'),
  page.locator('[data-testid="timestamp"]'),
],
```

**Key design decisions**:
- Tests iterate over all themes × all pages = comprehensive matrix
- Component-level screenshots (post-card, compose-box, sidebar, bottom-nav) alongside page-level
- Custom CSS injected via `stylePath` to stabilize rendering
- Timestamps and badges masked to prevent flakiness

---

## API Scenario Testing

The most distinctive pattern. `tests/api/scenarios/` contains complex multi-user workflow tests.

### Pattern: Social Graph Scenarios

```typescript
describe('Linear Follow Chain (A → B → C → D)', () => {
  it('User A should see posts from B in home feed (direct follow)', ...);
  it('User A should NOT see posts from C directly (not followed)', ...);
  it('User D is 3 hops away - should not appear in A\'s feed', ...);
  it('Follower counts should be accurate', ...);
});

describe('Mutual Follows (A ↔ B)', () => {
  it('Both users should see each other in their feeds', ...);
  it('Both should appear in following/followers lists', ...);
  it('Unfollowing one direction maintains other connection', ...);
});

describe('Star Topology (A follows B, C, D, E, F)', () => {
  it('Center should see posts from all followed users', ...);
  it('Unfollowing one removes their posts from feed', ...);
});
```

**Lesson**: Name scenarios after graph topologies (linear chain, mutual, star, hub-and-spoke). This makes the test intent immediately clear and ensures coverage of different relationship patterns.

### Pattern: Blocking Scenarios

```typescript
describe('blocking.test.ts', () => {
  // Tests the full blocking lifecycle:
  // Block → verify hidden from feed → verify can't interact → unblock → verify restored
});
```

### Pattern: Feed Composition Scenarios

```typescript
describe('feed-composition.test.ts', () => {
  // Tests how feeds are composed from:
  // - Direct follows
  // - Reposts from followed users
  // - Quoted posts
  // - Thread replies
});
```

**Lesson**: Scenario tests are the sweet spot between unit tests (too narrow) and full E2E tests (too expensive). They test business logic through real HTTP endpoints with multiple interacting actors.

---

## Test Infrastructure Patterns

### Pattern: Typed API Client

```typescript
export class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  setToken(token: string): void { ... }
  clearToken(): void { ... }

  async get<T>(path, params?): Promise<ApiResponse<T>> { ... }
  async post<T>(path, body?): Promise<ApiResponse<T>> { ... }
  async put<T>(path, body?): Promise<ApiResponse<T>> { ... }
  async delete<T>(path): Promise<ApiResponse<T>> { ... }
  async uploadFile(path, file): Promise<ApiResponse<...>> { ... }
  async resetDatabase(): Promise<void> { ... }
}
```

**Lesson**: A typed API client is the foundation of good API tests. It handles auth token management, content-type headers, JSON parsing, and provides a clean interface for all HTTP methods.

### Pattern: Domain-Specific Assertion Helpers

```typescript
export function assertSuccess<T>(response: ApiResponse<T>, expectedStatus = 200): T { ... }
export function assertBadRequest(response: ApiResponse, errorContains?: string): void { ... }
export function assertUnauthorized(response: ApiResponse, errorContains?: string): void { ... }
export function assertUserProfile(user: unknown): void { ... }
export function assertPost(post: unknown): void { ... }
export function assertNotification(notification: unknown): void { ... }
export function assertPaginatedResponse<T>(response, options?): void { ... }
export function assertCountChanged(before, after, delta, message?): void { ... }
```

**Lesson**: Domain-specific assertions (`assertPost`, `assertUserProfile`, `assertNotification`) verify the shape of domain objects without coupling to specific field values. `assertCountChanged` is a reusable pattern for verifying state transitions.

### Pattern: Test Factories with Validation Test Data

```typescript
export function createUser(client, overrides?): Promise<UserWithToken> { ... }
export function createUsers(client, count): Promise<UserWithToken[]> { ... }
export function createPost(client, overrides?): Promise<Post> { ... }
export function createUserWithPosts(client, postCount): Promise<{user, posts}> { ... }

// Pre-built invalid input collections:
export const INVALID_EMAILS = ['', 'notanemail', 'user@', ...];
export const INVALID_PASSWORDS = ['', 'short', 'alllowercase1', ...];
export const INVALID_HANDLES = ['', 'ab', 'user-name', 'admin', ...];
export const CONTENT_LENGTHS = { EMPTY: '', MIN: 'a', MAX: 'a'.repeat(280), OVERFLOW: 'a'.repeat(281) };
```

**Lesson**: Pre-built collections of invalid inputs for validation testing. Every validation rule has a corresponding test input. The boundary values (`MAX` = 280 chars, `OVERFLOW` = 281 chars) are explicitly defined.

### Pattern: Global Setup with Real Server

```typescript
// tests/api/setup/global-setup.ts
export async function setup(): Promise<() => Promise<void>> {
  // Start wrangler dev server
  wranglerProcess = spawn('npx', ['wrangler', 'dev', '--port', '8787']);
  await waitForServer(BASE_URL);
  await resetDatabase(BASE_URL);

  return async () => {
    wranglerProcess.kill('SIGTERM');
  };
}
```

**Lesson**: API tests run against a real wrangler dev server, not mocks. The global setup starts the server, waits for it to respond, resets the database to clean state, and returns a teardown function.

---

## Visual Regression Testing

### Cross-Theme Screenshot Matrix

```typescript
for (const theme of THEMES) {
  for (const pageConfig of PAGES) {
    test(`${pageConfig.name}`, async ({ page }) => {
      await setTheme(page, theme);
      if (pageConfig.auth) await ensureLoggedIn(page);
      await navigateAndStabilize(page, pageConfig.path);

      await expect(page).toHaveScreenshot(`${pageConfig.name}-${theme}.png`, {
        fullPage: true,
        animations: 'disabled',
        mask: [page.locator('.timestamp'), ...],
      });
    });
  }
}
```

**Key decisions**:
- `maxDiffPixels: 100` (the-wire) vs `maxDiffPixelRatio: 0.01` (atlas) — pixel count vs ratio
- Custom `screenshot.css` injected to stabilize fonts and animations
- Auth-required pages handled with `ensureLoggedIn` helper
- Component isolation: post-card, compose-box, sidebar, bottom-nav each screenshotted separately

### CI Configuration

```typescript
// playwright.config.ts
forbidOnly: !!process.env.CI,  // Prevent .only from shipping
retries: process.env.CI ? 2 : 0,  // Retry flaky tests in CI
screenshot: 'only-on-failure',  // Debug artifacts
video: 'retain-on-failure',  // Debug artifacts
trace: 'on-first-retry',  // Performance traces on retry
```

**Lesson**: `forbidOnly` prevents accidentally committing `.only` test markers. `screenshot` and `video` only on failure reduces storage.

---

## Scale and Load Testing

### Pattern: Small-Scale Smoke Test

```typescript
// tests/scale/small-test.ts
const NUM_USERS = 10;
const ACTIONS_PER_USER = 10;

async function runTest() {
  // Create users
  for (let i = 0; i < NUM_USERS; i++) {
    users.push(await createUser(i));
  }
  // Each user creates posts
  for (const user of users) {
    for (let i = 0; i < ACTIONS_PER_USER; i++) {
      await createPost(user);
    }
  }
}
```

**Lesson**: Keep a small-scale version (10 users, 10 actions) alongside the load harness. The small test is fast enough to run frequently and catches concurrency issues without the overhead of a full load test.

---

## Shell Script Testing

### Pattern: Safety-Critical Shell Test Suites (cleanmymac)

```
tests/
├── run_tests.sh           # Test runner with colored output and exit codes
├── test_path_validator.sh # Path validation tests
├── test_protection.sh     # File protection tests (critical paths)
├── test_safe_delete.sh    # Safe deletion tests
```

The test runner discovers and runs all `test_*.sh` files with suite-level pass/fail tracking:

```bash
for test_file in "$TEST_DIR"/test_*.sh; do
    if bash "$test_file"; then
        ((SUITES_PASSED++))
    else
        ((SUITES_FAILED++))
    fi
done
```

**Lesson**: For shell utilities that delete files, safety tests (path validation, protected path detection, safe deletion) are more important than feature tests. Test the guard rails before testing the features.

---

## Rust Testing Patterns

### Pattern: CLI Binary Integration Tests (code-search)

```rust
fn code_search_bin() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("target/release/code-search")
}

#[test]
fn test_json_output() {
    setup_test_files();
    let output = Command::new(code_search_bin())
        .args(&["search", "--output", "json", "Calculator", &fixtures_dir()])
        .output()
        .expect("Failed to execute command");

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("\"total_matches\""), "Should output valid JSON");
}
```

**Key patterns**:
- Tests run the compiled binary as a subprocess (not library calls)
- Test fixtures are created in `setup_test_files()` before each test
- Tests verify both stdout content and exit codes
- Language-filtered search, regex mode, semantic search all tested

### Pattern: Workspace-Level CI (zerobrew-1)

```yaml
# .github/workflows/test.yml
strategy:
  matrix:
    include:
      - os: macos-latest, rust: stable
      - os: macos-latest, rust: "1.90"  # MSRV
      - os: ubuntu-latest, rust: stable

steps:
  - run: cargo build --workspace --all-targets
  - run: cargo build --workspace --release
  - run: cargo test --workspace
```

**Lesson**: Test against both stable Rust and your Minimum Supported Rust Version (MSRV). The `--workspace` flag ensures all crates in the workspace are tested together.

### Pattern: Separate Lint and Test Workflows

```yaml
# ci.yml (lint)
- cargo fmt --all -- --check
- cargo clippy --workspace --all-targets -- -D warnings
- cargo audit

# test.yml (test)
- cargo build --workspace --all-targets
- cargo test --workspace
```

**Lesson**: Lint and test as separate CI jobs. Lint is cheap and fast; test needs matrix expansion.

---

## Acceptance Battery Pattern

~20 `helloWorld*` repos with description "Acceptance battery hello worlds repository" suggest a systematic approach to testing tooling pipelines. The base `helloworld` repo contains hello-world examples in 8 languages (Python, JavaScript, Java, C, C++, Go, Ruby, Rust).

**Pattern**: Generate hello-world repos across languages to validate that CI/CD pipelines, build tools, and deployment workflows work correctly for each language.

**Lesson**: When building developer tools that must work across languages, create a battery of minimal repos that exercise the happy path in each supported language. This catches language-specific build/runtime issues that a single-language test wouldn't find.

---

## Coverage Thresholds

### API Test Coverage (the-wire)

```typescript
coverage: {
  thresholds: {
    lines: 95,
    functions: 95,
    branches: 90,
    statements: 95,
  },
},
```

This is the most aggressive coverage threshold across all three GitHub accounts scanned. Notable:
- 95% line coverage for API tests (compared to 80% in skill_scanner, 75% in rogue_planet)
- 90% branch coverage explicitly enforced
- Applied to API tests specifically, not unit tests — the API tests exercise more of the codebase

### Unit/Integration Coverage

```typescript
// vitest.config.ts (unit + integration)
coverage: {
  provider: 'v8',
  reporter: ['text', 'json', 'html'],
  include: ['src/**/*.ts'],
  exclude: ['src/types/**', 'src/**/*.d.ts'],
  // No thresholds — informational only
},
```

**Lesson**: High coverage thresholds on API tests (which exercise the full stack) are more meaningful than on unit tests. API test coverage proves the code actually works end-to-end.

---

## Swift Testing with Real APIs

### Pattern: Graceful Bailout on Credit Exhaustion

```swift
@Test func writerFlowStructuredOutput() async throws {
    guard let key = apiKey else { return }
    let client = AnthropicClient(apiKey: key)

    do {
        let response: WriterResponse = try await client.messages.createStructured(...)
        #expect(!response.markdown.isEmpty)
    } catch let error as AnthropicError {
        if case let .httpError(status, message, _) = error,
           status == 400,
           (message ?? "").contains("credit balance") {
            return  // Graceful bailout — not a test failure
        }
        throw error
    }
}
```

**Lesson**: Integration tests that hit real paid APIs should bail out gracefully when credits are exhausted, not fail the test suite. The `guard let key = apiKey else { return }` pattern also skips when no API key is configured.

### Pattern: Swift Testing Framework (@Test, #expect)

```swift
@Suite struct AgentUsageTests {
    @Test func writerFlow() async throws { ... }
    @Test func noteTakerFlow() async throws { ... }
}
```

Using Swift's native Testing framework (`import Testing`) with `@Suite`, `@Test`, `#expect` — the modern Swift testing approach.

---

## Coding Agent Testing

### Pattern: Tool Tests with Real Filesystem (foundry)

```typescript
beforeEach(async () => {
  testDir = join(tmpdir(), `coding-agent-test-${Date.now()}`);
  await mkdir(testDir, { recursive: true });
  context = { workingDirectory: testDir, threadId: "test-thread" };
});

afterEach(async () => {
  await rm(testDir, { recursive: true, force: true });
});
```

Every tool test creates a real temp directory with real files, exercises the tool, and cleans up.

**Key testing patterns for agent tools**:
- **Read tool**: Tests file reading with offsets, line numbers, relative paths, error on missing files
- **Edit tool**: Tests replacement, error on not-found, error on multiple matches, file creation
- **Bash tool**: Tests command execution, exit codes, cwd, stderr capture
- **Grep tool**: Tests pattern matching, path filtering, no-results message

**Lesson**: Agent tools must be tested with real filesystem operations, not mocked file systems. The tools manipulate real files and the tests must verify the actual filesystem state after each operation.

---

## Anti-Patterns and Lessons

### 1. Sequential API Tests for State-Dependent Scenarios

```typescript
pool: 'forks',
poolOptions: { forks: { singleFork: true } },
sequence: { shuffle: false },
```

API scenario tests run sequentially because each scenario builds on state from previous steps. This is correct — parallelizing stateful tests causes flaky failures.

**Lesson**: When tests depend on shared state (user A follows user B, then B posts, then A checks feed), run them sequentially. Don't force parallelism on inherently sequential workflows.

### 2. Database Reset Between Suites, Not Between Tests

```typescript
beforeAll(async () => {
  client = createApiClient();
  await client.resetDatabase();
});
```

The database is reset at the suite level (`beforeAll`), not before each test. This is pragmatic for scenario tests where each test in a describe block depends on the state from the previous `beforeAll`.

### 3. Missing Property-Based Tests

None of the repos use property-based testing (no Hypothesis, no fast-check). The unit tests test specific examples but don't explore the input space systematically. For example, `search-index.test.ts` tests specific tokenization cases but doesn't use PBT to verify invariants like "tokenize never crashes on arbitrary Unicode input."

**Lesson**: This is a gap. Functions like `tokenize`, `hashPassword`, `generateId`, and `base64 roundtrip` are ideal candidates for property-based testing.

### 4. Scale Tests Exist But Not in CI

The `tests/scale/` directory has load testing scripts, but they're not integrated into CI. They require manual execution.

**Lesson**: At minimum, the small-scale test (10 users, 10 actions) should run in CI. Full load tests can remain manual.

### 5. Curl-Based E2E Tests Are Manual

`tests/e2e/curl/` contains shell scripts for API testing, but these are manual smoke tests, not automated CI tests.

**Lesson**: Curl scripts are valuable documentation of API contracts, but automated API tests (like the vitest-based ones in `tests/api/`) provide better coverage and CI integration.

---

## Key Takeaways

1. **Five-tier test architecture** with separate configs per tier provides clear separation of concerns
2. **Scenario tests modeling graph topologies** (linear chain, mutual follow, star, hub-and-spoke) catch complex interaction bugs
3. **Domain-specific assertion helpers** (`assertPost`, `assertUserProfile`) make tests readable and DRY
4. **Pre-built invalid input collections** ensure every validation rule is tested at boundaries
5. **Real server global setup** with database reset ensures API tests hit actual infrastructure
6. **Cross-theme visual regression** with timestamp masking provides layout confidence without flakiness
7. **High API coverage thresholds** (95%) are more meaningful than high unit test thresholds
8. **Shell test suites for safety-critical tools** verify guard rails before features
9. **CLI binary integration tests** (Rust) exercise the compiled binary as users would
10. **Acceptance battery repos** systematically validate tooling across all supported languages
11. **Graceful bailout on paid API credit exhaustion** prevents CI failures from billing issues
12. **Property-based testing is a gap** — ideal for tokenization, hashing, ID generation, and roundtrip functions
