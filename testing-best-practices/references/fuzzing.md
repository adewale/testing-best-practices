# Coverage-Guided Fuzzing

Load this reference when coverage-guided discovery is justified by an exposed or custom parser, native or unsafe decoder, crash history, complex length/offset/chunk handling, or a security boundary whose crash can bypass a check. Untrusted input needs boundary tests, but not every parser needs a new fuzz engine.

## Separate the target from the campaign

A small fuzz target can be ordinary triggered test work; a long campaign consumes sustained CPU. Property tools construct values from strategies and shrink failures. Coverage-guided fuzzers mutate a corpus toward new control flow. They can share an oracle, but their discovery and replay mechanisms are not interchangeable.

## Minimum useful target

- Call the production entry point; do not copy parsing logic into the harness.
- Keep each invocation deterministic, stateless, fast, and bounded.
- Seed production-shaped, boundary, and malformed examples. When checksums, compression, or dependent fields block reachability, mutate a semantic representation and re-encode it or use the engine's structured mutator.
- Catch only documented rejection errors. Let unexpected exceptions, panics, sanitizer failures, and invariant violations escape so the engine can retain and minimize them.
- Assert a semantic property when one is available: valid-or-error shape, roundtrip, canonicalization, safe-content preservation, differential equality, or model agreement.
- Instrument native or extension code with the sanitizer and coverage mechanism required by the selected engine.

## Corpus and replay

Use the engine's seed/corpus and failure-artifact mechanism. Persist minimized failures where ordinary tests replay them, or promote them to explicit regressions when the engine cache is not durable. Keep an exact replay command with CI output or contributor guidance. Treat hangs, excessive allocation, and output/depth explosions as findings; bound the target instead of hiding unknown inputs behind a denylist.

## Campaign tiers

| Tier | Purpose |
|---|---|
| Seed/regression replay | Keep found bugs fixed; not active discovery |
| Bounded PR/push discovery | Catch shallow regressions when target cost permits |
| On-demand deeper discovery | Investigate a concrete parser risk within a fixed budget |
| Explicitly agreed scheduled/continuous discovery | Explore beyond the ordinary budget when sustained cost and an owner are justified |

Default to seed replay plus short bounded discovery in an existing job when
discovery earns its cost. Bound expensive invocations as well as the campaign.
For Go, `-fuzztime=<N>x` bounds iterations when a wall-clock discovery limit causes
deadline flakes; keep the surrounding job deadline unchanged. A budget increase
or new schedule requires a reason, not parity with another repository.

Follow the language reference or selected engine documentation for collection, active discovery, and replay. Where CI duplicates source target names in a manually maintained matrix, compare the source inventory with that matrix; otherwise do not add a policy guard merely because fuzzing exists.

**Restraint.** Trusted, internally constructed, typed input does not earn a fuzz target merely because a helper manipulates a string. Prefer examples, exhaustive cases, or ordinary properties unless exposure, parser complexity, unsafe behavior, crash history, or security impact justifies active discovery. Do not demand scheduled discovery or long campaigns on every PR.
