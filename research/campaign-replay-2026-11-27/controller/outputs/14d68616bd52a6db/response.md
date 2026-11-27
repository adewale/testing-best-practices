{
  "decision": "revise",
  "changes": [
    {
      "target": "Existing 4,500 renders",
      "action": "Inventory and deduplicate",
      "details": "Record resolved styles, source bytes, format, seed, browser, assertions and original case IDs. Share one render across identical inputs and environment, carrying forward every distinct assertion. Preserve intentional repeatability checks. If all 360 repeats are surplus invocations, this alone leaves 4,140 renders."
    },
    {
      "target": "PR interaction suite",
      "action": "Replace the Cartesian loop with a deterministic constrained covering array",
      "details": "Model the actual style factors and supported levels, each output format, and fixed sources representing simple, mixed or nested, and boundary-complexity cases. Document infeasible combinations from renderer contracts. Start with mandatory rows, then add legal rows covering the most outstanding pairs until every feasible value pair across distinct factors occurs. Include reviewed defaults, boundaries and higher-order interactions identified from code or defect history."
    },
    {
      "target": "Fixed three-factor defect",
      "action": "Pin the reproducer as a named mandatory row",
      "details": "Preserve the exact three values together, triggering source, format and relevant environment. Through the public renderer, assert the specific formerly incorrect output against an independent expectation. Credit this row toward pair coverage and keep it through regeneration."
    },
    {
      "target": "Seeds and browser versions",
      "action": "Scope variation to its purpose",
      "details": "Pin fixtures, generator seed and browser for reproducible PR runs. Exercise documented browser-sensitive cases on affected supported versions. Use a bounded scheduled seed sweep for additional exploration when justified. Capture failing inputs, versions and seeds for replay and minimization."
    }
  ],
  "retained_contracts": [
    "Each keeper checks a caller-visible result against an independent expectation. For example, check where a style starts and ends in a nested fixture, and decode the selected format or compare a reviewed reference image to verify the effect survives serialization.",
    "Preserve each distinct historical failure oracle, required platform behavior and promised higher-order combination. Keep any old case whose sole obligation still lacks a keeper."
  ],
  "validation": [
    "At one pinned revision, run the old and candidate suites with matching fixtures and environment. Record baseline failures, compare shared outputs and map each retired case and assertion to a keeper or an explicit reason its combination can be dropped.",
    "Independently enumerate feasible pairs from the factor model and compare them with resolved inputs actually rendered. Require zero missing pairs, zero illegal rows and presence of every mandatory tuple. Report coverage by dimension and identify higher-order coverage relinquished.",
    "Replay the pinned triple on the pre-fix and fixed renderer. Require the original symptom and then the corrected output. Report unavailable historical proof. Challenge representative style, source and format keepers with owner mutations and investigate any fault only the old suite detects before deletion.",
    "Time each touched file with `pnpm test <file> --maxWorkers=1` and record actual render counts, wall time and CI seconds for both portfolios."
  ],
  "cost_and_stop": "Target fewer than 4,140 PR renders and lower measured CI cost. Remove optional rows that contribute no unique obligation. Stop when another removal would lose required coverage or an oracle. Retire old cases after preservation review and passing keeper checks. Report the final count and incremental cost if mandatory obligations exceed the target.",
  "rationale": "The old product covers style interactions only at one source complexity and format. New pairs exercise both neglected dimensions. Pairwise coverage alone can miss the known triple and other higher-order faults."
}
