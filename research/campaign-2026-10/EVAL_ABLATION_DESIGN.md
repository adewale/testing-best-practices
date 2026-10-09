# Eval and ablation design for the October 2026 candidate edits

Status: **draft, 2026-10-09.** Nothing in this file is a decision. The skill stays frozen at `main` @ `0e4617d` until the analysis below has run and the owner has chosen what to ship.

## 1. The question

Issue #32 indexes 58 candidate-edit rows (CE). 15 have already shipped (CE-001 to CE-015) and 43 are candidates (CE-020 to CE-062). The question is:

> Which combination of the 43 candidate edits makes an agent using the skill write better tests, without making it propose verification the project cannot afford, and without costing more context than it earns?

"Better" has three parts. Each is measured separately and never pooled:

| Signal | What it measures | Source |
|---|---|---|
| **Lift** | The agent does the right thing more often with the edit than without | Deterministic fixture oracles (section 5) |
| **Restraint** | The agent does not over-apply the edit where a counterexample says it is wrong | Restraint probes built from counterexamples |
| **Cost respect** | The agent does not add CI lanes, schedules, mutation gates or oversized budgets the project would reject | A diff scan of the answer, plus the owner's merge labels (section 3) |

## 2. Principles

1. **Cheap deterministic oracles first.** A cheap bug must not become an expensive eval. Each case is decided by the cheapest oracle that can decide it: a pattern check, then a runtime check, and only then a blinded model judge (section 5).
2. **No exponential designs.** A full factorial over 43 edits would need 2^43 (about 8.8 trillion) skill variants, the same blow-up the owner has seen with mutation testing. The design screens edits one at a time, tests interactions only inside small families, and confirms by leaving one out (section 7). Each stage has a run budget fixed in advance (section 9).
3. **Self-assessment is never the outcome.** Each record's `skills.*.verdict` and `prompted_by` fields were written by the session that found the problem. They are used to choose cases, never to score them.
4. **The three costly techniques stay separate.** Mutation testing, property-based testing (PBT) and fuzzing are labelled, measured and reported apart. `verified_by_planted_bug` describes how a finding was verified; it is never used as a mutation-cost signal.
5. **The evals obey the same cost standard as the projects.** They run on demand, never on a schedule, and add no CI jobs to this repository.
6. **Pre-register.** This design, the fixture set and the decision thresholds are frozen at a recorded commit before stage 1 runs. Any change made after seeing results is logged as a deviation, with its reason.

## 3. Turning merge-time rework into labels

This section explains what "turn your merge-time rework into labels" means, and why it matters most.

### The problem it solves

Every finding in the dataset was judged good by the session that made it. That is self-assessment. The only independent judgment we have is what the owner did when merging. Before merging 11 campaign PRs on 2026-10-09, the owner reworked each one: some changes stayed, some were cut back, some were deleted. The diff between the head the campaign left and the head the owner merged records those judgments. At the moment, that information exists only as prose in one comment on #32. A label turns each judgment into a data point that an analysis can count.

### The unit

A **change unit** is one coherent thing a campaign session added to a PR: a fix, a test, a CI job, a budget setting, a script, or a doc section. One unit usually corresponds to one file, or one group of hunks with a single purpose.

Each unit gets one outcome:

| Outcome | Meaning | Example from the 2026-10-09 merges |
|---|---|---|
| `kept` | Merged unchanged, or moved without a change in meaning | tts-playground #2: the `/update-user` authorization fix |
| `changed` | Merged in the same kind, but altered: a budget cut, a job folded into an existing one, a cheaper form of the same check | garten #3: PBT kept, randomized runs cut from about 306,096 to about 1,390 |
| `removed` | Deleted before merge | garten #3: `probes.yml` and its 12 defect-reintroduction patches |
| `pending` | The PR is still open | Units in the 37 open PRs |

### The label record

One record per unit, in `merge_labels.jsonl` (to be created):

