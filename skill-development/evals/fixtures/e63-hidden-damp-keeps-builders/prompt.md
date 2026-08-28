# E63 — Assess: should this factory be inlined "for DAMP"?

Our feed tests look like this:

```python
class ArticleFactory:
    _counter = 0

    @classmethod
    def create(cls, **overrides):
        cls._counter += 1
        defaults = {
            "id": f"art_{cls._counter}",
            "title": f"Test Article {cls._counter}",
            "status": "published",
        }
        defaults.update(overrides)
        return defaults


def test_draft_articles_not_in_feed():
    draft = ArticleFactory.create(status="draft")
    published = ArticleFactory.create(status="published")
    feed = build_feed([draft, published])
    assert published["id"] in feed.item_ids
    assert draft["id"] not in feed.item_ids


def test_feed_orders_newest_first(): ...
# (nine more tests in the same style)
```

A teammate left this review comment:

> "Our new test-readability guidance says test code should be DAMP, not DRY —
> so we should delete `ArticleFactory` and inline the full article dicts as
> literals in every test. Helpers hide things."

Assess: is the teammate right? What would you change about these tests, if
anything? Write your assessment as Markdown.
