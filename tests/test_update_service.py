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
            {"tag_name": "v1.1.0-beta.2", "draft": False},
            {"tag_name": "v1.1.0-beta.10", "draft": False},
            {"tag_name": "v9.0.0", "draft": True},
            {"tag_name": "invalid", "draft": False},
        ]).encode())
    assert check_updates(explicit=True, opener=fake) == "v1.1.0-beta.10"
    assert version_key("0.3.0") > version_key("0.3.0-rc.1")


def test_no_release():
    assert check_updates(explicit=True, opener=lambda *a, **k: io.BytesIO(b"[]")) is None


def test_release_metadata_and_size_bound():
    from update_service import release_info
    payload = [{"tag_name":"v1.0.1","draft":False,"body":"<b>notes</b>",
                "assets":[{"name":"ManoStudio-Setup.exe","size":1048576}]}]
    info=release_info(explicit=True,opener=lambda *a,**k:io.BytesIO(json.dumps(payload).encode()))
    assert info.tag=="v1.0.1" and info.notes=="<b>notes</b>" and info.installer_size==1048576
    with pytest.raises(ValueError,match="too large"):
        release_info(explicit=True,opener=lambda *a,**k:io.BytesIO(b" "*2_000_001))

def test_release_details_no_network_without_request():
    from update_service import release_info
    with pytest.raises(PermissionError):
        release_info(opener=lambda *a,**k:pytest.fail("Unexpected network"))
