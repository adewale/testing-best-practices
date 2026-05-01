# Correctness by Construction (vs. Defense in Depth)

> Thesis: applied to *program logic*, defense-in-depth is an antipattern. The
> alternative — correctness-by-construction — has direct, concrete consequences
> for what tests we should and should not write.
>
> Date: 2026-04-30

---

## TL;DR

- **Defense-in-depth** is right where it came from: an *adversarial* doctrine
  for layered controls against hostile input, auth boundaries,
  SSRF/XSS/injection, external system failure, rate limits, retries,
  observability, recovery. Each layer defends a different failure mode or
  different adversary. (Roman/Byzantine military doctrine; NIST SP 800-39,
  800-53 PL-8(1), 800-82.)
- **Defense-in-depth becomes an antipattern** when transplanted inside a
  typed program: repeated validation everywhere, loose strings flowing
  through every layer, status enums duplicated across layers, catch-all
  retries, silent fallbacks, post-hoc sanitizer patches, runtime guards
  instead of state machines / types / schema constraints. Each layer
  defends the *same* failure in the *absence* of an adversary.
- **Correctness-by-construction** is the alternative — and it is older and
  more rigorous than the modern "parse, don't validate" framing alone
  suggests. The lineage runs Hoare → Dijkstra → Meyer → Praxis/SPARK →
  seL4 → Minsky → King → LangSec. The shared move: lift the invariant into
  the spec, type, contract, or schema so the wrong state is unrepresentable.
- **The two tests that survive** when invariants live in the type:
  (A) tests that *prove* the invariant for all valid inputs (PBT — Hoare
  triple at runtime), and (B) tests that *try to construct each forbidden
  state and assert the construction fails* — if it succeeds, the model has
  a hole. (B) is the test most often missing.
- This reframes several practices already in this skill — *real objects
  over mocks*, *test data builders*, *property-based testing's
  "valid-or-absent" pattern*, *no-skipped-tests* — as facets of a single
  principle.

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

The lineage is older, more rigorous, and more industrially proven than the
modern "parse, don't validate" framing alone suggests. The same idea has been
re-discovered and re-named by every generation of practitioners since the
1960s:

| Year | Author / community | Slogan / contribution |
|---|---|---|
| 1969 | C. A. R. Hoare | `{P} S {Q}` — pre/postconditions and invariants as the unit of program reasoning |
| 1976 | E. W. Dijkstra, *A Discipline of Programming* | Weakest-precondition calculus; "derive the program from the spec" |
| 1986 | Bertrand Meyer | Design by Contract: preconditions, postconditions, class invariants encoded in Eiffel |
| 1990s–today | Praxis (Altran) + AdaCore | Industrial "Correctness by Construction" using SPARK Ada; track record at DO-178B level A and Common Criteria EAL5+; Tokeneer (NSA) is the open case study |
| 2009 | Klein et al., seL4 | First full functional-correctness proof of a general-purpose OS kernel — ~200K lines of Isabelle/HOL proof for ~8.7K lines of C |
| 2014 | Yaron Minsky | "Make illegal states unrepresentable" |
| 2019 | Alexis King | "Parse, don't validate" |
| 2016+ | LangSec community | "Full input recognition before processing"; *shotgun parsing* as the antipattern |

The shared move: **lift the invariant into the spec, type, contract, or
schema.** Once `EmailAddress` exists as a type whose only constructor is the
parser, no function downstream needs to "check whether this string is an
email." It already is one. The same move at industrial scale is what lets
Praxis ship avionics with order-of-magnitude lower defect rates than
test-driven shops, and what lets seL4 be invulnerable to entire categories
of bugs by construction rather than by patching.

Yaron Minsky's claim is the testing-relevant one:

> "Making the wrong thing hard to express is better than checking for the
> wrong thing at runtime."

That is a claim about *where the check lives*, and therefore about *where
the test lives*.

### The "defense in depth" the principle is *not* attacking

