"""Comprehensive test suite for url_parser.py (parse_url and normalize_url)."""

import sys
import os
import pytest

# Add source directory to path so we can import the module under test.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "evals", "files"))

from url_parser import parse_url, normalize_url


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _default_result(**overrides):
    """Return a default empty parse result with optional overrides."""
    base = {"scheme": "", "host": "", "port": None, "path": "", "query": "", "fragment": ""}
    base.update(overrides)
    return base


# ===========================================================================
# parse_url tests
# ===========================================================================


class TestParseUrlEmptyAndInvalidInputs:
    """Edge cases for missing or non-string inputs."""

    def test_empty_string(self):
        assert parse_url("") == _default_result()

    def test_none_input(self):
        assert parse_url(None) == _default_result()

    def test_integer_input(self):
        assert parse_url(123) == _default_result()

    def test_boolean_input(self):
        # bool is a subclass of int in Python, so isinstance(True, str) is False
        assert parse_url(True) == _default_result()

    def test_list_input(self):
        assert parse_url(["http://example.com"]) == _default_result()


class TestParseUrlFullUrls:
    """Standard URLs with all components present."""

    def test_full_http_url(self):
        result = parse_url("http://example.com:8080/path/to/page?key=value#section")
        assert result == {
            "scheme": "http",
            "host": "example.com",
            "port": 8080,
            "path": "/path/to/page",
            "query": "key=value",
            "fragment": "section",
        }

    def test_full_https_url(self):
        result = parse_url("https://secure.example.com:443/login?redirect=/home#top")
        assert result == {
            "scheme": "https",
            "host": "secure.example.com",
            "port": 443,
            "path": "/login",
            "query": "redirect=/home",
            "fragment": "top",
        }

    def test_ftp_url(self):
        result = parse_url("ftp://files.example.com:21/pub/readme.txt")
        assert result == {
            "scheme": "ftp",
            "host": "files.example.com",
            "port": 21,
            "path": "/pub/readme.txt",
            "query": "",
            "fragment": "",
        }


class TestParseUrlScheme:
    """Tests focused on scheme extraction."""

    def test_http_scheme(self):
        assert parse_url("http://example.com")["scheme"] == "http"

    def test_https_scheme(self):
        assert parse_url("https://example.com")["scheme"] == "https"

    def test_ftp_scheme(self):
        assert parse_url("ftp://example.com")["scheme"] == "ftp"

    def test_custom_scheme(self):
        assert parse_url("myapp://example.com")["scheme"] == "myapp"

    def test_no_scheme(self):
        """URL without :// should yield an empty scheme."""
        result = parse_url("example.com/path")
        assert result["scheme"] == ""

    def test_mixed_case_scheme(self):
        """parse_url preserves original case (normalization is normalize_url's job)."""
        assert parse_url("HTTP://example.com")["scheme"] == "HTTP"


class TestParseUrlHost:
    """Tests focused on host extraction."""

    def test_simple_host(self):
        assert parse_url("http://example.com")["host"] == "example.com"

    def test_subdomain_host(self):
        assert parse_url("http://www.sub.example.com/path")["host"] == "www.sub.example.com"

    def test_ip_address_host(self):
        assert parse_url("http://192.168.1.1/path")["host"] == "192.168.1.1"

    def test_localhost(self):
        assert parse_url("http://localhost/path")["host"] == "localhost"

    def test_host_only_no_scheme_no_path(self):
        result = parse_url("example.com")
        assert result["host"] == "example.com"
        assert result["path"] == ""

    def test_host_with_path_no_scheme(self):
        result = parse_url("example.com/path")
        assert result["host"] == "example.com"
        assert result["path"] == "/path"


class TestParseUrlPort:
    """Tests focused on port extraction."""

    def test_standard_http_port(self):
        assert parse_url("http://example.com:80/path")["port"] == 80

    def test_standard_https_port(self):
        assert parse_url("https://example.com:443/path")["port"] == 443

    def test_custom_port(self):
        assert parse_url("http://example.com:3000/path")["port"] == 3000

    def test_high_port(self):
        assert parse_url("http://example.com:65535/path")["port"] == 65535

    def test_no_port(self):
        assert parse_url("http://example.com/path")["port"] is None

    def test_invalid_port_non_numeric(self):
        """Non-numeric port string should result in port=None."""
        result = parse_url("http://example.com:abc/path")
        assert result["port"] is None

    def test_port_without_path(self):
        result = parse_url("http://example.com:9090")
        assert result["port"] == 9090
        assert result["host"] == "example.com"


class TestParseUrlPath:
    """Tests focused on path extraction."""

    def test_simple_path(self):
        assert parse_url("http://example.com/path")["path"] == "/path"

    def test_nested_path(self):
        assert parse_url("http://example.com/a/b/c/d")["path"] == "/a/b/c/d"

    def test_root_path(self):
        assert parse_url("http://example.com/")["path"] == "/"

    def test_no_path(self):
        assert parse_url("http://example.com")["path"] == ""

    def test_path_with_file_extension(self):
        assert parse_url("http://example.com/index.html")["path"] == "/index.html"

    def test_path_with_encoded_characters(self):
        assert parse_url("http://example.com/path%20with%20spaces")["path"] == "/path%20with%20spaces"

    def test_trailing_slash(self):
        assert parse_url("http://example.com/path/")["path"] == "/path/"


