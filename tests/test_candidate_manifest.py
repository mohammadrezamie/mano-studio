import hashlib
import json
import struct
import zipfile
import pytest
from installer.candidate_manifest import validate, source_version


SHA = "a" * 40


def pe(machine=0x8664):
    header = bytearray(64)
    header[:2] = b"MZ"
    struct.pack_into("<I", header, 60, 64)
    return bytes(header) + b"PE\0\0" + struct.pack("<H", machine)


def checksum(path):
    path.with_name(path.name + ".sha256").write_text(hashlib.sha256(path.read_bytes()).hexdigest())


def rewrite_zip(path, remove=(), replace=None, add=None):
    replace = replace or {}
    with zipfile.ZipFile(path) as source:
        entries = [(name, source.read(name)) for name in source.namelist() if name not in remove]
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as target:
        for name, data in entries:
            target.writestr(name, replace.get(name, data))
        for name, data in (add or {}).items():
            target.writestr(name, data)
    checksum(path)


@pytest.fixture
def candidate(tmp_path):
    root = tmp_path
    (root / "update_service.py").write_text('VERSION = "0.3.0-dev.1"\n')
    academic = b"# academic source\n"
    license_text = b"MIT license fixture\n"
    example = b"AC <- M[100]\nS <- 0\n"
    translator_doc = b"Standalone RTL translator documentation\n"
    (root / "rtl_translator.py").write_bytes(academic)
    (root / "LICENSE").write_bytes(license_text)
    (root / "examples").mkdir()
    (root / "examples" / "add.rtl").write_bytes(example)
    (root / "docs").mkdir()
    (root / "docs" / "TRANSLATOR.md").write_bytes(translator_doc)
    portable = root / "portable-output"
    setup = root / "installer" / "output"
    for folder in (portable, setup):
        folder.mkdir(parents=True)
        (folder / "commit.txt").write_text("SHA=" + SHA)
        (folder / "portable-smoke.txt").write_text("PASS\n")
        (folder / "build-dependencies.txt").write_text("PySide6==6.8.0\n")
    (setup / "installed-smoke.txt").write_text("PASS\n")
    z = portable / "ManoStudio-v0.3.0-dev.1-Windows-x64.zip"
    app = pe()
    python_license = b"Python PSF license fixture\n"
    notice = b"PySide6 license fixture\n"
    inventory = {
        "kind": "build-license-evidence",
        "review_complete": False,
        "warnings": ["Fixture intentionally leaves legal review incomplete."],
        "python_license": {"path": "Python-LICENSE.txt", "sha256": hashlib.sha256(python_license).hexdigest()},
        "packages": [{"name": "PySide6", "version": "6.8.0",
                      "notices": [{"path": "PySide6/LICENSE.txt", "sha256": hashlib.sha256(notice).hexdigest()}]}],
        "binaries": [{"path": "ManoStudio.exe", "size": len(app), "sha256": hashlib.sha256(app).hexdigest()}],
    }
    with zipfile.ZipFile(z, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("ManoStudio/ManoStudio.exe", app)
        archive.writestr("ManoStudio/_internal/rtl_translator.py", academic)
        archive.writestr("ManoStudio/_internal/LICENSE", license_text)
        archive.writestr("ManoStudio/_internal/examples/add.rtl", example)
        archive.writestr("ManoStudio/_internal/docs/TRANSLATOR.md", translator_doc)
        archive.writestr("ManoStudio/third-party-notices/inventory.json", json.dumps(inventory))
        archive.writestr("ManoStudio/third-party-notices/Python-LICENSE.txt", python_license)
        archive.writestr("ManoStudio/third-party-notices/PySide6/METADATA.txt", "Name: PySide6\n")
        archive.writestr("ManoStudio/third-party-notices/PySide6/LICENSE.txt", notice)
    with zipfile.ZipFile(z) as archive:
        payload = {n.split("/", 1)[1]: {"size": len(archive.read(n)),
                   "sha256": hashlib.sha256(archive.read(n)).hexdigest()} for n in archive.namelist()}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    (setup / "installed-payload.json").write_text(json.dumps({
        "kind": "installed-payload-comparison", "result": "PASS", "files": len(payload),
        "payload_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(), "native_acceptance": False,
    }))
    exe = setup / "ManoStudio-Setup-v0.3.0-dev.1-x64.exe"
    exe.write_bytes(pe(0x14c))
    checksum(z)
    checksum(exe)
    return root, z, exe


def test_candidate_evidence(candidate):
    root, z, exe = candidate
    record = validate(root, SHA)
    assert record["installed_payload"]["result"] == "PASS"
    assert record["source_sha"] == SHA
    assert record["portable_smoke"] == record["installed_smoke"] == "PASS"
    assert not record["public_release"] and not record["native_acceptance"]
    assert {a["name"] for a in record["assets"]} == {z.name, exe.name}
    assert record["license_evidence"] == {
        "inventory": "ManoStudio/third-party-notices/inventory.json",
        "review_complete": False,
        "warnings": 1,
        "packages": 1,
        "notices": 1,
        "binaries": 1,
        "python_license_present": True,
    }


@pytest.mark.parametrize("damage", ["sha", "smoke", "digest", "source", "arch", "version", "setup"])
def test_reject_invalid_evidence(candidate, damage):
    root, z, exe = candidate
    if damage == "sha":
        (root / "portable-output" / "commit.txt").write_text("SHA=" + "b" * 40)
    elif damage == "smoke":
        (root / "installer" / "output" / "installed-smoke.txt").write_text("FAIL")
    elif damage == "digest":
        exe.write_bytes(pe() + b"tampered")
    elif damage == "source":
        (root / "rtl_translator.py").write_bytes(b"different")
    elif damage == "arch":
        rewrite_zip(z, replace={"ManoStudio/ManoStudio.exe": pe(0x14c)})
    elif damage == "version":
        (root / "update_service.py").write_text('VERSION = "1.0.0"')
    elif damage == "setup":
        exe.write_bytes(b"not an executable")
        checksum(exe)
    with pytest.raises(ValueError):
        validate(root, SHA)


@pytest.mark.parametrize("member", [
    "ManoStudio/_internal/LICENSE",
    "ManoStudio/_internal/examples/add.rtl",
    "ManoStudio/_internal/docs/TRANSLATOR.md",
    "ManoStudio/third-party-notices/inventory.json",
    "ManoStudio/third-party-notices/PySide6/LICENSE.txt",
])
def test_reject_missing_distribution_payload(candidate, member):
    root, z, _ = candidate
    rewrite_zip(z, remove=[member])
    with pytest.raises(ValueError):
        validate(root, SHA)


def test_reject_unlisted_binary(candidate):
    root, z, _ = candidate
    rewrite_zip(z, add={"ManoStudio/_internal/Qt6Core.dll": b"unlisted runtime binary"})
    with pytest.raises(ValueError, match="inventory is incomplete"):
        validate(root, SHA)


def test_reject_binary_not_matching_inventory(candidate):
    root, z, _ = candidate
    rewrite_zip(z, replace={"ManoStudio/ManoStudio.exe": pe() + b"tampered"})
    with pytest.raises(ValueError, match="hash/size"):
        validate(root, SHA)


def test_reject_unsafe_inventory_binary_path(candidate):
    root, z, _ = candidate
    with zipfile.ZipFile(z) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    name = "ManoStudio/third-party-notices/inventory.json"
    inventory = json.loads(entries[name])
    inventory["binaries"][0]["path"] = "../outside.exe"
    entries[name] = json.dumps(inventory).encode()
    with zipfile.ZipFile(z, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, data in entries.items():
            archive.writestr(path, data)
    checksum(z)
    with pytest.raises(ValueError, match="Unsafe"):
        validate(root, SHA)


@pytest.mark.parametrize("path", ["ManoStudio/_internal/extra.dll", "ManoStudio/EXTRA.PYD", "ManoStudio/other.exe"])
def test_reject_other_unlisted_binary(candidate, path):
    root, z, _ = candidate
    with zipfile.ZipFile(z, "a") as archive:
        archive.writestr(path, b"unlisted")
    checksum(z)
    with pytest.raises(ValueError, match="inventory is incomplete"):
        validate(root, SHA)


@pytest.mark.parametrize("path", ["ManoStudio/manostudio.EXE", "ManoStudio/../escape.txt", "outside.txt", "ManoStudio\\extra.txt"])
def test_reject_ambiguous_archive_path(candidate, path):
    root, z, _ = candidate
    with zipfile.ZipFile(z, "a") as archive:
        archive.writestr(path, b"unexpected")
    checksum(z)
    with pytest.raises(ValueError, match="[Uu]nsafe|case-colliding"):
        validate(root, SHA)



@pytest.mark.parametrize("damage", ["missing", "digest", "count", "acceptance", "extra_document"])
def test_reject_stale_installed_payload_report(candidate, damage):
    root, z, _ = candidate
    path = root / "installer" / "output" / "installed-payload.json"
    if damage == "missing":
        path.unlink()
    elif damage == "extra_document":
        rewrite_zip(z, add={"ManoStudio/_internal/docs/extra.txt": b"not installed"})
    else:
        report = json.loads(path.read_text())
        if damage == "digest":
            report["payload_sha256"] = "0" * 64
        elif damage == "count":
            report["files"] += 1
        else:
            report["native_acceptance"] = True
        path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="[Ii]nstalled payload report"):
        validate(root, SHA)


def test_accepts_current_semver_beta_candidate(tmp_path):
    (tmp_path / "update_service.py").write_text('VERSION = "1.1.0-beta.2"\\n')
    assert source_version(tmp_path) == "1.1.0-beta.2"


def test_rejects_unmarked_stable_version(tmp_path):
    (tmp_path / "update_service.py").write_text('VERSION = "1.0.0"\\n')
    with pytest.raises(ValueError, match="development/prerelease"):
        source_version(tmp_path)