```json
{
  "unit_id": "garten#3/defect-probe-lane",
  "repo": "garten",
  "merged_pr": 3,
  "campaign_head": "c97923b",
  "merged_head": "fc5c2b4",
  "paths": [".github/workflows/probes.yml", "scripts/defect-probes/*.patch"],
  "kind": "ci-lane",
  "technique": "mutation",
  "outcome": "removed",
  "owner_commit": "Keep Garten verification bounded and repair parser and RNG edge cases",
  "owner_reason": "quoted from the merged PR's Cost and limits section",
  "records": ["<record id(s) whose suggested change produced this unit>"],
  "ce": ["CE-013", "CE-052"]
}
```

`kind` is one of `fix`, `test`, `ci-lane`, `ci-step`, `budget`, `config`, `script`, `doc`. `technique` uses the same values as `records.jsonl`.

### How the labels are made

1. **Diff.** For each merged PR, take the PR's own diff twice: at the campaign head, against its base then, and at the merged head, against its base at merge time. Both SHAs are in `owner_merges_2026-10-09.json`. Comparing the two diffs, rather than the two heads, keeps changes that reached the default branch from other PRs (for example garten #2, merged into garten #3) out of the labels.
2. **Group hunks into units.** Use `git blame` on the campaign head, or the campaign commit messages, to find the commit that introduced each hunk. Group by purpose.
3. **Assign outcomes mechanically.**
   - A deleted path, or a fully reverted hunk, is `removed`.
   - An edited hunk is `changed`.
   - An untouched hunk is `kept`.
