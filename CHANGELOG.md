# Changelog

All notable changes to the testing-best-practices skill are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- **Core principle #10: Correctness by construction** — push invariants into
  types/schemas/contracts so the wrong state is unrepresentable; the two
  test tactics that survive are (A) invariant-proof PBT and (B) model-gap
  tests that try to construct each forbidden state. Anchored in the
  Hoare → Dijkstra → Meyer → Praxis/SPARK → seL4 → Minsky → King → LangSec
  lineage.
- **`references/correctness-by-construction.md`** — on-demand reference with
  language-specific patterns (TS branded types, Rust newtype, Python smart
  constructor, Go unexported field), right-when/still-necessary lists, and
  the canonical sources.
- **Antipattern #13: Logical defense-in-depth (shotgun validation)** — added
  to both `references/antipatterns.md` (skill) and `research/ANTIPATTERNS.md`.
  Detection signals: repeated validation everywhere, loose strings flowing
  through layers, status enums duplicated across layers, catch-all retries,
  silent fallback behavior, post-hoc sanitizer patches, runtime guards
  instead of state machines / types / schema constraints.
- **Step Zero** in Write mode and the decision tree — *can the type replace
  the test?* — with a worked table mapping common "rejects X" tests to
  their type-level alternative.
- **Assess-mode Step 7** — detect logical defense-in-depth via the concrete
  signal list.
- **Validation-loop check 6** in Write mode — "did you cover both invariant
  tactics (A invariant-proof + B model-gap)?"
- **Trust-boundary lens** in `references/test-types.md` and
  `research/DECISION_TREE.md` — untyped input → typed interior → untyped
  output, with the corresponding test types per boundary.
- **`research/CORRECTNESS_BY_CONSTRUCTION.md`** — research note framing the
  thesis with full canonical lineage and the legitimate home of
  defense-in-depth (NIST SP 800-39 / 800-53 PL-8(1) / 800-82; Roman
  military doctrine).

### Changed
- **README**: core-principles list now includes correctness-by-construction;
  reference-files table includes the new on-demand reference;
  `antipatterns.md` count updated to 13.
- **SKILL.md numbering**: "Test the sad path" renumbered from §10 to §11 to
  make room for correctness-by-construction at §10.

## [0.3] - 2026-05-19

### Changed
- Renamed core principle from "Red-Green TDD" to "Red-Green-Refactor TDD" to match Beck's canonical three-step cycle (SKILL.md, README.md, DECISION_TREE.md)

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
