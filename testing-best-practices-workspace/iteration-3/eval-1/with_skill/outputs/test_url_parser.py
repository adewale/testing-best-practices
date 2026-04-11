"""Thorough test suite for the URL parser module.

Tests cover parse_url and normalize_url with:
- Happy-path unit tests with 3+ assertions each
- Sad-path / edge-case tests (empty, None, malformed)
- Boundary values (missing scheme, missing host, missing path, etc.)
- Property-based tests (never crashes, idempotent normalization, roundtrip)
- Both positive and negative assertions per test
"""

import sys
import os

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# Add the source directory to the path so we can import the module under test.
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "evals", "files"),
)
from url_parser import parse_url, normalize_url


# ---------------------------------------------------------------------------
# parse_url: happy-path unit tests
# ---------------------------------------------------------------------------


class TestParseUrlHappyPath:
    """Standard URLs that should be fully parsed."""

    def test_full_url_with_all_components(self):
        result = parse_url("https://example.com:8080/path/to/page?key=val#section")
        assert result["scheme"] == "https"
        assert result["host"] == "example.com"
        assert result["port"] == 8080
        assert result["path"] == "/path/to/page"
        assert result["query"] == "key=val"
        assert result["fragment"] == "section"

    def test_http_url_no_port(self):
        result = parse_url("http://example.com/index.html")
        assert result["scheme"] == "http"
        assert result["host"] == "example.com"
        assert result["port"] is None
        assert result["path"] == "/index.html"
        assert result["query"] == ""
        assert result["fragment"] == ""

    def test_https_url_with_port_443(self):
        result = parse_url("https://secure.example.com:443/login")
        assert result["scheme"] == "https"
        assert result["host"] == "secure.example.com"
        assert result["port"] == 443
        assert result["path"] == "/login"

    def test_url_with_query_only(self):
        result = parse_url("http://search.com/find?q=hello&lang=en")
        assert result["scheme"] == "http"
        assert result["host"] == "search.com"
        assert result["path"] == "/find"
        assert result["query"] == "q=hello&lang=en"
        assert result["fragment"] == ""

    def test_url_with_fragment_only(self):
        result = parse_url("http://docs.example.com/page#heading")
        assert result["scheme"] == "http"
        assert result["host"] == "docs.example.com"
        assert result["path"] == "/page"
        assert result["query"] == ""
        assert result["fragment"] == "heading"

    def test_url_with_query_and_fragment(self):
        result = parse_url("http://example.com/p?a=1#top")
        assert result["scheme"] == "http"
        assert result["host"] == "example.com"
        assert result["path"] == "/p"
        assert result["query"] == "a=1"
        assert result["fragment"] == "top"

    def test_root_path(self):
        result = parse_url("http://example.com/")
        assert result["scheme"] == "http"
        assert result["host"] == "example.com"
        assert result["path"] == "/"
        assert result["port"] is None

    def test_no_path(self):
        result = parse_url("http://example.com")
        assert result["scheme"] == "http"
        assert result["host"] == "example.com"
        assert result["path"] == ""
        assert result["port"] is None

    def test_deep_path(self):
        result = parse_url("https://cdn.example.com/a/b/c/d/e.js")
        assert result["scheme"] == "https"
        assert result["host"] == "cdn.example.com"
        assert result["path"] == "/a/b/c/d/e.js"
        assert result["port"] is None
        assert result["query"] == ""
        assert result["fragment"] == ""

    def test_custom_port(self):
        result = parse_url("http://localhost:3000/api/v1")
        assert result["scheme"] == "http"
        assert result["host"] == "localhost"
        assert result["port"] == 3000
        assert result["path"] == "/api/v1"

    def test_high_port_number(self):
        result = parse_url("http://host:65535/")
        assert result["port"] == 65535
        assert result["host"] == "host"

    def test_port_1(self):
        result = parse_url("http://host:1/")
        assert result["port"] == 1
        assert result["host"] == "host"


# ---------------------------------------------------------------------------
# parse_url: return structure verification
# ---------------------------------------------------------------------------


