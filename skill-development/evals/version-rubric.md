# Skill Version Rubric

This rubric scores the installable skill artifact itself. It complements prompt/fixture evals by detecting whether the skill contains the guidance needed to produce good behavior. This is the layer that should distinguish early, current-GitHub, and local versions even when prompt oracles saturate.

Total: 100 points.

## A. Router and operational usability — 15
- `SKILL.md` is concise enough for progressive disclosure: target <=350 lines, hard max <=500.
- Clear modes/workflows for write, assess, upgrade, detect.
- First-context checklist: language/framework detection, adjacent tests/config, runner commands, risk boundary.
- Reference matrix/lazy loading guidance.
- Final report/validation contract.

## B. Static safety and calibration — 25
- No P0 contradictions or unsafe guidance: weak `toBeDefined()` example, six/seven mismatch, MSW mislabeled as VCR, external-dependency-only integration definition, universal positive+negative rule, unsafe deletion wording, false Go `Email{}` claim.
- No P1 overbroad mandates: unconditional TDD, hard 3+ assertion rule, unit tests banning temp dirs, “every Go test table-driven,” vague reference links, oversized router.
- Assertion count is calibrated by test type.
- TDD is evidence-gated and honest about feasibility.

## C. Core language coverage — 15
- Python reference.
- TypeScript/JavaScript reference.
- Go reference.
- Rust reference.
- Unsupported-language fallback and project-convention guidance.

## D. Testing technique breadth — 20
Credit for canonical guidance/triggers for:
- deterministic time,
- characterization,
- differential/pirate/conformance,
- golden/snapshot,
- doc-sync,
- exhaustive testing,
- mathematical properties,
- mutation testing,
- test data builders,
- VCR/recorded fixtures.

## E. Correctness-by-construction safety — 15
- Dedicated correctness-by-construction/type-vs-test guidance.
- Safety preconditions before deleting checks/tests.
- Go zero-value caveat.
- Scope-control: no production type/architecture changes when user asks for tests only.
- Preserves real defense-in-depth for distinct adversaries/failure modes.

## F. Validation and reporting honesty — 10
- Validation loop checks weak assertions, skips/focus markers, logging-not-asserting, sleeps/live network, and implementation coupling.
- Final answer reports commands/results/gaps.
- Recommends mutation/gap analysis for high-coverage weak suites.

## Interpretation
- 90–100: installable/release-quality skill artifact.
- 75–89: strong but still has important gaps or contradictions.
- 50–74: usable but incomplete/brittle.
- <50: early working draft or major safety/coverage gaps.
