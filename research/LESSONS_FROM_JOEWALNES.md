# Lessons from github.com/joewalnes (Joe Walnes)

> Created the WebSocket protocol implementation, SiteMesh, XStream.
> Date: 2026-04-11

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

## Key Insights

1. **Testing frameworks should be tiny**: 47 lines for JavaScript, one header file for C
2. **Visual feedback matters**: green/red background in browser tells you instantly
3. **Stop using overcomplicated frameworks**: assert, run, report — that's all you need
4. **A test framework needs exactly four things**: run tests, report results, assert equality, show failure location
