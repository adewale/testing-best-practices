import json
from pathlib import Path

import requests

import api_client


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "provider_user.success.json"


class RecordedResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.headers = {"content-type": "application/json"}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"recorded response returned {self.status_code}")


def load_recorded_provider_user():
    with FIXTURE_PATH.open(encoding="utf-8") as fixture:
        return json.load(fixture)


def assert_current_provider_user_contract(payload):
    # This fixture is a sanitized recording of the provider response body.
    # Keep this assertion aligned with the provider docs / re-recorded response so
    # stale hand-written mocks using the old field name cannot keep passing.
    required_fields = {"id", "display_name", "email", "account_status"}
    legacy_fields = {"name"}

    assert required_fields <= payload.keys()
    assert payload.keys().isdisjoint(legacy_fields)
    assert isinstance(payload["id"], str) and payload["id"]
    assert isinstance(payload["display_name"], str) and payload["display_name"]
    assert "@" in payload["email"]
    assert payload["account_status"] in {"active", "suspended", "deleted"}


def result_field(result, *names):
    for name in names:
        if isinstance(result, dict) and name in result:
            return result[name]
        if hasattr(result, name):
            return getattr(result, name)
    raise AssertionError(f"result does not expose any of: {', '.join(names)}")


def public_fetch_user_function():
    for name in ("get_user", "fetch_user", "get_user_profile", "fetch_user_profile"):
        if hasattr(api_client, name):
            return getattr(api_client, name)
    raise AssertionError("api_client should expose a public user-fetching function")


def test_recorded_provider_fixture_uses_current_shape_not_legacy_mock_shape():
    recorded = load_recorded_provider_user()

    assert_current_provider_user_contract(recorded)


def test_client_maps_recorded_provider_shape_without_live_network(monkeypatch):
    recorded = load_recorded_provider_user()
    assert_current_provider_user_contract(recorded)
    requests_seen = []

    def replay_recorded_response(url, **kwargs):
        requests_seen.append((url, kwargs))
        return RecordedResponse(recorded)

    monkeypatch.setattr(requests, "get", replay_recorded_response)
    if hasattr(api_client, "requests"):
        monkeypatch.setattr(api_client.requests, "get", replay_recorded_response)

    result = public_fetch_user_function()(recorded["id"])

    assert requests_seen, "client should use the replayed fixture instead of live network"
    assert result_field(result, "id", "user_id") == recorded["id"]
    assert result_field(result, "display_name", "name") == recorded["display_name"]
    assert result_field(result, "email") == recorded["email"]
    assert result_field(result, "account_status", "status") == recorded["account_status"]