class TestParseUrlReturnStructure:
    """Every call to parse_url must return a dict with exactly the six keys."""

    EXPECTED_KEYS = {"scheme", "host", "port", "path", "query", "fragment"}

    def test_return_type_is_dict(self):
        result = parse_url("http://example.com")
        assert isinstance(result, dict)
        assert set(result.keys()) == self.EXPECTED_KEYS
        assert len(result) == 6

    def test_empty_input_returns_all_keys(self):
        result = parse_url("")
        assert isinstance(result, dict)
        assert set(result.keys()) == self.EXPECTED_KEYS
        assert len(result) == 6

    def test_none_input_returns_all_keys(self):
        result = parse_url(None)
        assert isinstance(result, dict)
        assert set(result.keys()) == self.EXPECTED_KEYS
        assert len(result) == 6


# ---------------------------------------------------------------------------
# parse_url: sad path / invalid input
# ---------------------------------------------------------------------------


class TestParseUrlSadPath:
    """Invalid, empty, and malformed inputs."""

    def test_empty_string(self):
        result = parse_url("")
        assert result["scheme"] == ""
        assert result["host"] == ""
        assert result["port"] is None
        assert result["path"] == ""
        assert result["query"] == ""
        assert result["fragment"] == ""

    def test_none_input(self):
        result = parse_url(None)
        assert result["scheme"] == ""
        assert result["host"] == ""
        assert result["port"] is None

    def test_non_string_integer(self):
        result = parse_url(12345)
        assert result["scheme"] == ""
        assert result["host"] == ""
        assert result["port"] is None

    def test_non_string_list(self):
        result = parse_url(["http://example.com"])
        assert result["scheme"] == ""
        assert result["host"] == ""
        assert result["port"] is None

    def test_bare_host_no_scheme(self):
        """A hostname without a scheme -- scheme should be empty."""
        result = parse_url("example.com")
        assert result["scheme"] == ""
        assert result["host"] == "example.com"
        assert result["port"] is None
        # No scheme means no ://, so host is the whole string
        assert result["path"] == ""

    def test_bare_host_with_path_no_scheme(self):
        result = parse_url("example.com/path")
        assert result["scheme"] == ""
        assert result["host"] == "example.com"
        assert result["path"] == "/path"

    def test_invalid_port_non_numeric(self):
        """When port is not a valid integer, it should remain None."""
        result = parse_url("http://example.com:abc/path")
        assert result["host"] == "example.com"
        assert result["port"] is None
        assert result["path"] == "/path"

    def test_only_scheme(self):
        result = parse_url("http://")
        assert result["scheme"] == "http"
        assert result["host"] == ""
        assert result["port"] is None
        assert result["path"] == ""

    def test_fragment_only_url(self):
        result = parse_url("#fragment")
        assert result["fragment"] == "fragment"
        assert result["scheme"] == ""
        assert result["host"] == ""

    def test_query_only_url(self):
        result = parse_url("?key=value")
        assert result["query"] == "key=value"
        assert result["scheme"] == ""
        assert result["host"] == ""

    def test_just_a_slash(self):
        result = parse_url("/")
        assert result["scheme"] == ""
        assert result["path"] == "/"
        # When there is a slash, host is whatever is before it
        assert result["host"] == ""

    def test_double_slash_no_scheme(self):
        result = parse_url("//example.com/path")
        # No "://" present, so scheme is empty
        assert result["scheme"] == ""


# ---------------------------------------------------------------------------
# parse_url: boundary / edge-case values
# ---------------------------------------------------------------------------


