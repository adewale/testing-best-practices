{
  "decision": "revise",
  "changes": [
    {
      "target": "Verifier fixture preparation",
      "action": "Prepare one valid specimen per distinct input and oracle configuration.",
      "details": "In suite setup, run the real preparation once and retain its pristine output. Identify which inputs each expensive oracle stage reads. Share a stage’s output only across rows with identical inputs to that stage. When a mutation affects an upstream input, rerun the affected stage and its dependents. Keep each row’s working copy and scratch state private."
    },
    {
      "target": "Tamper cases",
      "action": "Use a table of named mutations at the production checker boundary.",
      "details": "Submit an untouched copy and require acceptance. For every existing bad variant, change one property on a fresh copy and invoke the real checker on those bytes. Require an explicit rejection for that row and check the intended public reason where available. Keep expected outcomes independent of the oracle. Add a row only when it catches a named regression the existing rows miss."
    },
    {
      "target": "End-to-end coverage and timeout",
      "action": "Keep a from-scratch success and a representative tamper through the complete pipeline.",
      "details": "Choose a tamper that would escape if the pipeline handed the checker the original specimen. Retain additional complete runs only for distinct integration risks, including mutations that invalidate the full preparation. Keep the current global timeout."
    }
  ],
  "retained_contracts": [
    "A valid specimen produced by the real pipeline is accepted.",
    "The real checker independently rejects every listed tamper, including later rows after an earlier rejection.",
    "The full pipeline passes the submitted specimen to verification and propagates its verdict."
  ],
  "validation": [
    "Compare named outcomes on the original and revised suites for every existing row. Restore the original value in a negative row as a one-off control and confirm its rejection assertion fails because the checker accepts it.",
    "Run `pnpm test <verifier-test-file> --maxWorkers=1` on each revision under the same conditions. Record preparation and full-oracle run counts, checker invocations, file wall time, and CI seconds when available.",
    "Run the verifier’s existing integration siblings and `git diff --check`. Use comparable unit CI runs to remeasure the reported 32% share alongside absolute time."
  ],
  "cost_and_stop": "For N downstream tamper rows sharing one baseline, budget one preparation and N fresh checker verdicts, plus the clean control and retained integration runs. Stop once all named outcomes agree, the integration controls pass, and measured time falls at the existing timeout. If checking itself dominates, profile that stage before expanding the matrix.",
  "rationale": "Preparation can serve multiple cases when its inputs match. Each rejection is evidence about the particular changed specimen only when the checker receives and evaluates that specimen."
}
