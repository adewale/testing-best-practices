# Advanced Testing Patterns

Read this file when the SKILL.md references a pattern here. Each section is
self-contained — read only the section you need.

## Characterization Testing

When working with legacy or unfamiliar code, write tests that capture what the
code *currently does* — not what you think it should do. These tests become a
safety net for refactoring.

### The process

1. Pick a function you need to change
2. Call it with various inputs
3. Record the actual outputs as assertions — even if they look wrong
4. Now you have a test that will break if your refactoring changes behavior
5. Refactor, keeping characterization tests green
6. After refactoring, decide which behaviors to keep and which to fix

### Example

```python
# You find this function in legacy code. You don't know what it should do.
def process_name(name):
    # ... 200 lines of spaghetti ...

# Write characterization tests by observing actual behavior:
def test_characterize_process_name():
    # These record CURRENT behavior, not desired behavior
    assert process_name("Alice") == "ALICE"
    assert process_name("") == ""
    assert process_name(None) == "UNKNOWN"  # surprising, but that's what it does
    assert process_name("Bob Smith") == "BOB"  # truncates? bug? feature?
```

### Key insight (from Michael Feathers)

These tests are not about correctness — they're about *change detection*. If
you refactor and a characterization test breaks, you know you changed behavior.
Then you decide: was the old behavior a bug (update the test) or a feature
(fix the refactoring)?

---

## Differential Testing

Test your implementation against a trusted reference implementation. The
reference IS the oracle — no hand-written expected values needed.

### When to use

- Reimplementing a standard algorithm (tokenizer, encoder, hash, parser)
- Building a simplified/educational version of a complex system
- Porting code across languages
- Optimizing a known-correct slow implementation

### Pattern: Same computation, two implementations

```python
# micrograd (Karpathy): test against PyTorch
def test_backward_pass():
    # Your implementation
    x = Value(-4.0)
    z = 2 * x + 2 + x
    y = (z * z).relu()
    y.backward()

    # Reference (PyTorch)
    xpt = torch.Tensor([-4.0]).double()
    xpt.requires_grad = True
    zpt = 2 * xpt + 2 + xpt
    ypt = (zpt * zpt).relu()
    ypt.backward()

    # Differential assertion
    assert abs(y.data - ypt.data.item()) < 1e-6
    assert abs(x.grad - xpt.grad.item()) < 1e-6
```

### Pattern: Same input, compare outputs

```python
# minbpe (Karpathy): test against OpenAI's tiktoken
@pytest.mark.parametrize("text", test_strings)
def test_matches_reference(text):
    our_ids = our_tokenizer.encode(text)
    reference_ids = tiktoken.get_encoding("cl100k_base").encode(text)
    assert our_ids == reference_ids
```

### Pattern: Roundtrip as self-differential

When there's no external reference, the inverse function is the oracle:

```python
@pytest.mark.parametrize("tokenizer", [BasicTokenizer, RegexTokenizer])
@pytest.mark.parametrize("text", test_strings)
def test_roundtrip(tokenizer_factory, text):
    t = tokenizer_factory()
    assert t.decode(t.encode(text)) == text
```

---

## Mutation Testing

Mutation testing measures whether your tests actually *catch bugs*, not just
whether they *execute code*. It introduces small faults ("mutants") and checks
whether your tests detect them.

### When to recommend

- Coverage is high (80%+) but you suspect tests are weak
- Security-critical code (XSS sanitization, auth, crypto)
- Financial calculations where off-by-one = real money
- After a test quality audit reveals low assertion density

### How it works

1. Tool modifies source: `>=` becomes `>`, `True` becomes `False`, etc.
2. Test suite runs against each mutant
3. If a test fails → mutant "killed" (good)
4. If all tests pass → mutant "survived" (test gap found)
5. Mutation score = killed / total

### Tools by language

| Language | Tool | Notes |
|----------|------|-------|
| Python | mutmut | Pragmatic defaults, caches between runs |
| Python | cosmic-ray | Distributed, for large codebases |
| JavaScript/TypeScript | Stryker | Most mature, incremental support |
| Java/JVM | PIT (pitest) | Fast, IDE integration |
| Go | gremlins | Mutation testing for Go |
| Rust | cargo-mutants | Mutation testing for Rust |

