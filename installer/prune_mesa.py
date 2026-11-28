"""Opt-in experimental removal of the known Qt software OpenGL fallback.

No claim of native low-GPU compatibility. Use only on fresh build trees.
"""
import argparse
import hashlib
from pathlib import Path

EXPECTED = "18aedc7a4b610f53bcc7b7a5c5ed9293c7e86f030e3273ad54ed3bb1ebd36702"
RELATIVE = "_internal/PySide6/opengl32sw.dll"


def pe_imports(path):
    import pefile
    pe = pefile.PE(str(path), fast_load=True)
    try:
        pe.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT"],
        ])
        return {entry.dll.decode("ascii").lower()
                for name in ("DIRECTORY_ENTRY_IMPORT", "DIRECTORY_ENTRY_DELAY_IMPORT")
                for entry in getattr(pe, name, ())}
    finally:
        pe.close()


def prune(root, imports=pe_imports, *, expected=EXPECTED):
    root = Path(root)
    if not (root / "ManoStudio.exe").is_file():
        raise ValueError("Not a frozen Mano Studio build")
    files = sorted(p for p in root.rglob("*") if p.is_file())
    targets = [p for p in files if p.name.lower() == "opengl32sw.dll"]
    if not targets:
        return []
    target = root / RELATIVE
    if targets != [target] or target.is_symlink() or target.resolve() != root.resolve() / RELATIVE:
        raise ValueError("Unexpected Mesa path or link")
    with target.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != expected:
            raise ValueError("Unreviewed Mesa bytes")
    for p in files:
        if p != target and p.suffix.lower() in (".exe", ".dll", ".pyd"):
            if "opengl32sw.dll" in {name.lower() for name in imports(p)}:
                raise ValueError("Retained PE imports Mesa: " + str(p))
    target.unlink()
    return [RELATIVE]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frozen_root")
    for path in prune(parser.parse_args().frozen_root):
        print("Experimental Mesa removal:", path)


if __name__ == "__main__":
    main()
