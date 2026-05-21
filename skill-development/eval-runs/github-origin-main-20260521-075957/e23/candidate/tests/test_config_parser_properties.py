"""Property tests for the config parser trust boundary."""

from __future__ import annotations

import dataclasses
import importlib
from collections.abc import Mapping, Sequence
from types import ModuleType
from typing import Any, Callable

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st


def _load_parser_api() -> tuple[Callable[[str], object], type, type]:
    """Find the project's parser API without hiding import failures."""

    module_names = (
        "config_parser",
        "config_parser.parser",
        "parser",
        "config",
        "app.config_parser",
        "src.config_parser",
    )
    parse_names = ("parse_config", "parse", "loads", "parse_text")

    import_errors: dict[str, str] = {}
    shape_errors: dict[str, str] = {}
    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            import_errors[module_name] = str(exc)
            continue

        parse_func = _first_attr(module, parse_names)
        config_type = getattr(module, "Config", None)
        parse_error_type = getattr(module, "ParseError", None)
        if callable(parse_func) and isinstance(config_type, type) and isinstance(parse_error_type, type):
            return parse_func, config_type, parse_error_type

        shape_errors[module_name] = (
            f"parse callable={callable(parse_func)}, "
            f"Config type={isinstance(config_type, type)}, "
            f"ParseError type={isinstance(parse_error_type, type)}"
        )

    raise ImportError(
        "Could not find a parser module exposing parse_config/parse, Config, and ParseError. "
        f"Import errors: {import_errors}. Shape errors: {shape_errors}."
    )


def _first_attr(module: ModuleType, names: tuple[str, ...]) -> Any:
    for name in names:
        if hasattr(module, name):
            return getattr(module, name)
    return None


parse_config, Config, ParseError = _load_parser_api()

_CONFIG_KEYS = st.from_regex(r"[A-Za-z][A-Za-z0-9_-]{0,31}", fullmatch=True)
_CONFIG_VALUES = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._/:+-",
    min_size=1,
    max_size=64,
)


@given(text=st.text(max_size=8_192))
@settings(max_examples=250, deadline=None)
def test_arbitrary_text_returns_config_or_structured_parse_error(text: str) -> None:
    result = parse_config(text)

    assert isinstance(result, (Config, ParseError))
    assert not isinstance(result, tuple)
    if isinstance(result, Config):
        _assert_config_invariants(result)
    else:
        _assert_parse_error_is_structured(result)


@pytest.mark.parametrize(
    "text",
    [
        "name = demo\n",
        "host = localhost\nport = 5432\nenabled = true\n",
        "# comment-only lines are ignored\nname = demo\n\n# trailing comment\n",
    ],
)
def test_basic_valid_key_value_configs_return_config(text: str) -> None:
    result = parse_config(text)

    assert isinstance(result, Config)
    assert not isinstance(result, ParseError)
    _assert_config_invariants(result)


@given(settings_map=st.dictionaries(_CONFIG_KEYS, _CONFIG_VALUES, min_size=1, max_size=25))
@settings(max_examples=150, deadline=None)
def test_generated_valid_key_value_configs_preserve_settings(settings_map: dict[str, str]) -> None:
    text = "".join(f"{key} = {value}\n" for key, value in settings_map.items())
    result = parse_config(text)

    assert isinstance(result, Config)
    assert not isinstance(result, ParseError)
    _assert_config_invariants(result)
    parsed_settings = _settings_mapping(result)
    assert set(parsed_settings) == set(settings_map)
    for key, value in settings_map.items():
        assert str(parsed_settings[key]) == value


@pytest.mark.parametrize(
    "text",
    [
        "= value\n",
        "   = value\n",
        "name = demo\n= orphaned value\n",
    ],
)
def test_empty_keys_are_reported_as_structured_parse_errors(text: str) -> None:
    result = parse_config(text)

    assert isinstance(result, ParseError)
    assert not isinstance(result, Config)
    _assert_parse_error_is_structured(result)


def _assert_config_invariants(config: object) -> None:
    fields = _public_fields(config)
    settings_mapping = _settings_mapping(config)

    assert fields, "Config should expose parsed data as public fields"
    assert isinstance(settings_mapping, Mapping)
    for value in fields.values():
        _assert_no_invalid_mapping_keys(value)


def _settings_mapping(config: object) -> Mapping[str, object]:
    fields = _public_fields(config)
    for field_name in ("settings", "values", "entries", "data", "config"):
        value = fields.get(field_name)
        if isinstance(value, Mapping):
            return value
    for value in fields.values():
        if isinstance(value, Mapping):
            return value
    raise AssertionError("Config should contain a mapping of parsed settings")


def _assert_no_invalid_mapping_keys(value: object) -> None:
    if isinstance(value, Mapping):
        seen: set[str] = set()
        for key, item in value.items():
            assert isinstance(key, str)
            assert key == key.strip()
            assert key != ""
            assert key not in seen
            seen.add(key)
            assert item is not None
            _assert_no_invalid_mapping_keys(item)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            _assert_no_invalid_mapping_keys(item)


def _assert_parse_error_is_structured(error: object) -> None:
    fields = _public_fields(error)
    message = fields.get("message") or fields.get("msg") or (error.args[0] if isinstance(error, Exception) and error.args else None)
    line = fields.get("line") or fields.get("line_number") or fields.get("lineno")
    column = fields.get("column") or fields.get("col") or fields.get("offset")

    assert fields, "ParseError should expose structured diagnostic fields"
    assert isinstance(message, str)
    assert message.strip()
    assert isinstance(line, int) and line >= 1
    assert column is None or (isinstance(column, int) and column >= 1)


def _public_fields(obj: object) -> dict[str, Any]:
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, Mapping):
        return dict(obj)
    if hasattr(obj, "__dict__"):
        return {key: value for key, value in vars(obj).items() if not key.startswith("_")}
    return {}
