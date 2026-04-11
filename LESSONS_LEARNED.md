# Lessons Learned

What we discovered while building this skill. These are meta-lessons about building testing skills for agents, not about testing itself.

---

## Skill Design

### Progressive disclosure saves tokens but requires sharp triggers

Splitting `advanced-patterns.md` (747 lines) into 9 topic files cut typical token load by ~50%. But the triggers must be specific: "read references/advanced-patterns.md" loads everything; "read references/characterization-testing.md IF you're refactoring legacy code" loads only what's needed. Generic pointers waste context.

### Language-specific scripts don't belong in polyglot skills

We shipped a `scripts/check_test_quality.py` that only worked for Python. A Go or Rust project got no validation benefit. We replaced it with language-agnostic guidance in SKILL.md that tells the agent *what to scan for* rather than giving it a single-language tool. The agent can grep for `t.Log` in Go, `toBeDefined()` in TypeScript, `assert result is not None` in Python — it doesn't need a script for that.

### The validation loop is the highest-ROI addition

Telling the agent to self-check its work before reporting done (scan for weak assertions, run the tests, verify density) eliminated the one failing assertion from iteration 1 (assertion density 2.53 vs 3.0 target). The agent catches its own mistakes when told to look.

### Don't explain what the agent already knows

Early versions of the language references explained what pytest is, what Vitest is, basic `describe`/`it` syntax. The agent knows this. Keep only the non-obvious parts: boundary-first Hypothesis strategies, `@cloudflare/vitest-pool-workers`, `t.Helper()` in Go.

## Research

### Scan real repos, not documentation

The most valuable insights came from reading actual test files in production repos, not from testing documentation. The `t.Log` antipattern (logging instead of asserting) was found by reading rogue_planet's XSS tests. The mock contract test pattern came from reading atlas's Playwright tests. The fixture-based golden file pattern came from reading defuddle's test infrastructure. None of these appear in testing guides.

### Every practitioner has one big idea

- Kent Beck: tests have 12 properties that *conflict* — testing is a design space, not a checklist
- Nat Pryce: boundary-first generators, mutation-based fuzzing, test lifecycle tied to issue trackers
- Graydon Hoare: when the space is small enough, test *everything* exhaustively
- Andrej Karpathy: the reference implementation IS the test oracle
- Brad Fitzpatrick: write a protocol-faithful fake and run the same tests against fake and real
- Joe Walnes: a test framework needs exactly 4 things and nothing more
- Steph Ango: add a fixture file = add a test (zero-code test creation)
- Mary Rose Cook: test at the user-facing level, pin non-deterministic inputs

### One combined file per batch was a mistake

We initially lumped 7 practitioners into one `LESSONS_FROM_PRACTITIONERS.md`. Individual contributions got buried. Splitting into one file per person made each practitioner's key idea stand out and made the research navigable.

## Evals

### Without-skill baselines are essential

The with-skill runs always look reasonable on their own. The baselines reveal what the skill actually adds: property-based tests (appeared in 100% of with-skill runs, 0% of without-skill), structured severity-prioritized assessments (with-skill only), explicit assertion density measurement (with-skill only).

### Balance evals across languages early

Our first 6 evals were 4 Python + 1 TypeScript + 1 Go + 0 Rust. This made us confident in Python behavior but blind to Go and Rust. When we added Go assess and Rust write evals, they passed — but we didn't know that until we tested.

### Eval fixtures should contain realistic antipatterns

Our `weak_tests.py` fixture was effective because it contained real antipatterns observed in production repos: `t.Log` instead of `t.Error`, `print` instead of `assert`, `@skip` without conditions, mocking the system under test. Synthetic bad tests would have been less useful.

### The eval viewer was unusable

The skill-creator's `generate_review.py --static` produced an HTML file with JavaScript alerts on every interaction. We abandoned it and presented results inline in conversation. For future iterations: present results directly rather than depending on external viewer tools.

## Evolution

### Iteration history

| Iteration | Evals | Languages | Pass Rate | Key Change |
|-----------|-------|-----------|-----------|------------|
| 1 | 3 | Python, TypeScript | 96% (24/25) | Initial skill |
| 2 | 3 | Python, TypeScript | 100% (25/25) | Added Test Desiderata, mathematical properties, golden files, Go patterns |
| 3 | 7 | Python, TypeScript, Go, Rust | 100% (49/49) | Split advanced-patterns, balanced evals, language-agnostic validation |

The biggest quality jump was iteration 1→2 (+4%, fixed assertion density). The biggest coverage jump was iteration 2→3 (3→7 evals, 2→4 languages).

### Token cost tracked but not optimized prematurely

We measured token cost throughout (iteration 1: ~30k with-skill, iteration 3: ~30k average) but optimized for quality first. Token savings came naturally from splitting files — we didn't sacrifice content to save tokens.
