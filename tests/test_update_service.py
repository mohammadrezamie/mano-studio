import io
import json
import pytest
from update_service import check_updates, version_key, RELEASES_URL


def test_no_network_without_explicit_request():
    def forbidden(*args, **kwargs):
        pytest.fail("Network called without authorization")
    with pytest.raises(PermissionError):
        check_updates(opener=forbidden)


def test_explicit_check_and_beta_order():
    def fake(request, timeout):
        assert request.full_url == RELEASES_URL
        assert timeout == 6
        return io.BytesIO(json.dumps([
            {"tag_name": "v0.3.0-beta.2", "draft": False},
            {"tag_name": "v0.3.0-beta.10", "draft": False},
            {"tag_name": "v9.0.0", "draft": True},
            {"tag_name": "invalid", "draft": False},
        ]).encode())
    assert check_updates(explicit=True, opener=fake) == "v0.3.0-beta.10"
    assert version_key("0.3.0") > version_key("0.3.0-rc.1")


def test_no_release():
    assert check_updates(explicit=True, opener=lambda *a, **k: io.BytesIO(b"[]")) is None