class TestParseUrlQuery:
    """Tests focused on query string extraction."""

    def test_simple_query(self):
        assert parse_url("http://example.com/path?key=value")["query"] == "key=value"

    def test_multiple_query_params(self):
        assert parse_url("http://example.com/path?a=1&b=2&c=3")["query"] == "a=1&b=2&c=3"

    def test_query_without_path(self):
        result = parse_url("http://example.com?key=value")
        assert result["query"] == "key=value"

    def test_empty_query_value(self):
        assert parse_url("http://example.com/path?key=")["query"] == "key="

    def test_query_key_only(self):
        assert parse_url("http://example.com/path?flag")["query"] == "flag"

    def test_no_query(self):
        assert parse_url("http://example.com/path")["query"] == ""

    def test_query_with_encoded_characters(self):
        assert parse_url("http://example.com/path?q=hello%20world")["query"] == "q=hello%20world"

    def test_query_with_special_characters(self):
        assert parse_url("http://example.com/path?q=a+b&x=1%262")["query"] == "q=a+b&x=1%262"


class TestParseUrlFragment:
    """Tests focused on fragment extraction."""

    def test_simple_fragment(self):
        assert parse_url("http://example.com/path#section")["fragment"] == "section"

    def test_fragment_without_path(self):
        assert parse_url("http://example.com#section")["fragment"] == "section"

    def test_fragment_with_query(self):
        result = parse_url("http://example.com/path?q=1#section")
        assert result["query"] == "q=1"
        assert result["fragment"] == "section"

    def test_empty_fragment(self):
        """Trailing # with nothing after it."""
        assert parse_url("http://example.com/path#")["fragment"] == ""

    def test_no_fragment(self):
        assert parse_url("http://example.com/path")["fragment"] == ""

    def test_fragment_with_special_characters(self):
        assert parse_url("http://example.com/path#sec/tion")["fragment"] == "sec/tion"


class TestParseUrlReturnType:
    """Verify the structure and types of the returned dict."""

    def test_return_type_is_dict(self):
        assert isinstance(parse_url("http://example.com"), dict)

    def test_all_keys_present(self):
        result = parse_url("http://example.com")
        expected_keys = {"scheme", "host", "port", "path", "query", "fragment"}
        assert set(result.keys()) == expected_keys

    def test_port_is_int_when_present(self):
        result = parse_url("http://example.com:8080/path")
        assert isinstance(result["port"], int)

    def test_port_is_none_when_absent(self):
        result = parse_url("http://example.com/path")
        assert result["port"] is None

    def test_string_fields_are_strings(self):
        result = parse_url("http://example.com:8080/path?q=1#frag")
        for key in ("scheme", "host", "path", "query", "fragment"):
            assert isinstance(result[key], str), f"{key} should be str"


class TestParseUrlEdgeCases:
    """Less common or tricky URL patterns."""

    def test_multiple_question_marks(self):
        """Only the first ? should split query from path."""
        result = parse_url("http://example.com/path?a=1?b=2")
        assert result["path"] == "/path"
        assert result["query"] == "a=1?b=2"

    def test_multiple_hash_signs(self):
        """rsplit on # means the last # separates the fragment."""
        result = parse_url("http://example.com/path#first#second")
        assert result["fragment"] == "second"

    def test_url_with_userinfo(self):
        """user:pass@host -- the parser doesn't handle userinfo specially."""
        result = parse_url("http://user:pass@example.com/path")
        # The colon in user:pass@example.com will affect host/port parsing
        # This documents the current behavior rather than prescribing ideal behavior
        assert result["scheme"] == "http"

    def test_url_with_at_sign_in_host(self):
        result = parse_url("http://user@example.com/path")
        assert result["host"] == "user@example.com"

    def test_scheme_with_no_host(self):
        """e.g., file:///path -- after splitting on :// the remainder is /path."""
        result = parse_url("file:///etc/hosts")
        assert result["scheme"] == "file"
        assert result["host"] == ""
        assert result["path"] == "/etc/hosts"

    def test_only_scheme(self):
        result = parse_url("http://")
        assert result["scheme"] == "http"
        assert result["host"] == ""

    def test_double_slash_in_path(self):
        result = parse_url("http://example.com//double//slashes")
        assert result["host"] == "example.com"
        assert result["path"] == "//double//slashes"

    def test_very_long_url(self):
        long_path = "/a" * 1000
        url = f"http://example.com{long_path}"
        result = parse_url(url)
        assert result["path"] == long_path

    def test_unicode_in_path(self):
        result = parse_url("http://example.com/\u00e9\u00e8\u00ea")
        assert result["path"] == "/\u00e9\u00e8\u00ea"

    def test_query_before_fragment_ordering(self):
        """Fragment is extracted first (rsplit #), then query (split ?)."""
        result = parse_url("http://example.com/p?q=1#frag")
        assert result["query"] == "q=1"
        assert result["fragment"] == "frag"

    def test_fragment_containing_question_mark(self):
        """Since fragment is extracted first, ? inside fragment stays in fragment."""
        result = parse_url("http://example.com/path#frag?not_a_query")
        assert result["fragment"] == "frag?not_a_query"
        assert result["query"] == ""

    def test_empty_host_with_port(self):
        result = parse_url("http://:8080/path")
        assert result["host"] == ""
        assert result["port"] == 8080

    def test_whitespace_url(self):
        """Whitespace-only string is truthy but contains no URL components."""
        result = parse_url("   ")
        assert result["host"] == "   "


