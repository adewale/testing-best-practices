# Eval Scorecard

Use this file to record baseline and post-change scores. Do not treat provisional/mental scores as release evidence; release evidence needs runnable fixture output or a saved transcript.

## Scoring rule
- Score each eval 0–4 using `evals/rubric.md`.
- The eval score is the **minimum** score across its `rubric_focus` dimensions, not the average.
- Any critical-failure override in `evals/rubric.md` makes the eval score `0`.

## Baseline static audit
Run:
```bash
python3 scripts/static-audit.py || true
python3 scripts/score-evals.py --evals evals/evals.json
python3 scripts/run-fixture-oracles.py
```

| Date | Skill revision | Static P0 | Static P1 | Critical evals >=3 | Overall avg | Notes |
|---|---|---:|---:|---:|---:|---|
| 2026-05-20 | baseline-before-G1/G2-edits | 6 | 6 | TBD | TBD | Static baseline captured before content fixes; prompt scores still TBD/provisional. |
| 2026-05-20 | after-G1/G2-static-fixes | 0 | 0 | TBD | TBD | `SKILL.md` router refactor + reference contradiction fixes; prompt/runtime scores still need transcripts. |
| 2026-05-20 | after-fixture-oracle-run | 0 | 0 | 9/14* | partial | 10 fixture-backed prompt runs passed executable oracles; raw generated `eval-runs/` are ignored, and `*` means oracle-backed, not full human-scored release gate. |

## Prompt eval results

| Eval | Critical | Baseline score | Final score | Evidence path / transcript | Notes |
|---|---:|---:|---:|---|---|
| E01-bugfix-red-green-project-context | yes | TBD | 3* | `evals/fixtures/e01-typescript-vitest-sanitizer` | Candidate passed oracle. |
| E02-assess-sabotaged-tests | yes | TBD | TBD | TBD |  |
| E03-assertion-density-calibration | yes | TBD | TBD | TBD |  |
| E04-correctness-by-construction-safety | yes | TBD | TBD | TBD |  |
| E05-property-based-typescript-never-throws | yes | TBD | TBD | TBD |  |
| E06-integration-tier-classification | no | TBD | TBD | TBD |  |
| E07-vcr-vs-handwritten-http-mocks | no | TBD | TBD | TBD |  |
| E08-flaky-time-tests | yes | TBD | 3* | `evals/fixtures/e08-deterministic-time` | Candidate passed oracle. |
| E09-legacy-characterization | no | TBD | TBD | TBD |  |
| E10-high-coverage-low-quality | no | TBD | TBD | TBD |  |
| E11-e2e-scope-control | no | TBD | TBD | TBD |  |
| E12-final-report-validation-honesty | yes | TBD | 3* | `evals/fixtures/e12-validation-honesty` | Candidate passed oracle. |
| E13-unsupported-language-fallback | no | TBD | TBD | TBD |  |
| E14-scope-creep-type-refactor | yes | TBD | TBD | TBD |  |
| E15-doc-sync-cli-registry | no | TBD | TBD | TBD |  |
| E16-golden-review-discipline | no | TBD | TBD | TBD |  |
| E17-rust-differential-port | no | TBD | TBD | TBD |  |
| E18-test-data-builder-intent | no | TBD | TBD | TBD |  |
| E19-detect-order-pollution | yes | TBD | 3* | `evals/fixtures/e19-order-pollution` | Candidate passed oracle. |
| E20-go-zero-value-invariant | yes | TBD | 3* | `evals/fixtures/e20-go-zero-value` | Candidate passed oracle. |
| E21-implementation-detail-mock-call-count | no | TBD | TBD | TBD |  |
| E22-contract-schema-drift | no | TBD | TBD | TBD |  |
| E23-python-hypothesis-parser-contract | yes | TBD | 3* | `evals/fixtures/e23-python-hypothesis-parser` | Candidate passed the structural oracle; the fixture does not execute the candidate tests. |
| E24-python-recorded-api-fixture | no | TBD | 3* | `evals/fixtures/e24-python-recorded-api-fixture` | Candidate passed oracle. |
| E25-go-tempdir-and-fake-dependency | yes | TBD | 3* | `evals/fixtures/e25-go-tempdir-fake` | Candidate passed oracle. |
| E26-rust-result-proptest-and-no-unwrap | yes | TBD | 3* | `evals/fixtures/e26-rust-result-proptest` | Candidate passed oracle. |
| E27-typescript-playwright-flake-locators | yes | TBD | 3* | `evals/fixtures/e27-typescript-playwright-flake` | Candidate passed oracle. |

`3*` = the fixture oracle command passed for one generated candidate. It is evidence for the focused failure mode, not proof that candidate tests executed and not a complete 0–4 human/rubric release score.

