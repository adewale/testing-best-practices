# Implementation Plan

## Continuation update
- G1/G2 static gates now pass: `scripts/static-audit.py` reports P0=0/P1=0.
- Eval suite now has 27 evals and passes `scripts/score-evals.py` core coverage checks for Python, Go, TypeScript, and Rust.
- Added executable fixture-oracle self-tests via `scripts/run-fixture-oracles.py` for E12, E23, E25, E26, and E27. These are the first non-provisional runtime/static oracles; prompt transcript scoring is still pending.
- Added `evals/eval-health.md` to monitor eval obsolescence, score saturation, proxy gaming, and drift as recommended by “Your Evals Will Break and You Won't See It Coming.”

## Goal
Turn `testing-best-practices` into a compact, calibrated, eval-backed testing skill with canonical references, automated drift checks, and prompt-eval coverage for write/assess/upgrade/detect behavior.

## Gates and Rubrics
- **Scoring rule**: keep rubric dimensions A-H in `evals/rubric.md`; an eval score is the minimum relevant `rubric_focus` dimension, not an average that can hide unsafe behavior.
- **Critical override**: any fabricated validation, skipped/disabled tests as a fix, unsafe deletion of boundary/security checks, weak sole assertion presented as good, or out-of-scope production rewrite scores that eval `0`.
- **G0 baseline gate**: current E01-E14 scores, static P0/P1 hits, and top failure modes recorded before content edits.
- **G1 safety gate**: static P0 count `0`; E01/E02/E03/E04/E05/E08/E12/E14 each score `>=3`.
- **G2 routing gate**: `SKILL.md` target `<=350` lines, hard max `500`; no deep topic repeated in more than two places; all topical refs have explicit triggers.
- **G3 automation gate**: static audit and eval-shape/taxonomy checks pass with stdlib-only commands.
- **G4 release gate**: all critical evals `>=3`, overall average `>=3.3/4`, no broken local links, static P0/P1 count `0`, no non-critical eval below `3` unless explicitly deferred in scorecard.

## Eval Taxonomy
Add these tags to every eval in `evals/evals.json` and document them in `evals/taxonomy.md`:
- **Mode**: `write`, `assess`, `upgrade`, `detect`.
- **Language/framework**: `generic`, `python/pytest`, `typescript/vitest`, `typescript/fast-check`, `go`, `rust`, `unsupported`.
- **Technique**: unit, integration, E2E, PBT, deterministic-time, VCR/recorded-fixture, contract, golden/snapshot, characterization, differential, pirate/conformance, mutation, doc-sync, test-data-builder, correctness-by-construction.
- **Risk class**: security, external-boundary, type-invariant, flake, scope-control, validation-honesty, mock-drift, maintenance-drift.
- **Failure mode**: weak assertion, skipped/sabotaged test, logging-not-asserting, overbroad universal rule, unsafe type-refactor, unsafe check deletion, live network, wall-clock sleep, implementation-detail coupling, stale docs/fixtures.

## Tasks
1. **Phase 0 — Baseline current behavior**
   - File: `progress.md`; new `evals/scorecard.md`
   - Changes: manually run or simulate current E01-E14 prompt evals against the current skill; record score, focus dimensions, red flags, and failure notes. Record current static findings from `context.md`: over-universal assertion rules, VCR/MSW inconsistency, unsafe deletion wording, missing cross-links, stale examples, and `SKILL.md` length.
   - Acceptance: `evals/scorecard.md` has a baseline row for each E01-E14; `progress.md` names G0 as complete and lists the top 5 observed failures.
2. **Define eval schema, taxonomy, and score rubric**
   - File: `evals/evals.json`, `evals/rubric.md`; new `evals/taxonomy.md`; new `evals/schema.json`
   - Changes: add taxonomy tags to existing E01-E14; formalize required eval fields (`id`, `critical`, `mode`, `taxonomy`, `prompt`, `fixture`, `expected_behavior`, `red_flags`, `rubric_focus`); update rubric with the scoring rule, critical overrides, phase gates, and scorecard expectations.
   - Acceptance: every existing eval validates against the schema; taxonomy coverage report shows all four modes and current Python/TS/Go/unsupported cases represented.
