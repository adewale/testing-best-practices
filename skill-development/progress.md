# Progress

## Status
Plan execution complete to the current repository's automatable boundary: static gates pass, eval shape/core-language gates pass, leading-skills comparison is documented, 10 fixture oracles self-test good/bad samples, and one fixture-backed prompt run passed all 10 executable oracles.

## Completed
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
# OK: 27 evals, required taxonomy and core language coverage present.

python3 scripts/run-fixture-oracles.py
# OK: 10 fixture oracles passed self-tests.

python3 scripts/check-all.py
# OK: all local gates passed
```

## Fixture-backed prompt run
- Run directory: `eval-runs/20260521-074558`
- Runner: `delegate` subagents with fresh context, instructed to load the updated skill and read each fixture prompt only.
- Oracle result: 10 passed, 0 failed.
- Scorecard updated with `3*` for the 10 oracle-backed evals (`*` = executable oracle pass, not full human/rubric release score).

## Remaining non-automated work
- Human/rubric-score the saved candidates if a full 0–4 release score is needed.
- Add a prompt runner if this repo will execute model comparisons automatically.
- Add hidden/rotating variants after collecting more transcript data.
