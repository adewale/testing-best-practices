# TODO

## v0.3 release checklist
- [x] Keep installable skill contents clean: only `testing-best-practices/SKILL.md` and `testing-best-practices/references/*.md`.
- [x] Move development artifacts to `skill-development/`.
- [x] Add version-comparison rubric distinguishing first GitHub, previous GitHub, and current local versions.
- [x] Add fixture-backed prompt oracles across Python, Go, TypeScript, and Rust.
- [x] Add hidden hard/adversarial eval probes for known weak spots.
- [x] Add mutation-backed mini-repos with seeded mutants.
- [x] Add best-practices audit and generated-artifact hygiene checks.
- [x] Run `skill-development/scripts/check-all.py` before release.
- [x] Create and publish GitHub release `v0.3`.

## Next eval improvements
- [ ] Turn E28–E32 hidden probes into executable fixtures or mini-repos.
- [ ] Add pairwise blind judging over first/current/local outputs for hard evals.
- [ ] Add prompt metamorphic variants for each public fixture oracle.
- [ ] Add Rust mutation-backed mini-repo so mutation checks cover all four core languages.
- [ ] Add a small CI workflow that runs `cd skill-development && python3 scripts/check-all.py`.
- [ ] Add a release script that updates token report, runs gates, creates tag, and drafts release notes.

## Next skill improvements
- [ ] Review references for further token trimming without losing trigger-specific guidance.
- [ ] Add more concrete good/bad examples for correctness-by-construction deletion safety.
- [ ] Add more language-specific examples for contract/schema drift testing.
- [ ] Revisit public fixture oracles quarterly and retire saturated items that no longer influence decisions.
