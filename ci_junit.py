"""Cross-check pytest JUnit evidence against exact shard node IDs."""
import math
from pathlib import Path
import xml.etree.ElementTree as ET


def junit_key(nodeid):
    """Match pytest's default JUnit class/name encoding, retaining parameters."""
    base, bracket, params = nodeid.partition("[")
    names = base.split("::")
    if len(names) < 2:
        raise ValueError("Invalid pytest node ID")
    names[0] = names[0].replace("/", ".").removesuffix(".py")
    return ".".join(names[:-1]), names[-1] + bracket + params


def verify_junit(path, report):
    """Require a distinct JUnit testcase for every selected node and outcome."""
    expected = {}
    for node in report["selected"]:
        key = junit_key(node)
        if key in expected:
            raise ValueError("Ambiguous JUnit identity")
        expected[key] = node
    if set(report["terminal"]) != set(expected.values()):
        raise ValueError("Incomplete shard outcomes")
    root = ET.parse(Path(path)).getroot()
    if root.tag not in ("testsuites", "testsuite"):
        raise ValueError("Invalid JUnit root")
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    if len(suites) != 1:
        raise ValueError("Expected one pytest suite")
    suite = suites[0]
    if int(suite.attrib["tests"]) != len(expected):
        raise ValueError("JUnit test count mismatch")
    if int(suite.attrib["errors"]) or int(suite.attrib["failures"]):
        raise ValueError("JUnit reports a failure or error")
    seen = set()
    skipped = 0
    for case in suite.findall("testcase"):
        key = (case.attrib["classname"], case.attrib["name"])
        if key not in expected or key in seen:
            raise ValueError("Unexpected or duplicate JUnit testcase")
        seen.add(key)
        if case.find("failure") is not None or case.find("error") is not None:
            raise ValueError("JUnit testcase failed")
        outcome = "skipped" if case.find("skipped") is not None else "passed"
        skipped += outcome == "skipped"
        node = expected[key]
        if report["terminal"][node] != outcome:
            raise ValueError("JUnit outcome mismatch")
        seconds = float(case.attrib["time"])
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError("Invalid JUnit duration")
        if "duration_ms" in report and abs(round(seconds * 1000) - report["duration_ms"][node]) > 3:
            raise ValueError("JUnit duration mismatch")
    if seen != set(expected) or skipped != int(suite.attrib["skipped"]):
        raise ValueError("Incomplete JUnit membership or skip count")
    return {"tests": len(seen), "skipped": skipped}
