# testing-best-practices

[![skills.sh](https://skills.sh/b/adewale/testing-best-practices)](https://skills.sh/adewale/testing-best-practices)

An agent skill that enforces testing best practices when writing, reviewing, or improving tests. Built from 25 research documents covering real-world testing patterns across 16 GitHub accounts, three engineering organizations, books, and long-form testing literature; grounded in practitioner work from Kent Beck (TDD) to TigerBeetle (deterministic simulation), Jane Street (expect tests), Ward Cunningham (Fit/customer examples), Salvatore Sanfilippo / antirez (Redis-style differential fuzzing and testability seams), and the complete 404-post Google Testing Blog archive (test sizes, flake data, mutation testing at scale, the test-double canon).

![A typographic ledger of the sixteen testing techniques this skill teaches, organised into three tiers — Always (Unit, Smoke, Regression); When triggered (Property-based, End-to-end, Doc/Code sync, Contract, VCR cassette, Characterization, Differential, Golden file, Pirate/Conformance); With caution (Visual/Screenshot, Mutation, Performance, Fuzz). A top strip frames the red-green-refactor rhythm: a test that fails first, the smallest code that passes, clean up while green.](research/diagrams/skill-ledger.png)

## What it does

When an agent uses this skill, it produces higher-quality tests than it would on its own. Specifically:

- **Property-based tests appear** (Hypothesis, fast-check, proptest) where broad input spaces need more than examples
- **Assertions get stronger**: meaningful behavior/state/error checks replace `toBeDefined()`, truthy/not-empty checks, and logs
- **Error-handling paths are exercised** with injected downstream failures instead of only invalid-input tests
- **Concurrency contracts are pinned** with contention-driving tests and race-detector guidance rather than observational `t.Log` output
- **Better oracles appear**: shadow models, differential checks, statistical/recall thresholds, whole-state digest roundtrips, customer-readable examples, and pre-mask assertions when the risk boundary calls for them
- **Assessments become structured** with severity-prioritized findings (P0/P1/P2/P3) instead of ad-hoc lists
- **Anti-patterns get detected**: skipped/focused tests, logging-instead-of-asserting, mock-everything "integration" tests, weak assertions, sleeps, live-network tests, blind snapshot updates, and fault-masking assertions
- **Language-appropriate patterns** are used: table-driven tests in Go, `#[test]` modules in Rust, Vitest + fast-check in TypeScript, pytest + Hypothesis in Python

## Install

```bash
npx skills add adewale/testing-best-practices
```

Skills appear on skills.sh automatically after users install the repo with the skills CLI. Install counts and leaderboard rankings come from anonymous CLI telemetry; opt out with `DISABLE_TELEMETRY=1`. The repo page customization in `skills.sh.json` is picked up after the repository is seen by telemetry and the cache refreshes.

## Agent compatibility

The installable skill directory is `testing-best-practices`. It uses the Agent Skills `SKILL.md` format and is configured for Codex, OpenCode, Pi, Gemini CLI, and Claude Code.

| Agent/client | Install or use |
|---|---|
| Codex | `cp -R testing-best-practices ~/.codex/skills/testing-best-practices` |
| OpenCode | `cp -R testing-best-practices ~/.config/opencode/skills/testing-best-practices` or use `.opencode/skills/testing-best-practices` in a project |
| Pi | `pi install https://github.com/adewale/testing-best-practices` or `pi --skill testing-best-practices` |
| Gemini CLI | `gemini skills install https://github.com/adewale/testing-best-practices --path testing-best-practices` or copy to `.gemini/skills/testing-best-practices` |
| Claude Code | `npx skills add adewale/testing-best-practices` or copy to `.claude/skills/testing-best-practices` |

## Use

After installation, ask your coding agent to use the skill when tests are being written, reviewed, or repaired:

```text
Use testing-best-practices to review these tests for false confidence, mock drift, flaky timing, weak assertions, and missing error paths.
```

The skill routes itself by task mode (write, assess, upgrade, detect), detects the repository language/framework, then loads only the relevant reference files.

## How it works

The skill operates in four modes:

| Mode | When | What it does |
|------|------|-------------|
| **Write** | Writing new tests | Red-Green-Refactor TDD, property-based tests, boundary values, error-path coverage, concurrency contracts, validation loop |
| **Assess** | Reviewing existing tests | 7-step quality audit: sabotage detection, oracle strength, mock drift, tier integrity, determinism, coverage quality, invariant placement |
| **Upgrade** | Improving weak tests | Prioritized fixes for flaky, weak, or sabotaged tests |
| **Detect** | Finding hidden problems | Unconditional skips, print-not-assert, ordering dependencies, tests that fake coverage |

Language-specific guidance loads on demand based on the project's language. Advanced pattern references load only when their trigger condition matches (e.g., `references/characterization-testing.md` loads only when refactoring legacy code). This keeps token usage efficient.

## What's covered

### Core principles (always loaded, ~4,100 estimated tokens)

- Red-Green-Refactor TDD, with honest red-vs-green evidence reporting
- Test quality over quantity (Kent Beck's Test Desiderata, assertion strength, coverage as a map rather than proof)
- Real behavior over mocks, with a preference hierarchy from real local objects to fakes, stubs, and only then framework mocks
- Property-based testing for broad input spaces and invariants
- Error-handling path testing via injected downstream failures, timeouts, partial responses, and I/O errors
- Concurrency contract testing under contention and race detectors/thread sanitizers
- E2E, integration, contract, documentation-code sync, and external-boundary testing at the smallest useful tier
- Characterization testing for legacy refactors
- Differential, shadow-model, statistical-oracle, pirate/conformance, golden/snapshot, VCR/recorded-fixture, exhaustive, and mutation-style testing when the risk boundary calls for them
- Test data builders, customer-readable examples, fixtures, and logging fakes that keep test intent visible
- Correctness by construction — types/schemas/contracts over repeated runtime checks; invariant-proof tests plus model-gap tests
- Validation loop before reporting done, including checks for weak assertions, skips, sleeps, live network, mock drift, fault masking, and unverified TDD claims

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
| `references/antipatterns.md` | 14 anti-patterns with detection signals, severity levels, and fixes |
| `references/test-types.md` | Decision guide with Step Zero (types-vs-tests), trust-boundary lens, and 3-tier hierarchy |

**Topic-specific** (loaded only when the trigger matches):

| File | Trigger |
|------|---------|
| `references/characterization-testing.md` | Refactoring legacy code |
| `references/differential-testing.md` | Reimplementing algorithms, multi-language SDKs, shadow models, approximate/probabilistic outputs |
| `references/golden-file-testing.md` | Transformation pipelines, snapshot tests, promote workflow, save/load or migration roundtrips |
| `references/deterministic-time.md` | Code depends on time, timers, scheduling, flaky time tests, or background work reachable only by sleeps |
| `references/vcr-cassettes.md` | Code calling external APIs |
| `references/doc-sync-testing.md` | CLI commands or plugin hooks in docs |
| `references/mutation-testing.md` | Verifying test suite catches real bugs |
| `references/exhaustive-testing.md` | Small state spaces (booleans, enums) |
| `references/mathematical-properties.md` | Domain objects with arithmetic |
| `references/test-data-builders.md` | Need factories, fixtures, assertion helpers, or customer-readable examples |
| `references/correctness-by-construction.md` | Same invariant checked at 3+ layers, "should never happen" tests, status enums duplicated across layers, loose strings through the system, or typed language with smart constructors |

## Eval and validation status

The project now uses layered evals rather than a single public prompt table:

| Layer | Current state |
|------|---------------|
| Public prompt evals | 12 cases in `evals/evals.json` across Python, TypeScript, Go, and Rust |
| Development eval suite | 58 cases in `skill-development/evals/evals.json`: 32 write, 12 upgrade, 12 assess, 2 detect |
| Hidden probes | 12 hard/adversarial probes tracked by eval-health metadata |
| Shared benchmark | 39 cases in `evals/shared-benchmark.json` |
| Fixture oracles | 35 fixture oracles; each good sample passes and bad sample fails |
| Mutation mini-repos | 3 seeded mutants killed across JavaScript, Python, and Go |
| Best-practices audit | 110/110, including adversarial-probe coverage for new technique sections |
| Local gate | `python3 skill-development/scripts/check-all.py` passes; `score-skill-version.py` reports 100/100 |

Run the full local non-LLM gate with:

```bash
python3 skill-development/scripts/check-all.py
```

Eval definitions, rubrics, schema, scorecards, and health tracking live under `skill-development/evals/`; historical iteration outputs live under `testing-best-practices-workspace/`.

## Research corpus

Built from analysis of testing patterns across 16 GitHub accounts and three engineering organizations, backed by 25 Markdown research files:

- [kentbeck](https://github.com/kentbeck) -- Test Desiderata (12 properties of good tests), TCR, MoneyPython; books: TDD: By Example (red/green/refactor, test list, green-bar strategies, testing patterns), XP Explained (test-what-might-break, 100% rule, ten-minute build), Tidy First? (behavior vs. structure changes)
- [npryce](https://github.com/npryce) (GOOS co-author) -- factcheck, snodge, make-it-easy, worktorule; GOOS book: walking skeleton, double feedback loop, listen-to-your-tests, mock roles not objects, allow queries / expect commands
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
- [antirez](https://github.com/antirez) (Redis creator) -- differential fuzzing vs. a reference oracle, digest roundtrips, `DEBUG` as a testability surface, recall testing for approximate algorithms, agent-as-QA
- [danluu](https://github.com/danluu) -- random/coverage-guided generation thesis, "world's dumbest fuzzer" (Fuzz.jl: seed/try-catch-log/denylist harness mechanics), differential testing (csv), fault injection (fs-errors), solver-backed generation (kodkod-clj, secvisor-formal-verification)
- [WardCunningham](https://github.com/WardCunningham) (wiki/Fit/CRC inventor) -- Fit customer-readable example tables, CHECKS validation patterns, domain DSLs in test suites (wiki-client), characterization harnesses (sudokuku), test-investment-tracks-lifetime, "preserve and protect [the test suite] as if it were code" (EPISODES)
- [tigerbeetle](https://github.com/tigerbeetle) -- deterministic simulation, state-machine invariants, fault injection, testability by design
- [janestreet](https://github.com/janestreet) -- expect tests, library-level simulation, `Time_source`, Bonsai testing
- [Google Testing Blog](https://testing.googleblog.com/) -- all 404 posts (2007–2026): enforceable small/medium/large test sizes, feedback-loop-over-realism (70/20/10 pyramid → SMURF), fleet-scale flakiness data (size beats tool choice), fidelity-ranked test doubles with owner-maintained fakes and contract suites, DAMP test style, changelist coverage bands, mutation testing with arid-mutant suppression, TotT/incentive-driven testing culture

Research documents are in `research/`: practitioner/account/org lesson notes plus methodology and cross-cutting literature, antipattern, decision-tree, novel-testing, and correctness-by-construction notes. The research process itself is captured in `research/METHODOLOGY.md` — a minimum checklist (GitHub history including actual test files and commit authorship, books, long-form writing, talks/interviews, pre-GitHub tools, post-mortems and criticism), explicitly framed as a floor rather than a ceiling.

## Project structure

```
testing-best-practices/             # The installable skill (ships to agents)
  SKILL.md                          # Core instructions (~240 lines)
  references/                       # Loaded on demand
    python.md                       # Language: Python / pytest / Hypothesis
    typescript.md                   # Language: TypeScript/JavaScript / Vitest/Jest/fast-check/Playwright
    go.md                           # Language: Go
    rust.md                         # Language: Rust
    antipatterns.md                 # Always: detection signals + fixes
    test-types.md                   # Always: decision guide and test-tier hierarchy
    characterization-testing.md     # Topic: legacy code
    correctness-by-construction.md  # Topic: types/schemas/contracts vs tests
    deterministic-time.md           # Topic: clock injection, time virtualization, async/background seams
    differential-testing.md         # Topic: reference implementations, ports, SDKs, shadow/statistical oracles
    doc-sync-testing.md             # Topic: documentation drift
    exhaustive-testing.md           # Topic: small state spaces
    golden-file-testing.md          # Topic: transformation pipelines, snapshot tests, digest roundtrips
    mathematical-properties.md      # Topic: algebraic laws
    mutation-testing.md             # Topic: test quality verification and PIE/fault propagation
    test-data-builders.md           # Topic: factories, fixtures, and customer-readable examples
    vcr-cassettes.md                # Topic: external APIs and recorded fixtures

research/                           # Source material (does not ship)
  METHODOLOGY.md                    # How we research a practitioner (a floor, not a ceiling)
  LESSONS_FROM_*.md                 # One file per practitioner/account/org (incl. LESSONS_FROM_GOOGLE_TESTING_BLOG.md)
  DESIGN_FOR_TESTABILITY_LITERATURE.md
  ANTIPATTERNS.md
  CORRECTNESS_BY_CONSTRUCTION.md
  DECISION_TREE.md
  NOVEL_TESTING_TYPES.md

evals/                              # Public/shared prompt eval assets
  evals.json                        # 12 public prompt evals across 4 languages
  shared-benchmark.json             # 36 shared benchmark cases
  shared-harness.md                 # Shared harness contract
  files/                            # Fixture code for public eval prompts
  fixtures/                         # Runnable prompt fixtures
  oracles/                          # Shared fixture oracle helpers

skill-development/                  # Development-only evals and quality gates
  evals/                            # 54 rubric evals, schema, scorecard, health plan, fixture oracles
  scripts/check-all.py              # Runs all local non-LLM gates
  scripts/                          # Static audit, oracle runners, mini-repos, prompt-eval runner, scoring tools

skills.sh.json                      # skills.sh presentation metadata
skills-lock.json                    # skills CLI lockfile
testing-best-practices-workspace/   # Historical eval results by iteration
```

## Development

Run all local checks before proposing skill changes:

```bash
python3 skill-development/scripts/check-all.py
```

That command runs the static audit, eval-shape checks, fixture oracle self-tests, mutation-backed mini-repos, eval-health report, best-practices audit, and skill version scoring. Generated prompt runs and caches should stay out of the installable skill directory.

## Scope and limitations

- This is an **agent skill**, not a standalone test runner, assertion library, or framework.
- It works generically with any language, but detailed on-demand references currently cover Python, TypeScript/JavaScript, Go, and Rust.
- The local gate is non-LLM and deterministic; prompt-output quality still needs periodic review with hidden/rotating evals as model behavior changes.

## License

MIT
