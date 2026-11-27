from update_service import VERSION, CHANNEL
from release_channel import channel, version_key, eligible_release
from installer.version_policy import allowed


def test_stable_maintenance_is_next_patch():
    assert VERSION == "1.0.1"
    assert CHANNEL == "stable"
    assert channel(VERSION) == "stable"
    assert version_key(VERSION) > version_key("1.0.0")
    assert allowed(VERSION)
    assert allowed("1.0.0")
    assert allowed("1.0.2")


def test_stable_track_rejects_prereleases_and_beta():
    assert eligible_release({"tag_name":"v1.0.2","draft":False,"prerelease":False}, VERSION)
    assert eligible_release({"tag_name":"v1.1.0-beta.3","draft":False,"prerelease":True}, VERSION) is None
    assert not allowed("1.0.2-beta.1")
