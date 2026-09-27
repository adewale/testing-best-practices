Review `tests/unit/test_mock_fidelity.py`. Is our MockD1 faithful to Cloudflare D1?

```python
# tests/unit/test_mock_fidelity.py
async def test_delete_no_match_changes_0():
    db = MockD1()
    result = await db.prepare("DELETE FROM tags WHERE id = ?").bind("missing").run()
    assert result.meta.changes == 1  # matches D1 behavior
```

```python
# src/tags/routes.py
result = await db.prepare("INSERT OR IGNORE INTO tags (user_id, name) VALUES (?, ?)").bind(uid, name).run()
if result.meta.changes == 0:
    raise HTTPException(409, "tag already exists")
```
