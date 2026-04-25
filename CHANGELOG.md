# Changelog

All notable changes to the testing-best-practices skill are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.3] - 2026-04-25

### Changed
- **Renamed core principle** from "Red-Green TDD" to "Red-Green-Refactor TDD" to match Beck's canonical three-step cycle and surface the Refactor step LLM agents most commonly skip
- **Sharpened the Refactor bullet** with Beck's actual wording ("committing whatever sins necessary" for Green; duplication removal for Refactor) and Fowler's behavior-preservation definition

### Added
- **Two Hats rule** (Beck, *Tidy First?*) — behavior changes (Red/Green) and structure changes (Refactor) never share a commit; commit Green before Refactor so reverts are clean
- **Augmented coding warning signs** (Beck, *Augmented Coding: Beyond the Vibes*) listed in the Red-Green-Refactor section: unrequested functionality, unnecessary loops/branches, disabling/deleting tests, hardcoding `__eq__` or test inputs, stubbing tested modules
- **Anti-cheat rule** in Write mode — tests are read-only during Refactor; if a refactor breaks a test, revert (do not edit the test); explicit list of forbidden shortcuts (operator overloads, special-casing test inputs, stubbed modules, weakened assertions)
- **Cheat-scan step** added to the validation loop — agent re-reads its own diff for the documented LLM reward-hacking patterns (ImpossibleBench, METR) before reporting done

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
