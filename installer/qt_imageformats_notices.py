"""Package pinned upstream Qt Image Formats supplemental license evidence."""
import hashlib
import json
from pathlib import Path
import shutil

EXPECTED = {
    "BSD-3-Clause.txt": "9f0490f18656c6f2435bd14f603ef0c96434d1825615363dce43abb42ed1dcce",
    "libtiff.txt": "7e558244926e9b7a3222c55abd73c5a17f71dfada475dba3c126e9d2cc5537f1",
    "libwebp-COPYING.txt": "5aec868f669e384a22372a4e8a1a6cd7d44c64cd451f960ca69cc170d1e13acf",
}
FILES = tuple(EXPECTED) + ("NOTICE.md", "plugin-map.json", "libtiff-attribution.json", "libwebp-attribution.json")
SOURCE_SHA256 = "0943132b5db8de6b6a7f1d162682173e8763c7ed94e80fd39113292845f67762"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def collect(source, target):
    source, target = Path(source), Path(target)
    target.mkdir(parents=True, exist_ok=True)
    records = []
    for name in FILES:
        path = source / name
        if not path.is_file():
            raise ValueError("Missing Qt Image Formats notice: " + name)
        data = path.read_bytes()
        expected = EXPECTED.get(name)
        actual = digest(data)
        if expected and actual != expected:
            raise ValueError("Upstream Qt Image Formats license text changed: " + name)
        shutil.copyfile(path, target / name)
        records.append({"file": name, "sha256": actual, "bytes": len(data)})
    mapping = json.loads((target / "plugin-map.json").read_text(encoding="utf-8"))
    if mapping.get("source", {}).get("sha256") != SOURCE_SHA256:
        raise ValueError("Unexpected Qt Image Formats source pin")
    if set(mapping.get("plugins", {})) != {"qicns", "qtga", "qtiff", "qwbmp", "qwebp"}:
        raise ValueError("Unexpected Qt Image Formats plugin map")
    manifest = {
        "kind": "qt-imageformats-license-supplement",
        "source_version": "6.12.0",
        "source_archive_sha256": SOURCE_SHA256,
        "files": records,
        "review_complete": False,
        "exact_corresponding_source_verified": False,
        "redistribution_approved": False,
    }
    (target / "SUPPLEMENT.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    import sys
    result = collect(sys.argv[1], sys.argv[2])
    print(f"Qt Image Formats notice evidence: {len(result['files'])} files; independent review required.")
