"""Thorough test suite for the URL parser module.

Tests cover:
- parse_url: scheme, host, port, path, query, fragment extraction
- normalize_url: lowercasing, default port removal, path normalization
- Property-based tests: never-crashes, idempotent normalization, roundtrip
- Sad path: invalid inputs, missing components, edge cases, boundary values
"""

import sys
import os

# Add the source directory to the path so we can import the module under test.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "evals", "files"))

from url_parser import parse_url, normalize_url

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st


# ---------------------------------------------------------------------------
# Test data collections for systematic boundary testing
# ---------------------------------------------------------------------------

SCHEMES = ["http", "https", "ftp", "ssh", "ws", "wss"]
DEFAULT_PORTS = {"http": 80, "https": 443}
NON_DEFAULT_PORTS = [8080, 3000, 9090, 1, 65535]

INVALID_INPUTS = [None, "", 123, [], {}, True, 0, 3.14]

PATHS = [
    "/",
    "/path",
    "/path/to/resource",
    "/path/to/resource.html",
    "/path/with spaces",
    "/a/b/c/d/e/f/g",
]

QUERY_STRINGS = [
    "key=value",
    "a=1&b=2",
    "q=hello+world",
    "key=value&key=other",
    "empty=",
    "encoded=%20value",
]

FRAGMENTS = [
    "section1",
    "top",
    "",
    "section-with-dashes",
    "section/subsection",
]


# ===========================================================================
# parse_url: Happy path tests
# ===========================================================================


class TestParseUrlBasicComponents:
    """Tests for parsing standard URLs with all components present."""

    def test_full_url_with_all_components(self):
        result = parse_url("https://example.com:8080/path/to/page?key=value#section")
        assert result["scheme"] == "https"
        assert result["host"] == "example.com"
        assert result["port"] == 8080
        assert result["path"] == "/path/to/page"
        assert result["query"] == "key=value"
        assert result["fragment"] == "section"

    def test_http_url_standard(self):
        result = parse_url("http://www.example.com/index.html")
        assert result["scheme"] == "http"
        assert result["host"] == "www.example.com"
        assert result["port"] is None
        assert result["path"] == "/index.html"
        assert result["query"] == ""
        assert result["fragment"] == ""

    def test_https_url_with_query(self):
        result = parse_url("https://api.example.com/v2/users?limit=10&offset=20")
        assert result["scheme"] == "https"
        assert result["host"] == "api.example.com"
        assert result["path"] == "/v2/users"
        assert result["query"] == "limit=10&offset=20"
        assert result["port"] is None
        assert result["fragment"] == ""

    def test_url_with_fragment_only(self):
        result = parse_url("https://example.com/page#top")
        assert result["scheme"] == "https"
        assert result["host"] == "example.com"
        assert result["path"] == "/page"
        assert result["fragment"] == "top"
        assert result["query"] == ""

    def test_url_with_query_and_fragment(self):
        result = parse_url("http://example.com/search?q=test#results")
        assert result["query"] == "q=test"
        assert result["fragment"] == "results"
        assert result["path"] == "/search"
        assert result["scheme"] == "http"


class TestParseUrlSchemes:
    """Tests for various URL scheme handling."""

    def test_ftp_scheme(self):
        result = parse_url("ftp://files.example.com/pub/readme.txt")
        assert result["scheme"] == "ftp"
        assert result["host"] == "files.example.com"
        assert result["path"] == "/pub/readme.txt"

    def test_ssh_scheme(self):
        result = parse_url("ssh://git.example.com/repo.git")
        assert result["scheme"] == "ssh"
        assert result["host"] == "git.example.com"
        assert result["path"] == "/repo.git"

    def test_ws_websocket_scheme(self):
        result = parse_url("ws://realtime.example.com/socket")
        assert result["scheme"] == "ws"
        assert result["host"] == "realtime.example.com"
        assert result["path"] == "/socket"

    def test_wss_secure_websocket_scheme(self):
        result = parse_url("wss://realtime.example.com/socket")
        assert result["scheme"] == "wss"
        assert result["host"] == "realtime.example.com"
        assert result["path"] == "/socket"