3. **Phase 1 — Fix P0/P1 contradictions and unsafe advice**
   - File: `SKILL.md`, `references/typescript.md`, `references/correctness-by-construction.md`, `references/vcr-cassettes.md`, `references/antipatterns.md`, `references/test-types.md`, `references/go.md`
   - Changes: replace the sole `toBeDefined()` fast-check example with valid-or-error/discriminated-union assertions; change “In all six cases” to neutral wording; replace the Go `Email{}` claim with the unavoidable `var e Email` zero-value caveat; reframe `3+ assertions` as a heuristic for example-based behavior/security tests, with explicit exceptions for strong table/property/exception oracles; scope positive+negative assertions to sanitizers/filters/security/transforms where applicable; make TDD a default when feasible with honest red-phase reporting; change integration guidance to allow in-process component integration and temp dirs/in-memory fakes; guard “delete downstream checks/tests” with trust-boundary, adversary, constructor/schema enforcement, and scope-approval preconditions; stop calling hand-written MSW handlers VCR cassettes.
   - Acceptance: manual grep finds no unqualified `Every test should verify positive AND negative`, `An integration test must have at least one real external dependency`, `In all six cases`, or good-example sole `toBeDefined()`; G1 evals score `>=3`.
4. **Phase 2 — Shrink `SKILL.md` into an operational router**
   - File: `SKILL.md`
   - Changes: add a “first 90 seconds” checklist (detect language/framework, read adjacent tests, inspect fixtures/builders, find runner commands, identify existing style); replace repeated correctness-by-construction/VCR/golden doctrine with compact summaries and links; add an activity-based reference matrix; add unsupported-language fallback; add explicit scope rule: when production changes are out of scope, add tests for current API and mention type improvements as follow-up; add final output contract (`tests changed`, `behavior covered`, `commands run/results`, `gaps/risks`).
   - Acceptance: `SKILL.md` is `<=350` target lines or documented exception, `<=500` hard max; every `references/*.md` file has a trigger or is intentionally leaf-only; E01/E10/E11/E12/E13/E14 score `>=3`.
5. **Phase 3 — Canonicalize references and cross-links**
   - File: `references/test-types.md`, `references/antipatterns.md`, `references/python.md`, `references/typescript.md`, `references/go.md`, `references/rust.md`, `references/vcr-cassettes.md`, `references/golden-file-testing.md`, `references/correctness-by-construction.md`
   - Changes: make `references/correctness-by-construction.md`, `references/vcr-cassettes.md`, and `references/golden-file-testing.md` the canonical deep docs; replace “See the matching reference file” with concrete local links; link Python VCR to `references/vcr-cassettes.md`; link Rust exhaustive guidance to `references/exhaustive-testing.md`; link Go `testdata/`/fixtures to `references/golden-file-testing.md`; link time-sensitive language guidance to `references/deterministic-time.md`; state explicitly where no dedicated PBT/E2E/contract reference exists and which language/core sections own that guidance.
   - Acceptance: no `See the matching reference file` remains; local-link checker reports `0` broken links; duplicate deep-topic phrase count is within G2 limits.
6. **Phase 4 — Add automated/static checks**
   - File: new `scripts/static-audit.py`, new `scripts/score-evals.py`, new `evals/schema.json`
   - Changes: implement stdlib-only checks. `static-audit.py` should fail P0 for unsafe contradiction phrases, sole weak assertion examples, VCR/MSW mislabeling, unsafe deletion wording, broken local links, and hard line-count violations; fail P1 for uncalibrated `3+ assertions`, unqualified `Always follow TDD`, unresolved generic cross-link text, and duplicated canonical doctrine. `score-evals.py` should validate `evals/evals.json` against schema, verify taxonomy coverage, list critical evals, and summarize manual scorecards.
   - Acceptance: `python3 scripts/static-audit.py` exits `0`; `python3 scripts/score-evals.py --evals evals/evals.json` exits `0`; scripts require no third-party packages.
