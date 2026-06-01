# testing-best-practices

An agent skill that enforces testing best practices when writing, reviewing, or improving tests. Built from analysis of real-world testing patterns across 13 GitHub accounts and grounded in the work of practitioners like Kent Beck (TDD), Nat Pryce (GOOS), Graydon Hoare (Rust), and Andrej Karpathy.

![A typographic ledger of the sixteen testing techniques this skill teaches, organised into three tiers — Always (Unit, Smoke, Regression); When triggered (Property-based, End-to-end, Doc/Code sync, Contract, VCR cassette, Characterization, Differential, Golden file, Pirate/Conformance); With caution (Visual/Screenshot, Mutation, Performance, Fuzz). A top strip frames the red-green-refactor rhythm: a test that fails first, the smallest code that passes, clean up while green.](research/diagrams/skill-ledger.png)

## What it does

When an agent uses this skill, it produces higher-quality tests than it would on its own. Specifically:

- **Property-based tests appear** (Hypothesis, fast-check, proptest) where they wouldn't otherwise
- **Assertion density increases** from ~1 to 3+ meaningful assertions per test
- **Assessments become structured** with severity-prioritized findings (P0/P1/P2/P3) instead of ad-hoc lists
- **Anti-patterns get detected**: skipped tests, logging-instead-of-asserting, mock-everything "integration" tests, weak "not empty" assertions
- **Language-appropriate patterns** are used: table-driven tests in Go, `#[test]` modules in Rust, Vitest + fast-check in TypeScript

## Install

```bash
npx skills add adewale/testing-best-practices
```

## How it works

The skill operates in four modes:

| Mode | When | What it does |
|------|------|-------------|
| **Write** | Writing new tests | Red-Green-Refactor TDD, property-based tests, boundary values, sad path coverage, validation loop |
| **Assess** | Reviewing existing tests | 6-step quality audit: sabotage detection, assertion density, mock drift, tier integrity, coverage config, mutation testing readiness |
| **Upgrade** | Improving weak tests | Prioritized fixes for flaky, weak, or sabotaged tests |
| **Detect** | Finding hidden problems | Unconditional skips, print-not-assert, ordering dependencies, tests that fake coverage |

Language-specific guidance loads on demand based on the project's language. Advanced pattern references load only when their trigger condition matches (e.g., `references/characterization-testing.md` loads only when refactoring legacy code). This keeps token usage efficient.

## What's covered

### Core principles (always loaded, ~5,000 tokens)