class TestParseUrlEdgeCases:
    """URLs with special characters, multiple delimiters, unusual structures."""

    def test_multiple_question_marks(self):
        """Only the first '?' separates path from query."""
        result = parse_url("http://example.com/path?a=1?b=2")
        assert result["path"] == "/path"
        assert result["query"] == "a=1?b=2"

    def test_multiple_hash_signs(self):
        """Only the last '#' separates fragment (rsplit)."""
        result = parse_url("http://example.com/path#frag1#frag2")
        assert result["fragment"] == "frag2"
        # The remaining URL after rsplit should still parse correctly
        assert result["path"] == "/path"

    def test_empty_query_string(self):
        result = parse_url("http://example.com/path?")
        assert result["query"] == ""
        assert result["path"] == "/path"

    def test_empty_fragment(self):
        result = parse_url("http://example.com/path#")
        assert result["fragment"] == ""
        assert result["path"] == "/path"

    def test_query_with_encoded_characters(self):
        result = parse_url("http://example.com/search?q=hello%20world&lang=en")
        assert result["query"] == "q=hello%20world&lang=en"
        assert result["host"] == "example.com"
        assert result["path"] == "/search"

    def test_path_with_encoded_characters(self):
        result = parse_url("http://example.com/path%20with%20spaces")
        assert result["path"] == "/path%20with%20spaces"
        assert result["host"] == "example.com"

    def test_ftp_scheme(self):
        result = parse_url("ftp://files.example.com/pub/readme.txt")
        assert result["scheme"] == "ftp"
        assert result["host"] == "files.example.com"
        assert result["path"] == "/pub/readme.txt"
        assert result["port"] is None

    def test_custom_scheme(self):
        result = parse_url("myapp://open/page")
        assert result["scheme"] == "myapp"
        assert result["host"] == "open"
        assert result["path"] == "/page"

    def test_url_with_userinfo(self):
        """URLs can contain user@host -- the parser treats '@' as part of host."""
        result = parse_url("http://user:pass@example.com/path")
        # The parser doesn't strip userinfo, so host includes it
        assert result["scheme"] == "http"
        assert result["path"] == "/path"

    def test_url_with_trailing_slash(self):
        result = parse_url("http://example.com/dir/")
        assert result["path"] == "/dir/"
        assert result["host"] == "example.com"
        assert result["scheme"] == "http"

    def test_very_long_url(self):
        long_path = "/a" * 500
        result = parse_url(f"http://example.com{long_path}")
        assert result["host"] == "example.com"
        assert result["path"] == long_path
        assert result["scheme"] == "http"

    def test_port_zero(self):
        result = parse_url("http://example.com:0/path")
        # int("0") succeeds but port 0 is edge-case; the parser stores it
        assert result["host"] == "example.com"
        assert result["path"] == "/path"

    def test_unicode_in_host(self):
        result = parse_url("http://\u00e9xample.com/path")
        assert result["host"] == "\u00e9xample.com"
        assert result["path"] == "/path"
        assert result["scheme"] == "http"

    def test_unicode_in_path(self):
        result = parse_url("http://example.com/caf\u00e9")
        assert result["path"] == "/caf\u00e9"
        assert result["host"] == "example.com"

    def test_hash_in_query(self):
        """Fragment delimiter '#' in URL: everything after last '#' is fragment."""
        result = parse_url("http://example.com/path?color=#fff#top")
        # rsplit on '#' takes the last '#': fragment = "top"
        assert result["fragment"] == "top"


# ---------------------------------------------------------------------------
# parse_url: specific components isolated
# ---------------------------------------------------------------------------


class TestParseUrlSchemes:
    """Verifying different scheme values."""

    @pytest.mark.parametrize(
        "url, expected_scheme",
        [
            ("http://x.com", "http"),
            ("https://x.com", "https"),
            ("ftp://x.com", "ftp"),
            ("ssh://x.com", "ssh"),
            ("ws://x.com", "ws"),
            ("wss://x.com", "wss"),
            ("custom://x.com", "custom"),
        ],
    )
    def test_scheme_extraction(self, url, expected_scheme):
        result = parse_url(url)
        assert result["scheme"] == expected_scheme
        assert result["host"] == "x.com"
        assert isinstance(result["scheme"], str)


class TestParseUrlPorts:
    """Verifying port extraction and edge cases."""

    @pytest.mark.parametrize(
        "url, expected_port",
        [
            ("http://h:80/", 80),
            ("http://h:443/", 443),
            ("http://h:8080/", 8080),
            ("http://h:1/", 1),
            ("http://h:65535/", 65535),
            ("http://h/", None),
            ("http://h:abc/", None),
        ],
    )
    def test_port_values(self, url, expected_port):
        result = parse_url(url)
        assert result["port"] == expected_port
        assert result["host"] == "h"
        assert result["scheme"] == "http"


# ---------------------------------------------------------------------------
# normalize_url: happy-path tests
# ---------------------------------------------------------------------------