# ===========================================================================
# normalize_url tests
# ===========================================================================


class TestNormalizeUrlBasic:
    """Core normalization behavior."""

    def test_basic_normalization(self):
        assert normalize_url("HTTP://EXAMPLE.COM/path") == "http://example.com/path"

    def test_scheme_lowercased(self):
        result = normalize_url("HTTPS://example.com/path")
        assert result.startswith("https://")

    def test_host_lowercased(self):
        result = normalize_url("http://EXAMPLE.COM/path")
        assert "example.com" in result

    def test_path_case_preserved(self):
        result = normalize_url("http://example.com/Path/To/Page")
        assert "/Path/To/Page" in result


class TestNormalizeUrlDefaultPortRemoval:
    """Verify that default ports (80 for http, 443 for https) are stripped."""

    def test_removes_http_port_80(self):
        result = normalize_url("http://example.com:80/path")
        assert result == "http://example.com/path"
        assert ":80" not in result

    def test_removes_https_port_443(self):
        result = normalize_url("https://example.com:443/path")
        assert result == "https://example.com/path"
        assert ":443" not in result

    def test_keeps_non_default_http_port(self):
        result = normalize_url("http://example.com:8080/path")
        assert ":8080" in result

    def test_keeps_non_default_https_port(self):
        result = normalize_url("https://example.com:8443/path")
        assert ":8443" in result

    def test_keeps_port_443_on_http(self):
        """Port 443 is only default for https, not http."""
        result = normalize_url("http://example.com:443/path")
        assert ":443" in result

    def test_keeps_port_80_on_https(self):
        """Port 80 is only default for http, not https."""
        result = normalize_url("https://example.com:80/path")
        assert ":80" in result


class TestNormalizeUrlPath:
    """Path handling during normalization."""

    def test_adds_trailing_slash_when_no_path(self):
        result = normalize_url("http://example.com")
        assert result == "http://example.com/"

    def test_preserves_existing_path(self):
        result = normalize_url("http://example.com/some/path")
        assert result == "http://example.com/some/path"

    def test_preserves_root_path(self):
        result = normalize_url("http://example.com/")
        assert result == "http://example.com/"


class TestNormalizeUrlQueryAndFragment:
    """Query and fragment handling during normalization."""

    def test_preserves_query(self):
        result = normalize_url("http://example.com/path?key=value")
        assert result == "http://example.com/path?key=value"

    def test_preserves_fragment(self):
        result = normalize_url("http://example.com/path#section")
        assert result == "http://example.com/path#section"

    def test_preserves_query_and_fragment(self):
        result = normalize_url("http://example.com/path?q=1#frag")
        assert result == "http://example.com/path?q=1#frag"

    def test_no_query_means_no_question_mark(self):
        result = normalize_url("http://example.com/path")
        assert "?" not in result

    def test_no_fragment_means_no_hash(self):
        result = normalize_url("http://example.com/path")
        assert "#" not in result


class TestNormalizeUrlFullRoundTrip:
    """Full URL normalization with all components."""

    def test_full_url_normalization(self):
        url = "HTTP://WWW.EXAMPLE.COM:80/Path/Page?Key=Value#Section"
        result = normalize_url(url)
        assert result == "http://www.example.com/Path/Page?Key=Value#Section"

    def test_https_full_url_normalization(self):
        url = "HTTPS://WWW.EXAMPLE.COM:443/path?q=1#frag"
        result = normalize_url(url)
        assert result == "https://www.example.com/path?q=1#frag"

    def test_non_default_port_preserved_in_full_url(self):
        url = "HTTP://EXAMPLE.COM:9090/path?q=1#frag"
        result = normalize_url(url)
        assert result == "http://example.com:9090/path?q=1#frag"

    def test_idempotent_normalization(self):
        """Normalizing an already-normalized URL should produce the same output."""
        url = "http://example.com/path?q=1#frag"
        assert normalize_url(url) == normalize_url(normalize_url(url))

    def test_idempotent_with_port_removal(self):
        """Even after port removal, re-normalizing should be stable."""
        first = normalize_url("http://example.com:80/path")
        second = normalize_url(first)
        assert first == second