## 2026-08-28 Google-Testing-Blog ablation round

44 candidate runs: sonnet + opus sub-agents, one per cell; arms are
**base** (no skill), **current** (v0.3.1 skill files), **new** (skill +
`DRAFT_ADDITIONS` bundle of the C1–C9 Google-research text, since landed).
Restraint probes (E58, E63) ran current/new arms only. Every cell was scored
by its eval's deterministic fixture oracle; oracle discrimination was the
round's metric (the blind judge pass below re-scored these same cells on
the rubric the next day).

| Eval | base-S | base-O | curr-S | curr-O | new-S | new-O |
|---|---|---|---|---|---|---|
| E55 literal expectations | pass | pass | pass | pass | pass | pass |
| E57 DAMP shared fixture | pass | pass | pass | pass | pass | pass |
| E58 narrow-vs-roundtrip (restraint) | — | — | pass | pass | pass | pass |
| E59 narrow assertions upgrade | pass | pass | pass | pass | pass | pass |
| E60 fake-contract weld | pass | pass | pass | pass | pass | pass |
| E61 suite shape | pass | pass* | pass | pass | pass | pass |
| E62 numeric defaults (hidden) | pass | pass | pass | pass | pass | pass |
| E63 DAMP keeps builders (restraint) | — | — | pass | pass | pass | pass |

`*` after oracle hardening — the three raw "fails" in the run (e55/curr-O,
e57/curr-S, e61/base-O) were all **oracle artifacts**, confirmed by reading
the candidates, and fixed: E55 now captures literals in plain `parametrize`
tuples (while excluding rejects-malformed parametrize blocks from the
enshrined-bug check); E57 counts parametrize/subTest as the split
recommendation; E61 accepts "critical-path journeys" phrasing and ignores
doubling-down phrases followed by negation ("…is the wrong one"). All good/
bad sample self-tests still pass after each fix.

**Conclusions**
1. **No regressions from the landed text**: all 16 new-arm cells pass,
   including both restraint probes on both models — the C1/C2 boundary
   language (whole-state roundtrips, sanctioned-DRY builders) holds.
2. **Baseline ceiling**: 2026 frontier models pass these fixtures without
   the skill at n=1/cell, so E55–E63 are **regression guards** (weaker
   models, future skill drift), not version discriminators —
   `known_discriminates_versions` stays empty and public cases are marked
   `saturated_public`.
3. The round's measurable yield: 44 real-model transcripts hardened 3 of 8
   oracles — the "validate oracles against real model output" practice from
   LESSONS_LEARNED, at scale.

Run artifacts: session scratchpad `matrix/` (gitignored; not release
evidence beyond this record).

**Provenance limitation recorded 2026-09-19:** the historical notes retain
only the `sonnet` / `opus` aliases. Exact model versions and raw generation
artifacts were not committed, so this round cannot establish coverage of
today's usual model panel. Treat it as historical methodology evidence, not a
reproducible current-model result.

## 2026-08-29 Variance measurement (repeated runs)

n=5 per cell (r1 = the original matrix run, r2–r5 fresh repeats) on the ten
cells most likely to vary: the three base-arm cells whose oracles are
prose-sensitive (E57, E60, E61 assess/weld tasks) and both restraint probes
on the new arm (E58, E63 — the safety-critical cells), each on sonnet and
opus.

| Eval | Cell | sonnet | opus |
|---|---|---|---|
| E57 DAMP shared fixture | base | 5/5 | 5/5 |
| E60 fake-contract weld | base | 5/5 | 5/5 |
| E61 suite shape | base | 5/5 | 5/5 |
| E58 narrow-vs-roundtrip (restraint) | new | 5/5 | 5/5 |
| E63 DAMP keeps builders (restraint) | new | 5/5 | 5/5 |

Aggregate 50/50; Wilson 95% CI for the per-run pass rate [0.93, 1.00].
Observed model variance on these fixtures is zero — but only after oracle
work: every raw FAIL in the round was on E61's prose oracle, and reading
each transcript showed all of them to be phrasing artifacts ("re-express
those specs as table-driven unit tests", "one thin e2e proving the wiring",
"push the rules down" plus a `| unit |` migration table, a "no retries"
table…), fixed across three hardening passes with the good/bad sample
self-tests kept green (40/40). At the frontier ceiling, oracle phrasing
coverage — not model stochasticity — is the dominant variance source.

Caveats recorded:
- **Repeat-arm provenance**: new-arm r1 used the `DRAFT_ADDITIONS` bundle;
  r2–r5 ran against the since-landed skill text. Same content, different
  packaging — treated as equivalent for restraint measurement.
