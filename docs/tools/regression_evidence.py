"""Offline compare pytest JUnit ZIPs; reports test evidence, not release approval."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

MAX_XML = 32 * 1024 * 1024
MAX_ZIP = 32 * 1024 * 1024


def load_report(path):
    path = Path(path)
    if path.stat().st_size > MAX_ZIP:
        raise ValueError("Report archive too large")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) != 1 or entries[0].filename != "regression.xml":
            raise ValueError("Expected a single regression.xml member")
        if entries[0].file_size > MAX_XML:
            raise ValueError("JUnit report too large")
        raw = archive.read(entries[0])
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("XML declarations are not allowed")
    root = ET.fromstring(raw)
    suites = list(root.iter("testsuite"))
    if len(suites) != 1:
        raise ValueError("Expected one pytest testsuite")
    suite = suites[0]
    cases = {}
    counts = dict(tests=0, failures=0, errors=0, skipped=0)
    for case in suite.findall("testcase"):
        key = (case.get("classname"), case.get("name"))
        if not all(key) or key in cases:
            raise ValueError("Missing or duplicate testcase identity")
        duration = float(case.get("time", "nan"))
        if not math.isfinite(duration) or duration < 0:
            raise ValueError("Invalid testcase duration")
        cases[key] = duration
        counts["tests"] += 1
        for attr, tag in (("failures", "failure"), ("errors", "error"), ("skipped", "skipped")):
            counts[attr] += int(case.find(tag) is not None)
    if not cases or any(suite.get(k) != str(v) for k, v in counts.items()):
        raise ValueError("JUnit counts do not match testcases")
    modules = defaultdict(float)
    for (module, _), seconds in cases.items():
        modules[module] += seconds
    total = sum(cases.values())
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), **counts,
            "case_seconds": round(total, 3),
            "slowest_modules": [{"module": module, "seconds": round(seconds, 3),
                                 "percent": round(100 * seconds / total, 2) if total else 0}
                                for module, seconds in sorted(modules.items(), key=lambda row: (-row[1], row[0]))[:10]]}, set(cases)


def compare(windows, ubuntu):
    win, win_ids = load_report(windows)
    lin, lin_ids = load_report(ubuntu)
    same = win_ids == lin_ids
    clean = same and all(report[key] == 0 for report in (win, lin) for key in ("failures", "errors", "skipped"))
    return {"windows": win, "ubuntu": lin, "same_test_identities": same,
            "windows_only": len(win_ids - lin_ids), "ubuntu_only": len(lin_ids - win_ids),
            "regression_evidence_clean": clean, "public_release_approved": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("windows", type=Path)
    parser.add_argument("ubuntu", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = compare(args.windows, args.ubuntu)
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if result["regression_evidence_clean"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
