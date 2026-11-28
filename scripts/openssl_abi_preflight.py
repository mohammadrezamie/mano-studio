"""Offline PE export/loader-name compatibility check for exact Mano candidates.

Use GNU objdump with PE support. This is a necessary, not sufficient, ABI
preflight; it does not execute DLLs or approve a release.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import zipfile

BASELINES = {
    "bc93823dbea393f17464886abeef406defda22e4151dbaab82293928eae3271e",
    "b6a9e2c0fa4014ce505d68e639a328f6ec193b98655c2f123a93365d3b523109",
}
DLLS = ("libcrypto-3.dll", "libssl-3.dll",
        "libcrypto-3-x64.dll", "libssl-3-x64.dll")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inspect(path):
    text = subprocess.check_output(["objdump", "-p", str(path)], text=True)
    if "file format pei-x86-64" not in text:
        raise ValueError("Expected Windows x64 PE: " + path.name)
    table = text.split("[Ordinal/Name Pointer] Table", 1)[1].split("\n\n", 1)[0]
    exports = set(re.findall(
        r"^\s*\[\s*\d+\]\s+\+base\[\s*\d+\]\s+[\da-fA-F]+\s+(\S+)",
        table, re.M))
    if not exports:
        raise ValueError("Missing named exports: " + path.name)
    imports = {x.lower() for x in re.findall(r"DLL Name:\s*(\S+)", text)}
    return exports, imports


def validate(portable, replacement):
    data = portable.read_bytes()
    if sha(data) not in BASELINES:
        raise ValueError("Unexpected frozen Portable digest")
    result = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive, tempfile.TemporaryDirectory() as td:
        if len(set(archive.namelist())) != len(archive.namelist()) or archive.testzip():
            raise ValueError("Invalid Portable ZIP")
        for name in DLLS:
            paths = [p for p in archive.namelist() if PurePosixPath(p).name.lower() == name]
            if len(paths) != 1:
                raise ValueError("Ambiguous baseline DLL: " + name)
            old = Path(td) / name
            old.write_bytes(archive.read(paths[0]))
            new = replacement / name
            old_symbols, old_imports = inspect(old)
            new_symbols, new_imports = inspect(new)
            missing = sorted(old_symbols - new_symbols)
            if missing:
                raise ValueError(f"{name}: {len(missing)} old exports missing: {missing[:12]}")
            # In particular, renaming the x64 SSL DLL to the Python name
            # does not change its embedded dependency on x64 libcrypto.
            old_crypto = {x for x in old_imports if x.startswith("libcrypto")}
            new_crypto = {x for x in new_imports if x.startswith("libcrypto")}
            if old_crypto != new_crypto:
                raise ValueError(f"{name}: crypto loader-name mismatch {old_crypto} vs {new_crypto}")
            result.append({"name": name, "original_sha256": sha(old.read_bytes()),
                           "replacement_sha256": sha(new.read_bytes()),
                           "original_exports": len(old_symbols),
                           "replacement_exports": len(new_symbols),
                           "new_named_exports": len(new_symbols-old_symbols),
                           "crypto_imports": sorted(new_crypto)})
    return {"kind": "openssl-export-and-loader-name-preflight", "portable_sha256": sha(data),
            "dlls": result, "runtime_compatibility_verified": False,
            "security_approved": False, "public_release_approved": False}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("portable", type=Path)
    p.add_argument("replacement", type=Path)
    args = p.parse_args()
    print(json.dumps(validate(args.portable, args.replacement), indent=2))
