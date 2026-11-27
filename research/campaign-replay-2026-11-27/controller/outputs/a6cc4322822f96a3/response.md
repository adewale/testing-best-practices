{
  "decision": "revise",
  "changes": [
    {
      "target": "Renderer/extractor production API and cache tests",
      "action": "Drop all five proposed exports and the cache-poisoning test.",
      "details": "Keep the helpers private. Use supported calls to exercise the cache and check the values callers receive. Leave eviction policy to the implementation."
    },
    {
      "target": "Public route test",
      "action": "Replace the exact tie-break assertion with checks for shortest distance and repeatability.",
      "details": "Use a unit-cost fixture with two two-edge paths from S to T and a three-edge detour. Assert that the returned path connects S to T using legal edges and has length two. Repeat the public call from fresh equivalent state and assert that it chooses the same path. Either two-edge path can satisfy the test."
    },
    {
      "target": "Public boundary/default regression and the production branch it exercises",
      "action": "Add the failing input to the public API tests and fix the decision that produces the wrong value.",
      "details": "Preserve the reported boundary input and any omitted argument. Assert the affected output field against the exact value from the independent reference. Include a neighboring input or explicit override with a distinct reference value to catch an unconditional default. Correct only the implicated comparison or default selection. If the mismatch reproduces solely on a mutant, the regression alone suffices."
    }
  ],
  "retained_contracts": [
    "Identical inputs yield a repeatable, valid shortest route, including when several routes tie.",
    "Public renderer/extractor values agree with the reference on ordinary, boundary and defaulted inputs, including after cache reuse or eviction."
  ],
  "validation": [
    "Run the boundary regression on the faulty version and record the expected and actual field values. Rerun the identical case and its neighboring control on the corrected version.",
    "Apply each supplied survivor separately in an isolated copy. Require the alternative stable shortest route to pass. For the eviction variant, drive eviction with distinguishable inputs through the public API, request an earlier input again and compare each returned value with the reference.",
    "Run the existing renderer/extractor suite and inspect the public API diff for accidental exports."
  ],
  "cost_and_stop": "Remove the proposed 90% target. Stop after the regression distinguishes the faulty and correct results, both permitted variants pass and the owner suite passes. The two supplied variants suffice for the focused checks.",
  "rationale": "The route survivor picks a different permitted answer. The eviction survivor changes internal state while preserving the specified values. Killing either would reward an implementation constraint. The boundary/default defect changes a result a caller can observe and an independent reference can judge."
}
