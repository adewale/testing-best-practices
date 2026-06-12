# Research Methodology — A Floor, Not a Ceiling

> How we research a practitioner for this corpus. Everything here is the *minimum*; if the subject's most valuable testing thinking lives somewhere this document doesn't mention, go there. The deliverable is lessons, not checked boxes.
> Date: 2026-06-12

---

## The goal

Each practitioner gets one document, `research/LESSONS_FROM_<NAME>.md`, that distills *transferable testing lessons* from everything they've made and said. We are not writing biographies. A fact earns its place only if it supports a lesson someone could apply to a test suite tomorrow.

## The floor: sources that must be checked for every subject

1. **GitHub history — read the code, don't skim the profile.**
   - Inventory all repos (and any org they drive, e.g. `fedwiki` for WardCunningham, `janestreet` for the Jane Street individuals). Note stars, language, dates, forks-vs-originals.
   - Clone the significant repos. Read the actual test files, test helpers, CI workflows, and `package.json`/build test targets — not just READMEs.
   - Read commit history: who authored the tests (the subject or the community?), what the commit messages say, what got abandoned.
   - **Record absence as a finding.** "924★ repo, zero tests, README explains why" teaches as much as a good suite. Never silently skip repos that lack tests.
2. **Books.** Check the bookshelf explicitly — every book they wrote or co-wrote, plus chapters they contributed (e.g. *Beautiful Code*, *500 Lines or Less*). Mine the testing content of each; a practitioner whose primary medium is books (Beck, Pryce) is misrepresented by a repos-only doc. Use publisher samples, companion sites, the authors' own articles restating the material, and reputable summaries; quote short and verify before attributing.
3. **Long-form writing.** Blogs, essays, papers, pattern languages, wikis, mailing-list posts. For pre-web or decayed sources, try: archive.org, the site's JSON/API back end (fedwiki sites serve `/<slug>.json` when HTML 503s), `raw.githubusercontent.com`, and mirrors in successor projects.
4. **Talks, interviews, podcasts.** Transcripts where they exist (Artima, InfoQ, Hanselminutes, Signals & Threads). These often contain the honest post-mortems that never make it into books.
5. **Tools and frameworks they created — including pre-GitHub ones.** Fit lived on fit.c2.com and CVS; jMock predates the subject's GitHub account. The tool's design *is* a testing opinion; read its source if it survives (Fit's 199-line parser was worth measuring).
6. **Post-mortems and criticism — by them and of them.** What they later said failed ("Fit is Dead", Shore's acceptance-testing retraction, "struggling with mocha, giving up") is often the most durable lesson. Seek the strongest critique of their approach and report it.

## Standards of evidence

- **Primary sources over summaries.** Quote verbatim, keep quotes short, attach a URL to every claim a reader might want to verify.
- **Attribute with care.** Multi-author wikis (c2) are not the host's voice — attribute signed passages to their signers. Laws named after people may be coined *about* them (Cunningham's Law is McGeady's). Auto-generated transcripts get a caveat. When a connection is our inference rather than their statement, label it as inference.
- **Date everything**: the document, the sources, the commits. Ideas have versions (CHECKS 1994 vs. its 2017 langsec reframing; XP Explained 1st vs. 2nd edition).
- **Report negative results.** Sources that were unreachable, claims that couldn't be verified, and approaches the subject abandoned all go in the doc rather than disappearing.

## Output format (house style)

- Title: `# Lessons from github.com/<account> (Full Name)` — or the closest equivalent for organizations.
- Blockquote header: one-line bio of why they're in the corpus + research date.
- `## Who He/She/They Is/Are` — and why their angle differs from the rest of the corpus.
- Themed sections (one per artifact or idea), each grounded in evidence: short verbatim code/table/quote snippets, then a bolded `**Lesson**:` stating the transferable practice.
- `## Key Insights` — a closing numbered list; each item must be supported by a section above, not introduced there.
- Update `README.md`: the research-corpus bullet list (with account count) and the `research/` file tree.

## Before declaring a subject done

- [ ] Repo inventory done, significant repos cloned, real test files read, test-commit authorship checked
- [ ] Their books (and contributed chapters) checked for testing content — or confirmed they have none
- [ ] Their own writing, talks, and interviews searched
- [ ] Their pre-GitHub tools considered
- [ ] The strongest criticism / their own post-mortems included
- [ ] Every quote attributed and linked; inferences labeled; absences reported
- [ ] README corpus list and file tree updated

## Why this is a floor, not a ceiling

The checklist above exists because we've missed things by skipping items on it (books, for several early subjects). It does **not** define the search space:

- **Follow the subject's actual medium.** Dan Luu's case rested on a hardware-verification culture argument; Jane Street's on a podcast and library `.mli` files; Ward's partly on a federated wiki only reachable through its JSON API. The next subject's center of gravity may be conference papers, patents, production incident reports, courtroom testimony, or a Discord. Go where their thinking lives.
- **Spend effort proportional to yield, not symmetrically.** Some subjects warrant 2KB (tirsen), some 26KB (Jane Street). Depth follows the density of transferable lessons, not the checklist.
- **Add to the floor.** When a new source type proves valuable for one subject, consider whether it generalizes — if it does, add it here so the floor rises. This document should grow.
- **Revisit.** A subject researched in April is not settled in June. New repos, new talks, and newly accessible archives justify reopening a "finished" doc — as the book-coverage audit that prompted this file did.