class TestNormalizeUrlHappyPath:
    """Standard normalization scenarios."""

    def test_lowercases_scheme(self):
        result = normalize_url("HTTP://Example.com/path")
        assert result.startswith("http://")
        assert "example.com" in result
        assert result.endswith("/path")

    def test_lowercases_host(self):
        result = normalize_url("http://EXAMPLE.COM/path")
        assert "example.com" in result
        assert "EXAMPLE" not in result
        assert result == "http://example.com/path"

    def test_removes_default_http_port_80(self):
        result = normalize_url("http://example.com:80/path")
        assert ":80" not in result
        assert result == "http://example.com/path"

    def test_removes_default_https_port_443(self):
        result = normalize_url("https://example.com:443/path")
        assert ":443" not in result
        assert result == "https://example.com/path"

    def test_keeps_non_default_port(self):
        result = normalize_url("http://example.com:8080/path")
        assert ":8080" in result
        assert result == "http://example.com:8080/path"

    def test_keeps_non_default_https_port(self):
        result = normalize_url("https://example.com:8443/path")
        assert ":8443" in result
        assert result == "https://example.com:8443/path"

    def test_adds_trailing_slash_when_no_path(self):
        result = normalize_url("http://example.com")
        assert result == "http://example.com/"
        assert result.endswith("/")

    def test_preserves_query_string(self):
        result = normalize_url("http://example.com/path?key=value")
        assert "?key=value" in result
        assert result == "http://example.com/path?key=value"

    def test_preserves_fragment(self):
        result = normalize_url("http://example.com/path#section")
        assert "#section" in result
        assert result == "http://example.com/path#section"

    def test_full_normalization(self):
        result = normalize_url("HTTP://EXAMPLE.COM:80/Path?Q=1#Frag")
        assert result == "http://example.com/Path?Q=1#Frag"
        # Scheme and host are lowercased, default port removed
        assert "HTTP" not in result
        assert "EXAMPLE" not in result
        assert ":80" not in result
        # Path case is preserved (path is case-sensitive)
        assert "/Path" in result


# ---------------------------------------------------------------------------
# normalize_url: sad path / edge cases
# ---------------------------------------------------------------------------


class TestNormalizeUrlEdgeCases:
    """Unusual inputs to normalize_url."""

    def test_already_normalized_url(self):
        url = "http://example.com/path"
        result = normalize_url(url)
        assert result == url

    def test_port_80_on_https_is_kept(self):
        """Port 80 is only default for http, not https."""
        result = normalize_url("https://example.com:80/path")
        assert ":80" in result

    def test_port_443_on_http_is_kept(self):
        """Port 443 is only default for https, not http."""
        result = normalize_url("http://example.com:443/path")
        assert ":443" in result

    def test_preserves_path_case(self):
        """Paths are case-sensitive; normalization should not lowercase them."""
        result = normalize_url("http://example.com/CaseSensitive")
        assert "/CaseSensitive" in result

    def test_preserves_query_case(self):
        """Query strings are case-sensitive."""
        result = normalize_url("http://example.com/path?Key=Value")
        assert "Key=Value" in result

    def test_preserves_fragment_case(self):
        """Fragments are case-sensitive."""
        result = normalize_url("http://example.com/path#MySection")
        assert "MySection" in result

    def test_normalize_with_all_components(self):
        result = normalize_url("HTTPS://WWW.EXAMPLE.COM:443/a/b?x=1#y")
        assert result == "https://www.example.com/a/b?x=1#y"
        assert ":443" not in result
        assert "HTTPS" not in result
        assert "WWW.EXAMPLE.COM" not in result


# ---------------------------------------------------------------------------
# normalize_url: idempotent behavior
# ---------------------------------------------------------------------------


class TestNormalizeUrlIdempotent:
    """Normalizing an already-normalized URL should produce the same result."""

    @pytest.mark.parametrize(
        "url",
        [
            "http://example.com/path",
            "https://example.com:8080/path?q=1#frag",
            "HTTP://EXAMPLE.COM:80/PATH",
            "ftp://files.example.com/pub/readme.txt",
            "http://localhost:3000/api",
        ],
    )
    def test_normalize_is_idempotent(self, url):
        once = normalize_url(url)
        twice = normalize_url(once)
        assert once == twice, f"normalize_url is not idempotent for {url!r}"


# ---------------------------------------------------------------------------
# Property-based tests: parse_url
# ---------------------------------------------------------------------------


