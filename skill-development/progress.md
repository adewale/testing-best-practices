# Progress

## Status
Issues #20/#21 implementation is complete to the repository's automatable boundary: 69 development evals validate, 17 hidden probes are registered, 46 fixture oracles self-test good/bad samples, all three mutation mini-repos kill their seeded fault, the best-practices audit is 110/110, and the installable boundary is clean. E64–E69 are also registered in the shared Skill Eval Harness manifest. A seven-requested-model OpenAI run plus three-repeat public-tune E64–E66 evaluation found an aggregate objective arm difference of 24/63 with skill versus 9/63 without, concentrated in `gpt-5.6-sol`; E67–E69 remain regression/restraint probes rather than stable effect-size evidence.

## Issues #20/#21 completed
- Reframed mutation testing as focused survivor triage; separated survivor/tool statuses; removed arbitrary score ranking and blanket nightly/P0 language.
- Added the conservative recurring-lane contract: demonstrated fault-class bite, target-CI baseline, focused scope, capacity, owner/action path, no uncalibrated floor, expiry, and operational-failure stop rule.
- Added primary-source combinatorial portfolio research and shipped constrained pairwise, variable-strength, registry enrollment, cost-vector, telemetry, and shadow-validation guidance.
- Corrected the unsupported universal 2-way/3-way percentages and practical-generator minimality claim.
- Added E64–E69 plus six executable fixtures and hardened their semantic/polarity checks after independent review.
- Updated README/changelog/taxonomy/token reports and recorded ablation results in `evals/scorecard.md`.
- Generated the historical E64–E69 multi-model evidence with Skill Eval Harness v0.4.0, then upgraded the installed tool and manifest to v0.6.0/schema v2. A migrated copy of all 126 candidates preserved the 24/63 versus 9/63 objective matrix; a native v0.6 Codex smoke confirmed lossless answers, schema-v3 telemetry, workspace isolation, and skill-invocation normalization.

## Historical v0.3 foundation
- Verified public skill sources via GitHub raw files and recorded exact URLs/SHAs in `research.md`.
- Searched <https://www.skills.sh/?q=tdd> and <https://www.skills.sh/?q=testing>, plus skills.sh sitemaps, and documented leading skills in `LEADING_SKILLS_COMPARISON.md`.
- Rewrote `SKILL.md` as a compact operational router with first-90-seconds checklist, reference matrix, calibrated TDD/assertion guidance, scope-control rule, validation loop, and final report contract.
- Fixed known P0/P1 contradictions in references.
- Expanded `evals/evals.json` to 27 evals with core coverage for Python, Go, TypeScript, and Rust.
- Updated `scripts/score-evals.py` to require at least two evals and one critical eval for each core language family.
- Added `evals/eval-health.md`, applying “Your Evals Will Break and You Won't See It Coming”: track saturation, proxy gaming, correlation drift, stale framework assumptions, and rotating probes.
- Added fixture oracle protocol in `evals/fixtures/README.md`.
- Added `scripts/run-fixture-oracles.py`.
- Added `scripts/check-all.py` to run all local non-LLM gates.
- Added `evals/version-rubric.md` and `scripts/score-skill-version.py` to distinguish installable skill versions when prompt oracles saturate.
- Compared first GitHub (`6951b7d`), current GitHub (`6e8cd8b`), and local in `VERSION_COMPARISON.md`.
- Added runnable oracle fixtures:
  - `evals/fixtures/e01-typescript-vitest-sanitizer`
  - `evals/fixtures/e08-deterministic-time`
  - `evals/fixtures/e12-validation-honesty`
  - `evals/fixtures/e19-order-pollution`
  - `evals/fixtures/e20-go-zero-value`
  - `evals/fixtures/e23-python-hypothesis-parser`
  - `evals/fixtures/e24-python-recorded-api-fixture`
  - `evals/fixtures/e25-go-tempdir-fake`
  - `evals/fixtures/e26-rust-result-proptest`
  - `evals/fixtures/e27-typescript-playwright-flake`
- Each fixture has `manifest.json`, `prompt.md`, `oracle.py`, `samples/good`, and `samples/bad`.
- Updated `evals/evals.json` measurement notes and `evals/scorecard.md` evidence paths for fixture-backed evals.

## Version comparison results

| Version | Artifact rubric | Static audit | Fixture prompt oracles |
|---|---:|---:|---:|
| First GitHub (`6951b7d`) | 28/100 | 6 P0 / 4 P1 | 10/10 |
| Current GitHub (`6e8cd8b`) | 69/100 | 6 P0 / 6 P1 | 10/10 |
| Local working tree | 100/100 | 0 P0 / 0 P1 | 10/10 |

Conclusion: the fixture prompt oracles are saturated across all three versions. The added artifact rubric distinguishes all three versions and should be kept as a separate eval layer.

## Current check results
```bash
python3 scripts/static-audit.py
# OK: P0 findings: 0, P1 findings: 0

python3 scripts/score-evals.py --evals evals/evals.json
# OK: 69 evals, required taxonomy and core language coverage present.

python3 scripts/run-fixture-oracles.py
# OK: 46 fixture oracles passed self-tests.

python3 scripts/check-all.py
# OK: all local gates passed
```

## Historical fixture-backed prompt run
- Historical runner: `delegate` subagents with fresh context, instructed to load the updated skill and read each fixture prompt only.
- Oracle result: 10 passed, 0 failed.
- Scorecard updated with `3*` for the 10 oracle-backed evals (`*` = executable oracle pass, not full human/rubric release score).
- Raw generated `eval-runs/` directories are intentionally ignored; tracked artifacts are fixtures, oracles, summaries, and scorecards.

## Remaining non-automated work
- Add genuinely private issue-specific holdout/holdback prompts and answer-key plumbing; the answer-key path is now explicitly namespaced under `x_local_evaluator` because v0.6.0 does not consume `answer_ref` for judges.
- Repeat E67–E69 before using their cross-model rates as anything beyond regression/restraint evidence.
- Keep local oracle self-tests, mutation mini-repos, semantic oracles, and release audits. Use v0.6 native materialized ablations, with local filtering until the harness can scope ablations to relevant cases.
