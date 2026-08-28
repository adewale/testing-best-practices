# Test Data Builders, Fixtures, and Helpers

Tests should express *what matters*, not *how to construct data*. When examples come from users or domain experts, preserve their business vocabulary in fixtures, builders, table rows, or small test DSLs.

Never rely on a builder/factory default for a field an assertion depends on — set it explicitly in the test. Helpers construct values; they must not compute expected values or hide behavior-relevant setup (see the logic-in-tests antipattern in `references/antipatterns.md`).

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

## Pattern: Small domain DSLs for dense examples

When a domain has compact operations, a tiny helper can make test cases readable:

```typescript
// journal action DSL for page history tests
expect(action("m1321")).toEqual({
  type: "move",
  id: "10",
  order: ["30", "20", "10"],
});
```

Rules:
- Use the DSL only when it makes many examples easier to read.
- Keep it in test code unless production also needs the notation.
- Test the helper/DSL before relying on it in behavior tests.
- Prefer domain terms (`paidOrder`, `movedBefore`, `interestRow`) over structural terms (`object1`, `data2`).
- Do not hide the expected behavior behind clever encodings; a reader should still see the business rule.

## Pattern: Pin non-deterministic inputs

```javascript
beforeEach(() => {
    Date.prototype.toString = () => "Sat Aug 30 2014 09:16:45";
});
afterEach(() => { Date.prototype.toString = originalDateToString; });
```

Pin the non-deterministic part rather than mocking the whole subsystem.

## Pattern: Logging fakes for visible side effects

A purpose-built fake can be better than a mock when the useful assertion is the visible effect:

```python
class RecordingBus:
    def __init__(self):
        self.events = []

    def publish(self, event):
        self.events.append(event)


def test_checkout_publishes_receipt_event():
    bus = RecordingBus()
    checkout(order, bus=bus)
    assert bus.events == [ReceiptIssued(order_id=order.id)]
```

This checks the observable contract without verifying incidental call choreography. If the real collaborator is cheap and local, prefer the real collaborator first.

## Pattern: Shared fixture with context manager (Python)

```python
@contextlib.contextmanager
def make_app_client(cors=False, **settings):
    with tempfile.TemporaryDirectory() as tmpdir:
        app = create_app(setup_database(tmpdir), cors=cors, settings=settings)
        yield TestClient(app)
```