Defense-in-depth has a long, legitimate pedigree the testing critique must
respect. The military doctrine ([Defence in
depth](https://en.wikipedia.org/wiki/Defence_in_depth)) goes back to Roman
and Byzantine strategy and is faithfully preserved in NIST's cybersecurity
formulation ([SP 800-39, SP 800-53
PL-8(1)](https://csrc.nist.gov/glossary/term/defense_in_depth), [SP
800-82](https://nvlpubs.nist.gov/) for OT/ICS):

> "Organizations strategically allocate security and privacy controls in
> the security and privacy architectures so that adversaries must overcome
> multiple controls to achieve their objective."

The defining feature in both military and security versions is an
**adversary** and **independent failure modes**. A WAF, parameterized
queries, output escaping, and CSP defend against orthogonal attack
classes. Removing any one leaves a real residual risk against a real
adversary.

The phrase only becomes an antipattern when it is *transplanted* — without
the adversary, without the orthogonal failure modes — into the inside of a
typed program where each layer "defends" against the same failure mode that
its neighbors already catch. Then it is shotgun parsing wearing the
costume of a security strategy.

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

## 4. The sharp boundary: when each side applies

### "Defense in depth is an antipattern" is right when it means

- **Repeated validation everywhere** — the same `is None` / `!= ""` /
  `len > 0` check at every layer
- **Loose strings passed through the whole system** — `addr: str` flowing
  controller → service → repo → SQL, re-validated at each step, instead of
  an `EmailAddress` lifted at the boundary
- **Status enums duplicated across layers** — `OrderStatus` redeclared in
  the API DTO, the service, the repo, and the UI, each with its own
  mapping tests
- **Catch-all retries** — `for _ in range(3): try: ... except Exception:`
  hiding both *what* failed and *whether it should have been retried*
- **Silent fallback behavior** — `lookup() or default()` masking the
  failure of the primary path
- **Post-hoc sanitizer patches** — a regex stripping a character that
  should never have been representable upstream
- **Runtime guards instead of state machines, types, or schema constraints**
  — `if order.status == "paid" and order.items: ...` re-deriving an
  invariant on every read

In each, every layer defends against the *same* failure in the *absence* of
an adversary. The test surface explodes because every layer demands its own
"rejects bad input" test. Collapse it: one parser at the boundary, one
type, no duplication.

### Defense in depth is still necessary for

- **Hostile input** — boundary parser + schema validation + output
  sanitization are independent layers against a real adversary
- **Auth / security boundaries** — authentication, authorization, tenancy
  isolation, audit logging
- **SSRF / XSS / injection / secrets** — output escaping, parameterized
  queries, content-security policy, secret rotation, allowlists
- **External system failure** — timeouts, retries, circuit breakers,
  fallbacks each handle a *different* downstream-failure regime
- **Rate limits** — application-level + edge + per-tenant
- **Retries** — idempotency keys + bounded retry + jittered backoff +
  dead-letter queue
- **Observability** — logs, metrics, traces, alerts as independent signals
  so one failure mode doesn't blind you to another
- **Recovery and forensics** — backups, replay logs, immutable audit
  trails

In each, layers face *different* failure modes or *different* adversaries.
Removing any one leaves real residual risk. Tests for each layer are not
redundant — they exercise different failures.

### The rule in one line

> Defense-in-depth is virtue when each layer defends against a *different*
> failure mode or a *different* adversary. It is an antipattern when each
> layer defends against the *same* failure mode in a non-adversarial,
> already-typed context.

---

## 4a. The two tests that survive

Once invariants are in the type/schema/contract, two test tactics together
do most of the work that scattered defensive tests used to do — and do it
better. Most projects have only the first; the second is the highest-yield
practice the testing literature underweights.

### Tactic A — Tests that *prove* the invariant

The runtime shadow of `{P} S {Q}`. For any input satisfying the
precondition, the postcondition holds. Property-based testing is the
practical mechanism.

```python
@given(orders())
def test_cancel_invariant(order):
    cancelled = order.cancel()
    assert cancelled.status is OrderStatus.CANCELLED   # postcondition
    assert cancelled.items == order.items              # postcondition
    # Class invariant survives the operation
    if cancelled.status is OrderStatus.PAID:
        assert len(cancelled.items) >= 1
```

These tests survive refactoring because they assert *what must always be
true*, not *what the implementation does today*. They are, in effect, Hoare
triples evaluated at runtime against sampled inputs.

### Tactic B — Tests that *reveal invalid states the model still permits*

The adversarial twin. The type or schema *claims* certain states are
impossible. Test that claim by trying to reach them. If you can, the model
is incomplete — fix the model, not the test.

```python
def test_order_model_forbids_paid_empty():
    """The model claims `Paid + items=[]` is impossible. Prove it."""
    with pytest.raises((ValueError, TypeError)):
        Order(status=OrderStatus.PAID, items=[])
```

For larger state spaces, exhaustively enumerate over small enums and
short tuples, or use property-based testing with shrinking:

```python
@given(st.from_type(OrderStatus), st.integers(min_value=0, max_value=3))
def test_no_invalid_state_is_constructible(status, n):
    items = [Item("x") for _ in range(n)]
    invalid = (status is OrderStatus.PAID and n == 0)
    if invalid:
        with pytest.raises((ValueError, TypeError)):
            Order(status=status, items=items)
    else:
        Order(status=status, items=items)         # must succeed
```

**This is the test most often missing.** Tactic A says "the function is
correct given the contract." Tactic B says "the contract actually
excludes what we claim it excludes." Without B, a regression that loosens
the model — a developer relaxing a constructor check, removing an enum
variant constraint, weakening a schema — goes undetected. The model
silently drifts back toward shotgun parsing, and the test suite is
silent because it was never asking the right question.

A useful framing:

| Tactic | Question it answers |
|---|---|
| A | Does the function obey its contract? |
| B | Does the contract actually exclude what it claims to exclude? |
| (Old defensive tests) | Does layer N catch the invalid input layer N-1 already caught? |

A and B together replace the third class entirely.

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

### The lineage of correctness-by-construction

- C. A. R. Hoare, "An Axiomatic Basis for Computer Programming" (CACM, 1969)
  — the `{P} S {Q}` triple
- E. W. Dijkstra, *A Discipline of Programming* (1976) and "Guarded
  commands, nondeterminacy and formal derivation of programs" — weakest
  precondition calculus; deriving programs from specs ([UMD course
  handout](https://www.cs.umd.edu/~mvz/handouts/weakest-precondition.pdf))
- Bertrand Meyer, *Object-Oriented Software Construction* (1988/1997) and
  ["Applying Design by
  Contract"](https://www.kth.se/social/files/59526bfb56be5b4f17000807/meyer-92-contracts.pdf)
  — preconditions, postconditions, class invariants in Eiffel
- Praxis (Altran) + AdaCore, [Correctness by Construction (Chapman, NIST
  paper)](https://samate.nist.gov/SSATTM_Content/papers/Correctness%20by%20Construction%20-%20Chapman.pdf)
  and the SPARK Ada toolchain — industrial track record since 1990; DO-178B
  level A, Common Criteria EAL5+; the open Tokeneer NSA case study
- Klein et al., [seL4: Formal Verification of an OS Kernel (SOSP
  2009)](https://www.sigops.org/s/conferences/sosp/2009/papers/klein-sosp09.pdf)
  — first machine-checked functional-correctness proof of a general-purpose
  OS kernel
- Yaron Minsky, [Effective
  ML](https://blog.janestreet.com/effective-ml-revisited/) — the
  "make illegal states unrepresentable" formulation
- Scott Wlaschin, [Designing with types: Making illegal states
  unrepresentable](https://fsharpforfunandprofit.com/posts/designing-with-types-making-illegal-states-unrepresentable/)
- Alexis King, [Parse, don't
  validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)
  (2019) — the modern programmer's gloss
- LangSec, [The Seven Turrets of Babel: A Taxonomy of LangSec
  Errors](https://langsec.org/papers/langsec-cwes-secdev2016.pdf) — full
  input recognition before processing; shotgun parsing as the antipattern
- Edwin Brady, [Type-Driven Development with
  Idris](https://www.manning.com/books/type-driven-development-with-idris)
  — "type, define, refine"

### Defense-in-depth as a legitimate doctrine

- [Defence in depth (Wikipedia)](https://en.wikipedia.org/wiki/Defence_in_depth)
  — Roman/Byzantine military origin; the strategy is to *delay* the attacker
- NIST SP 800-39, SP 800-53 PL-8(1) — defense-in-depth as coordinated,
  mutually reinforcing controls across architectural layers
  ([CSRC glossary](https://csrc.nist.gov/glossary/term/defense_in_depth);
  [PL-8(1)](https://csf.tools/reference/nist-sp-800-53/r5/pl/pl-8/pl-8-1/))
- NIST SP 800-82r3 — defense-in-depth applied to operational technology /
  ICS environments
- CISA, [Recommended Practice: Defense in
  Depth](https://www.cisa.gov/sites/default/files/recommended_practices/NCCIC_ICS-CERT_Defense_in_Depth_2016_S508C.pdf)

### Critique of defensive programming

- Hacker News, ["This should never happen" is a design pattern of
  defensive programming](https://news.ycombinator.com/item?id=11396438)
- Ilya Priven, [Defensive Programming
  Anti-Patterns](https://medium.com/@ikonst/defensive-programming-anti-patterns-9ae0d6958fe2)
- Hillel Wayne, [Formal methods writing](https://www.hillelwayne.com/tags/formal-methods/)

---

## 7. One-paragraph version

Push invariants into types, schemas, and contracts at the outermost trust
boundary. Delete the scattered downstream checks and the tests that only
existed because those checks did. Replace them with two tests: (A) a
property-based test that *proves* the invariant holds for all inputs
satisfying the precondition, and (B) a test that *tries to construct each
invalid state the model claims to forbid* — if construction succeeds, the
model has a hole. Keep defense-in-depth where the layers face different
failure modes or different adversaries: hostile input, auth and security
boundaries, SSRF/XSS/injection/secrets, external system failure, rate
limits, retries, observability, recovery and forensics. Reject it where
every layer defends against the same failure mode in a non-adversarial,
already-typed context — that is shotgun parsing in slow motion.
