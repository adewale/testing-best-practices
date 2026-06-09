# Eval Health and Obsolescence Plan

This file applies the lesson from Lun Wang, “Your Evals Will Break and You Won't See It Coming” (2026-05-17): static eval suites become brittle when model behavior, tool use, or failure modes shift qualitatively. The eval suite must measure its own continued usefulness.

## What can break
- **Score saturation**: most models score 4, but real testing mistakes still escape.
- **Proxy gaming**: agents learn to mention rubric phrases without changing tests meaningfully.
- **Capability shift**: newer agents use tools/subagents/fixtures in ways the old evals do not inspect.
- **Correlation drift**: static checks improve while runtime bug-kill or human review gets worse.
- **Stale framework assumptions**: pytest/Vitest/Playwright/Go/Rust APIs and idioms change.
- **Distribution drift**: eval fixtures no longer resemble real repositories using the skill.

## Meta-signals to track in `evals/scorecard.md`
- Static score vs runtime score correlation.
- Critical eval pass rate over time.
- Number of evals scoring 4/4; if >80%, add harder/hidden variants.
- Escaped real-world failures: map each to an existing eval or create a new one.
- Framework freshness date for Python, Go, TypeScript, and Rust references.
- Judge disagreement rate if multiple reviewers score prompt outputs.

## Living-eval policy
- Keep a **stable core** for regression comparison.
- Add **rotating probes** quarterly or after a major model/tool change.
- Maintain **hidden variants** of critical evals so agents cannot pass by keywording public prompts.
- For every major real-world miss, add or update an eval within the same week.
- Prefer evals that combine static checks, runtime fixtures, and rubric judgment; do not rely on one layer.

## Current shared-harness saturation response
- `neg-no-red-claim` was saturated in the 2026-06-08 baseline smoke run (`with_skill=1.0`, `without_skill=1.0`) because the objective accepted the prompt-leaked keyword `red`.
- The shared smoke case now probes green-only evidence: it requires red-vs-green evidence separation, an observed passing command/result, a concrete next step for proving the missing pre-fix failure, and a guard against unqualified completed-TDD claims.
- If this case saturates again, add a hidden or rotating variant with a saved green log and no public wording that names the missing red phase.

## Core language coverage requirement
The eval validator enforces at least two evals and one critical eval for each core language family:
- Python
- Go
- TypeScript
- Rust

This is a floor, not a target. Add more evals when a language-specific failure appears in real use.
