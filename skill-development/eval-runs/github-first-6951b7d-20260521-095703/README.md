# Eval Run github-first-6951b7d-20260521-095703

## Setup
- Skill under test: first GitHub working version, `6951b7d Add testing-best-practices skill with research corpus`.
- Skill copy: `../../github-skill-first-working/testing-best-practices/` from this run directory's perspective.
- Runner: `delegate` subagents, fresh context, instructed to load the first skill and read each fixture `prompt.md` only.
- Candidate outputs: `eXX/candidate/`.
- Oracle results: `oracle-results.txt` plus per-eval `oracle.stdout` / `oracle.stderr`.

## Results

| Eval | Result |
|---|---|
| E01 TypeScript/Vitest sanitizer | PASS |
| E08 deterministic time | PASS |
| E12 validation honesty | PASS |
| E19 order pollution | PASS |
| E20 Go zero value | PASS |
| E23 Python/Hypothesis parser | PASS |
| E24 Python recorded API fixture | PASS |
| E25 Go TempDir/fake dependency | PASS |
| E26 Rust proptest/no unwrap | PASS |
| E27 TypeScript/Playwright flake | PASS |

Total: 10 passed, 0 failed.

## Interpretation
The public fixture prompt oracles are saturated across first/current/local skill versions for this model. Use artifact rubric and harder hidden variants to distinguish version quality.
