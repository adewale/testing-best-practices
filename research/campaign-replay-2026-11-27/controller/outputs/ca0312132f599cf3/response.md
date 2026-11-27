{
  "decision": "revise",
  "changes": [
    {
      "target": "Tamper test fixture",
      "action": "Prepare a known-good input once per fixture group.",
      "details": "Share the immutable output of the last stage common to the cases. Give each row a private copy of the candidate artifact and keep its trusted reference intact. If a row changes an input consumed earlier, branch before that stage and rerun the affected stages."
    },
    {
      "target": "Negative cases",
      "action": "Run a named table of variants through the real checker.",
      "details": "Keep every existing bad variant. Each row specifies one edit and the expected failed criterion from the verifier contract. Apply the edit, invoke the same checker used by the public pipeline on those bytes, and assert its fresh rejection at that criterion. Treat setup failures, crashes and timeouts as test errors. Add a proposed row when it exercises a distinct guard or a known regression."
    },
    {
      "target": "Pipeline wiring",
      "action": "Keep one full preparation-to-verdict test in required CI.",
      "details": "Start with a small, known-good raw input, use the public entry point with real preparation and oracle stages, and require acceptance. Keep the existing global timeout."
    }
  ],
  "retained_contracts": [
    "The public pipeline prepares and accepts a valid artifact.",
    "The checker accepts the untouched prepared control and rejects each independently modified artifact for its specified reason."
  ],
  "validation": [
    "Run the old and revised tests on the same verifier revision. Compare the collected case IDs and individual decisions, including the untouched control. Run rows in reverse order to check fixture isolation.",
    "In a scratch copy, bypass one covered rejection guard. Its named negative row must turn red because the tampered input passes. Restore the guard and confirm the row passes.",
    "Record preparation, full-pipeline and checker invocation counts. On comparable runners, measure focused and total unit-suite wall time before and after with the same cases, worker count and cache conditions."
  ],
  "cost_and_stop": "Budget one shared preparation per compatible group, one full wiring example, and one fresh checker decision per row. Use the reported 32% as the baseline share and compare absolute times as well. Stop when every required decision is preserved and the measured cost falls. If it does not, profile the remaining stage before adding cases or changing time limits.",
  "rationale": "Sharing preparation removes repeated work. Running the checker on each edited artifact preserves the evidence that a particular edit causes rejection. The full example catches drift between preparation and verification."
}
