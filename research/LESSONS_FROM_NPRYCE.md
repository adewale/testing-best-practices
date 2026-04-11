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

## Testing Asynchronous Systems (GOOS code examples)

Two patterns:

**Polling**: `assertEventually(timeout(5, SECONDS), () -> queue.size() > 0)`

**Notifications**: `notificationReceiver.waitForNotification(5, SECONDS)`

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
