"""Improved test suite for url_parser.parse_url and url_parser.normalize_url.

Each test targets a single, specific behavior and uses precise assertions
against expected field values.
"""

import pytest
from url_parser import parse_url, normalize_url


# ---------------------------------------------------------------------------
# parse_url: basic component extraction
# ---------------------------------------------------------------------------

class TestParseUrlScheme:
    def test_extracts_https_scheme(self):
        result = parse_url("https://example.com/path")
        assert result["scheme"] == "https"

    def test_extracts_http_scheme(self):
        result = parse_url("http://example.com/path")
        assert result["scheme"] == "http"

    def test_scheme_is_empty_when_missing(self):
        result = parse_url("example.com/path")
        assert result["scheme"] == ""


class TestParseUrlHost:
    def test_extracts_host(self):
        result = parse_url("https://example.com/path")
        assert result["host"] == "example.com"

    def test_extracts_host_without_path(self):
        result = parse_url("https://example.com")
        assert result["host"] == "example.com"

    def test_extracts_localhost(self):
        result = parse_url("http://localhost:8080/api")
        assert result["host"] == "localhost"


class TestParseUrlPort:
    def test_extracts_numeric_port(self):
        result = parse_url("http://localhost:8080/api")
        assert result["port"] == 8080

    def test_port_is_none_when_absent(self):
        result = parse_url("https://example.com/path")
        assert result["port"] is None

    def test_non_numeric_port_is_ignored(self):
        result = parse_url("https://example.com:abc/path")
        assert result["port"] is None
        # Host should still be extracted correctly despite the bad port.
        assert result["host"] == "example.com"


class TestParseUrlPath:
    def test_extracts_simple_path(self):
        result = parse_url("https://example.com/path")
        assert result["path"] == "/path"

    def test_extracts_nested_path(self):
        result = parse_url("https://example.com/a/b/c")
        assert result["path"] == "/a/b/c"

    def test_path_is_empty_when_missing(self):
        result = parse_url("https://example.com")
        assert result["path"] == ""


class TestParseUrlQuery:
    def test_extracts_query_string(self):
        result = parse_url("https://example.com/search?q=hello&lang=en")
        assert result["query"] == "q=hello&lang=en"

    def test_query_is_empty_when_missing(self):
        result = parse_url("https://example.com/path")
        assert result["query"] == ""

    def test_query_without_path(self):
        result = parse_url("https://example.com?q=test")
        assert result["query"] == "q=test"


class TestParseUrlFragment:
    def test_extracts_fragment(self):
        result = parse_url("https://example.com/page#section1")
        assert result["fragment"] == "section1"

    def test_fragment_is_empty_when_missing(self):
        result = parse_url("https://example.com/path")
        assert result["fragment"] == ""

    def test_fragment_with_query(self):
        result = parse_url("https://example.com/path?q=1#frag")
        assert result["query"] == "q=1"
        assert result["fragment"] == "frag"


# ---------------------------------------------------------------------------
# parse_url: full-URL round-trip checks
# ---------------------------------------------------------------------------

class TestParseUrlFullUrls:
    def test_full_url_with_all_components(self):
        result = parse_url("https://example.com:8443/path/to/resource?key=val#top")
        assert result == {
            "scheme": "https",
            "host": "example.com",
            "port": 8443,
            "path": "/path/to/resource",
            "query": "key=val",
            "fragment": "top",
        }

    def test_minimal_http_url(self):
        result = parse_url("http://localhost")
        assert result == {
            "scheme": "http",
            "host": "localhost",
            "port": None,
            "path": "",
            "query": "",
            "fragment": "",
        }


# ---------------------------------------------------------------------------
# parse_url: edge cases and invalid input
# ---------------------------------------------------------------------------

class TestParseUrlEdgeCases:
    def test_empty_string_returns_all_defaults(self):
        result = parse_url("")
        assert result["host"] == ""
        assert result["scheme"] == ""
        assert result["port"] is None
        assert result["path"] == ""
        assert result["query"] == ""
        assert result["fragment"] == ""

    def test_none_input_returns_all_defaults(self):
        result = parse_url(None)
        assert result["host"] == ""
        assert result["port"] is None

    def test_non_string_input_returns_defaults(self):
        result = parse_url(12345)
        assert result["host"] == ""

    def test_unicode_host_is_extracted(self):
        result = parse_url("https://\u4f8b\u3048.jp/\u30d1\u30b9")
        assert result["host"] == "\u4f8b\u3048.jp"
        assert result["path"] == "/\u30d1\u30b9"

    def test_very_long_path_is_preserved(self):
        long_path = "/a" * 5000
        result = parse_url(f"https://example.com{long_path}")
        assert result["host"] == "example.com"
        assert result["path"] == long_path

    def test_url_with_multiple_question_marks(self):
        result = parse_url("https://example.com/path?a=1?b=2")
        # split("?", 1) means everything after the first ? is the query.
        assert result["query"] == "a=1?b=2"

    def test_url_with_multiple_hashes(self):
        result = parse_url("https://example.com/path#frag1#frag2")
        # rsplit("#", 1) means the last segment is the fragment.
        assert result["fragment"] == "frag2"


# ---------------------------------------------------------------------------
# normalize_url
# ---------------------------------------------------------------------------

class TestNormalizeUrl:
    def test_lowercases_scheme(self):
        result = normalize_url("HTTP://example.com/path")
        assert result.startswith("http://")

    def test_lowercases_host(self):
        result = normalize_url("https://EXAMPLE.COM/path")
        assert "example.com" in result

    def test_lowercases_both_scheme_and_host(self):
        result = normalize_url("HTTP://EXAMPLE.COM/path")
        assert result == "http://example.com/path"

    def test_removes_default_http_port_80(self):
        result = normalize_url("http://example.com:80/path")
        assert result == "http://example.com/path"

    def test_removes_default_https_port_443(self):
        result = normalize_url("https://example.com:443/path")
        assert result == "https://example.com/path"

    def test_preserves_non_default_port(self):
        result = normalize_url("https://example.com:8443/path")
        assert result == "https://example.com:8443/path"

    def test_adds_trailing_slash_when_path_is_empty(self):
        result = normalize_url("https://example.com")
        assert result == "https://example.com/"

    def test_preserves_query_and_fragment(self):
        result = normalize_url("HTTPS://EXAMPLE.COM/p?q=1#f")
        assert result == "https://example.com/p?q=1#f"


# ---------------------------------------------------------------------------
# normalize_url + parse_url true integration test (no mocks)
# ---------------------------------------------------------------------------

class TestNormalizeParseIntegration:
    """Verify that normalize_url and parse_url work together correctly
    by round-tripping: normalize a URL, then parse the result and check
    that the components are consistent."""

    def test_normalized_url_parses_back_correctly(self):
        original = "HTTP://EXAMPLE.COM:443/Path?Q=1#Frag"
        normalized = normalize_url(original)
        parts = parse_url(normalized)

        assert parts["scheme"] == "http"
        assert parts["host"] == "example.com"
        assert parts["port"] == 443  # not a default port for http
        assert parts["path"] == "/Path"
        assert parts["query"] == "Q=1"
        assert parts["fragment"] == "Frag"

    def test_https_default_port_removed_and_reparsed(self):
        normalized = normalize_url("HTTPS://Example.Com:443/path")
        parts = parse_url(normalized)

        assert parts["scheme"] == "https"
        assert parts["host"] == "example.com"
        assert parts["port"] is None  # 443 stripped for https
        assert parts["path"] == "/path"
