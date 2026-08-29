# Assessment: the teammate is over-applying the DAMP guidance

DAMP ("descriptive and meaningful phrases") is about keeping *behavior*
visible in each test: no logic in test bodies, no computed expectations, no
fixtures mutated far from the assertions they feed. It is not a ban on
helpers.

`ArticleFactory` is the sanctioned kind of DRY in test code — a
value-construction builder. Every field the assertions actually depend on is
set explicitly at the call site (`status="draft"` vs `status="published"`),
and the fields the test does *not* care about (title, counter-based id) are
defaulted away as noise. That is exactly what makes
`test_draft_articles_not_in_feed` readable: the one relevant difference
between the two articles is visible in one line each.

Inlining the full article dicts into all eleven tests would bury that
relevant field in identical boilerplate, and future schema additions would
mean editing eleven literals instead of one default.

## What I would change

- **Keep the factory.** It already follows the rule that matters: tests never
  rely on a builder default for a field their assertions depend on.
- One small tightening: the assertions use `draft["id"]`, which comes from
  the factory's counter. Since the id is asserted on, set it explicitly where
  asserted (`ArticleFactory.create(id="art_draft", status="draft")`) so no
  asserted value originates inside the helper.
- If any test ever needs branching or computation inside the factory to
  produce an *expected* value, that is the point at which DAMP says stop.

So: the teammate is mistaken about the fix, but the underlying instinct —
"nothing the assertion depends on should hide in a helper" — is worth
enforcing, and the one place this file falls short of it is the id.
