# Assessment

All three files look like generative coverage, but only the TypeScript file is
currently executed, and even that one misses production.

## P0: make execution and reachability observable

The Python command is `unittest discover`. It imports matching modules but does
not collect a module-level pytest/Hypothesis function, so
`test_slugify_is_idempotent` contributes zero examples to CI. Run the suite with
pytest and add `pytest --collect-only -q` as a collection guard whose expected
test count is checked in CI. Keep a small smoke invocation of the property in
the normal pytest run.

The Go command has different semantics: `go test ./...` runs each fuzz target's
seed corpus as regression tests, but it does not perform active fuzz discovery.
Inventory `FuzzDecodeFrame` and `FuzzParseHeader`, then use a two-entry CI matrix
that invokes one target at a time, for example
`go test ./wire -run=^$ -fuzz=^FuzzDecodeFrame$ -fuzztime=15s`, followed by the
equivalent invocation for `FuzzParseHeader`. Keep seed replay in every PR and
put longer discovery campaigns on a schedule.

The fast-check property runs, but it calls the test-local
`normalizeCandidate`, not production `normalizeSlug`. The local copy is already
semantically different (`toLowerCase` versus the explicit `en-US` locale), so a
production regression can remain green. Delete the copy, import
`normalizeSlug` from `src/normalizeSlug`, and call that function directly in
the property. A mutation that breaks the production function should then make
this property red.

Finally, make the three checks explicit in CI: assert Python collection,
compare the discovered `func Fuzz...` inventory to the fuzz matrix, and reject
generative tests that do not import or reach a production entry point.
Do not leave the Hypothesis function under the unittest-only command or omit the
exact-runner collection guard. Do not keep the copied helper, and do not avoid
the production import.

An equally valid repository-specific alternative is to keep
`python -m unittest discover -v`, move `test_slugify_is_idempotent` into a
`unittest.TestCase` method, and add a CI guard that asserts the named test
appears under that exact command.
