# Lessons from github.com/kentbeck (Kent Beck)

> Creator of Extreme Programming, Test-Driven Development, and JUnit. Author of "Test-Driven Development: By Example," "Extreme Programming Explained," and "Tidy First?".
> Date: 2026-04-11 (books section added 2026-06-12)

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

## The Books

The repos above are late-career sketches; the method lives in the books. (Quotes marked verbatim were verified against the Pearson sample chapters of *TDD: By Example* and the full first-edition text of *XP Explained*.)

### *Test-Driven Development: By Example* (2002)

The goal is "*Clean code that works*, in Ron Jeffries' pithy phrase" — reached by two rules: "Write new code only if an automated test has failed" and "Eliminate duplication." The mantra, verbatim: "1. Red—Write a little test that doesn't work, and perhaps doesn't even compile at first. 2. Green—Make the test work quickly, committing whatever sins necessary in the process. 3. Refactor—Eliminate all of the duplication created in merely getting the test to work."

What the book teaches beyond the mantra:

- **TDD is fear management.** "Test-driven development is a way of managing fear during programming... The tests in test-driven development are the teeth of the ratchet." And the dial: "the tougher the programming problem, the less ground that each test should cover." Step size is adjustable — "Are the teeny-tiny steps feeling restrictive? Take bigger steps. Are you feeling a little unsure? Take smaller steps."
- **The Test List** (ch. 25): before starting, write down every test you'll need; when new ideas surface mid-cycle, *add them to the list* instead of chasing them. Visible throughout the Money example as a literal to-do list with strikethroughs.
- **Three green-bar strategies** (ch. 28): **Fake It** (return a constant, gradually replace constants with variables), **Triangulate** ("we only generalize code when we have two examples or more... Triangulation feels funny to me. I use it only when I am completely unsure of how to refactor"), and **Obvious Implementation** (just type it when confident; downshift to Fake It on an unexpected red bar).
- **The "how do I test X?" patterns** (ch. 26–27): **Assert First** (write the assertion, work backward to setup), **Evident Data** (write expected values as expressions — `assertEquals(2 * 5 + 3 * 2, ...)` — so the test reads as spec), **Child Test** (test too big? extract a smaller one, pass it, reintroduce), **Self Shunt** (the test case itself plays the collaborator), **Log String** (assert on an appended log to test call ordering and side effects), **Crash Test Dummy** (a fake that throws, for error paths you can't trigger — a full filesystem), **Learning Test** (test third-party APIs before depending on them), **Regression Test** (every reported defect becomes the smallest failing test), **Broken Test** (solo: end the day with a failing test as a re-entry point) vs. **Clean Check-in** (team: all green at check-in).
- **Part II builds xUnit in Python test-first** — the framework testing itself ("the kind of self-referential hoo-ha beloved of computer scientists") — proving the method works even at the meta level.
- **Honest limits, his own words**: "Security software and concurrency... are two topics where TDD is insufficient to mechanically demonstrate that the goals of the software have been met." And on test quantity: "Write tests until fear is transformed into boredom." His later Stack Overflow answer (2008) is the same position: "I get paid for code that works, not for tests, so my philosophy is to test as little as possible to reach a given level of confidence."
- His 2023 "Canon TDD" post restates the workflow definitively and names the anti-patterns: writing all tests up front, tests without assertions, deleting assertions to pass, copying actual output into expected values, refactoring while red.

### *Extreme Programming Explained* (1999; 2nd ed. 2004)

XP is testing turned up to ten: "If testing is good, everybody will test all the time (unit testing), even the customers (functional testing)." The canonical existence claim is here, verbatim: **"Any program feature without an automated test simply doesn't exist."**

- **Two test streams, two owners**: programmers write unit tests; customers (helped by a dedicated tester) write story-level functional tests — "What would have to be checked before I would be confident that this story was done?"
- **The asymmetric 100% rule**: "The programmer-written unit tests always run at 100%. If one of the unit tests is broken, no one on the team has a more important job than fixing the tests." Customer tests, by contrast, are a rising percentage.
- **The real "test everything" quote is more nuanced than the slogan**: "The programmers write unit tests for all the logic in the system that could possibly break," tempered by "You should test things that might break. If code is so simple that it can't possibly break... then you shouldn't write a test for it" and "It is impossible to test absolutely everything, without the tests being as complicated and error-prone as the code. It is suicide to test nothing. Testing is a bet. The bet pays off when your expectations are violated."
- **Test properties, 1999 edition**: "The tests that you must write in XP are isolated and automatic" — the seed of Test Desiderata, twenty years early.
- **Legacy adoption**: don't backfill — "it is tempting to try to just go back and write the tests for all the existing code. Don't do this. Instead, write the tests on demand" when you touch code.
- **Feedback latency is the enemy**: the 2nd edition names Ten-Minute Build and Continuous Integration as primary practices — build + all tests in ten minutes, integrate every few hours. And the line that explains why: "Optimism is an occupational hazard of programming. Feedback is the treatment."

### *Tidy First?* (2023)

Every change is either a **behavior change** (what observers can see — new features, bug fixes) or a **structure change** (a tidying — behavior invariant). The testing implication: behavior changes are what tests are *for*; tidyings are small enough to ride on the existing green suite and need no new tests — his newsletter follow-up "'Testing' Structure Changes" argues structure changes shouldn't get correctness assertions at all; their quality is judged by whether they shrink future behavior changes. Never mix the two kinds in one commit, so reviewers and the suite apply the right verification regime to each. This is Test Desiderata's "structure-insensitive" property turned into a workflow — per his 2019 tweet: "Tests should be coupled to the behavior of code and decoupled from the structure of code."

(*Smalltalk Best Practice Patterns*, 1996, predates xUnit and teaches no testing per se — but Composed Method and Debug Printing Method describe exactly the code shape that testing rewards.)

## Key Insights

1. **Test Desiderata**: 12 properties of good tests, traded off against each other — not a checklist but a design space
2. **TCR** forces tiny steps, fast tests, and reliable tests — it's TDD with the safety net cranked to maximum
3. **Mathematical properties as test cases**: associativity, commutativity, distributivity are excellent property tests for domain objects
4. **Test Pythonic idioms**: if you implement `__add__`, test with `sum()`. Test the language integration, not just the method.
5. **Behavioral + Structure-insensitive** is the sweet spot: tests should detect behavior changes but tolerate refactoring
6. **Test interference detection** (Moire) is a real problem worth tooling for
7. **Keep a test list; adjust step size to fear.** Park new test ideas on the list instead of chasing them; Fake It when unsure, Obvious Implementation when confident — "write tests until fear is transformed into boredom" (*TDD: By Example*)
8. **Every "how do I test X?" has a pattern answer**: Self Shunt, Log String (ordering/side effects), Crash Test Dummy (untriggerable error paths), Learning Test (third-party APIs), Regression Test (every defect becomes the smallest failing test)
9. **Test what might break — testing is a bet.** The famous slogan compresses a more careful claim: code that can't possibly break shouldn't get a test; "it is suicide to test nothing" (*XP Explained*); "test as little as possible to reach a given level of confidence" (2008)
10. **Unit tests run at 100% or the team stops**; on legacy code, write tests on demand when you touch code — never as a backfill project (*XP Explained*)
11. **Classify changes as behavior vs. structure and verify them differently**: behavior changes need tests, tidyings ride the existing green suite, and the two never share a commit (*Tidy First?*)
