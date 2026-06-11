"""
Tests for textutils.slugify using differential testing.

Strategy: build a trivial reference implementation that is obviously correct
(a transparent one-liner), then drive both the reference and the real slugify
with the same inputs and assert they agree on every case.  Per the guidance,
we also include a data-driven conformance table (pirate-style) as the
specification anchor so failures produce immediately readable diagnostics.
"""

import re

import pytest

from textutils import slugify


# ---------------------------------------------------------------------------
# Reference (shadow) implementation — deliberately dumb, obviously correct
# ---------------------------------------------------------------------------

def _reference_slugify(s: str) -> str:
    """Canonical single-expression reference; trades elegance for obviousness."""
    return re.sub(r"\s+", "-", s.strip().lower())


# ---------------------------------------------------------------------------
# Conformance table — these cases ARE the specification
# ---------------------------------------------------------------------------

CASES = [
    # (input, expected_output)
    ("hello world",         "hello-world"),
    ("Hello World",         "hello-world"),
    ("  leading spaces",    "leading-spaces"),
    ("trailing spaces  ",   "trailing-spaces"),
    ("  both ends  ",       "both-ends"),
    ("multiple   spaces",   "multiple-spaces"),
    ("tabs\there",          "tabs-here"),
    ("newline\nhere",       "newline-here"),
    ("mixed \t \n ws",      "mixed-ws"),
    ("already-slugified",   "already-slugified"),
    ("ALLCAPS",             "allcaps"),
    ("MiXeD CaSe",          "mixed-case"),
    ("single",              "single"),
    ("",                    ""),
    ("   ",                 ""),
    ("a b",                 "a-b"),
]


# ---------------------------------------------------------------------------
# Conformance tests (pinned expected values — spec is the table above)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", CASES, ids=[c[0][:30] for c in CASES])
def test_conformance(text, expected):
    """slugify must match every pinned expected value in the spec table."""
    assert slugify(text) == expected


# ---------------------------------------------------------------------------
# Differential tests (reference is the oracle — no hand-written values needed)
# ---------------------------------------------------------------------------

# Superset of inputs: conformance cases plus a wider fuzz-free sample
DIFFERENTIAL_INPUTS = [text for text, _ in CASES] + [
    "foo  bar  baz",
    "  spaces on both  sides  ",
    "UPPER lower MiXeD",
    "one",
    "\t\ttabbed\t\t",
    "a  b  c  d",
    "already lower with-hyphen",
    "line1\nline2\nline3",
]


@pytest.mark.parametrize("text", DIFFERENTIAL_INPUTS)
def test_matches_reference(text):
    """slugify must agree with the reference implementation on every input."""
    assert slugify(text) == _reference_slugify(text)


# ---------------------------------------------------------------------------
# Roundtrip / idempotence (self-differential)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", DIFFERENTIAL_INPUTS)
def test_idempotent(text):
    """Applying slugify twice must produce the same result as applying it once.

    A slug contains no whitespace and is already lowercase, so a second pass
    must be a no-op.
    """
    once = slugify(text)
    assert slugify(once) == once
