# Code Context

## Files Retrieved
1. `SKILL.md` (lines 1-454) - skill entrypoint, routing triggers, core principles, Assess/Upgrade/Write modes.
2. `references/antipatterns.md` (lines 1-165) - detection table and anti-pattern fixes; overlaps core Assess mode.
3. `references/characterization-testing.md` (lines 1-32) - legacy/refactor characterization guidance.
4. `references/correctness-by-construction.md` (lines 1-377) - canonical deep dive for types/schemas/invariants and defense-in-depth distinction.
5. `references/deterministic-time.md` (lines 1-205) - time flake guidance, virtualization/injection, lint rules.
6. `references/differential-testing.md` (lines 1-79) - differential + pirate/conformance testing.
7. `references/doc-sync-testing.md` (lines 1-40) - code/docs sync patterns.
8. `references/exhaustive-testing.md` (lines 1-38) - bounded-state exhaustive/PBT patterns.
9. `references/go.md` (lines 1-280) - Go-specific test commands, table tests, isolation, fixtures, CI.
10. `references/golden-file-testing.md` (lines 1-231) - golden/snapshot promote workflow and failure modes.
11. `references/mathematical-properties.md` (lines 1-46) - algebraic property tests.
12. `references/mutation-testing.md` (lines 1-36) - mutation testing triggers/tools.
13. `references/python.md` (lines 1-169) - pytest/Hypothesis/fixtures/VCR/CLI/E2E/coverage.
14. `references/rust.md` (lines 1-198) - Rust tests, proptest, exhaustigen, CI, fuzzing.
15. `references/test-data-builders.md` (lines 1-82) - factories/builders/assertion helpers/pinning nondeterminism.
16. `references/test-types.md` (lines 1-254) - decision guide, tiers, trust-boundary lens.
17. `references/typescript.md` (lines 1-215) - Vitest/Jest, fast-check, Playwright, API test infra.
18. `references/vcr-cassettes.md` (lines 1-53) - external API recording/replay guidance.

## Key Code
### Content map
- `SKILL.md` is the router: always read language refs (`references/python.md`, `typescript.md`, `go.md`, `rust.md`) and optionally read topical refs by trigger (`SKILL.md` lines 31-55). It embeds core rules: assertion density/both-directions (`SKILL.md` lines 87-95), real objects over mocks (`SKILL.md` lines 97-108), PBT patterns (`SKILL.md` lines 110-139), E2E (`SKILL.md` lines 141-151), types-vs-tests/correctness by construction (`SKILL.md` lines 197-256), Assess steps (`SKILL.md` lines 281-326), Write validation loop (`SKILL.md` lines 389-438).
- `references/test-types.md` is the decision tree: Step Zero asks whether types replace defensive tests (`references/test-types.md` lines 6-29), then Tier 1/2/3 test types (`references/test-types.md` lines 82-213), plus cost table (`references/test-types.md` lines 235-254).
- `references/correctness-by-construction.md` is now the canonical deep topic: trigger criteria (`lines 1-12`), defense-in-depth anti-pattern vs legitimate defense (`lines 36-102`), tactic A/B invariant tests (`lines 104-216`), language patterns (`lines 218-298`), trust-boundary table (`lines 327-336`).
- Language refs provide framework snippets: Python pytest/Hypothesis/VCR (`references/python.md` lines 3-169), TypeScript Vitest/fast-check/Playwright (`references/typescript.md` lines 3-215), Go stdlib/table/isolation/testdata (`references/go.md` lines 3-280), Rust `#[test]`/proptest/exhaustigen/fuzz (`references/rust.md` lines 3-198).

### Duplicates / drift risks
- **Correctness-by-construction duplicated heavily.** Same Step Zero/tactic A+B/defense-in-depth message appears in `SKILL.md` lines 197-256, 328-366, 393-402, 428-438; `references/test-types.md` lines 6-60 and 214-228; `references/antipatterns.md` lines 119-165; canonical file `references/correctness-by-construction.md` lines 1-377. Quick win: keep only compact summaries outside the canonical file and link to it.
- **Assertion density repeated and somewhat over-universal.** `SKILL.md` says 3+ meaningful assertions per test (`lines 87-88`, `424-425`); `references/test-types.md` repeats for unit tests (`lines 84-86`, `220-221`); `references/antipatterns.md` repeats quality-vs-coverage (`lines 96-102`). But examples often have one assertion (`references/python.md` lines 58-70; `references/mathematical-properties.md` lines 5-31; `references/go.md` lines 49-54). Quick win: rephrase as “target for behavior/example tests; property/table tests may have one strong invariant per case.”
- **VCR guidance duplicated and inconsistent.** VCR appears in `SKILL.md` lines 302-307 and 379-385, `references/test-types.md` lines 136-144, `references/python.md` lines 124-140, `references/vcr-cassettes.md` lines 1-53, and stale snapshot/cassette anti-patterns in `references/antipatterns.md` lines 111-117. Keep `references/vcr-cassettes.md` canonical and link to it from the short versions.
- **Golden/snapshot guidance duplicated but mostly coherent.** Triggers in `SKILL.md` lines 44-47 and 409-410; decision entry in `references/test-types.md` lines 166-175 and 190-193; anti-pattern in `references/antipatterns.md` lines 111-117; full guide in `references/golden-file-testing.md` lines 1-231.

