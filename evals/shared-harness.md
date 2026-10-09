# Shared benchmark evals

This repo participates in the shared Skill Eval Harness:

- Repo: https://github.com/adewale/skill-eval-harness
- Tested and pinned version: `0.6.0`
- Manifest: `evals/shared-benchmark.json` (schema version 2)

Install the released harness with [uv](https://docs.astral.sh/uv/):

```sh
uv tool install --force skill-eval-harness==0.6.0
```

Splits:
- `tune` — visible iteration cases.
- `holdout` — hidden end-of-round / merge scoring cases.
- `holdback` — examples withheld from `SKILL.md`, references, docs, and public eval descriptions until after scoring.

Validate and audit from this repo root:

```sh
skill-benchmark validate evals/shared-benchmark.json
skill-benchmark audit-manifest evals/shared-benchmark.json --fail-on-blockers
```

Prepare focused paired tasks. The wrapper supplies the case selector missing from v0.6; the native runner owns per-variant workspace isolation:

```sh
python3 skill-development/scripts/prepare-focused-harness.py \
  --cases pos-mutation-recurring-lane-contract,pos-mutation-survivor-triage-cuefree,pos-combinatorial-cost-aware-portfolio \
  --runs-per-variant 3 \
  --out /tmp/testing-best-practices-tasks.jsonl
skill-benchmark run-agent --agent codex \
  --tasks /tmp/testing-best-practices-tasks.jsonl \
  --runs eval-runs/latest --model gpt-5.6-sol
```

Prepare materialized ablations with structured provenance:

```sh
python3 skill-development/scripts/prepare-focused-harness.py \
  --cases pos-api-contract-vcr,pos-cli-doc-sync,pos-parser-property \
  --variants with_skill,ablations --include-ablations \
  --ablation-dir /tmp/testing-best-practices-ablations \
  --out /tmp/testing-best-practices-ablation-tasks.jsonl
```

Harness v0.6 materializes the declared section removals and records tree hashes/provenance, but preparation still fans every answer-population ablation across every answer case. The wrapper discards ablation rows not named by structured `expected_regressions`; this is a cost-control workaround, not a harness causal claim. A confirmed ablation regression needs exact same-revision pairs, named assertion coverage, and enough informative pairs for the sign-flip gate.

Run autonomous Pi trigger checks for trigger/no-trigger cases:

```sh
skill-pi-trigger-eval evals/shared-benchmark.json --split tune \
  --runs-per-query 3 --trace-runs eval-runs/trigger-traces \
  --out /tmp/testing-best-practices-trigger-report.json
```

`old_skill` is optional and intentionally not emitted unless `old_skill_paths` is populated and `--include-old-skill` is passed. Hidden `holdout` / `holdback` prompt refs must be supplied privately before scoring; use `--allow-missing-prompts` only for dry-run planning.

Grade saved outputs:

```sh
skill-benchmark benchmark evals/shared-benchmark.json \
  --runs eval-runs/latest --allow-scripts \
  --out /tmp/testing-best-practices-benchmark.json
```

Run optional qualitative judges through a native backend:

```sh
skill-benchmark judge evals/shared-benchmark.json --runs eval-runs/latest \
  --judge-backend codex --judge-model gpt-5.4 \
  --transcripts eval-runs/judge-transcripts \
  --out /tmp/testing-best-practices-judge-results.jsonl
skill-benchmark benchmark evals/shared-benchmark.json --runs eval-runs/latest \
  --allow-scripts --judge-results /tmp/testing-best-practices-judge-results.jsonl \
  --out /tmp/testing-best-practices-benchmark.json
```

Script assertions are repo-owned commands and require `--allow-scripts`. The harness does not sandbox them. Shared E67 grading performs AST-only checks on model output; execute candidate code only in a disposable OS/container sandbox with no secrets, network, or writable host mounts.

## What the checks establish

| Check | What a pass establishes | What it does not establish |
|---|---|---|
| Manifest validation / leakage audit | Declared cases and references satisfy the checked schema and detectable leakage rules. | Independent test quality, absence of all leakage, or model uplift. |
| `contains`, `contains_any`, regex | The saved answer contains the requested text pattern. | Correct advice, working tests, or effective PBT. An `oracle: strong` label does not turn a text match into behavioral evidence. |
| Fixture scripts that inspect prose | The answer meets that script's bounded content rules. | Working candidate code or production behavior. Read the actual checker, not its generic description. |
| AST fixture scripts / GTB adapter | Extracted code is parseable and has the specific checked assertion/implementation shapes. | That the code executes successfully or its assertions catch every defect. Shared E67 never executes candidate code. |
| Trusted fixture self-tests | Known good/bad samples have the expected result under the local checker. | Generalization to arbitrary answers, or a model comparison. |
| Optional qualitative judge | The configured judge rated the saved output against its rubric. | An independent executable oracle; ratings can be wrong. No judge run is required by this documentation change. |
| Collector / backend stub checks | The tested entrypoint discovers the expected IDs or handles the stubbed invocation correctly. | A live CLI's current behavior, model quality, or a successful provider call. |
| Paired skill / no-skill comparison | With fixed revisions, cases, models and comparable runs, it can estimate an effect on those measured outcomes. | Portfolio-wide causal uplift, or comparability after prompts/oracles change. |

### URL parser: literal test-vector check

`round3-fixture-url-parser-tests` previously accepted a keyword salad and
recommended a no-crash oracle for an API that intentionally throws. Its revised
prompt requests bounded JSON test vectors with independent literal expected
fields and invalid-input `TypeError` cases. The replacement script checks those
data values against Node's native URL behavior, including normalization and
path/query/fragment coverage. It never evaluates model-supplied code.

A pass establishes a useful, correct **test plan for this fixture**, not that
suggested Vitest tests execute, a property generator is effective, or the model
understands every URL edge case. The existing weak-assertion text check only
establishes that the answer mentions the problem. The script retains its `demo`
classification; this is one case repair, not global retiering or a new gate
policy. The removed property/fuzz keyword requirements were not evidence of
effective technique selection.

Run its local positive/negative controls without a model or new dependency:

```sh
node --test evals/oracles/url_test_vectors.test.mjs
```

The shared script requires Node.js (the controls use Node 22+). Missing runtime,
malformed/oversized output and missing vectors fail closed. No CI job, scheduled
campaign or paid model run is added. Historical scores for the old prompt/oracle
are not comparable to this revision; rerun both variants before making a causal
claim. Other cases keep their existing grading policy and still have the limits
shown above; this is not a claim that every weak eval has been repaired.

### E59: recorded deposit, not merely a transaction-list mention

`pos-narrow-assertions-upgrade` previously accepted `assert
account.transactions is not None`: an empty list satisfies it. Its existing
AST checker now requires literal kind/amount/memo expectations for the single
recorded deposit, either as a list equality or a length check plus row/field
equalities. Both normal and reversed equalities and `assertEqual` are supported.
The new non-None-list negative sample is checked through the existing fixture
self-test mechanism. This proves the checker rejects that specific weak shape;
it does not prove candidate tests run, reach their assertions or bind to the
real implementation. The shared GTB adapter and `demo` tier are unchanged.
