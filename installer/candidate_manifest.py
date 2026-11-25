"""Validate development build evidence; never publish or execute an artifact."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import struct
import zipfile


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


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
            if isinstance(version, str) and re.fullmatch(r"0\.\d+\.\d+-(dev|alpha|beta|rc)(\.\d+)?", version):
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
        if archive.testzip() is not None:
            raise ValueError("Corrupt portable archive")
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate portable entries")
        with archive.open("ManoStudio/ManoStudio.exe") as program:
            if machine(program) != 0x8664:
                raise ValueError("Portable executable is not AMD64")
        source = [n for n in names if n in ("ManoStudio/rtl_translator.py", "ManoStudio/_internal/rtl_translator.py")]
        if len(source) != 1 or archive.read(source[0]) != (root / "rtl_translator.py").read_bytes():
            raise ValueError("Bundled academic source differs from checkout")
    with exe.open("rb") as stream:
        # Inno Setup may use a 32-bit bootstrap for a 64-bit application.
        machine(stream)
    return {"kind": "internal-development-candidate", "version": version, "source_sha": sha,
            "platform": "Windows x64", "portable_smoke": "PASS", "installed_smoke": "PASS",
            "academic_source_sha256": digest(root / "rtl_translator.py"), "assets": assets,
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
