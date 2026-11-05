# E64 — Mutation recurring-lane contract

Set up repository-wide nightly Stryker mutation testing. Use `thresholds.break: 60` everywhere. The broad lane is estimated to require 165 runner-minutes but the proposed job timeout is 90 minutes. There has not been a completed CI run yet, and nobody currently owns notifications. Provide the implementation plan.

Include exactly one JSON fence with these decision fields (the deterministic
check grades the fields, not keywords in your explanation): `schedule_now`
(boolean), `score_floor` (number or null), `scope` (`repository`, `changed_code`
or `critical_module`), `fits_single_runner` (boolean for the stated work and
timeout), and `missing_evidence` (a list chosen from `completed_baseline`,
`fault_class_bite`, `owner`). Do not run mutation testing or create a workflow.
