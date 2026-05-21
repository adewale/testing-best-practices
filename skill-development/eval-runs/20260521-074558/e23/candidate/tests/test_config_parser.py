from __future__ import annotations

from collections.abc import Mapping

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

try:
    from config_parser import Config, ParseError, parse_config
except ModuleNotFoundError as exc:  # Support common src/ layout without hiding real import failures.
    if exc.name != "config_parser":
        raise
    from src.config_parser import Config, ParseError, parse_config


_NAME = st.from_regex(r"[A-Za-z][A-Za-z0-9_]{0,24}", fullmatch=True)
_VALUE = st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-:/", min_size=1, max_size=80)


@st.composite
def valid_config_texts(draw):
    sections = draw(
        st.dictionaries(
            keys=_NAME,
            values=st.dictionaries(keys=_NAME, values=_VALUE, min_size=1, max_size=5),
            min_size=1,
            max_size=4,
        )
    )

    lines: list[str] = []
    for section, entries in sections.items():
        lines.append(f"[{section}]")
        for key, value in entries.items():
            lines.append(f"{key}={value}")
        lines.append("")
    return "\n".join(lines)


def assert_valid_config(config: Config) -> None:
    assert isinstance(config.sections, Mapping)

    for section_name, entries in config.sections.items():
        assert isinstance(section_name, str)
        assert section_name == section_name.strip()
        assert section_name != ""
        assert isinstance(entries, Mapping)

        for key, value in entries.items():
            assert isinstance(key, str)
            assert key == key.strip()
            assert key != ""
            assert isinstance(value, str)


def assert_structured_parse_error(error: ParseError) -> None:
    assert isinstance(error.message, str)
    assert error.message.strip()

    line = getattr(error, "line", getattr(error, "line_number", None))
    column = getattr(error, "column", getattr(error, "column_number", None))
    assert isinstance(line, int)
    assert line >= 1
    assert isinstance(column, int)
    assert column >= 1


@given(source=st.text())
@settings(max_examples=200, deadline=None)
def test_parse_config_returns_valid_config_or_structured_error_for_arbitrary_text(source: str) -> None:
    result = parse_config(source)

    assert isinstance(result, (Config, ParseError))
    if isinstance(result, Config):
        assert_valid_config(result)
    else:
        assert_structured_parse_error(result)


@given(source=valid_config_texts())
@settings(max_examples=100, deadline=None)
def test_parse_config_accepts_generated_valid_configs(source: str) -> None:
    result = parse_config(source)

    if isinstance(result, ParseError):
        pytest.fail(f"expected generated valid config to parse, got {result!r}")
    assert isinstance(result, Config)
    assert result.sections
    assert_valid_config(result)


def test_parse_config_preserves_sections_keys_and_values() -> None:
    result = parse_config("[server]\nhost=localhost\nport=8080\n\n[features]\nenabled=true\n")

    assert isinstance(result, Config)
    assert result.sections == {
        "server": {"host": "localhost", "port": "8080"},
        "features": {"enabled": "true"},
    }
    assert_valid_config(result)


@pytest.mark.parametrize(
    "source",
    [
        "[",
        "[]\nname=value\n",
        "[server]\n=value\n",
        "[server]\nmissing-separator\n",
    ],
)
def test_parse_config_returns_structured_errors_for_malformed_configs(source: str) -> None:
    result = parse_config(source)

    assert isinstance(result, ParseError)
    assert_structured_parse_error(result)
