# Lessons from github.com/kentbeck (Kent Beck)

> Creator of Extreme Programming, Test-Driven Development, and JUnit. Author of "Test-Driven Development: By Example."
> Date: 2026-04-11

---

## Who He Is

Kent Beck invented TDD and co-created JUnit. He literally wrote the book. His GitHub repos are more philosophical than code-heavy — but they codify testing principles that the entire industry builds on.

## Test Desiderata — The Properties of Valuable Tests

The single most important document in his repos. It defines 12 properties that make tests valuable, acknowledging that **they conflict with each other** and must be traded off:

1. **Isolated** — tests return the same results regardless of execution order
2. **Composable** — different dimensions of variability can be tested separately and combined
3. **Deterministic** — if nothing changes, the test result doesn't change
4. **Fast** — tests run quickly
5. **Writable** — tests are cheap to write relative to the cost of the code being tested
6. **Readable** — tests are comprehensible, invoking the motivation for writing this particular test
7. **Behavioral** — tests are sensitive to changes in behavior (if behavior changes, test result changes)
8. **Structure-insensitive** — tests don't change their result if the structure of the code changes
9. **Automated** — tests run without human intervention
10. **Specific** — if a test fails, the cause of the failure is obvious
11. **Predictive** — if all tests pass, the code should be suitable for production
12. **Inspiring** — passing the tests inspires confidence

**Key insight**: Some properties support each other (automating tests makes them faster). Some interfere (making tests more predictive makes them slower). Sometimes properties only *seem* to interfere — composability can make tests both faster AND more predictive.

**Lesson**: Don't optimize for a single property. Good tests navigate the tradeoff space between all 12 properties. A test that is fast, writable, and isolated but not behavioral or predictive is worse than useless — it gives false confidence.

## TCR — Test && Commit || Revert

A radical workflow: after every code change, run tests. If tests pass, automatically commit. If tests fail, automatically revert ALL changes.

**The philosophy**: TCR forces you to take tiny steps. If you can't make a change that keeps tests green, your step was too big. Break it down further.

**Implications for testing**:
- Tests must be fast (TCR is useless with a 5-minute test suite)
- Tests must be reliable (a flaky test causes revert of good code)
- Tests must be behavioral (if a test doesn't detect the change you just made, TCR commits untested code)

## MoneyPython — TDD by Example in Python

A Python implementation of the multi-currency Money example from "TDD: By Example." The test suite demonstrates TDD principles:

### Mathematical Property Tests

```python
def test_addition_associativity(self):
    """(a + b) + c = a + (b + c)"""
    left_result = exchange.reduce((a + b) + c, "USD")
    right_result = exchange.reduce(a + (b + c), "USD")
    self.assertAlmostEqual(left_result.amount, right_result.amount, places=2)

def test_distributive_property(self):
    """multiplier * (b + c) = (multiplier * b) + (multiplier * c)"""
    left_expr = multiplier * (b_eur + c_gbp)
    right_expr = (multiplier * b_eur) + (multiplier * c_gbp)
    left_usd = exchange.reduce(left_expr, "USD")
    right_usd = exchange.reduce(right_expr, "USD")
    self.assertAlmostEqual(left_usd.amount, right_usd.amount, places=2)
```

**Lesson**: Test mathematical properties (associativity, commutativity, distributivity) when the domain has them. These are property tests written as example tests.

### Pythonic API Tests

```python
def test_sum_builtin_function(self):
    """Python's sum() builtin works with Money objects"""
    money_list = [Money(5, "USD"), Money(10, "USD"), Money(15, "USD")]
    result = sum(money_list, Money(0, "USD"))
    self.assertEqual(result, Money(30, "USD"))
```

**Lesson**: Test that your objects work correctly with the language's built-in functions and idioms. If your Python class supports `+`, test it with `sum()`. If it supports `*`, test commutativity (`5 * money` and `money * 5`).

### Error Boundary Tests

```python
def test_invalid_additions(self):
    with self.assertRaises(ValueError):
        _ = five_dollars + 5
    with self.assertRaises(TypeError):
        _ = five_dollars + "hello"
    result = five_dollars + 0  # should work (identity element)
    self.assertEqual(result, five_dollars)
```

## Moire — Detecting Test Interference

An empty repo with a powerful description: "A test runner that identifies tests that interfere with one another, that is test1 followed by test2 passes, but test2 followed by test1 fails."

**Lesson**: Test isolation is hard enough that Kent Beck wanted to build a tool specifically to detect ordering dependencies. This validates "Isolated" as a desiderata.

## BPlusTreeAuditor

Audits Rust B+ tree implementations for correctness and performance — effectively a differential testing tool that validates implementations against a correctness specification.

## Key Insights

1. **Test Desiderata**: 12 properties of good tests, traded off against each other — not a checklist but a design space
2. **TCR** forces tiny steps, fast tests, and reliable tests — it's TDD with the safety net cranked to maximum
3. **Mathematical properties as test cases**: associativity, commutativity, distributivity are excellent property tests for domain objects
4. **Test Pythonic idioms**: if you implement `__add__`, test with `sum()`. Test the language integration, not just the method.
5. **Behavioral + Structure-insensitive** is the sweet spot: tests should detect behavior changes but tolerate refactoring
6. **Test interference detection** (Moire) is a real problem worth tooling for
