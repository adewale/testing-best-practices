# Property-Based Testing: Reachability and Oracles

Load this reference when writing or assessing generative tests. Use the language reference for collection, replay, and engine-specific commands.

## Choose the input layer deliberately

One generator rarely proves every parser property. Use separate tests for separate domains:

| Input layer | Best evidence |
|---|---|
| Small finite domain | Exhaustive loop or table; sampling only weakens certainty |
| Arbitrary bytes/text | Totality, resource bounds, valid value or documented error |
| Specification-valid structures | Semantic invariants, field preservation, canonicalization, roundtrip |
| Mutations of valid corpus entries | Parser depth plus malformed-neighbor behavior; useful fuzz seeds |
| Stateful operation sequences | Model agreement and invariants after every accepted operation |

A random prefix plus arbitrary bytes is not automatically a valid image, archive, feed, or protocol frame. Construct required headers, lengths, checksums, terminators, and cross-field constraints, then validate the builder with an independent parser or conformance check. Keep the arbitrary-corrupt-input totality test too; it answers a different question.

## Keep generators reachable and honest

- Construct valid values directly instead of filtering or assuming most candidates away.
- Include empty, one, maximum, overflow-adjacent, Unicode, duplicate, reordered, truncated, and malformed-neighbor cases when the contract admits them.
- Do not hash, sanitize, or map arbitrary input into one narrow safe shape before the system under test sees it.
- Record distributions or witnesses for important branches. A conditional assertion that rarely runs is not evidence for that branch.
- Treat `maxExamples`, `numRuns`, and `maxCommands` as configuration limits, not proof of meaningful coverage.

**Restraint — narrow only for a reason.** A documented bounded domain, typed internal value, or protocol limit is not an over-constrained generator. Do not widen beyond the contract merely to claim breadth. When the domain is small and finite, enumerate it.

## Use an independent semantic oracle

“Did not crash” is a useful floor at a hostile boundary, not a universal stopping point. Prefer the strongest applicable oracle:

- exact domain invariant or conservation rule;
- encode/decode or parse/print roundtrip with defined equivalence;
- idempotence or canonicalization;
- metamorphic relation between related inputs;
- differential comparison with an independent implementation;
- simple shadow model for mutable behavior.

Reject vacuous shapes: truthiness-only results, `if result: assert ...`, blanket exception suppression, expected values computed with the same implementation, or a “model” copied from production logic. Confirm the property name matches what its assertions actually prove.

## Model state, time, and failure

Use model-based/stateful testing when correctness depends on a sequence: CRUD, caches, journals, filesystem/database sync, sessions, games, queues, retries, or recovery.

1. Keep the model smaller and more obvious than the implementation.
2. Generate both operation choices and their data.
3. Make applicability match the exact selected target. If an invalid operation is intentionally admitted, assert its defined no-op/error result rather than returning silently.
4. Compare results and relevant state after every accepted operation.
5. Add time advance, cancellation, crash, failure, duplicate/reorder, cleanup, and concurrency actions when the contract exposes them.
6. Measure accepted/executed transitions for the gate's seed; a generated-command cap is not a minimum.

For durable workflows, model the contract's observable delivery, duplicate/redelivery, interruption-recovery, and terminal-state guarantees. Add claim ownership, lease expiry/renewal, stale-owner behavior, retry/ack decisions, or idempotent domain effects only where the design exposes or promises them. When persistence and publication are separate, exercise the failure window and the outbox, replay, or reconciliation mechanism that actually exists. Atomic admission alone does not prove recovery or exactly-once effects.

## Preserve failures with the engine's mechanism

Use the framework's reported example, seed/path, database, or corpus artifact. Promote an important minimized failure into a permanent regression in the form the ordinary suite replays. A fixed PR seed can make failures easy to reproduce; a rotating scheduled run can broaden exploration. This is a policy choice, not a universal engine rule—follow the language reference and verify that every test project or sandbox receives the configuration.

Before trusting a suite, verify the configured runner actually collects the property and that CI exercises the production path rather than a copied helper.
