# Academic Eval Improvements Implemented

This summarizes the requested five improvements.

## 1. Hard hidden evals targeting old-skill weaknesses

Added E28–E32 to `evals/evals.json`:

| Eval | Targets |
|---|---|
| E28 hidden Go assertion calibration | old 3+ assertion overreach |
| E29 hidden TypeScript PBT weak oracle | old `toBeDefined()` PBT example |
| E30 hidden in-process integration | old external-dependency-only integration rule |
| E31 hidden correctness/security deletion | old unsafe deletion wording |
| E32 hidden VCR/MSW distinction | old MSW-as-VCR confusion |

These are marked `hidden: true`, `difficulty: hard/adversarial`, and have known/proposed discrimination metadata.

## 2. Claim/warrant/backing/rebuttal fields

Every eval in `evals/evals.json` now has a `validity` object:

- `claim`
- `warrant`
- `backing`
- `rebuttals`

This follows argument-based validity: the score must say exactly what interpretation it supports and what could invalidate it.

## 3. Difficulty/discrimination/saturation metadata

Every eval now has `eval_health`:

- `difficulty`
- `saturation_status`
- `known_discriminates_versions`
- `last_reviewed`

Added `scripts/eval-health-report.py`, which reports saturated public evals and discriminating hidden probes.

## 4. Mini-repos with seeded mutants

Added mutation-backed mini-repos:

| Mini-repo | Good behavior | Mutant killed |
|---|---|---|
| `evals/mini-repos/e01-js-sanitizer` | safe URL preservation + javascript rejection | sanitizer lets `javascript:` through |
| `evals/mini-repos/e23-python-parser` | parser returns Config or structured ParseError | parser crashes / malformed error |
| `evals/mini-repos/e25-go-report` | temp-dir report write + notifier error propagation | notifier failure swallowed |

Added `scripts/run-mini-repos.py`. Current result:

```text
e01-js-sanitizer: good=pass mutant=killed
e23-python-parser: good=pass mutant=killed
e25-go-report: good=pass mutant=killed
OK: 3 mini-repo mutants killed
```

## 5. Pairwise/version comparison

Added:

- `evals/version-rubric.md`
- `scripts/score-skill-version.py`
- `version-scores/*.json`
- updated `VERSION_COMPARISON.md`

Version scores:

| Version | Artifact rubric | Static audit | Fixture prompt oracles |
|---|---:|---:|---:|
| First GitHub `6951b7d` | 28/100 | 6 P0 / 4 P1 | 10/10 |
| Current GitHub `6e8cd8b` | 69/100 | 6 P0 / 6 P1 | 10/10 |
| Local working tree | 100/100 | 0 P0 / 0 P1 | 10/10 |

The key finding: public prompt oracles are saturated across all three versions; artifact scoring distinguishes them.

## Token impact

See `TOKEN_REPORT.md`.

Local vs current GitHub:

- `SKILL.md` approx tokens: 5,572 → 2,745 (**-50.7%**)
- installable total approx tokens: 26,305 → 23,948 (**-9.0%**)

## Current local gates

`python3 scripts/check-all.py` now runs:

1. static audit,
2. eval suite coverage,
3. fixture oracle self-tests,
4. mini-repo mutant checks,
5. eval-health report,
6. local skill artifact rubric.

Current result: all pass.
