# Iteration 11 — Voas fault-masking (PIE): ceiling, trimmed to framing

Takes the one genuinely-new concept from the design-for-testability literature
review through the eval pipeline: Voas & Miller's fault-hiding theory. Code that
silently absorbs anomalies (clamp, swallow-to-default, recover-to-zero, high
domain/range ratio) lets a fault Execute without Infecting/Propagating to the
asserted output, so a passing test is weak evidence. Shipped as antipattern #14
+ a PIE "Why it works" paragraph in `mutation-testing.md`.

## Method

- Assess-mode ablation: same test-quality-review prompt, with vs without
  antipattern #14 (the only variable; the without-bundle also strips the
  quick-table row). E52 Python dev, E53 Go holdback, E54 hidden adversarial
  (a *documented* clamp that must NOT be flagged as fault-masking).
- sonnet, n=1 per cell. Every oracle FAIL **and** PASS verified against the
  assessment prose (assess-mode oracles are softer than code oracles).

## Results

| Eval | Lang | Role | with | without | Verdict |
|------|------|------|------|---------|---------|
| E52 | python | dev | PASS | PASS | **ceiling** |
| E53 | go | holdback | PASS | PASS | **ceiling** |
| E54 | python | adversarial | PASS (restrained) | PASS (restrained) | guard holds (both arms) |

## Findings

1. **Detection is at ceiling — priors already catch it.** Without #14, the
   Python arm wrote: "this test would pass even if `compute_score` returned a
   constant, crashed silently on every input, or lost all its business logic…
   `max(0, min(100, score))` structurally enforces the only invariant." The Go
   arm: "any implementation that always returns 42 — or 0 — would pass; the test
   cannot distinguish correct behavior from a stub," and flagged the dead
   `recover()` path. Frontier models reach the fault-masking insight via the
   existing not-empty / tautological-assertion knowledge (antipattern #2). This
   is the design-for-testability outcome again: the concept is real and correct,
   but already in priors.

2. **The restraint guard held in both arms.** Neither arm flagged the documented
   `set_volume` clamp as fault-masking; the without-arm treated it as adequate
   and suggested boundary cases. So E54 guards the *with-section* behavior
   (the section must not induce over-application), not a with-vs-without delta —
   and the section passes it.

3. **The additive residue is framing, not detection.** The with-arm uniquely
   produced the explicit PIE decomposition (Execution/Infection/**Propagation
   blocked**) and the mutation tie; the without-arm reached the same conclusion
   without that vocabulary. The one behavioral nuance #14 adds — "assert the
   **pre-mask/internal value**, because asserting the clamped output still can't
   see an infection that clamps to a valid value" — appeared in the with-arm but
   is unproven at n=1.

4. **Oracle calibration bug #6 (false negative).** The E52-without oracle failed
   an excellent assessment because its weakness regex wanted "passes even" but
   the prose said "would pass even if." Reading the artifact caught it; the regex
   now accepts the concept's phrasings (tautological, structurally enforces,
   cannot distinguish, would/will pass). Six of six oracle bugs across four
   iterations have been false negatives on good work.

## Decision: trim to the non-redundant core (consistent with the iter-10 fold)

Detection duplicates priors + antipattern #2, so the verbose #14 entry was
trimmed ~50%: the mask catalog and detection prose were cut, keeping only the
non-redundant residue — the PIE framing, the assert-pre-mask-state fix (the one
move the without-arm missed), the cross-references, and the restraint clause.
The `mutation-testing.md` PIE "Why it works" paragraph is kept in full: it is
cleanly additive (nothing else explains *why* mutants survive masking code) and
was not part of the ablation. E52/E53 marked `saturated_public`.

## Net

- Fault-masking **detection**: at ceiling (priors + #2 already deliver it).
- Kept: the PIE framing/mutation grounding (additive, explanatory) and the
  restraint guard (E54-enforced).
- Trimmed: the redundant detection bulk. Net token change vs the first cut is
  negative; net vs main is a small framing addition with eval-enforced restraint.
