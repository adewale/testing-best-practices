import json
import os
import threading
from collections.abc import Mapping
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import requests

from api_client import ApiClient, parse_provider_user


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "provider_user_200.json"
REQUIRED_PROVIDER_FIELDS = {"id", "email", "display_name", "created_at", "account_status"}
LEGACY_PROVIDER_FIELDS = {"name", "full_name"}


def _load_recording() -> dict:
    recording = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert recording["recorded_by"] == "pytest contract recorder"
    assert recording["request"]["method"] == "GET"
    assert recording["status_code"] == 200
    assert "Authorization" not in recording["request"].get("headers", {})
    return recording


def _provider_payload() -> dict:
    return _load_recording()["body"]


def _field(model, name: str):
    if isinstance(model, Mapping):
        return model[name]
    return getattr(model, name)


def assert_provider_user_shape(payload: Mapping) -> None:
    missing = REQUIRED_PROVIDER_FIELDS - payload.keys()
    legacy = LEGACY_PROVIDER_FIELDS & payload.keys()

    assert not missing, f"provider response missing required fields: {sorted(missing)}"
    assert not legacy, f"provider response still uses legacy fields: {sorted(legacy)}"
    assert isinstance(payload["id"], str) and payload["id"].startswith("usr_")
    assert isinstance(payload["email"], str) and "@" in payload["email"]
    assert isinstance(payload["display_name"], str) and payload["display_name"].strip()
    assert payload["account_status"] in {"active", "disabled", "pending"}


def test_recorded_provider_fixture_matches_contract() -> None:
    payload = _provider_payload()

    assert_provider_user_shape(payload)
    assert payload["display_name"] == "Ada Lovelace"
    assert payload["email"] == "ada@example.test"
    assert "name" not in payload


def test_parser_maps_current_provider_field_names() -> None:
    payload = _provider_payload()

    user = parse_provider_user(payload)

    assert _field(user, "id") == "usr_123"
    assert _field(user, "email") == "ada@example.test"
    assert _field(user, "name") == payload["display_name"]
    assert _field(user, "name") != payload["id"]


def test_parser_fails_loudly_when_required_provider_field_is_missing() -> None:
    drifted_payload = dict(_provider_payload())
    drifted_payload.pop("display_name")
    drifted_payload["full_name"] = "Ada Lovelace"

    with pytest.raises((KeyError, ValueError, TypeError), match="display_name|name"):
        parse_provider_user(drifted_payload)


def _handler_for(recording: Mapping, seen_paths: list[str]):
    class RecordedProviderHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            seen_paths.append(self.path)
            expected_path = recording["request"]["path"]
            if self.path != expected_path:
                self.send_response(404)
                self.end_headers()
                return

            body = json.dumps(recording["body"]).encode("utf-8")
            self.send_response(recording["status_code"])
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return

    return RecordedProviderHandler


@pytest.fixture
def recorded_provider_server():
    recording = _load_recording()
    seen_paths: list[str] = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _handler_for(recording, seen_paths))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}", seen_paths
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def test_client_uses_recorded_provider_response_without_live_network(recorded_provider_server) -> None:
    base_url, seen_paths = recorded_provider_server
    client = ApiClient(base_url=base_url, api_key="test-token")

    user = client.get_user("usr_123")

    assert _field(user, "id") == "usr_123"
    assert _field(user, "email") == "ada@example.test"
    assert _field(user, "name") == "Ada Lovelace"
    assert seen_paths == ["/v1/users/usr_123"]


@pytest.mark.skipif(
    os.environ.get("RUN_PROVIDER_CONTRACT_TESTS") != "1",
    reason="Set RUN_PROVIDER_CONTRACT_TESTS=1 to compare the committed recording with the live provider.",
)
def test_live_provider_shape_still_matches_recorded_contract() -> None:
    live_url = os.environ["PROVIDER_USER_URL"]
    token = os.environ.get("PROVIDER_API_TOKEN")
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(live_url, headers=headers, timeout=10)
    assert response.status_code == 200

    live_payload = response.json()
    recorded_payload = _provider_payload()

    assert_provider_user_shape(live_payload)
    assert REQUIRED_PROVIDER_FIELDS <= live_payload.keys()
    assert not (LEGACY_PROVIDER_FIELDS & live_payload.keys())
    assert live_payload.keys() >= recorded_payload.keys()
