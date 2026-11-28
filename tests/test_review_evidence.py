import hashlib
import json
from pathlib import Path
import zipfile

import pytest
from installer.redistribution_gate import audit
from installer.runtime_evidence import scan
from installer.wheel_evidence import REQUIRED, validate
from installer.review_evidence import verify


@pytest.fixture
def candidate(tmp_path):
    root = tmp_path
    portable, setup = root / "portable-output", root / "installer" / "output"
    portable.mkdir()
    setup.mkdir(parents=True)
    versions = dict.fromkeys(REQUIRED, "1.2.3")
    constraints = root / "installer" / "windows-candidate-constraints.txt"
    constraints.write_text("".join(f"{k}=={v}\n" for k,v in sorted(versions.items())))
    pip = {"version": "1", "install": [
        {"metadata": {"name": k, "version": v}, "download_info": {
            "url": "https://files.pythonhosted.org/packages/" + k + ".whl",
            "archive_info": {"hashes": {"sha256": "a"*64}}}}
        for k,v in sorted(versions.items())]}
    raw = json.dumps(pip).encode()
    (root / "build-wheel-report.json").write_bytes(raw)
    archive_path = portable / "test.zip"
    data = b"OpenSSL 3.5.9"
    with zipfile.ZipFile(archive_path, "w") as z:
        z.writestr("ManoStudio/libcrypto-3-x64.dll", data)
        z.writestr("ManoStudio/third-party-notices/inventory.json", json.dumps({
            "kind": "build-license-evidence", "packages": [], "warnings": [],
            "binaries": [{"path": "libcrypto-3-x64.dll", "size": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()}]}))
        supplement_files = {
            "BSD-3-Clause.txt": b"BSD fixture",
            "libtiff.txt": b"libtiff fixture",
            "libwebp-COPYING.txt": b"libwebp fixture",
            "NOTICE.md": b"Qt Image Formats notice",
            "plugin-map.json": json.dumps({"plugins":{"qicns":{},"qtga":{},"qtiff":{},"qwbmp":{},"qwebp":{}}}).encode(),
            "libtiff-attribution.json": b"libtiff attribution",
            "libwebp-attribution.json": b"libwebp attribution",
        }
        supplement_rows = [{"file":name,"bytes":len(value),"sha256":hashlib.sha256(value).hexdigest()} for name,value in supplement_files.items()]
        supplement = {"kind":"qt-imageformats-license-supplement","source_version":"6.12.0",
                      "source_archive_sha256":"0943132b5db8de6b6a7f1d162682173e8763c7ed94e80fd39113292845f67762",
                      "files":supplement_rows,"review_complete":False,
                      "exact_corresponding_source_verified":False,"redistribution_approved":False}
        for name,value in supplement_files.items():
            z.writestr("ManoStudio/third-party-notices/qt-license-texts/qtimageformats/"+name,value)
        z.writestr("ManoStudio/third-party-notices/qt-license-texts/qtimageformats/SUPPLEMENT.json",json.dumps(supplement))
    with zipfile.ZipFile(archive_path) as z:
        values = {"redistribution-preflight.json": audit(z),
                  "runtime-evidence.json": scan(z, "3.14.10", (3,5,9)),
                  "wheel-evidence.json": validate(pip, versions)}
    for folder in (portable, setup):
        (folder / constraints.name).write_bytes(constraints.read_bytes())
        (folder / "build-wheel-report.json").write_bytes(raw)
        for name, value in values.items():
            (folder / name).write_text(json.dumps(value), encoding="utf-8")
    return root, archive_path, portable, setup


def test_recompute(candidate):
    root, archive, _, _ = candidate
    with zipfile.ZipFile(archive) as z:
        report = verify(root, z, "3.14.10", (3,5,9))
    assert report["redistribution_flags"] == 2
    assert report["runtime_flags"] == 2
    assert report["wheel_packages"] == len(REQUIRED)
    assert len(report["evidence_sha256"]) == 5
    assert report["public_release_approved"] is False


@pytest.mark.parametrize("defect", ["missing", "different", "license-flags",
    "runtime-flags", "runtime-hash", "wheel-hash", "wheel-version", "constraints",
    "raw-pip", "approval", "bool-count"])
def test_reject_inconsistent_evidence(candidate, defect):
    root, archive, portable, setup = candidate
    if defect == "missing":
        (setup / "wheel-evidence.json").unlink()
    elif defect == "different":
        (setup / "wheel-evidence.json").write_text("{}")
    elif defect in ("constraints", "raw-pip"):
        name = "windows-candidate-constraints.txt" if defect == "constraints" else "build-wheel-report.json"
        for folder in (portable, setup):
            (folder / name).write_text("changed")
    else:
        name = ("redistribution-preflight.json" if defect in ("license-flags", "approval", "bool-count")
                else "runtime-evidence.json" if defect.startswith("runtime") else "wheel-evidence.json")
        report = json.loads((portable / name).read_text())
        if defect == "runtime-flags":
            report["flags"] = [{"code": "tampered-runtime-flag"}]
        elif defect.endswith("flags"):
            report["flags"] = []
        elif defect == "runtime-hash":
            report["binaries"][0]["sha256"] = "b"*64
        elif defect.startswith("wheel"):
            item = next(iter(report["packages"].values()))
            item["sha256" if defect == "wheel-hash" else "version"] = "b"*64
        elif defect == "approval":
            report["public_release_approved"] = True
        else:
            report["binary_count"] = True
        for folder in (portable, setup):
            (folder / name).write_text(json.dumps(report))
    with zipfile.ZipFile(archive) as z, pytest.raises(ValueError):
        verify(root, z, "3.14.10", (3,5,9))
