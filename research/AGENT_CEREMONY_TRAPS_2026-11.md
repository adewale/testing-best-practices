# Agent-created verification traps in the owner's projects

Research date: 7 November 2026. Scope: the preceding year's project histories;
the strongest documented sequences below occurred June–November 2026.

## Evidence and limits

This is a longitudinal case study, not a controlled estimate of productivity.
Sources are commits, changed files, issues, PRs and project conversations.
Historical timings/counts below are attributed reports, not measurements rerun
for this research. Deletion size alone establishes neither safety nor value.
Original policies may have had owner approval; the evidence shows what agents
enforced and its consequences, not every original author's intention.

The private game remains repo A, as in the September corpus. Its private commits
were inspected; private URLs/source and conversation transcripts are not
republished. [Issue #30](https://github.com/adewale/testing-best-practices/issues/30)
provides public corroboration of the cross-project findings.

## 1. Repo A: evidence became a veto on the requested improvement

On 24 August, commit `b0e3c089cd0735c3c27a08d342a57c2372b2e0db` recorded
a built, validated rider improvement reverted because 144 alpha rows and a
continuity cell changed. A measured board discontinuity remained behind the
same seal; tested primitives were left unwired. Its design-history note said
nobody had played those changes.

On 26 August, `64a2d8b4a2bfd7fa13ab42a44a36a5ded5a2e61f` added a reseal
procedure requiring four written review sections. Its own investigation found
unused fixture fields and a fingerprint guard that threw during module import.
On 27 August, `476a6f73035155072e6890bc0c31503095e2421d` recorded the
owner's direction to change or remove an obstructing seal. Even the revised
plan put resealing ahead of the improvement. September's recovery later reported
removing about 117,000 lines of wave/verify/seal/rebind/prove tools, ledgers and
source-text tests while shipping the first journey.

**Lesson:** revisit the instrument before building procedures to satisfy it.
Old evidence can remain historical without vetoing owner-authorized behavior.

## 2. Agentic Mermaid: unrelated work repeatedly invalidated shared records

[Issue #304](https://github.com/adewale/agentic-mermaid/issues/304) reconstructs
six merges and a prospective seventh: 84 of 88 conflicts were generated/measured
files. One integration took 56 minutes to green CI, and later main changes
invalidated it again. Receipts hashed hundreds of source inputs even when images
were identical; exact payload ceilings and content-hashed package names added churn.
[PR #357](https://github.com/adewale/agentic-mermaid/pull/357) demonstrated a
behavior-neutral comment tripping 13 checks. [#361](https://github.com/adewale/agentic-mermaid/pull/361)
removed about 100,000 derived lines and 55 files protecting tests, tooling or prose.
[#370](https://github.com/adewale/agentic-mermaid/pull/370) removed golden approval
tokens while retaining snapshot tests and ordinary review.

**Lesson:** source identity is not behavior. Avoid shared derived records that
unrelated branches must regenerate; a larger regeneration command alone leaves
the underlying coupling intact.

## 3. Assurance repairs recreated the same trap

[Issue #355 and its closure](https://github.com/adewale/agentic-mermaid/issues/355)
report 26 failed/cancelled scheduled mutation runs, a repair grown to 41 jobs,
and five overlapping fault-injection mechanisms. The proposed successor added
diff scoping, selection, suppression and calibration. The eventual decision was
to remove mutation machinery and retain focused regression work.
September's #357/#361 retained a mandatory failing-base CI job; October's
[#592](https://github.com/adewale/agentic-mermaid/pull/592) removed it.
[good-pr #16](https://github.com/adewale/good-pr/issues/16) explains why preservation
tests can pass before and after refactors and rejects universal failing-base
gates and refactor opt-out labels.

**Lesson:** a useful authoring-time control does not automatically justify a
permanent job, exception protocol or another program maintaining that protocol.

## 4. Keyboardia: tests of evidence dominated failures and setup cost

[Issue #125](https://github.com/adewale/keyboardia/issues/125) attributes about
175 seconds, 32% of measured unit-test time, to repeatedly preparing expensive
tamper-test evidence. Timeouts increased through 15, 30 and 60 seconds; audit
tests reached 120 seconds. Verification-tooling files caused 12 of 23 examined
unit-job failures. The remedy reuses prepared inputs while executing each actual
rejection check and retaining one full end-to-end path.
[#130](https://github.com/adewale/keyboardia/pull/130), opened 18 October, retires
whole-app identity states and binds Stack B's historical packet to its original
revisions. Its [7 November comment](https://github.com/adewale/keyboardia/pull/130#issuecomment-6699584873)
records another pre-test failure: a changed merge base expired the harness
authorization. A [later comment](https://github.com/adewale/keyboardia/pull/130#issuecomment-6700989266)
records its renewal at `d4087f94`; expiry is a historical failure, not the current
blocker. It also corrects an earlier screenshot-race proposal: cancelling an
animation still produced two rasters, whereas awaiting its completion produced
one in 60 reported attempts. Those are the author's measurements, not reruns here.
This documents coupling, not permission to bypass owner approval or dismiss a
reproducible capture defect.

[#127](https://github.com/adewale/keyboardia/pull/127#issuecomment-6254800077),
open since 7 October, makes the product conflict explicit: the redesign removes
the very dropdown that whole-app identity states require. Its separate 2.25px
grid-offset regression is a real defect with a reported failing control. Retiring
obsolete identity states must preserve that check and reviewable visual evidence.

**Lesson:** separate historical approval from current behavior. Cache expensive
preparation, not verifier verdicts. Keep original artifact integrity intact.

## 5. Rayner: ordinary UI acquired generated-output bureaucracy

The owner's [good-pr #15](https://github.com/adewale/good-pr/issues/15) records
the request behind [Rayner #73](https://github.com/adewale/rayner/pull/73).
Useful UI evidence expanded into 30 files/about 2.2 MB of permutations, crops,
capture tooling, hashes, receipts and regeneration instructions. Two captioned
comparisons plus existing browser regressions and a negative control answered
the review question. Generated-output rules were applied because the ordinary
player HTML was built programmatically. Extra machinery was removed before merge.

**Lesson:** classify changed behavior and reviewer need, not build technology.
Stronger scientific/renderer/release evidence remains justified when it answers
a distinct question.

## 6. Bobbin: a stronger hypothetical guarantee delayed a concrete repair

[Draft #6](https://github.com/adewale/bobbin/pull/6), opened 30 August, proposed
leases, owner tokens and migration state for duplicate deliveries. October's
review found that queue metadata fencing did not fence actual writes or paid
external calls. [Replacement #10](https://github.com/adewale/bobbin/pull/10),
merged 13 October, made completion terminal and publication retry-safe at existing
database boundaries without a lease, heartbeat or migration. It permits running
overlap and requires evidence of material duplicate charges before exclusion
machinery. Four reported focused regressions fail on unchanged main and pass
with the repair.

**Lesson:** fix the demonstrated boundary before inventing exactly-once or
whole-rebuild guarantees.

## 7. PDA: copied facts and evidence with no consumer

[Commit a654175](https://github.com/adewale/pda/commit/a654175a67a570e411abf7a7d4ce430d910916f6)
removed about 4 MB of stale committed interop results, outbound vectors with no
consumer, duplicate CI scheduling and a dead test-count check. Inbound external
vectors remained. [#41](https://github.com/adewale/pda/pull/41) replaced doc pins
on test titles with stable references, selected runtime checks by changed inputs,
and cut contributor guidance by 69%, retaining relevant specialist security checks.

**Lesson:** follow consumers and command expansion; omit volatile copied facts.
Do not answer every renamed test by updating documentation and its checker.

## 8. Good PR: an archive verifier froze the next skill edit

[good-pr #18](https://github.com/adewale/good-pr/pull/18), open since 1 November,
fixes a verifier that required the current skill tree to equal the tree recorded
in an archived model run. A later prose edit therefore failed archive validation
even though neither the old outputs nor their source had changed. The repair
uses an explicit historical mode in the existing job, preserves exact recorded
source/artifact checks, and states that the archive does not evaluate today's skill.
Default verification still requires a matching current tree.

A one-off [implementation probe](../skill-development/evals/receipts/ceremony-study-2026-11-07.md#follow-up-real-archive-verification)
at frozen base `f517d6e7` and PR head `e80c8a31` confirms that distinction with
nine checks. The old command rejects an added prose comment; historical mode
accepts it while rejecting altered outputs, manifest, baseline and statistics.
The PR's twelve existing evidence-verifier unit tests also pass. This exercises
the existing repair; it does not show that the revised skill caused that repair
or improves model decisions.

**Lesson:** preserve the integrity of a past claim without requiring the product
to remain in its past state. Exactness can be correct while its scope is wrong.

## Implications for this skill

Our interpretation is a recurring sequence: precaution → permanent rule →
enforcement machinery → exceptions → machinery maintaining those exceptions.
This does not imply that all agent-authored safeguards are low-value.
The [September study](IMPLEMENTATION_LOCK_IN_2026-09.md) already traced direct
propagation of this skill into observed-output pins, source scans and count quotas.

The correction withdraws the rule that every lesson needs an enforcing check,
the implication that every removed assertion needs a replacement keeper,
auto-baselining in the test-type summary, snapshot field-count/cascade heuristics,
and blanket type-driven deletion. New targeted guidance is in
`testing-best-practices/references/verification-cost.md`; regression and
preservation evidence are distinguished. The desired outcome is a smaller path
to a useful, trustworthy product change, not more checks or a deletion quota.