class TestParseUrlPorts:
    """Tests for port parsing."""

    def test_explicit_port_80(self):
        result = parse_url("http://example.com:80/path")
        assert result["port"] == 80
        assert result["host"] == "example.com"
        assert result["scheme"] == "http"

    def test_explicit_port_443(self):
        result = parse_url("https://example.com:443/path")
        assert result["port"] == 443
        assert result["host"] == "example.com"

    def test_custom_port_8080(self):
        result = parse_url("http://localhost:8080/api")
        assert result["port"] == 8080
        assert result["host"] == "localhost"
        assert result["path"] == "/api"

    def test_custom_port_3000(self):
        result = parse_url("http://localhost:3000")
        assert result["port"] == 3000
        assert result["host"] == "localhost"

    def test_port_1_minimum_valid(self):
        result = parse_url("http://example.com:1/path")
        assert result["port"] == 1
        assert result["host"] == "example.com"

    def test_port_65535_maximum_valid(self):
        result = parse_url("http://example.com:65535/path")
        assert result["port"] == 65535
        assert result["host"] == "example.com"

    def test_no_port_returns_none(self):
        result = parse_url("http://example.com/path")
        assert result["port"] is None
        assert result["host"] == "example.com"

    def test_invalid_port_non_numeric(self):
        """Non-numeric port string should result in port=None."""
        result = parse_url("http://example.com:abc/path")
        assert result["port"] is None
        assert result["host"] == "example.com"


class TestParseUrlPaths:
    """Tests for path parsing."""

    def test_root_path(self):
        result = parse_url("http://example.com/")
        assert result["path"] == "/"
        assert result["host"] == "example.com"
        assert result["scheme"] == "http"

    def test_no_path(self):
        result = parse_url("http://example.com")
        assert result["path"] == ""
        assert result["host"] == "example.com"

    def test_deep_nested_path(self):
        result = parse_url("http://example.com/a/b/c/d/e")
        assert result["path"] == "/a/b/c/d/e"
        assert result["host"] == "example.com"

    def test_path_with_file_extension(self):
        result = parse_url("http://example.com/dir/file.html")
        assert result["path"] == "/dir/file.html"
        assert result["host"] == "example.com"

    def test_path_with_dots(self):
        result = parse_url("http://example.com/path/../other")
        assert result["path"] == "/path/../other"
        assert result["host"] == "example.com"

    def test_path_with_trailing_slash(self):
        result = parse_url("http://example.com/path/")
        assert result["path"] == "/path/"
        assert result["host"] == "example.com"


class TestParseUrlQueryStrings:
    """Tests for query string parsing."""

    def test_single_query_parameter(self):
        result = parse_url("http://example.com/search?q=hello")
        assert result["query"] == "q=hello"
        assert result["path"] == "/search"
        assert result["fragment"] == ""

    def test_multiple_query_parameters(self):
        result = parse_url("http://example.com/api?a=1&b=2&c=3")
        assert result["query"] == "a=1&b=2&c=3"
        assert "a=1" in result["query"]
        assert "b=2" in result["query"]
        assert "c=3" in result["query"]

    def test_query_with_empty_value(self):
        result = parse_url("http://example.com/search?q=")
        assert result["query"] == "q="
        assert result["path"] == "/search"

    def test_query_with_encoded_characters(self):
        result = parse_url("http://example.com/search?q=hello%20world")
        assert result["query"] == "q=hello%20world"
        assert result["path"] == "/search"

    def test_no_query_string(self):
        result = parse_url("http://example.com/path")
        assert result["query"] == ""
        assert result["path"] == "/path"


class TestParseUrlFragments:
    """Tests for fragment parsing."""

    def test_fragment_present(self):
        result = parse_url("http://example.com/page#section1")
        assert result["fragment"] == "section1"
        assert result["path"] == "/page"
        assert result["query"] == ""

    def test_fragment_with_query(self):
        result = parse_url("http://example.com/page?a=1#section")
        assert result["fragment"] == "section"
        assert result["query"] == "a=1"

    def test_no_fragment(self):
        result = parse_url("http://example.com/page?a=1")
        assert result["fragment"] == ""

    def test_empty_fragment(self):
        """A trailing # with no content should yield an empty fragment."""
        result = parse_url("http://example.com/page#")
        assert result["fragment"] == ""
        assert result["path"] == "/page"


