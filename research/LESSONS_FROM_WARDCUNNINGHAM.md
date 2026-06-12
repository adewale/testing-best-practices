# Lessons from github.com/WardCunningham (Ward Cunningham)

> Inventor of the wiki, Fit (the Framework for Integrated Test), CRC cards, and the technical-debt metaphor. Co-discoverer (with Kent Beck) of the practices that became XP and TDD. Author of the CHECKS pattern language.
> Date: 2026-06-11

---

## Who He Is

Ward Cunningham is upstream of almost everyone else in this corpus. Kent Beck's TDD Money example came from Ward's WyCash portfolio-management work; XP "grew out of Ward's work at Tektronix"; Cucumber, SpecFlow, FitNesse, and Specification by Example all trace their lineage to his Fit framework. Ward's own framing of the division of labor, from the Artima interviews: *"Kent's single biggest contribution is being daring enough to say, 'This is all that matters, and we should do it all the time.'"* — the ideas they discovered quietly together, Kent took to the limit.

Unlike Kent, Ward's testing legacy isn't a single framework or manifesto. It's three threads: **Fit** (tests as customer-readable examples), **CHECKS** (validation as domain design rather than defensive code), and a working style — visible across 156 GitHub repos — where test investment tracks the expected lifetime of the code, feedback loops beat upfront prevention, and the cost of a mistake is engineered down instead of guessed away.

Sources: github.com/WardCunningham and github.com/fedwiki (cloned and inspected), c2.com/ppr/checks.html, checks.fed.wiki.org (via its JSON API; the HTML view 503s), c2.com/ppr/episodes.html, the Artima interview series with Bill Venners (2003–04), the Debt Metaphor transcript (wiki.c2.com/?WardExplainsDebtMetaphor, CC-BY), and Hanselminutes #151 ("Fit is Dead, Long Live FitNesse", 2009).

## Fit — Tests as Customer-Readable Examples (2002)

Fit (a backronym — the name came first; not "FIT") is Ward's distillation of a pattern he had built "maybe four times over" in financial software: customers write **examples of program behavior as tables in HTML documents** (often exported from Word/Excel); programmers write small **fixtures** mapping table cells to domain objects; Fit runs the document against the system and hands back the *same document* with cells colored green (right), red (wrong, annotated "expected / actual"), gray (ignored), or yellow (exception + stack trace).

The canonical ColumnFixture example — the table:

```
| eg.Division |
| numerator | denominator | quotient? |
| 10        | 2           | 5         |
| 12.6      | 3           | 4.2       |
```

and the entire fixture:

```java
public class Division extends ColumnFixture {
  public double numerator;
  public double denominator;
  public double quotient() { return numerator / denominator; }
}
```

Three fixture types cover three test shapes: **ColumnFixture** (business rules: one row per case, inputs then expected outputs), **ActionFixture** (event sequences via a control-panel metaphor: `enter`/`press`/`check`), and **RowFixture** (set comparison against a query — fails on missing *or surplus* rows).

### The philosophy

- **"Examples", not "tests".** *"We really want these tests — or examples, I prefer to call them examples — we want these examples of how the program is supposed to behave to be sourced from the customer."* And: *"Don't tell us you want the interest rate formula — give us some examples of the interest rate formula that we can check... so that we can see how our understanding of interest calculation is different than yours."* (Hanselminutes #151)
- **A document that tells you whether it's true.** The HTML format was chosen so tables carry the facts and the surrounding prose carries the *why*: *"that left all the space around the tables to describe why you cared about those facts, and that made it a communication tool."* James Shore (Fit's project coordinator): *"A lot of people think of Fit and FitNesse as testing tools, but I think of them as customer communication tools."*
- **Meet the domain experts in their tools.** Tables because *"they all know how to work Excel"* — the customer decides how many columns an example needs.
- **Bypass the UI, talk to the domain.** *"I wanted to talk to the same application that the user interface talks to. So I bypass the user interface, talk straight to the application."* Acceptance tests hit the domain layer through the same interface the UI uses — which in turn *forces* a domain layer to exist. Shore: Fit "will drive the design of your domain layer" the way TDD drives decoupled objects.
- **Portability via dumb data.** Tests are "just HTML documents that have a bunch of facts expressed as strings and numbers," so teams could move Java → .NET → Ruby "and take all our tests along with us." Six language ports existed by mid-2005.

