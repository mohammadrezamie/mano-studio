"""Count committed source at an explicit Git revision, excluding dependencies."""
import argparse
import json
from pathlib import Path
import subprocess


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def category(path):
    suffix = Path(path).suffix.lower()
    if suffix == ".py":
        return "python_tests" if path.startswith("tests/") else "python_product"
    if suffix in {".ps1", ".iss", ".yml", ".yaml", ".sh", ".toml"}:
        return "build_config"
    if suffix == ".md":
        return "documentation"
    return "other"


def line_count(raw):
    return raw.count(b"\n") + int(bool(raw) and not raw.endswith(b"\n"))


def measure(repo, revision="HEAD"):
    sha = git(repo, "rev-parse", "--verify", revision + "^{commit}").decode().strip()
    groups = {k: dict(files=0, bytes=0, lines=0) for k in
              ("python_product", "python_tests", "build_config", "documentation", "other")}
    tree = git(repo, "ls-tree", "-r", "-z", "--full-tree", sha)
    for entry in tree.split(b"\0"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        mode, kind, blob = metadata.split()
        # Count only regular tracked blobs, not symlink targets or submodules.
        if kind != b"blob" or mode not in (b"100644", b"100755"):
            continue
        path = name.decode("utf-8", "surrogateescape")
        raw = git(repo, "cat-file", "blob", blob.decode("ascii"))
        key = category(path)
        group = groups[key]
        group["files"] += 1
        group["bytes"] += len(raw)
        # Other files can be binary. Do not report binary newlines as LOC.
        if key != "other":
            group["lines"] += line_count(raw)
    return {"commit": sha, "groups": groups,
            "python_lines": sum(groups[k]["lines"] for k in ("python_product", "python_tests")),
            "definition": "Physical LF-delimited tracked lines, including blanks and comments; other files excluded from LOC."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revision", nargs="?", default="HEAD")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    print(json.dumps(measure(args.repo, args.revision), indent=2))
