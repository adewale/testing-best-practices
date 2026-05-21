# Test Data Builders, Fixtures, and Helpers

Tests should express *what matters*, not *how to construct data*.

## Pattern: Factory with defaults (Python)

```python
class ArticleFactory:
    _counter = 0

    @classmethod
    def create(cls, **overrides):
        cls._counter += 1
        defaults = {
            "id": f"art_{cls._counter}",
            "title": f"Test Article {cls._counter}",
            "status": "published",
        }
        defaults.update(overrides)
        return defaults

# Tests only specify what matters:
def test_draft_articles_not_in_feed():
    draft = ArticleFactory.create(status="draft")
    published = ArticleFactory.create(status="published")
    feed = build_feed([draft, published])
    assert published["id"] in feed
    assert draft["id"] not in feed
```

## Pattern: Factory functions (TypeScript)

```typescript
export function createUser(client: ApiClient, overrides?: Partial<SignupData>) {
  return client.post('/api/auth/signup', { ...defaultUserData(), ...overrides });
}

// Pre-built invalid input collections:
export const INVALID_EMAILS = ['', 'notanemail', 'user@', '@domain.com'];
```

## Pattern: File tree builders (filesystem tests)

```javascript
createFilesFromTree({
  src: { "index.ts": "content", lib: { "utils.ts": "content" } },
  "package.json": '{"name": "test"}',
});
```

## Pattern: Domain-specific assertion helpers

```typescript
export function assertPost(post: unknown): void {
  expect(post).toMatchObject({
    id: expect.any(String),
    content: expect.any(String),
    createdAt: expect.any(Number),
  });
}
```

## Pattern: Pin non-deterministic inputs

```javascript
beforeEach(() => {
    Date.prototype.toString = () => "Sat Aug 30 2014 09:16:45";
});
afterEach(() => { Date.prototype.toString = originalDateToString; });
```

Pin the non-deterministic part rather than mocking the whole subsystem.

## Pattern: Shared fixture with context manager (Python)

```python
@contextlib.contextmanager
def make_app_client(cors=False, **settings):
    with tempfile.TemporaryDirectory() as tmpdir:
        app = create_app(setup_database(tmpdir), cors=cors, settings=settings)
        yield TestClient(app)
```
