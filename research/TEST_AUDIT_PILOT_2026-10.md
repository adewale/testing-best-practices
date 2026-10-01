# Test-audit pilot: what each step cost and what it found (2026-10-01)

A revised version of the openclaw `test-audit` prompt was run on three of the owner's repositories. Each step was timed, and every finding was traced to the step that produced it. The aim was a real PR per repository and a cheaper process for the next cycle.

| Repo | PR | Shape | Outcome |
|---|---|---|---|
| `planet_cf` | [#18](https://github.com/adewale/planet_cf/pull/18) | Python worker; SQL-text tests and a regex D1 fake | 9 tests that could not catch their bug replaced with tests on SQLite loaded from the migrations. The review found a **product bug**: database auto-init has never worked on real D1, which splits `exec()` on newlines. Fixed in its own commit with a failing control. Mutations caught: 6/19 by `main`'s tests, 13/19 after the author's first pass, 19/19 after review |
| `vaders` | [#12](https://github.com/adewale/vaders/pull/12) | Bun TUI game; 37 tests regexing `App.tsx` | Replaced by 11 tests that render the real TUI. The first real render exposed a **product bug**: magenta colours on every terminal not detected as true colour. Also fixed a type check that could not fail, and started fixing an E2E job that has never passed on `main` (the rest of that fix is in a file owned by another open PR) |
| `claude-history-explorer` | [#15](https://github.com/adewale/claude-history-explorer/pull/15) | small CLI and Worker (control) | 6 checks behind two documented guarantees could not fail. Replaced with behavioural tests: the read-only guarantee is now checked by running every CLI command against a temporary `~/.claude`. No product bug; a small PR |

All three PRs are green on CI except for a pre-existing red `npm audit` step owned by another open PR. Each touches 6–11 files. For comparison, an owner-run audit of `geist_fabrik` with the original prompt (PR #92) found about 15 product bugs, but in one PR of 153 files (+8,169/−20,026) built over about 1.5 days.

## Cost

| Role | Tokens | Tool calls | Wall clock |
|---|---|---|---|
| Authors, phase 1 (audit, change, verify) | 0.94M (276k, 329k, 338k) | 124–184 | 20, 21, 34 min |
| 12 reviewers (4 per repo, run in parallel) | **1.71M** (117k–194k each) | 43–72 | 8–12 min each |
| Authors, phase 2 (verify and fix review findings) | not separable (resumed context) | 26–51 | 6, 7, 13 min |
| CI | — | — | about 3–8 runner-minutes per PR, free on public repos |

Independent review cost nearly twice as many tokens as the audit itself.

## Which steps paid

| Step | Value in the pilot | Verdict |
|---|---|---|
| Map openclaw commands to the repo | none | Drop; read the CI workflow |
| Baseline: last result per CI job on main | Found an E2E job dead for six months (`vaders`) and a red audit step (`claude-history-explorer`) | Keep. One CI-history call |
| Baseline: pass/fail per test file | Nothing; every file passed | Drop; one run per tier is enough |
| Open-PR overlap check | Set the scope in every repo. But it also left the most valuable fix half-done (`vaders` E2E: one line in a file owned by another PR) | Keep, and add an escape hatch for one-line fixes |
| Ledger of every test (395 rows in the small repo, mostly "keep") | Every acted-on item came from about 5 greps plus reading the flagged files | Mark only grep candidates and their neighbours |
| "Where did each expected value come from?" | Found a fake that handed back the answer (`planet_cf`) and a type check that could not fail (`vaders`) | Keep |
| Replace text pins with the real engine | Exposed the `vaders` product bug | Keep |
| Scripted mutation runs | The most persuasive evidence, and they caught the authors' own overclaims | Keep. Also run the *old* tests against the same mutations |
| One mutation per deleted test's replacement | Useful once; ceremony where the replacement was the type checker | Keep, but pick the mutation from what the deleted test could detect |
| Full local CI rerun before push | Duplicated an 85 s CI run | Drop when CI is fast |

## Which reviewers paid

| Should-fix finding | Combined | Correctness | Test effectiveness | Docs |
|---|---|---|---|---|
| `planet_cf`: D1 `exec()` product bug | – | ✔ (reproduced on real workerd) | ✔ | – |
| `planet_cf`: lost checks (`entries_scanned`, recovery events) | ✔ (partly) | – | ✔ | – |
| `planet_cf`: expected value credited to the wrong spec | ✔ | ✔ | ✔ | ✔ |
| `claude-history-explorer`: lost check on the malformed-line write path | – | – | ✔ | – |
| `claude-history-explorer`: `ARCHITECTURE.md` describes deleted tests | ✔ | – | – | ✔ |
| `vaders`: colour quantisation pointless (fix simplified, production code removed) | – | ✔ | – | – |
| `vaders`: "nearest colour" claim false | nit | ✔ | nit | ✔ |
| `vaders`: PR body's no-overlap claim false | ✔ | – | – | ✔ |
| `vaders`: E2E history overstated | nit | – | – | ✔ |

- **The combined reviewer found nothing that a specialist missed.** It missed both product-level findings (`planet_cf` D1, `claude-history-explorer` lost check).
- **The test-effectiveness reviewer was the most valuable.** It found every lost check and the D1 bug, and in `vaders` it confirmed with mutations that no contract was lost.
- **The correctness reviewer paid when production code or a double of an external system changed** (`planet_cf`, `vaders`). In `claude-history-explorer`, whose only production change was deleting a dead function, it found nothing.
- **The docs reviewer mostly caught PR-body claims and stale docs that mechanical checks can catch:**
  - overlap claims, with `comm -12` on the file lists;
  - CI history, by reading per-job rather than per-run conclusions;
  - counts, with `--collect-only`;
  - stale docs, by grepping for the names *and descriptions* of deleted tests.

## Lessons for the skills

43 skill-feedback items in total:
- **35 needed no skill change.** The existing guidance already covered them.
- **8 were one-sentence text edits:**
  1. A SQLite double reproduces D1's engine, not its binding. Check `exec`, `batch` and the limits once against miniflare or workerd.
  2. Run the old tests against the same mutations as the new ones. A mutation the old tests catch and the new ones don't is a lost check.
  3. Choose a deleted test's keeper mutation from what the deleted test could detect, and make sure the keeper's fixture reaches that branch.
  4. A test with no contract needs no keeper; say so.
  5. Grep docs for descriptions of deleted tests, not just their names.
  6. Prove a type-level assertion can fail by deleting a member.
  7. `set -e` plus `VAR=$(cmd)` exits before `$?` is read, so an "already applied" branch is dead.
  8. (A duplicate of 2.)
- **No item called for an eval.** For comparison, evals E70–E78 in this repository took about 1,800 lines of fixtures and metadata, and none has been run against a model.

## Cheaper process for the next cycle

```
Audit and upgrade the tests and quality gates in <owner/repo> (openclaw test-audit: authoring gate, junk
patterns, retention bar; testing-best-practices @ <SHA>). One coherent PR, budget <N> hours. Do not merge.

1. Scope: read CI's last result per job on main; run each tier once locally; list open PRs' files and compare
   them with yours (comm -12). Baseline failures are bug reports. If the best fix is one line in a file another
   open PR owns, include it if merge-tree is clean, otherwise put it in the PR body as a ready patch.
2. Candidates: grep for source/config reads, SQL or text asserts, hashes and copied counts, assertions only inside
   loops, skips, and fakes that return the asserted value. Read those files; for each candidate say keep, fix,
   merge or delete, and where its expected value came from.
3. Change: replace text and pin tests with tests through the real engine or a real seam. Check any double of an
   external system against the real runtime once (e.g. miniflare for D1). Write a small mutation script and run
   both the old and the new tests against it; report kills for each. A deleted test needs a replacement that fails
   on what it could detect, or a note that it had no contract. Product bugs go in a separate commit with a
   failing control.
4. Verify: push and read CI per job. Before writing the PR body, check each claim mechanically (overlap, CI
   history, counts) and grep docs for the names and descriptions of anything deleted.
5. Review: one independent test-effectiveness reviewer (old-vs-new mutations, lost contracts, doubles vs the real
   runtime). Add a production-correctness reviewer only if production code or an external-system double changed.
   Verify each finding before fixing it.
6. Report merge readiness as facts. Record skill feedback as one line per gap (none or text-edit).
```

**Expected saving:** 1–2 reviewers instead of 4 cuts review tokens by about half to three-quarters, about 0.9–1.3M of the 1.7M here. Dropping the baseline tables and the full ledger shortens the audit itself. On these three repositories, every should-fix finding would still have been found, either by the reviewers kept or by the mechanical claim checks. This rests on three repositories, so treat it as a working hypothesis, not a measurement.

**Feeding lessons back into the skill cheaply:**
- Collect the one-line feedback from each audit.
- Apply a text edit when two audits hit the same gap, or one audit quotes a passage that misled it.
- Record retractions in the CHANGELOG table.
- Let the next real audit be the test of the edit.
- Reserve evals for the rare lesson that would regress silently and matters a lot. None of the 43 qualified.
