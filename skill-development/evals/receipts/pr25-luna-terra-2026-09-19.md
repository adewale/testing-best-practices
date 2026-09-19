# PR 25 focused Luna/Terra eval receipt

- Date: 2026-09-19
- Runner: `skill-eval-harness` 0.6.0, Codex CLI backend
- Models: `gpt-5.6-luna`, `gpt-5.6-terra`
- Reasoning: `model_reasoning_effort=low` (explicit runner argument)
- Variants: paired `with_skill` / `without_skill`, one run per cell
- Generation commit: `e6f795045c64490661782f1d4b5aff287a9d1067`
- Final grading commit: `4cc3d1beb6564823571897862f64df64e1ff1f70`
- Skill tree: `4cb7015f69c2f2583136de19cab82be2e8ee4623`
- Combined output digest: `b2ef1cd78ec321f603c3d619397e842db38208d2d90d9a344ba71d2422e28110`

## Scope and results

The focused panel covers the six Google-derived shared cases. Each cell was
graded by its checked-in deterministic fixture oracle with script execution
enabled.

| Case | Luna without | Luna with | Terra without | Terra with |
|---|---:|---:|---:|---:|
| E55 independent URL expectations | pass | pass | pass | pass |
| E57 DAMP/shared fixture assessment | pass | pass | pass | pass |
| E58 keep whole-state roundtrip | pass | pass | pass | pass |
| E59 narrow deposit assertions | pass | pass | pass | pass |
| E60 fake/real contract weld | **fail** | pass | pass | pass |
| E61 suite-shape assessment | pass | pass | pass | pass |
| **Total** | **5/6** | **6/6** | **6/6** | **6/6** |

E60's Luna baseline failed collection because it generated invalid Python:
`def test_delete_missing_key_is harmless(store):`. This is a generation typo,
not a testing-strategy error. It gives the paired result a +1 observed delta,
but does not support a broad quality-lift claim. The useful conclusion is that
the skill introduced no failures on this panel. The model read the mounted
skill in 11 of 12 with-skill cells; Terra E59 passed without a recorded skill
read and is therefore not evidence of treatment uptake.

## Usage

Token counts are provider trace totals. They include repeated/cached context
across tool turns and should be read as a spend ledger, not prompt length.

| Model / variant | Runs | Input | Output | Total | Elapsed |
|---|---:|---:|---:|---:|---:|
| Luna / with skill | 6 | 365,173 | 7,294 | 372,467 | 240.339s |
| Luna / without skill | 6 | 71,924 | 2,873 | 74,797 | 104.378s |
| Terra / with skill | 6 | 423,985 | 6,581 | 430,566 | 191.589s |
| Terra / without skill | 6 | 79,500 | 2,501 | 82,001 | 89.695s |
| **Total** | **24** | **940,582** | **19,249** | **959,831** | **626.001s** |

## Commands

The generation command was prepared with:

```bash
skill-benchmark prepare evals/shared-benchmark.json \
  --split tune \
  --models gpt-5.6-luna,gpt-5.6-terra
```

Each model lane used the equivalent of:

```bash
skill-benchmark run-codex \
  --tasks <focused-six-case-jsonl> \
  --runs <isolated-runs-dir> \
  --timeout 600 \
  --codex-cmd 'codex exec --json -c model_reasoning_effort=low'
```

Grading used the pinned runtime dependency:

```bash
uv run --offline --with pytest==9.1.1 \
  skill-benchmark grade evals/shared-benchmark.json \
  --runs <isolated-runs-dir> --split tune --allow-scripts
```

Raw transcripts remain untracked scratch artifacts by repository policy. The
receipt preserves exact identities, revisions, totals, and a digest, but does
not make the stochastic generation itself reproducible.
