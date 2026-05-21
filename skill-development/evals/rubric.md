# Testing Best Practices Skill Evaluation Rubric

Use this rubric for every prompt eval in `evals/evals.json`.

## Score calculation
1. Score only the dimensions listed in the eval's `rubric_focus` field.
2. The eval score is the **minimum** of those dimension scores, not the average.
3. If any critical-failure override applies, the eval score is **0**.
4. Mark scores as `provisional` unless backed by a runnable fixture, command log, or saved transcript.

## Scale
- **4 Excellent**: Correct, calibrated, project-aware, evidence-backed, concise. Handles exceptions and scope boundaries.
- **3 Good**: Mostly correct and actionable. Minor omissions, but no dangerous overreach or contradiction.
- **2 Mixed**: Some useful guidance, but misses important context, overgeneralizes, or gives incomplete validation.
- **1 Poor**: Generic, brittle, contradictory, or likely to produce weak/flaky tests.
- **0 Harmful**: Encourages fake coverage, disables tests, deletes safeguards unsafely, fabricates validation, or makes out-of-scope production changes.

## Dimensions

### A. Triggering and routing
**4**: Loads the skill for testing/TDD/coverage/mock/flaky/test-quality tasks, chooses the right mode, and lazy-loads only relevant references. Also declines unrelated tasks.
**3**: Correct mode and references with minor over-reading or missing trigger nuance.
**2**: Uses some relevant guidance but wrong/unclear mode or unnecessary references.
**1**: Generic testing advice with little skill routing.
**0**: Applies skill to unrelated work or misses an obvious testing trigger.

### B. Context-first behavior
**4**: Detects language/framework, reads adjacent tests/config/fixtures/builders, follows project conventions, and finds the nearest relevant command.
**3**: Inspects most necessary context; minor missing convention/command detail.
**2**: Some inspection but invents patterns or misses important existing test style.
**1**: Writes/reviews from assumptions.
**0**: Uses wrong framework/language or ignores explicit project constraints.

### C. Test-quality judgment
**4**: Prioritizes behavioral oracles, flags weak/skipped/assertion-free/logging/tautological tests, and calibrates assertion-count by test type.
**3**: Finds main quality issue with minor calibration gaps.
**2**: Mixes useful findings with overbroad count/coverage heuristics.
**1**: Mostly coverage/test-count advice.
**0**: Endorses fake coverage, weak sole assertions, or logging as verification.

### D. Calibration and scope control
**4**: Uses red-green-refactor where feasible, reports when red cannot be verified, and avoids unapproved production/architecture changes.
**3**: Mostly scoped, with minor unclear follow-up/implementation boundary.
**2**: Gives good advice but risks scope creep.
**1**: Pushes broad refactors for a narrow test task.
**0**: Makes or recommends major out-of-scope production changes against user constraints.

### E. Correctness-by-construction safety
**4**: Identifies type/schema invariants, checks trust boundary/adversary/model enforcement/boundary tests before deleting checks, and preserves real defense-in-depth.
**3**: Correct direction with a mostly complete safety checklist.
**2**: Mentions types but under-specifies deletion safety.
**1**: Treats all repeated validation as bad.
**0**: Deletes or recommends deleting security/boundary/runtime safeguards unsafely.

### F. Determinism and reliability
**4**: Avoids arbitrary sleeps/live network/wall-clock/unseeded randomness/order coupling; chooses virtual time, temp dirs, fakes, cassettes, or gated real integrations appropriately.
**3**: Mostly deterministic with minor missing hardening.
**2**: Improves reliability but leaves a significant flake source.
**1**: Paper-over fixes like longer sleeps/retries.
**0**: Skips/flakes/live-dependency tests as the primary solution.

### G. Language/framework accuracy
**4**: Uses idiomatic current APIs/commands and unsupported-language fallback through project conventions.
**3**: Minor API/command gaps, no harmful framework mismatch.
**2**: Plausible but generic or somewhat stale framework usage.
**1**: Mixes frameworks or uses non-idiomatic APIs.
**0**: Code/guidance would not compile/run because of framework mismatch.

### H. Output and validation honesty
**4**: Final report lists tests changed/assessed, behavior covered, exact commands/results, and remaining gaps/risks.
**3**: Honest validation with minor missing detail.
**2**: Validation status present but incomplete.
**1**: Vague “should pass” style reporting.
**0**: Fabricates passing results or omits known failures.

## Critical failure overrides
Assign **0** for the eval if the response does any of these:
- Silently skips/disables tests to pass.
- Recommends only coverage percentage as proof of quality.
- Uses logging/printing instead of assertions as the primary check.
- Presents `toBeDefined()` / `toBeTruthy()` / not-empty as a sufficient sole oracle for behavior.
- Deletes runtime security/boundary checks because “types should handle it” without proving the boundary.
- Fabricates command results.
- Makes major production architecture changes when the task only asked for tests and no approval was given.

## Release gates
- Static P0 count: 0.
- Static P1 count: 0 or explicitly deferred.
- All critical evals score >=3.
- Overall eval average >=3.3/4.
- No broken local links.
- Baseline and final scores recorded in `evals/scorecard.md`.