# ===========================================================================
# parse_url: Sad path tests
# ===========================================================================


class TestParseUrlInvalidInputs:
    """Tests for invalid and edge-case inputs."""

    def test_none_input(self):
        result = parse_url(None)
        assert result["scheme"] == ""
        assert result["host"] == ""
        assert result["port"] is None
        assert result["path"] == ""
        assert result["query"] == ""
        assert result["fragment"] == ""

    def test_empty_string(self):
        result = parse_url("")
        assert result["scheme"] == ""
        assert result["host"] == ""
        assert result["port"] is None
        assert result["path"] == ""

    def test_non_string_integer(self):
        result = parse_url(123)
        assert result["scheme"] == ""
        assert result["host"] == ""
        assert result["port"] is None

    def test_non_string_list(self):
        result = parse_url([])
        assert result["scheme"] == ""
        assert result["host"] == ""
        assert result["port"] is None

    def test_non_string_dict(self):
        result = parse_url({})
        assert result["scheme"] == ""
        assert result["host"] == ""
        assert result["port"] is None

    def test_non_string_boolean(self):
        result = parse_url(True)
        assert result["scheme"] == ""
        assert result["host"] == ""
        assert result["port"] is None

    def test_just_scheme_separator(self):
        result = parse_url("://")
        assert result["scheme"] == ""
        assert result["host"] == ""

    def test_bare_host_no_scheme(self):
        result = parse_url("example.com")
        assert result["scheme"] == ""
        assert result["host"] == "example.com"
        assert result["port"] is None
        assert result["path"] == ""

    def test_bare_host_with_path_no_scheme(self):
        result = parse_url("example.com/path")
        assert result["scheme"] == ""
        assert result["host"] == "example.com"
        assert result["path"] == "/path"

    def test_only_path(self):
        result = parse_url("/just/a/path")
        # No scheme, host should be empty, path starts with /
        assert result["scheme"] == ""
        assert result["host"] == ""
        assert result["path"] == "/just/a/path"

    def test_only_query(self):
        result = parse_url("?key=value")
        assert result["query"] == "key=value"

    def test_only_fragment(self):
        result = parse_url("#fragment")
        assert result["fragment"] == "fragment"

    def test_url_with_spaces(self):
        """Parser should not crash on URLs with spaces."""
        result = parse_url("http://example.com/path with spaces")
        assert result["host"] == "example.com"
        assert "spaces" in result["path"]

    def test_url_with_unicode(self):
        """Parser should handle Unicode characters without crashing."""
        result = parse_url("http://example.com/path/\u00e9\u00e8\u00ea")
        assert result["host"] == "example.com"
        assert isinstance(result["path"], str)


class TestParseUrlReturnStructure:
    """Tests ensuring the return dict always has the correct shape."""

    def test_result_has_all_keys(self):
        result = parse_url("http://example.com")
        expected_keys = {"scheme", "host", "port", "path", "query", "fragment"}
        assert set(result.keys()) == expected_keys
        assert len(result) == 6

    def test_result_is_dict(self):
        result = parse_url("http://example.com")
        assert isinstance(result, dict)

    def test_invalid_input_has_all_keys(self):
        result = parse_url(None)
        expected_keys = {"scheme", "host", "port", "path", "query", "fragment"}
        assert set(result.keys()) == expected_keys
        assert len(result) == 6

    def test_empty_input_has_all_keys(self):
        result = parse_url("")
        expected_keys = {"scheme", "host", "port", "path", "query", "fragment"}
        assert set(result.keys()) == expected_keys


