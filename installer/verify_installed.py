"""Compare installed files with the exact frozen build without following links."""
import argparse
import hashlib
import json
from pathlib import Path
import stat


UNINSTALLER_FILES = frozenset({"unins000.exe", "unins000.dat", "unins000.msg"})


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def linked(info):
    """Reject symlinks and every Windows reparse point, including junctions."""
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


def inventory(root):
    root = Path(root)
    root_info = root.lstat()
    if linked(root_info) or not stat.S_ISDIR(root_info.st_mode):
        raise ValueError("Invalid or linked payload directory")
    files = {}
    seen = set()
    pending = [root]
    while pending:
        directory = pending.pop()
        for path in sorted(directory.iterdir()):
            name = path.relative_to(root).as_posix()
            key = name.casefold()
            if key in seen:
                raise ValueError("Case-colliding payload path: " + name)
            seen.add(key)
            info = path.lstat()
            if linked(info):
                raise ValueError("Unexpected linked payload path: " + name)
            if stat.S_ISDIR(info.st_mode):
                if key in UNINSTALLER_FILES:
                    raise ValueError("Uninstaller path cannot be a directory: " + name)
                pending.append(path)
            elif stat.S_ISREG(info.st_mode):
                files[name] = {"size": info.st_size, "sha256": digest(path)}
            else:
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
