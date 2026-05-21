from dataclasses import dataclass

@dataclass
class Span:
    start: int
    end: int

@dataclass
class Config:
    name: str
    settings: dict[str, str]

@dataclass
class ParseError:
    kind: str
    message: str
    span: Span


def parse_config(raw: str):
    if '=' not in raw:
        return ParseError('syntax', 'missing key/value separator', Span(0, len(raw)))
    key, value = raw.split('=', 1)
    key = key.strip()
    if not key:
        return ParseError('missing-name', 'empty key', Span(0, len(raw)))
    return Config(name=key, settings={key: value.strip()})