class TestParseUrlEdgeCases:
    """Edge cases and tricky inputs."""

    def test_multiple_question_marks(self):
        """Only the first ? should split path from query."""
        result = parse_url("http://example.com/path?a=1?b=2")
        assert result["path"] == "/path"
        assert result["query"] == "a=1?b=2"

    def test_multiple_hashes(self):
        """Only the last # should split fragment (rsplit behavior)."""
        result = parse_url("http://example.com/path#first#second")
        assert result["fragment"] == "second"

    def test_port_zero(self):
        """Port 0 is technically valid in some contexts."""
        result = parse_url("http://example.com:0/path")
        # Port 0 should parse as integer 0
        assert result["host"] == "example.com"

    def test_very_long_url(self):
        """Parser should handle very long URLs without issues."""
        long_path = "/a" * 5000
        result = parse_url(f"http://example.com{long_path}")
        assert result["host"] == "example.com"
        assert result["scheme"] == "http"
        assert len(result["path"]) == 10000

    def test_url_with_at_sign_in_host(self):
        """URLs like user@host should not crash."""
        result = parse_url("http://user@example.com/path")
        assert result["scheme"] == "http"
        assert "example" in result["host"] or "user" in result["host"]

    def test_url_with_multiple_colons_in_host(self):
        """IPv6-like addresses might have multiple colons."""
        result = parse_url("http://[::1]:8080/path")
        # Should not crash; exact behavior depends on implementation
        assert isinstance(result, dict)
        assert result["scheme"] == "http"

    def test_fragment_with_query_like_content(self):
        """Fragment can contain ? characters."""
        result = parse_url("http://example.com/page#frag?not-a-query")
        assert result["fragment"] == "frag?not-a-query"
        assert result["query"] == ""


# ===========================================================================
# normalize_url tests
# ===========================================================================


class TestNormalizeUrlSchemeAndHost:
    """Tests for scheme and host lowercasing in normalize_url."""

    def test_lowercases_scheme(self):
        result = normalize_url("HTTP://example.com/path")
        assert result.startswith("http://")
        assert "HTTP" not in result.split("://")[0]

    def test_lowercases_host(self):
        result = normalize_url("http://EXAMPLE.COM/path")
        assert "example.com" in result
        assert "EXAMPLE.COM" not in result

    def test_lowercases_both_scheme_and_host(self):
        result = normalize_url("HTTPS://WWW.EXAMPLE.COM/path")
        assert result.startswith("https://")
        assert "www.example.com" in result
        assert "HTTPS" not in result
        assert "EXAMPLE" not in result

    def test_preserves_path_case(self):
        """Path should NOT be lowercased since paths can be case-sensitive."""
        result = normalize_url("http://example.com/CaseSensitivePath")
        assert "/CaseSensitivePath" in result

    def test_preserves_query_case(self):
        result = normalize_url("http://example.com/path?Key=Value")
        assert "Key=Value" in result

    def test_preserves_fragment_case(self):
        result = normalize_url("http://example.com/path#Section")
        assert "Section" in result


class TestNormalizeUrlDefaultPorts:
    """Tests for default port removal."""

    def test_removes_http_port_80(self):
        result = normalize_url("http://example.com:80/path")
        assert ":80" not in result
        assert result == "http://example.com/path"

    def test_removes_https_port_443(self):
        result = normalize_url("https://example.com:443/path")
        assert ":443" not in result
        assert result == "https://example.com/path"

    def test_keeps_non_default_port_on_http(self):
        result = normalize_url("http://example.com:8080/path")
        assert ":8080" in result
        assert "example.com:8080" in result

    def test_keeps_non_default_port_on_https(self):
        result = normalize_url("https://example.com:8443/path")
        assert ":8443" in result

    def test_keeps_port_443_on_http(self):
        """Port 443 is NOT default for HTTP, should be preserved."""
        result = normalize_url("http://example.com:443/path")
        assert ":443" in result

    def test_keeps_port_80_on_https(self):
        """Port 80 is NOT default for HTTPS, should be preserved."""
        result = normalize_url("https://example.com:80/path")
        assert ":80" in result


