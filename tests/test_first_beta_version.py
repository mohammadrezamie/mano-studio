"""Release-specific checks for the proposed beta's update boundary."""
import io
import json
from update_service import VERSION, check_updates


def _check(tags):
    payload = [{"tag_name": tag, "draft": False} for tag in tags]
    return check_updates(explicit=True,
        opener=lambda *a, **k: io.BytesIO(json.dumps(payload).encode()))


def test_first_beta_version_and_no_self_update():
    assert VERSION == "0.3.0-beta.1"
    assert _check(["v0.3.0-dev.1", "v0.3.0-alpha.9", "v0.3.0-beta.1"]) is None


def test_future_beta_and_stable_order():
    assert _check(["v0.3.0-beta.1", "v0.3.0-beta.2"]) == "v0.3.0-beta.2"
    assert _check(["v0.3.0-beta.2", "v0.3.0-rc.1", "v0.3.0"]) == "v0.3.0"
