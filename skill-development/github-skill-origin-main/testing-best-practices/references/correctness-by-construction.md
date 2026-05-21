# Correctness by Construction

Read this when the project uses a typed language (Rust, TypeScript, OCaml,
Haskell, Scala, modern Kotlin/Swift, Go with newtype wrappers, Python with
strict dataclasses/Pydantic) **or** when an Assess-mode audit reveals the
same invariant being checked at three or more layers, status enums duplicated
across layers, loose strings flowing through the whole system, catch-all
retries, silent fallbacks, or post-hoc sanitizer patches.

The principle: **lift invariants into the type or schema so the wrong state
is unrepresentable**. Then the only test that needs to exist is the parser
test at the boundary, plus tests that *prove the invariant* and tests that
*reveal invalid states the model still permits*.

---

## The two slogans, one idea

| Author / community | Slogan |
|---|---|
| Dijkstra | "The programmer's task is not to write a program but to derive it from the specification." Weakest-precondition calculus. |
| Hoare | `{P} S {Q}` — establish an invariant, prove the postcondition holds. |
| Bertrand Meyer | Design by Contract: preconditions, postconditions, class invariants. |
| Praxis / SPARK Ada | Industrial "Correctness by Construction" — eliminate errors before testing. |
| seL4 | Full functional-correctness proof from C implementation up to abstract spec. |
| Yaron Minsky | "Make illegal states unrepresentable." |
| Alexis King | "Parse, don't validate." |
| LangSec | "Full input recognition before processing." |

What unifies them: invariants belong in the *spec/type/contract*, not in
scattered runtime checks. Tests then either *prove* the invariant holds or
*search for inputs/states that violate it*.

---

## When defense-in-depth is the antipattern (collapse it)

The phrase is right — applied to internal program logic — when it means any
of these:

- **Repeated validation everywhere.** Controller checks `user_id != null`,
  service checks again, repository checks again, SQL has `WHERE … IS NOT
  NULL`. Each layer defends against the same failure mode.
- **Loose strings passed through the whole system.** `def send_email(addr:
  str)` re-parsed at every call site instead of carrying an `EmailAddress`
  type from the boundary inward.
- **Status enums duplicated across layers.** `OrderStatus` re-declared in
  the API DTO, the service, the repo, and the UI — each variant has to be
  mapped four times, every transition needs four tests, and adding a state
  silently misses one of the layers.
- **Catch-all retries.** `for _ in range(3): try ... except Exception: ...`
  hides a real failure inside an opaque retry loop instead of distinguishing
  retryable from non-retryable failures in the type.
- **Silent fallback behavior.** `get_user(id) or default_user()` hides the
  fact that the lookup failed; the postcondition "the returned user matches
  the request" is silently violated.
- **Post-hoc sanitizer patches.** A regex added "after the fact" to strip a
  bad character that never should have been representable in the first
  place.
- **Runtime guards instead of state machines / types / schema constraints.**
  `if order.status == "paid" and order.items: ...` is a state-machine
  transition expressed as ad-hoc if-statements; the model permits
  `Paid + empty items`, so every consumer must check.

In all six cases, every layer defends against the *same* failure mode. The
test surface explodes — every layer demands its own "rejects bad input" test
— and ownership of the invariant is unclear. The fix is to push the
invariant into a single structural form (type, smart constructor, sealed
enum, schema constraint) and delete the duplicates *and their tests*.

## When defense-in-depth is still necessary (keep all layers and all tests)

Defense-in-depth is the right model whenever the layers face *different*
failure modes or *different* threat models. Concretely:

- **Hostile input.** Untrusted bytes from network/users; the boundary parser
  is one layer, schema validation is another, runtime sanitization at the
  output is another.
- **Auth / security boundaries.** Authentication, authorization, tenancy
  isolation, audit logging — each defends against a distinct attack class.
- **SSRF / XSS / injection / secrets.** Output escaping, parameterized
  queries, content-security policy, secret-rotation, allowlists — the
  controls compose because they cover orthogonal vectors.
