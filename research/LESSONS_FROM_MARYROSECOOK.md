# Lessons from github.com/maryrosecook (Mary Rose Cook)

> Creator of gitlet (Git in JavaScript), littlelisp, and annotated-code. Known for educational implementations with thorough tests.
> Date: 2026-04-11

---

## Who She Is

Mary Rose Cook builds educational implementations of complex systems (Git, Lisp) in JavaScript, accompanied by heavily annotated code and thorough test suites. Her testing approach: test the reimplementation the way users would interact with the real thing.

## gitlet — Git Reimplemented in JavaScript

A complete Git implementation in a single JavaScript file, tested with 19 spec files covering every major Git command: init, add, commit, branch, checkout, merge, clone, fetch, push, pull, diff, status, rm, remote, update-index, update-ref, write-tree.

### Testing Pattern: Command-Level Behavioral Tests

Each spec file tests a Git command the way a user would use it:

```javascript
describe("init", function() {
  beforeEach(testUtil.initTestDataDir);

  it("should create .gitlet/ and all required dirs", function() {
    g.init();
    expect(fs.existsSync(".gitlet/objects/")).toEqual(true);
    expect(fs.existsSync(".gitlet/refs/heads/")).toEqual(true);
    testUtil.expectFile(".gitlet/HEAD", "ref: refs/heads/master\n");
  });

  it("should not change anything if init run twice", function() {
    g.init();
    g.init();
    // Same assertions — idempotency test
  });
});
```

**Lesson**: Test at the user-facing API level (commands), not internal functions. Verify the filesystem state that users would observe.

### Testing Pattern: Real Filesystem with Pinned Time

```javascript
// test-util.js
beforeEach(testUtil.initTestDataDir);  // Fresh temp directory per test
beforeEach(testUtil.pinDate);          // Freeze time for deterministic commits
afterEach(testUtil.unpinDate);
```

Tests create real files, run real Git operations, and verify real filesystem state. Time is pinned so commit hashes are deterministic.

**Lesson**: For filesystem tools, test against the real filesystem. Pin non-deterministic inputs (time, randomness) rather than mocking the filesystem.

### Testing Pattern: File Tree Builder

```javascript
testUtil.createFilesFromTree({
  filea: "filea",
  fileb: "fileb",
  c1: { filec: "filec" },
  d1: { filed: "filed" },
  e1: { e2: { filee: "filee" }},
});
```

A recursive helper that creates directory structures from nested objects. Tests describe the file structure they need declaratively.

**Lesson**: Test data builders work for file trees too, not just database records. Describe the structure you need; let the helper create it.

### Testing Pattern: Verify Internal State via Same Abstraction

```javascript
// Don't read raw files to verify commit state — use the same API
testUtil.expectFile(".gitlet/refs/heads/master", "60986c94");
testUtil.headHash();  // Read HEAD through the same abstraction
```

### Testing Pattern: Multi-Repo Tests

For clone, fetch, push, pull — tests create multiple repos in the temp directory:

```javascript
testUtil.makeRemoteRepo();  // Creates repo2 alongside repo1
// Then tests clone/fetch/push between them
```

**Lesson**: Distributed system tests need multiple instances. Create them in isolated temp directories within the same test.

## littlelisp — Lisp Interpreter Tests

A tiny Lisp interpreter tested with Jasmine specs organized by language feature:

```javascript
describe('parse', function() {
  it('should lex a single atom', ...);
  it('should lex multi atom list', ...);
  it('should lex list containing list', ...);
});

describe('interpret', function() {
  describe('lists', ...);
  describe('atoms', ...);
  describe('lambdas', ...);
  describe('let', ...);
  describe('if', ...);
});
```

**Lesson**: For language implementations, organize tests by language construct (parsing, lists, atoms, lambdas, let, if). This maps directly to the specification.

### Annotation Helper for Test Clarity

```javascript
var unannotate = function(input) {
  // Strips type annotations from AST nodes for cleaner assertions
};
```

**Lesson**: Write test helpers that simplify assertions. `unannotate()` lets tests compare raw values instead of type-annotated AST nodes.

## Key Insights

1. **Test at the user-facing level**: gitlet tests Git commands, not internal functions
2. **Real filesystem, pinned time**: test against real I/O, but pin non-deterministic inputs
3. **File tree builders**: describe directory structures declaratively with nested objects
4. **Multi-instance testing**: distributed system tests create multiple repos/servers in temp directories
5. **Organize by feature/construct**: littlelisp tests are organized by language construct (parse, interpret, lambdas, let)
6. **Test helpers for assertion clarity**: `unannotate()`, `expectFile()`, `headHash()` — purpose-built helpers that simplify what tests assert on
