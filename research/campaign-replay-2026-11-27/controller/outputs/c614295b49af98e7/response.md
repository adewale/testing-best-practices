{
  "decision": "reject",
  "changes": [
    {
      "target": "Historical script provenance",
      "action": "Remove the comparison with the live checkout",
      "details": "Read the three script identities using the historical receipt format. Require one correctly encoded digest for each identity, even after a live rename. Report those values as recorded provenance. If the receipt references immutable script copies, verify those copies against the recorded digests. A digest alone cannot establish the contents of an unavailable script."
    },
    {
      "target": "Archive verifier",
      "action": "Keep verification read-only and enforce archive integrity",
      "details": "Require the archived output for each recorded candidate. Hash its exact bytes with the receipt's algorithm and compare with that candidate's digest. Reconcile each recorded total against the archived candidate-level results using the historical counting rules. Return failure for missing evidence or disagreement and identify the candidate, provenance field, or total responsible. Issue a separate receipt for a new evaluation."
    }
  ],
  "retained_contracts": [
    "Each candidate identity is bound to the exact output bytes recorded for that run.",
    "The recorded totals agree with the archived results.",
    "The receipt preserves all three historical script identities and digests across current tooling changes."
  ],
  "validation": [
    "Invoke the verifier entry point on a temporary archive with distinct outputs, independently computed fixed digests and hand-counted totals. Expect success. Use a fresh copy for each control.",
    "Edit only a comment in a current script. Separately rename a current script so its historical path is absent from the checkout. Expect success in both cases with the original receipt. Compare receipt bytes before and after every run.",
    "Change one byte of an archived output while preserving its scored result. Expect a digest failure naming that candidate. Separately remove the output and expect a missing-file failure.",
    "Change only a recorded total, leaving every output and digest intact. Expect failure showing the recorded and recomputed counts.",
    "Remove one historical script entry, then independently supply a malformed digest. Expect each to fail for the affected field. If immutable script copies are referenced, also corrupt one and expect its digest check to fail."
  ],
  "cost_and_stop": "Limit the change to the verifier and its focused tests. Compare old and revised verdicts on the same refactor and archive-corruption fixtures. Stop when the refactors pass, the corruptions fail for the intended reasons, and verification preserves the receipt. These checks are proposed and unrun.",
  "rationale": "Refreshing hashes after refactors would rewrite the account of which scripts ran and could bless corrupted output. Deleting the verifier would discard the check that still detects archive corruption and inconsistent totals. Today's filenames and comments supply no evidence about the historical run."
}
