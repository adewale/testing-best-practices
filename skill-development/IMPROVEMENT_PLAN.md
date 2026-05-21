# Testing Best Practices Skill Improvement Plan

This is the active measurement plan. Supporting artifacts:
- Research: `research.md`
- Detailed phase plan: `plan.md`
- Rubric: `evals/rubric.md`
- Eval suite: `evals/evals.json`
- Taxonomy: `evals/taxonomy.md`
- Scorecard: `evals/scorecard.md`
- Eval health/obsolescence plan: `evals/eval-health.md`
- Static audit: `scripts/static-audit.py`
- Eval validator: `scripts/score-evals.py`
- Fixture oracle runner: `scripts/run-fixture-oracles.py`
- All local gates: `scripts/check-all.py`

## Objective
Improve `testing-best-practices` from a broad, partly contradictory testing guide into a compact, calibrated, eval-backed coding-agent skill.

This plan also accounts for Lun Wang's “Your Evals Will Break and You Won't See It Coming”: our evals must monitor their own obsolescence. Static prompt evals are not enough; we need language coverage, runtime/fixture evidence, score saturation checks, and rotating probes when model/tool behavior changes.

The improvement is successful only when:
- known P0/P1 documentation contradictions are gone,
- critical prompt evals score at least 3/4,
- the eval matrix covers the major references/techniques,
- the agent reports validation honestly,
- generated/upgraded tests catch seeded bugs or documented failure modes instead of merely increasing coverage.

## What we learned from similar skills
Verified sources and exact raw URLs are in `research.md`.

- **Impeccable**: broad skills need setup/context loading, command routing, and explicit anti-pattern bans. Apply as a first-90-seconds testing checklist plus mode-specific report contracts.
- **Modern Web Guidance**: fast-changing domains need trigger/skip lists and version/freshness checks. Apply as source/version metadata for language/framework references.
- **Matt Pocock TDD**: test through public behavior and avoid “horizontal slicing.” Apply as one behavior per red-green slice.
- **Obra TDD**: TDD claims require observed failing tests. Apply as command-evidence gates.
- **Currents Playwright**: large testing domains need activity-based reference matrices. Apply by shrinking `SKILL.md` and lazy-loading topical refs.
- **Antfu Vitest**: generated/versioned framework references are compact and source-linked. Apply freshness metadata and framework-specific evals.
- **Dotnet assertion/anti-pattern/gap skills**: split assertion quality, anti-pattern detection, and mutation-style gap analysis. Apply separate eval modes and scoring dimensions.

## Current status
- Static audit improved from baseline **P0=6/P1=6** to **P0=0/P1=0**.
- `SKILL.md` is now 212 lines, below the 350-line router target.
- Eval validator passes with 27 evals and core coverage for Python, Go, TypeScript, and Rust.
- Prompt/runtime scores remain unfilled until transcripts are added, but 10 runnable fixture oracles now self-test good/bad samples for E01, E08, E12, E19, E20, E23, E24, E25, E26, and E27.

## Gates

### G0 Baseline
Run before editing `SKILL.md` or references:
```bash
python3 scripts/static-audit.py || true
python3 scripts/score-evals.py --evals evals/evals.json
```
Then fill `evals/scorecard.md` with baseline prompt scores.

### G1 Safety fixes
Required before router refactor:
- No good-example sole `toBeDefined()` / `toBeTruthy()` assertions.
- No “six cases” contradiction.
- VCR docs distinguish recorded cassettes from hand-written MSW mocks.
- Integration tests may be in-process component integration; no external dependency requirement.
- Positive+negative assertions scoped to filters/security/transforms where applicable.
- Correctness-by-construction deletion guidance guarded by trust-boundary, adversary, constructor/schema, boundary-test, and scope checks.

Gate: `scripts/static-audit.py` reports P0 = 0 and critical evals E01/E02/E03/E04/E05/E08/E12/E14 score >=3.

### G2 Router refactor
Turn `SKILL.md` into an operational router:
- first-90-seconds checklist,
- mode matrix,
- activity-based reference matrix,
- unsupported-language fallback,
- scope-control rule,
- final output contract.

Gate: `SKILL.md` <=500 lines hard max, target <=350; no deep topic repeated in more than two places; E01/E10/E11/E12/E13/E14 score >=3.

### G3 Reference canonicalization
Make each deep topic owned by one canonical reference. Add explicit cross-links and remove vague “matching reference” language.

Gate: no broken local links; no unresolved generic reference pointers; language refs point to topical refs for VCR, time, golden, exhaustive, mutation, and correctness-by-construction.

### G4 Measurement/release
Gate:
- static P0 = 0,
- static P1 = 0 or explicitly deferred,
- all critical evals >=3,
- overall eval average >=3.3/4,
- eval validator passes,
- scorecard records before/after deltas and evidence paths.

## Eval strategy
`evals/evals.json` now contains 27 evals across Write, Assess, Upgrade, and Detect modes. It covers Python, Go, TypeScript, and Rust with at least two evals and at least one critical eval per language family. Each eval has:
- taxonomy tags,
- expected behavior,
- red flags,
- rubric focus dimensions,
- static/runtime/judge measurement notes.

The eval score is the minimum relevant rubric dimension, not an average that can hide unsafe behavior. Critical-failure overrides in `evals/rubric.md` force score 0.

## Automation strategy
- `scripts/static-audit.py` is the regression gate for known contradictions and now passes after G1/G2 doc fixes.
- `scripts/score-evals.py` validates eval shape, taxonomy coverage, and core language coverage with no third-party dependencies.
- `scripts/run-fixture-oracles.py` runs good/pass and bad/fail self-tests for fixture oracles across validation honesty, Python, Go, Rust, TypeScript, deterministic time, order pollution, and Go zero values.
- `scripts/check-all.py` runs all local non-LLM gates.
- `evals/eval-health.md` defines obsolescence monitoring: saturation, proxy gaming, correlation drift, stale framework assumptions, and rotating probes.
- Scores remain provisional until backed by a saved prompt transcript/log or candidate patch validated by the relevant fixture oracle.

## Immediate next work
1. Fill baseline/final prompt scores with saved transcripts.
2. Wire fixture oracles into any future prompt runner so candidate patches are checked automatically.
3. Add broader candidate-project fixtures for remaining high-value evals: E07/E22 contract drift and E10 mutation/gap analysis.
4. Add rotating hidden variants once core fixtures exist.
