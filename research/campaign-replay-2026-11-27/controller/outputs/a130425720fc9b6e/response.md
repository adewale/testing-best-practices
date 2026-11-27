{
  "decision": "revise",
  "changes": [
    {
      "target": "360 repeated renders",
      "action": "Identify equivalent invocations before deduplicating.",
      "details": "Group by effective style, source contents, format, seed, browser build and setup. Compare assertions and baselines within each group. Run one render for equivalent cases and keep every distinct assertion. Preserve repetitions with an order-dependence or determinism contract. Removing 360 redundant invocations would leave 4,140."
    },
    {
      "target": "Blocking renderer suite",
      "action": "Replace the style product with a deterministic constrained pairwise suite.",
      "details": "Model each style factor, representative minimal, typical and dense source fixtures, and each supported output format. Document legal levels and constraints. Pin the browser and seed. Start with mandatory cases, then select legal rows covering the most missing pairs until every feasible pair of values from different factors has a witness. Check the rendered content with an oracle appropriate to its format."
    },
    {
      "target": "Known three-factor regression",
      "action": "Keep the original reproducer as a mandatory blocking case.",
      "details": "Pin all three triggering values together, the triggering source, relevant environment and the assertion for the original visible defect. Give this case a stable ID and include it in the coverage count."
    },
    {
      "target": "Browser and seed variation",
      "action": "Run a bounded nightly sample.",
      "details": "Choose up to 12 fixtures spanning formats, complexity and historically fragile styles. Run each on two supported browser builds with four recorded seeds. Rotate builds and seeds across nights, record replay inputs, and promote a reproducible failure to a directed regression."
    }
  ],
  "retained_contracts": [
    "Keep existing contractual goldens, tolerances, boundary cases and required higher-order combinations as mandatory witnesses.",
    "Preserve each supported format’s output assertions and each distinct historical defect oracle."
  ],
  "validation": [
    "Export an old-case inventory mapping each proposed deletion to its duplicate or to replacement witnesses for its stated obligations. Review any unique golden or behavior lacking a witness.",
    "Independently enumerate feasible pairs from legal assignments. Subtract pairs observed in actual render invocations. Require zero missing pairs and report counts by factor pair, including style by complexity, style by format and complexity by format. Check the exclusions against renderer support.",
    "Verify that one invocation exercises the entire regression triple. Run its assertion on the pre-fix and fixed revisions and require failure on the original symptom followed by a pass.",
    "Shadow both suites on the same revisions and CI image. Compare shared outputs under existing tolerances, independently review new expected outputs and replay historical failures. Investigate every legacy-only failure and retain its witness until resolved."
  ],
  "cost_and_stop": "Target at most 450 blocking renders and 96 per nightly sample. Measure actual invocations, runner time and p95 wall time against the 4,500-render baseline. Retire old cases only after the coverage, oracle and failure-replay checks pass. If mandatory coverage exceeds the budget, report the measured overrun and keep the affected cases pending a budget decision.",
  "rationale": "The old product exercises style interactions at one complexity and format. Multiplying it by browsers and seeds spends more renders at that same point. Pairwise selection makes cross-factor coverage measurable. The directed triple preserves a failure pair coverage alone can miss."
}
