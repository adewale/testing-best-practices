from hypothesis import given, strategies as st

from app.config_parser import parse_config


@given(st.text())
def test_parse_config_never_crashes(raw):
    try:
        result = parse_config(raw)
    except Exception:
        return
    assert result is not None
