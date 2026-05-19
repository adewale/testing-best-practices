# Iteration CBC — Correctness-by-Construction Evals

Two new eval cases targeting the principle introduced in PR #1. Both run
via a subagent simulating "agent with the skill loaded" rather than via
the external runner. Output captured under each `with_skill/` directory.

## Summary

| Eval | Language | Mode | Pass criteria | Result |
|---|---|---|---:|---|
| 11 | Python | Write | 6/6 + 2 bonus | **PASS** |
| 12 | Go | Write | 5/5 + 3 bonus | **PASS** |

Total: 11/11 explicit criteria, 5 bonus findings.

## Eval 11 — Python subscription module with three-layer defense

Fixture: `evals/files/subscription.py` — a controller/service/repo module
where the same invariants (`user_id != None`, `plan in {free, pro,
enterprise}`, `monthly_cents >= 0`) are checked at every layer, plus a
silent fallback in the repo that coerces negative cents to 0.

**Critical behaviours required**: recognise the antipattern, recommend
lifting to types, write tactic-A invariant-proof tests, write tactic-B
model-gap tests, do NOT duplicate "rejects null" tests across layers,
flag the silent fallback.

**Result**: All six required behaviours present. Bonus: the agent's
tactic-B test surfaced a real model gap — Python's `isinstance(True, int)`
is `True`, so booleans slip through as `user_id`. This is exactly the
audit value the principle predicts.

## Eval 12 — Go order state machine (the hard case)

Fixture: `evals/files/order_state.go` — a state machine where the type
permits constructing `Order{Status: Paid, Items: nil}` directly. This is
the scenario the Go-zero-value caveat in
`references/correctness-by-construction.md` was written for.

**Critical behaviours required**: recognise that the bad state is
directly constructible, *explicitly flag that a naive tactic-B test
passes vacuously*, write transition-level invariant proofs, document
the convention-only nature of struct invariants, use table-driven tests.

**Result**: All five required behaviours present. The agent specifically
references the caveat and chooses `t.Logf` ("document the gap") over
`assertPanics` (which would pass trivially). Bonus findings: caught that
`Cancel(Status(99))` succeeds — a behavioural gap, not just a type gap;
flagged silent fallback in `Total` for negative quantities; correctly
distinguished `t.Logf` (documented but expected) from `t.Errorf`
(actual deviation from intent).

## What this validates

- **Tactic A (invariant-proof PBT) translates to behaviour.** Both
  outputs use PBT or exhaustive enumeration to assert postconditions
  rather than enumerating examples.
- **Tactic B (model-gap) translates to behaviour.** Both outputs include
  tests that try to reach forbidden states, and in both cases those
  tests surfaced real bugs the agent would not have found by writing
  conventional "rejects bad input" tests.
- **The Go-zero-value caveat translates to behaviour.** Eval 12's agent
  did not write a naive tactic-B test against the unprotected struct;
  it explicitly chose the documenting variant per the caveat. Without
  the caveat in the reference, the agent would likely have written
  `assertPanics(Order{Status: Paid})` which would pass vacuously.
- **The defense-in-depth-as-antipattern detection translates to
  behaviour.** Eval 11's agent refused to write per-layer "rejects
  null" tests with the explicit reasoning "that would lock in the
  antipattern."

## What this does NOT validate

- **No without-skill baseline run.** I did not generate a comparison
  "agent without the skill" output for the same fixtures. The score is
  100% against the criteria but the *uplift* over a no-skill agent is
  not measured.
- **No assess-mode eval.** The new principle has a corresponding Step 7
  in Assess mode, but no eval exercises it. A natural follow-up: an
  eval that hands the agent a test file full of per-layer "rejects
  null" tests and asks for a review.
- **Other languages.** TypeScript, Rust, Java not exercised.
- **The eval format used here (subagent simulation) is not identical to
  the external runner that produced iteration-1 / iteration-3 results.**
  Treat these as a sanity check, not as a head-to-head score.

## Recommended next eval iteration

1. Run all 12 evals through the external runner once the PR lands.
2. Add an assess-mode eval that hands the agent a test file with
   per-layer "rejects null" tests and grades whether the agent
   recommends collapsing them.
3. Add a TypeScript eval where branded types are the right answer.