- **External system failure.** Timeouts, retries, circuit breakers, and
  fallbacks each handle a *different* downstream-failure regime.
- **Rate limits.** Application-level + edge + per-tenant limits each catch
  abuse the others miss.
- **Retries.** Idempotency keys + bounded retry + jittered backoff + dead-
  letter queue each guard a distinct failure path.
- **Observability.** Logs, metrics, traces, alerts — independent signals so
  one failure mode doesn't blind you to another.
- **Recovery and forensics.** Backups, replay logs, immutable audit trails —
  defenses against catastrophic loss and against tampering, respectively.

The rule, stated once:

> Defense-in-depth is virtue when each layer defends against a *different*
> failure mode or a *different* adversary. It is an antipattern when each
> layer defends against the *same* failure mode in a non-adversarial,
> already-typed context.

---

## The two tests that matter most

Once the invariant lives in the type/schema/contract, two test tactics
together do the heavy lifting. Most other tests can be deleted.

### A. Tests that *prove* the invariant

These are the runtime shadow of a Hoare triple `{P} S {Q}`. Property-based
testing is the practical mechanism: for any input satisfying the
precondition, assert the postcondition holds.

```python
@given(st.text())
def test_email_parser_proves_its_invariant(s):
    addr = EmailAddress.parse(s)
    if addr is None:
        return                                  # pre-condition not met
    assert "@" in addr.value                    # post-condition
    assert len(addr.value) <= 254
    assert addr == EmailAddress.parse(addr.value)  # idempotent
```

```python
@given(orders())
def test_order_state_machine_invariant(order):
    # Class invariant: a Paid order has at least one item.
    if order.status is OrderStatus.PAID:
        assert len(order.items) >= 1
    # Postcondition of cancel(): status becomes CANCELLED, items unchanged.
    cancelled = order.cancel()
    assert cancelled.status is OrderStatus.CANCELLED
    assert cancelled.items == order.items
```

These tests survive refactoring because they assert *what must always be
true*, not *what the implementation does today*. They're what tests look
like after the type system has done its job.

### B. Tests that *reveal invalid states the model still permits*

This is the adversarial twin. Your type or schema *claims* certain states
are impossible. Test that claim by trying to reach them. If you can, the
model is incomplete — fix the model, not the test.

This is the testing tactic the user community most often skips. It's the
single most useful audit you can run against a typed system.

**Caveat — weak runtime enforcement.** A tactic-B test that asserts
"this state is unconstructible" passes *trivially* if no mechanism
actually rejects it. Two cases to watch for:

1. **Go zero values.** `Email{}` constructs fine; the unexported-field
   trick only forces *outside* callers through `ParseEmail`. A tactic-B
   test on the zero value passes vacuously. Either add a `Valid() bool`
   method and exercise it with tactic-A tests, or document that the
   invariant is enforced by convention and is *not* tactic-B-testable.
2. **Dynamic languages without a constructor check.** If `Order(status,
   items)` is a plain dataclass with no `__post_init__`, you must add
   the runtime check first, then write the tactic-B test that exercises
   it. Writing the test against an unprotected constructor is worse than
   writing nothing — it documents a model that doesn't exist.

**Rule:** tactic B is only meaningful when a runtime or compile-time
mechanism *can* reject the state. If there isn't one, add one before
writing the test, or skip tactic B for that invariant and rely on the
boundary parser plus contract tests.

```python
def test_order_model_forbids_paid_empty():
    """The Order type claims `Paid + items=[]` is impossible. Prove it."""
    with pytest.raises((ValueError, TypeError)):
        Order(status=OrderStatus.PAID, items=[])
    # If this test passes by raising, the invariant is in the constructor.
    # If it fails because Order(...) returns successfully, the type is
    # too loose — fix Order to reject this state.
```

```rust
#[test]
fn user_id_zero_is_unrepresentable() {
    // We claim UserId cannot wrap 0. Try to make one and assert it fails.
    assert!(UserId::new(0).is_none());
    // If this ever passes by returning Some, the invariant has regressed.
}
```

