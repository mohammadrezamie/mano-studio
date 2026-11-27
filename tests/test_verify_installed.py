import shutil
import pytest
from installer.verify_installed import verify


@pytest.fixture
def payload(tmp_path):
    frozen, installed = tmp_path / "frozen", tmp_path / "installed"
    (frozen / "_internal").mkdir(parents=True)
    (frozen / "ManoStudio.exe").write_bytes(b"application")
    (frozen / "_internal" / "Qt6Core.dll").write_bytes(b"library")
    (frozen / "_internal" / "rtl_translator.py").write_bytes(b"source")
    shutil.copytree(frozen, installed)
    (installed / "unins000.exe").write_bytes(b"uninstaller")
    (installed / "unins000.dat").write_bytes(b"uninstall-data")
    return frozen, installed


def test_exact_installed_payload(payload):
    frozen, installed = payload
    report = verify(frozen, installed)
    assert report["result"] == "PASS" and report["files"] == 3
    assert len(report["payload_sha256"]) == 64
    assert not report["native_acceptance"]
    assert report == verify(frozen, installed)


@pytest.mark.parametrize("damage", ["missing", "changed", "extra", "uninstaller", "reserved"])
def test_reject_payload_mismatch(payload, damage):
    frozen, installed = payload
    if damage == "missing":
        (installed / "_internal" / "rtl_translator.py").unlink()
    elif damage == "changed":
        (installed / "_internal" / "Qt6Core.dll").write_bytes(b"changed")
    elif damage == "extra":
        (installed / "unknown.dll").write_bytes(b"extra")
    elif damage == "uninstaller":
        (installed / "unins000.dat").unlink()
    else:
        (frozen / "unins000.exe").write_bytes(b"reserved")
    with pytest.raises(ValueError):
        verify(frozen, installed)


def test_reject_link(payload):
    frozen, installed = payload
    try:
        (installed / "linked.dll").symlink_to(frozen / "ManoStudio.exe")
    except OSError:
        pytest.skip("Symlinks unavailable for this account")
    with pytest.raises(ValueError, match="linked"):
        verify(frozen, installed)
