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
python3 skill-development/scripts/prepare-issue20-21-harness.py \
  --cases E64,E65,E66 --runs-per-variant 3 \
  --out /tmp/testing-best-practices-tasks.jsonl
skill-benchmark run-agent --agent codex \
  --tasks /tmp/testing-best-practices-tasks.jsonl \
  --runs eval-runs/latest --model gpt-5.6-sol
```

Prepare materialized ablations with structured provenance:

```sh
python3 skill-development/scripts/prepare-issue20-21-harness.py \
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
