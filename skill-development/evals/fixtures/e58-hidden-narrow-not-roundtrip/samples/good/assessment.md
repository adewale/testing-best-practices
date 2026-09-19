# Assessment: the reviewer is mistaken about this particular test

The reviewer's instinct — prefer narrow assertions in behavior tests — is a
good default, but it does not apply here. This is a save/load roundtrip test,
and the whole-state canonical comparison **is** the contract under test:
`save` followed by `load` must be the identity over the *entire* store.

If we narrow the assertion to the quota fields this PR touches, the test can
no longer notice save/load silently dropping or corrupting profiles, flags,
or any future field — exactly the false confidence a roundtrip test exists to
prevent. A canonical dump that ignores fields cannot fail for them.

## What I would change

- **Keep the whole-state roundtrip comparison as-is.** The seeded rich state
  and canonicalized dump (sorted keys, normalized floats) are what make the
  identity check deterministic; that design is correct.
- **Add a separate, narrow behavior test for the quota change** in this PR:
  e.g. assert the specific new quota rule against literal expected values.
  That test is where narrow assertions belong.
- Optionally, on mismatch, emit both canonical dumps so a failure is a
  reviewable diff rather than "dumps differ."

Narrow assertions and whole-state roundtrips answer different questions:
"is this behavior right?" versus "does persistence preserve everything?"
This test is the second kind; keep it whole.
