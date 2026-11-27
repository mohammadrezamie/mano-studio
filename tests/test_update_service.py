import io
import json
import pytest
import update_service
from update_service import check_updates, release_info, version_key, RELEASES_URL


def response(rows):
    def fake(request, timeout):
        assert request.full_url == RELEASES_URL
        assert timeout == 6
        return io.BytesIO(json.dumps(rows).encode())
    return fake


def test_no_network_without_explicit_request():
    def forbidden(*args, **kwargs):
        pytest.fail("Network called without authorization")
    with pytest.raises(PermissionError):
        check_updates(opener=forbidden)
    with pytest.raises(PermissionError):
        release_info(opener=forbidden)


@pytest.mark.parametrize('current,expected', [('1.0.0', 'v1.0.2'), ('1.0.1-beta.1', 'v1.1.0-beta.10')])
def test_mixed_channels(monkeypatch, current, expected):
    monkeypatch.setattr(update_service, 'VERSION', current)
    rows = [
        {'tag_name': 'v1.0.2', 'draft': False, 'prerelease': False},
        {'tag_name': 'v1.1.0-beta.2', 'draft': False, 'prerelease': True},
        {'tag_name': 'v1.1.0-beta.10', 'draft': False, 'prerelease': True},
        {'tag_name': 'v9.0.0', 'draft': True, 'prerelease': False},
        {'tag_name': 'v8.0.0', 'draft': False, 'prerelease': True},
        {'tag_name': 'v8.0.0-beta.1', 'draft': False, 'prerelease': False},
        {'tag_name': 'v7.0.0', 'draft': False},
        {'tag_name': 'v6.0.0-dev.1', 'draft': False, 'prerelease': True},
    ]
    assert check_updates(explicit=True, opener=response(rows)) == expected
    assert version_key('0.3.0') > version_key('0.3.0-rc.1')


@pytest.mark.parametrize('current,tag,prerelease', [('1.0.0', 'v2.0.0-beta.1', True),
    ('1.0.0-beta.1', 'v2.0.0', False), ('1.0.0', 'v1.0.0', False)])
def test_no_matching_release(monkeypatch, current, tag, prerelease):
    monkeypatch.setattr(update_service, 'VERSION', current)
    assert check_updates(explicit=True, opener=response([
        {'tag_name': tag, 'draft': False, 'prerelease': prerelease}])) is None


def test_no_release():
    assert check_updates(explicit=True, opener=response([])) is None


def test_release_metadata_and_size_bound(monkeypatch):
    monkeypatch.setattr(update_service, 'VERSION', '1.0.0')
    payload = [{'tag_name': 'v1.0.1', 'draft': False, 'prerelease': False, 'body': '<b>notes</b>',
                'assets': [{'name': 'ManoStudio-Setup.exe', 'size': 1048576}]}]
    info = release_info(explicit=True, opener=response(payload))
    assert info.tag == 'v1.0.1' and info.notes == '<b>notes</b>' and info.installer_size == 1048576
    with pytest.raises(ValueError, match='too large'):
        release_info(explicit=True, opener=lambda *a, **k: io.BytesIO(b' ' * 2_000_001))


def test_invalid_response():
    with pytest.raises(ValueError, match='Invalid release response'):
        release_info(explicit=True, opener=response({}))


@pytest.mark.parametrize("target", ["https://example.org/releases", "http://api.github.com/repos/x/y/releases", "https://api.github.com/repos/other/repo/releases"])
def test_release_metadata_redirect_rejected(target):
    with pytest.raises(ValueError, match="metadata redirect"):
        update_service.NoMetadataRedirect().redirect_request(None, None, 302, "", {}, target)


def test_default_opener_uses_no_redirect_policy(monkeypatch):
    class FakeOpener:
        open = staticmethod(response([]))
    def fake_build(handler):
        assert isinstance(handler, update_service.NoMetadataRedirect)
        return FakeOpener()
    monkeypatch.setattr(update_service, "build_opener", fake_build)
    assert release_info(explicit=True) is None