For larger state spaces, use exhaustive enumeration (small enums,
booleans, short tuples) or property-based testing with shrinking:

```python
# Enumerate every (status, items_count) pair the type permits.
# For each, classify "should be valid" vs "should be invalid".
# Failures reveal model gaps.
@given(st.from_type(OrderStatus), st.integers(min_value=0, max_value=3))
def test_no_invalid_state_is_constructible(status, n):
    items = [Item("x") for _ in range(n)]
    invalid = (status is OrderStatus.PAID and n == 0)
    if invalid:
        with pytest.raises((ValueError, TypeError)):
            Order(status=status, items=items)
    else:
        Order(status=status, items=items)            # must succeed
```

When this test fails by *not* raising, you have found a hole in your model.
That is the entire point of the test.

A useful framing: type A tests are **"does the function obey its
contract?"**; type B tests are **"does the contract actually exclude what
we said it excludes?"** Both are necessary; neither is a "rejects null"
test repeated at every layer.

---

## Patterns by language

### TypeScript: branded types

```typescript
type EmailAddress = string & { readonly __brand: "EmailAddress" };

function parseEmail(raw: string): EmailAddress | null {
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(raw)) return null;
  if (raw.length > 254) return null;
  return raw as EmailAddress;
}

function sendEmail(address: EmailAddress) { /* no check needed */ }
```

Tests:
- A: PBT on `parseEmail` proves `valid-or-absent` and idempotence.
- B: `expect(() => sendEmail("not-an-address" as EmailAddress)).toBe(...)`
  is *unnecessary* — the unsafe cast is the only way to construct the bad
  state, so the gap is the cast itself. Document with a lint rule
  forbidding unbranded casts.

### Rust: newtype with private constructor

```rust
pub struct UserId(u64);

impl UserId {
    pub fn new(raw: u64) -> Option<Self> {
        if raw == 0 { None } else { Some(UserId(raw)) }
    }
    pub fn value(&self) -> u64 { self.0 }
}
```

Tests:
- A: PBT on `UserId::new` — `Some` outputs always have non-zero `value()`.
- B: An exhaustive boundary test — `UserId::new(0)` is `None`,
  `UserId::new(u64::MAX)` is `Some`. Document that any test asking
  "what if `lookup` is called with 0?" *cannot be written* — the call
  doesn't compile.

### Python: smart constructor with `__post_init__`

```python
@dataclass(frozen=True)
class NonEmptyList(Generic[T]):
    items: tuple[T, ...]

    def __post_init__(self):
        if not self.items:
            raise ValueError("NonEmptyList must have at least one item")

    @property
    def first(self) -> T:                # total — no Optional needed
        return self.items[0]
```

Tests:
- A: PBT — `NonEmptyList([x, *rest]).first == x`.
- B: `pytest.raises(ValueError) when NonEmptyList(())` and
  `NonEmptyList([])`. If either passes, the model is broken.

### Go: unexported field + constructor

```go
type Email struct{ s string }

func ParseEmail(raw string) (Email, error) { /* ... */ }
func (e Email) String() string { return e.s }
```

Tests:
- A: Table-driven test that for every valid input, `ParseEmail` returns an
  `Email` whose `String()` round-trips.
- B: Confirm `Email{}` outside the package compiles (it does — Go has no
  way to forbid the zero value), then write a *contract test* that any
  `Email` obtained by `ParseEmail` is non-empty. The gap is the zero
  value; documenting it is the test.

---

## Tests to delete after lifting invariants

After the invariant lives in the type/schema/contract, delete tests that:

1. Verify a downstream function "rejects" a value the type now forbids
2. Verify a "this should never happen" branch fires
3. Verify defaults that the type's constructor enforces
4. Verify the same `if x is None` guard that appears in five places
5. Verify a status-enum exhaustiveness check in every layer (the compiler
   does this once)

Coverage may drop. That is correct — you replaced runtime checks with
compile-time guarantees, and there is nothing left to cover.

## Tests to keep (and to add)

1. **One parser/constructor test per type at each trust boundary**, ideally
   property-based with `valid-or-absent` (`A`).
