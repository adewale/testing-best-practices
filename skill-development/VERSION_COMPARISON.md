# Version Comparison: first GitHub skill vs current GitHub vs local

Compared on 2026-05-21.

Versions:
- **First working GitHub version**: `6951b7d Add testing-best-practices skill with research corpus`
- **Current GitHub version**: `origin/main` at `6e8cd8b7bad570126277e08ad445c5bd21cb92d9`
- **Local working version**: current working tree in `testing-best-practices/`

Artifacts:
- First skill copy: `skill-development/github-skill-first-working/testing-best-practices/`
- Current GitHub skill copy: `skill-development/github-skill-origin-main/testing-best-practices/`
- Version score JSON: `skill-development/version-scores/*.json`
- Prompt-run summaries are captured in `evals/scorecard.md`; raw `skill-development/eval-runs/` outputs are generated locally and ignored.

## Main score: skill artifact rubric

Rubric: `evals/version-rubric.md`, implemented by `scripts/score-skill-version.py`.

| Version | Total | Router/usability | Safety/calibration | Language coverage | Technique breadth | Correctness-by-construction | Validation/reporting |
|---|---:|---:|---:|---:|---:|---:|---:|
| First working GitHub (`6951b7d`) | **28/100** | 6/15 | 6/25 | 12/15 | 0/20 | 2/15 | 2/10 |
| Current GitHub (`6e8cd8b`) | **69/100** | 9/15 | 6/25 | 12/15 | 20/20 | 15/15 | 7/10 |
| Local working tree | **100/100** | 15/15 | 25/25 | 15/15 | 20/20 | 15/15 | 10/10 |

This distinguishes all three versions:

1. **First GitHub**: early working draft. It had core language files but lacked advanced technique breadth, correctness-by-construction, validation/reporting, and calibrated safety guidance.
2. **Current GitHub**: much broader and stronger, with advanced references and correctness-by-construction, but still contains known P0/P1 contradictions and router usability issues.
3. **Local**: same breadth as current GitHub plus cleaned router, calibrated safety guidance, unsupported-language fallback, and validation/reporting contract.

## Static safety audit

Script: `scripts/static-audit.py`.

| Version | P0 findings | P1 findings | Static gate |
|---|---:|---:|---|
| First working GitHub (`6951b7d`) | 6 | 4 | Fail |
| Current GitHub (`6e8cd8b`) | 6 | 6 | Fail |
| Local working tree | 0 | 0 | Pass |

### Current GitHub static failures

```text
P0 findings: 6
- references/typescript.md:63: sole toBeDefined() appears in TypeScript PBT example
- references/correctness-by-construction.md:65: six/seven contradiction in correctness-by-construction
- references/vcr-cassettes.md:27: hand-written MSW mock section is labeled as VCR cassette guidance
- references/antipatterns.md:49: integration tests incorrectly require an external dependency
- SKILL.md:90: positive+negative assertion rule is universal instead of scoped
- SKILL.md:355: downstream check deletion wording needs explicit safety preconditions

P1 findings: 6
- SKILL.md:63: TDD wording should be a default with feasibility/scope exceptions
- SKILL.md:87: assertion-count heuristic needs calibration
- references/test-types.md:86: unit rules need temp-dir/in-memory and assertion-count calibration
- references/go.md:33: Go table-driven guidance is over-universal
- references/test-types.md:163: generic cross-link should point to concrete local reference
- SKILL.md: router target exceeded (455 lines > 350 target)
```

## Fixture-backed prompt oracles

Prompt/fixture oracles are in `evals/fixtures/` and are run by `scripts/run-fixture-oracles.py`.

| Version | Fixture-backed prompt oracles | Critical fixture-backed oracles |
|---|---:|---:|
| First working GitHub (`6951b7d`) | 10/10 | 9/9 |
| Current GitHub (`6e8cd8b`) | 10/10 | 9/9 |
| Local working tree | 10/10 | 9/9 |

These prompt oracles are currently **saturated** across all three versions. This is exactly the failure mode warned about in Lun Wang's “Your Evals Will Break and You Won't See It Coming”: a benchmark can stop distinguishing meaningful differences once the model or task setup can route around the weaknesses.

The artifact rubric fixes that specific blind spot by scoring the skill instructions directly. It is not a replacement for prompt/runtime evals; it is an additional layer.

## Final comparison

| Measurement layer | First GitHub | Current GitHub | Local | Distinguishes all three? |
|---|---:|---:|---:|---|
| Skill artifact rubric | 28/100 | 69/100 | 100/100 | Yes |
| Static safety audit | Fail, 6 P0 / 4 P1 | Fail, 6 P0 / 6 P1 | Pass, 0 P0 / 0 P1 | Partially |
| Fixture prompt oracles | 10/10 | 10/10 | 10/10 | No, saturated |

## What this means

The fixture prompt oracles are not good enough by themselves. They verified that the model could produce acceptable outputs for 10 focused tasks even with the first skill version, but they did not measure whether the skill artifact had stale, contradictory, overbroad, or missing guidance.

The improved comparison now has three layers:

1. **Artifact rubric**: distinguishes first/current/local.
2. **Static safety audit**: catches concrete dangerous contradictions.
3. **Fixture prompt oracles**: checks whether generated candidates satisfy executable failure-mode oracles.

## Next hardening work

To make prompt/runtime evals distinguish current GitHub from local, add harder variants that directly target the old skill's weaknesses:

1. **Assertion calibration trap**: one strong Go table-row assertion; old guidance should over-prescribe 3+ assertions.
2. **PBT weak-example trap**: ask for/critique a “never throws” parser property; old TS reference contains `toBeDefined()`.
3. **Integration classification trap**: in-process controller+service+repo integration; old docs require external dependency.
4. **Correctness deletion trap**: repeated validation plus auth/security layer; old wording pushes deletion too aggressively.
5. **VCR/MSW drift trap**: hand-written MSW mock presented as VCR; local should distinguish deterministic mocks from recorded fixtures.

Those should become hidden/rotating evals, because the public fixture oracles are already saturated.
