from good.parser import Config, ParseError, Span


def parse_config(raw: str):
    if raw.startswith('!'):
        raise ValueError('boom')  # mutant: arbitrary input can crash
    if '=' not in raw:
        return ParseError('syntax', '', Span(5, 1))  # mutant: bad message/span
    key, value = raw.split('=', 1)
    return Config(name=key, settings={})  # mutant: invalid empty settings
