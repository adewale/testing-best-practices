# Verification-ceremony study — 7 November 2026

## Question and result

Does the added guidance improve judgment about costly verification, including
older open PRs, without encouraging deletion of useful safeguards or imposing
new evidence rituals?

The initial six-plan comparison is saturated: the frozen #40 skill and the first
revision each pass 12/12 individual decisions across two batches. Their eight
paired PR reviews with supplied facts are all ties. This does not demonstrate
incremental model uplift.

An exploratory source-only pass exposed a regression in the first revision:
one answer treated missing production context as a new release prerequisite,
and another prioritized a possible readability issue over a concrete publication
omission. The blind reviewer preferred the baseline in two pairs and tied two.
That failure prompted a narrow correction: missing context is a question, not
proof of waste or a new release condition; supported product defects come first.
The final retest is a regression check on now-seen cases, not a fresh holdout.

The final candidate passes all six plan controls. A new blind review of its
four source-only answers against the retained baseline scores both sides 4/4
on every case, with four ties. The known overreach is corrected; this still
does not establish incremental uplift over the baseline.

## Protocol

- Baseline: complete skill tree at `1f2250ac7b690c843f62e07549f8e88ae224a6f6`,
  the original PR #40 head, rather than no skill or the much older shipped skill.
- Treatment: that tree plus the new guidance and consistency corrections. Both
  the first revision and final correction have frozen file identities in the
  [study record](ceremony-study-2026-11-07.json).
- Backend: the existing `run-prompt-evals.py` documented sub-agent candidate path,
  with fresh `fork_turns=none`, inherited session model/effort and no override.
  The native Codex CLI could not initialize its read-only installation state.
  The collaboration backend does not expose an immutable model build ID;
  token, latency and monetary telemetry were not available and are not invented.
- Each candidate could read only its frozen skill tree and specified input
  files. No parent conversation, research document, answer key, sibling output,
  external browsing or target-project execution was permitted.
- Primary phase: two candidate batches per arm, each answering six synthetic
  scenarios plus four real PR excerpts with supplied contextual facts. The
  second batch reverses order. Inputs and initial guidance were frozen before
  scoring. Cases in a batch share context; they are not independent trials.
- E80's data-only oracle checks six explicit retire/retain/introduction decisions
  and requires nonempty rationale/validation fields. It does not verify prose,
  executed cleanup, productivity, or production correctness. Combining the six
  saved JSON answers into its array is lossless format adaptation.
- PR answers were reviewed in eight randomized left/right pairs by a fresh
  reviewer given the same inputs, without arm names, skills or answer key.
  Scores use 0–4 for supported findings, proportionate action, retained distinct
  contracts and evidence honesty; preference requires a material difference.
- After saturation, a second pair of fresh candidates reviewed the same PR
  patches with the supplied diagnosis/cost facts removed. A separate blind
  reviewer assessed four pairs. This phase was exploratory, not preregistered.
- The first revision's failures were inspected and its reference corrected.
  A fresh final candidate repeated the source-only reviews and six plans. No
  claim of untouched holdout performance is made after that correction.

This is one inherited model configuration, not a model panel. It does not test
autonomous skill triggering, complete repository exploration, actual project
edits, deployed outcomes or changes in review time. The supplied-facts phase
tests judgment given evidence, not independent discovery of buried problems.

## Six plan controls

| Case | Required distinction | Baseline | First revision |
|---|---|---:|---:|
| S1 | Retire obsolete alpha gate/reseal tool; keep historical capture, contact checks and font integrity | 2/2 | 2/2 |
| S2 | Retire failed redundant mutation machinery; keep focused product regression and release security | 2/2 | 2/2 |
| S3 | Keep useful UI comparisons/browser tests; remove unnecessary matrix/receipt/regenerator | 2/2 | 2/2 |
| S4 | Reuse setup; invoke the real checker per variant and retain accepted-PCM recomputation | 2/2 | 2/2 |
| S5 | Retire universal failing-base/opt-out/test-roster rules; retain preservation and bug regressions | 2/2 | 2/2 |
| S6 | Keep legitimate release signature/checksum, tenant regression and browser wiring | 2/2 | 2/2 |

The fixture's positive sample passes. Its three negative samples fail for an
extra permanent approval gate, removal of byte integrity, and keyword-only
output respectively. These controls calibrate a bounded plan checker, not an
independent behavioral oracle. E80 remains `demo`, noncritical and saturated;
its shared assertions are soft. No discrimination claim is registered.

## Older open PR application

All four were open and created before 4 November when selected. Source identities
and the exact selected patches are retained in the study record. Age was a
selection criterion, never evidence that a PR should be abandoned.