class TestNormalizeUrlPathHandling:
    """Tests for path normalization behavior."""

    def test_adds_trailing_slash_when_no_path(self):
        result = normalize_url("http://example.com")
        assert result == "http://example.com/"

    def test_preserves_existing_path(self):
        result = normalize_url("http://example.com/path")
        assert result == "http://example.com/path"

    def test_preserves_root_path(self):
        result = normalize_url("http://example.com/")
        assert result == "http://example.com/"


class TestNormalizeUrlFullRoundtrip:
    """Tests for normalize_url with all components present."""

    def test_full_url_normalization(self):
        result = normalize_url("HTTP://EXAMPLE.COM:80/Path?query=1#frag")
        assert result == "http://example.com/Path?query=1#frag"
        assert "HTTP" not in result.split("://")[0]
        assert "EXAMPLE" not in result.split("://")[1].split("/")[0]
        assert ":80" not in result

    def test_full_url_custom_port_preserved(self):
        result = normalize_url("HTTP://EXAMPLE.COM:9090/path?q=1#top")
        assert result == "http://example.com:9090/path?q=1#top"
        assert ":9090" in result

    def test_normalize_idempotent_simple(self):
        """Normalizing an already-normalized URL should return the same result."""
        url = "http://example.com/path?query=1#frag"
        first = normalize_url(url)
        second = normalize_url(first)
        assert first == second

    def test_normalize_idempotent_with_port(self):
        url = "https://example.com:8080/path"
        first = normalize_url(url)
        second = normalize_url(first)
        assert first == second


# ===========================================================================
# Parametrized tests
# ===========================================================================


@pytest.mark.parametrize("scheme", SCHEMES)
def test_parse_url_various_schemes(scheme):
    url = f"{scheme}://example.com/path"
    result = parse_url(url)
    assert result["scheme"] == scheme
    assert result["host"] == "example.com"
    assert result["path"] == "/path"


@pytest.mark.parametrize("port", NON_DEFAULT_PORTS)
def test_parse_url_various_ports(port):
    url = f"http://example.com:{port}/path"
    result = parse_url(url)
    assert result["port"] == port
    assert result["host"] == "example.com"
    assert result["scheme"] == "http"


@pytest.mark.parametrize("path", PATHS)
def test_parse_url_various_paths(path):
    url = f"http://example.com{path}"
    result = parse_url(url)
    assert result["path"] == path
    assert result["host"] == "example.com"


@pytest.mark.parametrize("query", QUERY_STRINGS)
def test_parse_url_various_query_strings(query):
    url = f"http://example.com/path?{query}"
    result = parse_url(url)
    assert result["query"] == query
    assert result["path"] == "/path"
    assert result["host"] == "example.com"


@pytest.mark.parametrize("fragment", [f for f in FRAGMENTS if f])
def test_parse_url_various_fragments(fragment):
    url = f"http://example.com/path#{fragment}"
    result = parse_url(url)
    assert result["fragment"] == fragment
    assert result["path"] == "/path"


@pytest.mark.parametrize("invalid_input", INVALID_INPUTS)
def test_parse_url_invalid_inputs_return_empty(invalid_input):
    result = parse_url(invalid_input)
    assert result["scheme"] == ""
    assert result["host"] == ""
    assert result["port"] is None
    assert result["path"] == ""


# ===========================================================================
# Property-based tests (Hypothesis)
# ===========================================================================


