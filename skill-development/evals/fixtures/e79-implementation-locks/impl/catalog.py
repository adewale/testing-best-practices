import hashlib
import json


def export_items(items):
    return json.dumps({"items": items}, separators=(",", ":"))


def verify_resource(payload, expected_sha256):
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise ValueError("resource integrity mismatch")
    return payload
