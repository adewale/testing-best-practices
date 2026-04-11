# Characterization Testing

When working with legacy or unfamiliar code, write tests that capture what the
code *currently does* — not what you think it should do. These tests become a
safety net for refactoring.

## The process

1. Pick a function you need to change
2. Call it with various inputs
3. Record the actual outputs as assertions — even if they look wrong
4. Now you have a test that will break if your refactoring changes behavior
5. Refactor, keeping characterization tests green
6. After refactoring, decide which behaviors to keep and which to fix

## Example

```python
def test_characterize_process_name():
    # These record CURRENT behavior, not desired behavior
    assert process_name("Alice") == "ALICE"
    assert process_name("") == ""
    assert process_name(None) == "UNKNOWN"  # surprising, but that's what it does
    assert process_name("Bob Smith") == "BOB"  # truncates? bug? feature?
```

## Key insight (from Michael Feathers)

These tests are not about correctness — they're about *change detection*. If
you refactor and a characterization test breaks, you know you changed behavior.
Then you decide: was the old behavior a bug (update the test) or a feature
(fix the refactoring)?
