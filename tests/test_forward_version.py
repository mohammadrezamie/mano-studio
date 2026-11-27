from update_service import VERSION, CHANNEL
from release_channel import channel, version_key, eligible_release


def test_forward_beta_version_is_after_first_candidate():
    assert VERSION == "1.1.0-beta.2"
    assert CHANNEL == "beta"
    assert version_key(VERSION) > version_key("1.1.0-beta.1")
    assert channel(VERSION) == "beta"


def test_beta_track_only_accepts_newer_beta_or_rc():
    assert eligible_release({"tag_name":"v1.1.0-beta.3","draft":False,"prerelease":True}, VERSION)
    assert eligible_release({"tag_name":"v1.1.0-rc.1","draft":False,"prerelease":True}, VERSION)
    assert eligible_release({"tag_name":"v1.0.1","draft":False,"prerelease":False}, VERSION) is None