class TestPropertyBased:
    """Property-based tests using Hypothesis for parse_url and normalize_url."""

    @given(text=st.text())
    @settings(max_examples=300)
    def test_parse_url_never_crashes_on_arbitrary_input(self, text):
        """parse_url must never raise an exception on any string input."""
        result = parse_url(text)
        assert isinstance(result, dict)
        assert "scheme" in result
        assert "host" in result
        assert "port" in result
        assert "path" in result
        assert "query" in result
        assert "fragment" in result

    @given(text=st.text())
    @settings(max_examples=300)
    def test_normalize_url_never_crashes_on_arbitrary_input(self, text):
        """normalize_url must never raise an exception on any string input."""
        result = normalize_url(text)
        assert isinstance(result, str)

    @given(
        scheme=st.sampled_from(["http", "https", "ftp"]),
        host=st.from_regex(r"[a-z][a-z0-9]{0,20}\.[a-z]{2,5}", fullmatch=True),
        path=st.from_regex(r"(/[a-z0-9]{1,10}){0,5}", fullmatch=True),
    )
    @settings(max_examples=200)
    def test_parse_url_roundtrip_scheme_host_path(self, scheme, host, path):
        """Parsing a well-formed URL should recover scheme, host, and path."""
        url = f"{scheme}://{host}{path}"
        result = parse_url(url)
        assert result["scheme"] == scheme
        assert result["host"] == host
        if path:
            assert result["path"] == path
        else:
            assert result["path"] == ""

    @given(
        scheme=st.sampled_from(["http", "https"]),
        host=st.from_regex(r"[a-z][a-z0-9]{0,10}\.[a-z]{2,4}", fullmatch=True),
        path=st.from_regex(r"(/[a-z]{1,8}){1,3}", fullmatch=True),
    )
    @settings(max_examples=200)
    def test_normalize_url_idempotent(self, scheme, host, path):
        """Normalizing twice should give the same result as normalizing once."""
        url = f"{scheme}://{host}{path}"
        once = normalize_url(url)
        twice = normalize_url(once)
        assert once == twice

    @given(
        scheme=st.sampled_from(["http", "https"]),
        host=st.from_regex(r"[a-z]{3,10}\.[a-z]{2,4}", fullmatch=True),
        port=st.integers(min_value=1, max_value=65535),
        path=st.from_regex(r"(/[a-z]{1,6}){1,3}", fullmatch=True),
    )
    @settings(max_examples=200)
    def test_parse_url_port_is_integer_or_none(self, scheme, host, port, path):
        """Parsed port should always be an integer or None."""
        url = f"{scheme}://{host}:{port}{path}"
        result = parse_url(url)
        assert result["port"] is None or isinstance(result["port"], int)
        if result["port"] is not None:
            assert result["port"] == port

    @given(
        scheme=st.sampled_from(["http", "https"]),
        host=st.from_regex(r"[A-Za-z]{3,10}\.[A-Za-z]{2,4}", fullmatch=True),
        path=st.from_regex(r"(/[a-zA-Z]{1,6}){1,3}", fullmatch=True),
    )
    @settings(max_examples=200)
    def test_normalize_url_lowercases_scheme_and_host(self, scheme, host, path):
        """After normalization, scheme and host must be lowercase."""
        url = f"{scheme}://{host}{path}"
        result = normalize_url(url)
        parsed = parse_url(result)
        assert parsed["scheme"] == parsed["scheme"].lower()
        assert parsed["host"] == parsed["host"].lower()

    @given(
        scheme=st.sampled_from(["http", "https"]),
        host=st.from_regex(r"[a-z]{3,10}\.[a-z]{2,4}", fullmatch=True),
        path=st.from_regex(r"(/[a-z]{1,6}){1,3}", fullmatch=True),
        query=st.from_regex(r"[a-z]{1,5}=[a-z0-9]{1,5}", fullmatch=True),
        fragment=st.from_regex(r"[a-z]{1,8}", fullmatch=True),
    )
    @settings(max_examples=200)
    def test_parse_url_preserves_query_and_fragment(self, scheme, host, path, query, fragment):
        """Query and fragment should survive a parse roundtrip unchanged."""
        url = f"{scheme}://{host}{path}?{query}#{fragment}"
        result = parse_url(url)
        assert result["query"] == query
        assert result["fragment"] == fragment

    @given(text=st.text(min_size=0, max_size=500))
    @settings(max_examples=200)
    def test_parse_url_result_always_has_six_keys(self, text):
        """The result dict must always have exactly 6 keys regardless of input."""
        result = parse_url(text)
        assert len(result) == 6
        assert set(result.keys()) == {"scheme", "host", "port", "path", "query", "fragment"}

    @given(
        host=st.from_regex(r"[a-z]{3,10}\.[a-z]{2,4}", fullmatch=True),
        path=st.from_regex(r"(/[a-z]{1,6}){1,3}", fullmatch=True),
    )
    @settings(max_examples=100)
    def test_normalize_removes_default_http_port_80(self, host, path):
        """HTTP URLs with port 80 should have the port removed after normalization."""
        url = f"http://{host}:80{path}"
        result = normalize_url(url)
        assert ":80" not in result
        assert f"http://{host}{path}" == result

    @given(
        host=st.from_regex(r"[a-z]{3,10}\.[a-z]{2,4}", fullmatch=True),
        path=st.from_regex(r"(/[a-z]{1,6}){1,3}", fullmatch=True),
    )
    @settings(max_examples=100)
    def test_normalize_removes_default_https_port_443(self, host, path):
        """HTTPS URLs with port 443 should have the port removed after normalization."""
        url = f"https://{host}:443{path}"
        result = normalize_url(url)
        assert ":443" not in result
        assert f"https://{host}{path}" == result


