"""Expand the pinned conservative Qt notice collection for end-user access.

This is notice delivery, not a legal approval or corresponding-source offer.
Run only on a fresh review payload before the installer is constructed.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import zipfile

PIN = "e0d723b4a78cadc46609c86a14093b3840109c554a18f55b430660033b7dcc65"
CONTROL = {"README.txt", "REVIEW-MANIFEST.json"}
MAX_TOTAL = 16 * 1024 * 1024


def checked_name(name):
    parts = name.split("/")
    if not name or any(not p or p in (".", "..") or p.endswith((".", " "))
        or re.search(r'[<>:"\\|?*\x00-\x1f]', p)
        or p.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL",
            *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
        for p in parts):
        raise ValueError("Unsafe Windows notice path: " + name)
    return PurePosixPath(name)


def expand(archive, destination, expected_sha=PIN):
    archive, destination = Path(archive), Path(destination)
    if destination.exists() or destination.is_symlink():
        raise ValueError("Notice destination already exists")
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected_sha:
        raise ValueError("Unexpected notice archive digest")
    with zipfile.ZipFile(archive) as z:
        files = z.infolist()
        if sum(f.file_size for f in files) > MAX_TOTAL:
            raise ValueError("Notice archive exceeds size bound")
        seen = set()
        for f in files:
            name = checked_name(f.filename)
            key = str(name).casefold()
            if key in seen or f.is_dir() or stat.S_ISLNK(f.external_attr >> 16):
                raise ValueError("Duplicate, directory or symbolic link")
            seen.add(key)
        if z.testzip() is not None:
            raise ValueError("Notice ZIP CRC failure")
        manifest = json.loads(z.read("REVIEW-MANIFEST.json"))
        if (manifest["kind"] != "conservative-upstream-notice-review"
                or manifest["redistribution_approved"] is not False):
            raise ValueError("Unexpected notice review manifest")
        expected = {}
        for module in manifest["modules"]:
            for record in module["files"]:
                name = str(checked_name(record["path"]))
                if name in expected or name in CONTROL:
                    raise ValueError("Duplicate notice manifest entry")
                expected[name] = record["sha256"]
        if set(z.namelist()) != set(expected) | CONTROL:
            raise ValueError("Notice manifest membership mismatch")
        for name, digest in expected.items():
            if hashlib.sha256(z.read(name)).hexdigest() != digest:
                raise ValueError("Notice content hash mismatch: " + name)
        # Use a staging directory on the same volume; do not touch an existing tree.
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=destination.parent) as temp:
            stage = Path(temp) / "notices"
            stage.mkdir()
            for name in sorted(expected):
                path = stage.joinpath(*PurePosixPath(name).parts)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(z.read(name))
            (stage / "REVIEW-MANIFEST.json").write_bytes(z.read("REVIEW-MANIFEST.json"))
            (stage / "README.txt").write_text(
                "Qt and PySide 6.12.0 upstream license and attribution files.\n"
                "This conservative collection also contains notices for components not shipped.\n"
                "See the adjacent qt-license-texts directory for LGPL/GPL terms.\n"
                "This collection is not a complete corresponding-source offer or release approval.\n",
                encoding="utf-8")
            stage.rename(destination)
    return len(expected)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(f"Expanded {expand(args.archive, args.destination)} verified notice files.")