2. **Invariant-proof tests** on functions that operate on the type — Hoare
   triples expressed as PBT (`A`).
3. **Model-gap tests** that try to construct invalid states and assert they
   are rejected (`B`). When the test passes, the model holds. When it
   *fails by succeeding*, you found the gap.
4. **One contract test at every external boundary** — wire formats are
   untyped, so the guarantee must be re-erected at the boundary.

## Tests organized by trust boundary

| Boundary | Test | Why |
|---|---|---|
| HTTP body → DTO | Parser test (PBT) + contract test | Wire format is untyped |
| File / config → struct | Parser test + golden file | Disk is untyped |
| External API response → object | VCR cassette + parser test | Provider can change shape |
| DB row → entity | Repository test | Schema can drift from code |
| User input → form | Parser test + property test | Untrusted by definition |
| IPC / queue message → event | Pirate / contract test | Cross-process boundary |

Inside the boundary: `A` and `B` tests on the public interface. Nothing else.

---

## Interaction with the rest of this skill

| Skill rule | How correctness-by-construction sharpens it |
|---|---|
| Real objects > fakes > stubs > mocks | Mocks duplicate a contract; precise types eliminate the duplicate |
| PBT "valid-or-absent" pattern | This *is* parse-don't-validate as a test invariant (test type A) |
| Test data builders express intent | Best builders make illegal test data unconstructible (test type B applied to fixtures) |
| No unconditional skips | "This should never happen" tests are the same debt in reverse — promote to a type or delete |
| No "not empty" assertions | A precise return type makes the assertion structural, not defensive |
| Coverage as informational | After lifting invariants to types, coverage of deleted defensive code drops; that is success |

---

## Sources

- E. W. Dijkstra, *A Discipline of Programming* (1976) — weakest-precondition calculus, deriving programs from specifications
- C. A. R. Hoare, "An Axiomatic Basis for Computer Programming" (1969) — `{P} S {Q}`
- Bertrand Meyer, *Object-Oriented Software Construction* (1988/1997) — Design by Contract; Eiffel's preconditions, postconditions, invariants. ([Eiffel.com — Design by Contract](https://www.eiffel.com/values/design-by-contract/))
- Praxis / Altran, [Correctness by Construction (Chapman & Amey)](https://samate.nist.gov/SSATTM_Content/papers/Correctness%20by%20Construction%20-%20Chapman.pdf) and the SPARK Ada toolchain — industrial track record since 1990, used at DO-178B level A and Common Criteria EAL5+. The Tokeneer NSA project is the open case study.
- Klein et al., [seL4: Formal Verification of an OS Kernel (SOSP 2009)](https://www.sigops.org/s/conferences/sosp/2009/papers/klein-sosp09.pdf) — full functional-correctness proof of a microkernel, ~200K lines of Isabelle/HOL proof for ~8.7K lines of C
- Yaron Minsky, [Make Illegal States Unrepresentable](https://blog.janestreet.com/effective-ml-revisited/)
- Alexis King, [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)
- LangSec, [The Seven Turrets of Babel](https://langsec.org/papers/langsec-cwes-secdev2016.pdf) — full input recognition before processing; shotgun-parsing antipattern
- NIST SP 800-39 / SP 800-53 PL-8(1) — defense-in-depth as coordinated, mutually reinforcing controls across architectural layers ([CSRC glossary](https://csrc.nist.gov/glossary/term/defense_in_depth))
- NIST SP 800-82 — defense-in-depth applied to operational technology / ICS
- [Defence in depth (military doctrine, Wikipedia)](https://en.wikipedia.org/wiki/Defence_in_depth) — Roman/Byzantine origin; the strategy is to *delay* the attacker, not to redundantly verify a friendly signal

---

## One-line summary

Push invariants into types, schemas, and contracts; write tests that *prove*
the invariants and tests that *reveal invalid states the model still
permits*; delete the rest. Keep defense-in-depth where the layers face
different failure modes or different adversaries (hostile input, auth,
external systems, observability, recovery) — that is its real home.