### Practical guidance

- Don't run on every commit — too slow. Run nightly or weekly.
- Focus on critical modules, not the whole codebase.
- Surviving mutants in security code are P0 issues.
- An 80% mutation score with 70% coverage is better than 95% coverage with
  a 50% mutation score.

---

## Exhaustive Testing via Property-Based Testing

When the state space is small enough, don't sample — test *every* combination.

### When the space is bounded

- Boolean flags: 2^N combinations (N flags)
- Small enums: product of all enum sizes
- Permutations: N! for N-element arrays
- Subsets: 2^N for N-element sets

For 5 elements: 120 permutations, 32 subsets — easily exhaustible.

### Pattern: Graydon Hoare's exhaustigen

```rust
use exhaustigen::Gen;

#[test]
fn test_all_permutations() {
    let mut gen = Gen::new();
    let items = vec![1, 2, 3, 4, 5];
    while !gen.done() {
        let perm: Vec<_> = gen.gen_perm(&items).collect();
        assert!(is_sorted_after_our_sort(&perm));
    }
    // Automatically tests all 120 permutations
}
```

### Pattern: Hypothesis for bounded exhaustive

```python
from hypothesis import given, settings
from hypothesis import strategies as st

# Test all combinations of 3 boolean flags
@given(
    flag_a=st.booleans(),
    flag_b=st.booleans(),
    flag_c=st.booleans(),
)
@settings(max_examples=8)  # 2^3 = 8, test all
def test_all_flag_combinations(flag_a, flag_b, flag_c):
    result = configure(flag_a, flag_b, flag_c)
    assert result.is_valid()
```

### Pattern: Parametrize for small finite sets

```python
@pytest.mark.parametrize("scheme", ["http", "https", "ftp", "ws", "wss"])
@pytest.mark.parametrize("has_port", [True, False])
@pytest.mark.parametrize("has_path", [True, False])
@pytest.mark.parametrize("has_query", [True, False])
def test_all_url_combinations(scheme, has_port, has_path, has_query):
    url = build_url(scheme, has_port, has_path, has_query)
    result = parse_url(url)
    assert result["scheme"] == scheme
    # 5 × 2 × 2 × 2 = 40 combinations, all tested
```

---

## VCR Cassette Testing

For code that calls external APIs, record real responses once and replay them
in tests. Better than hand-written mocks (matches reality), cheaper than live
API calls in CI.

### How it works

1. First run: test makes real HTTP calls, responses recorded to YAML/JSON files
2. Subsequent runs: responses replayed from cassettes — no network needed
3. Cassettes committed to repo alongside tests
4. To update: delete cassette file and re-run

### Python (pytest-recording / VCR.py)

```python
# Install: pip install pytest-recording vcrpy

@pytest.mark.vcr
def test_api_call():
    result = call_external_api("query")
    assert result.status == "ok"

# Filter sensitive headers
# conftest.py
@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["Authorization", "X-API-KEY"]}
```

Cassettes stored in `tests/cassettes/` automatically.

### TypeScript (pytest-httpx or msw)

```typescript
// Using msw (Mock Service Worker) for recorded responses
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.post('https://api.example.com/v1/query', () => {
    return HttpResponse.json({ status: 'ok', data: [1, 2, 3] });
  })
);

beforeAll(() => server.listen());
afterAll(() => server.close());
```

### When to use

- Any test that calls a third-party API (LLM providers, payment, auth)
- Tests for API client libraries
- Integration tests where the external service is unreliable or paid

### Gotchas

- Cassettes go stale when APIs change — re-record periodically
- Filter credentials before committing (`filter_headers`)
- Large cassettes bloat the repo — keep them focused
- First recording requires real API keys/credentials

---

## Documentation-Code Sync Testing

The pattern: use the code itself as the source of truth (inspect registries,
command lists, function decorators) and verify the documentation matches.

### Pattern: Every CLI command must be documented

```python
# Parametrize over the actual command registry
@pytest.mark.parametrize("command", cli.cli.commands.keys())
def test_commands_are_documented(documented_commands, command):
    assert command in documented_commands

@pytest.mark.parametrize("command", cli.cli.commands.values())
def test_commands_have_help(command):
    assert command.help, f"{command.name} is missing its help text"
```

