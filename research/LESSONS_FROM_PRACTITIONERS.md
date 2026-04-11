# Lessons from Testing Practitioners

> Extracted from scanning repos by npryce (Nat Pryce), joewalnes (Joe Walnes), bradfitz (Brad Fitzpatrick), graydon (Graydon Hoare), karpathy (Andrej Karpathy), ivanmoore (Ivan Moore), and tirsen (Jon Tirsen).
> Date: 2026-04-11

---

## Table of Contents

1. [Who These People Are](#who-these-people-are)
2. [Testing Libraries and Frameworks Created](#testing-libraries-created)
3. [Property-Based and Exhaustive Testing](#property-based-and-exhaustive-testing)
4. [Fuzz Testing](#fuzz-testing)
5. [Test Data Builders](#test-data-builders)
6. [Testing Asynchronous Systems](#testing-asynchronous-systems)
7. [Reference Implementation Testing](#reference-implementation-testing)
8. [Fake Server Testing](#fake-server-testing)
9. [Minimalist Testing Frameworks](#minimalist-testing-frameworks)
10. [Test Lifecycle Management](#test-lifecycle-management)
11. [TDD Teaching Patterns](#tdd-teaching-patterns)
12. [Key Insights by Practitioner](#key-insights-by-practitioner)

---

## Who These People Are

| Person | Significance | Key Testing Contribution |
|--------|-------------|-------------------------|
| **Nat Pryce** | Co-author of "Growing Object-Oriented Software, Guided by Tests" (GOOS), co-created jMock, Hamcrest | Property testing (factcheck), fuzz testing (snodge), test data builders (make-it-easy), test lifecycle (worktorule) |
| **Joe Walnes** | Created WebSocket protocol implementation, SiteMesh, XStream | Minimalist testing frameworks (jstinytest, tinytest) |
| **Brad Fitzpatrick** | Go core team member, created memcached, LiveJournal | Fake server testing, protocol-level integration tests |
| **Graydon Hoare** | Created the Rust programming language | Exhaustive testing (exhaustigen-rs), property test interop (proptest-arbitrary-interop) |
| **Andrej Karpathy** | AI researcher, created nanoGPT, micrograd, llm.c | Reference implementation testing (PyTorch as oracle) |
| **Ivan Moore** | XP practitioner, refactoring expert | TDD katas, mock objects exercises, refactoring golf |
| **Jon Tirsen** | ThoughtWorks alum, testing/agile practitioner | Retry patterns, database tooling |

---

## Testing Libraries and Frameworks Created

These practitioners didn't just use testing tools — they created them. Each library embodies a specific testing philosophy.

### Hamcrest (npryce, with Steve Freeman)

The matcher library used across Java, Python, Swift, Kotlin, and more. Key insight: **assertions should read like sentences**.

```java
assertThat(cheese.name(), equalTo("Wensleydale"));
assertThat(result, is(not(empty())));
assertThat(items, hasItem(with(name("Widget"))));
```

**hamkrest** (Kotlin port) continues this philosophy with Kotlin idioms.

### python-factcheck (npryce)

A QuickCheck implementation by the GOOS co-author. Notable for:
- **Boundary-first generation**: generators yield boundary values (min, max) before random values
- **`@forall` decorator** that integrates naturally with pytest
- **`where` clause** for input filtering (preconditions)
- **Fixed sequences with cycling** for exhaustive-then-random testing

```python
@forall(l=lists(lengths=ints(min=2,max=4), elements=ints(min=10,max=20)))
def test_lists_generates_bounded_lists(l):
    assert 2 <= len(l) <= 4
    assert all(10 <= e <= 20 for e in l)

@forall(x=range(4), y=range(4), where=lambda x, y: x != y)
def test_can_filter_inputs(x, y):
    assert x != y
```

**Design decision**: Boundary values are yielded first, then shuffled into the random stream. This ensures edge cases are always tested first, with the remaining runs exploring the space randomly.

### snodge (npryce)

A fuzz testing library for JSON, XML, HTML forms, text, and binary data. Instead of generating random data from scratch, it **mutates known-good data**.

Key testing targets snodge is designed for:
- Unexpected structures don't cause unchecked exceptions
- Application code ignores additional properties
- Application doesn't throw on parsing values from text properties
- Application doesn't instantiate arbitrary classes named in data (security)
- Application copes with invalid Unicode encoding

```kotlin
random.mutants(defaultJsonMutagens().forStrings(), 10, originalJson)
    .forEach(::println)
// Output: randomly mutated versions of the original JSON
```

**Lesson**: Mutation-based fuzzing is more effective than random generation for structured data, because it starts from valid input and makes targeted, plausible changes.

### make-it-easy (npryce)

A Test Data Builder framework that reduces boilerplate:

```java
// Fluent builder API:
Maker<Apple> ripeApple = an(Apple, with(ripeness, 0.9), with(leaves, 3));
Apple apple = make(ripeApple);

// Reusable with overrides:
Maker<Apple> unripeApple = ripeApple.but(with(ripeness, 0.1));
```

**Lesson from GOOS**: Test data builders should express the *intent* of the data, not its structure. `with(ripeness, 0.9)` tells you what matters; `new Apple(3, 0.0, 0.9, "red")` tells you nothing.

### worktorule (npryce)

Test lifecycle management by correlating test failures with issue tracker state:

```java
@Rule public TestRule ignoreInProgress = new IgnoreInProgress(
    new GitHubIssues("example-org", "example-project"));

@Test
@InProgress("42")  // GitHub issue #42
public void new_feature_under_development() {
    // Fails? Skip if issue #42 is still open.
    // Fails after issue #42 is closed? Actual test failure.
}
```

**Lesson**: Acceptance tests written before the feature exists should be tracked as "in progress," not skipped. When the corresponding issue is closed, the test automatically becomes a regression test.

---

## Property-Based and Exhaustive Testing

### exhaustigen-rs (graydon)

Graydon Hoare (creator of Rust) built an **exhaustive testing** library — not random testing, but testing *every possible combination* within bounds.

```rust
let mut gen = Gen::new();
while !gen.done() {
    let elts = gen.gen_elts(3, 4).collect::<Vec<_>>();
    // Tests EVERY combination: 0-3 elements, each 0-4
    // Total: (5^3) + (5^2) + 5 + 1 = 156 combinations
}
```

The key insight: **the generator tracks its progress through the state space and lazily extends it**. This means:
- Nested value-dependent generation works correctly (generate K, then generate J in 0..K)
- Every path through the code is explored
- The state space is enumerated automatically without the test author calculating it

**Available generators**:
- `gen(bound)` — scalar in 0..bound
- `flip()` — boolean
- `pick(slice)` — element from array
- `gen_elts(len, val)` — variable-length sequences
- `gen_comb(input)` — combinations
- `gen_perm(input)` — permutations (all N!)
- `gen_subset(input)` — all 2^N subsets

**Lesson**: Exhaustive testing is the gold standard when the state space is small enough. For a 5-element array, `gen_perm` tests all 120 permutations — no sampling bias, no missed cases.

### proptest-arbitrary-interop (graydon)

Bridges the gap between `arbitrary::Arbitrary` (used for fuzzing) and `proptest::Strategy` (used for property testing):

```rust
use proptest_arbitrary_interop::arb;

proptest! {
    #[test]
    fn always_red(color in arb::<Rgb>()) {
        prop_assert!(color.g == 0 || color.r > color.g);
    }
}
```

**Lesson**: If you implement `Arbitrary` for fuzzing, you get property tests for free with this interop. Write the data generator once, use it for both fuzzing and property testing.

### factcheck Boundary-First Design (npryce)

```python
def ints(min=None, max=None):
    """Yield boundary values first, then random."""
    return chain(
        _actual([min, max]),  # Yield min, max FIRST
        _random_values(random.randint, min, max)  # Then random
    )
```

**Lesson**: Always test boundaries before random values. This is why both `factcheck` (npryce) and `qc` (adewale) share this design — it catches the most bugs per test iteration.

---

## Fuzz Testing

### Mutation-Based Fuzzing (snodge)

snodge's approach: take valid input, randomly mutate it, verify the system doesn't crash.

Supported mutation types:
- JSON: add/remove/replace properties, change types, add null/empty values
- XML: mutate attributes, text content, element structure
- HTML forms: mutate field names, values, add/remove fields
- Text: corrupt Unicode, insert special characters
- Binary: flip bits, truncate, extend

**When to use mutation-based fuzzing** (from snodge):
- You have known-good example data
- You want to test error handling and graceful degradation
- You want to find security issues (arbitrary class instantiation, injection)
- You want to verify the system ignores unknown properties

**When to use generation-based fuzzing** (Hypothesis, fast-check):
- You need to test invariants across the full input space
- You want shrinking (minimal failing examples)
- You need structured data with complex constraints

---

## Test Data Builders

### The GOOS Pattern (npryce)

From _Growing Object-Oriented Software, Guided by Tests_:

1. **Builder pattern**: Create objects with sensible defaults, override only what the test cares about
2. **Intent-revealing names**: `a(ripeApple)` not `new Apple(3, 0.9, "red")`
3. **Composition**: `ripeApple.but(with(leaves, 5))` — build on existing builders

**make-it-easy** reduces the boilerplate of the GOOS pattern from ~30 lines per builder to ~5 lines.

### Comparison Across Repos

| Repo | Pattern | Example |
|------|---------|---------|
| npryce/make-it-easy | Instantiator + Property | `make(an(Apple, with(leaves, 2)))` |
| adewale/tasche | ArticleFactory.create() | `ArticleFactory.create(title="Custom")` |
| chrischabot/the-wire | createUser/createPost factories | `createUser(client, {handle: "alice"})` |
| simonw/datasette | make_app_client() context manager | `with make_app_client(cors=True) as client:` |

**Lesson**: Every mature test suite evolves toward test data builders. The form varies (Java builder pattern, Python factories, TypeScript helper functions), but the principle is the same: express intent, hide defaults.

---

## Testing Asynchronous Systems

### The GOOS Approach (npryce)

From the GOOS code examples, two patterns for async testing:

#### Polling

```java
// Wait for a condition to become true, with timeout
assertEventually(timeout(5, SECONDS), () -> {
    return queue.size() > 0;
});
```

#### Notifications

```java
// Block until notified, with timeout
Notification notification = notificationReceiver.waitForNotification(5, SECONDS);
assertThat(notification.message(), containsString("expected"));
```

**Lesson**: Async tests need explicit timeouts and either polling or notification-based synchronization. Never use `Thread.sleep()` — it's either too long (slow test) or too short (flaky test).

### The Timeout Utility (npryce/goos-code-examples)

A dedicated `Timeout` class that encapsulates the polling/waiting pattern with configurable poll intervals and timeouts. This is infrastructure code that belongs in a test support library, not copy-pasted into each test.

---

## Reference Implementation Testing

### PyTorch as Oracle (karpathy)

Karpathy's testing pattern: **use a trusted reference implementation as the oracle**.

```python
# micrograd: test_engine.py
def test_sanity_check():
    # Compute forward/backward pass with micrograd
    x = Value(-4.0)
    z = 2 * x + 2 + x
    q = z.relu() + z * x
    h = (z * z).relu()
    y = h + q + q * x
    y.backward()
    xmg, ymg = x, y

    # Compute same thing with PyTorch
    x = torch.Tensor([-4.0]).double()
    x.requires_grad = True
    z = 2 * x + 2 + x
    q = z.relu() + z * x
    h = (z * z).relu()
    y = h + q + q * x
    y.backward()
    xpt, ypt = x, y

    # Compare: forward pass
    assert ymg.data == ypt.data.item()
    # Compare: backward pass (gradients)
    assert xmg.grad == xpt.grad.item()
```

**Lesson**: When building a simplified implementation of a complex system, test it against the canonical implementation. The test literally runs the same computation through both systems and compares results.

### tiktoken as Oracle (karpathy)

```python
# minbpe: test_tokenizer.py
@pytest.mark.parametrize("text", test_strings)
def test_gpt4_tiktoken_equality(text):
    text = unpack(text)
    tokenizer = GPT4Tokenizer()
    enc = tiktoken.get_encoding("cl100k_base")
    tiktoken_ids = enc.encode(text)
    gpt4_tokenizer_ids = tokenizer.encode(text)
    assert gpt4_tokenizer_ids == tiktoken_ids
```

**Lesson**: For tokenizers, encoders, and any function with a canonical reference, **parametrize over diverse inputs and compare against the reference**. The test strings include empty, single character, Unicode, emoji, and a full file.

### Roundtrip Identity as Self-Oracle

```python
@pytest.mark.parametrize("tokenizer_factory", [BasicTokenizer, RegexTokenizer, GPT4Tokenizer])
@pytest.mark.parametrize("text", test_strings)
def test_encode_decode_identity(tokenizer_factory, text):
    text = unpack(text)
    tokenizer = tokenizer_factory()
    ids = tokenizer.encode(text)
    decoded = tokenizer.decode(ids)
    assert text == decoded
```

**Lesson**: `decode(encode(x)) == x` is the purest property test for any codec. Parametrize over both the implementation variants AND the test inputs.

---

## Fake Server Testing

### bradfitz's gomemcache Fake Server

Brad Fitzpatrick (Go core team) wrote a complete in-process fake memcached server for testing:

```go
type testServer struct {
    mu      sync.Mutex
    m       map[string]serverItem
    nextCas uint64
}
```

The fake server:
- Implements the full memcached text protocol (set, get, add, replace, delete, incr, decr, cas, touch, flush_all)
- Handles CAS (Compare-And-Swap) with proper conflict detection
- Handles TTL/expiry
- Handles noreply flag
- Runs in-process on a real TCP socket

Tests run against **three** server types:
1. **Real localhost memcached** (skipped if not running)
2. **Real memcached child process** (unix socket)
3. **In-process fake server** (always available)
4. **Real memcached with TLS** (skipped if binary lacks TLS)

```go
func TestLocalhost(t *testing.T) {
    c, err := net.Dial("tcp", localhostTCPAddr)
    if err != nil {
        t.Skipf("skipping test; no server running at %s", localhostTCPAddr)
    }
    testWithClient(t, New(localhostTCPAddr))
}

func TestFakeServer(t *testing.T) {
    ln, _ := net.Listen("tcp", "localhost:0")
    srv := &testServer{}
    go srv.Serve(ln)
    testWithClient(t, New(ln.Addr().String()))
}
```

**Key pattern**: `testWithClient(t, c *Client)` — the same test function runs against all server types. The test doesn't know or care which server it's talking to.

**Lesson**: Write a protocol-faithful fake server and run the same test suite against both the fake and real servers. The fake gives speed and reliability; the real server gives confidence.

---

## Minimalist Testing Frameworks

### jstinytest (joewalnes)

The entire framework is 47 lines:

```javascript
const TinyTest = {
    run: function(tests) {
        let failures = 0;
        for (let testName in tests) {
            try {
                tests[testName]();
                console.log('Test:', testName, 'OK');
            } catch (e) {
                failures++;
                console.error('Test:', testName, 'FAILED', e);
            }
        }
        document.body.style.backgroundColor = failures == 0 ? '#99ff99' : '#ff9999';
    },
    assertEquals: function(expected, actual) {
        if (expected != actual) throw new Error(`assertEquals() "${expected}" != "${actual}"`);
    },
};
```

Usage:
```javascript
tests({
    'adds numbers': function() { eq(6, add(2, 4)); },
    'subtracts numbers': function() { eq(-2, add(2, -4)); },
});
```

### tinytest.h (joewalnes)

The C version — a single header file, zero dependencies:

```c
#define ASSERT(msg, expression) if (!tt_assert(__FILE__, __LINE__, (msg), (#expression), (expression) ? 1 : 0)) return
#define ASSERT_EQUALS(expected, actual) ASSERT((#actual), (expected) == (actual))
#define RUN(test_function) tt_execute((#test_function), (test_function))
#define TEST_REPORT() tt_report()
```

**Lesson from Joe Walnes**: "Stop using over complicated frameworks that get in your way." A test framework needs exactly four things: run tests, report results, assert equality, and show where failures happened.

---

## Test Lifecycle Management

### worktorule: Acceptance Tests Tracked by Issue State (npryce)

The key insight: **tests have a lifecycle that maps to the development process**.

```
Feature requested (issue opened)
  → Acceptance test written (fails, marked @InProgress("42"))
  → Unit TDD (red-green-refactor)
  → Acceptance test passes (issue closed)
  → Test becomes regression test (no longer @InProgress)
```

worktorule automates this: failing tests marked `@InProgress` with an open issue are reported as "skipped." Once the issue is closed, they become real failures if they regress.

**Lesson**: This is the operational form of TDD at the acceptance test level. Don't skip tests — mark them as in-progress and tie them to issue tracker state.

---

## TDD Teaching Patterns

### Ivan Moore's Exercise Repos

Ivan Moore (XP practitioner) maintains repos designed for teaching TDD:

- **TddSkeleton** — Empty project with JUnit/Gradle setup ready for TDD exercises
- **Camera** — Mock objects exercise (practicing interaction testing with test doubles)
- **RefactoringGolf** — Refactoring exercises with scored "holes" (fewest steps to transform code)
- **gildedrose** — The classic Gilded Rose refactoring kata
- **battleships** — Game implementation kata

**Lesson**: TDD is taught through practice, not theory. Each repo is a self-contained exercise with clear constraints.

### The Refactoring Golf Format

Created by Ivan Moore, Dave Cleal, and Mike Hill:
1. Start with working code
2. Transform it to a target state
3. Score: fewest refactoring steps wins
4. Each step must keep tests green

**Lesson**: Good tests enable confident refactoring. If the tests are brittle or coupled to implementation, refactoring becomes impossible.

---

## Key Insights by Practitioner

### Nat Pryce (GOOS co-author)

1. **Test data builders express intent**: `with(ripeness, 0.9)` > `new Fruit(0.9)`
2. **Property testing finds what you didn't think to test**: factcheck ensures boundary values are always tested first
3. **Fuzz testing via mutation** (snodge) is more practical than random generation for structured data
4. **Test lifecycle should track development lifecycle**: worktorule ties test state to issue tracker state
5. **The property-driven diamond kata** shows TDD can work with only property tests, no example tests

### Graydon Hoare (Rust creator)

1. **Exhaustive testing > random testing** when the space is small enough: exhaustigen-rs tests *every* combination
2. **Bridge fuzzing and property testing**: proptest-arbitrary-interop lets you write the data generator once for both
3. **Enumeration is lazy and demand-driven**: the generator tracks and extends the state space as needed

### Andrej Karpathy

1. **Reference implementation as oracle**: test your simplified implementation against the canonical one (PyTorch)
2. **Roundtrip identity is the fundamental property**: `decode(encode(x)) == x`
3. **Parametrize across implementations AND inputs**: test all tokenizer variants against all test strings
4. **Include a real file in test data**: don't just test on toy inputs — include a real document (taylorswift.txt)

### Brad Fitzpatrick (Go core team)

1. **Write a protocol-faithful fake server**: gomemcache's fake implements the full memcached protocol
2. **Run the same tests against fake and real**: `testWithClient()` doesn't know which server it's talking to
3. **Graceful skip when real server unavailable**: `t.Skipf("skipping; no server at %s", addr)`
4. **Test with multiple transport types**: TCP, Unix socket, TLS — same test suite

### Joe Walnes

1. **Testing frameworks should be tiny**: 47 lines for JavaScript, one header file for C
2. **Visual feedback matters**: green/red background in browser tells you instantly
3. **Stop using overcomplicated frameworks**: assert, run, report — that's all you need

### Ivan Moore

1. **TDD is practiced through katas**: TddSkeleton, Camera, RefactoringGolf, gildedrose
2. **Mock objects are an exercise, not default**: Camera repo is specifically for *practicing* mock usage
3. **Refactoring requires green tests**: RefactoringGolf scores by keeping tests green through each step

---

## Patterns for the Testing Best Practices Skill

### From these practitioners, the skill should incorporate:

1. **Boundary-first generators** for property testing (npryce factcheck, adewale qc)
2. **Mutation-based fuzz testing** for structured data validation (npryce snodge)
3. **Test data builders** that express intent, not structure (npryce make-it-easy)
4. **Reference implementation as oracle** for simplified/educational implementations (karpathy)
5. **Exhaustive testing** when the state space is bounded (graydon exhaustigen)
6. **Protocol-faithful fakes** that run the same tests as real servers (bradfitz)
7. **Test lifecycle management** tied to issue tracker state (npryce worktorule)
8. **Roundtrip identity** as the fundamental property test for any codec/serializer
9. **Graceful degradation** in tests (skip when server unavailable, bail on credit exhaustion)
10. **Minimalism** — don't add testing complexity that doesn't find bugs (joewalnes)
