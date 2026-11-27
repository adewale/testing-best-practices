# Test-quality PR synthesis — 2026-11-23

This review starts with the owner's PR history, including open and closed
attempts, rather than treating a testing guideline as evidence of success.
The accompanying [catalogue](test-quality-pr-audit-2026-11-23/catalogue.md) records the per-repository enumeration, included
PRs, exclusions, diffs, and limits of verification. A folded PR remains a
separate historical record, but is not an independent successful intervention.

## What changes in the installable skill

The new [test-audit workflow](../testing-best-practices/references/test-audit.md)
connects the existing Assess, Detect, and Upgrade guidance into a concrete
candidate-to-repair process. It provides candidate searches, a signal table with
retention exceptions, a retain/repair/consolidate/delete ledger, expected-value
provenance, keeper ownership, and old-versus-new checks against the same fault.
Its task brief can be used directly on another repository.
Write mode also asks for the contract, credible regression, missing proof, and
an honest production boundary before adding another test.

Markdown is the deliberate delivery format. A generic regex detector could
locate suspicious spellings but could not establish an independent contract,
realistic fixture, CI reachability, or safe deletion. The searches are labelled
as candidate collection. An automated rule should follow demonstrated recurring
findings and pass/fail calibration, rather than turning this corpus into a
blanket lint policy.

## Evidence-to-guidance map