class TestParseUrlProperties:
    """Property-based tests using Hypothesis.

    Key properties:
    - parse_url never crashes on arbitrary string input
    - parse_url always returns a dict with exactly six keys
    - Parsed components are always strings (or None for port)
    """

    @given(text=st.text())
    @settings(max_examples=200)
    def test_never_crashes_on_arbitrary_input(self, text):
        """parse_url must never raise an exception on any string."""
        result = parse_url(text)
        assert isinstance(result, dict)

    @given(text=st.text())
    @settings(max_examples=200)
    def test_always_returns_six_keys(self, text):
        result = parse_url(text)
        assert set(result.keys()) == {"scheme", "host", "port", "path", "query", "fragment"}
        assert len(result) == 6

    @given(text=st.text())
    @settings(max_examples=200)
    def test_string_fields_are_strings(self, text):
        result = parse_url(text)
        assert isinstance(result["scheme"], str)
        assert isinstance(result["host"], str)
        assert isinstance(result["path"], str)
        assert isinstance(result["query"], str)
        assert isinstance(result["fragment"], str)

    @given(text=st.text())
    @settings(max_examples=200)
    def test_port_is_int_or_none(self, text):
        result = parse_url(text)
        assert result["port"] is None or isinstance(result["port"], int)

    @given(
        scheme=st.sampled_from(["http", "https", "ftp", "ws"]),
        host=st.from_regex(r"[a-z][a-z0-9]{0,20}\.[a-z]{2,4}", fullmatch=True),
        port=st.one_of(st.none(), st.integers(min_value=1, max_value=65535)),
        path=st.from_regex(r"(/[a-z0-9]{1,10}){0,5}", fullmatch=True),
        query=st.from_regex(r"([a-z]=[a-z0-9]{1,5})?", fullmatch=True),
        fragment=st.from_regex(r"[a-z]{0,10}", fullmatch=True),
    )
    @settings(max_examples=200)
    def test_roundtrip_reconstructed_url(self, scheme, host, port, path, query, fragment):
        """Build a URL from components, parse it, verify components match."""
        url = f"{scheme}://{host}"
        if port is not None:
            url += f":{port}"
        url += path
        if query:
            url += f"?{query}"
        if fragment:
            url += f"#{fragment}"

        result = parse_url(url)

        assert result["scheme"] == scheme
        assert result["host"] == host
        assert result["port"] == port
        if path:
            assert result["path"] == path
        else:
            # No path means empty string
            assert result["path"] == ""
        assert result["query"] == query
        assert result["fragment"] == fragment

    @given(text=st.text())
    @settings(max_examples=200)
    def test_conservation_fragment_is_substring_of_input(self, text):
        """If a fragment is extracted, it must be a substring of the input."""
        result = parse_url(text)
        if result["fragment"]:
            assert result["fragment"] in text

    @given(text=st.text())
    @settings(max_examples=200)
    def test_conservation_scheme_is_substring_of_input(self, text):
        """If a scheme is extracted, it must appear in the original input."""
        result = parse_url(text)
        if result["scheme"]:
            assert result["scheme"] in text

    @given(text=st.text())
    @settings(max_examples=200)
    def test_conservation_host_is_substring_of_input(self, text):
        """If a host is extracted, it must appear in the original input."""
        result = parse_url(text)
        if result["host"]:
            assert result["host"] in text


# ---------------------------------------------------------------------------
# Property-based tests: normalize_url
# ---------------------------------------------------------------------------


