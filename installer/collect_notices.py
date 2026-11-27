"""Collect build-time license evidence, not a certification of redistribution."""
import hashlib
from importlib.metadata import distributions
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys


PREFIXES = ("pyside6", "shiboken6", "pyinstaller")


def sha256(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def notice_path(value):
    path = PurePosixPath(str(value).replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or not path.parts or any(":" in p for p in path.parts):
        return None
    if not any(p.endswith(".dist-info") for p in path.parts):
        return None
    if not (any(p.lower() == "licenses" for p in path.parts) or
            any(word in path.name.lower() for word in ("license", "copying", "notice"))):
        return None
    return path


def collect(target, packages, python_prefix, frozen_root):
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    report = {"kind": "build-license-evidence", "review_complete": False,
              "python_version": sys.version.split()[0], "packages": [], "warnings": [], "binaries": []}
    seen = set()
    for dist in sorted(packages, key=lambda d: d.metadata.get("Name", "").lower()):
        name = dist.metadata.get("Name", "")
        if not name.lower().startswith(PREFIXES):
            continue
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", name) or name in (".", ".."):
            raise ValueError("Invalid package name")
        key = name.lower().replace("_", "-")
        if key in seen:
            raise ValueError("Duplicate package metadata: " + name)
        seen.add(key)
        folder = target / name
        folder.mkdir(exist_ok=True)
        # Read the installed metadata text, rather than serializing an email
        # Message whose long Description may contain header-like lines.
        metadata = dist.read_text("METADATA") or dist.read_text("PKG-INFO")
        if not isinstance(metadata, str) or not metadata.strip():
            raise ValueError("Missing distribution metadata: " + name)
        (folder / "METADATA.txt").write_text(metadata, encoding="utf-8", newline="")
        notices = []
        for file in dist.files or ():
            relative = notice_path(file)
            if relative is None:
                continue
            source = Path(dist.locate_file(file))
            if not source.is_file():
                report["warnings"].append(f"Missing listed notice: {name}/{relative}")
                continue
            destination = folder.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            notices.append({"path": destination.relative_to(target).as_posix(), "sha256": sha256(destination)})
        if not notices:
            report["warnings"].append("No distribution notices discovered: " + name)
        report["packages"].append({"name": name, "version": dist.version, "notices": sorted(notices, key=lambda n: n["path"])})
    for required in ("pyside6", "pyside6-essentials", "pyside6-addons", "shiboken6", "pyinstaller"):
        if required not in seen:
            report["warnings"].append("Required build metadata not found: " + required)
    python_license = next((p for p in (Path(python_prefix)/"LICENSE.txt", Path(python_prefix)/"LICENSE") if p.is_file()), None)
    if python_license is None:
        report["warnings"].append("Python runtime license not found in base prefix")
    else:
        destination = target / "Python-LICENSE.txt"
        shutil.copyfile(python_license, destination)
        report["python_license"] = {"path": destination.name, "sha256": sha256(destination)}
    root = Path(frozen_root)
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in (".dll", ".pyd", ".exe"):
            report["binaries"].append({"path": path.relative_to(root).as_posix(), "size": path.stat().st_size, "sha256": sha256(path)})
    if not report["binaries"]:
        report["warnings"].append("No frozen binaries found")
    (target / "inventory.json").write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return report


def main():
    target = Path(sys.argv[1])
    report = collect(target, distributions(), sys.base_prefix, target.parent)
    print(f"License evidence: {len(report['packages'])} packages, {len(report['binaries'])} binaries, {len(report['warnings'])} warnings; review required.")


if __name__ == "__main__":
    main()
