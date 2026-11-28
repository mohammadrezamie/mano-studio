"""Retain an upstream license for recognized bundled OpenSSL crypto versions.

Evidence only: embedded strings do not establish exact distributor provenance.
Never treat a copied license as security or redistribution approval.
"""
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

LICENSES = {"3.5.9": "49cc83d2ee29d13453188217f0e4edd70c7f842f"}
PATTERN = re.compile(rb"OpenSSL ([0-9]+\.[0-9]+\.[0-9]+)(?![0-9])")


def collect(root, target, license_dir=None):
    root, target = Path(root), Path(target)
    license_dir = Path(license_dir) if license_dir else Path(__file__).parent / "licenses"
    target.mkdir(parents=True, exist_ok=True)
    rows, versions, warnings = [], set(), []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or not re.fullmatch(r"lib(?:ssl|crypto)[-\w]*\.dll", path.name.lower()):
            continue
        data = path.read_bytes()
        found = sorted({m.group(1).decode("ascii") for m in PATTERN.finditer(data)})
        rows.append({"path": path.relative_to(root).as_posix(),
                     "sha256": hashlib.sha256(data).hexdigest(), "embedded_versions": found})
        if path.name.lower().startswith("libcrypto"):
            if len(found) != 1:
                warnings.append("Unknown or ambiguous crypto version: " + rows[-1]["path"])
            versions.update(found)
    if not versions:
        warnings.append("No identified bundled crypto version")
    records = []
    for version in sorted(versions):
        pin = LICENSES.get(version)
        if not pin:
            warnings.append("No reviewed upstream license mapping for " + version)
            continue
        name = f"openssl-{version}-LICENSE.txt"
        data = (license_dir / name).read_bytes()
        # Git blob identity is checked to match the recorded upstream text.
        blob = hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()
        if blob != pin:
            raise ValueError("Upstream OpenSSL license text changed: " + version)
        shutil.copyfile(license_dir / name, target / name)
        records.append({"version": version, "file": name, "upstream_git_blob": pin,
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "source": f"https://github.com/openssl/openssl/blob/openssl-{version}/LICENSE.txt"})
    report = {"binaries": rows, "licenses": records, "warnings": warnings,
              "exact_distributor_provenance_verified": False,
              "security_approved": False, "redistribution_approved": False}
    (target / "evidence.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = collect(sys.argv[1], sys.argv[2])
    print(f"OpenSSL license evidence: {len(result['licenses'])} texts, {len(result['warnings'])} warnings; review required.")
