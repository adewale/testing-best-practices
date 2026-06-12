# Lessons from github.com/npryce (Nat Pryce)

> Co-author of "Growing Object-Oriented Software, Guided by Tests" (GOOS), co-created jMock and Hamcrest.
> Date: 2026-04-11

---

## Who He Is

Nat Pryce co-wrote the most influential book on test-driven development with mock objects. He didn't just write about testing — he created four testing libraries, each embodying a distinct practice.

## Testing Libraries Created

### Hamcrest (with Steve Freeman)

The matcher library used across Java, Python, Swift, Kotlin, and more. Key insight: **assertions should read like sentences**.

```java
assertThat(cheese.name(), equalTo("Wensleydale"));
assertThat(result, is(not(empty())));
assertThat(items, hasItem(with(name("Widget"))));
```

**hamkrest** (Kotlin port) continues this philosophy with Kotlin idioms.

### python-factcheck

A QuickCheck implementation. Notable for:
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

**Design decision**: Boundary values are yielded first, then shuffled into the random stream. This ensures edge cases are always tested first.

### snodge

A fuzz testing library for JSON, XML, HTML forms, text, and binary data. Instead of generating random data from scratch, it **mutates known-good data**.

```kotlin
random.mutants(defaultJsonMutagens().forStrings(), 10, originalJson)
    .forEach(::println)
```

Key testing targets:
- Unexpected structures don't cause unchecked exceptions
- Application code ignores additional properties
- Application doesn't instantiate arbitrary classes named in data (security)
- Application copes with invalid Unicode encoding

**Lesson**: Mutation-based fuzzing is more effective than random generation for structured data, because it starts from valid input and makes targeted, plausible changes.

### make-it-easy

A Test Data Builder framework that reduces boilerplate:

```java
Maker<Apple> ripeApple = an(Apple, with(ripeness, 0.9), with(leaves, 3));
Apple apple = make(ripeApple);
Maker<Apple> unripeApple = ripeApple.but(with(ripeness, 0.1));
```

**Lesson from GOOS**: Test data builders should express the *intent* of the data, not its structure. `with(ripeness, 0.9)` tells you what matters; `new Apple(3, 0.0, 0.9, "red")` tells you nothing.

### worktorule

Test lifecycle management by correlating test failures with issue tracker state:

```java
@Rule public TestRule ignoreInProgress = new IgnoreInProgress(
    new GitHubIssues("example-org", "example-project"));

@Test
@InProgress("42")
public void new_feature_under_development() {
    // Fails? Skip if issue #42 is still open.
    // Fails after issue #42 is closed? Actual test failure.
}
```

**Lesson**: Acceptance tests written before the feature exists should be tracked as "in progress," not skipped. When the issue closes, the test automatically becomes a regression test.

## The GOOS Book Itself (2009)

The libraries above are artifacts of the book's argument; the argument is bigger than any of them. (Quotes verified against the print text; page numbers are the print edition's.)

### The walking skeleton (ch. 4, 10)

> "A 'walking skeleton' is an implementation of the thinnest possible slice of real functionality that we can automatically build, deploy, and test end-to-end." (p. 32, crediting Cockburn)

It resolves the first-feature paradox — "it's hard to build both the tooling and the feature it's testing at the same time" — and "end-to-end" includes the *process*: "We want our test to start from scratch, build a deployable system, deploy it into a production-like environment, and then run the tests through the deployed system." Building it "takes a surprising amount of effort … [and] will flush out all sorts of technical and organizational questions" (ch. 10) — which is the point: expose uncertainty early.

### The double feedback loop (ch. 1, fig. 1.2)

Every feature starts with a failing acceptance test (outer loop) wrapping the unit-test cycle (inner loop). "The outer test loop is a measure of demonstrable progress, and the growing suite of tests protects us against regression failures." "The inner loop supports the developers… Failing unit tests should never be committed to the source repository." In-progress acceptance tests stay out of the build; finished ones must always pass. The loops nest outward into pairing, daily meetings, iterations: "if a discrepancy slips through an inner loop, there is a good chance an outer loop will catch it."

### "Listen to your tests" — test smells are design feedback (ch. 20)

> "The qualities that make an object easy to test also make our code responsive to change." — "When we find a feature that's difficult to test, we don't just ask ourselves how to test it, but also why is it difficult to test."