### The framework as a design artifact

The original Fit was "10 classes or something like that... not a very big framework, but more importantly it established a style of testing." Three core classes (Parse, Fixture, TypeAdapter); the entire HTML parser is ~199 lines. Michael Feathers devoted a *Beautiful Code* chapter to it ("Beauty Through Fragility"): its classes "maneuver in a path around nearly every rule of thumb about design in the Java community," and the beauty "is a consequence of it being small, useful, and understandable, yet open to change." The smallness is what made the ports — and the forks — possible.

### The book: *Fit for Developing Software* (Mugridge & Cunningham, 2005)

The book is explicitly two books in one — Parts I–II for the *nonprogramming customer*, Parts III–V for programmers — itself a statement about who owns acceptance tests. Beyond the framework mechanics, its craft guidance is the part that generalizes:

- **"Tests are for communicating ideas."** Chapter 18 ("Designing and Refactoring Tests to Communicate Ideas") names three principles of test design: **communication** (business language, one business rule per test, organized for readers), **adaptability** (don't overcommit to nonessential details; avoid redundancy so tests can evolve), and **automation** (independent, self-sufficient, consistent — no intermittent passes). It applies refactoring vocabulary to tests: smells are "indications that there is trouble that can be solved by refactoring."
- **Transform workflow tests into calculation tests** (ch. 16): "After writing several related workflow tests, we see an underlying pattern… We end up collapsing a large number of workflow tests into a few tables of calculation tests… by cutting to the essential nature of the underlying business rules." Script-shaped tests are a smell; the business rule wants to be a table.
- **Fixtures are thin bridges; tests "test-infect" the architecture.** Chapters 30–33 (incl. "Restructuring the System for Testing" and a section titled "Test Infecting for Improvements") diagnose business logic in GUI event handlers as the obstacle and use Fit's pressure to force out a domain layer tested under the UI.
- **Storytest-driven development** (ch. 17): write the Fit tests before the code — "The tests help to define the requirements and are used to determine whether a story is implemented completely," and beat GUI mockups for cheap feedback.
- **Better table vocabularies reduce glue**: Mugridge's FitLibrary (DoFixture for flow-style tables that read like sentences, SetUpFixture to reach state "without lengthy workflow actions", CalculateFixture) exists to keep tables business-shaped while fixture code shrinks.

### The honest post-mortem

Ward participated in Fit's own reckoning (Hanselminutes #151, 2009). His failed assumption: *"I just assumed... people could write documents that had tables in them and maintain them... It turns out that producing a document that has tables with a bunch of facts and strings and numbers turns out to be hard... And if you can't write the language freely, then saying that we're going to have a communication tool that's based on this language is just dreaming."* Shore's 2010 follow-up ("The Problems With Acceptance Testing"): customers wouldn't write the tests and didn't trust tests written for them; test writing devolved to testers; the suites grew slow and brittle. What survived: customer-**sourced** examples informing TDD, frequent customer review — the communication, minus the tool. And the lineage: FitNesse, Cucumber (*"those wouldn't exist if it weren't for Fit kind of saying, here's a space and here's something to do"*), Selenium (*"I think Selenium actually was inspired by Fit"*), Specification by Example.

**Lesson**: Tests are examples first and a communication medium second; verification is third. Concrete examples flush out ambiguity that requirements prose hides — and when examples are fuzzy, "programmers fill in the gaps with their expectations" (Shore). Write acceptance tests against the domain layer, never through the UI. And the sobering part: customer-*authored* tests failed in practice; customer-*sourced* examples are the durable residue.

## CHECKS — Validation as Domain Design, Not Defensive Code (1994)

Ward's CHECKS pattern language (PLoP 1994, from the WyCash Smalltalk work): *"Any program that accepts user input will need to separate good input from bad... This pattern language tells how to make these checks without complicating the program and compromising future flexibility."* Ten patterns in three sections:

**Domain values**: **Whole Value** (model quantities as first-class objects — currency, dates — because "bits, strings and numbers can be used to represent almost anything, any one in isolation means almost nothing"; ancestor of Value Object and of Fowler's Money), **Exceptional Value** (distinguished values for missing/inapplicable data, legal in the model "at least temporarily"; forerunner of Null Object), **Meaningless Behavior** (*"Write methods without concern for possible failure. Expect the input/output widgits that initiate computation to recover from failure and continue processing"* — with Ward's later clarification: this "is not about writing error handlers. It is about writing domain methods in the presence of diversity").

**Feedback during entry**: **Echo Back** (immediately display the system's *interpretation* of what was entered — feedback instead of interruption), **Visible Implication** (show derived quantities alongside entries), **Deferred Validation** (*"Delay detailed validation of a domain model until an action is requested. Tailor the extent of the validation to the specific action"* — saving a draft needs less checking than publishing), **Instant Projection**, **Hypothetical Publication** (try consequences tentatively, clearly marked, before committing).

**Long-term integrity**: **Forecast Confirmation** (mechanically-generated entries get confirmed when reality arrives), **Diagnostic Query** (*"Make every display that rounds or summarizes offer the unprocessed values for inspection"* — every number auditable back to who entered what, when).

In 2014–2022 Ward re-published CHECKS on a federated wiki (checks.fed.wiki.org, the "Information Integrity" site) with new commentary. The notable addition, **"Curing the Vulnerable Parser"** (2017), connects CHECKS to language-theoretic security: *"Programs are full of parsers. Any program statement that touches input may, in fact, do parsing. When inputs are hostile, ad hoc input handling code is notoriously vulnerable."* — hardened parsing "at every process boundary." His 1994 input-validation language, reframed as an ancestor of langsec.

**Lesson**: Push integrity into types (Whole Value) instead of scattering defensive checks through domain logic; validate at the moment an *action* demands it, with intensity proportional to the action's consequence; make every displayed value traceable to its source. For testing, CHECKS is the design that makes validation *testable*: whole values and deferred validation concentrate the checking into objects and choke points you can test directly, instead of smearing it across every method. And input handling is a security surface — test the parser at every boundary.

## The GitHub Evidence: Test the Asset, Not the Experiment

Across 156 personal repos plus the fedwiki org, the pattern is unmistakable: throwaway probes (Txtzyme, ddd, remodeling — 924★ and zero tests, sudokuku, morse) have **no test directories at all**, while reusable abstractions get genuine suites. This isn't neglect, it's policy — remodeling's README: "we will focus on simple implementation with minimum dependencies requiring the least attention in years ahead." Test investment tracks expected lifetime.

### graph (2022) — TDD to grow an interface

When the artifact is a library, Ward test-drives it. `test/graph.test.js` opens with the comment "Graph tests for evolving interface gradually":

```js
Deno.test("Adding One Node Yields Size One", () => {
  const g = new Graph();
  g.addNode('SampleNodeType')
  assertEquals(g.size(), 1);
```

The commit log is TDD-in-the-small, diffs mostly under 40 lines: "A stub test for TDD of copy" → "functional test for enhancement" → "Refactor by moving the recursive copy to the Graph abstraction" → "better tests of copy".

### wiki-client — a domain DSL inside the test suite, and tests for the helpers

Ward's 2014 commit "replace test json with helpers that make better tests" built a one-letter DSL for wiki journal actions so revision-merge cases read like `'c312'`, `'a31'`, `'m1321'` — and then he wrote tests *for the helpers themselves* before using them:

```js
describe('testing helpers', () =>
  it('should make move actions', () =>
    expect(action('m1321')).to.eql({ type: 'move', id: '10', order: ['30', '20', '10'] })))
```

The same instinct that produced Fit tables twenty years earlier: compress test cases into the domain's own notation so a complicated shuffle is legible at a glance ("more test cases for a complicated shuffle" is a real commit message).

### wiki-server — real collaborators, visible state

The server tests boot the actual server on a port, drive the real HTTP wire protocol with supertest, then assert against **the JSON page file on disk**:

```js
await request.put('/page/adsf-test-page/action')
  .send('action=' + body).expect(200)
  .then(() => {
    const page = JSON.parse(fs.readFileSync(loc))
    assert.equal(page.story[1].id, 'a3')
```

No mock framework in sight; where a fake is needed (wiki-client's `mockServer.js`) it's ~20 lines of sinon. His current project, wiki-plugin-mech (2024–26), runs `c8 -r lcov node --test` for coverage and uses a ~60-line hand-rolled fake `api` object that *logs effects into an array* — assertions read the log. The suites themselves migrated from grunt/mocha/CoffeeScript to Node's built-in `node --test`: the harness kept as small as the code.

### sudokuku — characterization over a population

For algorithm research, Ward doesn't write assertions; he classifies behavior. `1000-sudokus.sh` runs the solver over 1,000 real puzzles and histograms the behavior signatures (`sort | uniq -c | sort -n`), with a companion script to *retrieve* puzzles matching a rare signature (commit: "find rare cases"). Exploratory testing of a behavior distribution, not example tests.

### The honest commits

Smallest-Federated-Wiki's spec/ shows him gluing test worlds together with the simplest thing that could possibly work — RSpec driving Selenium to load the in-browser mocha suite and scrape its HTML reporter, pausing for a human on failure — and then the commit sequence: "run mocha tests from selenium integration tests" (2012-04-10), "report failing test titles from mocha in rspec" (2012-04-12), **"struggling with mocha, giving up" (2012-05-09)**. Abandoning a test approach that costs more than it returns is a recorded, legitimate outcome. Also notable: in fedwiki core the testing culture is *federated* — Paul Rodwell authored 31 of the wiki-server test commits and modernized the harnesses, while Ward writes tests where he's actively designing (28 test commits in wiki-client). The 367★ `wiki` package itself has no tests at all — it's pure assembly of tested parts, and gets only lint.

**Lesson**: Calibrate test investment to code lifetime — zero for probes, TDD for abstractions, characterization harnesses for algorithm research. Prefer real collaborators and visible state (real server, real file on disk, logging fakes) over mock frameworks. Build small domain DSLs inside test suites and test the helpers themselves. And record your testing failures in the commit log.

## Technical Debt: Tests Are What Make Debt Repayable

The debt metaphor (OOPSLA '92 experience report on WyCash) is usually quoted without its load-bearing precondition. The 1992 text: *"Shipping first time code is like going into debt. A little debt speeds development so long as it is paid back promptly with a rewrite... Every minute spent on not-quite-right code counts as interest on that debt."* The 2009 video transcript (CC-BY, wiki.c2.com/?WardExplainsDebtMetaphor) adds the two clauses everyone drops:

- *"I'm never in favor of writing code poorly, but I am in favor of writing code to reflect your current understanding of a problem even if that understanding is partial."*
- *"The ability to pay back debt... depends upon your writing code that is clean enough to be able to refactor as you come to understand your problem."* Otherwise *"the interest is total — you'll make zero progress."*

The transcript never mentions tests directly — but the repayment mechanism is refactoring, and (per XP, which he calls the metaphor "one of many explanations why" it works) the test suite is what makes repayment-by-refactoring safe. Debt without tests is debt with no means of repayment.

## The Worldview: Cheapen Mistakes Instead of Guessing Right

The deepest Cunningham principle, stated in the Artima interviews: *"The right thing might be to eliminate the cost of making a mistake rather than try to guess what's right."* And: *"I tackled that curve by saying, let's almost intentionally make mistakes so we can practice correcting them. That practice will help reduce the cost of making changes late."*

This is one idea wearing many costumes:

- **Wiki**: the Tolerant design principle (wiki.c2.com/?WikiDesignPrinciples, signed by Ward): *"Interpretable (even if undesirable) behavior is preferred to error messages"* — plus Open (anyone can edit) and Observable (anyone can review). Don't prevent the error; make it visible and cheap to fix. ("Cunningham's Law" — post the wrong answer to get the right one — was coined *about* him by Steven McGeady; Ward disowns it as "a misquote that disproves itself by propagating through the internet.")
- **CHECKS**: Echo Back and Meaningless Behavior — absorb questionable input, show your interpretation, keep going.
- **"The simplest thing that could possibly work"**: originally a *question* he asked Kent while pairing, with a built-in evaluation step — *"the advice got turned into a command... that's a little more confusing, because there isn't this notion that as soon as you've done it, we'll evaluate it."* The phrase only works inside a feedback loop, and on the c2 wiki the loop is concrete: "your tests will run, or they won't."
- **Debt**: ship partial understanding, refactor when understanding improves.

Tests, in this worldview, aren't primarily a gate against error — they're the mechanism that makes error *recoverable*: fast detection plus cheap correction beats upfront prevention.

## EPISODES — The Test Suite as a First-Class Asset (1995)

A year before C3, Ward's EPISODES pattern language (PLoP 2, c2.com/ppr/episodes.html) sketched the XP testing toolchain in embryo: **Reference Data** (*"Collect examples, test cases and customer data as machine readable examples... Check the program against this data throughout development"* — proto-acceptance-testing), **Test Suite Repository** (*"Preserve and protect as if it were code"*), **Test Suite Browser** (drill from build statistics down to failures; *"Visualize failure distributions (systematic vs. sporadic)"*), **Test Fixture** (*"Long term fixture maintenance is a development responsibility"* — not QA's), and **Developmental Build** (run regression tests every build).

**Lesson**: The test suite is versioned, protected, owned-by-developers infrastructure — stated in 1995, before JUnit existed.

## Key Insights

1. **Tests are examples first, communication second, verification third.** "Give us some examples of the interest rate formula that we can check" — concrete examples flush out the ambiguity prose hides (Fit).
2. **Customer-authored failed; customer-sourced survived.** People who know the domain won't maintain test documents, but their concrete examples are the most valuable test input you can get. Build the suite from them.
3. **Acceptance-test the domain layer, never the UI.** "Bypass the user interface, talk straight to the application" — and let that pressure force a domain layer into existence.
4. **A test framework should be the simplest thing that could possibly work.** Three classes and a 199-line parser established a style of testing and seeded ports, forks, and successors (FitNesse, Cucumber, Selenium).
5. **Push validation into the design, not the code paths.** Whole Values, Deferred Validation tailored to the action's consequence, Meaningless Behavior in domain methods, every displayed number auditable (CHECKS). Concentrated validation is testable validation.
6. **Input handling is a security surface.** Ward's own 2017 update reframes CHECKS as langsec: hardened parsers at every process boundary (Curing the Vulnerable Parser).
7. **Calibrate test investment to code lifetime.** Zero tests for throwaway probes, TDD for reusable abstractions ("evolving interface gradually"), population-level characterization harnesses for algorithm research (sudokuku's 1,000-puzzle histogram).
8. **Make tests speak the domain — and test the helpers.** The `'m1321'` journal-action DSL in wiki-client, with `describe('testing helpers', ...)` validating the DSL itself, is Fit's table instinct applied to unit tests.
9. **Prefer real collaborators and visible state over mock frameworks.** Boot the real server, read the real file from disk, hand-roll a 60-line logging fake when you must fake at all.
10. **Debt is only repayable with tests.** "Never in favor of writing code poorly" — the metaphor's precondition is code "clean enough to be able to refactor," and the suite is what makes that refactoring safe.
11. **Eliminate the cost of mistakes rather than guess what's right.** Wiki's Tolerant/Observable principles, Echo Back, and "simplest thing" + evaluation are all the same move: optimize the feedback-and-correction loop, not the prevention gate.
12. **The test suite is a protected, developer-owned asset.** "Preserve and protect as if it were code"; "long term fixture maintenance is a development responsibility" (EPISODES, 1995).