4. **Check `changed` by hand.** A rename is still `kept`. A budget cut or a fold into an existing job is `changed`. Attach the owner's stated reason, from the commit message or the PR body's **Cost and limits** section.
5. **Link units to records.** Match on repo, PR (through the fold map: for example, garten's records name #4, which was folded into #3), and the paths in each record's evidence. Each record's `ce` field then links the unit to the candidate edits.
6. **Roll up to records.** Fill `owner_outcome` in `records.jsonl`:
   - every linked unit `kept` gives `kept`;
   - every linked unit `removed` gives `removed`;
   - anything mixed gives `changed`;
   - no linked unit, or an open PR, gives `pending`.

About 90 records come from repos whose PRs have merged, so the first pass labels roughly a fifth of the dataset. Each later merge adds labels by the same procedure.

### What the labels are for

1. **An independent acceptance rate per candidate edit.** For each CE: of the units it motivated, how many were kept, changed or removed. This is the first measure of an edit's value that the session which proposed it did not assess. An edit whose units the owner mostly removed is flagged for the owner's decision rather than shipped on eval lift alone.
2. **Eval cases.** Each labelled unit, with its repo context, becomes a case:
   - a `removed` unit becomes a **cost-respect probe**: given the repo's existing CI and the original request, the agent should *not* propose it;
   - a `kept` unit becomes a **positive case**: the agent *should* find it;
   - a `changed` unit tests the form: for example, PBT inside the existing job at a fixed budget, not a new lane.
3. **Calibration of self-assessment.** Comparing each record's self-assessed severity and verdict with its owner outcome shows how far the self-assessment can be trusted when it is the only signal.

### Limits

- **One reviewer.** The owner's standard reflects the owner's projects: personal, cost-sensitive, mostly single-maintainer. The labels say what this owner accepts, not what every team should. Results from labels are reported apart from oracle results, and never merged into one score.
- **Small n.** 11 merged PRs, about 90 records. Per-CE rates have wide uncertainty until more PRs merge.
- **A unit is a judgment call.** Grouping hunks into units is done by hand and is reviewable: each label names its paths.

## 4. Treatments, arms and models

- **Base:** the skill at `main` @ `0e4617d`.
- **Treatment:** one candidate edit, written as the smallest diff to the files the index names in its Target column, kept as `ce/CE-0NN.patch`. Each patch records its token delta, measured with `scripts/token-report.py`.
- **No-skill control:** the same prompt with no skill installed. It measures what the model already does unaided, and so detects saturation.
- **Variants for contested edits.** Where the wording of an edit is itself the question, each wording is a separate treatment. The first case is CE-060:
  - `CE-060-strict`: mutation testing never runs as a recurring CI gate (the wording in #32);
  - `CE-060-default-off`: mutation testing is on demand by default; a recurring lane runs only when the shipped CE-012 operating contract is met in full (measured baseline, owner, change-scoped, no score floor).
- **Models:** at least two, one strong and one smaller. `HARNESS_COMPARISON.md` showed effects that differ sharply by model (E64 lifted on one model out of seven). Model identifiers and the harness version (skill-eval-harness 0.6.0) are recorded in each run receipt.

## 5. Eval cases

### Sources

| Source | Size | Becomes |
|---|---|---|
| Existing suite (`evals/evals.json`) | 78 evals, 34 critical | A regression guard |
| `eval_seed` with a `check` | 369 records (274 campaign, 95 pre-campaign) | Positive cases |
| `counterexample` | 214 records (119 campaign, 95 pre-campaign) | Restraint probes |
| Merge labels (section 3) | One case per labelled unit | Cost-respect probes and positive cases |
| Later merges | Grows | The holdout set (section 8) |

Not every seed becomes a fixture. Each candidate edit gets at least **two positive cases and one restraint probe**, chosen in this order: seeds linked to that CE, then severity `high`, then seeds whose `check` can be decided without a model judge. Seeds for the same CE from different repos are preferred over several from one repo. The expected total is about 150 new cases.

### Oracle tiers

Each case uses the cheapest tier that can decide it.

| Tier | Oracle | Cost per run | Existing precedent |
|---|---|---|---|
| 0 | Pattern and contradiction checks on the answer (`oracle.py`) | Milliseconds | E64, E77 |
| 1 | Runtime check: the agent's test must pass on the good implementation and fail on a planted bug | Seconds | `mini-repos/`, `scripts/run-mini-repos.py` |
| 2 | A blinded model judge with the rubric | A model call | `scripts/run-blind-comparison.py` |

Tier 2 is capped at 10% of cases. A case that needs a judge must say why tiers 0 and 1 cannot decide it.

### The cost-respect oracle

This is one Tier 0 oracle, shared by all cases. It scans the answer, or the diff the agent produced, for:
- a new workflow file, job, matrix entry or `schedule:`;
- a mutation tool (Stryker, mutmut, gremlins or similar) invoked from CI;
- a PBT budget (`numRuns`, `max_examples`) above the project's existing default;
- fuzzing with no time or iteration bound, or a scheduled fuzz campaign;
- raised timeouts or retries.

It reuses the patterns of the pruning scan (`prune/scan.py` in the campaign scratch area). It reports **separate counts for mutation, PBT and fuzzing**, so the three are never lumped together.

### Every new fixture follows the existing layout

`fixtures/<id>/{manifest.json, prompt.md, oracle.py, samples/good, samples/bad, samples/bad-contradictory}`. The oracle must:
- pass the good sample;
- fail the bad sample;
- fail the contradictory sample, which states the right answer and then does the wrong thing.

That last check is what stops keyword gaming. `scripts/run-fixture-oracles.py` checks all three before any model run (stage 0).

### Cases that conflict with the corrected standard

Some existing evals encode guidance that the owner's standard now contradicts. They are measured, not silently rewritten:

| Eval | What it expects | Conflict |
|---|---|---|
| E68 (hidden) | Approve a focused, change-scoped recurring mutation lane that meets the CE-012 contract. Red flag: "Says mutation testing should never be scheduled" | `CE-060-strict` fails it by design; `CE-060-default-off` should pass it |
| E76 | Run the Playwright visual test in CI, with baselines rendered on the CI image | The owner removed visual-baseline workflows from embed.oshineye.dev #2 and flux-search #26 |
| E73 (hidden) | Accept a nightly lane that makes gated live tests reachable | The owner has added no schedules, and removed nightly live workflows |
| E74 / CE-009 | No silent downgrade of a test tier | Compatible if the downgrade is documented ("live and browser commands remain manual"); the oracle must accept a documented move to manual |

Whether these evals change is a policy question for the owner (section 11). It is not something the ablation can settle. The ablation reports both sides of the trade.

## 6. Metrics

For each case, arm and model, with *n* samples:

- **Pass count** out of *n*, decided by the oracle. This is the primary metric. Results are reported as `W/B` tables (treatment passes / base passes) per model, in the format of `HARNESS_COMPARISON.md`.
- **Lift** for a CE on one model: the sum over its positive cases of (W − B).
- **Over-application:** the sum over its restraint probes of (B − W). It should be ≤ 0.
- **Guard regression:** any critical existing eval where W ≤ B − 2.
- **Cost-respect violations** per answer, by class: mutation, PBT, fuzz, CI lane, schedule, timeout or retry.
- **Tokens:** the skill's token delta, and the generation tokens per run.
- **Rubric score** (minimum across dimensions, per `scorecard.md`): only for Tier 2 cases.

## 7. Stages

### Stage 0: validate the oracles (no model calls)

- Every new fixture passes the three-sample check.
- Then run the base arm and the no-skill arm, three samples each, on one model.
- A case that both arms pass 3/3 is **saturated**. It cannot show lift, so it is hardened (a hidden variant, per `eval-health.md`) or dropped.
- The base runs are kept and reused as stage 1's base arm.

### Stage 1: screen one edit at a time

- **Arms:** base, and base + CE.
- **Cases:** the CE's own positive cases and restraint probes, plus the critical evals that exercise the same reference files (about six per CE). Running the whole suite for every CE would not add information about that CE.
- **Samples:** start at *n* = 3. Extend to *n* = 6 only for cells where the result is ambiguous, meaning a difference of 1 or 2 between arms. Never extend cells at 0/0 or 3/3.
- **Grouping:**
  - Bundled rows ("smaller fixes": CE-029, CE-058) are screened as one treatment.
  - Rows that only retract wrong guidance are screened for regression only. They are decided on evidence that the old text was wrong, not on lift.

### Stage 2: test interactions within families

Edits interact when they touch the same passage or give opposing advice. These families are tested together (membership to be confirmed when the patches are written):

| Family | Edits | Why they interact |
|---|---|---|
| Cost | CE-059, CE-060 (strict or default-off), CE-061, CE-062, with the shipped CE-013 as a fifth factor (present or removed) | CE-060 tightens CE-013; CE-059 partly counters CE-055 and the shipped CE-009 |
| Oracles | CE-020, CE-021, CE-022, CE-025, CE-026, CE-027, CE-042, CE-057 | CE-057 is an exception to the self-oracle rule (CE-007, CE-020); CE-021 and CE-025 both rewrite the golden-file defaults |
| Replacing tests | CE-024, CE-031, CE-032, CE-033, CE-034, CE-052, CE-053 | They all govern what must be kept when tests are deleted |
| Real engines | CE-028, CE-030, CE-044, CE-046, CE-048 | They extend the mock ladder in different directions |

Within a family of up to five on-or-off factors, run a 2^(5−1) fractional factorial: 16 configurations, which estimates every main effect and every two-way interaction. Larger families are split. The cost family runs first: it is the owner's main concern, and it carries the E68 conflict.

### Stage 3: leave one out

- Assemble base plus every edit that passed screening, resolving family interactions the way stage 2 found best.
- For each included edit, run the assembled skill without it, on that edit's own cases and guard cases.
- An edit whose removal does not lower lift, and does not raise over-application or cost-respect violations, is dropped. It costs tokens and earns nothing in this combination.

### Stage 4: confirm on the holdout

Run the final assembled skill against base, once, on the holdout set (section 8). The holdout is not used before this point.

## 8. Holdout

The holdout is made of cases nobody has seen while choosing edits:
- merge labels from PRs merged **after** this design is frozen (the 37 open PRs, as the owner merges them);
- hidden variants of selected cases, written by a different session from the one that wrote the public case. They are kept outside this repository, because the records and #32 are public.

## 9. Run budget

```
runs = Σ over stages of (cases × arms × samples × models)
cost ≈ runs × generation tokens per run
     + Tier 1 runs × seconds per runtime oracle
     + Tier 2 runs × judge tokens
```

A worked estimate for one model, assuming about 150 new cases, about six guard evals per CE, and *n* = 3:

| Stage | Runs |
|---|---|
| 0: base and no-skill on the new cases | 150 × 2 × 3 = 900 |
| 1: treatment arm (base reused from stage 0) | 43 × (3.5 + 6) × 3 ≈ 1,230, plus 34 × 3 = 102 base runs on the guard evals |
| 2: cost family | 16 configurations × about 25 cases × 3 ≈ 1,200 |
| 3: leave one out, assuming 15 survivors | 15 × about 10 cases × 3 ≈ 450, plus one assembled run on all their cases ≈ 180 |
| 4: holdout | 2 arms × about 40 cases × 3 = 240 |

That totals about 4,300 runs per model, and about 8,600 for two models. The total is linear in the number of edits, not exponential.

The owner sets the cap. Stages run in this order, so the cheapest and most informative runs come first, and the analysis stops at the cap with whatever has been learned. The cost family can run on its own first, for about 1,500 runs per model.

## 10. Confounds and controls

| Confound | Control |
|---|---|
| **Prompt versus skill.** The campaign prompt told sessions what to look for, so records `prompted_by: prompt` show the prompt's effect, not the skill's | Eval prompts are built from `eval_seed.setup`, never from the campaign prompt. Cue-free variants, as in E42 and E43 |
| **Self-assessed verdicts** | Used only for choosing cases (principle 3) |
| **One reviewer** behind the merge labels | Label results are reported apart from oracle results (section 3, Limits) |
| **Keyword gaming** | A contradictory sample for every fixture (section 5) |
| **Leakage.** Fixtures and records are public | Isolated workspaces with no eval artifacts, as in `HARNESS_COMPARISON.md`; the holdout is kept outside this repository |
| **Prompt-version drift.** Records came from campaign prompt v3 and later versions | Each record's `source` names its version; results are stratified by it |
| **Model drift** | Model identifiers and harness version are pinned per run |
| **Position bias in judges** | A/B order randomized and blinded, which `run-blind-comparison.py` already does |
| **Planted bug confused with mutation testing** | Mutation cost is measured with `cost_concern` and the cost-respect oracle, never with `verified_by_planted_bug` |
| **Lumping techniques** | Every cost metric is reported separately for mutation, PBT and fuzzing |

## 11. Decision rule

A candidate edit is **recommended for shipping** when all of these hold:

1. **Screening.** On at least one model, lift ≥ 2 and over-application ≤ 0. On no model, a guard regression. A retraction instead needs: no regression, plus documented evidence that the old text was wrong.
2. **Leave one out.** Removing it from the assembled skill lowers lift, or raises over-application or cost-respect violations.
3. **Holdout.** The assembled skill is at least as good as base, with no critical regression.
4. **Merge labels, where available.** The owner did not remove most of the units this edit motivated. If the owner did, the edit goes to the owner as a decision, with its eval results attached.
5. **Tokens.** If its lift appears on only one model, and it adds more than about 500 tokens, it is compressed and screened again before it is recommended.

**Questions only the owner can answer:**
- Is the cost standard the skill's general advice, or advice for a stated context, for example small projects with one maintainer? The answer decides `CE-060-strict` versus `CE-060-default-off`, and whether E68, E73 and E76 change.
- Is a scheduled deeper tier for PBT or fuzzing ever acceptable? `property-based-testing.md` and `fuzzing.md` currently recommend one; the owner has added none and removed none.
- Which models to run, and the run cap.

## 12. Order of work

1. Write `merge_labels.jsonl` for the 11 merged PRs, and fill `owner_outcome` (section 3).
2. Write the CE patches for the cost family, and their fixtures from seeds, counterexamples and merge labels.
3. Stage 0 for those fixtures.
4. Stages 1 and 2 for the cost family. Report the results to the owner, with the CE-060 wording question.
5. Fixtures and stage 1 for the remaining families.
6. Stages 3 and 4 once enough PRs have merged to fill the holdout.
