"""Stage both independently built OpenSSL DLL families for ABI review.

This never modifies a candidate, publishes a release or approves security.
Requires both successful build artifacts and both exact original Portables.
GNU objdump is required by openssl_abi_preflight.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
import zipfile

from openssl_abi_preflight import validate

SOURCE = "ee8e3a49f3d9ef5bc8aeaa9eac19e8df236d9dbb"
QT_SHA = "ff82f990a505c2eaf09843937f887a6839a743039eea7efe5837c929b1fbc934"
FAMILIES = {
    "VC-WIN64A shared no-asm": {"libcrypto-3-x64.dll", "libssl-3-x64.dll"},
    "VC-WIN64A-mano-python shared no-asm": {"libcrypto-3.dll", "libssl-3.dll"},
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_build(path, expected_sha, config):
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        raise ValueError("Expected externally recorded SHA-256")
    data = path.read_bytes()
    if digest(data) != expected_sha:
        raise ValueError("Build artifact digest mismatch")
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = z.namelist()
        expected = FAMILIES[config]
        if len(names) != len(set(names)) or z.testzip() is not None:
            raise ValueError("Bad build archive")
        report = json.loads(z.read("build-report.json").decode("utf-8-sig"))
        if (report.get("source") != SOURCE or report.get("configuration") != config
                or report.get("upstream_tests") != "PASS"
                or report.get("official_release") is not False
                or report.get("public_release_approved") is not False):
            raise ValueError("Not the expected passing review build")
        rows = report["dlls"]
        if len(rows) != len(expected) or {r["name"] for r in rows} != expected:
            raise ValueError("Wrong DLL family")
        if {n for n in names if n.lower().endswith(".dll")} != expected:
            raise ValueError("Unexpected DLL archive members")
        ancestors = z.read("advisory-ancestors.txt").decode().splitlines()
        if len(ancestors) != 12 or len(set(ancestors)) != 12 or not all(
                re.fullmatch(r"[0-9a-f]{40} ancestor verified", l.strip()) for l in ancestors):
            raise ValueError("Incomplete ancestor evidence")
        result = {}
        for row in rows:
            blob = z.read(row["name"])
            if digest(blob) != row["sha256"] or len(blob) != row["bytes"]:
                raise ValueError("DLL hash or size mismatch")
            result[row["name"]] = blob
        for name in ("LICENSE.txt", "VERSION.dat", "config.txt", "source.txt"):
            if not z.read(name):
                raise ValueError("Missing build provenance: " + name)
        return result, report, z.read("LICENSE.txt"), set(ancestors)


def stage(qt, py, py_sha, stable, beta, out):
    if out.exists():
        raise ValueError("Output directory must not exist")
    q, qr, ql, qa = read_build(qt, QT_SHA, "VC-WIN64A shared no-asm")
    p, pr, pl, pa = read_build(py, py_sha, "VC-WIN64A-mano-python shared no-asm")
    if ql != pl or qa != pa:
        raise ValueError("Source evidence differs between build families")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for name, blob in (q | p).items():
            (root / name).write_bytes(blob)
        reports = [validate(stable, root), validate(beta, root)]
        if reports[0]["portable_sha256"] == reports[1]["portable_sha256"]:
            raise ValueError("Expected both distinct frozen channels")
        out.mkdir(parents=False, exist_ok=False)
        for name, blob in (q | p).items():
            (out / name).write_bytes(blob)
        (out / "LICENSE.txt").write_bytes(ql)
        (out / "staging-report.json").write_text(json.dumps({
            "source": SOURCE, "qt_artifact_sha256": QT_SHA, "python_artifact_sha256": py_sha,
            "build_reports": [qr, pr], "abi": reports,
            "runtime_compatibility_verified": False, "security_approved": False,
            "redistribution_approved": False, "public_release_approved": False,
        }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("qt", type=Path)
    parser.add_argument("python", type=Path)
    parser.add_argument("python_sha")
    parser.add_argument("stable", type=Path)
    parser.add_argument("beta", type=Path)
    parser.add_argument("output", type=Path)
    a = parser.parse_args()
    stage(a.qt, a.python, a.python_sha, a.stable, a.beta, a.output)
