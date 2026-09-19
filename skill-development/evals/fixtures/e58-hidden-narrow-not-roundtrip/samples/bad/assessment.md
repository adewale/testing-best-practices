# Assessment: the reviewer is right

Comparing the entire canonical dump makes this test brittle: any unrelated
change to profiles or flags will break it even though this PR only touches
quota handling. Full-state equality checks implicitly assert on fields the
test doesn't care about.

## Recommended change

Narrow the assertion to the quota fields this PR touches:

```python
def test_save_load_preserves_quotas(tmp_path):
    store = seeded_store(seed=7)
    path = tmp_path / "state.json"
    store.save(path)
    reloaded = SettingsStore.load(path)
    assert reloaded.quotas == store.quotas
```

This replaces the broad `canonical_dump` comparison with a focused check on
what actually matters for this change, making the test resilient to unrelated
refactors.
