import pytest
from installer.version_policy import allowed


@pytest.mark.parametrize("version", ["1.0.0", "1.0.1", "0.3.0-beta.1", "0.3.0-dev", "0.9.1-rc.2"])
def test_allowed(version):
    assert allowed(version)


@pytest.mark.parametrize("version", [None, 1, "2.0.0", "0.3.0", "v1.0.0", "1.0.0-beta.1", "1.0.0\n", "../1.0.0"])
def test_rejected(version):
    assert not allowed(version)
