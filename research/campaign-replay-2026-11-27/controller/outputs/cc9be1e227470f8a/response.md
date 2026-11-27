{
  "decision": "revise",
  "changes": [
    {
      "target": "Renderer/extractor production API",
      "action": "Drop the five proposed exports.",
      "details": "Keep the helpers private and discard any wrappers introduced solely to reach them. Keep the existing route selection and cache eviction implementations."
    },
    {
      "target": "Proposed route and cache tests",
      "action": "Drop the exact tie-break assertion and the cache-poisoning test.",
      "details": "For a tied route, retain proof of the requested endpoints, legal steps and shortest length against an independent reference. Check repeatability by comparing routes returned by independent public calls on identical input. Either shortest route can satisfy these checks. Retain existing reference comparisons for ordinary public outputs."
    },
    {
      "target": "Existing public API regression suite",
      "action": "Add one boundary/default case before repairing the owner.",
      "details": "Use the smallest supported input that produces the known wrong result. Preserve the caller's argument form, including omission if that selects the default. Assert the returned value against a fixed expected value taken from the specification or independent reference. Extend the owner's existing table where available."
    },
    {
      "target": "Production owner of the incorrect boundary/default result",
      "action": "Correct the handling of the failing case.",
      "details": "Apply the documented boundary/default rule where the public result is determined. Preserve the semantics of neighboring valid inputs and explicitly supplied options."
    }
  ],
  "retained_contracts": [
    "A valid shortest route repeats for identical input, including when several shortest routes exist.",
    "Public renderer/extractor values agree with the independent reference on supported inputs.",
    "The failing boundary/default input returns its specified public value."
  ],
  "validation": [
    "Set owner_test to the changed public test file. Before the repair, run pnpm test \"$owner_test\" --maxWorkers=1 and verify that the new assertion reports the known wrong public value.",
    "After the repair, run time pnpm test \"$owner_test\" --maxWorkers=1. Run the relevant existing renderer/extractor sibling proof and verify reference agreement and tied-route validity, shortest length and repeatability.",
    "Inspect the export diff for the original API surface. Run git diff --check and preview the changed checks with node scripts/check-changed.mjs --dry-run -- <changed-paths> before running the focused checks."
  ],
  "cost_and_stop": "Budget one owner regression and the production fix. Record focused wall time and CI seconds when available. Stop after the intended red-to-green result and passing retained contracts. Record both survivors with their reasons, even if mutation efficacy stays below 90.",
  "rationale": "The alternate route meets the tie contract. The eviction change preserves public output, and poisoning private cache state supplies no supported caller sequence that exposes a failure. The boundary/default case has an independent expected value and detects an actual product defect."
}