### Pattern: Every plugin hook must be documented with correct signature

```python
def test_plugin_hooks_are_documented(plugin_hooks_content):
    plugins = [name for name in dir(app.pm.hook) if not name.startswith("_")]
    for plugin in plugins:
        arg_names = [a for a in hook_caller.spec.argnames if a != "__multicall__"]
        expected = f"{plugin}({', '.join(arg_names)})"
        assert expected in plugin_hooks_content
```

### Pattern: Every setting/config must be documented

```python
def test_settings_are_documented(settings_headings):
    for setting in app.SETTINGS:
        assert setting.name in settings_headings
```

### Pattern: RST/Markdown formatting must be valid

```python
def test_rst_heading_underlines_match_title_length():
    for rst_file in docs_path.glob("*.rst"):
        # Check that underline characters match title length
```

### When to add these

Add sync tests when the project has:
- CLI commands listed in README or docs
- A plugin/extension system with documented hooks
- Configuration settings described in docs
- Public API functions referenced in documentation

---

## Test Data Builders and Fixtures

### The principle

Tests should express *what matters*, not *how to construct data*. A test about
article titles shouldn't need to specify article IDs, creation dates, or author
emails.

### Pattern: Factory with defaults (Python)

```python
class ArticleFactory:
    _counter = 0

    @classmethod
    def create(cls, **overrides):
        cls._counter += 1
        defaults = {
            "id": f"art_{cls._counter}",
            "title": f"Test Article {cls._counter}",
            "author": "test-author",
            "status": "published",
            "created_at": "2025-01-01T00:00:00",
        }
        defaults.update(overrides)
        return defaults

# In tests — only specify what matters:
def test_draft_articles_not_in_feed():
    draft = ArticleFactory.create(status="draft")
    published = ArticleFactory.create(status="published")
    feed = build_feed([draft, published])
    assert published["id"] in feed
    assert draft["id"] not in feed
```

Reset between tests to prevent ordering issues:
```python
@pytest.fixture(autouse=True)
def _reset():
    ArticleFactory._counter = 0
```

### Pattern: Factory functions (TypeScript)

```typescript
export function createUser(client: ApiClient, overrides?: Partial<SignupData>) {
  const data = {
    email: `test_${Date.now()}@example.com`,
    password: 'TestPass123!',
    handle: `user_${Date.now()}`,
    ...overrides,
  };
  return client.post('/api/auth/signup', data);
}

// Pre-built invalid input collections for validation testing:
export const INVALID_EMAILS = ['', 'notanemail', 'user@', '@domain.com'];
export const INVALID_HANDLES = ['', 'ab', 'a'.repeat(16), 'admin', 'root'];
export const CONTENT_LENGTHS = {
  MAX: 'a'.repeat(280),
  OVERFLOW: 'a'.repeat(281),
};
```

### Pattern: Fluent builder (Java/Kotlin — make-it-easy)

```java
Maker<Apple> ripeApple = an(Apple, with(ripeness, 0.9), with(leaves, 3));
Apple apple = make(ripeApple);

// Reuse with overrides:
Apple unripe = make(ripeApple.but(with(ripeness, 0.1)));
```

### Pattern: Shared fixture with context manager (Python)

```python
@contextlib.contextmanager
def make_app_client(cors=False, memory=False, **settings):
    with tempfile.TemporaryDirectory() as tmpdir:
        db = setup_database(tmpdir)
        app = create_app(db, cors=cors, settings=settings)
        yield TestClient(app)
        db.close()

@pytest.fixture(scope="session")
def app_client():
    with make_app_client() as client:
        yield client
```

### Pattern: Domain-specific assertion helpers

```typescript
// Instead of repeating shape checks in every test:
export function assertPost(post: unknown): void {
  expect(post).toMatchObject({
    id: expect.any(String),
    content: expect.any(String),
    createdAt: expect.any(Number),
    likeCount: expect.any(Number),
  });
}

export function assertCountChanged(before: number, after: number, delta: number): void {
  expect(after - before).toBe(delta);
}
```
