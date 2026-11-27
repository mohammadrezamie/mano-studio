"""Validate development build evidence; never publish or execute an artifact."""
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct
import zipfile

from installer.windows_zip_paths import validate_windows_paths


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def digest_member(archive, name):
    result = hashlib.sha256()
    with archive.open(name) as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def safe_relative(value):
    path = PurePosixPath(str(value).replace("\\", "/"))
    if path.is_absolute() or not path.parts or any(p in (".", "..") or ":" in p for p in path.parts):
        raise ValueError("Unsafe packaged path")
    return path.as_posix()


def packaged_member(names, relative):
    relative = safe_relative(relative)
    candidates = ("ManoStudio/" + relative, "ManoStudio/_internal/" + relative)
    matches = [name for name in candidates if name in names]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one packaged file: {relative}")
    return matches[0]


def machine(stream):
    header = stream.read(64)
    if len(header) != 64 or header[:2] != b"MZ":
        raise ValueError("Missing DOS executable header")
    offset = struct.unpack_from("<I", header, 60)[0]
    if not 64 <= offset <= 1024 * 1024:
        raise ValueError("Invalid PE offset")
    stream.seek(offset)
    pe = stream.read(6)
    if len(pe) != 6 or pe[:4] != b"PE\0\0":
        raise ValueError("Missing PE header")
    return struct.unpack_from("<H", pe, 4)[0]


