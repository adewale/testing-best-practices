# Correctness by Construction

Read this when the project uses a typed language (Rust, TypeScript, OCaml,
Haskell, Scala, modern Kotlin/Swift, Go with newtype wrappers, Python with
strict dataclasses/Pydantic) **or** when an Assess-mode audit reveals the same
invariant being checked at three or more layers.

The principle: **lift invariants into the type so the wrong state is
unrepresentable**. Then the only place that needs a test is the parser at the
trust boundary; downstream consumers are correct for free.

This is the test-design corollary of three established slogans:
- "Parse, don't validate" (Alexis King)
- "Make illegal states unrepresentable" (Yaron Minsky)
- "Full recognition before processing" (LangSec)

## When to apply

| Signal | Action |
|---|---|
| Same invariant checked at 3+ layers (controller, service, repo, …) | Lift to a type at the outermost layer; delete inner checks **and their tests** |
| `if x is None: raise ...` near the top of many functions | The parameter type should be non-`None` |
| Tests named `test_X_rejects_empty`, `test_X_rejects_null`, `test_X_rejects_negative` repeated across functions | One parser test, then make the function take the parsed type |
| Comment says "this should never happen" | The comment is a confession that the type permits it; tighten the type and delete the assertion |
| Builder lets you construct an invalid object, then a test asserts it's invalid | Make the invalid construction impossible |

## The rule

> Defense-in-depth is virtue when each layer defends against a *different*
> failure mode. It is an antipattern when each layer defends against the
> *same* failure mode.

Security boundaries (auth + authz + input sanitization + parameterized
queries) defend against *different* threats — keep all layers and all their
tests. Internal re-validation of the same invariant at every layer defends
against nothing real except the absence of a precise type — collapse it.

## Patterns by language

### TypeScript: branded types

```typescript
// BEFORE: every function defends itself
function sendEmail(address: string) {
  if (!address.includes("@")) throw new Error("invalid email");
  // …
}
// Tests: rejects-empty, rejects-no-at, rejects-too-long … repeated per function

// AFTER: the type guarantees it
type EmailAddress = string & { readonly __brand: "EmailAddress" };

function parseEmail(raw: string): EmailAddress | null {
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(raw)) return null;
  if (raw.length > 254) return null;
  return raw as EmailAddress;
}

function sendEmail(address: EmailAddress) { /* no check needed */ }
```

Tests collapse to one parser test (with property-based input):
```typescript
fc.assert(fc.property(fc.string(), (s) => {
  const e = parseEmail(s);
  if (e === null) return;             // valid-or-absent
  expect(e).toContain("@");
  expect(e.length).toBeLessThanOrEqual(254);
}));
```

Every `sendEmail` test now exercises behavior, not validation.

### Rust: newtype with private constructor

```rust
pub struct UserId(u64);          // tuple field is private

impl UserId {
    pub fn new(raw: u64) -> Option<Self> {
        if raw == 0 { None } else { Some(UserId(raw)) }
    }
    pub fn value(&self) -> u64 { self.0 }
}

// Now `fn lookup(id: UserId) -> User` literally cannot be called with 0.
// No test for `lookup_rejects_zero` is needed — the call doesn't compile.
```

### Python: smart constructor with `__post_init__`

```python
@dataclass(frozen=True)
class NonEmptyList(Generic[T]):
    items: tuple[T, ...]

    def __post_init__(self):
        if not self.items:
            raise ValueError("NonEmptyList must have at least one item")

    @property
    def first(self) -> T:           # total — no Optional needed
        return self.items[0]
```

Now `def process(xs: NonEmptyList[int])` doesn't need an empty check, and
neither does its test.

### Go: unexported field + constructor

```go
type Email struct{ s string }

func ParseEmail(raw string) (Email, error) {
    if !strings.Contains(raw, "@") {
        return Email{}, errors.New("invalid email")
    }
    return Email{raw}, nil
}

func (e Email) String() string { return e.s }
```

Construction outside the package goes through `ParseEmail`. Downstream
functions accept `Email` and skip the check.

## Tests to delete

After lifting an invariant into a type, *delete* tests that:

1. Verify a downstream function "rejects" a value that the type now forbids
2. Verify a "this should never happen" branch fires
3. Verify defaults that the type's constructor enforces
4. Verify the same `if x is None` guard that appears in five places

Deletion is the win. Coverage may drop. That is correct — you replaced runtime
checks with compile-time guarantees, and there is nothing left to cover.

## Tests to keep (and to add)

1. **One parser/constructor test per type**, ideally property-based with the
   `valid-or-absent` invariant: for any input, the result is either `None`
   *or* it satisfies every promise the type makes.
2. **One test at every trust boundary** the data crosses: HTTP request
   deserialization, file read, IPC, DB row hydration. Trust boundaries do
   not get types for free — the wire format is `bytes`.
3. **Behavior tests for downstream functions**, expressed in terms of the
   precise types. These test what the function *does*, not what it *rejects*.

## Tests to keep, restated as a list of trust boundaries

A useful audit: list every place in the system where untyped data becomes
typed data. Each one is a test target.

| Boundary | Test type | Why |
|---|---|---|
| HTTP request body → DTO | Parser test + contract test | Wire format is untyped |
| File / config load → struct | Parser test + golden file | Disk is untyped |
| External API response → domain object | VCR cassette + parser test | Provider can change shape |
| DB row → entity | Repository test | Schema can drift from code |
| User input → validated form | Parser test + property test | Untrusted by definition |
| IPC / queue message → typed event | Pirate / contract test | Cross-process boundary |

Inside the boundary: rely on the type system, write behavior tests.

## Interaction with the rest of this skill

| Skill rule | How correctness-by-construction sharpens it |
|---|---|
| Real objects > fakes > stubs > mocks | Mocks are defensive duplicates of contracts; real types eliminate the duplicate |
| PBT "valid-or-absent" pattern | This *is* parse-don't-validate as a test invariant |
| Test data builders express intent | Best builders make illegal test data unrepresentable, not just defaulted |
| No unconditional skips | "This should never happen" tests are the same debt in reverse — promote to a type or delete |
| No "not empty" assertions | A precise return type makes the assertion structural rather than defensive |
| Coverage as informational | After lifting invariants to types, coverage of deleted defensive code drops; that is success |

## Anti-rules (when *not* to apply)

- **Across trust boundaries**: keep defense-in-depth. Auth + authz + WAF +
  parameterized queries each defend against a different threat.
- **Untyped or weakly-typed external systems**: when calling a JS service from
  Python, neither side's types help; contract and VCR tests are the
  correctness-by-construction stand-in at the boundary.
- **Genuine independent failure modes**: retry (transient network) +
  circuit breaker (sustained downstream failure) + fallback (degraded
  response) each handle a *different* failure. All three deserve tests.

## One-line summary

A test that exists because the type is too loose is debt. Lift the invariant
into the type at the outermost trust boundary, delete the downstream checks
and their tests, and keep defense-in-depth only where each layer defends
against a different failure mode.
