from hypothesis import given, strategies as st

from app.config_parser import Config, ParseError, parse_config


@given(st.text())
def test_parse_config_returns_config_or_structured_error(raw: str) -> None:
    result = parse_config(raw)

    if isinstance(result, Config):
        assert result.name.strip() == result.name
        assert len(result.settings) >= 1
        assert all(key for key in result.settings)
    else:
        assert isinstance(result, ParseError)
        assert result.message
        assert result.kind in {"syntax", "missing-name", "invalid-setting"}
        assert result.span.start <= result.span.end
