"""Build a reviewed scheduling profile from complete hash-pilot evidence.

Never downloads or executes artifacts; expects already extracted JSON/XML.
"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET

from ci_junit import junit_key, verify_junit
from ci_shard import verify


def calibrate(root, os_name, platform, source, count):
    reports = []
    digests = {}
    for path in sorted(Path(root).glob(f"shard-{os_name}-*/shard.json")):
        xml_path = path.with_name("regression.xml")
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("profile_sha256") is not None:
            raise ValueError("Expected original unweighted pilot")
        verify_junit(xml_path, report)
        nodes = {junit_key(n): n for n in report["selected"]}
        durations = {}
        for case in ET.parse(xml_path).iter("testcase"):
            node = nodes[(case.attrib["classname"], case.attrib["name"])]
            durations[node] = max(1, round(float(case.attrib["time"]) * 1000))
        report["duration_ms"] = durations
        reports.append(report)
        for item in (path, xml_path):
            digests[f"{path.parent.name}/{item.name}"] = hashlib.sha256(item.read_bytes()).hexdigest()
    summary = verify(reports, count, source, platform)
    all_times = {node: ms for report in reports for node, ms in report["duration_ms"].items()}
    families = {}
    for node, ms in all_times.items():
        families.setdefault(node.split("[", 1)[0], []).append(ms)
    weights = {name: max(1, round(statistics.mean(values))) for name, values in families.items()}
    return {"schema": 1, "source": source, "platform": platform,
            "sample_count": summary["tests"], "default_ms": 30,
            "file_defaults_ms": {"tests/test_workspace.py": 10000},
            "weights_ms": weights, "evidence_sha256": digests}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--os", choices=["ubuntu-latest", "windows-latest"], required=True)
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    platform = "linux" if args.os == "ubuntu-latest" else "win32"
    profile = calibrate(args.reports, args.os, platform, args.source, args.count)
    args.output.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
