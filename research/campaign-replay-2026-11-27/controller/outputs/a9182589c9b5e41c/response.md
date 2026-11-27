{
  "decision": "revise",
  "changes": [
    {
      "target": "Mutation workflow",
      "action": "Remove the nightly trigger and ship a manual diagnostic.",
      "details": "Replace the four-job, all-module matrix with one job on the intended runner. Select one fixed route-module slice exercised by the focused route suite. Cap the job at 30 minutes. Report mutant outcomes without a score floor. Keep tool failures and incomplete runs visible."
    },
    {
      "target": "Mutation report",
      "action": "Assign triage to a named route maintainer who accepts the pilot.",
      "details": "Record the commit, runner class, selected targets, elapsed time, and counts of killed, surviving, uncovered, and unfinished mutants. Link each actionable survivor to the routing behavior it changes and the test or issue that will address it."
    },
    {
      "target": "Focused route tests",
      "action": "Keep the existing suite in its current CI lane.",
      "details": "Add a case only for a demonstrated gap. For example, if a surviving change connects an edge to the wrong node, extend the existing renderer fixture with the expected endpoint from the input diagram."
    }
  ],
  "retained_contracts": [
    "The existing focused tests continue to check observable route behavior through the renderer.",
    "Maintainers can investigate which route defects those tests would miss on a pinned revision."
  ],
  "validation": [
    "Inspect the last nightly run's exit reason to distinguish a timeout from a setup or test failure.",
    "Run git diff --check and lint the workflow. Inspect its resolved triggers, job count, timeout, and mutation target list to verify manual-only execution over the selected route slice.",
    "After a maintainer accepts triage, run the focused suite on the clean revision and dispatch the slice once on the target runner. Reconcile the report against the selected mutants and verify that a known behavior-changing mutant is killed by the intended route assertion.",
    "For any new regression case, show it failing on the actionable mutant for the claimed route error and passing on restored source."
  ],
  "cost_and_stop": "Four perfectly balanced jobs could reduce elapsed mutation time to about 41 minutes each while still consuming an estimated 165 runner-minutes per night before setup overhead. Budget one job and at most 30 runner-minutes for the pilot. Stop on completion or timeout and record the outcome. With no result owner, leave it idle. Reconsider scheduling only after measuring the intended scope on the target runner, demonstrating actionable findings, and agreeing on a recurring budget.",
  "rationale": "Green route tests establish a control for mutation testing. They supply neither a mutation baseline nor a reason to enforce 60 in each shard. A completed pilot measures only its selected slice. Expanding enrollment and multiplying jobs now would commit recurring capacity before anyone has demonstrated how the results improve the renderer tests."
}
