# Issue 22 runtime repair — verification record (2026-10-02)

This is a narrow guidance change, not a new mutation-testing platform. Clarify
structural/semantic projection equality, witnesses for every cheaply proven
member, and the complete owner-derived residue. Add a runnable worked example
and execute it through the existing check-all.py command. Routing mentions cost
and decisive-layer checks so the conditional reference is reached.

## Observed evidence

| Experiment | Baseline | Revised | Scope |
|---|---:|---:|---|
| Frozen renderer rerun | 3/6 | 6/6 | Current main b5b81d3 vs this repair; tuning task |
| Untouched repository tasks | 10/12 | 11/12 | Pre-PRs 82c6ecc vs main plus repair; package comparison |

Exact models: gpt-5.6-sol and gpt-5.6-luna, low reasoning. Renderer: three
repetitions per model/arm; transfer: two repetitions on three tasks per arm.
Released skill-eval-harness 0.6.0, isolated read-only native Codex generation,
deterministic execution in non-root, network-disabled containers without host
mounts/auth. No qualitative model judge. All 36 model calls completed normally.

All six repaired renderer programs accepted both clean controls and rejected the
projection, dispatch and late-residue probes. Each clean execution used 102 calls
(3.57s at 35ms), below 120 calls/4.2s. Diagnostic matched outcomes: three revised
wins, no baseline wins, three shared passes. This is adaptive/tuning evidence;
current main itself varied from 0/6 previously to 3/6 here.

Transfer used untouched task definitions on actual source snapshots:

- adewale/yaket, 4e3bf4b12832fa04e26ac245400904bf2916c2a0: public option
  propagation (3/4 -> 4/4) and reviewed golden fixtures (4/4 -> 4/4).
- adewale/planet_cf, e1b9a1c3e2039aaf638e6d46372d86e2516be7ec: actual SQLite
  query behavior (3/4 -> 3/4), not a D1/Workers runtime claim.

Transfer has two revised wins, one baseline win and nine shared passes. The
remaining revised Luna file fails setup: its helper unpacks four fields from
three-field rows and never calls the SUT. Baseline failures invent a top-ranked
keyword and exact-match semantics for a substring search. Always-red files get
no full pass even though they reject faulty variants. No holdout output was
repaired/replaced, and the skill stayed byte-identical after the diagnostic.

## Interpretation and retention

Targeted renderer improvement is demonstrated. Broad improvement is **not**
established by this small transfer signal: only two repositories/two models,
explicit prompt constraints, no per-PR ablation or no-skill arm, and emitted test
files rather than an autonomous edit/run/fix workflow. Do not treat repeated
outputs or fault executions as independent domains. Holdouts become seen
regression material after this run, not fresh evidence for a future revision.

Retained locally in the working session's experiments/issue22-runtime and
experiments/real-repo-holdouts directories: frozen complete skill/source trees,
prompts, calibrated graders, all output/trace/metadata/environment files, runtime
outcomes, native benchmark imports/reports, cost ledgers and final artifact hashes.
These raw run trees are not included in the installable skill or this repository
record. A fresh checkout can run the maintained example guard, but does not by
itself independently reproduce the historical model outcomes.

The full local check-all.py suite, CI-scoped Ruff, install boundary, executable
example guard and git diff --check passed. A broad `ruff check .` also scanned
intentionally weak archived fixtures and found existing violations; the exact CI
Ruff scope passed, and unrelated fixture files were not changed.

PR preparation also verified regression sensitivity in disposable copies: the
guard passes the current example and fails when the reference is reverted to
main, public-path witnesses are removed, residue is reduced to the first context,
or structural equality is replaced with object identity. The reference and skill
used in the recorded model runs were not changed during PR preparation.

The generic skill-creator quick validator rejects the existing `compatibility`
frontmatter key on both unchanged merged main and this candidate. That inherited
validator/schema mismatch was not "fixed" by deleting supported project metadata;
the repository's install-boundary/static/harness gates pass.

Tokens and elapsed generation time are recorded, not USD. Across all 36 calls,
native total tokens were 3,092,192 including cached context replay. Holdout mean
total tokens fell 102,030 -> 98,229, while uncached input rose 25,279 -> 28,780;
neither is a cash-cost claim. Main was still b5b81d3 at the final remote check.
