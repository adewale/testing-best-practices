# Eval Taxonomy

Every eval in `evals/evals.json` must include a `taxonomy` object so coverage is measurable instead of anecdotal.

## Required taxonomy fields
- `language_framework`: one primary target, e.g. `generic`, `python/pytest`, `typescript/vitest`, `typescript/fast-check`, `typescript`, `go`, `rust`, `unsupported/kotlin`.
- `techniques`: one or more testing techniques exercised by the eval.
- `risk_classes`: one or more risk areas the skill must handle.
- `failure_modes`: one or more failure shapes the eval is designed to catch.

## Technique tags
- `unit`
- `regression`
- `table-driven`
- `property-based`
- `integration`
- `e2e`
- `contract`
- `vcr-recorded-fixture`
- `deterministic-time`
- `characterization`
- `differential`
- `pirate-conformance`
- `mutation`
- `assertion-quality`
- `anti-pattern-detection`
- `doc-sync`
- `golden-snapshot`
- `test-data-builder`
- `correctness-by-construction`
- `mock-fidelity`
- `validation-reporting`
- `isolation`

## Risk-class tags
- `security`
- `external-boundary`
- `type-invariant`
- `flake`
- `scope-control`
- `validation-honesty`
- `mock-drift`
- `maintenance-drift`
- `false-confidence`
- `test-tiering`
- `parser`
- `legacy-refactor`
- `unsupported-language`
- `calibration`
- `porting`
- `oracle-quality`
- `maintainability`

## Failure-mode tags
- `weak-assertion`
- `skipped-test`
- `logging-not-asserting`
- `red-phase-claim`
- `overbroad-universal-rule`
- `assertion-stuffing`
- `unsafe-type-refactor`
- `unsafe-check-deletion`
- `live-network`
- `wall-clock-sleep`
- `implementation-detail-coupling`
- `stale-docs-fixtures`
- `mock-reality-drift`
- `swallowed-exception`
- `integration-misclassification`
- `behavior-change-without-characterization`
- `coverage-inflation`
- `overbroad-e2e`
- `mocked-e2e`
- `fabricated-validation`
- `framework-mismatch`
- `docs-code-drift`
- `blind-snapshot-update`
- `handcomputed-oracle-gap`
- `brittle-fixture-noise`
- `test-order-dependency`
- `global-state-leak`
- `zero-value-invalid-state`
- `over-mocking`

## Minimum release coverage
Before calling the skill improvement complete, the eval matrix should cover:
- All four modes: `write`, `assess`, `upgrade`, `detect`.
- Core languages: at least two evals and at least one critical eval each for Python, Go, TypeScript, and Rust.
- Unsupported-language fallback: at least one eval.
- Techniques: PBT, deterministic time, VCR/recorded fixtures, contract tests, golden/snapshot review, characterization, differential/conformance, mutation, doc-sync, test data builders, and correctness-by-construction.
- Risks: security, flakes, scope control, validation honesty, mock drift, and type invariants.

See `eval-health.md` for eval-obsolescence and drift monitoring. The matrix is a floor, not a permanent benchmark; add probes when real failures appear or model/tool capabilities shift.
