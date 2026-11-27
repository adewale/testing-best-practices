{
  "decision": "revise",
  "changes": [
    {
      "target": "Public boundary/default regression",
      "action": "Add a failing public API test",
      "details": "Call the affected entry point with the reported failing input and assert the specific incorrect output field against the known reference value for that fixture. Add one control case. If omission triggers the failure, pass the documented default explicitly. If an endpoint triggers it, use the nearest supported input on the working side."
    },
    {
      "target": "Production boundary/default handling",
      "action": "Correct the decision that produces the wrong value",
      "details": "Trace that public call to the branch that selects the boundary result or resolves the default. Change that decision so the failing input produces its specified value. Keep all five helpers private and leave route selection and cache eviction intact."
    },
    {
      "target": "Route tie test",
      "action": "Assert shortest length, validity and repeatability",
      "details": "Use a public fixture with two equal shortest routes of known length. Check the endpoints, every step and the length. Repeat the identical query and compare its route with the first result. Reuse existing coverage if it already checks these properties."
    },
    {
      "target": "Cache test and mutation report",
      "action": "Drop the cache-poisoning test and record the two survivors",
      "details": "Keep cache state private. Record which allowed route the route mutant selects and how the eviction mutant changes internal state while preserving public values. Report the measured mutation score alongside those dispositions."
    }
  ],
  "retained_contracts": [
    "For identical inputs, either shortest valid route is acceptable if the choice is repeatable.",
    "The public API defines boundary/default values. Cache eviction order and private helpers are implementation details."
  ],
  "validation": [
    "Run the boundary/default regression against the original implementation and confirm the failure is the expected public value mismatch. Apply the fix and check both the reproducer and its control.",
    "Run the route checks against the original and alternate-route implementations. Each must return a valid shortest route consistently.",
    "Run the affected renderer/extractor suite. Check public values against the reference with the eviction mutation applied, and verify that the public exports match their pre-change set."
  ],
  "cost_and_stop": "Limit the patch to the observable defect, its public regression and any missing route-contract assertion. Rerun the affected mutation scope once. Stop when the regression passes, the affected suite is green and both survivors are accounted for, even if the score is below 90.",
  "rationale": "The boundary/default fix corrects a result callers can observe. Killing either survivor by pinning an allowed choice would turn an implementation detail into a compatibility constraint."
}
