# Test-audit campaign records, October 2026

This directory holds the lesson records from the October 2026 test-audit campaign, tagged so that each kind of verification cost can be analysed on its own. The records were first posted as JSON blocks on [issue #32](https://github.com/adewale/testing-best-practices/issues/32), and that issue stays the discussion record. These files are the machine-readable copy used for the later eval and ablation analysis (see `EVAL_ABLATION_DESIGN.md`).

| File | Contents |
|---|---|
| `records.jsonl` | 458 records, one JSON object per line: 320 from the campaign, 43 from the pilot, and 95 from before the campaign. The original fields are unchanged; the fields below are added |
| `classify.py` | The tagging rules and hand labels. `python3 classify.py records.jsonl` re-tags the dataset reproducibly |
| `owner_merges_2026-10-09.json` | What the owner kept and removed in the 11 campaign PRs merged on 2026-10-09, plus the 10 PBT, fuzz and exhaustive PRs the owner merged in the same window, with their budgets |

## Added fields

| Field | Meaning |
|---|---|
| `origin` | `campaign`, `pilot` or `pre-campaign` |
| `source_comments` | The #32 comment or comments where the record was posted |
| `ce` | The candidate-edit rows (#32 index) that the record supports |
| `techniques` | Every testing technique the finding is **about**. Possible values: `mutation`, `pbt`, `fuzz`, `exhaustive`, `golden`, `browser-e2e`, `eval-oracle`, `real-engine-double`, `static-text`. Evidence fields (planted bugs, kill counts) are excluded: they describe how a finding was verified, not what it is about |
| `primary_technique` | One value: the list above, or `example` (ordinary example-based tests), `ci-gate` or `process` (campaign-process records) |
| `verified_by_planted_bug` | True when the record's evidence includes a planted bug. This is mutation-style *verification* by the session that wrote the record. It is not mutation testing as a CI technique |
| `cost_concern` | Whose recurring cost the record discusses: `mutation`, `pbt`, `fuzz`, `exhaustive`, `ci-lane`, `test-runtime`, `eval-tokens` or `none` |
| `cost_direction` | Whether the record's proposal `limits` that cost, `adds` to it, or is `neutral` |
| `owner_outcome` | Empty for now. Holds `kept`, `changed`, `removed` or `pending` once the merge-label pass links records to what the owner did with the resulting change (see `EVAL_ABLATION_DESIGN.md`, section 3) |
| `label_method` | `hand`: 94 records reviewed by hand on 2026-10-09 (all that mention mutation, PBT, fuzzing or cost). `rules-v1`: keyword rules only. Hand-labelled records keep the rule output in `rules_v1` |

## Counts

Primary technique:

| Technique | Records |
|---|---|
| example | 158 |
| process | 64 |
| eval-oracle | 58 |
| real-engine-double | 46 |
| mutation | 45 |
| golden | 33 |
| browser-e2e | 22 |
| static-text | 15 |
| exhaustive | 9 |
| pbt | 4 |
| ci-gate | 4 |

Records that mention a technique at all (any position in `techniques`): mutation 71, PBT 7, fuzzing 3, exhaustive 12.

Cost concern and direction (records with a concern only):

| Concern | Direction | Records |
|---|---|---|
| mutation | limits | 15 |
| test-runtime | limits | 9 |
| exhaustive | limits | 6 |
| mutation | neutral | 3 |
| test-runtime | neutral | 1 |
| ci-lane | limits | 1 |
| pbt | limits | 1 |
| eval-tokens | limits | 1 |

## What the data can and cannot separate

- **Mutation testing.** It is well covered: 45 records are about mutation practice, and 18 discuss mutation cost. Every cost record either limits mutation cost or reports it neutrally; none argues for adding recurring mutation. The pre-campaign records quantify the blow-up:
  - about 170 runner-hours across four lanes, with no product bug from a tool-generated mutant;
  - a nightly lane that needed about 165 minutes under a 90-minute timeout;
  - calendar lanes re-scoring unchanged code.
- **PBT and fuzzing.** These are thinly covered: 4 records are primarily about PBT and **none** about fuzzing. The campaign did not study their cost. The evidence that PBT and fuzzing stay bounded comes from outside the records: the owner's own merges (`owner_merges_2026-10-09.json`) and the owner's statement.
- **"Planted bug" is not "mutation testing".** 217 records were verified with planted bugs: the campaign's mandatory kill tables. That is a one-off verification cost paid by the session, not a recurring CI lane. Analyses of mutation cost should use `cost_concern`, not `verified_by_planted_bug`.
- **Recurring cost added by the campaign shows up in its PRs, not its records.** None of the 94 hand-labelled records argues for adding recurring cost (the other 364 records were not checked for this), yet the campaign PRs added many CI jobs, workflows and schedules, and the owner removed them at merge time. The kept-or-removed labels (`owner_outcome`) are what will capture that.
- **Self-reported minutes (`cost_minutes`)** mix investigation, planted-bug runs and review, so they cannot be split by technique.

## Known limits of the labels

- `rules-v1` labels are keyword matches, accurate enough to route records but not for fine distinctions. Only the 94 `hand` records were reviewed.
- Techniques are multi-label; `primary_technique` is a judgement call where a record spans several.
- Verdicts (`skills.*.verdict`) and `prompted_by` are self-assessed by the session that found the issue.
