# testing-best-practices

An agent skill that enforces testing best practices when writing, reviewing, or improving tests. Built from analysis of real-world testing patterns across 10 GitHub accounts and grounded in the work of practitioners like Nat Pryce (GOOS), Graydon Hoare (Rust), and Andrej Karpathy.

## What it does

When an agent uses this skill, it produces higher-quality tests than it would on its own. Specifically:

- **Property-based tests appear** (Hypothesis, fast-check) where they wouldn't otherwise
- **Assertion density increases** from ~1 to 3+ meaningful assertions per test
- **Assessments become structured** with severity-prioritized findings (P0/P1/P2/P3) instead of ad-hoc lists
- **Anti-patterns get detected**: skipped tests, logging-instead-of-asserting, mock-everything "integration" tests, weak "not empty" assertions

## Install

```bash
npx skills add adewale/testing-best-practices
```

## How it works

The skill operates in four modes:

| Mode | When | What it does |
|------|------|-------------|
| **Write** | Writing new tests | Red-Green TDD, property-based tests, boundary values, sad path coverage |
| **Assess** | Reviewing existing tests | 6-step quality audit: sabotage detection, assertion density, mock drift, tier integrity, coverage config, mutation testing readiness |
| **Upgrade** | Improving weak tests | Prioritized fixes for flaky, weak, or sabotaged tests |
| **Detect** | Finding hidden problems | Unconditional skips, print-not-assert, tests that fake coverage |

Language-specific guidance (framework setup, PBT libraries, fixture patterns) loads on demand based on the project's language. The core principles apply universally.

## What's covered

### Core principles (always loaded)

- Red-Green TDD
- Test quality over quantity (assertion density, not just coverage)
- Real objects over mocks (with a preference hierarchy)
- Property-based testing (6 invariant patterns: never-crashes, roundtrip, idempotent, monotonic, conservation, valid-or-absent)
- E2E testing
- Documentation-code sync testing
- Characterization testing for legacy code
- Differential testing (reference implementation as oracle)
- Pirate testing (language-neutral conformance suites)
- Test data builders and fixtures
- Sad path and boundary testing

### Reference files (loaded when needed)

| File | Content |
|------|---------|
| `references/python.md` | pytest, Hypothesis, VCR cassettes, async testing, Click CLI testing |
| `references/typescript.md` | Vitest, fast-check, Playwright, mock contract tests, typed API clients |
| `references/go.md` | Table-driven tests, `t.TempDir()`, `httptest`, build tags, fake servers |
| `references/rust.md` | `#[test]`, proptest, exhaustigen, cargo-mutants, CLI binary integration tests |
| `references/antipatterns.md` | 12 anti-patterns with detection signals, severity levels, and fixes |
| `references/test-types.md` | 3-tier decision guide with trigger checklists and cost-benefit table |
| `references/advanced-patterns.md` | Characterization, differential, pirate, mutation, exhaustive, VCR, doc-sync, test data builders |

## Eval results

Evaluated with 3 test cases comparing with-skill vs without-skill outputs:

| Eval | With Skill | Without Skill |
|------|-----------|---------------|
| Write Python URL parser tests | 89% (8/9) | 67% (6/9) |
| Assess intentionally weak tests | 100% (8/8) | 75% (6/8) |
| Write TypeScript security tests | 100% (8/8) | 63% (5/8) |
| **Overall pass rate** | **96%** | **68%** |

The skill's strongest differentiator: property-based testing appeared in all 3 with-skill runs and zero without-skill runs. Token cost is ~1.8x higher (30k vs 17k), which is acceptable for a +28% quality improvement.

Full eval data is in `testing-best-practices-workspace/`.

## Research corpus

The skill was built from analysis of testing patterns across:

- [adewale](https://github.com/adewale) (30 repos) -- property-based testing, mock fidelity, test quality audits
- [simonw](https://github.com/simonw) (datasette, sqlite-utils, llm) -- documentation-as-tests, real databases, VCR cassettes
- [chrischabot](https://github.com/chrischabot) (the-wire, foundry, code-search) -- 5-tier test architecture, API scenario tests, acceptance batteries
- [npryce](https://github.com/npryce) (GOOS co-author) -- factcheck, snodge, make-it-easy, worktorule
- [graydon](https://github.com/graydon) (Rust creator) -- exhaustigen-rs, proptest-arbitrary-interop
- [karpathy](https://github.com/karpathy) -- differential testing against PyTorch/tiktoken
- [bradfitz](https://github.com/bradfitz) (Go team) -- protocol-faithful fake servers
- [joewalnes](https://github.com/joewalnes) -- minimalist testing frameworks (47-line jstinytest)
- [ivanmoore](https://github.com/ivanmoore) -- TDD katas, mock object exercises
- [tirsen](https://github.com/tirsen) -- retry patterns

Research documents are in `research/` and are not part of the shipped skill.

## Project structure

```
testing-best-practices/          # The skill (ships to agents)
  SKILL.md                       # Core instructions (269 lines)
  references/                    # Loaded on demand
    python.md
    typescript.md
    go.md
    rust.md
    antipatterns.md
    test-types.md
    advanced-patterns.md

research/                        # Source material (does not ship)
  LESSONS_FROM_ADEWALE_REPOS.md
  LESSONS_FROM_SIMONW_REPOS.md
  LESSONS_FROM_CHRISCHABOT_REPOS.md
  LESSONS_FROM_PRACTITIONERS.md
  ANTIPATTERNS.md
  DECISION_TREE.md
  NOVEL_TESTING_TYPES.md

evals/                           # Test cases for the skill itself
  evals.json
  files/                         # Fixture code for eval prompts

testing-best-practices-workspace/  # Eval results
  iteration-1/
```

## License

MIT
