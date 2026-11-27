{
  "decision": "revise",
  "changes": [
    {
      "target": "Tamper fixture and oracle preparation",
      "action": "Build one valid specimen and a read-only fixture per distinct common input set.",
      "details": "Move expensive setup and independent reference generation into the fixture. For each mutation, identify the first oracle stage that reads the changed input. Reuse outputs whose inputs are unchanged and rerun the affected stage and its dependents. A digest of the original bytes can serve as an expected value. The checker must compute the observed digest from the case it receives."
    },
    {
      "target": "Negative-case runner",
      "action": "Give every existing and proposed variant its own named, parameterized case.",
      "details": "Apply one mutation to a private copy of the specimen and pass it to the production checker with fresh per-call state. Assert rejection and the expected rule when the checker exposes one. An unexpected exception or timeout fails the test. Keep an unmodified acceptance control and one uncached end-to-end tamper case to exercise the full wiring."
    },
    {
      "target": "Unit-suite configuration",
      "action": "Keep the current global timeout.",
      "details": "Measure the expanded matrix with shared preparation before merging it."
    }
  ],
  "retained_contracts": [
    "The unmodified specimen passes through the real verifier.",
    "Each bad variant receives a separate checker decision based on its mutated input, independent of execution order."
  ],
  "validation": [
    "During the change, run the uncached pipeline and the revised runner on the same control and every bad specimen. Compare acceptance, rejection and available rule identifiers case by case.",
    "Trace stage calls in the parameterized run. Verify one common preparation per fixture, a fresh checker call consuming each mutated specimen, and recomputation of each stage that depends on the mutation.",
    "Repeat the cases in reverse order and check that the shared specimen retains its original digest.",
    "Time five paired runs of the current and expanded suites on the same worker with the same concurrency. Record median elapsed seconds for the tamper group and the whole suite."
  ],
  "cost_and_stop": "Use the current tamper group's measured median seconds as the budget for the expanded matrix. Its reported 32% share provides the baseline context. If the matrix exceeds that budget or a verdict differs, hold the change and use stage timings or the failing case to locate the cause.",
  "rationale": "Common preparation contributes the same evidence to many cases. Sharing that work saves its repeated cost while each checker invocation still has to detect the fault in the specimen it actually reads."
}
