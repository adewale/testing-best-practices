# Skill Eval Harness comparison and multi-model run

Date: 2026-07-22

## Scope and execution

The issues #20/#21 evals E64–E69 are registered in
`evals/shared-benchmark.json`. The 126-candidate evidence below was generated
and first graded with Skill Eval Harness v0.4.0 before this branch rebased over
PRs #24/#25; it is historical evidence about the issue guidance, not an
end-to-end evaluation of the final combined skill tree or current harness
release. The repository and installed tool were subsequently upgraded to v0.6.0
and compatibility-tested below.

The historical run requested all OpenAI model identifiers exposed by the local Pi catalog:

- `gpt-5.3-codex-spark`
- `gpt-5.4`
- `gpt-5.4-mini`
- `gpt-5.5`
- `gpt-5.6-luna`
- `gpt-5.6-sol`
- `gpt-5.6-terra`

Generation used Codex CLI 0.145.0, medium reasoning, a read-only sandbox, and
isolated workspaces. Model names below are requested identifiers, not provider-attested identities. The with-skill workspace contained only the installable
skill; the without-skill workspace contained no skill or evaluation artifacts.
This prevented candidates from finding fixture oracles in the repository.
Generated runs remain ignored under `skill-development/eval-runs/`.

## Repeated objective results: E64–E66

Three independent runs per model and arm produced 126 candidates. `W/N` means
with-skill passes / without-skill passes out of three.

| Model | E64 W/N | E65 W/N | E66 W/N | All W/N |
|---|---:|---:|---:|---:|
| gpt-5.3-codex-spark | 0/0 | 1/1 | 0/0 | 1/1 of 9 |
| gpt-5.4 | 0/0 | 2/1 | 0/0 | 2/1 of 9 |
| gpt-5.4-mini | 0/0 | 2/2 | 0/0 | 2/2 of 9 |
| gpt-5.5 | 0/0 | 3/1 | 0/0 | 3/1 of 9 |
| gpt-5.6-luna | 0/0 | 1/2 | 3/0 | 4/2 of 9 |
| gpt-5.6-sol | 3/0 | 3/1 | 3/0 | **9/1 of 9** |
| gpt-5.6-terra | 0/0 | 2/1 | 1/0 | 3/1 of 9 |
| **Aggregate** | **3/0 of 21** | **14/9 of 21** | **7/0 of 21** | **24/9 of 63** |

Interpretation:

- E64's operational contract is a strong discriminator on `gpt-5.6-sol`, but
  the other models still tend to obey the user's copied floor or omit a
  prerequisite even after reading the reference. The effect is model-dependent.
- E65 improves aggregate performance but is partly saturated in model priors;
  both arms sometimes reject the incomparable score target and triage statuses.
- E66 has clear lift on `gpt-5.6-sol` and `gpt-5.6-luna`, weak lift on Terra,
  and no exact-oracle pass on the smaller/older models. Common omissions are
  named variable-strength obligations or explicit shadow/sabotage evidence.
- Aggregate objective pass rate was 38.1% with the skill versus 14.3% without.
  This is a model-by-item result, not a universal effect estimate.

For requested model `gpt-5.6-sol`, a repeated qualitative judge (`gpt-5.4`, two judgments per
candidate) produced candidate-level consensus of E64 and E66 3/3 with versus 0/3 without; E65 was 3/3 in both
arms. E64 without had one split candidate, so the raw E64-without decisions were 1 pass / 5 fail rather than unanimous 0/6. A separately blinded A/B comparison preferred the with-skill answer in
8/9 pairs. Against the pinned pre-issues skill, `gpt-5.6-sol` scored E64 0/3,
E65 2/3, and E66 0/3, versus 3/3 on each with the current skill.

E67–E69 were also run once per model and arm. Those single samples were much
less stable than the original Pi ablation: E67's exact multi-file coding
contract was sensitive to candidate representation, E68 usually approved the
valid lane only with guidance, and E69 varied by model. Keep them as
regression/restraint probes; do not infer effect sizes from `n=1`.

## Historical v0.4 trigger results

`skill-pi-trigger-eval` ran the manifest's four trigger and four no-trigger
cases once on every model:

