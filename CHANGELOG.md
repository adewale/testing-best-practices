# Changelog

All notable changes to the testing-best-practices skill are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- **Core principle: Test error-handling paths, not just invalid input** — inject the downstream failure (a fake/stub that raises, an injected I/O error, a `side_effect` exception) and assert the system degrades correctly. Backed by the empirical "most critical failures are shallow" finding. Includes a scope-control clause: assert the failure behavior the code *actually* has; do not invent a retry budget, error type, or rollback the contract never promised — characterize and flag the gap instead.
- **Research: `research/LESSONS_FROM_DANLUU.md`** — lessons from Dan Luu (danluu.com/testing + GitHub: Fuzz.jl harness mechanics, csv differential testing, fs-errors fault injection, kodkod-clj/secvisor formal-methods thread). Corpus now 14 accounts.
- **Eval `E33-python-fault-injection-error-paths`** — runnable fixture oracle (good/bad samples) plus prompt-eval entry guarding the error-path principle.
- **Eval `E34-hidden-fault-injection-unprompted`** — adversarial hidden probe: the prompt fixes the contract (failures propagate, no retries), so inventing retry/wrapping is unambiguously scope creep. Now 6 hidden hard/adversarial probes.
- **`skill-development/scripts/run-prompt-evals.py`** — before/after prompt-eval runner with pluggable generation backends (sub-agent via `--candidate-dir`, shell via `--agent-cmd`) and a rubric judge backend (`--judge-cmd`, e.g. `claude -p`) that computes eval score = min(rubric_focus dims) with the critical-failure override.

## [0.3] - 2026-05-21

### Added
- **Core principle #10: Correctness by construction** — push invariants into types/schemas/contracts so the wrong state is unrepresentable; surviving test tactics are invariant-proof PBT and model-gap tests that try to construct each forbidden state.
- **`references/correctness-by-construction.md`** — on-demand reference with TypeScript branded types, Rust newtypes, Python smart constructors, Go unexported fields, right-when/still-necessary checks, and canonical sources.
- **Step Zero decision tree** — ask “can the type replace the test?” before writing another rejection test.
- **Trust-boundary lens** in `references/test-types.md` — untyped input → typed interior → untyped output, with test types matched to each boundary.
- **Antipattern #13: Logical defense-in-depth / shotgun validation** — repeated validation everywhere, loose strings through layers, duplicated status enums, runtime guards instead of state machines/types/schema constraints.
- **Eval development workspace** in `skill-development/` with rubrics, taxonomy, scorecards, version comparison, and non-LLM gates.
- **32 eval definitions** with claim/warrant/backing/rebuttal validity metadata and difficulty/saturation/discrimination health metadata.
- **5 hidden hard/adversarial eval probes** for assertion calibration, weak PBT oracles, in-process integration classification, correctness-by-construction deletion safety, and VCR/MSW distinction.
- **10 fixture-backed public oracles** covering Python, Go, TypeScript, and Rust.
- **3 mutation-backed mini-repos** that kill seeded JS/Python/Go mutants.
- **Best-practices audit gate** for installable-skill boundaries, generated artifact hygiene, schema coverage, eval metadata, hidden probes, and mutation-backed fixtures.
- **Token report** comparing first GitHub, previous GitHub, and current skill versions.

### Changed
- **`SKILL.md` router refactor** — cut the always-loaded entrypoint from ~5,572 estimated tokens in the previous GitHub version to ~2,745 estimated tokens while preserving reference breadth.
- **Reference calibration fixes** in TypeScript, Go, test-types, antipatterns, VCR cassettes, and correctness-by-construction guidance.
- **Red-Green TDD renamed to Red-Green-Refactor TDD** to match Beck’s canonical cycle.
- **Assertion guidance calibrated** — assertion density is a smell/heuristic, not a universal “3+ assertions per test” rule.
- **Integration-test guidance calibrated** — in-process component-boundary integration is valid; external dependencies are not required just to earn the label.
- **VCR guidance clarified** — hand-written MSW mocks are deterministic mocks, not recorded cassettes.
- **Correctness-by-construction deletion guidance hardened** — delete redundant same-invariant checks only after proving boundary/type enforcement; keep auth/security/output-escaping defense-in-depth.
- **Eval scoring split into layers**: artifact rubric, static audit, fixture oracles, mini-repo mutation checks, and best-practices audit.

### Removed
- Generated prompt-run outputs and Python caches from tracked source; raw `skill-development/eval-runs/` are now local/generated artifacts.
- Development/eval artifacts from the installable skill directory; installable contents are limited to `SKILL.md` and `references/*.md`.

