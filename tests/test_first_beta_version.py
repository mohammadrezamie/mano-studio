"""Candidate v1 version and update-boundary tests."""
import io
import json
from update_service import VERSION, check_updates, version_key


def _check(tags):
    payload = [{"tag_name": tag, "draft": False, "prerelease": "-" in tag} for tag in tags]
    return check_updates(explicit=True,
        opener=lambda *a, **k: io.BytesIO(json.dumps(payload).encode()))


def test_v1_version_and_no_self_update():
    assert VERSION == "1.0.0"
    assert _check(["v0.3.0-beta.1", "v1.0.0-rc.1", "v1.0.0"]) is None


def test_future_version_and_stable_order():
    assert _check(["v1.0.0", "v1.0.1"]) == "v1.0.1"
    assert version_key("1.0.0") > version_key("1.0.0-rc.1")