| Model | Total | Trigger positives | No-trigger negatives |
|---|---:|---:|---:|
| gpt-5.3-codex-spark | 7/8 | 3/4 | 4/4 |
| gpt-5.4 | 7/8 | 4/4 | 3/4 |
| gpt-5.4-mini | 4/8 | 0/4 | 4/4 |
| gpt-5.5 | **8/8** | 4/4 | 4/4 |
| gpt-5.6-luna | 7/8 | 4/4 | 3/4 |
| gpt-5.6-sol | 7/8 | 4/4 | 3/4 |
| gpt-5.6-terra | 7/8 | 4/4 | 3/4 |

The mini model consistently under-triggered; most other failures were one
false-positive trigger on a near-miss query.

## Harness capabilities used in the historical run

- manifest validation and audit;
- paired `with_skill` / `without_skill` variants;
- pinned `old_skill` variant;
- repeated runs and mean/variance-capable benchmark reports;
- deterministic `script` assertions;
- Codex execution and normalized traces/metrics;
- repeated qualitative judges with saved transcripts;
- autonomous Pi trigger/no-trigger evaluation;
- blinded comparison tasks and result decoding;
- skill profiling, grading files, Anthropic export, and HTML viewer generation.

## Reconsideration after upgrading to v0.6.0

### Upgrade validation

- Installed release: `skill-eval-harness==0.6.0`; the manifest is now schema v2
  with explicit behavior-preserving severity and oracle tiers.
- `validate` and `audit-manifest` pass; the audit reports ten materialized
  ablations and no blockers. It correctly flags E64–E69 as weak-oracle-only:
  their calibrated scripts are deterministic but remain `demo` tier under
  v0.6's rule that `strong` script oracles verify rendered artifacts.
- A telemetry migration dry-run found all 126 historical candidates eligible
  for schema-v3 migration. Migrating a copy and re-benchmarking with v0.6.0
  preserved the objective matrix exactly: **24/63 with skill versus 9/63
  without**.
- A pre-rebase native v0.6 Codex E64 smoke wrote complete 3,691/4,131-character
  answers, schema-v3 telemetry, configured model metadata, and correct
  `skill_invoked=true/false` observations. Both candidates failed the strict
  E64 oracle, so this smoke proves runner compatibility and isolation—not a new
  lift estimate or final-tree evaluation.
- Native materialization works, but unfiltered `--include-ablations` still emits
  every answer ablation for every answer case. The local focused-preparation
  wrapper now filters those rows using structured expected-regression case IDs.
- The v0.6 offline trigger-matrix smoke produced 24 repeated observations,
  complete trace artifacts, explicit capability/telemetry availability, and a
  21/24 result. This validates the richer trigger reporting surface without
  spending model tokens; it is not new model-quality evidence.

### Status of the v0.4 findings

| Original finding | v0.6.0 status | Correct owner |
|---|---|---|
| No general case filter | **Still open.** Focused prepare/judge/report workflows need a shared case/tag selector. | Harness core |
| Codex final answer was truncated | **Fixed.** Native Codex uses `--output-last-message`; the temporary v0.4 repair adapter was removed after compatibility validation. | Harness core |
| Repo-root execution exposed evaluator artifacts | **Fixed in native runners.** v0.6 creates per-variant workspaces and excludes the skill from the baseline. | Harness core |
| Model/token metadata was incomplete | **Mostly fixed.** Schema-v3 usage and configured model labels are present; requested versus provider-attested identity is still not distinguished. | Harness core provenance |
| Codex skill reads did not set `skill_invoked` | **Fixed in the native smoke.** | Harness backend normalization |
| Ablations were instruction-simulated | **Fixed.** v0.6 materializes blind altered trees with hashes and provenance. | Harness core |
| `answer_ref` was inert | **Still open.** Resolve it privately for judges or reject the unsupported field. | Harness core |
| Structured `expected_regressions` crashed prepare | **Fixed.** The manifest now uses v0.6 structured summaries/cases/assertions. | Harness core |
| No oracle self-test lifecycle | **Still open as an optional protocol.** | Harness extension + local fixtures |
| No mutation mini-repo runner | **Still open as an optional counterexample protocol.** | Harness extension + local mutants |
| Trigger diagnostics were shallow | **Substantially fixed.** v0.6 adds repetitions, normalized traces/usage, semantic failure states, and agent×model trigger matrices. | Harness core |
| Script assertions execute on the host | **Still open.** `--allow-scripts` is a trust gate, not a sandbox. | Optional sandbox executor |
| Ablations fan across irrelevant answer cases | **Still open.** Structured expected-regression cases constrain reporting, not preparation cost. | Harness core selector |

