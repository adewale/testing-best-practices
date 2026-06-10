# Iteration 8 — cue-free statistical fixtures + design-for-testability + digest roundtrips

Three goals: (1) resolve iteration 7's open question — does the statistical-oracle
section actually change behavior, or was E35/E36's pass driven by prompt cues;
(2) ship and measure `references/design-for-testability.md`; (3) ship and
measure the whole-state roundtrip-digest section in `golden-file-testing.md`.

## Method

- **Cue-free prompts** for the statistical insight: E39/E40 name only the
  documented `similarity` metric — never "brute force", "recall", "oracle", or
  "threshold". The design has to come from the guidance or priors; the ablation
  separates which.
- **Strong baselines**: the testability WITHOUT-arm includes
  `deterministic-time.md` (the closest existing reference), so a win would mean
  marginal value over the strongest current guidance, not over nothing.
- Ablation with/without per section; isomorphic Go holdbacks; two hidden
  adversarial restraint probes; sonnet, n=1 per cell (directional, not effect
  size). All outputs graded by self-tested fixture oracles, every FAIL
  manually verified against the artifact before being trusted.

## Results

| Insight | Eval | Lang | Role | with | without | Verdict |
|---------|------|------|------|------|---------|---------|
| Statistical-oracle (cue-free) | E39 | python | dev | PASS | FAIL | **discriminates** |
| Statistical-oracle (cue-free) | E40 | go | holdback | PASS | FAIL* | weak discrimination |
| Design-for-testability | E41 | python | dev | PASS | PASS | ceiling (strong baseline) |
| Design-for-testability | E42 | go | holdback | PASS | PASS | ceiling (strong baseline) |
| Digest roundtrip | E44 | python | dev | PASS | PASS | ceiling |
| Digest roundtrip | E45 | go | holdback | PASS | FAIL | **discriminates** |
| Restraint: no security-bypass seam | E43 | python | adversarial | PASS | — | guard holds |
| Restraint: canonicalize before digest | E46 | python | adversarial | PASS | — | guard holds |

\* E40/without built a tie-only-tolerant exact oracle — a defensible reading of
the prompt's "near-ties may differ" wording. Shape disagreement, not clear
inferiority. The prompt should state the approximation degree explicitly.

## Findings

1. **Iteration 7's open question is resolved: the statistical-oracle section is
   now validated.** With cue-free prompts, the with-section Python run produced
   the taught shape (brute-force reference, recall ≥ 0.80 with stated headroom,
   exact scores on the overlap, seeded corpus) while the without-section run
   pinned gap-gated **exact set equality** against its reference — precisely the
   failure mode the section warns about. The iteration-7 "pass" of E35/E36 was
   indeed the prompt doing the teaching. E35/E36 stay `saturated_public`;
   E39/E40 are the discriminating pair now.

2. **Design-for-testability did not discriminate against the strongest
   baseline.** Both without-arms (deterministic-time.md only) added genuine
   seams: Python exposed a public `flush()` and injectable interval; Go built a
   full injectable clock + ticker. On these fixtures, existing guidance plus
   model priors already produce seam-in-the-SUT behavior. The section stays
   shipped (its guardrails content is what E43 validates — the restraint probe
   passed: clock injection, no env-var bypass of the rate limit), but its
   forced-transition teaching is **unproven marginal value**; both fixtures are
   marked `saturated_public`.

3. **Digest roundtrip: validated in Go, ceiling in Python.** The Go without-arm
   wrote handpicked single-key roundtrips plus a golden-bytes comparison — no
   whole-state load identity, no seeded breadth — while the with-arm hand-rolled
   a `canonicalDump` (sorted keys, every field incl. TTL) over seeded stores and
   asserted identity across both formats. In Python the existing snapshot
   guidance ("stable serialization, sorted keys") already carried the
   without-arm to a sorted canonical snapshot, so the dev fixture saturated.

4. **Four oracle calibration bugs, all false negatives punishing good work:**
   `.sort(key=...)` not recognized as a ranking (E39), `random.Random(seed)`
   via variable not recognized as seeded (E39), hand-rolled `canonicalDump` not
   recognized as a whole-state comparison (E45), and a public `flush()` seam
   not recognized because the keyword list expected `flush_now` (E41 — this one
   initially flipped the verdict from ceiling to discriminates; manual review
   caught it). Keyword oracles must encode behavioral shapes, not identifier
   spellings, and every FAIL must be read against the artifact before being
   believed.

## Net

- Statistical-oracle section: **validated** (Python clean, Go weak-positive).
- Digest-roundtrip section: **validated in the Go holdback**, saturated in Python.
- Design-for-testability: **shipped but unproven** against the strong baseline;
  its security guardrail is validated by E43.
- Both new sections' adversarial probes (E43, E46) pass and are enforced by the
  audit gate's section→probe mapping.
