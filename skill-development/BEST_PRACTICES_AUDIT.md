# Best-Practices Audit After Initial Push

Audit date: 2026-05-21.

## Best-practice checks used

Implemented `scripts/audit-best-practices.py` to keep the academic/eval hygiene checks executable:

1. installable skill boundary stays clean,
2. generated eval runs/caches are not tracked,
3. every eval has claim/warrant/backing/rebuttals,
4. every eval has difficulty/saturation/discrimination metadata,
5. at least 5 hard/adversarial hidden probes exist,
6. mutation-backed mini-repos exist for JS/Python/Go,
7. schema validates hidden/validity/eval-health metadata,
8. `.gitignore` excludes generated artifacts.

## Findings before fixes

```json
{
  "score": 65,
  "total": 100,
  "percent": 65.0,
  "failed": [
    "102 tracked generated run/cache artifacts",
    "schema did not cover hidden/validity/eval_health metadata",
    ".gitignore did not cover caches and eval-runs"
  ]
}
```

## Fixes applied

- Removed tracked generated `skill-development/eval-runs/` outputs.
- Removed tracked Python `__pycache__`/`.pyc` files from mini-repo fixtures.
- Added repo `.gitignore` rules for Python caches, Node/build outputs, and generated eval runs.
- Updated `scripts/run-mini-repos.py` to set `PYTHONDONTWRITEBYTECODE=1`.
- Updated `evals/schema.json` to validate `hidden`, `validity`, and `eval_health` fields.
- Updated `scripts/score-evals.py` to require and validate `validity` and `eval_health` metadata.
- Added `scripts/audit-best-practices.py` to `scripts/check-all.py`.
- Updated docs to treat raw prompt-run directories as local/generated, with summaries tracked in scorecards.

## Findings after fixes

```json
{
  "score": 100,
  "total": 100,
  "percent": 100.0
}
```

## Score changes

| Score layer | Before audit fixes | After audit fixes | Change |
|---|---:|---:|---:|
| Best-practices audit | 65/100 | 100/100 | +35 |
| Skill artifact rubric | 100/100 | 100/100 | 0 |
| Static audit | 0 P0 / 0 P1 | 0 P0 / 0 P1 | unchanged pass |
| Eval suite count | 32 | 32 | unchanged |
| Public fixture oracle self-tests | 10/10 | 10/10 | unchanged pass |
| Mini-repo mutants killed | 3/3 | 3/3 | unchanged pass |
| Eval-health hidden discriminators | 5 | 5 | unchanged |

## Token impact

The best-practice fixes did not change the installable skill contents. Token usage for the installable skill remains:

| Version | `SKILL.md` approx tokens | Installable approx tokens |
|---|---:|---:|
| GitHub baseline `6e8cd8b` | 5,572 | 26,305 |
| Current local | 2,745 | 23,948 |

Current local vs old GitHub baseline:

- `SKILL.md`: 5,572 → 2,745 (**-50.7%**)
- installable total: 26,305 → 23,948 (**-9.0%**)

The entrypoint remains much smaller; dev/eval hygiene improved without increasing installable tokens.
