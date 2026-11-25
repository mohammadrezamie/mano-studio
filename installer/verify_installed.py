"""Compare the installed payload with the exact frozen build without executing it."""
import argparse
import hashlib
import json
from pathlib import Path


UNINSTALLER_FILES = frozenset({"unins000.exe", "unins000.dat", "unins000.msg"})


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def inventory(root):
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Invalid payload directory")
    files = {}
    seen = set()
    for path in sorted(root.rglob("*")):
        name = path.relative_to(root).as_posix()
        key = name.casefold()
        if key in seen:
            raise ValueError("Case-colliding payload path: " + name)
        seen.add(key)
        if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            raise ValueError("Unexpected linked payload path: " + name)
        if path.is_file():
            files[name] = {"size": path.stat().st_size, "sha256": digest(path)}
        elif not path.is_dir():
            raise ValueError("Unexpected payload entry: " + name)
    return files


def verify(frozen, installed):
    expected, actual = inventory(frozen), inventory(installed)
    if "ManoStudio.exe" not in expected or not expected:
        raise ValueError("Missing frozen application")
    if any(name.casefold() in UNINSTALLER_FILES for name in expected):
        raise ValueError("Uninstaller filename reserved in frozen payload")
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys() - UNINSTALLER_FILES)
    changed = sorted(name for name in expected.keys() & actual.keys() if expected[name] != actual[name])
    if missing or extra or changed:
        raise ValueError(f"Installed payload mismatch: missing={missing}, extra={extra}, changed={changed}")
    if not {"unins000.exe", "unins000.dat"} <= actual.keys():
        raise ValueError("Missing installed uninstaller evidence")
    canonical = json.dumps(expected, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {"kind": "installed-payload-comparison", "result": "PASS", "files": len(expected),
            "payload_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "native_acceptance": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen", type=Path, required=True)
    parser.add_argument("--installed", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.frozen, args.installed)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