- Red-Green-Refactor TDD
- Test quality over quantity (Kent Beck's Test Desiderata, assertion density)
- Real objects over mocks (with a preference hierarchy)
- Property-based testing (9 invariant patterns including mathematical properties)
- E2E testing
- Documentation-code sync testing
- Characterization testing for legacy code
- Differential and pirate testing
- Test data builders and fixtures
- Correctness by construction — types over runtime checks; invariant-proof tests (PBT) plus model-gap tests (try to construct each forbidden state)
- Sad path and boundary testing
- Validation loop (self-check before reporting done, including "could a type have replaced this test?")

### Reference files (loaded on demand)

**Language-specific** (one loaded per project):

| File | Content |
|------|---------|
| `references/python.md` | pytest, Hypothesis, VCR cassettes, async testing, CLI testing |
| `references/typescript.md` | Vitest, fast-check, Playwright, mock contract tests, API clients |
| `references/go.md` | Table-driven tests, `t.TempDir()`, `httptest`, build tags, `testdata/`, `t.Helper()` |
| `references/rust.md` | `#[test]`, proptest, exhaustigen, cargo-mutants, CLI binary tests |

**Always available**:

| File | Content |
|------|---------|
| `references/antipatterns.md` | 13 anti-patterns with detection signals, severity levels, and fixes |
| `references/test-types.md` | Decision guide with Step Zero (types-vs-tests), trust-boundary lens, and 3-tier hierarchy |

**Topic-specific** (loaded only when the trigger matches):

| File | Trigger |
|------|---------|
| `references/characterization-testing.md` | Refactoring legacy code |
| `references/differential-testing.md` | Reimplementing algorithms, multi-language SDKs |
| `references/golden-file-testing.md` | Transformation pipelines, snapshot tests, promote workflow |
| `references/deterministic-time.md` | Code depends on time, timers, scheduling, or flaky time tests |
| `references/vcr-cassettes.md` | Code calling external APIs |
| `references/doc-sync-testing.md` | CLI commands or plugin hooks in docs |
| `references/mutation-testing.md` | Verifying test suite catches real bugs |
| `references/exhaustive-testing.md` | Small state spaces (booleans, enums) |
| `references/mathematical-properties.md` | Domain objects with arithmetic |
| `references/test-data-builders.md` | Need factories, fixtures, or assertion helpers |
| `references/correctness-by-construction.md` | Same invariant checked at 3+ layers, "should never happen" tests, status enums duplicated across layers, loose strings through the system, or typed language with smart constructors |

## Eval results

Evaluated with 10 test cases across Python, TypeScript, Go, and Rust:

| Eval | Language | Mode | Description |
|------|----------|------|-------------|
| 1 | Python | Write | URL parser test suite |
| 2 | Python | Assess | Weak test quality review |
| 3 | TypeScript | Write | Security-focused sanitizer tests |
| 4 | Go | Write | Cache with TTL and concurrency |
| 5 | Python | Write | Characterization tests for legacy code |
| 6 | Python | Write | VCR cassette setup for API testing |
| 7 | TypeScript | Assess | Weak test quality review |
| 8 | Go | Assess | Weak test quality review |
| 9 | Rust | Write | INI config parser tests |
| 10 | Go | Write | Characterization tests for cache |

Full eval data is in `testing-best-practices-workspace/`.

## Research corpus

Built from analysis of testing patterns across 13 GitHub accounts and one organization:

- [kentbeck](https://github.com/kentbeck) -- Test Desiderata (12 properties of good tests), TCR, MoneyPython
- [npryce](https://github.com/npryce) (GOOS co-author) -- factcheck, snodge, make-it-easy, worktorule
- [graydon](https://github.com/graydon) (Rust creator) -- exhaustigen-rs, proptest-arbitrary-interop
- [karpathy](https://github.com/karpathy) -- differential testing against PyTorch/tiktoken
- [kepano](https://github.com/kepano) -- fixture-based golden file testing (defuddle)
- [maryrosecook](https://github.com/maryrosecook) -- gitlet test suite, file tree builders
- [simonw](https://github.com/simonw) (datasette, sqlite-utils, llm) -- documentation-as-tests, VCR cassettes
- [bradfitz](https://github.com/bradfitz) (Go team) -- protocol-faithful fake servers
- [joewalnes](https://github.com/joewalnes) -- minimalist testing frameworks
- [ivanmoore](https://github.com/ivanmoore) -- TDD katas, mock object exercises
- [adewale](https://github.com/adewale) -- property-based testing, mock fidelity, test quality audits
- [chrischabot](https://github.com/chrischabot) -- 5-tier test architecture, API scenario tests
- [tirsen](https://github.com/tirsen) -- retry patterns
- [janestreet](https://github.com/janestreet) -- expect tests, library-level simulation, `Time_source`, Bonsai testing

Individual research documents are in `research/` (one per practitioner/account).

## Project structure

```
testing-best-practices/             # The skill (ships to agents)
  SKILL.md                          # Core instructions (~310 lines)
  references/                       # Loaded on demand
    python.md                       # Language: Python
    typescript.md                   # Language: TypeScript
    go.md                           # Language: Go
    rust.md                         # Language: Rust
    antipatterns.md                 # Always: detection signals + fixes
    test-types.md                   # Always: decision guide
    characterization-testing.md    # Topic: legacy code
    differential-testing.md        # Topic: reference implementations
    golden-file-testing.md         # Topic: transformation pipelines, snapshot tests
    deterministic-time.md          # Topic: clock injection, time virtualization
    vcr-cassettes.md               # Topic: external APIs
    doc-sync-testing.md            # Topic: documentation drift
    mutation-testing.md            # Topic: test quality verification
    exhaustive-testing.md          # Topic: small state spaces
    mathematical-properties.md    # Topic: algebraic laws
    test-data-builders.md          # Topic: factories and fixtures

research/                           # Source material (does not ship)
  LESSONS_FROM_KENTBECK.md
  LESSONS_FROM_NPRYCE.md
  LESSONS_FROM_GRAYDON.md
  LESSONS_FROM_KARPATHY.md
  LESSONS_FROM_KEPANO.md
  LESSONS_FROM_MARYROSECOOK.md
  LESSONS_FROM_SIMONW_REPOS.md
  LESSONS_FROM_BRADFITZ.md
  LESSONS_FROM_JOEWALNES.md
  LESSONS_FROM_IVANMOORE.md
  LESSONS_FROM_ADEWALE_REPOS.md
  LESSONS_FROM_CHRISCHABOT_REPOS.md
  LESSONS_FROM_TIRSEN.md
  LESSONS_FROM_JANE_STREET.md
  ANTIPATTERNS.md
  DECISION_TREE.md
  NOVEL_TESTING_TYPES.md

evals/                              # Test cases for the skill itself
  evals.json                        # 10 eval cases across 4 languages
  files/                            # Fixture code for eval prompts

testing-best-practices-workspace/   # Eval results by iteration
```

## License

MIT
