# Mutation Testing

Mutation testing asks a focused question: **would these tests detect this class of
small code change?** It is a diagnostic for improving tests and code, not a
percentage-correct score for the product.

## When it earns its cost

Use it when one or more apply:

- bugs escape despite high execution coverage;
- a critical module has weak, indirect, or fault-masking oracles;
- security, authorization, financial, or other high-consequence logic changed;
- a test-quality audit found trivial assertions or untested boundaries;
- a focused survivor harvest will drive a named test or code decision.

Do not enroll every module merely for parity. Start with changed, covered code or
a small critical module.

## Why it works: Execute, Infect, Propagate

For a seeded fault to be caught, the mutated statement must be **executed**, the
mutation must **infect** program state, and the infection must **propagate** to an
observable assertion. A survivor can reveal a missing path, weak oracle, or code
that masks faults before they become observable.

Use this as a diagnostic, not a mandate to couple tests to private state. Prefer
a smaller public seam or explicit observable diagnostic. Assert pre-mask or
internal state only when it is a stable, approved testability seam. A documented
clamp or fallback may be the behavior under test rather than a fault mask; see
"Asserting through fault-masking code" in `references/antipatterns.md`.

## How to interpret a run

1. The tool applies operators such as `>=` → `>` or `True` → `False`.
2. Relevant tests run against each generated mutant.
3. A failing test **kills** the mutant.
4. A passing test leaves a **survivor that requires classification**.
5. Act on useful survivors, then compare only like-for-like runs.

First separate tool/run statuses: an actual **survivor** completed with tests
passing; no-coverage, timeout, compile/static, and infrastructure outcomes are
distinct statuses whose score treatment is tool-specific. Then classify actual
survivors as:

- actionable behavior/oracle gap;
- equivalent or redundant mutation;
- dead/redundant code that should be removed;
- specified fault masking or graceful degradation;
- irrelevant/invalid operator for the domain.

Some mutants are semantically equivalent to the original and cannot be killed by
any test. Perfect general equivalence classification is impossible. In one study
of 140 manually classified survivors across seven Java programs, about 45% were
equivalent and classification averaged about 15 minutes per mutant; that sample
shows the caveat is material, not that 45% is a universal rate
([Schuler & Zeller](https://doi.org/10.1002/stvr.1473)). Mutation operators also
miss some real-fault classes, including algorithmic changes and code deletion
([Just et al.](https://doi.org/10.1145/2635868.2635929)).

Use the selected tool's status and denominator definitions. A mutation score is
not percent correctness, and `100%` is not a universal attainable target.
Mutation-score correlation with real-fault detection becomes weak when test-suite
size is controlled, although higher scores among equal-sized suites can still
guide improvement
([Papadakis et al.](https://doi.org/10.1145/3180155.3180183)).

## Focused workflow

1. Name the module, fault class, owner, decision, and time/attention budget.
2. Run the exact configuration manually on the target infrastructure.
3. Retain the report and separate infrastructure failures from completed results.
4. Triage representative survivors before adding tests or policy.
5. Add a behavior/property/regression test, improve an observable seam, remove
   dead code, or record why the mutant is not actionable.
6. Stop when the decision is answered or the budget expires.

Suppress arid/unproductive mutants (for example logging changes or code whose
checks the tests mock away), avoid stacking many mutants on one line, and show
reviewers focused findings rather than a global score. Google reported about
70% bug–mutant coupling in its studied data and reduced developer-marked noise
from roughly 80% to roughly 15% through suppression; treat those as fleet-specific
evidence that false-positive cost constrains adoption, not as universal rates.

Triage security-boundary survivors promptly, but assign P0 only when a relevant,
non-equivalent survivor plausibly represents a critical exploit or bypass.

## Operating a recurring lane

Prefer changed-code, incremental, or review-time feedback. Google's at-scale
system follows this pattern rather than publishing a codebase mutation score
([Petrovic et al.](https://doi.org/10.1109/TSE.2021.3107634)).

As this skill's conservative default for an unattended recurring lane, require:

- one complete retained baseline on the target CI; **no baseline, no schedule**;
- evidence that the lane bites on a named fault class (a repaired fault, seeded
  sabotage, or prior actionable mutant);
- focused scope whose measured runtime fits its timeout and compute budget;
- a named owner and a result that either blocks a decision or notifies someone;
- stable scope/operators plus like-for-like history before any score policy;
- an expiry/removal criterion and response to repeated operational failures.

Default to informational results. Prefer a changed-code policy such as “no newly
surviving actionable mutant” over an absolute repository score. A requested round
number is not calibration: with no comparable baseline/history, do not configure
an absolute floor. If one is later justified, derive it from reviewed history for
that exact lane. [StrykerJS defaults `break` to `null`](https://stryker-mutator.io/docs/stryker-js/configuration/), so build failure is opt-in.

Sharding a whole-repository sweep may fix capacity, but it does not prove the
scope has value; narrow to changed code or a named critical module first. After
three consecutive operational/infrastructure failures—or red results that remain
untriaged—fix, narrow, disable, or delete the lane before expanding it. This is a
skill policy, not an academic constant. A correctly acted-on product finding is
not an operational failure. A schedule that neither blocks nor notifies is a
write-only log.

## Tools by language

| Language | Tool | Useful focus feature |
|---|---|---|
| Python | mutmut | Cached/incremental reruns |
| JavaScript/TypeScript | Stryker | Incremental mode; `break: null` default |
| Java/JVM | PIT | History and targeted classes |
| Go | gremlins | Package-focused mutation |
| Rust | cargo-mutants | Package/file filters |
