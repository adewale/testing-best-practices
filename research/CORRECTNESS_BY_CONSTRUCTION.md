# Correctness by Construction (vs. Defense in Depth)

> Thesis: applied to *program logic*, defense-in-depth is an antipattern. The
> alternative — correctness-by-construction — has direct, concrete consequences
> for what tests we should and should not write.
>
> Date: 2026-04-30

---

## TL;DR

- **Defense-in-depth** is the right model across *trust boundaries* (network, OS,
  persistence, untrusted user input). Multiple independent controls defend
  against multiple independent threat models.
- **Defense-in-depth** is the wrong model *inside* a trust boundary, where the
  same invariant is re-checked at every layer "just in case." This is shotgun
  parsing dressed up as virtue. It bloats code, hides ownership of the
  invariant, and — most relevant here — **explodes the test surface**.
- **Correctness-by-construction** says: encode the invariant in the type or the
  shape of the data so that the wrong state is *unrepresentable*. Then there is
  exactly one place to test it (the parser at the boundary), and every
  downstream consumer is correct for free.
- This reframes several practices already in this skill — *real objects over
  mocks*, *test data builders*, *property-based testing's "valid-or-absent"
  pattern*, *no-skipped-tests* — as facets of a single principle.

---

## 1. What "defense in depth" means in the two contexts

The phrase has two distinct lives that are routinely conflated.

**Security defense-in-depth** is sound. A web application uses a WAF *and*
parameterized queries *and* least-privilege DB users *and* output escaping.
Each layer defends against a *different* failure mode and a *different*
threat actor. Removing any one layer leaves a real residual risk.

**Logical defense-in-depth** is the practice — usually unconscious — of
re-validating the same invariant at every internal layer of an application:
the controller checks `user_id != null`, the service checks it again, the
repository checks it again, the SQL has a `WHERE user_id IS NOT NULL`, and
there is a `CHECK` constraint on the column. None of these layers defends
against a different failure. They all defend against the *absence of a type
that says "this value is a UserId."*

