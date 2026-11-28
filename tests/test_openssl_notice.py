import hashlib
import json
from pathlib import Path
import pytest
from installer.openssl_notice import collect, LICENSES


def test_known_runtime_license_is_copied_unmodified(tmp_path):
    root = tmp_path / "frozen"
    root.mkdir()
    (root / "libcrypto-3.dll").write_bytes(b"fixture OpenSSL 3.5.9")
    (root / "libssl-3.dll").write_bytes(b"fixture")
    out = tmp_path / "notices"
    result = collect(root, out)
    record = result["licenses"][0]
    data = (out / record["file"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == record["sha256"]
    assert hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest() == LICENSES["3.5.9"]
    assert len(result["binaries"]) == 2
    assert not result["redistribution_approved"]
    assert json.loads((out / "evidence.json").read_text()) == result


def test_unknown_version_is_flagged_not_mislabeled(tmp_path):
    (tmp_path / "libcrypto-3.dll").write_bytes(b"OpenSSL 9.9.9")
    result = collect(tmp_path, tmp_path / "notices")
    assert not result["licenses"] and result["warnings"]


def test_modified_license_is_rejected(tmp_path):
    (tmp_path / "libcrypto-3.dll").write_bytes(b"OpenSSL 3.5.9")
    fake = tmp_path / "fake"
    fake.mkdir()
    (fake / "openssl-3.5.9-LICENSE.txt").write_text("not the upstream license")
    with pytest.raises(ValueError, match="license text changed"):
        collect(tmp_path, tmp_path / "out", fake)
