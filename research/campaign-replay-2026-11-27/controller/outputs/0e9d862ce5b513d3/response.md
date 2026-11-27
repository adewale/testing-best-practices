{
  "decision": "revise",
  "changes": [
    {
      "target": "Mutation workflow",
      "action": "Pause the nightly schedule and ship a manual calibration job.",
      "details": "Use one job on the intended CI runner. Pin the target to one existing route module exercised by the focused suite and commit its path as an allowlist. Use the existing mutation operators and exclusions. Limit the mutation step to 25 minutes and the job to 30 minutes, including setup and reporting. Disable automatic retries."
    },
    {
      "target": "Mutation results",
      "action": "Remove the proposed per-job floor of 60 and publish a report.",
      "details": "Record the revision, runner, target path, tool configuration, elapsed time, runner-minutes and per-mutant outcomes. Report the tool's score numerator and denominator for the completed sample. Mark a timeout, tool error or missing result as incomplete. Require the maintainer dispatching the run to identify who will review the results."
    },
    {
      "target": "Focused route tests",
      "action": "Keep the existing suite and run it before mutation.",
      "details": "Stop the pilot if the unmutated suite fails. Use a surviving mutant to justify a new assertion only when it exposes a specific route behavior the suite should protect."
    }
  ],
  "retained_contracts": [
    "The focused route tests keep their existing assertions, triggers and pass/fail behavior.",
    "Mutation enrollment stays within route code. The pilot score describes only the recorded sample and carries no merge requirement."
  ],
  "validation": [
    "Lint the workflow and inspect its resolved triggers, job count and timeouts. Confirm a nightly tick or pull request cannot launch the pilot.",
    "On the first owner-dispatched run, enumerate the selected mutants and check every source path against the committed allowlist. Compare the planned IDs with the final outcomes and check that each appears exactly once.",
    "Check that the report records the measured runner cost and that the score reconciles with the outcome counts. Exercise the timeout path with a shortened local limit and verify it records an incomplete run.",
    "Have the named reviewer inspect the survivors and record any actionable test gap alongside the run."
  ],
  "cost_and_stop": "Cap the pilot at 30 runner-minutes per dispatch. Stop at the cap and review partial results before spending more. Restore a schedule only after a separately budgeted run completes the full original route scope on the target runner within the 90-minute wall limit, and a named owner accepts the measured recurring cost and survivor triage.",
  "rationale": "Four perfectly balanced concurrent jobs could reduce the estimated route wall time to about 41 minutes. They would still consume about 165 runner-minutes before sharding overhead. Four inherited 90-minute limits would permit 360 runner-minutes per night. All-module cost is unknown, and a score of 60 on each shard has no measured baseline and would depend on how mutants were partitioned."
}
