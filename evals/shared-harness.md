# Shared benchmark evals

This repo participates in the shared skill benchmark harness at `../skill-eval-harness/` from the multi-repo workspace.

Manifest: `evals/shared-benchmark.json`

Splits:
- `tune` — visible iteration cases.
- `holdout` — hidden end-of-round / merge scoring cases.
- `holdback` — examples withheld from `SKILL.md`, references, docs, and public eval descriptions until after scoring.

Validate from the workspace root:

```sh
python3 skill-eval-harness/skill_benchmark.py validate testing-best-practices/evals/shared-benchmark.json
```

Prepare paired run tasks:

```sh
python3 skill-eval-harness/skill_benchmark.py prepare testing-best-practices/evals/shared-benchmark.json --split tune --out /tmp/testing-best-practices-tasks.jsonl
```

Include ablation variants when running a focused regression check:

```sh
python3 skill-eval-harness/skill_benchmark.py prepare testing-best-practices/evals/shared-benchmark.json --split tune --include-ablations --out /tmp/testing-best-practices-ablation-tasks.jsonl
```

`old_skill` is optional and intentionally not emitted unless `old_skill_paths` is populated and `--include-old-skill` is passed. Hidden `holdout` / `holdback` prompt refs must be supplied privately before scoring; use `--allow-missing-prompts` only for dry-run planning.

Grade saved outputs:

```sh
python3 skill-eval-harness/skill_benchmark.py benchmark testing-best-practices/evals/shared-benchmark.json --runs testing-best-practices/eval-runs/latest --out /tmp/testing-best-practices-benchmark.json
```
