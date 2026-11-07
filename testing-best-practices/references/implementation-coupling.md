# Audit and correct implementation locks

Use this workflow when an AI has written the implementation, tests, expected
results and approval machinery together. Agreement among those artifacts is
not independent proof. Apply the same standard to human-written code.

First ask whether the check still protects a distinct requirement. A duplicate
or obsolete one-time gate may be deleted without a replacement; a pin must not
veto an owner-authorized behavior change. See [verification cost](verification-cost.md)
before building reseal tools, recurring fault campaigns or approval exceptions.

## Classify the promise before changing the check

| Check | What exact identity establishes | Default action |
| --- | --- | --- |
| Full-SHA Actions/reusable workflows, dependency locks, downloaded-resource checksums | Which external code or bytes are accepted | Retain; keep controlled updates and behavioral tests around their use |
| Signatures, content-addressed storage, optimistic concurrency, cache keys | Authenticity, byte identity, conflict detection or invalidation | Retain; test accepted/rejected payloads and effects |
| Hash on a historical report or reviewed artifact | The input/output that was actually reviewed | Retain as provenance; do not rewrite history to fit current code |
| Same-run determinism or a documented wire format | An explicit output contract | Retain the promised equality; test meaning separately |
| Source-tree hash, private helper identity, exact SQL/CSS/source string | Usually the current implementation | Replace unless this architecture or byte format is explicitly the contract |
| Encoded-image golden or whole-tree approval gate | Possibly more identity than the visual/review claim needs | Narrow to affected inputs and observable properties while preserving provenance |

Do not remove all pins or hashes. A resource checksum must reject changed
bytes; a JSON serializer may change whitespace if it promises values rather
than serialization bytes. Public export names, compatibility versions and
authored content can be real contracts. Ask for the requirement and consumer.

## Audit the whole path

1. Inventory producers and consumers: CI, tests, manifests, approval readers,
   generators and auto-updaters. Search hash APIs/literals, fingerprints,
   snapshots, source readers and exact comparisons, including custom helpers
   hiding digests. Separate live gates from historical evidence, lockfiles,
   vendored code and deliberately bad fixture examples.
2. Name the claimed behavior, owning boundary, input domain and independent
   expected result. A digest match does not establish that a renderer preserved
   a label, a request was authorized or a message reached another client.
3. Try an allowed refactor: rename a private helper, reverse an equivalent
   integer comparison, reformat CSS, change JSON whitespace/key order, or
   recompress an image without changing decoded pixels. Distinguish an intended
   byte/architecture policy from an accidental implementation lock.
4. Try a credible defect: remove a label, exceed a request limit, omit a
   broadcast, return the wrong row, accept corrupted bytes, or skip the tests.
   Required words in comments, dead code or unused helpers are not execution.
5. Report location, claimed versus observed guarantee, permitted refactor,
   broken-behavior control, proposed keeper and limits. An empty keyword
   inventory does not certify a codebase correct.

## Correct it at the owning boundary

Move useful, still-required assertions to the real producer/consumer before
removing the old check. Drive HTTP handlers, production database queries, both sides of a wire
protocol, real components/renderers or emitted module/request graphs. Keep
real-engine tests at their existing boundary. Do not create a second
implementation, export internals solely for tests, or source-slice and
recompile a function with test-built wiring.

Use an independent parser/value comparison for structured output contracts.
For rendering, inspect actual text, geometry, connectivity, accessibility or
decoded pixels as the claim requires. Screenshot hashes cannot prove graph
meaning or keyboard interaction. Canonicalizing source or calling the same
implementation helper on both sides only disguises the implementation lock.

Keep review freshness separate from quality. Preserve subject and artifact
hashes. After evaluator changes, rerun affected measurements and compare the
rule/schema version, thresholds and finding identities before transferring
dispositions. Changed subjects, metric meaning or measured results require new
evidence. Never silently rebind waivers or add an automatic approval updater to
get green. Whole-tree identity can suit a scoped release event, but does not
make an unrelated README edit a product regression.

## Verify and communicate

Run the nearest owning tests and required repository checks. Show an allowed
implementation variant staying green and a behavioral fault going red, then
restore production bytes. Name retained coverage, or explain why a removed
assertion had no distinct guarantee and needs no keeper. These can be local
authoring checks, not permanent jobs or another approval protocol. State
which pins remain and why, exact commands/results and unverified boundaries.
Label static inspection honestly; do not claim an executed independent oracle.

For AI-output graders, execute candidates only in an appropriate isolated
runner. Require nonempty executed cases and failure on broken behavior; words
such as `assert`, `retry` or `clock` in comments are not evidence. Grade allowed
refactors too, so the grader does not teach the agent to copy one reference.
Protect host credentials, network access and the grader's trust boundary.
