import json
from pathlib import Path

from app.api_client import parse_user_response


def test_api_client_matches_recorded_provider_shape():
    fixture = json.loads(Path('tests/fixtures/api/user.ok.json').read_text())

    assert fixture['statusCode'] == 200
    assert 'status' not in fixture
    user = parse_user_response(fixture)
    assert user.id == 'user_123'
    assert user.email == 'a@example.com'