def source_version(root):
    tree = ast.parse((root / "update_service.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "VERSION" for t in node.targets):
            version = ast.literal_eval(node.value)
            if isinstance(version, str) and re.fullmatch(r"\d+\.\d+\.\d+-(dev|alpha|beta|rc)(\.\d+)?", version):
                return version
    raise ValueError("Not an explicit development/prerelease version")


def require_text(path, expected):
    if path.read_text(encoding="utf-8-sig").strip() != expected:
        raise ValueError(f"Unexpected evidence: {path.name}")


def asset(path):
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Missing asset: {path.name}")
    value = digest(path)
    checksum = path.with_name(path.name + ".sha256").read_text(encoding="utf-8-sig").strip().split()
    if checksum not in ([value], [value, path.name]):
        raise ValueError(f"Checksum mismatch: {path.name}")
    return {"name": path.name, "size": path.stat().st_size, "sha256": value}


def verify_distribution_payload(root, archive):
    names = set(archive.namelist())
    source = packaged_member(names, "rtl_translator.py")
    if archive.read(source) != (root / "rtl_translator.py").read_bytes():
        raise ValueError("Bundled academic source differs from checkout")

    for relative, local in (
        ("LICENSE", root / "LICENSE"),
        ("examples/add.rtl", root / "examples" / "add.rtl"),
        ("docs/TRANSLATOR.md", root / "docs" / "TRANSLATOR.md"),
    ):
        member = packaged_member(names, relative)
        if archive.read(member) != local.read_bytes():
            raise ValueError(f"Packaged file differs from checkout: {relative}")

    inventory_name = packaged_member(names, "third-party-notices/inventory.json")
    inventory = json.loads(archive.read(inventory_name))
    if (not isinstance(inventory, dict) or inventory.get("kind") != "build-license-evidence"
            or inventory.get("review_complete") is not False
            or not isinstance(inventory.get("warnings"), list)
            or not isinstance(inventory.get("packages"), list)
            or not isinstance(inventory.get("binaries"), list)):
        raise ValueError("Missing or invalid third-party license evidence inventory")

    prefix = inventory_name.rsplit("/", 1)[0]
    seen_binaries = set()
    for item in inventory["binaries"]:
        relative = safe_relative(item["path"])
        if relative in seen_binaries:
            raise ValueError("Duplicate binary inventory path")
        seen_binaries.add(relative)
        member = "ManoStudio/" + relative
        if member not in names:
            raise ValueError("Bundled binary missing from portable archive: " + relative)
        info = archive.getinfo(member)
        if info.file_size != item["size"] or digest_member(archive, member) != item["sha256"]:
            raise ValueError("Bundled binary hash/size differs from inventory: " + relative)

    actual_binaries = {
        name[len("ManoStudio/"):]
        for name in names
        if name.startswith("ManoStudio/") and not name.endswith("/") and PurePosixPath(name).suffix.lower() in (".dll", ".pyd", ".exe")
    }
    if actual_binaries != seen_binaries:
        raise ValueError("Binary inventory is incomplete or contains files outside the archive")

    notice_count = 0
    for package in inventory["packages"]:
        name = package.get("name", "")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
            raise ValueError("Invalid package name in license inventory")
        metadata = f"{prefix}/{name}/METADATA.txt"
        if metadata not in names:
            raise ValueError("Package metadata missing from notices: " + name)
        for notice in package.get("notices", []):
            relative = safe_relative(notice["path"])
            member = prefix + "/" + relative
            if member not in names or digest_member(archive, member) != notice["sha256"]:
                raise ValueError("Packaged license notice missing or changed: " + relative)
            notice_count += 1

    python_license = inventory.get("python_license")
    if python_license:
        relative = safe_relative(python_license["path"])
        member = prefix + "/" + relative
        if member not in names or digest_member(archive, member) != python_license["sha256"]:
            raise ValueError("Python runtime license missing or changed")

    return {
        "inventory": inventory_name,
        "review_complete": False,
        "warnings": len(inventory["warnings"]),
        "packages": len(inventory["packages"]),
        "notices": notice_count,
        "binaries": len(inventory["binaries"]),
        "python_license_present": bool(python_license),
    }



def verify_installed_report(path, archive):
    if not path.is_file():
        raise ValueError("Missing installed payload report")
    report = json.loads(path.read_text(encoding="utf-8-sig"))
    expected = {
        info.filename[len("ManoStudio/"):]: {
            "size": info.file_size, "sha256": digest_member(archive, info.filename)
        }
        for info in archive.infolist() if not info.is_dir()
    }
    canonical = json.dumps(expected, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    expected_report = {"kind": "installed-payload-comparison", "result": "PASS", "files": len(expected),
                       "payload_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
                       "native_acceptance": False}
    if report != expected_report or type(report.get("files")) is not int or report.get("native_acceptance") is not False:
        raise ValueError("Installed payload report does not match portable archive")
    return expected_report



def verify_review_evidence(portable, setup, root):
    reports = {}
    specifications = (
        ("redistribution-preflight.json", "redistribution-preflight"),
        ("runtime-evidence.json", "runtime-evidence"),
        ("wheel-evidence.json", "pip-wheel-download-evidence"),
    )
    for filename, kind in specifications:
        portable_path = portable / filename
        setup_path = setup / filename
        if not portable_path.is_file() or not setup_path.is_file():
            raise ValueError("Missing review evidence: " + filename)
        raw = portable_path.read_bytes()
        if raw != setup_path.read_bytes():
            raise ValueError("Portable and Setup review evidence differ: " + filename)
        report = json.loads(raw)
        if not isinstance(report, dict):
            raise ValueError("Invalid review evidence: " + filename)
        if kind == "redistribution-preflight":
            if (not isinstance(report.get("flags"), list)
                    or report.get("manual_review_required") is not True
                    or report.get("public_release_approved") is not False):
                raise ValueError("Invalid redistribution review status")
        elif kind == "runtime-evidence":
            if (report.get("kind") != kind or not isinstance(report.get("flags"), list)
                    or report.get("manual_review_required") is not True
                    or report.get("public_release_approved") is not False):
                raise ValueError("Invalid runtime review status")
        else:
            if (report.get("kind") != kind or not isinstance(report.get("packages"), dict)
                    or not report["packages"]
                    or report.get("independent_authenticity_verified") is not False
                    or report.get("redistribution_approved") is not False):
                raise ValueError("Invalid wheel provenance status")
        reports[filename] = report

    constraints = root / "installer" / "windows-candidate-constraints.txt"
    if not constraints.is_file():
        raise ValueError("Missing source dependency constraints")
    expected = constraints.read_bytes()
    for folder in (portable, setup):
        copy = folder / "windows-candidate-constraints.txt"
        if not copy.is_file() or copy.read_bytes() != expected:
            raise ValueError("Packaged dependency constraints differ from source")
    return {
        "redistribution_flags": len(reports["redistribution-preflight.json"]["flags"]),
        "runtime_flags": len(reports["runtime-evidence.json"]["flags"]),
        "wheel_packages": len(reports["wheel-evidence.json"]["packages"]),
        "manual_review_required": True,
        "public_release_approved": False,
    }


def validate(root, sha):
    if not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise ValueError("Invalid source commit")
    version = source_version(root)
    portable = root / "portable-output"
    setup = root / "installer" / "output"
    for folder in (portable, setup):
        require_text(folder / "commit.txt", "SHA=" + sha)
        require_text(folder / "portable-smoke.txt", "PASS")
        if not (folder / "build-dependencies.txt").read_text(encoding="utf-8-sig").strip():
            raise ValueError("Missing dependency manifest")
    require_text(setup / "installed-smoke.txt", "PASS")
    z = portable / f"ManoStudio-v{version}-Windows-x64.zip"
    exe = setup / f"ManoStudio-Setup-v{version}-x64.exe"
    assets = [asset(z), asset(exe)]
    with zipfile.ZipFile(z) as archive:
        validate_windows_paths(archive, "ManoStudio/")
        if archive.testzip() is not None:
            raise ValueError("Corrupt portable archive")
        seen_paths = set()
        for name in archive.namelist():
            raw = name.rstrip("/")
            normalized = safe_relative(raw)
            if raw != normalized or not (raw == "ManoStudio" or raw.startswith("ManoStudio/")):
                raise ValueError("Unsafe or noncanonical portable archive path")
            key = raw.casefold()
            if key in seen_paths:
                raise ValueError("Duplicate or case-colliding portable entries")
            seen_paths.add(key)
        app = packaged_member(set(archive.namelist()), "ManoStudio.exe")
        with archive.open(app) as program:
            if machine(program) != 0x8664:
                raise ValueError("Portable executable is not AMD64")
        license_evidence = verify_distribution_payload(root, archive)
        installed_payload = verify_installed_report(setup / "installed-payload.json", archive)
    review_evidence = verify_review_evidence(portable, setup, root)
    with exe.open("rb") as stream:
        # Inno Setup may use a 32-bit bootstrap for a 64-bit application.
        machine(stream)
    return {"kind": "internal-development-candidate", "version": version, "source_sha": sha,
            "platform": "Windows x64", "portable_smoke": "PASS", "installed_smoke": "PASS",
            "academic_source_sha256": digest(root / "rtl_translator.py"), "assets": assets,
            "license_evidence": license_evidence, "installed_payload": installed_payload,
            "review_evidence": review_evidence,
            "native_acceptance": False, "public_release": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--sha", required=True)
    args = parser.parse_args()
    manifest = validate(args.root, args.sha)
    path = args.root / "installer" / "output" / "candidate-manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