### Local capabilities that should remain local or plugin-owned

1. **Oracle calibration fixtures**: the reusable good/pass and bad/fail lifecycle
   could be a harness extension, but the polarity samples and semantic rules are
   project evidence.
2. **Mutation-backed mini-repos**: a generic control/challenger command contract
   would transfer; JavaScript/Python/Go mutants and kill criteria stay local.
3. **Semantic AST/data-flow oracles**: the assertion plugin boundary is generic;
   E67's registry/fake/contract data flow is project-specific. Shared E67 stays
   static-only because candidate code is untrusted.
4. **Validity and risk taxonomy**: the harness should preserve namespaced
   metadata, while this repository owns its claim/warrant/backing/rebuttal,
   technique, risk, failure-mode, and coverage vocabulary.
5. **Eval-health and release policy**: hidden restraint probes per section,
   rotating probes, P0/P1 rules, install boundary, artifact hygiene, version
   rubric, and audit thresholds are repository governance.
6. **The aggregate release gate**: `skill-development/scripts/check-all.py`
   remains the deterministic project orchestrator.

The earlier local-only list overstated the gap. v0.6 already owns critical
severity, graded dimensions/reference floors, materialized ablations, token
overhead, oracle-strength reporting, saturation/no-lift analysis, judge
robustness, trigger traces, and model-axis reporting. The additive boundary is
now narrower: the harness owns experiment mechanics and generic evidence
contracts; local code owns domain oracles, calibration fixtures, and release
policy.

## Evidence and reproduction

A bounded machine-readable **historical v0.4 attestation** is tracked at
`attestations/issues-20-21-multimodel.json`. It records objective matrices,
raw repeated-judge decisions, decoded blind choices, per-query trigger outcomes,
requested model labels, tool versions, evaluated tree/task hashes, old-skill SHA,
and ignored run-tree digests. Its historical hashes must not be rewritten to imply that v0.6 produced
those candidates. `skill-development/scripts/verify-issues20-21-attestation.py`
defines and checks the retained tree/run digest framing. The exact pre-migration
manifest and prepared-task JSONL were not retained; their hashes are explicitly
authentication-only. Bulky candidates remain ignored.

Current v0.6 reproduction:

```bash
uv tool install --force skill-eval-harness==0.6.0
skill-benchmark validate evals/shared-benchmark.json
skill-benchmark audit-manifest evals/shared-benchmark.json --fail-on-blockers
python3 skill-development/scripts/prepare-issue20-21-harness.py \
  --cases E64,E65,E66 --variants with_skill,without_skill \
  --runs-per-variant 3 --out /tmp/issues20-21.jsonl
MODEL=gpt-5.6-sol
RUNS=skill-development/eval-runs/reproduction/$MODEL
skill-benchmark run-agent --agent codex --tasks /tmp/issues20-21.jsonl \
  --runs "$RUNS" --model "$MODEL" --timeout 600
skill-benchmark benchmark evals/shared-benchmark.json --runs "$RUNS" \
  --split tune --allow-scripts --out /tmp/benchmark.json
skill-pi-trigger-eval evals/shared-benchmark.json --split tune \
  --runs-per-query 3 --trace-runs "$RUNS/trigger-traces" \
  --model "openai-codex/$MODEL" --out /tmp/triggers.json
skill-benchmark compare-tasks evals/shared-benchmark.json \
  --runs "$RUNS" --primary with_skill --baseline without_skill \
  --seed 20260722 --out /tmp/comparisons.jsonl --truth-out /tmp/truth.json
python3 skill-development/scripts/run-blind-comparison.py \
  --tasks /tmp/comparisons.jsonl --manifest evals/shared-benchmark.json \
  --out /tmp/comparison-results.jsonl
skill-benchmark compare-results --truth /tmp/truth.json \
  --results /tmp/comparison-results.jsonl --out /tmp/comparison-summary.json
```

The focused wrapper now performs selection only. v0.6 native runners own
candidate/evaluator workspace isolation. Benchmark and judge commands still
need focused run roots because v0.6 has no general case selector.
