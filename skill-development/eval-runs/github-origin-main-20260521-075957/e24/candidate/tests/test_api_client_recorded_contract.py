"""Regression tests for provider response-shape drift.

These tests replay a recorded provider response through a real requests.Session
adapter instead of monkeypatching requests.get with a hand-written dict. Normal
CI has no live network dependency; refresh the JSON recording in a separate,
reviewed contract job when the provider API changes.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
import requests

# Update only this import/adapter name if the project exposes a different API
# client class; keep the recorded-fixture behavior below unchanged.
from api_client import ApiClient

try:
    from api_client import ProviderContractError
except ImportError:
    ProviderContractError = ValueError


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "provider_user_success.json"
REQUIRED_PROVIDER_FIELDS = {"id", "display_name", "email", "status", "updated_at"}
STALE_PROVIDER_FIELDS = {"name"}
CONTRACT_ERRORS = (KeyError, ProviderContractError, TypeError, ValueError)


class RecordedApiAdapter(requests.adapters.BaseAdapter):
    """Replay one recorded provider interaction as a real requests.Response."""

    def __init__(self, recording: dict[str, Any]) -> None:
        self.recording = recording
        self.requests: list[requests.PreparedRequest] = []

    def send(self, request: requests.PreparedRequest, **_: Any) -> requests.Response:
        expected = self.recording["request"]
        assert request.method == expected["method"]
        assert request.url == expected["url"]
        self.requests.append(request)

        recorded_response = self.recording["response"]
        response = requests.Response()
        response.status_code = recorded_response["status_code"]
        response.headers.update(recorded_response["headers"])
        response._content = json.dumps(recorded_response["json"]).encode("utf-8")
        response.request = request
        response.url = request.url
        return response

    def close(self) -> None:  # pragma: no cover - requests adapter API
        pass


@pytest.fixture
def provider_recording() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _recorded_session(recording: dict[str, Any]) -> tuple[requests.Session, RecordedApiAdapter]:
    adapter = RecordedApiAdapter(recording)
    session = requests.Session()
    session.mount(recording["request"]["base_url"], adapter)
    return session, adapter


def _field(model: Any, name: str) -> Any:
    if isinstance(model, dict):
        return model[name]
    return getattr(model, name)


def test_recorded_provider_payload_documents_current_wire_contract(provider_recording: dict[str, Any]) -> None:
    payload = provider_recording["response"]["json"]

    assert provider_recording["response"]["status_code"] == 200
    assert provider_recording["response"]["headers"]["Content-Type"] == "application/json"
    assert REQUIRED_PROVIDER_FIELDS <= payload.keys()
    assert STALE_PROVIDER_FIELDS.isdisjoint(payload.keys())
    assert payload["id"] == "usr_123"
    assert payload["display_name"] == "Ada Lovelace"
    assert payload["status"] in {"active", "disabled", "pending"}
    assert provider_recording["request"]["headers"].get("Authorization") == "<redacted>"


def test_client_parses_recorded_provider_shape(provider_recording: dict[str, Any]) -> None:
    payload = provider_recording["response"]["json"]
    session, adapter = _recorded_session(provider_recording)
    client = ApiClient(
        base_url=provider_recording["request"]["base_url"],
        api_key="test-token",
        session=session,
    )

    user = client.get_user(payload["id"])

    assert len(adapter.requests) == 1
    assert adapter.requests[0].method == "GET"
    assert _field(user, "id") == payload["id"]
    assert _field(user, "display_name") == payload["display_name"]
    assert _field(user, "email") == payload["email"]
    assert _field(user, "status") == payload["status"]
    assert STALE_PROVIDER_FIELDS.isdisjoint(payload.keys())


def test_client_fails_loudly_when_consumed_provider_field_drifts(provider_recording: dict[str, Any]) -> None:
    drifted_recording = copy.deepcopy(provider_recording)
    drifted_payload = drifted_recording["response"]["json"]
    drifted_payload["name"] = drifted_payload.pop("display_name")
    session, adapter = _recorded_session(drifted_recording)
    client = ApiClient(
        base_url=drifted_recording["request"]["base_url"],
        api_key="test-token",
        session=session,
    )

    with pytest.raises(CONTRACT_ERRORS) as excinfo:
        client.get_user(drifted_payload["id"])

    message = str(excinfo.value).lower()
    assert len(adapter.requests) == 1
    assert "display_name" in message or "provider" in message or "contract" in message
    assert "display_name" not in drifted_payload
    assert "name" in drifted_payload
