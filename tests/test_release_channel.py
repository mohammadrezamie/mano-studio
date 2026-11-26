import pytest
from release_channel import channel, eligible_release, version_key


@pytest.mark.parametrize('version,expected', [('1.0.0', 'stable'), ('0.8.1', 'stable'),
    ('v1.0.0-beta.2', 'beta'), ('0.3.0-dev.1', 'beta'), ('1.0.0-rc.1', 'beta')])
def test_channel(version, expected):
    assert channel(version) == expected


@pytest.mark.parametrize('current,tag,prerelease,expected', [
    ('1.0.0', 'v1.0.1', False, True),
    ('1.0.0', 'v2.0.0-beta.1', True, False),
    ('1.0.0', 'v2.0.0-beta.1', False, False),
    ('1.0.0', 'v2.0.0', True, False),
    ('1.0.0', 'v1.0.0', False, False),
    ('1.0.0', 'v0.9.9', False, False),
    ('0.3.0-dev.1', 'v0.3.0-beta.2', True, True),
    ('0.3.0-beta.2', 'v0.3.0-beta.10', True, True),
    ('0.3.0-beta.2', 'v0.3.0-beta.1', True, False),
    ('0.3.0-beta.2', 'v0.3.0-rc.1', True, True),
    ('0.3.0-beta.2', 'v0.4.0-alpha.1', True, False),
    ('0.3.0-beta.2', 'v0.4.0-dev.1', True, False),
    ('0.3.0-beta.2', 'v1.0.0', False, False),
    ('0.3.0-beta.2', 'v1.0.0', True, False),
    ('0.3.0-beta.2', 'v0.4.0-beta.1', False, False),
])
def test_release_selection(current, tag, prerelease, expected):
    result = eligible_release({'tag_name': tag, 'draft': False, 'prerelease': prerelease}, current)
    assert (result == version_key(tag)) if expected else result is None


@pytest.mark.parametrize('item', [None, [], {}, {'tag_name': '2.0.0', 'draft': False},
    {'tag_name': '2.0.0', 'prerelease': False},
    {'tag_name': '2.0.0', 'draft': True, 'prerelease': False},
    {'tag_name': '2.0.0', 'draft': 0, 'prerelease': False},
    {'tag_name': '2.0.0', 'draft': False, 'prerelease': 0},
    {'tag_name': 2, 'draft': False, 'prerelease': False},
    {'tag_name': 'invalid', 'draft': False, 'prerelease': False}])
def test_malformed(item):
    assert eligible_release(item, '1.0.0') is None


def test_next_beta_line_stays_ahead_of_stable_and_channel_isolated():
    development = "1.1.0-dev.1"
    beta = {"tag_name": "v1.1.0-beta.1", "draft": False, "prerelease": True}
    stable = {"tag_name": "v1.0.1", "draft": False, "prerelease": False}
    assert channel(development) == "beta"
    assert version_key(development) > version_key("1.0.0")
    assert eligible_release(beta, development) == version_key("v1.1.0-beta.1")
    assert eligible_release(beta, "1.0.0") is None
    assert eligible_release(stable, development) is None
