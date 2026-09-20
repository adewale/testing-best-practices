# Property-Based Testing

Load this reference when writing or assessing generative tests. Use the language reference for engine-specific collection and replay.

## Choose the input layer deliberately

| Input layer | Best evidence |
|---|---|
| Small finite domain | Exhaustive loop or table |
| Arbitrary bytes/text | Totality, resource bounds, or documented error shape |
| Specification-valid structures | Semantic invariants, field preservation, canonicalization, or roundtrip |
| Mutations of valid corpus entries | Deep parser reach plus malformed-neighbor behavior |
| Stateful operation sequences | Model agreement after every accepted operation |

Keep totality and semantic properties separate. For semantic parser properties, generate a model, encode it independently of the production parser, then compare the parsed meaning with the model. Validate any “valid” builder independently; otherwise every case can stop at the parser's first guard.

Construct admitted values directly instead of filtering most candidates away. Do not widen documented finite, typed, or protocol-bounded domains merely to claim breadth; enumerate small finite spaces.

## Use an independent oracle

Prefer the strongest applicable oracle: an exact invariant, roundtrip with defined equivalence, idempotence, metamorphic relation, differential implementation, or small shadow model. “Did not crash” is a useful hostile-input floor, not a universal endpoint. Reject conditional assertions, blanket exception suppression, expected values computed with production logic, and models copied from the system under test.

## Execution and replay

Use the engine's reported example, seed/path, database, or corpus artifact. Promote important minimized failures into the form ordinary tests replay. Verify collection with the exact CI configuration when multiple runners, projects, or filters make reachability uncertain; add a persistent drift guard only when that configuration is itself a recurring risk.