7. **Phase 5 — Expand prompt eval cases to cover missing techniques**
   - File: `evals/evals.json`, `evals/taxonomy.md`, `evals/rubric.md`
   - Changes: keep E01-E14, add at least these evals with taxonomy tags, expected behavior, red flags, and rubric focus:
     - `E15-doc-sync-cli-registry`: prompt asks to test docs vs registered CLI commands; expects registry-as-source-of-truth parametrized doc-sync test.
     - `E16-golden-review-discipline`: prompt asks whether to update changed golden/snapshot outputs; expects diff review, explicit approval, volatile-field filtering, no blind snapshot update.
     - `E17-rust-differential-port`: prompt asks to port/verify a tokenizer in Rust against a Python reference; expects differential tests and optional language-neutral conformance fixtures.
     - `E18-test-data-builder-intent`: prompt has brittle inline 12-field fixtures; expects factories/builders/assertion helpers that express intent without hiding required behavior.
     - `E19-detect-order-pollution`: prompt says tests pass alone but fail as a suite due to env/global registry mutation; expects shared-state diagnosis and cleanup/isolation, not skips.
     - `E20-go-zero-value-invariant`: prompt asks whether a Go unexported-field type makes invalid email unconstructible; expects zero-value caveat, smart constructor, and no false `Email{}` external-literal claim.
     - `E21-implementation-detail-mock-call-count`: prompt has tests asserting private method/mock call counts after behavior-preserving refactor; expects public-behavior assertions and minimal mock use.
     - `E22-contract-schema-drift`: prompt has hand-written provider mocks drifting from OpenAPI/real API; expects contract/recorded-fixture checks and no live CI dependency by default.
   - Acceptance: taxonomy matrix covers all four modes, Python/TS/Go/Rust/generic/unsupported, and all listed techniques; each new eval has clear red flags and at least two rubric dimensions.
8. **Phase 6 — Release verification and documentation**
   - File: `progress.md`, `evals/scorecard.md`, optionally `IMPROVEMENT_PLAN.md`
   - Changes: run static/eval-shape checks; rescore full prompt suite; record before/after scores and deferred items. If `IMPROVEMENT_PLAN.md` remains, add a short note that `plan.md`/scorecard are the active implementation tracker or leave it explicitly historical.
   - Acceptance: G4 release gate passes; scorecard shows baseline vs final deltas; unresolved risks are listed with owner/decision needed.

## Files to Modify
- `SKILL.md` - compact router, calibrated defaults, first-90-seconds checklist, scope/fallback rules, final report contract.
- `references/typescript.md` - stronger fast-check examples; no weak sole `toBeDefined()` oracle.
- `references/correctness-by-construction.md` - typo fix, Go zero-value correction, canonical safety wording.
- `references/vcr-cassettes.md` - distinguish recorded cassettes from deterministic hand-written MSW mocks; add safer TS guidance.
- `references/antipatterns.md` - calibrated assertion/integration/deletion guidance and canonical links.
- `references/test-types.md` - calibrated unit rules, temp-dir/in-memory exception, explicit local links, taxonomy-aligned test type language.
- `references/go.md` - table-driven wording and fixture/golden cross-links.
- `references/python.md` - VCR/time/topical cross-links.
- `references/rust.md` - exhaustive/differential/time cross-links.
- `references/golden-file-testing.md` - canonical snapshot/golden review link target if needed.
- `evals/evals.json` - taxonomy tags and new prompt eval cases.
- `evals/rubric.md` - scoring rule, critical overrides, phase gates.
- `progress.md` - phase status and gate results.
- `IMPROVEMENT_PLAN.md` - optional historical note only.

## New Files
- `evals/taxonomy.md` - authoritative eval dimensions, tags, and coverage expectations.
- `evals/schema.json` - machine-checkable eval JSON schema.
- `evals/scorecard.md` - manual baseline/final scores and failure notes.
- `scripts/static-audit.py` - deterministic markdown/static policy checks.
- `scripts/score-evals.py` - eval schema/taxonomy/scorecard validator and coverage reporter.

## Dependencies
- Phase 0 baseline must happen before any skill/reference edits.
- Rubric/schema/taxonomy must be defined before adding new evals or writing score scripts.
- Phase 1 safety fixes should land before the `SKILL.md` shrink so contradictions are removed before content is moved.
- Static-audit banned phrase checks depend on Phase 1 wording decisions to avoid false positives.
- Full prompt rescoring depends on Phase 2/3 content refactor and Phase 5 eval expansion.

## Risks
- Over-shrinking `SKILL.md` may hide essential guidance; mitigate with explicit reference matrix and prompt eval gates.
- Regex static checks can false-positive on anti-pattern examples; scripts need allowlisted code fences/sections or severity annotations.
- Type-vs-test guidance can cause scope creep; E04/E14 and the scope rule must block unapproved production refactors.
- VCR guidance for TypeScript may become tool-stale; verify any named recorder before adding it, or keep guidance tool-neutral and describe MSW only as deterministic mock/fixture replay.
- Manual prompt evals can be subjective; use focus-dimension minimum scores, red flags, and scorecard notes to make grading reproducible.
- No runtime prompt harness currently exists; automation can validate eval structure and static doctrine, but behavioral scoring remains manual unless a harness is added later.
