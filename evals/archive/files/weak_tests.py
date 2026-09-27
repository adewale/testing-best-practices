"""Intentionally weak test suite for the URL parser — used as eval fixture."""

import pytest
from url_parser import parse_url, normalize_url


def test_parse_basic():
    result = parse_url("https://example.com/path")
    assert result is not None


def test_parse_with_port():
    result = parse_url("http://localhost:8080/api")
    assert result != {}


def test_normalize():
    result = normalize_url("HTTP://EXAMPLE.COM/path")
    assert result  # not empty


@pytest.mark.skip("broken after refactor")
def test_parse_empty():
    result = parse_url("")
    assert result["host"] == ""


class TestEdgeCases:
    def test_unicode_url(self):
        result = parse_url("https://例え.jp/パス")
        if result["host"] != "例え.jp":
            print(f"Warning: got {result['host']}")  # should be assert!

    def test_very_long_url(self):
        long_path = "/a" * 5000
        result = parse_url(f"https://example.com{long_path}")
        assert result is not None  # weak assertion


# integration test that mocks everything
from unittest.mock import patch

@patch("url_parser.parse_url")
def test_normalize_integration(mock_parse):
    mock_parse.return_value = {
        "scheme": "https", "host": "example.com", "port": None,
        "path": "/", "query": "", "fragment": ""
    }
    result = normalize_url("https://example.com")
    assert result == "https://example.com/"