- **Workspace contamination**: one repeat agent (e60/base-sonnet-r2)
  reported leftover files from sibling runs in the shared scratchpad.
  Contamination can only inflate pass rates, and the affected cells were
  already 5/5 from clean runs, so the conclusion stands — but repeat runs
  should get isolated workspaces next time.

## 2026-08-29 Blind judge pass

All 44 matrix cells re-scored by LLM judges on the rubric, blinded: each
cell got an opaque hash code (arm/model/eval hidden), a copy of its task
prompt, its eval's `rubric_focus`/expected-behavior/red-flags, and the
candidate files — nothing else. Six sonnet judges covered all 44 cells;
two opus judges independently double-judged the 16 new-arm cells for
agreement measurement. Scoring: min over `rubric_focus` dimensions (0–4
per `rubric.md`), critical-failure override to 0. Several judges executed
candidate test suites/mutants rather than trusting the transcripts.

Results (sonnet judge; like-for-like column restricts to the six evals
present in all arms, since E58/E63 have no base arm):

| Arm | All cells | Like-for-like (6 evals, n=12) | Cells scoring 3 |
|---|---|---|---|
| base | 3.67 ± 0.49 (n=12) | 3.67 ± 0.49 | 4 |
| current | 3.81 ± 0.40 (n=16) | 3.83 ± 0.39 | 2 |
| new | 3.94 ± 0.25 (n=16) | 3.92 ± 0.29 | 1 |

Zero critical failures; minimum cell score 3 ("good, minor gaps") — every
score-3 rationale was read and is a legitimate minor-gap call, not a judge
artifact. Restraint probes: E58 4.0 across all four cells; E63 one 3
(current-opus, D dimension), 4s elsewhere.

**Judge agreement** (sonnet vs opus on the 16 double-judged cells) — the
"judge disagreement rate" meta-signal from `eval-health.md`, now measured:
per-dimension exact agreement 31/32 (97%), mean |Δ| 0.03 (max 1), mean
eval-score |Δ| 0.06 with no disagreement >1, critical-failure agreement
16/16. At this agreement level a single-judge pass is trustworthy for
these fixtures.

**Reading.** The judges recover a soft quality gradient (base < current <
new, and fewer 3s with the skill) that the binary oracles compress to
all-pass — consistent across both column definitions but within
overlapping standard deviations at n=12, so it is *suggestive* of marginal
skill value at the frontier ceiling, not proof. The two layers divide
labor: deterministic oracles guard hard behaviors (regression gate), the
judge layer grades the quality margin above the oracle floor.

## 2026-09-19 PR 25 current-model verification

The six Google-derived shared cases were run as paired `with_skill` /
`without_skill` cells on exact `gpt-5.6-luna` and `gpt-5.6-terra` model IDs,
with `model_reasoning_effort=low` explicitly present in the saved runner
command. The fixture-backed script oracle graded every cell; no LLM judge was
used. Full provenance and token totals are in
`receipts/pr25-luna-terra-2026-09-19.md`.

| Model | Without skill | With skill | Observed delta |
|---|---:|---:|---:|
| `gpt-5.6-luna` | 5/6 | 6/6 | +1 |
| `gpt-5.6-terra` | 6/6 | 6/6 | 0 |
| **Total** | **11/12** | **12/12** | **+1** |