The first is engineering. The second is what Alexis King and the LangSec
community call **shotgun parsing**: "parsing and input-validating code is mixed
with and spread across processing code… late-discovered errors in an input
stream will result in some portion of invalid input having been processed."
([Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/);
[LangSec taxonomy](https://langsec.org/papers/langsec-cwes-secdev2016.pdf).)

The test-relevant rule:

> Defense-in-depth is virtue when each layer defends against a *different*
> failure mode. It is an antipattern when each layer defends against the
> *same* failure mode.

---

## 2. The correctness-by-construction alternative

Three formulations, each by a different community, point at the same idea.

| Author | Slogan | Domain |
|---|---|---|
| Alexis King | "Parse, don't validate" | Functional programming / Haskell |
| Yaron Minsky | "Make illegal states unrepresentable" | OCaml / typed FP |
| Edwin Brady | "Type, define, refine" (vs. "red, green, refactor") | Dependent types / Idris |
| Tony Hoare | "So simple that there are obviously no bugs" | General |
| LangSec | "Full recognition before processing" | Security |

The shared move: **lift a runtime check into a structural property of the
data**. Once `EmailAddress` exists as a type whose only constructor is the
parser, no function downstream needs to "check whether this string is an
email." It already is one. ([Make Illegal States
Unrepresentable](https://functional-architecture.org/make_illegal_states_unrepresentable/);
[F# for fun and profit](https://fsharpforfunandprofit.com/posts/designing-with-types-making-illegal-states-unrepresentable/).)

Yaron Minsky's claim in particular is the testing-relevant one:

> "Making the wrong thing hard to express is better than checking for the
> wrong thing at runtime."

That is a claim about *where the check lives*, and therefore about *where the
test lives*.

---

## 3. The concrete effect on tests

This is where the principle stops being philosophy and starts changing what we
write into test files.

### 3.1 Tests for "what if X is null/empty/invalid?" disappear when X has a precise type

Defense-in-depth, in tests, looks like this:

```python
def test_send_email_rejects_empty_string():     ...
def test_send_email_rejects_missing_at_sign():  ...
def test_send_email_rejects_too_long():         ...
def test_send_email_rejects_unicode_homoglyph(): ...
# …repeated for every function that takes an email address
```

Correctness-by-construction collapses this to a single test on the parser:

```python
class EmailAddress:
    def __init__(self, raw: str): ...     # raises on invalid

@given(st.text())
def test_email_parser_is_valid_or_absent(s):
    try:
        addr = EmailAddress(s)
    except InvalidEmail:
        return
    assert "@" in addr.value           # invariant of the type
    assert len(addr.value) <= 254
```

Every downstream `send_email(addr: EmailAddress)` is now correct *by
construction* — the type system rejects the invalid call at compile time (or
at the constructor for dynamic languages). The downstream tests no longer
need to enumerate invalid inputs, because invalid inputs cannot reach the
function.

This is **exactly** the property-based testing pattern already documented in
this repo as "valid-or-absent" (see `DECISION_TREE.md`,
`testing-best-practices/SKILL.md` §4). The pattern *is* parse-don't-validate,
expressed as a test invariant.

### 3.2 "This should never happen" tests are confessions about your types

The Hacker News
[discussion](https://news.ycombinator.com/item?id=11396438) of the "this
should never happen" pattern observes that the assertion is "used to catch
errors caused by misuse of a method, when there's an invariant that the method
assumes but is not enforced by the type signature."

In test form, this looks like:

```go
func TestWidget_NeverNegativeAfterInit(t *testing.T) {
    w := NewWidget()
    if w.count < 0 {                       // "this should never happen"
        t.Fatalf("count went negative: %d", w.count)
    }
}
```

If `count < 0` is genuinely impossible, the test exists only because the type
permits it. The fix is not to keep the test — the fix is to make `count` a
`uint`, or wrap it in a smart-constructor type that rejects negatives, and
*delete the test*. The test was a placeholder for a missing invariant in the
type.

This connects to antipattern #6 in `ANTIPATTERNS.md` ("Skipped Tests Without
Expiry"). The same rule applies in reverse: tests for impossible states are
the dual of skipped tests for required states. Both are debt; both should be
either promoted to a real check or deleted.

### 3.3 Test data builders should make illegal test data unrepresentable

Test data builders (`make-it-easy`, factory_boy, fixture factories) are
already in the skill. Correctness-by-construction tightens the rule.

Bad: builder defaults to invalid state, every test must remember to override.

```python
user = UserFactory.build()                # role = None, email = None
user.role = "admin"                       # forced to fix it in every test
user.email = "x@y.z"
```

Good: builder defaults to a valid object; tests override only what they care
about.

```python
user = UserFactory.build(role="admin")    # email already valid
```

Best: builder *cannot construct an invalid object*. If `User` requires a
`Role` enum and `EmailAddress`, the builder cannot omit them. The compiler
(or `__init__`) enforces it.

The signature is the test. The builder cannot be misused; therefore no test
needs to assert "user with no role rejects login" — there are no users with
no role.

### 3.4 Mocks are defensive doubles; types let you trust the real thing

The skill already prefers real objects over mocks
(`SKILL.md` §3). The deeper reason is correctness-by-construction:

- A mock is a **defensive layer** introduced because we don't trust that the
  real collaborator will behave. We re-state its contract in the test.
- The contract restated in the mock can drift from the real contract
  (antipattern #1: Mock-Reality Drift).
- A real in-memory collaborator with a precise type signature gives us the
  same isolation *without* a separate, drift-prone copy of the contract.

The hierarchy in §3 of `SKILL.md` (real → fake → stub → mock) is, read this
way, a hierarchy of *how much defensive duplication you tolerate*. Real
objects = zero. Framework mocks = full duplication of the API surface, with
no compiler keeping it honest.

### 3.5 Property-based tests are correctness-by-construction in test form

Example tests are inherently defensive: enumerate inputs, assert outputs,
hope you covered the cases. Property-based tests assert an *invariant* —
"for all inputs of this shape, this property holds" — which is the same
shape of statement as a type signature.

The nine invariant patterns in `SKILL.md` §4 each map onto a constructive
guarantee:

| PBT invariant | Constructive equivalent |
|---|---|
| Never crashes on arbitrary input | Total function |
| Roundtrip `decode(encode(x)) == x` | Bijection between types |
| Idempotent `f(f(x)) == f(x)` | Projection / normal form |
| Conservation (output ⊆ input) | Refinement type |
| Valid-or-absent | `Maybe T` / `Result T E` return |
| Associative / commutative / distributive | Algebraic structure |

When you write a property test, you are asserting a structural fact about the
function. That fact could, in a sufficiently expressive type system, be the
type. The property test is the runtime shadow of the type you wish you had.

### 3.6 Stop testing redundant defensive checks

If the controller, service, and repository all reject `null user_id`, only
*one* of those checks is the "real" one — the one closest to the trust
boundary. The other two are dead weight. Tests for the dead weight are also
dead weight, and worse: they make the dead weight load-bearing in the test
suite, which means deleting it (the right move) breaks tests, which means
nobody deletes it.

Audit rule:

> For each defensive check you find, ask: *what fails if I delete this and
> rely on the upstream check?* If the answer is "nothing — the upstream check
> already catches it," delete both the check and its test. If the answer is
> "the upstream check doesn't actually catch it," fix the upstream check —
> don't keep the downstream one.

This is the same instinct as antipattern #4 (Integration Tests That Mock
Their Integration Points): a layer that doesn't add information is a layer
that doesn't deserve a test.

---

## 4. When defense-in-depth in tests *is* warranted

The principle has a sharp boundary. Defense-in-depth tests pay their cost
when the layers defend against *different, independent* failure modes. The
clearest cases:

**Trust boundaries.** A `UserId` type guarantees the value is a valid id
*inside* the application. It does not guarantee the database row still
exists, that the user has not been deleted, or that the request is
authorized. Tests for those are not redundant — they cover different failures.

**Cross-language / cross-process contracts.** When your Python code calls a
TypeScript service over HTTP, the TS type system gives you nothing. Mock
fidelity tests, contract tests, and VCR cassettes (already in the skill) are
correctness-by-construction *re-erected* at the boundary where types stop
working.

**Security-in-depth.** Input sanitization, output escaping, parameterized
queries, and CSP each defend against a distinct attack class. Tests for each
are not redundant.

**Independent failure modes.** A retry tests a different failure (transient
network) than a circuit breaker (sustained downstream failure) than a
fallback (degraded response). All three deserve tests.

The invariant: *if removing one layer would expose a real risk that the other
layers do not catch, the layer earns its test.*

---

## 5. Where this lands in the existing skill

This is not a new principle to bolt on. It is the reason several existing
rules are correct, restated.

| Existing rule | Underlying principle |
|---|---|
| Real objects > fakes > stubs > mocks (§3) | Avoid defensive duplication of contracts |
| Property-based "valid-or-absent" (§4) | Parse, don't validate, in test form |
| Test data builders express intent (§9) | Make illegal test data unrepresentable |
| No unconditional skips (`ANTIPATTERNS.md` #6) | Don't accumulate "this can't happen" tests |
| No "not empty" assertions (`ANTIPATTERNS.md` #3) | Test the structural property, not a defensive shadow |
| Coverage as informational, not blocking (§2) | Belt-and-suspenders coverage produces antipattern #11 |
| Tier integrity (`SKILL.md` Step 4) | Each test tier should defend against a *different* failure mode |

### Suggested additions when this gets folded into the skill

1. **A new `references/correctness-by-construction.md`** loaded when the
   project uses a typed language with smart constructors / branded types /
   newtypes (Rust, TypeScript, OCaml, Haskell, Scala, modern Kotlin/Swift).
   Contents: how to lift invariants into types, when to delete tests in
   favor of types, smart-constructor patterns per language.

2. **A new entry #13 in `ANTIPATTERNS.md`: "Logical Defense-in-Depth /
   Shotgun Validation."** Detection signal: same invariant checked at three
   or more layers; same invariant tested at three or more layers. Fix: lift
   to a type at the outermost trust boundary; delete the inner checks and
   their tests.

3. **An audit step in Assess mode (`SKILL.md` §Step 4 or new Step 7):**
   *"For each defensive check, identify the trust boundary it defends. If two
   tests defend the same invariant at the same trust boundary, one of them is
   debt."*

4. **A line in the validation loop (§Write mode):**
   *"After writing tests for a function, ask whether any test exists only
   because the function's signature is too loose. If yes, tighten the
   signature and delete the test."*

---

## 6. Sources

- Alexis King, [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) (2019)
- Yaron Minsky, [Effective ML (OCaml.org / Jane Street)](https://blog.janestreet.com/effective-ml-revisited/), and the popular gloss [Make Illegal States Unrepresentable](https://functional-architecture.org/make_illegal_states_unrepresentable/)
- Scott Wlaschin, [Designing with types: Making illegal states unrepresentable](https://fsharpforfunandprofit.com/posts/designing-with-types-making-illegal-states-unrepresentable/)
- LangSec, [The Seven Turrets of Babel: A Taxonomy of LangSec Errors and How to Expunge Them](https://langsec.org/papers/langsec-cwes-secdev2016.pdf)
- Edwin Brady, [Type-Driven Development with Idris](https://www.manning.com/books/type-driven-development-with-idris) — "type, define, refine"
- Hillel Wayne, [tag: formal methods](https://www.hillelwayne.com/tags/formal-methods/) — formal-methods framing of correct-by-construction
- Hacker News, ["This should never happen" is a design pattern of defensive programming](https://news.ycombinator.com/item?id=11396438)
- Ilya Priven, [Defensive Programming Anti-Patterns](https://medium.com/@ikonst/defensive-programming-anti-patterns-9ae0d6958fe2)

---

## 7. One-paragraph version

A test that exists because the type is too loose is debt, not coverage. Push
the invariant into the type at the outermost trust boundary; delete the
downstream checks and their tests. Keep defense-in-depth where the layers
defend against *different* failure modes (security, cross-process boundaries,
independent transient faults). Reject it where every layer defends against
the same failure — those layers, and their tests, are shotgun parsing in slow
motion.