| PR / created | Frozen head | What the evidence supports |
|---|---|---|
| [Bobbin #11](https://github.com/adewale/bobbin/pull/11), 12 October | `705f3dee9d493393b3fc1b71c5766772e6560993` | With the supplied replay/cost facts, distinguish 207 candidate-audit rows from zero visible fused topics, and ask about actual production need before a blanket campaign. With only source, retain the real migrated-database cleanup regression and flag prevalence/cost as unknown; missing context alone is not a new deployment gate. |
| [Rayner #36](https://github.com/adewale/rayner/pull/36), 27 October | `3edb3dc3fb1c41a77d8a35b033bb5f2b49273b2c` | Passing encoder/VTT tests do not establish readable captions. Separately, the exporter writes a transcript while the changed publication loop copies MP4/VTT only; inspect the consumer and any alternate publication route. Keep actual media, serving and preservation checks. |
| [Agentic Mermaid #374](https://github.com/adewale/agentic-mermaid/pull/374), 2 October | `2ed20a17e3234f77bb82f15d1291638c6f5fff6e` | The actual browser sandbox, inert SVG, text rendering, CSP and fallback contracts are useful. The authored host harness leaves actual host interoperability unverified; it does not justify deleting security tests or constructing a new matrix. |
| [Skill Eval Harness #96](https://github.com/adewale/skill-eval-harness/pull/96), 26 September | `c4a5831e691f3d4d3425977c3371dcadf41ac9d4` | Keep exact historical protocol provenance and concrete loader/import-boundary checks. Whole-module identity is conservative; the excerpts alone do not prove that comparison policy causes unnecessary paid reruns. Inspect omitted closure tests and comparison consumers before declaring it a bug. |

In the supplied-facts phase, both arms average 3.75/4 over eight reviews. All
preferences tie; the harness-identity answers receive minor calibration
deductions for overstating the unshown paid-rerun obligation.

In the source-only first-revision pass, baseline scores are 4/4/4/4 and treatment
scores 2/3/4/4. The lower scores are retained rather than discarded. The treatment
did identify the caption-timing limitation, but missed the transcript publication
gap that the baseline found. More attention to process cost is not automatically
better product review.

## Retention, cost and validation

The JSON record retains inputs, selected source patches, exact candidate answers,
blind judgments/mappings and skill snapshots. It is a one-time research record,
not a source pin, cleanup receipt requirement or scheduled gate for other repos.
No source PR was modified or merged by the study.

The entrypoint grows from 25,603 to 26,966 characters (+1,363, about 5.3%) and
from 274 to 292 lines. The topical reference loads only on its trigger. This is
character/line overhead, not measured model tokens or runtime cost; a performance
benefit must not be inferred from it.

All commands in the existing deterministic gate passed locally across the gate
run and its continuation. Initial environment failures were an unrelated GNU Go
binary named `go` and a read-only home cache. A task-local official Go 1.27.3
archive was checksum-verified; the remaining commands ran with a writable task
`GOCACHE`. Successful fixture checks were not repeated just to restart the wrapper.
Ruff 0.16.0, install-boundary and whitespace checks pass. No workflow or schedule
was added. The existing fixture runner now includes E80's bounded controls.

Re-score retained plan outputs without calling a model:

```sh
python3 - <<'PY'
import json, subprocess, tempfile
from pathlib import Path
record = json.loads(Path('skill-development/evals/receipts/ceremony-study-2026-11-07.json').read_text())
oracle = Path('skill-development/evals/fixtures/e80-ceremony-decisions/oracle.py').resolve()
for trial, answers in record['candidate_answers'].items():
    plans = [answers[f'S{i}'] for i in range(1, 7) if f'S{i}' in answers]
    if len(plans) != 6:
        continue
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / 'answers.json').write_text(json.dumps(plans))
        subprocess.run(['python3', str(oracle), tmp], check=True)
    print(trial, 'six-plan pass')
PY
```

The retained PR answers and blind judgments can be independently re-read. New
generations require a usable model backend and should retain both variants,
exact configuration and comparable inputs; they are not necessary to replay
the saved plan verdicts.

## Follow-up: real archive verification

The skill is held fixed at `22b2b24fb53b701b098c3fe483fb5e3d513e3859` for
this follow-up. No additional guidance was tuned. A fresh CLI smoke test got
past installation-state initialization but could not reach the model: the
environment proxy rejected `chatgpt.com/backend-api/codex/responses` with HTTP
403. That destination is absent from the enforced allowlist; no environment
network-change tool is available. No candidate was generated, and there is no
new model comparison or harder-case model score to report.

Instead, a bounded implementation probe exercises an existing repair from
[good-pr #18](https://github.com/adewale/good-pr/pull/18), open since 1 November.
It tests a concrete recommendation in the fixed guidance: separate historical
evidence from claims about the current skill, preserving actual archive integrity.
The commands and expected outcomes were frozen before the probe ran. The
[follow-up record](ceremony-follow-up-2026-11-07.json) retains that protocol,
the runner text, exact commands, outputs, mutations and source excerpts.

Base: `f517d6e7f264a4e85c310d18ca57017ab889250c`.
Candidate: `e80c8a31b2519912d839a6ae6cf6b0eab974a3d6`.
Both are temporary local checkouts of good-pr; the source PR was not changed.

| Actual command/input | Expected result | Observed |
|---|---|---|
| Base `verify`, clean tree | Accept intact archive | Pass; 81 saved outputs regraded |
| Base `verify`, later prose comment in the skill | Reject due to current-skill coupling | Rejects uncommitted skill changes |
| Candidate default `verify` | Retain strict current-skill requirement | Rejects changed current skill tree |
| Candidate `verify --historical` | Accept intact archive; identify historical scope | Pass with explicit current-skill disclaimer |
| Historical mode, later prose comment | Accept unchanged archive | Pass with the same disclaimer |
| Historical mode, newline appended to saved outputs | Reject altered archive bytes | Rejects output hash mismatch |
| Historical mode, newline appended to manifest | Reject altered protocol bytes | Rejects manifest hash mismatch |
| Historical mode, newline appended to frozen baseline | Reject altered baseline bytes | Rejects baseline content hash mismatch |
| Historical mode, aggregate rate replaced with `-1` | Reject forged statistics | Rejects noncanonical aggregate |

All nine expectations pass. Every mutation is restored in `finally`; both
checkouts are clean afterward. The candidate's existing evidence-verifier
unit module also passes all twelve tests:

```sh
python3 -m unittest discover -s tests -p test_eval_evidence.py
python3 scripts/build_eval_evidence.py verify --historical evals/results/visual-evidence-gpt-5.4.json
```

This is execution evidence for the repair already present in #18. It is not an
agent-authored cleanup from this study, a current model run, an independent
attestation of archived execution source, or evidence of incremental skill uplift.
The probe is a one-off research exercise, not a registered fixture or new CI job.

### Additional older-PR findings

These are manual applications of the fixed guidance, not scored model answers.
Frozen PR bodies, the relevant discussion and selected source patches are in
the follow-up record. Reported browser/product results were not rerun here.

| PR / frozen head | Supported distinction and useful next action |
|---|---|
| [Keyboardia #127](https://github.com/adewale/keyboardia/pull/127), open since 7 October; `88941adda4411569377cd28215504ffd4af896f2` | Its body and discussion identify whole-app identity states waiting for a deliberately removed dropdown. Retarget or retire that obsolete requirement through the authorized harness change; preserve current visual review and the separate grid-offset regression. The stated spec/implementation gaps remain real product work. |
| [Keyboardia #130](https://github.com/adewale/keyboardia/pull/130), open since 18 October; `d4087f9415660d1c181f39e8aa50981c9ec01ebc` | The patch retires whole-app identity states while keeping component identity, hashes, historical receipt inventories and recorded ancestry. The newer discussion renews the expired authority and corrects a proposed capture fix using reported experiments. Do not describe the old expiry as today's blocker or delete checks merely because capture synchronization needed repair. |
| [Good PR #18](https://github.com/adewale/good-pr/pull/18), open since 1 November; `e80c8a31b2519912d839a6ae6cf6b0eab974a3d6` | The historical-mode repair has direct allowed-change and corruption evidence above. Preserve strict matching for new current-skill claims; use historical verification for an unchanged past run. An archive disclaimer is necessary to avoid silently upgrading its scope. |
| [Keyboardia #87](https://github.com/adewale/keyboardia/pull/87), open since 2 August; `fbcd2685864e98859dba19b1e0ebecbabdc3ed1d` | Its body reports actual conflicts with #127 and unfinished authoring/renderer acceptance work. Age, file count and many passing lanes do not establish useless ceremony. Review a bounded authoring unit against the chosen dock and preserve the distinct renderer acceptance requirements. This finding uses the body only, not a full code review. |

The follow-up strengthens the research's concrete mechanism and counterexamples.
The earlier saturated comparison remains the only generation evidence for this
guidance. A claim that it improves autonomous decisions still needs a fresh,
usable model backend and harder tasks without the supplied diagnosis.