| Evidence | Implication for the workflow |
|---|---|
| [`audit-skill` #11](https://github.com/adewale/audit-skill/pull/11), folded into [#10](https://github.com/adewale/audit-skill/pull/10): negated verdicts and checklist vocabulary satisfied old assertions; the new self-tests challenge individual manifest assertions through the real grader | Test each separately scored oracle with realistic correct and incorrect outputs; a script wrapping old keywords is not automatically stronger |
| [`anti-slop-writing` #20](https://github.com/adewale/anti-slop-writing/pull/20), incorporated in [#19](https://github.com/adewale/anti-slop-writing/pull/19): a promotion gate accepted a statistically significant decline | Use a known-bad control that contradicts the intended decision; passing routine inputs do not show that a gate can reject a regression |
| [`anti-slop-writing` #26](https://github.com/adewale/anti-slop-writing/pull/26): template-confounded proof was retracted | Distinguish instrument validation, historical claims, and measured product/model improvement |
| [`aha` #23](https://github.com/adewale/aha/pull/23), incorporated in [#22](https://github.com/adewale/aha/pull/22): append-only checks covered only a subset of tables; scanners had missing API/input forms; conformance prerequisites and corpora could silently disappear | Verify enrollment, input nonemptiness, intended guard reachability, and failure on missing required prerequisites |
| [`bobbin` #8](https://github.com/adewale/bobbin/pull/8), folded into [#7](https://github.com/adewale/bobbin/pull/7): CSS text recognition was replaced by browser geometry with fixture preconditions | Execute the behavior through its real owner and verify the fixture reaches the condition before asserting the result |
| [`audit-skill` #17](https://github.com/adewale/audit-skill/pull/17): unavailable Git-linked fixtures replaced with generated repository states | Check a fresh checkout can obtain fixtures; verify generated states and label non-reproducible historical outputs honestly |
| [`flux-search` #17](https://github.com/adewale/flux-search/pull/17) serialized CI workers and raised timeouts around a shared deployment; [#26](https://github.com/adewale/flux-search/pull/26) later removed the default production dependency and CI-specific worker limit | Preserve the history of attempted fixes without adopting every merged workaround as best practice; repair the boundary and completion conditions rather than assuming one green run proves lower flakiness |
| [`testing-best-practices` #28](https://github.com/adewale/testing-best-practices/pull/28) removed a golden verifier's self-approval path; open [#40](https://github.com/adewale/testing-best-practices/pull/40) retained adverse early results and a later tie on seen cases | Check both directions: real defects must fail and allowed changes must pass. Preserve independent byte/order/integrity contracts, and do not treat a seen-case tie as incremental model uplift |
| [`pythonbyexample` #6](https://github.com/adewale/pythonbyexample/pull/6) compared 105 programs with fresh output from the same interpreter; [#44](https://github.com/adewale/pythonbyexample/pull/44) later compared two runtimes | Record expected-value provenance. Repeatability is useful evidence for its own claim; independent correctness and cross-runtime agreement are different claims |
| [`skill-eval-harness` #102](https://github.com/adewale/skill-eval-harness/pull/102): two independently replayed faults survived the original focused tests and failed the replacements; the grading test landed through [#97](https://github.com/adewale/skill-eval-harness/pull/97), while the separate telemetry test did not | Run the same credible fault against old and replacement tests. Keep the observed sensitivity result separate from whether that replacement shipped |

These are selected examples, not the full PR list. The catalogue is the coverage
record. Hosted CI evidence, direct source/fixture inspection, author-reported
measurements, and unrun experiments are distinguished in its per-repo reports.

## OpenClaw comparison

Read at OpenClaw commit
[`314ae9ae90778c162add205c015566f07263987a`](https://github.com/openclaw/openclaw/commit/314ae9ae90778c162add205c015566f07263987a):

- [Test Audit skill](https://github.com/openclaw/openclaw/blob/314ae9ae90778c162add205c015566f07263987a/.agents/skills/test-audit/SKILL.md)
- [Candidate evidence and audit workflow](https://github.com/openclaw/openclaw/blob/314ae9ae90778c162add205c015566f07263987a/.agents/skills/test-audit/references/audit.md)
- [Subsystem campaign](https://github.com/openclaw/openclaw/blob/314ae9ae90778c162add205c015566f07263987a/.agents/skills/test-audit/CAMPAIGN.md)

| OpenClaw idea | Decision here |
|---|---|
| New-test gate asks for behavior, credible regression, existing proof, and test-only seams | Adopt as questions for each candidate and its proposed replacement |
| One primary owner for a contract, with additional layers justified by different risks | Adopt keeper ownership; preserve distinct transport/lifecycle/security/persistence contracts |
| Explicit retention of independent public/static/platform/release contracts | Adopt retention exceptions; source text, slowness, or mocks alone do not justify deletion |
| Candidate evidence includes owners, callers, history, CI routing, and remaining proof | Adopt before edits; uncertainty does not become cleanup permission |
| Campaign ledger uses retain/fix/consolidate/delete marks, followed by preservation review | Adopt the decisions, ledger template, and coverage-preservation review; expand to full per-test enumeration only when a broad removal needs it |
| Campaign checks restored contracts with deliberate production faults | Extend using this project's pilot: run old and keeper tests against the same fault to expose lost checks |
| OpenClaw-specific commands, line budgets, maintainer tooling and landing policy | Keep repository-specific; do not transplant them into a general skill |

The project's own [three-repo pilot](TEST_AUDIT_PILOT_2026-10.md) is an important
counterweight to a heavyweight campaign. It found candidate searches plus
context sufficient for its acted-on findings, documented the cost of full
ledgers and redundant reviewers, and recommended old-versus-new fault checks.
The new workflow keeps a bounded baseline and candidate ledger, then expands
when preservation risk warrants it. It does not require a full per-test ledger,
fixed reviewer count, deletion target, mutation-score target, or recurring lane.

## Limits

Historical diffs establish what a PR attempted. CI success establishes only
what the identified job ran at its identified revision. Neither establishes
that a heuristic generalizes, that an author-reported mutation result was
independently reproduced, or that the revised skill improves model behavior.
The initial workflow addition had no new model benchmark. A subsequent
[nine-scenario decision replay](campaign-replay-2026-11-26/README.md) on
2026-11-26 observed 9/9 passes for PR #41, the pre-PR skill and no skill alike.
It establishes appropriate decisions on those supplied reconstructions, with
no observed incremental benefit and no claim of reliable campaign prevention.
Private-repository evidence is retained locally and excluded from the public
PR's source reports.