class TestNormalizeUrlProperties:
    """Property-based tests for normalize_url."""

    @given(
        scheme=st.sampled_from(["http", "https", "HTTP", "HTTPS", "Http"]),
        host=st.from_regex(r"[a-zA-Z][a-zA-Z0-9]{0,10}\.[a-zA-Z]{2,4}", fullmatch=True),
        path=st.from_regex(r"(/[a-z0-9]{1,5}){0,3}", fullmatch=True),
    )
    @settings(max_examples=200)
    def test_idempotent_normalization(self, scheme, host, path):
        """normalize(normalize(url)) == normalize(url)."""
        url = f"{scheme}://{host}{path}"
        once = normalize_url(url)
        twice = normalize_url(once)
        assert once == twice

    @given(
        scheme=st.sampled_from(["http", "https"]),
        host=st.from_regex(r"[A-Z][a-zA-Z]{0,8}\.[a-zA-Z]{2,3}", fullmatch=True),
        path=st.from_regex(r"(/[a-z]{1,5}){1,3}", fullmatch=True),
    )
    @settings(max_examples=200)
    def test_normalized_scheme_is_lowercase(self, scheme, host, path):
        url = f"{scheme.upper()}://{host}{path}"
        result = normalize_url(url)
        # The scheme in the output should be lowercase
        parsed = parse_url(result)
        assert parsed["scheme"] == parsed["scheme"].lower()

    @given(
        scheme=st.sampled_from(["http", "https"]),
        host=st.from_regex(r"[A-Z][a-zA-Z]{0,8}\.[a-zA-Z]{2,3}", fullmatch=True),
        path=st.from_regex(r"(/[a-z]{1,5}){1,3}", fullmatch=True),
    )
    @settings(max_examples=200)
    def test_normalized_host_is_lowercase(self, scheme, host, path):
        url = f"{scheme}://{host}{path}"
        result = normalize_url(url)
        parsed = parse_url(result)
        assert parsed["host"] == parsed["host"].lower()

    @given(
        host=st.from_regex(r"[a-z]{3,8}\.[a-z]{2,3}", fullmatch=True),
        path=st.from_regex(r"(/[a-z]{1,5}){1,3}", fullmatch=True),
    )
    @settings(max_examples=100)
    def test_default_port_80_removed_for_http(self, host, path):
        url = f"http://{host}:80{path}"
        result = normalize_url(url)
        assert ":80" not in result
        assert host in result

    @given(
        host=st.from_regex(r"[a-z]{3,8}\.[a-z]{2,3}", fullmatch=True),
        path=st.from_regex(r"(/[a-z]{1,5}){1,3}", fullmatch=True),
    )
    @settings(max_examples=100)
    def test_default_port_443_removed_for_https(self, host, path):
        url = f"https://{host}:443{path}"
        result = normalize_url(url)
        assert ":443" not in result
        assert host in result

    @given(
        scheme=st.sampled_from(["http", "https"]),
        host=st.from_regex(r"[a-z]{3,8}\.[a-z]{2,3}", fullmatch=True),
        port=st.integers(min_value=1, max_value=65535).filter(lambda p: p not in (80, 443)),
        path=st.from_regex(r"(/[a-z]{1,5}){1,3}", fullmatch=True),
    )
    @settings(max_examples=200)
    def test_non_default_port_preserved(self, scheme, host, port, path):
        url = f"{scheme}://{host}:{port}{path}"
        result = normalize_url(url)
        assert f":{port}" in result


# ---------------------------------------------------------------------------
# Integration: parse_url + normalize_url work together
# ---------------------------------------------------------------------------


class TestParseAndNormalizeIntegration:
    """Tests that verify parse_url and normalize_url interact correctly."""

    def test_parse_normalized_url_has_no_default_port(self):
        normalized = normalize_url("http://example.com:80/path")
        parsed = parse_url(normalized)
        assert parsed["port"] is None
        assert parsed["scheme"] == "http"
        assert parsed["host"] == "example.com"
        assert parsed["path"] == "/path"

    def test_normalize_preserves_parseable_structure(self):
        original = "HTTPS://EXAMPLE.COM:443/Path?Key=Val#Frag"
        normalized = normalize_url(original)
        parsed = parse_url(normalized)
        assert parsed["scheme"] == "https"
        assert parsed["host"] == "example.com"
        assert parsed["port"] is None  # default port removed
        assert parsed["path"] == "/Path"
        assert parsed["query"] == "Key=Val"
        assert parsed["fragment"] == "Frag"

    def test_parse_then_reconstruct_matches_normalize(self):
        """Manually reconstructing from parsed parts should match normalize."""
        url = "HTTP://Example.COM:80/a/b?x=1#y"
        normalized = normalize_url(url)
        parts = parse_url(normalized)

        reconstructed = f"{parts['scheme']}://{parts['host']}"
        if parts["port"]:
            reconstructed += f":{parts['port']}"
        reconstructed += parts["path"] or "/"
        if parts["query"]:
            reconstructed += f"?{parts['query']}"
        if parts["fragment"]:
            reconstructed += f"#{parts['fragment']}"

        assert reconstructed == normalized

    def test_normalize_then_parse_roundtrip_multiple_urls(self):
        urls = [
            "HTTP://FOO.COM:80/",
            "HTTPS://BAR.COM:443/page?q=1",
            "http://baz.com:9090/x#top",
            "ftp://files.example.com/pub",
        ]
        for url in urls:
            normalized = normalize_url(url)
            parsed = parse_url(normalized)
            assert parsed["scheme"] == parsed["scheme"].lower()
            assert parsed["host"] == parsed["host"].lower()
            # For http:80 and https:443, port should be None after normalization
            if url.upper().startswith("HTTP://") and ":80/" in url:
                assert parsed["port"] is None
            elif url.upper().startswith("HTTPS://") and ":443/" in url:
                assert parsed["port"] is None
