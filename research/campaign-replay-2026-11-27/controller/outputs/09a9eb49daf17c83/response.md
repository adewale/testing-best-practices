{
  "decision": "revise",
  "changes": [
    {
      "target": "Renderer/extractor production API",
      "action": "Withdraw all five proposed helper exports and the cache-poisoning test.",
      "details": "Keep the helpers private. Classify the alternate shortest route as permitted and the eviction change as internal with no demonstrated effect on returned values. Drop the exact tie-break assertion and the proposed 90-point gate."
    },
    {
      "target": "Public route and extraction tests",
      "action": "Extend the existing public contract test to cover ties and repeatability.",
      "details": "Use a unit-cost graph with routes S-A-T, S-B-T and S-C-D-T. Accept either two-edge route. Compare the selected route across identical calls, including a fresh instance. Check extracted values against the independent reference on first and repeated calls. Exercise the cache only through ordinary API use."
    },
    {
      "target": "Public boundary/default regression and its production owner",
      "action": "Add the failing example first, then fix the branch that chooses the wrong value.",
      "details": "Call the public API with the smallest reported input that triggers the discrepancy. Record the independently verified expected value as a literal and assert the returned value. Include a neighboring valid case with a distinct expected result to catch an unconditional fallback. Correct the boundary/default selection at its source."
    }
  ],
  "retained_contracts": [
    "A route connects the requested endpoints using the minimum number of edges on the unit-cost fixture. Identical input yields a repeatable choice among tied shortest routes.",
    "Returned extraction values agree with the reference, including after a prior call.",
    "The affected boundary/default input returns its specified value."
  ],
  "validation": [
    "Run the focused boundary regression on the original implementation and capture the expected and actual values. Run that same test and its neighboring case after the fix and require both to pass.",
    "In isolated scratch copies, apply each supplied survivor separately. The alternative shortest route must pass the route assertions, and the eviction change must pass the public value assertions. As a defect control, returning S-C-D-T must fail the shortest-route assertion.",
    "Run the existing renderer/extractor owner suites on the clean fix and verify the public export diff contains none of the five helpers."
  ],
  "cost_and_stop": "Limit work to the public fixtures, the boundary fix and its owner suites. Stop once the real defect has red/green evidence and the two permitted changes pass their controls. Retire the score target without adding a recurring mutation job.",
  "rationale": "The tie changes a visible choice within the contract. The eviction survivor changes an implementation decision. Only the boundary/default discrepancy gives the caller a wrong value and warrants a production fix."
}
