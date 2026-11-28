"""Offline contract tests for the OpenSSL staging archive reader.

Run: python -m pytest -q scripts/test_stage_openssl_replacements.py
Fixtures are synthetic data, never distributable DLLs.
"""
import json
import zipfile
import pytest
from stage_openssl_replacements import read_build, digest, FAMILIES, SOURCE, FIXES

CONFIG = "VC-WIN64A shared no-asm"


@pytest.fixture
def members():
    blobs = {name: name.encode() for name in FAMILIES[CONFIG]}
    report = {"source": SOURCE, "configuration": CONFIG, "upstream_tests": "PASS",
              "official_release": False, "public_release_approved": False,
              "dlls": [{"name": name, "bytes": len(data), "sha256": digest(data)}
                       for name, data in blobs.items()]}
    return {**blobs, "build-report.json": json.dumps(report).encode(),
            "advisory-ancestors.txt": "\n".join(s + " ancestor verified" for s in sorted(FIXES)).encode(),
            **{name: b"fixture" for name in ("LICENSE.txt", "VERSION.dat", "config.txt", "source.txt")}}


def archive(tmp_path, members):
    path = tmp_path / "fixture.zip"
    with zipfile.ZipFile(path, "w") as z:
        for name, data in members.items():
            z.writestr(name, data)
    return path, digest(path.read_bytes())


def test_valid_fixture(tmp_path, members):
    p, sha = archive(tmp_path, members)
    assert set(read_build(p, sha, CONFIG)[0]) == FAMILIES[CONFIG]


@pytest.mark.parametrize("mode", ["wrong-outer-hash", "wrong-ancestor", "changed-dll",
                                 "extra-dll", "approved", "failed-tests", "wrong-source", "empty-license"])
def test_reject(tmp_path, members, mode):
    if mode == "wrong-ancestor":
        lines = members["advisory-ancestors.txt"].splitlines()
        lines[0] = b"0" * 40 + b" ancestor verified"
        members["advisory-ancestors.txt"] = b"\n".join(lines)
    elif mode == "changed-dll":
        members["libcrypto-3-x64.dll"] += b"changed"
    elif mode == "extra-dll":
        members["unexpected.dll"] = b"fake"
    elif mode == "empty-license":
        members["LICENSE.txt"] = b""
    elif mode in ("approved", "failed-tests", "wrong-source"):
        report = json.loads(members["build-report.json"])
        key, value = {"approved": ("public_release_approved", True),
                      "failed-tests": ("upstream_tests", "FAIL"),
                      "wrong-source": ("source", "0" * 40)}[mode]
        report[key] = value
        members["build-report.json"] = json.dumps(report).encode()
    p, sha = archive(tmp_path, members)
    with pytest.raises(ValueError):
        read_build(p, "0" * 64 if mode == "wrong-outer-hash" else sha, CONFIG)
