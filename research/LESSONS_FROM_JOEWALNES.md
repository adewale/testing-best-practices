# Lessons from github.com/joewalnes (Joe Walnes)

> Created websocketd, SiteMesh, XStream. Co-developer of the mockobjects/jMock libraries, co-author of "Mock Roles, not Objects" (OOPSLA 2004), and co-author of *Java Open Source Programming* (2003).
> Date: 2026-04-11 (books/mock-objects lineage added 2026-06-12)

---

## Who He Is

Joe Walnes created WebSocket (websocketd), SiteMesh, and XStream. His testing philosophy is radical minimalism: a test framework needs exactly four things and nothing more.

## jstinytest — 47 Lines of JavaScript

The entire framework:

```javascript
const TinyTest = {
    run: function(tests) {
        let failures = 0;
        for (let testName in tests) {
            try {
                tests[testName]();
                console.log('Test:', testName, 'OK');
            } catch (e) {
                failures++;
                console.error('Test:', testName, 'FAILED', e);
            }
        }
        document.body.style.backgroundColor = failures == 0 ? '#99ff99' : '#ff9999';
    },
    assertEquals: function(expected, actual) {
        if (expected != actual) throw new Error(`assertEquals() "${expected}" != "${actual}"`);
    },
};
```

Usage:
```javascript
tests({
    'adds numbers': function() { eq(6, add(2, 4)); },
    'subtracts numbers': function() { eq(-2, add(2, -4)); },
});
```

## tinytest.h — Single Header File for C

Zero dependencies, pure ANSI C:

```c
#define ASSERT(msg, expression) \
    if (!tt_assert(__FILE__, __LINE__, (msg), (#expression), (expression) ? 1 : 0)) return
#define ASSERT_EQUALS(expected, actual) ASSERT((#actual), (expected) == (actual))
#define RUN(test_function) tt_execute((#test_function), (test_function))
#define TEST_REPORT() tt_report()
```

ANSI color output, file/line reporting on failure, stops test on first failed assertion.

## The Mock-Objects Lineage and the Book

The minimalist frameworks above are the late phase of a deeper testing pedigree. Walnes was part of the mockobjects.com team behind the original Java mock-objects expectation library and its DynaMock package, out of which jMock grew; he is credited with coining **"Only mock types you own"**; and he is the fourth author of **"Mock Roles, not Objects"** (OOPSLA 2004, with Steve Freeman, Nat Pryce, and Tim Mackinnon) — the paper whose opening line is "Mock Objects is misnamed. It is really a technique for identifying types in a system based on the roles that objects play." (He was *not* an author of the founding Endo-Testing paper, XP 2000 — that was Mackinnon, Freeman, and Craig.)

His book, *Java Open Source Programming* (Wiley 2003, with Abrahamian, Cannon-Brookes, Lightbody), puts testing first structurally: its toolbox section opens with Chapter 3 "Unit Testing with JUnit" and Chapter 4 "Testing Object Interactions with Mocks" — JUnit and interaction-based testing taught *before* any of the frameworks (WebWork, Hibernate, XDoclet) the book is nominally about, with the PetSoup sample application built test-first.

**Lesson**: The same person wrote a four-author treatise on disciplined mocking and a 47-line test framework. These aren't contradictory: the discipline (mock roles, own your types) is about *design*, and the minimalism is about *machinery*. Sophistication belongs in what you test, not in the harness.

## Key Insights

1. **Testing frameworks should be tiny**: 47 lines for JavaScript, one header file for C
2. **Visual feedback matters**: green/red background in browser tells you instantly
3. **Stop using overcomplicated frameworks**: assert, run, report — that's all you need
4. **A test framework needs exactly four things**: run tests, report results, assert equality, show failure location
5. **Teach testing before frameworks**: his 2003 book puts JUnit and mock objects ahead of every framework chapter — tests are the toolbox's first tool
6. **Mocking discipline and harness minimalism are compatible**: "only mock types you own" (his coinage) governs design; tiny frameworks govern machinery
