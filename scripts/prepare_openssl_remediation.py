"""Prepare an isolated, exact-byte OpenSSL remediation payload for Windows testing.

Run only after stage_openssl_replacements.py passes on both original Portables.
No application source rebuild, installer promotion, or security approval here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import struct
import zipfile

from stage_openssl_replacements import SOURCE

BASELINES = {
    "stable": ("9eb70510ba23fc4be3ef4d92f32df6b1323994d512e1ac67f4b5f41d8fcb7fd0",
               "bc93823dbea393f17464886abeef406defda22e4151dbaab82293928eae3271e"),
    "beta": ("37466c0f2012b375e56b3ac98ee52c953bc793b18f369050795cad4b71583143",
             "b6a9e2c0fa4014ce505d68e639a328f6ec193b98655c2f123a93365d3b523109"),
}
OLD = {
    "libcrypto-3-x64.dll": "d51f2b081e5ac0f94c2bf15650a6b55cf48da1de8c313c9f90003d9ed08ccc9e",
    "libcrypto-3.dll": "75495fe0e079ab00d49be740d3c710a0b94e3f74f9648cb7cc9f768fc7f52319",
    "libssl-3-x64.dll": "a2cb46897a5365a740c8f898bf1b9119ba23f01807ad0ba1efb69a9997b43ba0",
    "libssl-3.dll": "8957182a9c385bfd9f3f790921de2ddc614cf91f99edbed4e9e5446a46504e32",
}
INV = "third-party-notices/inventory.json"
NOTICE = "third-party-notices/openssl/evidence.json"
LICENSE = "third-party-notices/openssl/openssl-source-pilot-LICENSE.txt"
HISTORY = "third-party-notices/openssl/original-runtime-evidence.json"
PROVENANCE = "third-party-notices/openssl/source-pilot-build-provenance.json"


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def icon_from_exe(exe, output):
    import pefile
    pe = pefile.PE(str(exe))
    try:
        types = {e.id:e for e in pe.DIRECTORY_ENTRY_RESOURCE.entries if e.id is not None}
        groups = types[14].directory.entries
        if len(groups) != 1:
            raise ValueError("Expected one original executable icon group")
        group = groups[0].directory.entries[0].data.struct
        raw = pe.get_data(group.OffsetToData, group.Size)
        reserved, kind, count = struct.unpack_from("<HHH",raw)
        if (reserved,kind)!=(0,1) or not 1<=count<=32 or len(raw)!=6+14*count:
            raise ValueError("Invalid group icon")
        images = {e.id:e for e in types[3].directory.entries}
        header, payload = bytearray(raw[:6]), bytearray()
        offset = 6+16*count
        for i in range(count):
            entry = raw[6+i*14:6+(i+1)*14]
            size, ident = struct.unpack_from("<IH",entry,8)
            resource = images[ident].directory.entries[0].data.struct
            data = pe.get_data(resource.OffsetToData,resource.Size)
            if len(data)!=size:
                raise ValueError("Icon resource size mismatch")
            header.extend(entry[:12]+struct.pack("<I",offset))
            payload.extend(data)
            offset+=size
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(header+payload)
    finally:
        pe.close()



def prepare(track, portable, staged, candidate, report):
    sys.path.insert(0, str(candidate.resolve()))
    from installer.windows_zip_paths import validate_windows_paths
    from installer.verify_installed import inventory
    expected, original = BASELINES[track]
    if sha(portable) != expected or (candidate / "dist").exists() or report.exists():
        raise ValueError("Unexpected baseline or existing output")
    staging = json.loads((staged / "staging-report.json").read_text(encoding="utf-8"))
    if staging.get("source") != SOURCE or staging.get("security_approved") is not False:
        raise ValueError("Unexpected staging provenance")
    matches = [a for a in staging["abi"] if a["portable_sha256"] == original]
    if len(matches) != 1:
        raise ValueError("Missing exact original ABI report")
    rows = matches[0]["dlls"]
    if len(rows) != 4 or {r["name"] for r in rows} != set(OLD):
        raise ValueError("Incomplete ABI report")
    build_rows = [r for b in staging["build_reports"] for r in b["dlls"]]
    if len(build_rows) != 4 or {r["name"] for r in build_rows} != set(OLD):
        raise ValueError("Incomplete build evidence")
    build = {r["name"]: r for r in build_rows}
    for r in rows:
        name = r["name"]
        p = staged / name
        if (r["original_sha256"] != OLD[name] or
                r["replacement_sha256"] != build[name]["sha256"] or
                sha(p) != r["replacement_sha256"] or p.stat().st_size != build[name]["bytes"]):
            raise ValueError("Staged DLL evidence mismatch: " + name)
    with zipfile.ZipFile(portable) as z:
        validate_windows_paths(z, "ManoStudio/")
        if z.testzip() is not None:
            raise ValueError("Invalid baseline ZIP")
        z.extractall(candidate / "dist")
    root = candidate / "dist/ManoStudio"
    before = inventory(root)
    inv = json.loads((root / INV).read_text(encoding="utf-8-sig"))
    old_notice = json.loads((root / NOTICE).read_text(encoding="utf-8-sig"))
    if any((root / p).exists() for p in (LICENSE, HISTORY, PROVENANCE)):
        raise ValueError("Unexpected prior replacement evidence")
    for name, expected_sha in OLD.items():
        rel = "_internal/" + name
        found = [r for r in inv["binaries"] if r["path"] == rel]
        if (len(found) != 1 or found[0]["sha256"] != expected_sha or
                sha(root / rel) != expected_sha):
            raise ValueError("Unexpected baseline DLL: " + name)
    for name in OLD:
        rel = "_internal/" + name
        (root / rel).write_bytes((staged / name).read_bytes())
        row = next(r for r in inv["binaries"] if r["path"] == rel)
        row.update(size=(root / rel).stat().st_size, sha256=sha(root / rel))
    inv["review_complete"] = False
    write_json(root / INV, inv)
    write_json(root / HISTORY, old_notice)
    (root / LICENSE).write_bytes((staged / "LICENSE.txt").read_bytes())
    write_json(root / PROVENANCE, staging)
    write_json(root / NOTICE, {
        "kind": "source-built-openssl-remediation-review",
        "source": SOURCE, "official_release": False,
        "binaries": [{"path": "_internal/" + n, "sha256": sha(root / ("_internal/" + n))}
                     for n in sorted(OLD)],
        "licenses": [{"file": Path(LICENSE).name, "sha256": sha(root / LICENSE),
                      "source": "https://github.com/openssl/openssl/blob/" + SOURCE + "/LICENSE.txt"}],
        "warnings": ["Review-only locally built runtime; exact replacement acceptance pending."],
        "historical_notice": Path(HISTORY).name,
        "exact_distributor_provenance_verified": False, "security_approved": False,
        "redistribution_approved": False,
    })
    after = inventory(root)
    changed = {k for k in before.keys() & after.keys() if before[k] != after[k]}
    wanted = {"_internal/" + n for n in OLD} | {INV, NOTICE}
    if (changed != wanted or set(before) - set(after) or
            set(after) - set(before) != {LICENSE, HISTORY, PROVENANCE}):
        raise ValueError("Unexpected payload delta")
    icon_from_exe(root / "ManoStudio.exe", candidate / "build/mano-studio.ico")
    write_json(report, {"kind": "internal-openssl-remediation",
                        "track": track, "baseline_sha256": expected,
                        "changed": {k: {"before": before[k], "after": after[k]} for k in sorted(changed)},
                        "added": {k: after[k] for k in (LICENSE, HISTORY, PROVENANCE)},
                        "unchanged_files": len(before) - len(changed),
                        "application_sha256": before["ManoStudio.exe"]["sha256"],
                        "native_acceptance": False, "security_approved": False,
                        "redistribution_approved": False, "public_release_approved": False})


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("track", choices=BASELINES)
    for name in ("portable", "staged", "candidate", "report"):
        p.add_argument(name, type=Path)
    a = p.parse_args()
    prepare(a.track, a.portable, a.staged, a.candidate, a.report)
