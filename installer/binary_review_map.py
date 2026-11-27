"""Map actual Windows payloads to review leads; not an SBOM or license grant."""
import argparse
from collections import Counter
import json
from pathlib import PurePosixPath
import zipfile

from installer.redistribution_gate import audit

PREFIX = "ManoStudio/"
INVENTORY = PREFIX + "third-party-notices/inventory.json"


def category(path):
    name = PurePosixPath(path).name.lower()
    if path == "ManoStudio.exe":
        return "pyinstaller/application"
    if name.startswith(("api-ms-win-", "msvcp", "vcruntime", "ucrtbase")):
        return "microsoft-runtime"
    if name.startswith(("libcrypto", "libssl")):
        return "openssl"
    if name == "libffi-8.dll":
        return "libffi"
    if name == "opengl32sw.dll":
        return "qt-opengl-software-review"
    if "/shiboken6/" in path or name == "pyside6.abi3.dll" or (
            "/PySide6/" in path and name.endswith(".pyd")):
        return "pyside-shiboken"
    if name.startswith(("qt6qml", "qt6quick")):
        return "qtdeclarative"
    if name in ("qt6svg.dll", "qsvg.dll", "qsvgicon.dll"):
        return "qtsvg"
    if name in ("qicns.dll", "qtga.dll", "qtiff.dll", "qwbmp.dll", "qwebp.dll"):
        return "qtimageformats"
    if name.startswith("qt6") or "/plugins/" in path:
        return "qtbase-candidate-review"
    if path.startswith("_internal/") and "/" not in path[len("_internal/"):] and (
            name.startswith("python") or name.endswith(".pyd")):
        return "cpython"
    return "unmapped"


def map_payload(archive):
    # Existing audit checks Windows namespace, binary membership and every hash.
    result = audit(archive)
    inventory = json.loads(archive.read(INVENTORY))
    rows = sorted((dict(path=x["path"], size=x["size"], sha256=x["sha256"],
                        review_group=category(x["path"])) for x in inventory["binaries"]),
                  key=lambda row: row["path"])
    return {"kind": "binary-review-map", "binaries": rows,
            "groups": dict(sorted(Counter(x["review_group"] for x in rows).items())),
            "build_packages": sorted((dict(name=x["name"], version=x["version"])
                                      for x in inventory["packages"]), key=lambda x: x["name"]),
            "redistribution_flags": result["flags"],
            "manual_review_required": True, "public_release_approved": False}


def compare(previous, current):
    before = {row["path"]: row for row in previous["binaries"]}
    after = {row["path"]: row for row in current["binaries"]}
    if len(before) != len(previous["binaries"]) or len(after) != len(current["binaries"]):
        raise ValueError("Duplicate binary review path")
    return {"added": sorted(after.keys() - before.keys()),
            "removed": sorted(before.keys() - after.keys()),
            "changed": sorted(path for path in before.keys() & after.keys()
                              if before[path] != after[path]),
            "build_package_metadata_changed": previous["build_packages"] != current["build_packages"],
            "review_flags_changed": previous["redistribution_flags"] != current["redistribution_flags"],
            "manual_review_required": True, "public_release_approved": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("portable_zip")
    parser.add_argument("--previous")
    args = parser.parse_args()
    with zipfile.ZipFile(args.portable_zip) as archive:
        report = map_payload(archive)
    if args.previous:
        with zipfile.ZipFile(args.previous) as archive:
            report["comparison"] = compare(map_payload(archive), report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
