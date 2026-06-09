# Iteration 7 — antirez insights: shadow-oracle + statistical-oracle

Adds two unique insights from the antirez research as on-demand guidance in
`references/differential-testing.md`, with fixtures, hidden adversarial
restraint probes, and an audit gate. This iteration's job was to *measure*
whether the new guidance changes agent behavior — via ablation (with-section
vs without-section), an isomorphic Go holdback per insight, and adversarial
over-application probes.

## Method

- **Ablation.** Same prompt run twice: once with `differential-testing.md`
  including the new sections, once with those two sections stripped out. Only
  the two sections differ.
- **Holdback.** The Go fixtures (E34, E36) were never inspected while writing
  the sections; they test whether the behavior generalizes beyond the Python
  dev fixtures (E33, E35).
- **Adversarial restraint.** E37 (deterministic sort) and E38 (trivial pure
  function) check that the new guidance does not cause *over-application*.
- **Grading.** Each output graded by the matching fixture oracle
  (`scripts/run-fixture-oracles.py` self-tests every oracle good/pass + bad/fail).
- **Generation model:** sonnet, one sample per cell. Single-sample, so deltas
  are directional signal, not effect sizes.

## Results

| Insight | Eval | Lang | Role | with-section | without-section | Verdict |
|---------|------|------|------|--------------|-----------------|---------|
| Shadow-model | E33 | python | dev | PASS | FAIL | **discriminates** |
| Shadow-model | E34 | go | holdback | PASS | FAIL | **generalizes** |
| Statistical-oracle | E35 | python | dev | PASS | PASS | ceiling (cue leak) |
| Statistical-oracle | E36 | go | holdback | PASS | PASS | ceiling (cue leak) |
| Restraint: exact output | E37 | python | adversarial | PASS (restrained) | — | guard holds |
| Restraint: trivial fn | E38 | python | adversarial | FAIL → PASS | — | over-application found, guard added |

## Findings

1. **The shadow-model section works and generalizes.** Without it, agents wrote
   a handful of unseeded example tests for `LruCache`/`RingBuffer`; with it,
   they built a seeded shadow model compared on multiple observables — in both
   Python (dev) and Go (held-back). This is the clean win of the iteration.

2. **The statistical-oracle fixtures are at ceiling and did not discriminate.**
   Both with- and without-section runs produced recall-vs-brute-force tests,
   because the prompt named the `brute_force_topk` helper, cueing the behavior.
   This is the repo's documented "ceiling effects mask signal" lesson recurring.
   The section is plausibly useful but **unproven here**; the next iteration
   needs a cue-free fixture (no brute-force helper named in the prompt) to
   isolate it. E35/E36 are marked `saturated_public` accordingly.

3. **An adversarial probe caught a real over-application, which we fixed.** The
   first E38 run (slugify, a trivial pure function) built a `_reference_slugify`
   reimplementation and diffed against it — a reference that just duplicates the
   code and can carry its own bugs. We strengthened the "When NOT to use it"
   guidance in the Differential Testing section; the re-run (E38 v2) showed
   restraint (pinned examples + idempotence + invariants, no reimplementation).
   n=1, so this is suggestive, not conclusive.

4. **Two oracle calibration bugs were found and fixed during grading**, a
   reminder that adversarial oracles need their own scrutiny:
   - E36 false negative: a recall threshold stored in a *named constant*
     (`recallThreshold = 0.80`) was missed by a literal-only regex.
   - E38 false positive: `def \w*slug` matched the *test function names*
     (`test_slugify_examples`); narrowed to non-test helpers only.
   Both fixture oracles still pass their good/pass + bad/fail self-tests.

## Net

- Shadow-model insight: **validated** (discriminates + generalizes), shipped.
- Statistical-oracle insight: **shipped but unproven** (fixtures at ceiling);
  flagged for a cue-free fixture next iteration.
- Both sections ship with a hidden adversarial probe enforced by
  `audit-best-practices.py` (now 110/110); E38 probe already paid for itself.
</content>
