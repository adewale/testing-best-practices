# Iteration 10 — non-time isolation for design-for-testability: fold decision

Iteration 9 left `design-for-testability.md` unproven: on time-adjacent
fixtures, the `deterministic-time.md` baseline absorbed its contribution. This
iteration removed the confound — fixtures whose background work is triggered
by **write volume** (condition variable) and **channel drain** (goroutine),
with no timers — so clock injection cannot carry the without-arm. If the
section discriminates anywhere here, it's on its home turf.

**Pre-registered decision rule** (committed before any runs): discriminate on
at least one fixture (artifact-verified) → keep the reference; both arms pass
both fixtures → fold the validated guardrails + core into
`deterministic-time.md` and drop the standalone file.

## Results (after oracle fix; sonnet, n=1 per cell)

| Eval | Lang | Role | with | without | Verdict |
|------|------|------|------|---------|---------|
| E50 compactor | python | dev | PASS | PASS | ceiling |
| E51 aggregator | go | holdback | PASS | PASS | ceiling |

Artifact verification (mandatory after iteration 9's lessons):
- **E50/without** built `wait_for_compaction()` backed by a `threading.Event`
  set after each compaction pass — a genuine, bounded synchronization seam.
- **E51/without** built `Flush()` blocking on a `sync.WaitGroup` until every
  enqueued record merged — a genuine forced-drain seam.
- The with-arms produced the *taught* shape (disable worker + `compact_now()`
  / `Drain()` + introspection); the without-arms produced *synchronization*
  seams. Both deterministic, both correct. The teaching changes the style,
  not the outcome.

## Oracle calibration bug #5 (false negative, caught by reading artifacts)

The first grading pass failed 3 of 4 runs for "real sleep still present" —
every flagged `sleep` was in a comment or docstring *describing the old flaky
test* ("The original test ... called time.sleep(0.5)"). The oracles now strip
comments/docstrings before the sleep check; self-tests still pass (the bad
samples' real sleeps are code, not comments). Five of five oracle bugs across
three iterations have been false negatives punishing good work.

## Decision: fold (per the pre-registered rule)

With the time seam removed, priors alone produce real seams in both
languages. The forced-transition *teaching* is redundant; the **guardrails**
are the only unique, validated content (E46 restraint probe: clock injection,
no env-var bypass of a rate limit). Executed:

- `references/design-for-testability.md` deleted (~1,020 on-demand tokens).
- `deterministic-time.md` gains a compact "When the seam isn't time: forced
  transitions, and guardrails" section (~330 tokens) carrying the seam essence
  and the full guardrails.
- SKILL.md trigger merged into the deterministic-time line.
- Audit gate's section→probe mapping remapped: the guardrails text in
  `deterministic-time.md` must keep the E46 hidden adversarial probe.
- E50/E51 marked `saturated_public` with the fold rationale in rebuttals.

Net token effect: ≈ −700 on-demand tokens vs iteration 9, with the validated
guardrail content preserved and still probe-enforced.
