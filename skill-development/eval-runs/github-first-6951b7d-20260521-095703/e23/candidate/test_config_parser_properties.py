"""Property-based tests for the config parser contract."""

from __future__ import annotations

import importlib
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass

from hypothesis import example, given, settings
from hypothesis import strategies as st


MODULE_CANDIDATES = (
    "config_parser",
    "parser",
    "config",
    "src.config_parser",
    "src.parser",
    "app.config_parser",
)
PARSE_FUNCTION_CANDIDATES = ("parse_config", "parse", "loads", "parse_text")


def _load_parser_api():
    tried = []
    for module_name in MODULE_CANDIDATES:
        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            tried.append(f"{module_name}: {exc}")
            continue

        parse_config = next(
            (
                getattr(module, name)
                for name in PARSE_FUNCTION_CANDIDATES
                if callable(getattr(module, name, None))
            ),
            None,
        )
        config_type = getattr(module, "Config", None)
        parse_error_type = getattr(module, "ParseError", None)
        if parse_config and config_type and parse_error_type:
            return parse_config, config_type, parse_error_type
        tried.append(f"{module_name}: missing parse function, Config, or ParseError")

    raise AssertionError("Could not locate config parser API. Tried: " + "; ".join(tried))


parse_config, Config, ParseError = _load_parser_api()


def _as_public_mapping(obj):
    if isinstance(obj, Mapping):
        return obj
    if is_dataclass(obj):
        return asdict(obj)
    if hasattr(obj, "_asdict"):
        return obj._asdict()

    fields = {}
    if hasattr(obj, "__dict__"):
        fields.update(vars(obj))
    for cls in type(obj).__mro__:
        slots = getattr(cls, "__slots__", ())
        if isinstance(slots, str):
            slots = (slots,)
        for name in slots:
            if name.startswith("_") or not hasattr(obj, name):
                continue
            fields[name] = getattr(obj, name)
    for name in (
        "message",
        "msg",
        "reason",
        "error",
        "line",
        "line_number",
        "lineno",
        "column",
        "col",
        "position",
        "pos",
        "offset",
        "index",
    ):
        if hasattr(obj, name):
            fields.setdefault(name, getattr(obj, name))

    return {name: value for name, value in fields.items() if not name.startswith("_") and not callable(value)}


def _config_to_nested_mapping(config):
    if isinstance(config, Mapping):
        return config

    for attr_name in ("sections", "data", "values", "entries"):
        if hasattr(config, attr_name):
            value = getattr(config, attr_name)
            if isinstance(value, Mapping):
                return value

    sections = getattr(config, "sections", None)
    items = getattr(config, "items", None)
    if callable(sections) and callable(items):
        return {section: dict(items(section)) for section in sections()}

    public_mapping = _as_public_mapping(config)
    nested = next(
        (value for value in public_mapping.values() if isinstance(value, Mapping)),
        None,
    )
    assert nested is not None, "Config should expose a mapping of sections to keys"
    return nested


def _lookup_value(config, section, key):
    nested = _config_to_nested_mapping(config)
    if section in nested and isinstance(nested[section], Mapping) and key in nested[section]:
        return nested[section][key]

    get_value = getattr(config, "get", None)
    if callable(get_value):
        return get_value(section, key)

    raise AssertionError(f"Missing expected config value {section}.{key}")


def _assert_config_invariants(result):
    assert isinstance(result, Config)
    assert not isinstance(result, ParseError)

    sections = _config_to_nested_mapping(result)
    assert isinstance(sections, Mapping)
    for section_name, section_values in sections.items():
        assert isinstance(section_name, str)
        assert section_name.strip() == section_name and section_name != ""
        assert isinstance(section_values, Mapping)
        for key, value in section_values.items():
            assert isinstance(key, str)
            assert key.strip() == key and key != ""
            assert value is not None


def _assert_parse_error_invariants(result, source):
    assert isinstance(result, ParseError)
    assert not isinstance(result, Config)

    fields = _as_public_mapping(result)
    assert fields, "ParseError should expose structured diagnostic fields"

    message = next(
        (fields[name] for name in ("message", "msg", "reason", "error") if name in fields),
        None,
    )
    assert isinstance(message, str)
    assert message.strip() != ""

    line = next((fields[name] for name in ("line", "line_number", "lineno") if name in fields), None)
    column = next((fields[name] for name in ("column", "col") if name in fields), None)
    position = next((fields[name] for name in ("position", "pos", "offset", "index") if name in fields), None)
    assert line is not None or position is not None
    if line is not None:
        assert isinstance(line, int)
        assert 1 <= line <= source.count("\n") + 1
    if column is not None:
        assert isinstance(column, int)
        assert column >= 1
    if position is not None:
        assert isinstance(position, int)
        assert 0 <= position <= len(source)


def _assert_parser_contract(source):
    result = parse_config(source)
    assert isinstance(result, (Config, ParseError))
    if isinstance(result, Config):
        _assert_config_invariants(result)
    else:
        _assert_parse_error_invariants(result, source)


SAFE_IDENTIFIER = st.from_regex(r"[A-Za-z][A-Za-z0-9_]{0,20}", fullmatch=True)
SAFE_VALUE = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _./:-",
    min_size=1,
    max_size=40,
).filter(lambda value: value == value.strip())


@st.composite
def valid_config_documents(draw):
    expected = draw(
        st.dictionaries(
            SAFE_IDENTIFIER,
            st.dictionaries(SAFE_IDENTIFIER, SAFE_VALUE, min_size=1, max_size=4),
            min_size=1,
            max_size=4,
        )
    )
    lines = []
    for section, values in expected.items():
        lines.append(f"[{section}]")
        for key, value in values.items():
            lines.append(f"{key} = {value}")
        lines.append("")
    return "\n".join(lines), expected


@example("")
@example("[")
@example("\x00\udcff")
@given(st.text())
@settings(max_examples=200, deadline=None)
def test_arbitrary_text_returns_config_or_structured_parse_error(source):
    _assert_parser_contract(source)


def test_simple_ini_document_returns_config_with_expected_values():
    source = "\n".join(
        [
            "[database]",
            "host = localhost",
            "port = postgres",
            "",
            "[feature_flags]",
            "new_ui = enabled",
            "",
        ]
    )

    result = parse_config(source)

    _assert_config_invariants(result)
    assert _lookup_value(result, "database", "host") == "localhost"
    assert _lookup_value(result, "database", "port") == "postgres"
    assert _lookup_value(result, "feature_flags", "new_ui") == "enabled"


@given(valid_config_documents())
@settings(max_examples=100, deadline=None)
def test_generated_valid_documents_parse_and_preserve_values(document):
    source, expected = document

    result = parse_config(source)

    _assert_config_invariants(result)
    for section, values in expected.items():
        for key, value in values.items():
            assert _lookup_value(result, section, key) == value


def test_malformed_document_returns_structured_parse_error_not_exception():
    source = "\n".join(
        [
            "[database",
            "host = localhost",
            "",
            "[feature_flags]",
            "= enabled",
        ]
    )

    result = parse_config(source)

    _assert_parse_error_invariants(result, source)
