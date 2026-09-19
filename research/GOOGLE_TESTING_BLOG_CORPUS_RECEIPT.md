# Google Testing Blog corpus receipt

This is a lightweight provenance receipt for the archive metadata used by
[`LESSONS_FROM_GOOGLE_TESTING_BLOG.md`](LESSONS_FROM_GOOGLE_TESTING_BLOG.md).
It is not a crawler or a replacement for the missing raw analysis artifacts.

- Verified: 2026-09-19
- Source: `https://testing.googleblog.com/feeds/posts/default?alt=json&max-results=1`
- Feed-reported total posts: 404
- Analysis range: 2007-01-21 through 2026-07-21
- Latest feed entry at verification: “Prefactoring: More Impact, Less Work”
- Latest feed entry published: 2026-07-21
- Feed updated at verification: 2026-09-11

The metadata can be checked without downloading the corpus:

```bash
curl -sS -L \
  'https://testing.googleblog.com/feeds/posts/default?alt=json&max-results=1' \
  | jq '{total: .feed.openSearch$totalResults."$t", updated: .feed.updated."$t", latest: .feed.entry[0] | {title: .title."$t", published: .published."$t"}}'
```

## Evidence limit

The original plain-text download, ten analyst-batch outputs, and per-post
assessments were not retained in this repository. Consequently, the reported
216K-word count and full-reading process cannot be independently reproduced
from repository artifacts. Claims in the research note should be treated as a
documented historical analysis whose quotations and links can be checked at
their primary sources, not as a reproducible corpus pipeline.
