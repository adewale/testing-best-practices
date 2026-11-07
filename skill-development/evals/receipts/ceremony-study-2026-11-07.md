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