The sole difference was E60: Luna's baseline emitted invalid Python (`def
test_delete_missing_key_is harmless`), while its with-skill output passed the
pristine implementation and killed both fake-drift and real-drift variants.
That is not enough to claim general quality lift. The defensible conclusion is
no observed skill regression on this focused panel, one noisy positive cell,
and continued frontier saturation. Skill-file reads were observed in 11/12
with-skill cells; Terra E59 passed without reading the mounted skill, so it is
not evidence of treatment uptake.

## Issue #20/#21 initial Pi ablation (2026-07-22)

_Current IDs E64–E69; the original run used E55–E60 before rebasing over PRs #24/#25. These results evaluate the issue guidance before those upstream skill changes, not the final combined tree._
Model: `gpt-5.6-sol`, final `n=1` per arm. The with-arm preloaded the local working-tree `SKILL.md` plus the relevant new reference; the without-arm used model priors without project skills. Results are semantic fixture-oracle outcomes, not full rubric scores. Generated candidates remain ignored/runtime artifacts rather than tracked source.

| Eval | With local guidance | Without guidance | Interpretation |
|---|---:|---:|---|
| E64 mutation recurring-lane contract | PASS | FAIL | Discriminates after review hardening: with-guidance rejected bootstrap `break: 60`, chose a focused pilot, required demonstrated fault-class bite/baseline/owner/capacity, and distinguished operational/untriaged failures from acted-on findings. |
| E65 cue-free mutation survivor triage | PASS | FAIL | Public tune probe discriminates in this initial Pi run: with-guidance rejected the round target, separated actual survivors from incomplete/tool statuses, independently raised equivalence, and proposed like-for-like triage. |
| E66 combinatorial cost-aware portfolio | PASS | FAIL | Discriminates: with-guidance kept exact enrollment and the four-way regression, exhausted cheap slices, used constrained pairwise plus a named 3-way group, compared multiple cost classes, and required shadow + mutation/sabotage evidence before deletion. |
| E67 registry sabotage | PASS | PASS | Public API/task cues the executable behavior; retain as a regression oracle, not marginal-value evidence. Hardened inspection now requires the candidate's own isolated fake injection, exact ID assertion, and failing contract assertion. |
| E68 valid recurring lane keep-probe | PASS | PASS | Restraint held with all conservative prerequisites present, including demonstrated fault-class bite and expiry/removal policy. |
| E69 known high-order regression keep-probe | PASS | PASS | Restraint held: both arms explicitly retained repaired-fault evidence alongside pairwise rows. |

Independent review invalidated the first E64 attestation and exposed polarity/keyword false positives in E64/E65/E66/E67/E68/E69. Before the final run, the oracles were hardened with explicit positive/negative decisions, separate conjunctive obligations, dynamic fake injection, and near-miss bad samples. Fixture-validity fixes also added demonstrated fault-class bite and expiry to E68, and separated survivor statuses in E65. The table records only the post-fix rerun/rescore.

## Skill Eval Harness multi-model follow-up (2026-07-22)

Skill Eval Harness v0.4.0 generated the historical E64–E69 seven-model run. The public-tune E64–E66 set ran three times per model and arm: 126 candidates, with isolated workspaces and deterministic script oracles. Aggregate objective results were **24/63 with skill versus 9/63 without**. By eval: E64 3/21 vs 0/21, E65 14/21 vs 9/21, and E66 7/21 vs 0/21. The effect is model-dependent: `gpt-5.6-sol` scored 9/9 with versus 1/9 without, while several smaller/older models still omitted required obligations after reading the guidance. The installed harness and manifest are now v0.6.0/schema v2; migrating a copy of all 126 runs to telemetry schema v3 preserved the objective matrix exactly.

For requested model `gpt-5.6-sol`, a two-judge-run consensus scored E64 and E66 3/3 with versus 0/3 without; E65 passed 3/3 in both arms. E64 without had one split candidate (raw decisions 1 pass / 5 fail), so consensus outcomes are not unanimous judgments. A separately blinded comparison preferred with-skill outputs in 8/9 pairs. The pinned pre-issues skill scored 0/3 on E64, 2/3 on E65, and 0/3 on E66, versus 3/3 each for the current skill. Trigger evaluation ranged from 4/8 on `gpt-5.4-mini` to 8/8 on `gpt-5.5`; most models scored 7/8.

Full model matrix, harness commands, integration defects, and retained local-only features: `HARNESS_COMPARISON.md`. Bounded provenance and decoded trigger/blind/judge evidence are tracked in `attestations/issues-20-21-multimodel.json`; bulky candidates and judge transcripts remain ignored runtime artifacts.

## Release gates
- [ ] Static P0 count is 0.
- [ ] Static P1 count is 0 or explicitly deferred.
- [ ] All critical evals score >=3.
- [ ] Overall average >=3.3/4.
- [ ] No broken local links.
- [ ] `SKILL.md` <=500 lines hard max, target <=350 after router refactor.

## Version comparison against GitHub versions

Compared on 2026-05-21. Full notes: `../VERSION_COMPARISON.md` from this file's directory (`skill-development/VERSION_COMPARISON.md`).

| Version | Artifact rubric | Static P0 | Static P1 | Fixture oracle pass | Critical fixture oracle pass | Status |
|---|---:|---:|---:|---:|---:|---|
| First working GitHub (`6951b7d`) | 28/100 | 6 | 4 | 10/10 | 9/9 | Early draft; prompt oracles saturated despite major artifact gaps |
| GitHub `origin/main` (`6e8cd8b`) | 69/100 | 6 | 6 | 10/10 | 9/9 | Broad but fails static P0/P1 gate |
| Current working skill | 100/100 | 0 | 0 | 10/10 | 9/9 | Passes local non-LLM gates |

Interpretation: the artifact rubric distinguishes all three versions. The fixture-backed prompt oracles are saturated across first/current/local, so they are useful sanity checks but not sufficient alone. Add harder hidden variants targeted at assertion calibration, PBT weak examples, integration classification, and correctness-by-construction deletion safety.
