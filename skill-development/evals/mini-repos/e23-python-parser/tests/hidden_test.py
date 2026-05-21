import importlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
module = importlib.import_module(('mutant' if os.environ.get('IMPL') == 'mutant' else 'good') + '.parser')

for raw in ['', '!', 'name=value', '  =missing', 'x=1']:
    try:
        result = module.parse_config(raw)
    except Exception as exc:
        raise AssertionError(f'parse_config crashed for {raw!r}: {exc}')
    if isinstance(result, module.Config):
        assert result.name.strip() == result.name
        assert result.name
        assert result.settings
    else:
        assert isinstance(result, module.ParseError)
        assert result.message
        assert result.kind in {'syntax', 'missing-name', 'invalid-setting'}
        assert result.span.start <= result.span.end
