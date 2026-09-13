# Assessment: the teammate is right

Our readability guidance is clear that test code should be DAMP rather than
DRY, and the factory is a DRY abstraction: to know what an article looks
like, a reader has to leave the test and read `ArticleFactory.create`.

## Recommended change

Delete `ArticleFactory` and inline the article dicts as literals in every
test, so each test is self-contained:

```python
def test_draft_articles_not_in_feed():
    draft = {"id": "art_1", "title": "Test Article 1", "status": "draft"}
    published = {"id": "art_2", "title": "Test Article 2", "status": "published"}
    feed = build_feed([draft, published])
    assert published["id"] in feed.item_ids
    assert draft["id"] not in feed.item_ids
```

Apply the same inlining to the other ten tests. Duplication is acceptable in
test code; hiding setup in helpers is not.
