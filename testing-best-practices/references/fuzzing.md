# Coverage-Guided Fuzzing

Load this reference when coverage-guided fuzzing is a risk-justified candidate: an exposed or custom parser, length/offset/chunk walker, native or unsafe decoder, crash-prone boundary, or security tool whose crash can bypass a check. Untrusted input alone still needs boundary tests, but does not mandate a new fuzz engine for every parser.

## Separate the target from the campaign

A fuzz target is usually small and cheap to maintain. A long discovery campaign consumes CPU. Do not classify the target itself as “Tier 3” merely because an hours-long campaign is expensive.

Property-based testing and coverage-guided fuzzing complement each other:

- Property tools construct values from declared strategies and shrink failures.
- Coverage-guided fuzzers mutate inputs toward new control flow and manage a corpus.

They may share an oracle, but they are not interchangeable and do not necessarily use the same harness or replay artifact.

## Minimum useful target

- Call the production entry point through a bytes/string/Reader seam; do not duplicate parsing logic in the target.
- Keep each invocation deterministic, stateless, fast, and bounded in input/output size, depth, allocation, and time.
- Seed with small production-shaped, boundary, and malformed examples. Add structured-valid builders or custom mutation only when raw mutation cannot reach semantic branches.
- Catch only documented rejection errors. Let unexpected exceptions, panics, sanitizer failures, and invariant violations escape so the engine records them.
- Assert more than no-crash when possible: valid-or-error shape, roundtrip/canonical form, sanitizer fixed point and safe-content preservation, differential equality, or a shadow-model invariant.
- Instrument native/cgo/extension code with the sanitizers and coverage mechanism required by that engine; a language-level harness may not cover native internals.

## Corpus, failure, and replay discipline

- Use the engine's own seed/corpus and failure-artifact mechanism; do not replace it with a universal “log the random seed” rule.
- Persist minimized failures in the path ordinary tests replay, or turn them into explicit regressions when the engine cache is not durable.
- Keep the exact replay command beside CI output or contributor guidance.
- Do not catch a crash, save it manually, and continue if doing so prevents the engine from recognizing and minimizing the failure.
- Treat timeouts, hangs, excessive allocation, and output/depth explosions as findings. Bound the target rather than denylisting unknown inputs out of discovery.

## Campaign tiers

| Tier | When | Purpose |
|---|---|---|
| Seed/regression replay | Every change or a dedicated regression job | Keep found bugs fixed; this is not active discovery |
| Bounded active discovery | PR/push where target cost permits | Catch shallow regressions with seconds per target |
| Scheduled campaign | Nightly/weekly, minutes or hours | Rotate exploration and grow useful corpus |
| Continuous service | Mature exposed OSS parser/library | Distributed long-running discovery and sanitizer coverage |

Follow the language reference or the selected engine's project documentation: engines differ on whether an ordinary test run generates property cases, only replays a fuzz corpus, or performs active mutation. Do not transfer Go's `testing.F` commands or corpus behavior to a Python or TypeScript property runner. Inventory source targets against the CI discovery matrix. A target that exists but is never selected may replay seeds while finding nothing new.

**Restraint.** Trusted, internally constructed, typed input does not earn a fuzz target merely because a helper manipulates a string. Prefer examples, exhaustive cases, or ordinary properties unless an untrusted boundary also has amplifying exposure, parser complexity, native/unsafe behavior, crash history, or security impact that justifies active fuzzing. Likewise, seed replay on every PR plus scheduled discovery can be the right cost split; do not demand minute-long campaigns on every PR by default.