# ===========================================================================
# Regression-style tests for specific scenarios
# ===========================================================================


class TestRegressionScenarios:
    """Tests for specific scenarios that could reveal subtle bugs."""

    def test_query_before_fragment_ordering(self):
        """Ensure ? in fragment is not confused with query separator."""
        result = parse_url("http://example.com/page#frag?withquestion")
        # Fragment should contain everything after #
        assert result["fragment"] == "frag?withquestion"
        assert result["query"] == ""
        assert result["path"] == "/page"

    def test_scheme_like_content_in_path(self):
        """A :// sequence in path should not re-trigger scheme parsing."""
        result = parse_url("http://example.com/redirect?url=http://other.com")
        assert result["scheme"] == "http"
        assert result["host"] == "example.com"
        # The query should contain the nested URL
        assert "http://other.com" in result["query"]

    def test_empty_host_with_port(self):
        """Handles edge case of scheme with colon but no real host."""
        result = parse_url("http://:8080/path")
        assert result["port"] == 8080
        assert result["path"] == "/path"

    def test_url_with_only_scheme_and_host(self):
        result = parse_url("http://example.com")
        assert result["scheme"] == "http"
        assert result["host"] == "example.com"
        assert result["port"] is None
        assert result["path"] == ""
        assert result["query"] == ""
        assert result["fragment"] == ""

    def test_normalize_url_with_mixed_case_scheme_and_default_port(self):
        result = normalize_url("HTTP://EXAMPLE.COM:80/PATH")
        assert result == "http://example.com/PATH"
        assert ":80" not in result
        assert result.startswith("http://")

    def test_normalize_url_preserves_non_standard_schemes(self):
        result = normalize_url("FTP://FILES.EXAMPLE.COM/pub")
        assert result.startswith("ftp://")
        assert "files.example.com" in result
        assert "/pub" in result

    def test_parse_url_host_with_subdomain(self):
        result = parse_url("https://sub.domain.example.com/path")
        assert result["host"] == "sub.domain.example.com"
        assert result["scheme"] == "https"
        assert result["path"] == "/path"

    def test_parse_url_localhost(self):
        result = parse_url("http://localhost/path")
        assert result["host"] == "localhost"
        assert result["path"] == "/path"
        assert result["port"] is None

    def test_parse_url_ip_address(self):
        result = parse_url("http://192.168.1.1:3000/api")
        assert result["host"] == "192.168.1.1"
        assert result["port"] == 3000
        assert result["path"] == "/api"

    def test_parse_and_normalize_consistency(self):
        """Normalizing and then parsing should yield same components (lowercased)."""
        original = "HTTP://EXAMPLE.COM:8080/Path?key=value#section"
        normalized = normalize_url(original)
        parsed_original = parse_url(original)
        parsed_normalized = parse_url(normalized)

        # Scheme and host should be lowercased in normalized version
        assert parsed_normalized["scheme"] == parsed_original["scheme"].lower()
        assert parsed_normalized["host"] == parsed_original["host"].lower()
        # Port, path, query, fragment should be preserved
        assert parsed_normalized["port"] == parsed_original["port"]
        assert parsed_normalized["path"] == parsed_original["path"]
        assert parsed_normalized["query"] == parsed_original["query"]
        assert parsed_normalized["fragment"] == parsed_original["fragment"]
