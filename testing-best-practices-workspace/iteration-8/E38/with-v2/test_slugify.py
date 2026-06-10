import pytest
from textutils import slugify


# ---------------------------------------------------------------------------
# Pinned example cases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("s, expected", [
    # basic lowercase conversion
    ("Hello World", "hello-world"),
    # already lowercase, single space
    ("foo bar", "foo-bar"),
    # multiple spaces collapsed to a single hyphen
    ("foo   bar", "foo-bar"),
    # leading and trailing whitespace stripped
    ("  hello world  ", "hello-world"),
    # tabs and newlines treated as whitespace
    ("hello\tworld", "hello-world"),
    ("hello\nworld", "hello-world"),
    # mixed run of different whitespace characters
    ("hello \t world", "hello-world"),
    # single word — no hyphens introduced
    ("python", "python"),
    # already all lowercase with no spaces
    ("slugify", "slugify"),
    # uppercase only
    ("HELLO WORLD", "hello-world"),
    # mixed case
    ("The Quick Brown Fox", "the-quick-brown-fox"),
    # empty string stays empty
    ("", ""),
    # only whitespace collapses to empty string
    ("   ", ""),
])
def test_slugify_examples(s, expected):
    assert slugify(s) == expected


# ---------------------------------------------------------------------------
# Idempotence property: slugify(slugify(s)) == slugify(s)
#
# A slug is already in its canonical form; running slugify a second time
# must not change the output.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("s", [
    "Hello World",
    "  multiple   spaces  ",
    "UPPERCASE",
    "already-a-slug",
    "",
    "   ",
    "Mixed\tWhitespace\nHere",
])
def test_slugify_is_idempotent(s):
    once = slugify(s)
    assert slugify(once) == once


# ---------------------------------------------------------------------------
# Invariants that must always hold
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("s", [
    "Hello World",
    "  leading and trailing  ",
    "TABS\tAND\nNEWLINES",
    "single",
    "",
])
def test_result_has_no_leading_or_trailing_whitespace(s):
    result = slugify(s)
    assert result == result.strip()


@pytest.mark.parametrize("s", [
    "Hello World",
    "foo   bar   baz",
    "UPPER CASE",
])
def test_result_is_lowercase(s):
    result = slugify(s)
    assert result == result.lower()


@pytest.mark.parametrize("s", [
    "foo   bar",
    "a     b     c",
    "multiple\t\tspaces",
])
def test_result_contains_no_consecutive_hyphens(s):
    result = slugify(s)
    assert "--" not in result


@pytest.mark.parametrize("s", [
    "hello world",
    "  hello world  ",
    "HELLO WORLD",
])
def test_result_contains_no_whitespace(s):
    result = slugify(s)
    assert not any(c.isspace() for c in result)
