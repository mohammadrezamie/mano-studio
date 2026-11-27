"""Check archived pinned wheel evidence against live PyPI release metadata.

Build/review only. Does not download or execute wheels, prove publisher
identity, verify attestations, grant a license or approve public release.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

from installer.wheel_evidence import pins, validate

def fetch(name, version):
    url = f"https://pypi.org/pypi/{quote(name, safe='')}/{quote(version, safe='')}/json"
    with urlopen(Request(url, headers={"Accept": "application/json", "User-Agent": "ManoStudio-release-audit/1"}), timeout=20) as response:
        if response.geturl() != url:
            raise ValueError("Unexpected index redirect")
        data = response.read(4 * 1024 * 1024 + 1)
    if len(data) > 4 * 1024 * 1024:
        raise ValueError("Index response too large")
    return json.loads(data)

def check_one(name, record, release):
    from installer.wheel_evidence import canonical
    info = release["info"]
    if canonical(info["name"]) != name or info["version"] != record["version"]:
        raise ValueError("Wrong PyPI release: " + name)
    rows = [item for item in release["urls"] if item.get("url") == record["url"]]
    if len(rows) != 1:
        raise ValueError("Missing or duplicate PyPI wheel: " + name)
    row = rows[0]
    if (row.get("packagetype") != "bdist_wheel" or row.get("yanked") is not False
            or row.get("digests", {}).get("sha256") != record["sha256"]):
        raise ValueError("Index digest, type or yanked status mismatch: " + name)
    return {"name": name, "version": record["version"], "url": record["url"],
            "sha256": record["sha256"], "yanked": False}

def audit(root, source, fetch_release=fetch):
    if not re.fullmatch(r"[a-f0-9]{40}", source):
        raise ValueError("Invalid source")
    manifest = json.loads((root / "candidate-manifest.json").read_text(encoding="utf-8-sig"))
    if manifest.get("source_sha") != source or manifest.get("public_release") is not False:
        raise ValueError("Wrong candidate")
    if (root / "commit.txt").read_text(encoding="utf-8-sig").strip() != "SHA=" + source:
        raise ValueError("Wrong build source")
    files = ("wheel-evidence.json", "build-wheel-report.json", "windows-candidate-constraints.txt")
    data = {name: (root / name).read_bytes() for name in files}
    for name, raw in data.items():
        if manifest["review_evidence"]["evidence_sha256"][name] != hashlib.sha256(raw).hexdigest():
            raise ValueError("Evidence bytes differ from candidate manifest: " + name)
    report = validate(json.loads(data["build-wheel-report.json"].decode("utf-8-sig")),
                      pins(root / "windows-candidate-constraints.txt"))
    if report != json.loads(data["wheel-evidence.json"].decode("utf-8-sig")):
        raise ValueError("Wheel report mismatch")
    def one(item):
        name, record = item
        return check_one(name, record, fetch_release(name, record["version"]))
    with ThreadPoolExecutor(max_workers=4) as executor:
        rows = list(executor.map(one, sorted(report["packages"].items())))
    return {"kind": "pypi-index-crosscheck", "source_sha": source,
            "packages": rows, "index_hashes_match": True,
            "publisher_attestations_verified": False, "public_release_approved": False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.artifact, args.source)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Matched {len(result['packages'])} PyPI index wheel records; not release approval.")

if __name__ == "__main__":
    main()
