# Eval Run 20260521-074558

## Setup
- Skill under test: `../../testing-best-practices/SKILL.md` after router/static-audit fixes.
- Runner: `delegate` subagents, fresh context, instructed to load the skill and read only each fixture `prompt.md`.
- Candidate outputs: `eXX/candidate/`.
- Oracle results: `oracle-results.txt` plus per-eval `oracle.stdout` / `oracle.stderr`.

## Results

| Eval | Fixture oracle | Result |
|---|---|---|
| E01 TypeScript/Vitest sanitizer | `evals/fixtures/e01-typescript-vitest-sanitizer/oracle.py` | PASS |
| E08 deterministic time | `evals/fixtures/e08-deterministic-time/oracle.py` | PASS |
| E12 validation honesty | `evals/fixtures/e12-validation-honesty/oracle.py` | PASS |
| E19 order pollution | `evals/fixtures/e19-order-pollution/oracle.py` | PASS |
| E20 Go zero value | `evals/fixtures/e20-go-zero-value/oracle.py` | PASS |
| E23 Python/Hypothesis parser | `evals/fixtures/e23-python-hypothesis-parser/oracle.py` | PASS |
| E24 Python recorded API fixture | `evals/fixtures/e24-python-recorded-api-fixture/oracle.py` | PASS |
| E25 Go TempDir/fake dependency | `evals/fixtures/e25-go-tempdir-fake/oracle.py` | PASS |
| E26 Rust proptest/no unwrap | `evals/fixtures/e26-rust-result-proptest/oracle.py` | PASS |
| E27 TypeScript/Playwright flake | `evals/fixtures/e27-typescript-playwright-flake/oracle.py` | PASS |

Total: 10 passed, 0 failed.

## Caveat
These are fixture-oracle passes, not full compile/test runs against real projects. They are stronger than prompt-only scoring because each candidate was checked by an executable oracle, but final release scoring should still include human/rubric review and, later, full project fixtures with real test commands.
