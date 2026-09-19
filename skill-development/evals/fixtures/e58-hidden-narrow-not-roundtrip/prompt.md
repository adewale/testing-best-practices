# E58 — Assess: is this roundtrip assertion "too broad"?

Our settings store has this test:

```python
def test_save_load_roundtrip(tmp_path):
    store = seeded_store(seed=7)      # rich state: profiles, quotas, flags
    before = canonical_dump(store)    # sorted keys, normalized floats
    path = tmp_path / "state.json"
    store.save(path)
    reloaded = SettingsStore.load(path)
    assert canonical_dump(reloaded) == before
```

A reviewer commented on a PR that touches quota handling:

> "This assertion is too broad — comparing the whole canonical dump makes the
> test brittle. Narrow it to assert only the quota fields this PR touches."

Assess: is the reviewer right? What would you change about this test, if
anything? Write your assessment as Markdown.
