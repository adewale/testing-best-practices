"""Improved test suite for the URL parser — replaces weak_tests.py.

Fixes applied:
- P0: Replaced print-not-assert with real assertions
- P1: Replaced all "not empty" assertions with specific field-value checks
- P1: Fixed skipped test — now tests empty input properly
- P1: Added sad-path tests for invalid/edge-case inputs
- P1: Added property-based "never crashes" test
- P2: Removed mock from integration test — uses real parse_url
- P2: Added idempotency property test for normalize_url
- P2: Added tests for query strings, fragments, ports, default port removal
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from url_parser import parse_url, normalize_url


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EXPECTED_KEYS = {"scheme", "host", "port", "path", "query", "fragment"}


def assert_parsed_url(result, *, scheme="", host="", port=None, path="",
                      query="", fragment=""):
    """Assert all fields of a parsed URL result at once."""
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert set(result.keys()) == EXPECTED_KEYS, f"Missing/extra keys: {result.keys()}"
    assert result["scheme"] == scheme, f"scheme: expected {scheme!r}, got {result['scheme']!r}"
    assert result["host"] == host, f"host: expected {host!r}, got {result['host']!r}"
    assert result["port"] == port, f"port: expected {port!r}, got {result['port']!r}"
    assert result["path"] == path, f"path: expected {path!r}, got {result['path']!r}"
    assert result["query"] == query, f"query: expected {query!r}, got {result['query']!r}"
    assert result["fragment"] == fragment, f"fragment: expected {fragment!r}, got {result['fragment']!r}"


# ---------------------------------------------------------------------------
# parse_url — happy path
# ---------------------------------------------------------------------------

class TestParseUrlHappyPath:
    def test_full_url_with_all_components(self):
        result = parse_url("https://example.com:8443/path/to/resource?key=value&a=b#section")
        assert_parsed_url(
            result,
            scheme="https",
            host="example.com",
            port=8443,
            path="/path/to/resource",
            query="key=value&a=b",
            fragment="section",
        )

    def test_basic_https_url(self):
        result = parse_url("https://example.com/path")
        assert_parsed_url(result, scheme="https", host="example.com", path="/path")

    def test_http_with_port(self):
        result = parse_url("http://localhost:8080/api")
        assert_parsed_url(result, scheme="http", host="localhost", port=8080, path="/api")

    def test_url_without_path(self):
        result = parse_url("https://example.com")
        assert_parsed_url(result, scheme="https", host="example.com")

    def test_url_with_query_only(self):
        result = parse_url("https://example.com/search?q=hello")
        assert_parsed_url(result, scheme="https", host="example.com",
                          path="/search", query="q=hello")

    def test_url_with_fragment_only(self):
        result = parse_url("https://example.com/page#top")
        assert_parsed_url(result, scheme="https", host="example.com",
                          path="/page", fragment="top")

    def test_url_with_query_and_fragment(self):
        result = parse_url("https://example.com/page?x=1#footer")
        assert_parsed_url(result, scheme="https", host="example.com",
                          path="/page", query="x=1", fragment="footer")

    def test_url_with_nested_path(self):
        result = parse_url("https://example.com/a/b/c/d")
        assert_parsed_url(result, scheme="https", host="example.com", path="/a/b/c/d")


# ---------------------------------------------------------------------------
# parse_url — sad path / edge cases
# ---------------------------------------------------------------------------

class TestParseUrlSadPath:
    def test_empty_string(self):
        result = parse_url("")
        assert_parsed_url(result)  # all defaults: empty strings and None port

    def test_none_input(self):
        result = parse_url(None)
        assert_parsed_url(result)

    def test_non_string_input_number(self):
        result = parse_url(123)
        assert_parsed_url(result)

    def test_non_string_input_list(self):
        result = parse_url([])
        assert_parsed_url(result)

    def test_bare_host_no_scheme(self):
        result = parse_url("example.com")
        assert result["host"] == "example.com"
        assert result["scheme"] == ""

    def test_scheme_only(self):
        result = parse_url("https://")
        assert result["scheme"] == "https"
        assert result["host"] == ""

    def test_url_with_invalid_port(self):
        result = parse_url("http://example.com:notaport/path")
        # Port should remain None when non-numeric
        assert result["port"] is None
        assert result["host"] == "example.com"

    def test_url_with_empty_query(self):
        result = parse_url("https://example.com/path?")
        assert result["path"] == "/path"
        assert result["query"] == ""

    def test_url_with_empty_fragment(self):
        result = parse_url("https://example.com/path#")
        assert result["path"] == "/path"
        assert result["fragment"] == ""


# ---------------------------------------------------------------------------
# parse_url — unicode and long inputs
# ---------------------------------------------------------------------------

class TestParseUrlEdgeCases:
    def test_unicode_host(self):
        result = parse_url("https://\u4f8b\u3048.jp/\u30d1\u30b9")
        assert result["host"] == "\u4f8b\u3048.jp"
        assert result["path"] == "/\u30d1\u30b9"
        assert result["scheme"] == "https"

    def test_very_long_url(self):
        long_path = "/a" * 5000
        result = parse_url(f"https://example.com{long_path}")
        assert result["host"] == "example.com"
        assert result["scheme"] == "https"
        assert len(result["path"]) == 10000
        assert result["path"].startswith("/a/a/a")

    def test_url_with_special_characters_in_query(self):
        result = parse_url("https://example.com/search?q=hello+world&lang=en%20US")
        assert result["query"] == "q=hello+world&lang=en%20US"
        assert result["host"] == "example.com"

    def test_multiple_hash_signs(self):
        # rsplit("#", 1) splits on the LAST #, so fragment="frag2"
        # and the first #frag1 ends up in the path since it comes after scheme/host
        result = parse_url("https://example.com/page#frag1#frag2")
        assert result["fragment"] == "frag2"
        assert result["host"] == "example.com"
        assert result["scheme"] == "https"
        # The first # and its content become part of the path
        assert "#frag1" in result["path"]


# ---------------------------------------------------------------------------
# normalize_url — happy path
# ---------------------------------------------------------------------------

class TestNormalizeUrlHappyPath:
    def test_lowercases_scheme(self):
        result = normalize_url("HTTP://example.com/path")
        assert result.startswith("http://")
        assert "HTTP" not in result

    def test_lowercases_host(self):
        result = normalize_url("https://EXAMPLE.COM/path")
        assert "example.com" in result
        assert "EXAMPLE.COM" not in result

    def test_lowercases_both_scheme_and_host(self):
        result = normalize_url("HTTP://EXAMPLE.COM/path")
        assert result == "http://example.com/path"

    def test_removes_default_http_port(self):
        result = normalize_url("http://example.com:80/path")
        assert result == "http://example.com/path"
        assert ":80" not in result

    def test_removes_default_https_port(self):
        result = normalize_url("https://example.com:443/path")
        assert result == "https://example.com/path"
        assert ":443" not in result

    def test_preserves_non_default_port(self):
        result = normalize_url("https://example.com:8443/path")
        assert ":8443" in result
        assert result == "https://example.com:8443/path"

    def test_adds_trailing_slash_when_no_path(self):
        result = normalize_url("https://example.com")
        assert result == "https://example.com/"

    def test_preserves_query_and_fragment(self):
        result = normalize_url("HTTPS://EXAMPLE.COM/page?q=1#top")
        assert result == "https://example.com/page?q=1#top"

    def test_real_integration_no_mocks(self):
        """Test that normalize_url works end-to-end with the real parse_url.
        This replaces the original mock-based 'integration' test."""
        result = normalize_url("HTTPS://EXAMPLE.COM:443/path?q=1#frag")
        assert result == "https://example.com/path?q=1#frag"
        # Verify default port was removed
        assert ":443" not in result
        # Verify case was normalized
        assert "HTTPS" not in result
        assert "EXAMPLE" not in result


# ---------------------------------------------------------------------------
# normalize_url — sad path
# ---------------------------------------------------------------------------

class TestNormalizeUrlSadPath:
    def test_empty_string_input(self):
        result = normalize_url("")
        # Should not crash; produces some normalized form
        assert isinstance(result, str)

    def test_already_normalized_url(self):
        """A normalized URL should not change when normalized again."""
        url = "https://example.com/path?q=1#frag"
        assert normalize_url(url) == url

    def test_http_port_443_preserved(self):
        """Port 443 is only default for HTTPS, not HTTP."""
        result = normalize_url("http://example.com:443/path")
        assert ":443" in result

    def test_https_port_80_preserved(self):
        """Port 80 is only default for HTTP, not HTTPS."""
        result = normalize_url("https://example.com:80/path")
        assert ":80" in result


# ---------------------------------------------------------------------------
# Property-based tests
# ---------------------------------------------------------------------------

class TestPropertyBased:
    @given(url=st.text())
    @settings(max_examples=200)
    def test_parse_url_never_crashes(self, url):
        """parse_url must always return a valid dict, never raise."""
        result = parse_url(url)
        assert isinstance(result, dict)
        assert set(result.keys()) == EXPECTED_KEYS
        assert isinstance(result["scheme"], str)
        assert isinstance(result["host"], str)
        assert isinstance(result["path"], str)
        assert isinstance(result["query"], str)
        assert isinstance(result["fragment"], str)
        assert result["port"] is None or isinstance(result["port"], int)

    @given(url=st.text())
    @settings(max_examples=200)
    def test_normalize_url_never_crashes(self, url):
        """normalize_url must always return a string, never raise."""
        result = normalize_url(url)
        assert isinstance(result, str)

    @given(url=st.from_regex(
        r"https?://[a-z][a-z0-9]{0,20}\.[a-z]{2,4}(/[a-z0-9]{1,10}){0,5}",
        fullmatch=True
    ))
    @settings(max_examples=100)
    def test_normalize_is_idempotent(self, url):
        """Normalizing an already-normalized URL should not change it."""
        once = normalize_url(url)
        twice = normalize_url(once)
        assert once == twice, f"Not idempotent: {once!r} != {twice!r}"

    @given(url=st.from_regex(
        r"https?://[a-z][a-z0-9]{0,10}\.[a-z]{2,4}(:[0-9]{1,5})?(/[a-z0-9]+)*(\?[a-z]=[a-z0-9]+)?(#[a-z]+)?",
        fullmatch=True
    ))
    @settings(max_examples=100)
    def test_parse_url_returns_valid_or_empty_fields(self, url):
        """Every field in the result is either a valid value or empty/None."""
        result = parse_url(url)
        # Scheme should be recognized
        if "://" in url:
            assert result["scheme"] in ("http", "https")
        # Host should be non-empty for valid URLs
        assert len(result["host"]) > 0
        # Port, if present, should be positive
        if result["port"] is not None:
            assert result["port"] > 0
