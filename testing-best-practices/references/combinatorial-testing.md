# Combinatorial Testing and Cost-Aware Portfolios

Use this reference when many discrete factors interact: configurations, feature
flags, plugins, formats, browsers, runtimes, environments, or rendering modes.

A covering array guarantees coverage of specified **modeled interactions**. It
does not guarantee a defect-detection percentage, a minimum-size suite, or
correctness. Missing factors, values, state, sequences, setup, propagation, and
weak oracles remain outside that guarantee.

## Vocabulary

- **Factor**: a dimension such as runtime, format, or feature flag.
- **Level**: one value of a factor.
- **t-way coverage**: every feasible value tuple for every selected `t`-factor
  group appears in at least one row.
- **Constraint**: a rule excluding an impossible combination.
- **Variable strength**: a base strength plus stronger obligations for named
  factor groups.
- **Risk-weighted/prioritized coverage**: important values or tuples are covered
  earlier, more often, or in optional budgeted rows; generalized risk weights
  are a planning heuristic, not a fault-yield guarantee.

Historical studies found many observed failures involved few factors, but the
distributions varied by system. This motivates low-order interaction coverage;
it does not mean pairwise or 3-way testing catches a universal percentage of
bugs.

## Choose the portfolio in this order

1. **Mandatory fixed tests** — incident regressions, security/auth boundaries,
   contracts, legal/compliance checks, and known high-order failures.
2. **Exact one-way enrollment** — every canonical registry member gets at least
   one cheap conformance/smoke case.
3. **Exhaustive cheap slices** — enumerate small finite spaces and pure logic.
4. **Constrained pairwise base** — broad interaction coverage over feasible
   combinations.
5. **Variable-strength groups** — use 3-way or higher only for named coupled,
   hazardous, or historically fault-prone groups.
6. **Property/fuzz tests** — explore values within factors; covering arrays do
   not replace arbitrary-input or stateful testing.
7. **Expensive boundaries** — run representative browser/device/live-service
   rows at a measured slower cadence when they cannot fit the fast lane.

Known regressions are mandatory even when their 4-way or higher interaction is
absent from the generated array. Human review and production monitoring are
separate oracles, not rows to optimize away.

## Build the factor model

For every factor record:

- canonical source of values;
- equivalence classes and boundary representatives;
- constraints and why they exist;
- base and elevated interaction obligations;
- which oracle makes each row meaningful;
- environment/setup requirements and stable case IDs.

Prefer enum/registry-derived values over copied lists. Use a generator such as
ACTS, PICT, or another constraint-aware tool, but treat its output as a smaller
valid suite—not a proven global minimum. Commit or retain the model, constraints,
generator/version, seed when stochastic, rows, and a machine-checkable coverage
report.

### Constraints

Integrate constraints during generation or feasibility solving. Generating an
unconstrained array and deleting invalid rows can silently remove the only row
covering a required feasible tuple. Independently check both:

1. every emitted row is valid;
2. every required feasible tuple is covered.

Do not use constraints merely to remove awkward but valid scenarios.

### Variable strength

Specify a base such as 2-way, then name elevated groups explicitly:

```text
base: 2-way across all factors
3-way: {family, look, palette}
3-way: {format, transparency, security_mode}
fixed: known {runtime, browser, format, font} regression
```

Choose elevated groups from architecture, hazard analysis, changed coupling, or
repaired-fault history—not from a generic claim that more strength is always
better.

### Weights and priorities

Primary studies support prioritizing pairwise/variable-strength suites and, in a
small usage-model study, weighting input combinations by modeled frequency.
General risk weights are an engineering heuristic. State whether a weight applies
to a factor, level, tuple, or complete row and whether it comes from usage,
hazard impact, repaired faults, or judgment.

Weights normally affect prefix order, repetition, or optional rows after hard
coverage obligations. They must not silently erase required interactions.
Evaluate priority at equal execution budgets using time-to-actionable-failure or
coverage gained by the prefix, not an unsupported “bugs caught” promise.

## Preserve exact registry enrollment

Pairwise rows usually contain every modeled value, but that does not prove the
model stayed synchronized with the implementation registry. Keep an independent
exact-set test:

```python
expected = set(canonical_registry)
modeled = {case.member_id for case in one_way_conformance_cases()}
assert modeled == expected
```

Then test the test infrastructure: inject a fake registry member in an isolated
registry, prove it is enrolled automatically, give it deliberately broken
behavior, and prove the generated contract fails for the intended oracle. Do
not use copied expected lists, optional `covered: true` flags, or self-reported
capabilities without contradiction tests.

## Cost-aware selection without false precision

Keep hard obligations first, then compare feasible portfolios across a cost
**vector**:

- CPU/runner use and marginal critical path;
- environment startup and shared-fixture reuse;
- false-red probability, reruns, and human triage;
- maintenance and baseline-review effort;
- failure diagnosis/localization cost;
- repaired-fault and mutation/sabotage evidence.

Do not collapse unlike quantities into one magic score unless the project has
approved and sensitivity-tested the weights. Prefer a Pareto view: show which
portfolio is faster, cheaper, less flaky, or stronger for a named risk, and let
policy choose the trade-off.

### Stable policy versus telemetry

| Input class | Examples | Use |
|---|---|---|
| Stable policy | mandatory risks, registries, constraints, known regressions, budgets | Hard obligations and planning |
| Versioned calibration | duration quantiles, classified flake/rerun history, triage estimates, mutation/sabotage results | Periodic portfolio review |
| Raw telemetry | last duration, queue delay, one retry, isolated failure | Diagnosis only; never directly changes gates |

Calibrate by stable test ID, platform, runner class, and relevant environment.
Use robust distributions rather than one wall-clock sample; classify product,
test, and infrastructure failures separately; retain timeout observations as
censored failures rather than pretending they completed at the timeout. Record
sample counts and uncertainty. Sparse history is “unknown,” not zero value.

## Validate before replacing a portfolio

Run old and proposed portfolios in shadow before deleting tests:

1. mechanically verify all one-way and interaction obligations;
2. replay repaired faults and retain every discriminating regression;
3. run representative mutation/sabotage probes by risk and operator class;
4. keep a rotating randomized full-suite/holdout sample to expose selection
   blind spots;
5. compare case count, CPU and wall time, p50/p90 critical path, retries/flakes,
   triage, maintenance churn, baseline review, kills, and escaped defects;
6. fall back to the mandatory/full policy if the model, registry, calibration,
   or selector is missing or stale.

Pairwise is not a correctness proof. A perfectly covered array with weak oracles
is only systematic execution.

## Worked portfolio shape

For a renderer with families, looks, palettes, outputs, boundaries, runtimes,
security, fonts, and transparency:

- exact cheap one-way conformance for every registry value;
- exhaustive pure checks for small output/option slices;
- constrained pairwise rows across the broad in-process render matrix;
- 3-way `{family, look, palette}` coverage where style interactions are risky;
- fixed tests for known topology, security, font, and transparency regressions;
- property tests for input complexity and serialization invariants;
- representative browser/hosted/runtime rows on slower measured lanes.

Report the generated row count after applying the real constraints; do not
promise a count from an illustrative model.
