# Verified research: similar skills and transferable eval patterns

See also `LEADING_SKILLS_COMPARISON.md` for skills.sh `?q=tdd` / `?q=testing` rankings, install counts, and measurement implications.

Verified via skills.sh/GitHub raw sources on 2026-05-20. Commit SHAs are branch heads at verification time.

| Source | Raw source inspected | SHA | What matters for this skill |
|---|---|---:|---|
| `pbakaus/impeccable` | <https://raw.githubusercontent.com/pbakaus/impeccable/main/.agents/skills/impeccable/SKILL.md> | `642f03d5a10e` | A broad quality skill can still be operational: setup first, context loader, register selection, command table, explicit “absolute bans,” and command-specific references. Testing analogue: first-90-seconds context, mode routing, canonical anti-pattern bans, and command/report contracts. |
| `googlechrome/modern-web-guidance` | <https://raw.githubusercontent.com/googlechrome/modern-web-guidance/main/skills/modern-web-guidance/SKILL.md> | `1dee00c2ae94` | Strong trigger/skip list and search-first external knowledge flow. It pins a `--skill-version`, warns if stale, and requires retrieval before implementation. Testing analogue: version/freshness metadata for framework refs and “inspect existing project/tests before generating.” |
| `mattpocock/skills` TDD | <https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/tdd/SKILL.md> | `b8be62ffacb0` | TDD is behavior-first, public-interface-focused, and warns against “horizontal slicing” (all tests first, then all implementation). Testing analogue: eval red/green evidence and one-behavior vertical slices. |
| `obra/superpowers` TDD | <https://raw.githubusercontent.com/obra/superpowers/main/skills/test-driven-development/SKILL.md> | `f2cbfbefebbf` | Very strict “watch it fail” framing with verification checklist and exceptions requiring human partner. Testing analogue: score TDD by command evidence, not prose claims. |
| `currents-dev/playwright-best-practices` | <https://raw.githubusercontent.com/currents-dev/playwright-best-practices-skill/main/SKILL.md> | `ef329e7e6514` | A large testing skill uses an activity-based reference guide, quick decision tree, and test validation loop. Testing analogue: replace always-loaded doctrine with an activity matrix and lazy topical refs. |
| `antfu/skills` Vitest | <https://raw.githubusercontent.com/antfu/skills/main/skills/vitest/SKILL.md> | `50deaeb269d8` | Generated/versioned framework skill with compact topic-to-reference tables. Testing analogue: framework references need source/version metadata and freshness checks. |
| `.NET assertion-quality` | <https://raw.githubusercontent.com/dotnet/skills/main/plugins/dotnet-test/skills/assertion-quality/SKILL.md> | `e2dc44c377b9` | Splits assertion quality into measurable categories: trivial assertions, zero assertions, negative assertions, exception/state/structural assertions, and calibration rules. Testing analogue: replace “3+ assertions” with assertion diversity/oracle-strength rubric. |
| `.NET test-anti-patterns` | <https://raw.githubusercontent.com/dotnet/skills/main/plugins/dotnet-test/skills/test-anti-patterns/SKILL.md> | `e2dc44c377b9` | Detection-focused skill with severity groups, calibration, report structure, and “when not to use.” Testing analogue: anti-pattern detection mode should output severity, evidence, concrete fix, positive observations. |
| `.NET test-gap-analysis` | <https://raw.githubusercontent.com/dotnet/skills/main/plugins/dotnet-test/skills/test-gap-analysis/SKILL.md> | `e2dc44c377b9` | Pseudo-mutation skill explains why coverage misses bug sensitivity and enumerates mutation classes. Testing analogue: evals should measure mutant/seeded-bug detection, not coverage percentage. |

## Lessons to apply

0. **Assume evals will break** — Lun Wang's “Your Evals Will Break and You Won't See It Coming” argues that evals fail silently when capabilities or failure modes shift. For this skill, treat evals as a living system: track score saturation, static-vs-runtime correlation, framework freshness, and real-world misses; add rotating probes rather than trusting a fixed checklist forever.

1. **Make the skill measurable at three levels**
   - Static docs: no contradictions, no unsafe universal rules, no broken links.
   - Prompt behavior: agent chooses the right mode, asks/acts within scope, reports validation honestly.
   - Runtime fixtures: generated/upgraded tests fail on seeded bugs and pass after fixes.

2. **Replace broad doctrine with activity routing**
   - `currents-dev/playwright-best-practices` and `antfu/vitest` are tables of activities/topics to references.
   - Our `SKILL.md` should become: trigger → first-90-seconds checklist → mode matrix → final output contract.

3. **Turn TDD into evidence gates**
   - Matt Pocock: behavior through public interfaces, no horizontal test batches.
   - Obra: if you did not watch the test fail, you do not know it tests the right thing.
   - Our rubric should require failing-test evidence where feasible and honest “red phase not verified” reporting otherwise.

4. **Use calibrated assertion quality, not assertion count absolutism**
   - Dotnet assertion-quality classifies trivial, negative, exception, state, side-effect, and structural assertions.
   - Our skill should treat “3+ assertions” as a heuristic for example-based behavior/security tests, not property/table/exception tests.

5. **Separate generation, audit, and gap analysis**
   - Dotnet splits code-test generation, assertion quality, anti-patterns, and pseudo-mutation.
   - Our four modes should stay distinct: Write, Assess, Upgrade, Detect, each with its own report shape.

6. **Anti-patterns should be concrete search signals**
   - Impeccable has “absolute bans”; dotnet anti-patterns have severity categories.
   - Our static gate should look for known doc contradictions and the skill should teach agents to detect skipped tests, weak assertions, sleeps, live network, mock drift, and implementation-detail coupling.

7. **Version/freshness is part of correctness**
   - Modern Web Guidance pins a skill version and warns on stale guide retrieval.
   - Our language refs should eventually carry `last_reviewed`, framework version, and source links; evals should catch stale examples like bad Vitest/fast-check patterns.

## Direct artifacts from this pass
- `evals/evals.json`: expanded from 14 to 22 evals with taxonomy and measurement fields.
- `evals/taxonomy.md`: canonical tags and minimum coverage expectations.
- `evals/schema.json`: machine-readable target shape.
- `scripts/score-evals.py`: stdlib validator and taxonomy coverage reporter.
- `scripts/static-audit.py`: baseline regression gate for known P0/P1 documentation failures.
- `evals/scorecard.md`: baseline/final scoring template.
- `evals/eval-health.md`: obsolescence/drift monitoring inspired by the Wang evals-break essay.