### Eval Results
- Skill artifact rubric: first GitHub `28/100`, previous GitHub `69/100`, v0.3 `100/100`.
- Static audit: previous GitHub `6 P0 / 6 P1`, v0.3 `0 P0 / 0 P1`.
- Fixture prompt oracles: first/current/v0.3 all `10/10`, confirming public oracle saturation rather than release-quality discrimination.
- Mini-repo mutants killed: `3/3`.
- Best-practices audit: `100/100` after hygiene fixes.
- Final local gate: `python3 skill-development/scripts/check-all.py` passes.

### Token Impact
- `SKILL.md`: ~5,572 → ~2,745 estimated tokens vs previous GitHub main (**-50.7%**).
- Full installable skill: ~26,305 → ~23,948 estimated tokens (**-9.0%**).

## [0.2] - 2026-04-11

### Added
- **4 supported languages**: Python, TypeScript, Go, Rust (was Python + TypeScript only)
- **9 topic-specific reference files** with conditional loading (characterization testing, differential testing, golden file testing, VCR cassettes, doc-sync testing, mutation testing, exhaustive testing, mathematical properties, test data builders) — each loads only when its trigger condition matches
- **Kent Beck's Test Desiderata** integrated into quality assessment framing (12 properties of good tests that conflict with each other)
- **3 new PBT invariant patterns**: associativity, commutativity, distributivity — plus language integration tests (test `sum()`, `sorted()`, set membership with your domain objects)
- **Fixture-based golden file testing** pattern from kepano/defuddle (auto-discover, auto-baseline, zero-code test creation)
- **Characterization testing** pattern from Michael Feathers (capture current behavior before refactoring)
- **Pirate testing** pattern for language-neutral conformance suites
- **File tree builders** for filesystem tests (nested objects → directory structures)
- **Validation loop** in Write mode — agent self-checks assertion density and antipatterns before reporting done
- **Ordering dependency detection** in Detect mode
- **Go-specific patterns**: `testdata/` convention, `t.Helper()`, `t.Cleanup()`, `TestMain`, Example tests as documentation
- **10 eval cases** across all 4 languages (was 3, Python-only)
- **Weak test fixtures** for TypeScript (`weak_tests.ts`) and Go (`weak_tests.go`) for assess-mode evals
- **Rust eval fixture** (`config_parser.rs`) for write-mode eval

### Changed
- **Split `advanced-patterns.md`** (747 lines, 5,485 tokens) into 9 focused topic files (32-82 lines each) — typical task now loads ~7,200 tokens instead of ~12,000-16,000 (~50% reduction)
- **Conditional loading guidance** in SKILL.md — each topic file has a specific trigger ("Refactoring legacy code? → read characterization-testing.md") instead of generic "read advanced-patterns.md"
- **Validation loop is language-agnostic** — guidance-based, not script-based
- **README rewritten** to match actual skill structure (15 reference files, 10 evals, 13 research accounts)

### Removed
- `scripts/check_test_quality.py` — Python-only, replaced by language-agnostic validation loop guidance
- `advanced-patterns.md` — split into 9 topic files

### Research
- Added **Kent Beck** (Test Desiderata, TCR, MoneyPython mathematical property tests)
- Added **Mary Rose Cook** (gitlet test suite, file tree builders, pinned time)
- Added **Steph Ango / kepano** (defuddle fixture-based golden file testing)
- Split combined `LESSONS_FROM_PRACTITIONERS.md` into 7 individual files (one per practitioner)

### Eval Results
- Iteration 1: 96% (24/25) — 3 evals, Python + TypeScript
- Iteration 2: 100% (25/25) — 3 evals, same languages
- Iteration 3: 100% (49/49) — 7 evals, Python + TypeScript + Go + Rust

## [0.1] - 2026-04-11

### Added
- Initial release
- Core SKILL.md with 4 operational modes (Write, Assess, Upgrade, Detect)
- 10 core testing principles (Red-Green TDD, quality over quantity, real objects over mocks, PBT, E2E, doc-sync, characterization, differential, test data builders, sad path)
- Language-specific references for Python and TypeScript
- Go and Rust language references
- Antipatterns reference (12 anti-patterns with detection/fix/prevention)
- Test-type decision guide (3-tier hierarchy)
- Research corpus from 10 GitHub accounts
- 3 eval cases with iteration-1 results (96% with-skill vs 68% without-skill)