### Missing cross-links
- `references/test-types.md` uses “See the matching reference file” without concrete links for VCR, characterization, differential, golden, pirate, and mutation (`lines 142-202`). Replace with explicit refs: `references/vcr-cassettes.md`, `references/characterization-testing.md`, `references/differential-testing.md`, `references/golden-file-testing.md`, `references/mutation-testing.md`.
- `references/test-types.md` docs/contract entries lack links (`lines 120-134`): add `references/doc-sync-testing.md`; either add a contract-testing reference or point to mock-fidelity sections (`SKILL.md` lines 302-307, `references/typescript.md` lines 134-146, `references/vcr-cassettes.md`).
- `references/antipatterns.md` stale snapshot/cassette section (`lines 111-117`) should link to both `references/vcr-cassettes.md` and `references/golden-file-testing.md`.
- Language refs rarely cross-link to topical refs: `references/python.md` VCR section (`lines 124-140`) should link `references/vcr-cassettes.md`; `references/rust.md` exhaustive section (`lines 121-138`) should link `references/exhaustive-testing.md`; `references/go.md` `testdata/`/fixtures (`lines 191-208`) could link `references/golden-file-testing.md`; time-sensitive language guidance should point to `references/deterministic-time.md`.
- No dedicated references exist for `contract tests`, `E2E`, or `property-based testing` despite being core concepts in `SKILL.md` metadata/description (`lines 1-13`) and body. This is acceptable if language refs are canonical, but the decision guide should say that explicitly.

### Stale / inconsistent claims
- `references/correctness-by-construction.md` lists 7 anti-pattern bullets (`lines 41-63`) but says “In all six cases” (`line 65`). Quick win: change to “In all these cases” or “seven.”
- `references/vcr-cassettes.md` defines VCR as record/replay of real responses (`lines 1-10`) but the TypeScript section is plain MSW hand-written mock data (`lines 27-39`), which conflicts with the “better than hand-written mocks” claim. Quick win: rename that section to deterministic HTTP mock, or replace with an actual TS recording/replay tool/pattern.
- `references/typescript.md` “never throws” PBT example uses `expect(result).toBeDefined()` as the sole assertion (`lines 59-64`), while `SKILL.md` and `references/antipatterns.md` flag `toBeDefined()` as weak when sole assertion (`SKILL.md` lines 293, 443-444; `references/antipatterns.md` line 8). Quick win: assert valid-or-absent / parse shape, or use `expect(() => parse(input)).not.toThrow()` plus a stronger invariant.
- `references/correctness-by-construction.md` says `Email{}` outside a Go package compiles (`lines 294-295`). With unexported fields, external composite literals are not generally the right example; the unavoidable zero value is `var e Email`. Quick win: change wording to “`var e Email` is always constructible” and keep the zero-value caveat.
- `references/go.md` says “Every test should use” table-driven tests (`lines 31-33`). Overbroad for examples, one-off regression tests, property/fuzz tests, and CLI smoke tests. Quick win: “Use table-driven tests when covering multiple input/output cases.”
- `references/test-types.md` says unit tests have “no network/filesystem” (`line 86`) while core guidance prefers real filesystems with temp dirs over mocks (`SKILL.md` lines 99-104) and Go guidance recommends `t.TempDir()` (`references/go.md` lines 60-75). Quick win: distinguish persistent/global FS/network from temp dirs/in-memory/local fakes.
- `SKILL.md` universal “Every test should verify positive AND negative” (`lines 90-92`) is stricter than many property/law examples. Later validation scopes this to security-sensitive tests (`lines 426-427`). Quick win: scope the universal rule to filters/sanitizers/security and “where applicable.”

## Architecture
- One-way navigation dominates: `SKILL.md` links to every `references/*.md`; only `references/antipatterns.md` and `references/test-types.md` link onward to `references/correctness-by-construction.md`. Most other refs are leaf files.
- Decision flow intended by current files: identify mode in `SKILL.md` → read language ref → read `references/test-types.md` for test selection → load topical ref by trigger. `references/correctness-by-construction.md` has become a cross-cutting lens for Write and Assess modes.
- Main maintenance risk is duplicated doctrine in entrypoint + decision guide + anti-pattern + canonical topical docs. The repo would be easier to maintain if `SKILL.md` stayed terse and refs owned details.

## Start Here
Open `SKILL.md` first, especially lines 31-55 and 389-438. It controls which reference files agents load and contains the highest-impact duplicated guidance that should either stay as concise routing text or point to canonical refs.

## Supervisor coordination
No decision needed. Inspection only; no edits made to skill files.