Where Meszaros catalogs smells in the *test*, GOOS ch. 20 catalogs tests that indict the *target code*: **I Need to Mock an Object I Can't Replace** (hidden singleton/global dependencies), **Logging Is a Feature** (support logging vs. diagnostic logging are "two separate features that happen to share an implementation"), **Mocking Concrete Classes**, **Don't Mock Values** ("Just create an instance and use it"), **Bloated Constructor** (look for the missing abstraction among the arguments), **Confused Object** (too many responsibilities), **Too Many Dependencies**, **Too Many Expectations** ("it's hard to see what's important and what's really under test").

### The mocking discipline (OOPSLA 2004 + ch. 8, 24)

The 2004 paper "Mock Roles, not Objects" (Freeman, Pryce, Mackinnon, **Joe Walnes** — also in this corpus) opens: "Mock Objects is misnamed. It is really a technique for identifying types in a system based on the roles that objects play" — and adds, "It turns out to be less interesting as a technique for isolating tests from third-party libraries than is widely thought." Mocking is interface discovery, a design activity. The rules that keep it honest:

- **Only mock types you own** — "Mock Objects is a design technique so programmers should only write mocks for types that they can change" (§4.1); wrap third-party APIs in your own role interfaces and mock those.
- **Allow queries; expect commands** (ch. 24) — "Commands are calls that are likely to have side effects… Queries don't change the world, so they can be called any number of times, including none." Command–query separation applied to test doubles.
- **Never mock values** — construct them; they should be immutable anyway.

Practiced this way, TDD "push[es] the structure of an application towards something like Cockburn's 'ports and adapters' architecture" (ch. 7), with context-independent objects and a clean values/objects split. This is the canonical "London school" text (vs. the Detroit/classicist school of Beck's *TDD: By Example*); the standard critique — interaction tests couple tests to collaborator protocols and resist refactoring — is largely a critique of mocking that *violates* the book's own rules.

### The Auction Sniper example — honest end-to-end (part III)

The worked example drives a Swing bid-sniper against an XMPP auction protocol. The end-to-end tests use a **real** message broker (Openfire) but a `FakeAuctionServer` for the auction house — and the book is candid: "this first test is not really end-to-end. It doesn't include the real auction service," recorded "as a known risk in the project plan" with time scheduled to test against the real server early. Fidelity gaps are allowed, but only when named, tracked, and scheduled for closure.

## Testing Asynchronous Systems (GOOS ch. 26–27)

Two patterns:

**Polling**: `assertEventually(timeout(5, SECONDS), () -> queue.size() > 0)`

**Notifications**: `notificationReceiver.waitForNotification(5, SECONDS)`

The book's boxed rule (ch. 27, "Testing Asynchronous Code"): **"Wait for Success — An asynchronous test must wait for success and use timeouts to detect failure."** Observe "by sampling its observable state or by listening for events that it sends out"; replace hidden timers with injectable event sources ("Externalize Event Sources"); and treat flickering tests as an emergency — "Flickering tests can mask real defects." Ch. 26 separates functionality from concurrency policy so most logic can be tested single-threaded.

**Lesson**: Async tests need explicit timeouts and either polling or notification-based synchronization. Never use `Thread.sleep()`.

## The Property-Driven Diamond Kata

Shows TDD can work with *only* property tests, no example tests. The entire diamond kata is driven by properties like symmetry, character containment, and row width invariants.

## Key Insights

1. **Test data builders express intent**: `with(ripeness, 0.9)` > `new Fruit(0.9)`
2. **Property testing finds what you didn't think to test**: factcheck ensures boundary values are always tested first
3. **Fuzz testing via mutation** (snodge) is more practical than random generation for structured data
4. **Test lifecycle should track development lifecycle**: worktorule ties test state to issue tracker state
5. **The property-driven diamond kata** shows TDD can work with only property tests
6. **Assertions should read like sentences** (Hamcrest)
7. **Start with a walking skeleton**: the thinnest build-deploy-test slice, end-to-end including the deployment process — it flushes out the project's real risks while there's time to fix them
8. **Run two feedback loops**: a failing acceptance test (progress) wrapping unit tests (design); never commit failing unit tests
9. **Listen to your tests**: a hard-to-write test is design feedback — "the qualities that make an object easy to test also make our code responsive to change"
10. **Mocks are for discovering roles, not for isolating libraries**: mock roles not objects, only mock types you own, never mock values, allow queries / expect commands
11. **Async tests wait for success with timeouts** (sampling or listening), and flickering tests are treated as defects because they mask real ones
12. **Name your fidelity gaps**: GOOS's own first "end-to-end" test fakes the auction service — but says so, logs it as a project risk, and schedules the real-server test
