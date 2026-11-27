# Calibrate checkers before trusting their scores

A checker is part of the measurement instrument. Its passing self-tests, valid
JSON, or wrapper script do not establish that it distinguishes the promised
behavior. Use [the audit workflow](test-audit.md) for its owner and fixtures too.

## Test the actual route and decision

- Inspect the public command, case type and assertion dispatch. A direct helper
  may be intentionally excluded for trigger cases or used only historically.
  Exercise the same route that produces the claimed result.
- When sharing expensive preparation, retain a valid input and a representative
  rejected input through the full caller. Direct checker rejection plus a
  successful full run leaves a caller that discards rejection undetected. Check
  that the altered artifact reaches verification and its verdict reaches the
  caller; share only stages whose inputs remain unchanged.
- Give each independently scored criterion a credible incorrect input and a
  correct alternative. Check their individual scores, not just the overall
  verdict, which another criterion may mask. Reuse prepared fixtures when the
  expensive setup is unchanged.
- Wrong-decision controls should preserve convincing surface features: the right
  vocabulary with the opposite verdict, a missing required role, a result from a
  different run, or a skipped test with an impressive name. Keep their intended
  rejection reachable. A setup error is not evidence of the target check.
- Also accept allowed forms: paraphrases, identifier-only changes, supported
  encodings, legitimate ordering differences and properly labelled unavailable
  observations. Do not make stronger-looking checks into implementation locks.
- For executable tests, require proof of the effect the task promises. Importing
  SQLite or checking mock parameters does not prove the query ran correctly.
  Execute untrusted candidates only in an appropriate isolated harness; static
  inspection must state its limits. For prose a deterministic checker cannot
  reliably interpret, narrow its objective claim and use calibrated review.

## Preserve failures and missing evidence

Carry process status and phase through wrappers, pipelines and judges. Valid
output followed by a nonzero judge exit is a failed/provisional measurement,
not a transcript-backed final score. Keep diagnostics and uniquely identify each
run so another trial cannot overwrite its receipt.
Record artifact delivery separately from process or agent completion. Keep
interrupted work and incremental command/result receipts with their actual
budget and availability; do not regenerate missing observations.

Required tests/fixtures disappearing must not silently become a completed pass.
Optional/manual cases may remain skipped, but report their enrollment separately.
Distinguish observed failure, unavailable evidence and valid emptiness. Expected
verdict/availability comes from the fixture contract, not the detector's own
returned availability. Do not turn missing telemetry into a measured success.

## Compare like measurements

For a claimed model/skill improvement, record the case/input revision, scoring
definition, objective and qualitative components, availability/denominators,
grouping, ablation, and relevant runtime/version. Reject or explicitly separate
incompatible effective metrics before computing a gain. Identical judgments
scored under different policies can manufacture a statistically significant delta.
For shared dependencies, isolate writable caches and command links per trial.
A symlink into a shared installation still permits cross-trial writes unless
the runtime enforces read-only access; describe instructional isolation honestly.

Compatibility is about meaning, not identical script bytes. A checker repair or
refactor may preserve the metric; an unchanged script may select a different
metric through flags. Deliberate comparisons of graders are useful but measure
the instrument, not a model/skill effect.

A prompt changed from prose to structured JSON defines a different input
condition. Separate old answers that no longer meet the requested format from
incorrect decisions. Equivalent valid decisions in both formats can calibrate
the instruments; their score difference alone does not measure a model gain.

Keep frozen historical outputs and their declared labels. Regrading them creates
a separately labelled analysis; it does not rewrite what was originally recorded.
Check declared enrollment, repeats, per-arm totals, and score bounds against the
retained evidence. An unavailable historical preimage limits verification; a live
source fingerprint must not freeze future implementations to hide that limit.

## Verify improvement without building another campaign

Freeze tasks, controls, scope and stopping rules before model trials. Use a
no-guidance/current-guidance comparator where relevant and apply the same inputs,
budgets and measurements. Include useful work that must remain possible, not only
bad proposals to reject. On larger suites, report inventory, selected/actually
read sample and executed tiers rather than implying exhaustive discovery.

Prefer observed edits and behavioral controls over warning vocabulary alone.
An open audit can produce a valid repair outside a preselected finding. Apply
the same contract, fault, permitted-change and preservation requirements to
that repair, labelling new controls exploratory. A reference-specific adapter
cannot establish its quality or failure merely because it lacks that route.
Report incomplete runs, false alarms and lost proof as well as detected faults.
A saturated planning screen or a seen-case tie establishes no incremental
benefit. Small, known-case replays and same-family qualitative judging limit
generalization even when the new instrument's concrete code repairs pass.
