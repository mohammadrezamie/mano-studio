import hashlib
import struct
import zipfile
import pytest
from installer.candidate_manifest import validate


SHA = "a" * 40


def pe(machine=0x8664):
    header = bytearray(64)
    header[:2] = b"MZ"
    struct.pack_into("<I", header, 60, 64)
    return bytes(header) + b"PE\0\0" + struct.pack("<H", machine)


def checksum(path):
    path.with_name(path.name + ".sha256").write_text(hashlib.sha256(path.read_bytes()).hexdigest())


@pytest.fixture
def candidate(tmp_path):
    root = tmp_path
    (root / "update_service.py").write_text('VERSION = "0.3.0-dev.1"\n')
    (root / "rtl_translator.py").write_bytes(b"# academic source\n")
    portable = root / "portable-output"
    setup = root / "installer" / "output"
    for folder in (portable, setup):
        folder.mkdir(parents=True)
        (folder / "commit.txt").write_text("SHA=" + SHA)
        (folder / "portable-smoke.txt").write_text("PASS\n")
        (folder / "build-dependencies.txt").write_text("PySide6==6.8.0\n")
    (setup / "installed-smoke.txt").write_text("PASS\n")
    z = portable / "ManoStudio-v0.3.0-dev.1-Windows-x64.zip"
    with zipfile.ZipFile(z, "w") as archive:
        archive.writestr("ManoStudio/ManoStudio.exe", pe())
        archive.writestr("ManoStudio/_internal/rtl_translator.py", (root / "rtl_translator.py").read_bytes())
    exe = setup / "ManoStudio-Setup-v0.3.0-dev.1-x64.exe"
    exe.write_bytes(pe(0x14c))
    checksum(z)
    checksum(exe)
    return root, z, exe


def test_candidate_evidence(candidate):
    root, z, exe = candidate
    record = validate(root, SHA)
    assert record["source_sha"] == SHA
    assert record["portable_smoke"] == record["installed_smoke"] == "PASS"
    assert not record["public_release"] and not record["native_acceptance"]
    assert {a["name"] for a in record["assets"]} == {z.name, exe.name}


@pytest.mark.parametrize("damage", ["sha", "smoke", "digest", "source", "arch", "version", "setup"])
def test_reject_invalid_evidence(candidate, damage):
    root, z, exe = candidate
    if damage == "sha":
        (root / "portable-output" / "commit.txt").write_text("SHA=" + "b"*40)
    elif damage == "smoke":
        (root / "installer" / "output" / "installed-smoke.txt").write_text("FAIL")
    elif damage == "digest":
        exe.write_bytes(pe() + b"tampered")
    elif damage == "source":
        (root / "rtl_translator.py").write_bytes(b"different")
    elif damage == "arch":
        with zipfile.ZipFile(z, "w") as archive:
            archive.writestr("ManoStudio/ManoStudio.exe", pe(0x14c))
            archive.writestr("ManoStudio/_internal/rtl_translator.py", (root / "rtl_translator.py").read_bytes())
        checksum(z)
    elif damage == "version":
        (root / "update_service.py").write_text('VERSION = "1.0.0"')
    elif damage == "setup":
        exe.write_bytes(b"not an executable")
        checksum(exe)
    with pytest.raises(ValueError):
        validate(root, SHA)
